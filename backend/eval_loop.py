"""backend/eval_loop.py — quality gate for the live compose pipeline.

The persona modeler is gone: POST /api/experience now takes {role, topics,
style, visitor_state} and synthesizes the PersonaModel deterministically
server-side. The gate exercises each of the three roles (student, warwick,
business) with an empty topic list (-> the role's curated list) and no style
override (-> the agent picks the mode), measures the round-trip latency per
role, and validates the returned experience schema.

Knowledge pass: the same request plus a gate visitor_state must additionally
return the catalog questions the page was composed around
(knowledge_questions) and should answer them via the atomic sections
(Statement/FactList/StageFlow/PartnerLayers, all on the component
allowlist); a 25 s latency ceiling guards the knowledge-augmented compose.

Run:  python eval_loop.py [--url http://127.0.0.1:8000]
Exit: 0 = all roles valid, 1 = any failure.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import time

import httpx

# The three roles main.py's ROLE_PROFILES accepts.
ROLES = ("student", "warwick", "business")

# knowledge pass: (role, gate visitor_state, extra request fields, minimum
# section count) tuples exercising the question catalog end to end through
# the live compose pipeline. The structured tail is topic-conditional, so a
# question-less orientation page floors at its anchors plus whichever tail
# topics they touch, while a clicked question pins the tail it asks about.
KNOWLEDGE_CHECKS = (
    ("student", "deciding", {}, 4),
    ("business", "deciding", {}, 4),
    ("student", "preparing", {"anchor_qid": "q06-day-to-day"}, 5),
    ("warwick", "discovering", {"anchor_qid": "q14-wbs-role"}, 5),
)
KNOWLEDGE_LATENCY_CEILING_MS = 25000

# Components the pipeline may emit: the ATHA atomic set plus the TextBlock
# render fallback — exactly what frontend registry.js renders.
ALLOWED_COMPONENTS = {
    "TextBlock", "Statement", "FactList", "StageFlow", "PartnerLayers",
}

# UINode fields that count as structured (non-copy) content
STRUCTURED_FIELDS = ("facts", "stages", "layers")

# Brand never-list (ATHA-brand-identity.md §2). Structured payloads are hydrated
# deterministically, so a banned name can reach a page without the model ever
# writing it — the gate checks the rendered content, not the prompt.
NEVER_LIST = re.compile(
    r"\b(hadora|teamwork|whack|monash|cristian)\b", re.IGNORECASE)


def validate_experience(exp: dict) -> tuple[bool, list[str]]:
    problems = []
    if not exp or "sections" not in exp:
        return False, ["no sections"]
    if not 1 <= len(exp["sections"]) <= 10:
        problems.append(f"section count {len(exp['sections'])}")
    entities = exp.get("entities", {})
    banned = NEVER_LIST.findall(json.dumps(exp.get("sections", []),
                                           ensure_ascii=False))
    if banned:
        problems.append(f"never-list name on the page: {sorted(set(banned))}")
    for sec in exp["sections"]:
        comp = sec.get("component")
        if comp not in ALLOWED_COMPONENTS:
            problems.append(f"unknown component {comp!r}")
        for eid in sec.get("entity_ids", []):
            if eid not in entities:
                problems.append(f"entity {eid} referenced but not hydrated")
        if sec.get("title") and len(sec["title"]) > 80:
            problems.append("title > 80")
        if sec.get("text") and len(sec["text"]) > 500:
            problems.append("text > 500")
        if not (sec.get("title") or "").strip():
            problems.append("section without title")
        if not (sec.get("text") or "").strip() and not any(
                sec.get(k) for k in STRUCTURED_FIELDS):
            problems.append(f"section {comp!r} without text or content")
    return len(problems) == 0, problems


async def run(base_url: str) -> int:
    results = []
    latencies: dict[str, int] = {}
    async with httpx.AsyncClient(timeout=180.0) as client:
        for role in ROLES:
            t0 = time.perf_counter()
            try:
                resp = await client.post(
                    f"{base_url}/api/experience",
                    json={"role": role, "topics": [], "style": None},
                )
            except httpx.HTTPError as exc:
                print(f"[{role}] REQUEST FAILED: {exc}")
                results.append({"role": role, "ok": False})
                continue
            ms = int((time.perf_counter() - t0) * 1000)
            latencies[role] = ms
            if resp.status_code != 200:
                print(f"[{role}] HTTP {resp.status_code}: {resp.text[:200]}")
                results.append({"role": role, "ok": False})
                continue
            body = resp.json()
            exp = body.get("experience", {})
            valid, problems = validate_experience(exp)
            if body.get("degraded"):
                valid = False
                problems.append(f"degraded: {body.get('degraded_reason', '?')}")
            mode = exp.get("mode")
            spectrum = exp.get("spectrum")
            mix = ",".join(s.get("component", "?") for s in exp.get("sections", []))
            layout = exp.get("layout")
            results.append({"role": role, "ok": valid, "spectrum": spectrum,
                            "mode": mode, "mix": mix})
            print(f"\n=== {role} ({ms} ms) {'PASS' if valid else 'FAIL'} ===")
            print(f"  schema: {'valid' if valid else 'INVALID'} "
                  f"{problems if problems else ''}")
            print(f"  spectrum: {spectrum} | mode: {mode} | "
                  f"layout: {layout} | mix: {mix}")

    all_ok = bool(results) and all(r.get("ok") for r in results)

    knowledge_ok = True
    async with httpx.AsyncClient(timeout=180.0) as client:
        for role, state, extra, floor in KNOWLEDGE_CHECKS:
            label = f"{role}+{state}" + (
                f"+{extra['anchor_qid']}" if extra.get("anchor_qid") else "")
            t0 = time.perf_counter()
            try:
                resp = await client.post(
                    f"{base_url}/api/experience",
                    json={"role": role, "topics": [], "style": None,
                          "visitor_state": state, **extra},
                )
            except httpx.HTTPError as exc:
                print(f"[{label}] REQUEST FAILED: {exc}")
                knowledge_ok = False
                continue
            ms = int((time.perf_counter() - t0) * 1000)
            if resp.status_code != 200:
                print(f"[{label}] HTTP {resp.status_code}: "
                      f"{resp.text[:200]}")
                knowledge_ok = False
                continue
            body = resp.json()
            exp = body.get("experience", {})
            valid, problems = validate_experience(exp)
            if body.get("degraded"):
                valid = False
                problems.append(f"degraded: {body.get('degraded_reason', '?')}")
            qids = body.get("knowledge_questions") or []
            sections = exp.get("sections", [])
            if len(sections) < floor:
                valid = False
                problems.append(f"only {len(sections)} sections (<{floor})")
            if not isinstance(body.get("suggestions"), list):
                valid = False
                problems.append("suggestions missing or not a list")
            if not qids:
                valid = False
                problems.append("no knowledge_questions")
            too_slow = ms > KNOWLEDGE_LATENCY_CEILING_MS
            ok = valid and not too_slow
            knowledge_ok = knowledge_ok and ok
            print(f"\n=== knowledge {label} ({ms} ms) "
                  f"{'PASS' if ok else 'FAIL'} ===")
            print(f"  schema: {'valid' if valid else 'INVALID'} "
                  f"{problems if problems else ''}")
            print(f"  sections: {len(sections)} (floor {floor}) | "
                  f"answered: {qids}")
            print(f"  spectrum: {exp.get('spectrum')} | mode: {exp.get('mode')}")
            if too_slow:
                print(f"  FAIL: latency {ms} ms > ceiling "
                      f"{KNOWLEDGE_LATENCY_CEILING_MS} ms")

    all_ok = all_ok and knowledge_ok
    spectra = {r.get("spectrum") for r in results if r.get("spectrum")}
    mixes = {r.get("mix") for r in results if r.get("mix")}
    values = list(latencies.values())
    print("\n--- summary ---")
    for role in ROLES:
        print(f"latency {role}: {latencies.get(role, '-')} ms")
    print(f"latency range: {min(values) if values else '-'}–"
          f"{max(values) if values else '-'} ms")
    print(f"spectra distinct: {sorted(spectra)} ({len(spectra)}/{len(ROLES)})")
    print(f"component mixes distinct: {len(mixes)}/{len(ROLES)}")
    print(f"OVERALL: {'PASS' if all_ok else 'FAIL'}")
    return 0 if all_ok else 1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    raise SystemExit(asyncio.run(run(args.url)))


if __name__ == "__main__":
    main()

"""backend/eval_loop.py — quality gate for the live compose pipeline.

The persona modeler is gone: POST /api/experience now takes {role, topics,
style, visitor_state} and synthesizes the PersonaModel deterministically
server-side. The gate exercises each of the three roles (student, warwick,
business) with an empty topic list (-> the role's curated list) and no style
override (-> the agent picks the mode), measures the round-trip latency per
role, and validates the returned experience schema.

Knowledge pass: the same request plus a gate visitor_state must additionally
return the catalog questions the page was composed around
(knowledge_questions) and should answer them via TextBlock sections; a 25 s
latency ceiling guards the knowledge-augmented compose.

Run:  python eval_loop.py [--url http://127.0.0.1:8000]
Exit: 0 = all roles valid, 1 = any failure.
"""

from __future__ import annotations

import argparse
import asyncio
import time

import httpx

# The three roles main.py's ROLE_PROFILES accepts.
ROLES = ("student", "warwick", "business")

# knowledge pass: (role, gate visitor_state) pairs exercising the question
# catalog end to end through the live compose pipeline.
KNOWLEDGE_CHECKS = (("student", "discovering"), ("business", "deciding"))
KNOWLEDGE_LATENCY_CEILING_MS = 25000


def validate_experience(exp: dict) -> tuple[bool, list[str]]:
    problems = []
    if not exp or "sections" not in exp:
        return False, ["no sections"]
    if not 1 <= len(exp["sections"]) <= 10:
        problems.append(f"section count {len(exp['sections'])}")
    entities = exp.get("entities", {})
    for sec in exp["sections"]:
        for eid in sec.get("entity_ids", []):
            if eid not in entities:
                problems.append(f"entity {eid} referenced but not hydrated")
        if sec.get("title") and len(sec["title"]) > 80:
            problems.append("title > 80")
        if sec.get("text") and len(sec["text"]) > 500:
            problems.append("text > 500")
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
        for role, state in KNOWLEDGE_CHECKS:
            t0 = time.perf_counter()
            try:
                resp = await client.post(
                    f"{base_url}/api/experience",
                    json={"role": role, "topics": [], "style": None,
                          "visitor_state": state},
                )
            except httpx.HTTPError as exc:
                print(f"[{role}+{state}] REQUEST FAILED: {exc}")
                knowledge_ok = False
                continue
            ms = int((time.perf_counter() - t0) * 1000)
            if resp.status_code != 200:
                print(f"[{role}+{state}] HTTP {resp.status_code}: "
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
            if len(sections) < 8:
                valid = False
                problems.append(f"only {len(sections)} sections (<8)")
            non_tb = [s.get("component") for s in sections
                      if s.get("component") != "TextBlock"]
            if non_tb:
                valid = False
                problems.append(f"non-TextBlock sections: {non_tb}")
            empty = [i for i, s in enumerate(sections)
                     if not (s.get("title") and s.get("text"))]
            if empty:
                valid = False
                problems.append(f"sections missing title/text: {empty}")
            if not isinstance(body.get("suggestions"), list):
                valid = False
                problems.append("suggestions missing or not a list")
            if not qids:
                valid = False
                problems.append("no knowledge_questions")
            too_slow = ms > KNOWLEDGE_LATENCY_CEILING_MS
            ok = valid and not too_slow
            knowledge_ok = knowledge_ok and ok
            print(f"\n=== knowledge {role}+{state} ({ms} ms) "
                  f"{'PASS' if ok else 'FAIL'} ===")
            print(f"  schema: {'valid' if valid else 'INVALID'} "
                  f"{problems if problems else ''}")
            print(f"  sections: {len(sections)} | answered: {qids}")
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

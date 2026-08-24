"""backend/eval_loop.py — quality gate for the live compose pipeline.

The persona modeler is gone: POST /api/experience now takes {role, topics,
style} and synthesizes the PersonaModel deterministically server-side. So the
gate exercises each of the three roles (student, warwick, business) with an
empty topic list (-> the role's curated list) and no style override (-> the
agent picks the mode), measures the round-trip latency per role, and
validates the returned experience schema.

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


def validate_experience(exp: dict) -> tuple[bool, list[str]]:
    problems = []
    if not exp or "sections" not in exp:
        return False, ["no sections"]
    if not 1 <= len(exp["sections"]) <= 6:
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

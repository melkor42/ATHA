"""backend/eval_loop.py — ticket 10 acceptance loop.

Reads the four fixtures from personas/*.md (example prompt + expected
PersonaModel), posts each prompt to the live POST /api/experience endpoint,
scores Agent 1 against the expected PersonaModel, validates the returned
schema, and checks that the four compositions are visibly different
(distinct spectra + component mixes).

Run:  python eval_loop.py [--url http://127.0.0.1:8000]
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import time
from difflib import SequenceMatcher
from pathlib import Path

import httpx

REPO_ROOT = Path(__file__).resolve().parents[1]
PERSONAS_DIR = REPO_ROOT / "personas"

PROMPT_RE = re.compile(
    r"## Example prompt[^\n]*\n\s*[\"“]([^\n]+)[\"”]", re.IGNORECASE
)
EXPECTED_RE = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL)

# Phase-A contrast table: the spectrum each fixture must land on.
EXPECTED_SPECTRUM = {
    "miriam-stahl": "void",
    "jonas-neumann": "aurora",
    "david-bergmann": "mycelium",
    "tobias-winter": "neon",
}


def load_fixtures() -> list[dict]:
    fixtures = []
    for path in sorted(PERSONAS_DIR.glob("*.md")):
        md = path.read_text(encoding="utf-8")
        prompt_m = PROMPT_RE.search(md)
        expected_m = EXPECTED_RE.search(md)
        if not prompt_m or not expected_m:
            raise SystemExit(f"fixture {path.name}: prompt/expected block missing")
        fixtures.append({
            "slug": path.stem,
            "prompt": prompt_m.group(1).strip(),
            "expected": json.loads(expected_m.group(1)),
        })
    return fixtures


def _overlap(actual: list[str], expected: list[str]) -> tuple[int, list[str]]:
    """Fuzzy per-expected-phrase match (substring or ratio >= 0.6)."""
    matched: list[str] = []
    for exp in expected:
        exp_l = exp.lower()
        for act in actual:
            act_l = act.lower()
            if (exp_l in act_l or act_l in exp_l
                    or SequenceMatcher(None, exp_l, act_l).ratio() >= 0.6):
                matched.append(exp)
                break
    return len(matched), matched


def score_persona(got: dict | None, expected: dict) -> dict:
    if not got:
        return {"pass": False, "reason": "no persona (pipeline failed)"}
    exp_int = expected.get("interests", [])
    n_matched, matched = _overlap(got.get("interests", []), exp_int)
    interests_ok = n_matched >= max(2, len(exp_int) * 2 // 3)
    tone_ok = got.get("tone", "").lower() == expected.get("tone", "").lower()
    accent_ok = got.get("accent_color") == expected.get("accent_color")
    expertise_ok = got.get("expertise_level") == expected.get("expertise_level")
    checks = [interests_ok, tone_ok, accent_ok]
    if "expertise_level" in expected:
        checks.append(expertise_ok)
    return {
        "pass": all(checks),
        "interests": f"{n_matched}/{len(exp_int)} {matched}",
        "got_interests": got.get("interests"),
        "tone": f"{got.get('tone')} {'==' if tone_ok else '!='} "
                f"{expected.get('tone')}",
        "accent": f"{got.get('accent_color')} "
                  f"{'==' if accent_ok else '!='} {expected.get('accent_color')}",
        "expertise": f"{got.get('expertise_level')} "
                     f"{'==' if expertise_ok else '!='} "
                     f"{expected.get('expertise_level', '-')}",
        "perspective": got.get("perspective"),
    }


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
    fixtures = load_fixtures()
    results = []
    latencies = []
    async with httpx.AsyncClient(timeout=180.0) as client:
        for fx in fixtures:
            t0 = time.perf_counter()
            try:
                resp = await client.post(
                    f"{base_url}/api/experience", json={"text": fx["prompt"]}
                )
            except httpx.HTTPError as exc:
                print(f"[{fx['slug']}] REQUEST FAILED: {exc}")
                results.append({"slug": fx["slug"], "ok": False})
                continue
            ms = int((time.perf_counter() - t0) * 1000)
            latencies.append(ms)
            if resp.status_code != 200:
                print(f"[{fx['slug']}] HTTP {resp.status_code}: {resp.text[:200]}")
                results.append({"slug": fx["slug"], "ok": False})
                continue
            body = resp.json()
            persona_score = score_persona(body.get("persona"), fx["expected"])
            exp = body.get("experience", {})
            valid, problems = validate_experience(exp)
            theme = exp.get("theme")
            spectrum = exp.get("spectrum")
            mode = exp.get("mode")
            mix = ",".join(s.get("component", "?") for s in exp.get("sections", []))
            layout = exp.get("layout")
            spectrum_ok = spectrum == EXPECTED_SPECTRUM[fx["slug"]]
            ok = persona_score.get("pass", False) and valid and spectrum_ok
            results.append({"slug": fx["slug"], "ok": ok, "spectrum": spectrum,
                            "mode": mode, "mix": mix})
            print(f"\n=== {fx['slug']} ({ms} ms) "
                  f"{'PASS' if ok else 'FAIL'} ===")
            print(f"  persona: {'PASS' if persona_score.get('pass') else 'FAIL'}")
            for k in ("interests", "got_interests", "tone", "accent",
                      "expertise", "perspective"):
                if k in persona_score:
                    print(f"    {k}: {persona_score[k]}")
            if "reason" in persona_score:
                print(f"    reason: {persona_score['reason']}")
            print(f"  schema: {'valid' if valid else 'INVALID'} "
                  f"{problems if problems else ''}")
            print(f"  spectrum: {spectrum} (want {EXPECTED_SPECTRUM[fx['slug']]}) "
                  f"| mode: {mode} | layout: {layout} | mix: {mix}")
            if theme is not None:
                print(f"  WARNING: legacy 'theme' field present: {theme}")

    spectra = {r.get("spectrum") for r in results if r.get("spectrum")}
    mixes = {r.get("mix") for r in results if r.get("mix")}
    diverse = len(spectra) == 4 and len(mixes) >= 3
    all_ok = bool(results) and all(r.get("ok") for r in results)
    print("\n--- summary ---")
    print(f"spectra distinct: {sorted(s for s in spectra if s)} "
          f"(distinct={len(spectra)}/4)")
    print(f"component mixes distinct: {len(mixes)}/4")
    print(f"latency: {min(latencies) if latencies else '-'}–"
          f"{max(latencies) if latencies else '-'} ms")
    print(f"OVERALL: {'PASS' if all_ok and diverse else 'FAIL'}")
    return 0 if all_ok and diverse else 1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    raise SystemExit(asyncio.run(run(args.url)))


if __name__ == "__main__":
    main()

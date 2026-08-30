"""backend/test_knowledge_retrieval.py — the digestion quality gate.

Asserts that the committed question catalog is actually answerable from the
ingested graph, for every role — i.e. that the digest shape serves the goal
("the page answers the visitor's most important questions"). Requires the
knowledge graph to be ingested (run ingest_knowledge.py first).

Checks:
  1. every catalog question appears in the full catalog of each of its roles,
     with at least one grounded answer;
  2. internal passage ids never surface in any role/state bundle;
  3. realistic compose-sized bundles (top 5 questions) are non-empty for every
     role × state combination;
  4. skeleton gate: every role × state yields >=7 slots incl. the guaranteed
     tail (edition/rhythm/layers) and leaks no internal passage;
  5. facet probes (value form honest ceiling, lens dedicated slot) and the
     calibrated free-text threshold (relevant surfaces, irrelevant does not).

Run:  python test_knowledge_retrieval.py      (exit 0 = gate passed)
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from graph_queries import get_database, get_driver
from knowledge import knowledge_for
from skeleton import build_skeleton

MAP_PATH = Path(__file__).resolve().parents[1] / "data" / "knowledge" / "knowledge_map.json"
ROLES = ["student", "warwick", "business"]
STATES = ["discovering", "deciding", "preparing", "experienced"]


async def main() -> None:
    m = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    internal_ids = {p["id"] for p in m["passages"] if p["internal"]}
    questions = m["questions"]
    errors: list[str] = []

    driver = get_driver()
    db = get_database()
    try:
        # 1. full-catalog answerability per role
        for role in ROLES:
            bundle = await knowledge_for(role, None, driver=driver, database=db,
                                         top_questions=None, max_answers=3)
            got = {q["id"]: q for q in bundle["questions"]}
            for q in questions:
                if role not in q["roles"]:
                    continue
                if q["id"] not in got:
                    errors.append(f"{q['id']} missing from role '{role}' catalog")
                elif not got[q["id"]]["answers"]:
                    errors.append(f"{q['id']} has no grounded answers for '{role}'")
            leaked = [a["passage_id"] for q in bundle["questions"]
                      for a in q["answers"] if a["passage_id"] in internal_ids]
            leaked += [s["passage_id"] for s in bundle["supporting"]
                       if s["passage_id"] in internal_ids]
            if leaked:
                errors.append(f"INTERNAL PASSAGES LEAKED for role '{role}': {leaked}")

        # 2. compose-sized bundles for every role x state
        for role in ROLES:
            for state in STATES:
                bundle = await knowledge_for(role, state, driver=driver,
                                             database=db, top_questions=5)
                if not bundle["questions"]:
                    errors.append(f"empty bundle for role={role} state={state}")
                    continue
                unanswered = [q["id"] for q in bundle["questions"]
                              if not q["answers"]]
                if unanswered:
                    errors.append(f"role={role} state={state}: questions "
                                  f"without answers: {unanswered}")

        # 4. skeleton gate — filled page, guaranteed tail, no internal leak
        for role in ROLES:
            for state in STATES:
                sk = await build_skeleton(role, state, driver=driver,
                                          database=db)
                kinds = {s["kind"] for s in sk["slots"]}
                if len(sk["slots"]) < 7:
                    errors.append(f"skeleton role={role} state={state}: "
                                  f"only {len(sk['slots'])} slots (<7)")
                for tail in ("edition", "rhythm", "layers"):
                    if tail not in kinds:
                        errors.append(f"skeleton role={role} state={state}: "
                                      f"missing tail '{tail}'")
                leaked = [src["pid"] for s in sk["slots"]
                          for src in s["sources"]
                          if src.get("pid") in internal_ids]
                if leaked:
                    errors.append(f"SKELETON INTERNAL LEAK role={role} "
                                  f"state={state}: {leaked}")

        # 5a. facet probes
        sk = await build_skeleton("business", "deciding", driver=driver,
                                  database=db, facet="value-decision")
        facets = [s for s in sk["slots"] if s["kind"] == "facet"]
        if not facets:
            errors.append("value-decision facet produced no facet slot")
        elif len(facets[0]["sources"]) != 1:
            errors.append("value-decision facet: expected exactly 1 source "
                          f"(honest ceiling), got {len(facets[0]['sources'])}")
        sk = await build_skeleton("student", None, driver=driver, database=db,
                                  facet="lens-responsibility")
        if not any(s["kind"] == "facet" for s in sk["slots"]):
            errors.append("lens-responsibility facet produced no facet slot")

        # 5b. free-text threshold: relevant surfaces, irrelevant falls back
        sk = await build_skeleton("student", None, driver=driver, database=db,
                                  free_text="how are teams formed and how is "
                                            "the work judged")
        extra_pids = {src["pid"] for s in sk["slots"] if s["kind"] == "extra"
                      for src in s["sources"]}
        if not extra_pids & {"team-setup-03", "assessment-framework-03",
                             "team-setup-01"}:
            errors.append("relevant free_text did not surface team/judgement "
                          f"passages as extras (got {sorted(extra_pids)})")
        sk = await build_skeleton("student", None, driver=driver, database=db,
                                  free_text="banana pancake recipe")
        if len(sk["slots"]) < 7:
            errors.append("irrelevant free_text shrank the page below 7 slots")
    finally:
        await driver.close()

    if errors:
        for e in errors:
            print("FAIL:", e)
        sys.exit(1)
    print("retrieval quality gate OK: all catalog questions answerable per "
          "role, no internal leakage, all role x state bundles grounded")


if __name__ == "__main__":
    asyncio.run(main())

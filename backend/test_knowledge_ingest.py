"""backend/test_knowledge_ingest.py — offline contract test for knowledge_map.json.

Instant, credential-free schema contract (like test_experience_schema.py):
unique ids, all references resolve, roles/states valid, internal passages
isolated, every question answered, text lengths embeddable. Exit 0 = valid.

Run:  python test_knowledge_ingest.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

MAP_PATH = Path(__file__).resolve().parents[1] / "data" / "knowledge" / "knowledge_map.json"
EDITION_PATH = Path(__file__).resolve().parents[1] / "data" / "knowledge" / "edition_facts.json"
MAX_TEXT_CHARS = 2000
VALID_PERSPECTIVES = {"om", "hadora", "joint", "operational"}
VALID_STATUSES = {"confirmed", "proposed", "open"}

# ontology label -> Neo4j label used by ingest_knowledge.py (kept in sync here
# so the contract test fails loudly if the map grows a group ingest ignores)
ONTOLOGY_GROUPS = {
    "organizations", "lenses", "verdict_states", "arc_stages", "team_functions",
    "assessment_areas", "recommendation_categories", "value_forms",
    "hadora_principles",
}


def fail(errors: list[str]) -> None:
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)


def main() -> None:
    m = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []

    role_ids = {r["id"] for r in m["roles"]}
    state_ids = {s["id"] for s in m["states"]}
    question_ids = {q["id"] for q in m["questions"]}
    onto_ids: set[str] = set()
    if set(m["ontology"]) != ONTOLOGY_GROUPS:
        errors.append(f"ontology groups drifted: {sorted(m['ontology'])} "
                      f"!= {sorted(ONTOLOGY_GROUPS)}")
    for items in m["ontology"].values():
        for item in items:
            onto_ids.add(item["id"])

    all_ids = onto_ids | question_ids | role_ids | state_ids
    if len(all_ids) != len(onto_ids) + len(question_ids) + len(role_ids) + len(state_ids):
        errors.append("id collision across ontology/questions/roles/states")

    # every question ranks itself for exactly the roles it lists
    for q in m["questions"]:
        if set(q["rank_by_role"]) != set(q["roles"]):
            errors.append(f"{q['id']}: rank_by_role keys != roles")
        for s in q["states"]:
            if s not in state_ids:
                errors.append(f"{q['id']}: unknown state '{s}'")

    passages = m["passages"]
    seen: set[str] = set()
    answered: dict[str, int] = {}
    for p in passages:
        pid = p["id"]
        if pid in seen:
            errors.append(f"duplicate passage id '{pid}'")
        seen.add(pid)
        for s in p["supports"]:
            if s not in onto_ids:
                errors.append(f"{pid}: unknown supports id '{s}'")
        for q in p["answers"]:
            if q not in question_ids:
                errors.append(f"{pid}: unknown question id '{q}'")
            answered[q] = answered.get(q, 0) + 1
        for r in p["roles"]:
            if r not in role_ids:
                errors.append(f"{pid}: unknown role '{r}'")
        for s in p["visitor_states"]:
            if s not in state_ids:
                errors.append(f"{pid}: unknown state '{s}'")
        if p["perspective"] not in VALID_PERSPECTIVES:
            errors.append(f"{pid}: bad perspective '{p['perspective']}'")
        if p["status"] not in VALID_STATUSES:
            errors.append(f"{pid}: bad status '{p['status']}'")
        if len(p["text"]) > MAX_TEXT_CHARS:
            errors.append(f"{pid}: text {len(p['text'])} chars > {MAX_TEXT_CHARS}")
        if not p["text"].strip():
            errors.append(f"{pid}: empty text")
        if p["internal"] and (p["roles"] or p["visitor_states"]):
            errors.append(f"{pid}: internal passage must be unreachable "
                          "(no roles/states)")
        if not p["internal"] and not p["roles"]:
            errors.append(f"{pid}: visitor passage without roles is unreachable")

    for qid in question_ids:
        if not answered.get(qid):
            errors.append(f"question '{qid}' has no answering passage")

    # edition facts (static skeleton tail source, not ingested as passages)
    if not EDITION_PATH.exists():
        errors.append("edition_facts.json missing")
    else:
        edition = json.loads(EDITION_PATH.read_text(encoding="utf-8"))
        facts = edition.get("facts") or []
        if not facts:
            errors.append("edition_facts.json: no facts")
        seen_ids: set[str] = set()
        for f in facts:
            fid = f.get("id", "?")
            if fid in seen_ids:
                errors.append(f"edition fact id duplicated: {fid}")
            seen_ids.add(fid)
            if not f.get("fact"):
                errors.append(f"edition fact {fid}: empty fact text")
            elif len(f["fact"]) > 200:
                errors.append(f"edition fact {fid}: fact text > 200 chars")
            if f.get("status") not in VALID_STATUSES:
                errors.append(f"edition fact {fid}: bad status {f.get('status')!r}")

    if errors:
        fail(errors)
    print(f"knowledge map contract OK: {len(passages)} passages "
          f"({sum(1 for p in passages if p['internal'])} internal), "
          f"{len(onto_ids)} ontology nodes, {len(question_ids)} questions, "
          f"all questions answered")


if __name__ == "__main__":
    main()

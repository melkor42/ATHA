"""backend/ingest_knowledge.py — offline, idempotent ingest of the ATHA knowledge graph.

Reads data/knowledge/knowledge_map.json (produced by build_knowledge_map.py),
MERGE-writes the three digest layers into Neo4j Aura in UNWIND batches, embeds
visitor-reachable passages locally with fastembed BAAI/bge-small-en-v1.5 (384
dims — same model family as the Profile pipeline), creates the
``knowledge_embeddings`` vector index and waits until ONLINE.

Layers:
  1. Question catalog   (:Question)-[:FOR_ROLE|FOR_STATE], rank_by_role JSON prop
  2. Ontology           Organization, Lens, VerdictState, ArcStage, TeamFunction,
                        AssessmentArea (versioned, -[:VARIANT_OF]->Lens),
                        RecommendationCategory, ValueForm, HadoraPrinciple
  3. Passages           (:Passage) + :InternalPassage label for internal content;
                        -[:ANSWERED_BY] from questions, -[:SUPPORTS]-> ontology,
                        -[:RELEVANT_FOR]-> role, -[:RELEVANT_FOR_STATE]-> state.

Internal passages carry NO embedding and NO role/state edges, so no retrieval
path can surface them to visitors.

Stale :Passage/:Question nodes absent from the map are detached-deleted so a
re-run converges exactly to the committed map (ontology stays MERGE-only).

Run:  python ingest_knowledge.py        (needs .env Aura credentials)
"""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path

from neo4j import AsyncDriver

from graph_queries import (
    EMBED_DIMS,
    embed_passages,
    get_database,
    get_driver,
)

MAP_PATH = Path(__file__).resolve().parents[1] / "data" / "knowledge" / "knowledge_map.json"
KNOWLEDGE_INDEX_NAME = "knowledge_embeddings"
BATCH = 50

# ontology group in the map -> (Neo4j label, properties written verbatim)
ONTOLOGY_LABELS = {
    "organizations": "Organization",
    "lenses": "Lens",
    "verdict_states": "VerdictState",
    "arc_stages": "ArcStage",
    "team_functions": "TeamFunction",
    "assessment_areas": "AssessmentArea",
    "recommendation_categories": "RecommendationCategory",
    "value_forms": "ValueForm",
    "hadora_principles": "HadoraPrinciple",
}

CREATE_INDEX_QUERY = f"""
CREATE VECTOR INDEX {KNOWLEDGE_INDEX_NAME} IF NOT EXISTS
FOR (p:Passage) ON (p.embedding)
OPTIONS {{indexConfig: {{
  `vector.dimensions`: {EMBED_DIMS},
  `vector.similarity_function`: 'cosine'
}}}}
"""

UPSERT_ROLES_STATES_QUERY = """
UNWIND $roles AS row
MERGE (r:VisitorRole {id: row.id})
SET r.name = row.name, r.description = row.description
WITH 1 AS dummy
UNWIND $states AS srow
MERGE (s:VisitorState {id: srow.id})
SET s.name = srow.name
"""

UPSERT_QUESTIONS_QUERY = """
UNWIND $rows AS row
MERGE (q:Question {id: row.id})
SET q.text = row.text,
    q.keywords = row.keywords,
    q.rank_by_role = row.rank_by_role
"""

QUESTION_ROLE_STATE_QUERY = """
UNWIND $rows AS row
MATCH (q:Question {id: row.qid})
MATCH (r:VisitorRole {id: row.role})
MERGE (q)-[:FOR_ROLE]->(r)
WITH q, row
UNWIND row.states AS sid
MATCH (s:VisitorState {id: sid})
MERGE (q)-[:FOR_STATE]->(s)
"""

# generic ontology upsert: label is parameterized per group in python, props
# are merged wholesale (every item's keys become node properties).
UPSERT_ONTOLOGY_QUERY = """
UNWIND $rows AS row
MERGE (n:{label} {{id: row.id}})
SET n += row.props
"""

ASSESSMENT_VARIANT_OF_QUERY = """
UNWIND $rows AS row
MATCH (a:AssessmentArea {id: row.id})
MATCH (l:Lens {id: row.variant_of})
MERGE (a)-[:VARIANT_OF]->(l)
"""

UPSERT_PASSAGES_QUERY = """
UNWIND $rows AS row
MERGE (p:Passage {id: row.id})
SET p.source_file = row.source_file,
    p.heading_path = row.heading_path,
    p.text = row.text,
    p.perspective = row.perspective,
    p.status = row.status,
    p.roles = row.roles,
    p.visitor_states = row.visitor_states,
    p.internal = row.internal
WITH p, row
FOREACH (_ IN CASE WHEN row.internal THEN [1] ELSE [] END |
  SET p:InternalPassage)
FOREACH (_ IN CASE WHEN NOT row.internal THEN [1] ELSE [] END |
  REMOVE p:InternalPassage)
FOREACH (_ IN CASE WHEN row.embedding IS NOT NULL THEN [1] ELSE [] END |
  SET p.embedding = row.embedding)
FOREACH (_ IN CASE WHEN row.embedding IS NULL THEN [1] ELSE [] END |
  SET p.embedding = null)
"""

PASSAGE_SUPPORTS_QUERY = """
UNWIND $rows AS row
MATCH (p:Passage {id: row.pid})
MATCH (t {id: row.target})
MERGE (p)-[:SUPPORTS]->(t)
"""

PASSAGE_ROLE_STATE_QUERY = """
UNWIND $rows AS row
MATCH (p:Passage {id: row.pid})
MATCH (r:VisitorRole {id: row.role})
MERGE (p)-[:RELEVANT_FOR]->(r)
WITH p, row
UNWIND row.states AS sid
MATCH (s:VisitorState {id: sid})
MERGE (p)-[:RELEVANT_FOR_STATE]->(s)
"""

ANSWERED_BY_QUERY = """
UNWIND $rows AS row
MATCH (q:Question {id: row.qid})
MATCH (p:Passage {id: row.pid})
MERGE (q)-[:ANSWERED_BY]->(p)
"""

PRUNE_STALE_QUERY = """
MATCH (p:Passage) WHERE NOT p.id IN $passage_ids
DETACH DELETE p
WITH 1 AS dummy
MATCH (q:Question) WHERE NOT q.id IN $question_ids
DETACH DELETE q
"""

# MERGE only adds relationships, so edges the map dropped would accumulate.
# All of these types are fully derived from the committed map, so clearing and
# recreating them makes re-ingest converge exactly.
CLEAR_DERIVED_EDGES_QUERY = """
MATCH ()-[r:ANSWERED_BY|SUPPORTS|RELEVANT_FOR|RELEVANT_FOR_STATE
          |FOR_ROLE|FOR_STATE|VARIANT_OF]->()
DELETE r
"""

COUNTS_QUERY = """
OPTIONAL MATCH (q:Question)
WITH count(q) AS questions
OPTIONAL MATCH (p:Passage)
WITH questions, count(p) AS passages
OPTIONAL MATCH (i:InternalPassage)
WITH questions, passages, count(i) AS internal
OPTIONAL MATCH ()-[r]->()
WHERE any(l IN ['Question', 'Passage', 'VisitorRole', 'VisitorState',
                'Organization', 'Lens', 'VerdictState', 'ArcStage',
                'TeamFunction', 'AssessmentArea', 'RecommendationCategory',
                'ValueForm', 'HadoraPrinciple']
          WHERE l IN labels(startNode(r)) OR l IN labels(endNode(r)))
RETURN questions, passages, internal, count(r) AS relationships
"""


def chunked(rows: list, size: int = BATCH):
    for start in range(0, len(rows), size):
        yield rows[start:start + size]


async def run_batched(driver: AsyncDriver, database: str, query: str,
                      rows: list, label: str) -> None:
    for chunk in chunked(rows):
        async with driver.session(database=database) as session:
            await session.run(query, rows=chunk)
    print(f"  upserted {len(rows):4d} {label}")


async def wait_index_online(driver: AsyncDriver, database: str,
                            timeout_s: float = 180.0) -> None:
    deadline = time.monotonic() + timeout_s
    async with driver.session(database=database) as session:
        while time.monotonic() < deadline:
            result = await session.run(
                "SHOW VECTOR INDEXES YIELD name, state "
                "WHERE name = $name RETURN state", name=KNOWLEDGE_INDEX_NAME
            )
            rows = await result.data()
            if rows and rows[0]["state"] == "ONLINE":
                print(f"  vector index '{KNOWLEDGE_INDEX_NAME}' is ONLINE")
                return
            await asyncio.sleep(1)
    raise TimeoutError(
        f"vector index '{KNOWLEDGE_INDEX_NAME}' not ONLINE in {timeout_s}s")


async def main() -> None:
    m = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    passages = m["passages"]
    driver = get_driver()
    database = get_database()
    try:
        async with driver.session(database=database) as session:
            before = await (await session.run(COUNTS_QUERY)).data()
            await session.run(CREATE_INDEX_QUERY)
        print("counts before:", dict(before[0]))
        print(f"  vector index '{KNOWLEDGE_INDEX_NAME}' ensured "
              f"({EMBED_DIMS} dims, cosine)")

        # layer 0: roles + states
        async with driver.session(database=database) as session:
            await session.run(UPSERT_ROLES_STATES_QUERY,
                              roles=m["roles"], states=m["states"])
        print(f"  upserted {len(m['roles']):4d} visitor roles, "
              f"{len(m['states'])} visitor states")

        # layer 1: question catalog (edges deferred until after the clear)
        question_rows = [
            {"id": q["id"], "text": q["text"], "keywords": q["keywords"],
             "rank_by_role": json.dumps(q["rank_by_role"])}
            for q in m["questions"]
        ]
        await run_batched(driver, database, UPSERT_QUESTIONS_QUERY,
                          question_rows, "questions")
        qrs_rows = [
            {"qid": q["id"], "role": role, "states": q["states"]}
            for q in m["questions"] for role in q["roles"]
        ]

        # layer 2: ontology
        for group, label in ONTOLOGY_LABELS.items():
            rows = [{"id": item["id"],
                     "props": {k: v for k, v in item.items()
                               if v is not None and k != "variant_of"}}
                    for item in m["ontology"][group]]
            await run_batched(driver, database,
                              UPSERT_ONTOLOGY_QUERY.format(label=label),
                              rows, label)
        variant_rows = [
            {"id": a["id"], "variant_of": a["variant_of"]}
            for a in m["ontology"]["assessment_areas"] if a.get("variant_of")
        ]

        # layer 3: passages (+ embeddings for visitor-reachable ones)
        reachable = [p for p in passages if not p["internal"]]
        vectors = embed_passages([p["text"] for p in reachable])
        vec_by_id = {p["id"]: v for p, v in zip(reachable, vectors)}
        passage_rows = [
            {**{k: p[k] for k in ("id", "source_file", "heading_path", "text",
                                  "perspective", "status", "roles",
                                  "visitor_states", "internal")},
             "embedding": vec_by_id.get(p["id"])}
            for p in passages
        ]
        await run_batched(driver, database, UPSERT_PASSAGES_QUERY,
                          passage_rows,
                          f"passages ({len(reachable)} embedded)")

        # converge exactly to the committed map: prune stale nodes, then clear
        # and recreate every map-derived relationship type (MERGE alone would
        # keep edges the map dropped).
        async with driver.session(database=database) as session:
            await session.run(
                PRUNE_STALE_QUERY,
                passage_ids=[p["id"] for p in passages],
                question_ids=[q["id"] for q in m["questions"]])
            await session.run(CLEAR_DERIVED_EDGES_QUERY)
        print("  pruned stale nodes and cleared derived edges")

        await run_batched(driver, database, QUESTION_ROLE_STATE_QUERY,
                          qrs_rows, "question role/state edges")
        await run_batched(driver, database, ASSESSMENT_VARIANT_OF_QUERY,
                          variant_rows, "assessment VARIANT_OF edges")

        supports_rows = [
            {"pid": p["id"], "target": t}
            for p in passages for t in p["supports"]
        ]
        await run_batched(driver, database, PASSAGE_SUPPORTS_QUERY,
                          supports_rows, "SUPPORTS")

        prs_rows = [
            {"pid": p["id"], "role": role, "states": p["visitor_states"]}
            for p in passages if not p["internal"] for role in p["roles"]
        ]
        await run_batched(driver, database, PASSAGE_ROLE_STATE_QUERY,
                          prs_rows, "passage role/state edges")

        answered_rows = [
            {"qid": q, "pid": p["id"]}
            for p in passages for q in p["answers"]
        ]
        await run_batched(driver, database, ANSWERED_BY_QUERY,
                          answered_rows, "ANSWERED_BY")

        await wait_index_online(driver, database)
        async with driver.session(database=database) as session:
            after = await (await session.run(COUNTS_QUERY)).data()
        print("counts after: ", dict(after[0]))
    finally:
        await driver.close()


if __name__ == "__main__":
    asyncio.run(main())

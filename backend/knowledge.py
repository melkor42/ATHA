"""backend/knowledge.py — the knowledge layer of the compose pipeline.

knowledge_for(role, visitor_state) returns the visitor's most important
questions (from the committed question catalog) together with the grounded
passages that answer them — the bundle the compose agent turns into a page
that answers instead of making the visitor search.

Resolution order:
  1. catalog hit   (:Question)-[:FOR_ROLE]-> the visitor's role, ordered by the
                   role's rank (questions matching the visitor's gate state
                   float first), answers via (:Question)-[:ANSWERED_BY]->
                   (:Passage), confirmed passages first;
  2. vector net    SEARCH over knowledge_embeddings filtered to the role —
                   supporting passages beyond the catalog.

Internal passages carry no embeddings, no roles and no ANSWERED_BY edges from
visitor-visible questions; the explicit ``p.internal = false`` filters are the
belt to those braces. The interface is deliberately thin so the Neo4j Aura
Agent can replace this implementation later without touching compose.
"""

from __future__ import annotations

import json

from neo4j import AsyncDriver

from graph_queries import embed_query, get_database

KNOWLEDGE_VECTOR_INDEX = "knowledge_embeddings"

CATALOG_QUERY = """
MATCH (q:Question)-[:FOR_ROLE]->(:VisitorRole {id: $role})
OPTIONAL MATCH (q)-[:FOR_STATE]->(s:VisitorState)
RETURN q.id AS id, q.text AS text, q.rank_by_role AS rank_json,
       collect(DISTINCT s.id) AS states
"""

ANSWERS_QUERY = f"""
UNWIND $qids AS qid
MATCH (q:Question {{id: qid}})-[:ANSWERED_BY]->(p:Passage)
WHERE p.internal = false
RETURN qid,
       collect({{pid: p.id, text: p.text, heading_path: p.heading_path,
                 perspective: p.perspective, status: p.status}}) AS answers
"""

VECTOR_NET_QUERY = f"""
MATCH (p:Passage)
SEARCH p IN (
  VECTOR INDEX {KNOWLEDGE_VECTOR_INDEX}
  FOR $vector
  LIMIT $top_k
) SCORE AS score
WHERE $role IN p.roles AND p.internal = false
RETURN p.id AS pid, p.text AS text, p.heading_path AS heading_path,
       p.status AS status, score
ORDER BY score DESC
LIMIT $limit
"""


def _rank_of(rank_json: str | None, role: str) -> int:
    try:
        return int(json.loads(rank_json or "{}").get(role, 99))
    except (ValueError, TypeError):
        return 99


async def catalog_questions(driver: AsyncDriver, database: str, role: str,
                            visitor_state: str | None) -> list[dict]:
    """All catalog questions for a role, state-adjusted rank order."""
    async with driver.session(database=database) as session:
        rows = await (await session.run(CATALOG_QUERY, role=role)).data()
    for row in rows:
        row["rank"] = _rank_of(row["rank_json"], role)
        row["state_match"] = bool(visitor_state) and visitor_state in row["states"]
    rows.sort(key=lambda r: (not r["state_match"], r["rank"]))
    return rows


async def knowledge_for(
    role: str,
    visitor_state: str | None = None,
    *,
    driver: AsyncDriver,
    database: str | None = None,
    top_questions: int = 5,
    max_answers: int = 2,
    vector_top_k: int = 10,
    vector_limit: int = 4,
) -> dict:
    """Compose the knowledge bundle for one visitor.

    Returns ``{"role", "visitor_state", "questions": [{id, text, answers:
    [{passage_id, text, heading_path, perspective, status}]}], "supporting":
    [{passage_id, text, heading_path, score}]}``. ``top_questions=None``
    returns the full catalog (used by the retrieval quality gate).
    """
    db = database or get_database()
    questions = await catalog_questions(driver, db, role, visitor_state)
    if top_questions is not None:
        questions = questions[:top_questions]

    bundle_questions: list[dict] = []
    if questions:
        async with driver.session(database=db) as session:
            answer_rows = await (
                await session.run(
                    ANSWERS_QUERY, qids=[q["id"] for q in questions])
            ).data()
        answers_by_q: dict[str, list[dict]] = {r["qid"]: r["answers"]
                                               for r in answer_rows}
        used_pids: set[str] = set()
        for q in questions:
            candidates = sorted(
                answers_by_q.get(q["id"], []),
                key=lambda a: ({"confirmed": 0, "proposed": 1}.get(a["status"], 2),
                               a["pid"]),
            )
            # prefer passages not already answering an earlier question, so the
            # page's TextBlocks stay distinct; fall back to the full list when
            # every candidate is already used.
            fresh = [a for a in candidates if a["pid"] not in used_pids]
            answers = (fresh or candidates)[:max_answers]
            for a in answers:
                used_pids.add(a["pid"])
            bundle_questions.append({
                "id": q["id"],
                "text": q["text"],
                "answers": [
                    {"passage_id": a["pid"], "text": a["text"],
                     "heading_path": a["heading_path"],
                     "perspective": a["perspective"], "status": a["status"]}
                    for a in answers
                ],
            })

    # vector net: role-filtered similarity over the embedded passages
    supporting: list[dict] = []
    if bundle_questions:
        query_text = f"{role} {visitor_state or ''} " + " ".join(
            q["text"] for q in bundle_questions[:3])
        vector = embed_query(query_text)
        async with driver.session(database=db) as session:
            net_rows = await (
                await session.run(VECTOR_NET_QUERY, vector=vector, role=role,
                                  top_k=vector_top_k, limit=vector_limit)
            ).data()
        seen = {a["passage_id"] for q in bundle_questions for a in q["answers"]}
        supporting = [
            {"passage_id": r["pid"], "text": r["text"],
             "heading_path": r["heading_path"], "score": r["score"]}
            for r in net_rows if r["pid"] not in seen
        ]

    return {"role": role, "visitor_state": visitor_state,
            "questions": bundle_questions, "supporting": supporting}

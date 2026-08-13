"""backend/graph_queries.py — verified hybrid retrieval for the SIGNAL wow-page.

Single source of truth for:
  * the local embedding model (fastembed BAAI/bge-small-en-v1.5, 384 dims) —
    SAME model at ingest and query time;
  * the Neo4j Aura connection (.env at repo root, loaded via python-dotenv);
  * HYBRID_QUERY — vector search + graph traversal in one Cypher statement,
    using the current Cypher ``SEARCH`` clause (``db.index.vector.queryNodes``
    is deprecated since Neo4j 2026.04);
  * ``hybrid_retrieve()`` — async function reusable by the FastAPI orchestrator.

Returns per match: person id / name / role / school / score plus the matched
enterprises/topics, and the allowed-id whitelist (person ids + enterprise ids)
that verify() checks entity_ids against.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from dotenv import dotenv_values
from fastembed import TextEmbedding
from neo4j import AsyncGraphDatabase, AsyncDriver

# --- constants ----------------------------------------------------------------

EMBED_MODEL_NAME = "BAAI/bge-small-en-v1.5"   # local fastembed model, 384 dims
EMBED_DIMS = 384                               # MUST match the vector index
VECTOR_INDEX_NAME = "profile_embeddings"

# Hybrid retrieval: vector search over Profile embeddings via the current
# SEARCH clause, then graph traversal Person -> School and
# Person -INTERESTED_IN-> Topic <-SEEKS_EXPERTISE- Enterprise.
HYBRID_QUERY = f"""
MATCH (profile:Profile)
SEARCH profile IN (
  VECTOR INDEX {VECTOR_INDEX_NAME}
  FOR $vector
  LIMIT $top_k
) SCORE AS score
MATCH (profile)<-[:HAS_PROFILE]-(person:Person)-[:ATTENDS]->(school:School)
OPTIONAL MATCH (person)-[:INTERESTED_IN]->(topic:Topic)
                       <-[:SEEKS_EXPERTISE]-(enterprise:Enterprise)
WITH person, school, score,
     collect(DISTINCT CASE WHEN enterprise IS NULL THEN NULL
          ELSE {{id: enterprise.id, name: enterprise.name,
                 topic: topic.name}} END) AS matches
RETURN person.id AS person_id,
       person.name AS name,
       person.role AS role,
       school.name AS school,
       score,
       matches
ORDER BY score DESC
LIMIT $limit
"""


# --- environment / driver ------------------------------------------------------

def load_env() -> dict[str, str]:
    """Load .env from the repo root (tolerates a UTF-8 BOM on the first key)."""
    env_path = Path(__file__).resolve().parents[1] / ".env"
    values = dotenv_values(env_path)
    return {k.lstrip("\ufeff"): v for k, v in values.items() if v is not None}


def get_driver(env: dict[str, str] | None = None) -> AsyncDriver:
    env = env or load_env()
    return AsyncGraphDatabase.driver(
        env["NEO4J_URI"],
        auth=(env["NEO4J_USERNAME"], env["NEO4J_PASSWORD"]),
        # fail fast on dead/paused Aura sockets — a hung driver must never
        # freeze the orchestrator (2026-08-13 incident: stale post-sleep
        # socket hung every request including /health)
        connection_timeout=10,
        connection_acquisition_timeout=10,
        max_transaction_retry_time=15,
    )


def get_database(env: dict[str, str] | None = None) -> str:
    return (env or load_env())["NEO4J_DATABASE"]


# --- embeddings (shared by ingest and query — never re-embed with another model)

_embedder: TextEmbedding | None = None


def get_embedder() -> TextEmbedding:
    global _embedder
    if _embedder is None:
        _embedder = TextEmbedding(model_name=EMBED_MODEL_NAME)
    return _embedder


def embed_passages(texts: Iterable[str]) -> list[list[float]]:
    """Document-side embeddings (ingest)."""
    return [v.tolist() for v in get_embedder().passage_embed(list(texts))]


def embed_query(text: str) -> list[float]:
    """Query-side embedding (bge query prefix handled by fastembed)."""
    return next(iter(get_embedder().query_embed([text]))).tolist()


# --- hybrid retrieval -----------------------------------------------------------

async def hybrid_retrieve(
    query_text: str,
    *,
    top_k: int = 10,
    limit: int = 5,
    driver: AsyncDriver | None = None,
) -> tuple[list[dict], set[str]]:
    """Run the hybrid vector+graph query for an interest string.

    Returns ``(rows, allowed_ids)`` where each row carries person_id, name,
    role, school, score and matched enterprises/topics, and ``allowed_ids``
    is the whitelist of person + enterprise ids the orchestrator may render.
    """
    own_driver = driver is None
    drv = driver or get_driver()
    try:
        vector = embed_query(query_text)
        async with drv.session(database=get_database()) as session:
            result = await session.run(
                HYBRID_QUERY, vector=vector, top_k=top_k, limit=limit
            )
            rows = await result.data()
    finally:
        if own_driver:
            await drv.close()
    allowed_ids: set[str] = set()
    for row in rows:
        allowed_ids.add(row["person_id"])
        for match in row["matches"] or []:
            if match.get("id"):
                allowed_ids.add(match["id"])
    return rows, allowed_ids


def format_rows(rows: list[dict], top: int = 3) -> str:
    lines = []
    for row in rows[:top]:
        matched = ", ".join(
            f"{m['name']} ({m['topic']})" for m in (row["matches"] or []) if m
        ) or "—"
        lines.append(
            f"  - [{row['score']:.3f}] {row['name']} ({row['role']}, "
            f"{row['school']}, id={row['person_id']}) | matches: {matched}"
        )
    return "\n".join(lines)


async def _main() -> None:
    fixtures = [
        "cybersecurity data science talent acquisition",
        "networking entrepreneurship events",
        "mentoring wellbeing community",
        "data quality methodology network analysis",
    ]
    drv = get_driver()
    try:
        for q in fixtures:
            rows, allowed = await hybrid_retrieve(q, top_k=10, limit=5, driver=drv)
            print(f"\n== {q!r}")
            print(format_rows(rows, top=3))
            print(f"  allowed_ids: {sorted(allowed)}")
    finally:
        await drv.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(_main())

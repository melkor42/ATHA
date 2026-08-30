"""backend/graph_queries.py — shared embedding model + Neo4j Aura connection.

Single source of truth for:
  * the local embedding model (fastembed BAAI/bge-small-en-v1.5, 384 dims) —
    SAME model at ingest and query time;
  * the Neo4j Aura connection (.env at repo root, loaded via python-dotenv).

The knowledge graph (passages, questions, ontology) is queried by
backend/knowledge.py and backend/skeleton.py. The old person-network hybrid
retrieval retired with the synthetic dataset.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

from dotenv import dotenv_values
from fastembed import TextEmbedding
from neo4j import AsyncGraphDatabase, AsyncDriver

# --- constants ----------------------------------------------------------------

EMBED_MODEL_NAME = "BAAI/bge-small-en-v1.5"   # local fastembed model, 384 dims
EMBED_DIMS = 384                               # MUST match the vector index


# --- environment / driver ------------------------------------------------------

# keys that may arrive via platform env (Render) instead of a .env file
_PLATFORM_KEYS = (
    "NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD",
    "NEO4J_DATABASE", "OPENROUTER_API_KEY",
)


def load_env() -> dict[str, str]:
    """Merged config: .env values from the repo root, overridden by platform
    env vars on conflict (hosts like Render inject secrets as platform env
    and ship no .env file). Tolerates a UTF-8 BOM on the first .env key.
    Locally (.env present, no platform vars) the result is unchanged.
    """
    env_path = Path(__file__).resolve().parents[1] / ".env"
    values = dotenv_values(env_path)
    merged = {k.lstrip("\ufeff"): v for k, v in values.items() if v is not None}
    for key in _PLATFORM_KEYS:
        if os.environ.get(key):
            merged[key] = os.environ[key]  # platform env wins
    return merged


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


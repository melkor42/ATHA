"""backend/main.py — FastAPI orchestrator for the SIGNAL wow-page (ticket 10).

Pipeline per POST /api/experience {text}:
  Agent 1 (PersonaModel) -> hybrid retrieval (graph_queries.hybrid_retrieve,
  REUSED from ticket 09) -> Agent 2 (ExperienceSchema, prompt includes persona
  JSON + data pool WITH ids) -> verify() filters entity_ids against the
  whitelist -> hydrate() fills the entities map from Neo4j -> ExperienceSchema
  JSON. Any failure degrades to DEFAULT_EXPERIENCE — the endpoint never crashes.

Plus: CORS for the Vite dev server, /health, in-memory rate limit
(30 req/day per IP), per-request tracing to backend/trace.jsonl, and a
sha256(text)-keyed response cache so repeat runs cost zero LLM calls.

Run:  uvicorn main:app --reload   (from backend/)
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from collections import OrderedDict
from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from neo4j import AsyncDriver
from pydantic import BaseModel

from agents import (
    FALLBACK_MODEL,
    PRIMARY_MODEL,
    experience_agent,
    get_client,
    persona_agent,
    render_pool,
)
from graph_queries import get_database, get_driver, hybrid_retrieve
from ui_schema import (
    ActionType,
    Button,
    ComponentType,
    EntityPayload,
    EntityType,
    ExperienceSchema,
    Layout,
    Theme,
    UINode,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
log = logging.getLogger("signal.main")

TRACE_FILE = Path(__file__).resolve().parent / "trace.jsonl"
RATE_LIMIT_PER_DAY = 30
CACHE_MAX = 256
TOP_K, LIMIT = 10, 6
EVENT_LIMIT = 6

app = FastAPI(title="SIGNAL wow-page orchestrator", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- graceful degradation ----------------------------------------------------------

DEFAULT_EXPERIENCE = ExperienceSchema(
    layout=Layout.SINGLE_COLUMN,
    theme=Theme.GARDEN,
    sections=[
        UINode(
            component=ComponentType.TEXT_BLOCK,
            title="Welcome to SIGNAL",
            text=(
                "The network is composing your personal page. This time the "
                "connection was too quiet to ground it in live data — try "
                "again in a moment."
            ),
            button=Button(label="Try again", action=ActionType.SHOW_DETAILS),
        )
    ],
    entities={},
)

# --- state -----------------------------------------------------------------------------

_response_cache: "OrderedDict[str, dict]" = OrderedDict()
_rate_counts: dict[str, tuple[str, int]] = {}
_driver: AsyncDriver | None = None


def get_app_driver() -> AsyncDriver:
    global _driver
    if _driver is None:
        _driver = get_driver()
    return _driver


@app.on_event("shutdown")
async def _shutdown() -> None:
    if _driver is not None:
        await _driver.close()


class ExperienceRequest(BaseModel):
    text: str


# --- hydration queries (server-side, by id) ----------------------------------------------

PERSONS_BY_ID_QUERY = """
MATCH (p:Person) WHERE p.id IN $ids
OPTIONAL MATCH (p)-[:ATTENDS]->(s:School)
OPTIONAL MATCH (p)-[:INTERESTED_IN]->(t:Topic)
OPTIONAL MATCH (p)-[:MENTORED_BY]->(m:Person)
RETURN p.id AS id, p.name AS name, p.role AS role,
       p.program_or_role AS program, p.skills AS skills,
       s.name AS school, collect(DISTINCT t.name) AS topics,
       m.name AS mentor
"""

ENTERPRISES_BY_ID_QUERY = """
MATCH (e:Enterprise) WHERE e.id IN $ids
OPTIONAL MATCH (e)-[:SEEKS_EXPERTISE]->(t:Topic)
RETURN e.id AS id, e.name AS name, e.sector AS sector, e.size AS size,
       e.hq AS hq, e.contact_name AS contact_name, e.contact_role AS contact_role,
       collect(DISTINCT t.name) AS topics
"""

EVENTS_BY_ID_QUERY = """
MATCH (ev:Event) WHERE ev.id IN $ids
RETURN ev.id AS id, ev.name AS name, ev.date AS date, ev.kind AS kind,
       ev.location AS location, ev.highlights AS highlights
"""

EVENTS_QUERY = """
MATCH (ev:Event)
RETURN ev.id AS id, ev.name AS name, ev.date AS date, ev.kind AS kind,
       ev.location AS location, ev.highlights AS highlights
ORDER BY CASE WHEN ev.kind = 'upcoming' THEN 0 ELSE 1 END, ev.date
LIMIT $limit
"""


async def _hydrate(driver: AsyncDriver, ids: set[str]) -> dict[str, EntityPayload]:
    """Fill the entities map from Neo4j for exactly the given ids."""
    entities: dict[str, EntityPayload] = {}
    ids_list = list(ids)
    async with driver.session(database=get_database()) as session:
        persons = await (await session.run(PERSONS_BY_ID_QUERY, ids=ids_list)).data()
        enterprises = await (
            await session.run(ENTERPRISES_BY_ID_QUERY, ids=ids_list)
        ).data()
        events = await (await session.run(EVENTS_BY_ID_QUERY, ids=ids_list)).data()
    for row in persons:
        story = None
        if row.get("mentor"):
            story = f"Found a mentor through the network: {row['mentor']}."
        entities[row["id"]] = EntityPayload(
            type=EntityType.PERSON,
            name=row["name"],
            school=row.get("school"),
            topics=[t for t in (row.get("topics") or []) if t],
            role=row.get("program") or row.get("role"),
            story=story,
        )
    for row in enterprises:
        contact = row.get("contact_name")
        if contact and row.get("contact_role"):
            contact = f"{contact} ({row['contact_role']})"
        entities[row["id"]] = EntityPayload(
            type=EntityType.ENTERPRISE,
            name=row["name"],
            sector=row.get("sector"),
            size=row.get("size"),
            hq=row.get("hq"),
            contact=contact,
            topics=[t for t in (row.get("topics") or []) if t],
        )
    for row in events:
        entities[row["id"]] = EntityPayload(
            type=EntityType.EVENT,
            name=row["name"],
            date=row.get("date"),
            location=row.get("location"),
            highlights=[h for h in (row.get("highlights") or []) if h],
        )
    return entities


async def enrich_persons_async(rows: list[dict]) -> list[dict]:
    """Attach mentor names to retrieval rows so mentor stories stay grounded."""
    by_id = {r["person_id"]: r for r in rows}
    if not by_id:
        return rows
    async with get_app_driver().session(database=get_database()) as session:
        result = await session.run(
            "UNWIND $ids AS pid "
            "MATCH (p:Person {id: pid})-[:MENTORED_BY]->(m:Person) "
            "RETURN pid AS id, m.name AS mentor",
            ids=list(by_id),
        )
        for rec in await result.data():
            if rec["id"] in by_id:
                by_id[rec["id"]]["mentor_name"] = rec["mentor"]
    return rows


async def fetch_events(limit: int = EVENT_LIMIT) -> list[dict]:
    async with get_app_driver().session(database=get_database()) as session:
        return await (await session.run(EVENTS_QUERY, limit=limit)).data()


# --- verify + hydrate ----------------------------------------------------------------------


def verify(schema: ExperienceSchema, allowed_ids: set[str]) -> ExperienceSchema:
    """Whitelist-filter: keep only sections whose entity_ids survive filtering.

    TextBlocks carry no entity references and always survive; a section that
    references entities of which none are whitelisted is dropped (its claims
    would be ungrounded). Sections beyond six are cut.
    """
    kept: list[UINode] = []
    for section in schema.sections:
        if section.component == ComponentType.TEXT_BLOCK and not section.entity_ids:
            kept.append(section)
            continue
        filtered = [eid for eid in section.entity_ids if eid in allowed_ids]
        if filtered:
            section.entity_ids = filtered
            kept.append(section)
        else:
            log.info("verify(): dropped section %s (no whitelisted entity_ids)",
                     section.component.value)
    if not kept:
        kept = [
            UINode(
                component=ComponentType.TEXT_BLOCK,
                title="SIGNAL",
                text=(
                    "Your page is being recomposed — the first draft referenced "
                    "data outside the verified pool."
                ),
            )
        ]
    return ExperienceSchema(
        layout=schema.layout,
        theme=schema.theme,
        sections=kept[:6],
        entities={},
    )


# --- rate limit + cache + trace -----------------------------------------------------------------


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _check_rate_limit(ip: str) -> bool:
    today = date.today().isoformat()
    day, count = _rate_counts.get(ip, (today, 0))
    if day != today:
        count = 0
    if count >= RATE_LIMIT_PER_DAY:
        return False
    _rate_counts[ip] = (today, count + 1)
    return True


def _append_trace(record: dict) -> None:
    try:
        with TRACE_FILE.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError as exc:  # tracing must never break the request
        log.warning("trace write failed: %s", exc)


# --- endpoints -----------------------------------------------------------------------------------


@app.get("/health")
async def health() -> dict:
    try:
        async with get_app_driver().session(database=get_database()) as session:
            await session.run("RETURN 1")
        neo4j = "up"
    except Exception as exc:  # noqa: BLE001 — health reports, never crashes
        neo4j = f"down: {exc}"
    return {"status": "ok", "neo4j": neo4j,
            "models": {"primary": PRIMARY_MODEL, "fallback": FALLBACK_MODEL}}


@app.post("/api/experience")
async def build_experience(body: ExperienceRequest, request: Request) -> dict:
    ip = _client_ip(request)
    if not _check_rate_limit(ip):
        raise HTTPException(status_code=429,
                            detail=f"Rate limit: {RATE_LIMIT_PER_DAY} requests/day.")

    text = (body.text or "").strip()
    if not text:
        raise HTTPException(status_code=422, detail="Empty input text.")

    key = hashlib.sha256(text.encode("utf-8")).hexdigest()
    started = time.perf_counter()
    cached = _response_cache.get(key)
    if cached is not None:
        _response_cache.move_to_end(key)
        _append_trace({
            "ts": time.time(), "input": text, "persona": cached.get("persona"),
            "allowed_ids": cached.get("allowed_ids"),
            "ui_schema": cached.get("experience"), "latency_ms": 0,
            "cache_hit": True,
        })
        return cached

    persona = None
    allowed_ids: list[str] = []
    draft_schema = None
    experience = DEFAULT_EXPERIENCE.model_dump()
    try:
        client = get_client()
        persona_model = await persona_agent(text, client)
        persona = persona_model.model_dump()

        query_text = " ".join(persona_model.interests) or text
        rows, allowed = await hybrid_retrieve(
            query_text, top_k=TOP_K, limit=LIMIT, driver=get_app_driver()
        )
        rows = await enrich_persons_async(rows)
        events = await fetch_events()
        ids = set(allowed) | {ev["id"] for ev in events}
        allowed_ids = sorted(ids)

        pool_text = render_pool(rows, events)
        draft = await experience_agent(persona_model, pool_text, ids, client)
        draft_schema = draft.model_dump()
        verified = verify(draft, ids)
        entities = await _hydrate(get_app_driver(),
                                  {eid for s in verified.sections
                                   for eid in s.entity_ids})
        verified.entities = entities
        experience = verified.model_dump()
    except Exception as exc:  # noqa: BLE001 — DEFAULT_EXPERIENCE, never crash
        log.exception("pipeline failed -> DEFAULT_EXPERIENCE: %s", exc)

    payload = {"persona": persona, "experience": experience,
               "allowed_ids": allowed_ids}
    _response_cache[key] = payload
    while len(_response_cache) > CACHE_MAX:
        _response_cache.popitem(last=False)

    latency_ms = int((time.perf_counter() - started) * 1000)
    _append_trace({
        "ts": time.time(), "input": text, "persona": persona,
        "allowed_ids": allowed_ids, "draft_schema": draft_schema,
        "ui_schema": experience,
        "latency_ms": latency_ms, "cache_hit": False,
    })
    log.info("composed experience in %d ms (sections=%d)",
             latency_ms, len(experience.get("sections", [])))
    return payload


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

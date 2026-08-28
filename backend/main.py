"""backend/main.py — FastAPI orchestrator for the SIGNAL wow-page (ticket 10).

Pipeline per POST /api/experience {role, topics, style}:
  visitor's role selection -> deterministic PersonaModel synthesis (no LLM)
  -> hybrid retrieval over the selected topics (graph_queries.hybrid_retrieve,
  REUSED from ticket 09) -> compose agent (ExperienceSchema, prompt includes
  persona JSON + data pool WITH ids) -> the visitor-chosen style overrides
  the schema's mode (prompt stays untouched) -> verify() filters entity_ids
  against the whitelist -> hydrate() fills the entities map from Neo4j ->
  ExperienceSchema JSON. Any failure degrades to DEFAULT_EXPERIENCE — the
  endpoint never crashes.

Plus: CORS for the Vite dev server, /health, in-memory rate limit
(30 req/day per IP), per-request tracing to backend/trace.jsonl, and a
role+topics+style-keyed response cache so repeat runs cost zero LLM calls.

Run:  uvicorn main:app --reload   (from backend/)
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
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
    render_knowledge_bundle,
    render_pool,
)
from graph_queries import get_database, get_driver, get_embedder, hybrid_retrieve
from knowledge import knowledge_for
from ui_schema import (
    ActionType,
    Button,
    ColorToken,
    ComponentType,
    EntityPayload,
    EntityType,
    ExperienceSchema,
    Layout,
    PersonaModel,
    Spectrum,
    StyleMode,
    UINode,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
log = logging.getLogger("signal.main")

TRACE_FILE = Path(__file__).resolve().parent / "trace.jsonl"
RATE_LIMIT_PER_DAY = 30
CACHE_MAX = 512  # role x topics x style x visitor_state cardinality
TOP_K, LIMIT = 10, 6
EVENT_LIMIT = 6
VISITOR_STATES = {"discovering", "deciding", "preparing", "experienced"}

app = FastAPI(title="SIGNAL wow-page orchestrator", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"]
    + [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- graceful degradation ----------------------------------------------------------

DEFAULT_EXPERIENCE = ExperienceSchema(
    layout=Layout.SINGLE_COLUMN,
    spectrum=Spectrum.TERRA,
    mode=StyleMode.NONE,
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


@app.on_event("startup")
async def _warmup() -> None:
    """Warm the embedder (initiates the first-use fastembed model download,
    ~90MB — intended) and the Neo4j driver so the first real request starts
    warm. A paused Aura or a slow download only warns: startup never fails."""
    try:
        get_embedder()
    except Exception as exc:  # noqa: BLE001 — warm-up is best-effort
        log.warning("warm-up: embedder not ready yet: %s", exc)
    try:
        get_app_driver()
    except Exception as exc:  # noqa: BLE001 — warm-up is best-effort
        log.warning("warm-up: Neo4j driver not ready yet: %s", exc)


@app.on_event("shutdown")
async def _shutdown() -> None:
    if _driver is not None:
        await _driver.close()


class ExperienceRequest(BaseModel):
    role: str
    topics: list[str] = []
    style: StyleMode | None = None
    visitor_state: str | None = None


# --- role selection ---------------------------------------------------------------
# The persona modeler is gone: the visitor picks a role and (optionally) topics
# in the AI Corner; the PersonaModel the compose agent consumes is synthesized
# deterministically here. The curated topic lists double as the retrieval
# fallback when the visitor selects none.

ROLE_PROFILES: dict[str, dict] = {
    "student": {
        "topics": ["networking", "mentoring", "career development",
                   "events", "entrepreneurship"],
        "tone": "playful",
        "accent_color": ColorToken.ACCENT,
        "expertise_level": "advanced",
        "perspective": "talent",
    },
    "warwick": {
        "topics": ["mentoring", "wellbeing", "community",
                   "events", "leadership"],
        "tone": "warm",
        "accent_color": ColorToken.SUCCESS,
        "expertise_level": "expert",
        "perspective": "education",
    },
    "business": {
        "topics": ["talent acquisition", "consulting", "fintech",
                   "sustainability", "entrepreneurship"],
        "tone": "direct",
        "accent_color": ColorToken.PRIMARY,
        "expertise_level": "expert",
        "perspective": "enterprise",
    },
}


def resolve_topics(role: str, requested: list[str]) -> list[str]:
    """Keep only topics from the role's curated list (order-preserving,
    de-duplicated); an empty or fully unknown selection means CAM chooses —
    the role's full list."""
    curated = ROLE_PROFILES[role]["topics"]
    allowed = set(curated)
    picked = list(dict.fromkeys(t.strip().lower() for t in requested if t and t.strip().lower() in allowed))
    return picked or list(curated)


def synthesize_persona(role: str, topics: list[str]) -> PersonaModel:
    profile = ROLE_PROFILES[role]
    return PersonaModel(
        interests=topics,
        tone=profile["tone"],
        accent_color=profile["accent_color"],
        expertise_level=profile["expertise_level"],
        perspective=profile["perspective"],
    )


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
        spectrum=schema.spectrum,
        mode=schema.mode,
        sections=kept[:6],
        entities={},
    )


# round-trip smoke: verify() rebuilds the schema naming fields explicitly —
# if spectrum/mode were ever dropped there, this assert fails at import.
assert verify(DEFAULT_EXPERIENCE, set()).spectrum == DEFAULT_EXPERIENCE.spectrum
assert verify(DEFAULT_EXPERIENCE, set()).mode == DEFAULT_EXPERIENCE.mode


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
        log.warning("rate limit exceeded for %s -> returning 429", ip)
        raise HTTPException(status_code=429,
                            detail=f"Rate limit: {RATE_LIMIT_PER_DAY} requests/day.")

    role = (body.role or "").strip().lower()
    if role not in ROLE_PROFILES:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown role: {role!r}. Expected one of {sorted(ROLE_PROFILES)}.",
        )
    topics = resolve_topics(role, body.topics)
    style = body.style  # StyleMode | None, pydantic-validated
    visitor_state = ((body.visitor_state or "").strip().lower() or None)
    if visitor_state is not None and visitor_state not in VISITOR_STATES:
        visitor_state = None  # unknown gate state -> no state emphasis
    log.info("experience request: role=%s topics=%s style=%s state=%s",
             role, topics, style.value if style else None, visitor_state)

    key = hashlib.sha256(
        f"{role}|{'.'.join(topics)}|{style.value if style else ''}|"
        f"{visitor_state or ''}".encode("utf-8")
    ).hexdigest()
    started = time.perf_counter()
    cached = _response_cache.get(key)
    if cached is not None:
        log.info("cache hit for role=%s style=%s", role,
                 style.value if style else None)
        _response_cache.move_to_end(key)
        _append_trace({
            "ts": time.time(), "role": role, "topics": topics,
            "style": style.value if style else None,
            "persona": cached.get("persona"),
            "allowed_ids": cached.get("allowed_ids"),
            "ui_schema": cached.get("experience"), "latency_ms": 0,
            "cache_hit": True,
        })
        return cached
    log.info("cache miss for role=%s style=%s", role,
             style.value if style else None)

    persona = None
    allowed_ids: list[str] = []
    draft_schema = None
    knowledge_qids: list[str] = []
    degraded_reason: str | None = None
    experience = DEFAULT_EXPERIENCE.model_dump()
    try:
        client = get_client()
        persona_model = synthesize_persona(role, topics)
        persona = persona_model.model_dump()

        query_text = " ".join(persona_model.interests)
        retrieval_started = time.perf_counter()
        rows, allowed = await hybrid_retrieve(
            query_text, top_k=TOP_K, limit=LIMIT, driver=get_app_driver()
        )
        rows = await enrich_persons_async(rows)
        events = await fetch_events()
        log.info("retrieval finished in %d ms (rows=%d, events=%d)",
                 int((time.perf_counter() - retrieval_started) * 1000),
                 len(rows), len(events))
        ids = set(allowed) | {ev["id"] for ev in events}
        allowed_ids = sorted(ids)

        pool_text = render_pool(rows, events)

        # knowledge layer: the visitor's most important questions, answered
        # from the digested ATHA canon. Degrades silently — compose works
        # without knowledge, it just can't answer beyond the data pool.
        knowledge_text = ""
        try:
            bundle = await knowledge_for(
                role, visitor_state, driver=get_app_driver(),
                database=get_database(), top_questions=4, max_answers=2)
            knowledge_text = render_knowledge_bundle(bundle)
            knowledge_qids = [q["id"] for q in bundle["questions"]]
            log.info("knowledge bundle: %d questions (%s)",
                     len(knowledge_qids), ", ".join(knowledge_qids))
        except Exception as exc:  # noqa: BLE001 — knowledge is an enhancement
            log.warning("knowledge retrieval failed -> compose without "
                        "knowledge: %s", exc)

        log.info("llm compose starting (model handled in agents.py)")
        llm_started = time.perf_counter()
        draft = await experience_agent(persona_model, pool_text, ids, client,
                                       knowledge_text=knowledge_text)
        log.info("llm compose finished in %d ms",
                 int((time.perf_counter() - llm_started) * 1000))
        # the visitor's style pick wins over the agent's temperament choice —
        # server-side, deterministic, prompt untouched. No style chosen:
        # keep the agent's mode (the diversity rule).
        if style is not None:
            draft.mode = style
        draft_schema = draft.model_dump()
        verified = verify(draft, ids)
        entities = await _hydrate(get_app_driver(),
                                  {eid for s in verified.sections
                                   for eid in s.entity_ids})
        verified.entities = entities
        experience = verified.model_dump()
    except Exception as exc:  # noqa: BLE001 — DEFAULT_EXPERIENCE, never crash
        log.exception("pipeline failed -> DEFAULT_EXPERIENCE: %s", exc)
        degraded_reason = f"{type(exc).__name__}: {exc}"

    payload = {"persona": persona, "experience": experience,
               "allowed_ids": allowed_ids,
               "knowledge_questions": knowledge_qids}
    if degraded_reason is not None:
        # surfaced as a console.error by the frontend — makes a paused or
        # deleted Aura instance impossible to miss during development
        payload["degraded"] = True
        payload["degraded_reason"] = degraded_reason
    else:
        _response_cache[key] = payload
        while len(_response_cache) > CACHE_MAX:
            _response_cache.popitem(last=False)

    latency_ms = int((time.perf_counter() - started) * 1000)
    _append_trace({
        "ts": time.time(), "role": role, "topics": topics,
        "style": style.value if style else None,
        "visitor_state": visitor_state,
        "persona": persona,
        "allowed_ids": allowed_ids, "draft_schema": draft_schema,
        "knowledge_questions": knowledge_qids,
        "ui_schema": experience,
        "latency_ms": latency_ms, "cache_hit": False,
    })
    log.info("composed experience in %d ms (sections=%d)",
             latency_ms, len(experience.get("sections", [])))
    return payload


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

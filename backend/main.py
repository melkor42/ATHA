"""backend/main.py — FastAPI orchestrator for the ATHA knowledge page.

Pipeline per POST /api/experience {role, topics?, style?, visitor_state?,
intent?, facet?, free_text?}:
  deterministic skeleton plan (skeleton.build_skeleton: anchor questions ->
  facet -> vector extras -> edition/rhythm/layers tail, all from the
  knowledge graph) -> copywriter agent writes the title/text copy for the
  slots AND ranks them for the current visitor (order/lead/source_i; the
  structure itself never comes from the model) -> main.py hydrates each slot
  into its atomic node (Statement / FactList / StageFlow / PartnerLayers,
  structured payloads filtered by source_i) -> the visitor's style overrides
  the mode -> verify() -> ExperienceSchema JSON (entities empty). Any failure
  degrades to DEFAULT_EXPERIENCE — the endpoint never crashes.

`topics` is accepted for API stability but ignored (the skeleton plans from
role/state/intent/facet/free_text).

Plus: CORS for the Vite dev server, /health, in-memory rate limit
(30 req/day per IP), per-request tracing to backend/trace.jsonl, and a
role+state+intent+facet+free_text+style-keyed response cache so repeat runs
cost zero LLM calls.

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
from fastapi.staticfiles import StaticFiles
from neo4j import AsyncDriver
from pydantic import BaseModel

from agents import (
    FALLBACK_MODEL,
    PRIMARY_MODEL,
    copywriter_agent,
    get_client,
)
from graph_queries import get_database, get_driver, get_embedder
from skeleton import (
    INTENTS,
    align_copy,
    build_skeleton,
    deterministic_fallback,
    known_facet_ids,
    render_slots_for_prompt,
)
from ui_schema import (
    ActionType,
    Button,
    ColorToken,
    ComponentType,
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
CACHE_MAX = 512  # role x state x intent x facet x free_text x style cardinality
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
            title="Welcome to ATHA",
            text=(
                "ATHA is composing your page. This time the connection was "
                "too quiet to ground it in live data — try again in a moment."
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
    intent: str | None = None
    facet: str | None = None
    free_text: str | None = None


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

# Skeleton architecture: spectrum and base mode are fixed per role (the old
# prompt's tone->mode rule, made deterministic). A visitor style pick still
# overrides the mode; spectrum always stays the role's.
ROLE_SPECTRUM = {
    "student": Spectrum.AURORA,
    "warwick": Spectrum.MYCELIUM,
    "business": Spectrum.VOID,
}
ROLE_MODE = {
    "student": StyleMode.RETRO,      # playful -> retro
    "warwick": StyleMode.ORGANIC,    # warm -> organic
    "business": StyleMode.MINIMAL,   # direct -> minimal
}


def synthesize_persona(role: str) -> PersonaModel:
    profile = ROLE_PROFILES[role]
    return PersonaModel(
        interests=list(profile["topics"]),
        tone=profile["tone"],
        accent_color=profile["accent_color"],
        expertise_level=profile["expertise_level"],
        perspective=profile["perspective"],
    )


# --- verify --------------------------------------------------------------------------------


def verify(schema: ExperienceSchema, allowed_ids: set[str]) -> ExperienceSchema:
    """Whitelist-filter: keep only sections whose entity_ids survive filtering.

    The structural components (TextBlock + the ATHA atomic set) carry no
    entity references and always survive; a section that references entities
    of which none are whitelisted is dropped (its claims would be ungrounded).
    Sections beyond ten are cut. (In the skeleton architecture entity_ids are
    always empty, so the filter is dormant but stays armed for a future
    return of entity cards.)
    """
    structural = {
        ComponentType.TEXT_BLOCK, ComponentType.STATEMENT,
        ComponentType.FACT_LIST, ComponentType.STAGE_FLOW,
        ComponentType.PARTNER_LAYERS,
    }
    kept: list[UINode] = []
    for section in schema.sections:
        if section.component in structural and not section.entity_ids:
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
                title="ATHA",
                text=(
                    "Your page is being recomposed — the first draft "
                    "referenced data outside the verified pool."
                ),
            )
        ]
    return ExperienceSchema(
        layout=schema.layout,
        spectrum=schema.spectrum,
        mode=schema.mode,
        sections=kept[:10],
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
    # `topics` is accepted for API stability but ignored — the skeleton
    # plans the page from role/state/intent/facet/free_text instead.
    style = body.style  # StyleMode | None, pydantic-validated
    visitor_state = ((body.visitor_state or "").strip().lower() or None)
    if visitor_state is not None and visitor_state not in VISITOR_STATES:
        visitor_state = None  # unknown gate state -> no state emphasis
    intent = ((body.intent or "").strip().lower() or None)
    if intent is not None:
        spec = INTENTS.get(intent)
        if spec is None or ("roles" in spec and role not in spec["roles"]):
            intent = None  # unknown or role-incompatible intent -> ignore
    facet = ((body.facet or "").strip().lower() or None)
    if facet is not None and facet not in known_facet_ids():
        facet = None  # unknown facet -> ignore
    free_text = ((body.free_text or "").strip() or None)
    if free_text is not None:
        free_text = " ".join(free_text.split())[:400] or None
    log.info("experience request: role=%s state=%s intent=%s facet=%s "
             "free_text=%s style=%s", role, visitor_state, intent, facet,
             bool(free_text), style.value if style else None)

    key = hashlib.sha256(
        f"{role}|{visitor_state or ''}|{intent or ''}|{facet or ''}|"
        f"{free_text or ''}|{style.value if style else ''}".encode("utf-8")
    ).hexdigest()
    started = time.perf_counter()
    cached = _response_cache.get(key)
    if cached is not None:
        log.info("cache hit for role=%s style=%s", role,
                 style.value if style else None)
        _response_cache.move_to_end(key)
        _append_trace({
            "ts": time.time(), "role": role,
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
    knowledge_qids: list[str] = []
    suggestions: list[dict] = []
    copy_source: str | None = None
    slot_kinds: list[str] = []
    degraded_reason: str | None = None
    experience = DEFAULT_EXPERIENCE.model_dump()
    try:
        client = get_client()
        persona_model = synthesize_persona(role)
        persona = persona_model.model_dump()

        # 1. deterministic page plan from the knowledge graph (structure,
        #    grounding and section order never come from the model)
        retrieval_started = time.perf_counter()
        skel = await build_skeleton(
            role, visitor_state, driver=get_app_driver(),
            database=get_database(), intent=intent, facet=facet,
            free_text=free_text)
        slots = skel["slots"]
        knowledge_qids = skel["anchor_qids"]
        suggestions = skel["suggestions"]
        slot_kinds = [s["kind"] for s in slots]
        log.info("skeleton built in %d ms: %d slots %s",
                 int((time.perf_counter() - retrieval_started) * 1000),
                 len(slots), slot_kinds)

        # 2. copy + ranking: one LLM call over the slots. Any failure falls
        #    back to deterministic template copy in slot order — the page
        #    always renders, and the atomic structure is never model-authored.
        try:
            llm_started = time.perf_counter()
            raw = await copywriter_agent(
                render_slots_for_prompt(slots),
                ROLE_PROFILES[role]["tone"], client,
                visitor_state=visitor_state, question=free_text)
            plan, copy_source = align_copy(slots, raw)
            log.info("copywriter finished in %d ms (source=%s)",
                     int((time.perf_counter() - llm_started) * 1000),
                     copy_source)
        except Exception as exc:  # noqa: BLE001 — copy is degradable
            log.warning("copywriter failed -> deterministic copy: %s", exc)
            plan = [{"slot": s, "title": c["title"], "text": c["text"],
                     "si": list(range(len(s["sources"])))}
                    for s, c in zip(slots, deterministic_fallback(slots))]
            copy_source = "fallback"

        # 3. assemble the ExperienceSchema: one atomic node per plan entry.
        #    The copywriter ranks; it never deletes. Edition facts follow the
        #    model's promotion order, the rhythm and the layers keep theirs —
        #    for those two the sequence IS the information.
        sections = []
        for entry in plan:
            slot = entry["slot"]
            structured = slot.get("structured") or []
            promoted = [structured[j] for j in entry["si"]
                        if j < len(structured)]
            chosen = promoted + [s for s in structured if s not in promoted]
            node = {"title": entry["title"][:80], "text": entry["text"][:500]}
            if slot["kind"] == "edition":
                node.update(component=ComponentType.FACT_LIST,
                            facts=chosen[:8])
            elif slot["kind"] == "rhythm":
                node.update(component=ComponentType.STAGE_FLOW,
                            stages=structured)
            elif slot["kind"] == "layers":
                node.update(component=ComponentType.PARTNER_LAYERS,
                            layers=structured)
            else:
                node["component"] = ComponentType.STATEMENT
            sections.append(UINode(**node))
        draft = ExperienceSchema(
            layout=Layout.GRID,
            spectrum=ROLE_SPECTRUM[role],
            mode=style if style is not None else ROLE_MODE[role],
            sections=sections,
            entities={},
        )
        verified = verify(draft, set())
        verified.entities = {}
        experience = verified.model_dump()
    except Exception as exc:  # noqa: BLE001 — DEFAULT_EXPERIENCE, never crash
        log.exception("pipeline failed -> DEFAULT_EXPERIENCE: %s", exc)
        degraded_reason = f"{type(exc).__name__}: {exc}"

    payload = {"persona": persona, "experience": experience,
               "allowed_ids": allowed_ids,
               "knowledge_questions": knowledge_qids,
               "suggestions": suggestions}
    if degraded_reason is not None:
        # surfaced as a console.error by the frontend — makes a paused or
        # deleted Aura instance impossible to miss during development
        payload["degraded"] = True
        payload["degraded_reason"] = degraded_reason
    elif copy_source == "llm":
        # never cache fallback/mixed copy: a throttled-provider window would
        # otherwise keep serving raw-dump text long after recovery
        _response_cache[key] = payload
        while len(_response_cache) > CACHE_MAX:
            _response_cache.popitem(last=False)

    latency_ms = int((time.perf_counter() - started) * 1000)
    _append_trace({
        "ts": time.time(), "role": role, "visitor_state": visitor_state,
        "intent": intent, "facet": facet, "free_text": bool(free_text),
        "style": style.value if style else None,
        "persona": persona,
        "knowledge_questions": knowledge_qids,
        "suggestions": suggestions,
        "slot_kinds": slot_kinds, "copy_source": copy_source,
        "ui_schema": experience,
        "latency_ms": latency_ms, "cache_hit": False,
    })
    log.info("composed experience in %d ms (sections=%d, copy=%s)",
             latency_ms, len(experience.get("sections", [])), copy_source)
    return payload


# --- single-service packaging ---------------------------------------------------
# The Docker image builds the Vue app and ships it as ./static next to this
# file; FastAPI then serves API and SPA from one origin (no CORS). The mount
# comes last so the /api and /health routes above keep priority. In local dev
# the directory does not exist and Vite serves the frontend as before.
STATIC_DIR = Path(__file__).resolve().parent / "static"


class SPAStaticFiles(StaticFiles):
    """index.html is the only file naming the hashed bundles, so a cached
    copy keeps visitors on the previous deploy; Starlette sends no
    Cache-Control at all, leaving the reuse decision to the browser."""

    def file_response(self, full_path, stat_result, scope, status_code=200):
        response = super().file_response(
            full_path, stat_result, scope, status_code)
        name = str(full_path).replace("\\", "/")
        if name.endswith(".html"):
            response.headers["Cache-Control"] = "no-cache"
        elif "/assets/" in name:
            response.headers["Cache-Control"] = (
                "public, max-age=31536000, immutable")
        return response


if STATIC_DIR.is_dir():
    app.mount("/", SPAStaticFiles(directory=STATIC_DIR, html=True), name="spa")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

# Backend: Orchestrator Pipeline

<cite>
**Referenced Files**
- [backend/main.py](file://backend/main.py)
- [backend/ui_schema.py](file://backend/ui_schema.py)
- [backend/graph_queries.py](file://backend/graph_queries.py)
- [backend/agents.py](file://backend/agents.py)
</cite>

## Request walkthrough

`POST /api/experience {text}` in `backend/main.py`:
1. Rate-limit check (30 requests/day per IP, in-memory).
2. Answers-hash cache lookup — repeats return instantly with zero LLM calls.
3. Agent 1 produces a validated PersonaModel (interests, tone, accent_color, expertise_level, perspective).
4. `hybrid_retrieve()` in `graph_queries.py` embeds the persona interests locally (fastembed, 384 dims) and runs the hybrid vector+traversal query, returning rows plus the allowed-id whitelist.
5. Persons are enriched with mentor names; upcoming/past events are fetched; the pool is rendered with ids for Agent 2.
6. Agent 2 composes an ExperienceSchema draft (sections only; it must leave `entities` empty).
7. `verify()` whitelist-filters every `entity_ids` list; sections whose references all fail are dropped; more than six sections are cut.
8. `_hydrate()` fills the entities map from Neo4j by id (persons, enterprises, events).
9. The envelope `{persona, experience, allowed_ids}` is returned and cached.

## Allowlist schema

`backend/ui_schema.py` defines the only UI vocabulary: ComponentType (SignalCard, StudentProfile, EnterpriseCard, EventBanner, TextBlock), ColorToken (primary, accent, success, warning), ActionType, Layout (single_column, grid), Theme (boardroom, festival, garden, ledger). UINode is recursive with children; titles/texts are length-capped and stripped of markup characters.

## Failure strategy

Any exception anywhere in the pipeline degrades to DEFAULT_EXPERIENCE (a calm welcome TextBlock) — the endpoint never crashes. The Neo4j driver carries timeouts (connection_timeout=10, connection_acquisition_timeout=10, max_transaction_retry_time=15) so a dead or paused Aura degrades in ~10 seconds instead of hanging. On OpenRouter 429s the agent layer sleeps 15s between attempts so a per-minute window can recover mid-theater.

## Caching, tracing, rate limiting

Responses are cached by sha256(text) (LRU, 256 entries). Every request appends a trace record (input, persona, allowed_ids, final schema, latency, cache hit) to `backend/trace.jsonl` — the substrate for prompt iteration. CORS allows `http://localhost:5173` and `http://127.0.0.1:5173`.

## Setup and run

`pip install -r requirements.txt`; `python -m uvicorn main:app --host 127.0.0.1 --port 8000` from `backend/`. Credentials come from `.env` at the repo root (gitignored, never committed). `/health` reports Neo4j liveness and the configured models.

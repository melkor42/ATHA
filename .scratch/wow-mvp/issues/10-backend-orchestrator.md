# Build the backend orchestrator

Type: task
Status: open
Blocked by: 01, 02, 03, 04, 05, 07

## Comments

2026-08-13 incident + fix: after a machine sleep the Neo4j driver's stale socket hung every request (including /health) — no timeouts were configured, so the frontend showed "still composing" forever. Fix: driver-level timeouts in graph_queries.py (connection_timeout=10, connection_acquisition_timeout=10, max_transaction_retry_time=15 — top-level kwargs; this driver version rejects a config= dict and connection_max_lifetime), CORS widened to 127.0.0.1:5173, backend restarted detached. A dead Aura now degrades to DEFAULT_EXPERIENCE in ~10s instead of hanging.

2026-08-13 follow-up: free-tier 429s (both free models exhausted after prompt iteration) degraded in 420ms; agents.py now sleeps 15s between attempts on RateLimitError so a per-minute window recovers mid-theater instead of failing instantly.

## Question

Build the FastAPI orchestrator: `persona_agent` (PersonaModel output), backend-side hybrid retrieval returning context + allowed_ids, `ui_agent` (ExperienceSchema output per the composition grammar from [Define the composition grammar](07-composition-grammar.md)) — ui_schema gains a `Theme` enum (boardroom | festival | garden | ledger) as allowlist, Agent 2 selects it per grammar —, `verify()` filtering entity_ids against the whitelist, DEFAULT_EXPERIENCE graceful degradation on any failure, minimal rate-limit middleware, single `POST /api/experience`. English prompts. Plus, absorbed from the legacy task CSV: per-request tracing log (input, persona output, retrieval result, UI output, latency) for prompt iteration, and response caching keyed by answers-hash so repeat runs cost no LLM calls. Resolved when curl with each fixture prompt returns a valid, verified schema.

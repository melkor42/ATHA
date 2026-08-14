# Architecture Overview and Decisions

<cite>
**Referenced Files**
- [docs/architecture-sketch.png](file://docs/architecture-sketch.png)
- [docs/system.html](file://docs/system.html)
- [CONTEXT.md](file://CONTEXT.md)
- [.scratch/wow-mvp/map.md](file://.scratch/wow-mvp/map.md)
</cite>

## System shape

Online path (blue in the sketch): a Vue + Vite frontend collects one free-text onboarding input and POSTs it to `/api/experience`. The FastAPI orchestrator runs Agent 1 (Persona Modeler) to extract a PersonaModel, performs backend-side graph-RAG retrieval (vector search + graph traversal in one Cypher statement against Neo4j Aura), hands persona + retrieved data pool to Agent 2 (Experience Builder), which composes an ExperienceSchema JSON. The orchestrator whitelist-verifies every entity_id against the retrieval result, hydrates the entities map server-side from Neo4j, and returns the schema. The frontend renders it through a Component Registry with a recursive UiRenderer while a client-side theater animates the pipeline steps during the wait.

Offline path (orange): raw synthetic data is transformed, embedded locally, and MERGE-written into Neo4j (graph + vector index) by an idempotent ingest pipeline.

External services: Neo4j Aura (free instance "Signal", graph + 384-dim vector index) and OpenRouter (free chat models only). Embeddings are computed locally, not via OpenRouter.

## Settled decisions and their rationale

- **Allowlist generative UI.** The LLM may only select from enums (components, color tokens, actions, layouts, themes) defined in `backend/ui_schema.py`; `verify()` drops any entity reference outside the retrieval whitelist; the frontend never uses `v-html`. Rationale: personalization without injection or hallucination surface.
- **Signal is derived, not stored.** A "Signal" (person–enterprise match) is computed by the hybrid query over shared Topics; it is never a node. Rationale: keeps the graph honest and the ingest simple.
- **Single POST + client-side theater.** The contract is one JSON response; the waiting theater is client-side. SSE live-sync was considered and deferred as an upgrade path. Rationale: simplest contract first; the theater makes latency feel like depth.
- **Free models only, local embeddings.** OpenRouter serves no embedding models at all, so embeddings run locally via fastembed `BAAI/bge-small-en-v1.5` (384 dims), same model in ingest and query; the Aura vector index is built at 384, not the sketch's original 1536. Chat runs on `nvidia/nemotron-3-super-120b-a12b:free` with `openai/gpt-oss-20b:free` as fallback. Rationale: the user's account is restricted to free models by setting.
- **Current Cypher vector SEARCH syntax.** `db.index.vector.queryNodes` is deprecated; retrieval uses the newer SEARCH clause. Rationale: verified against Aura during research (see `.scratch/wow-mvp/research/03-aura-free-tier-limits.md`).
- **Perspective is the primary persona axis.** enterprise / talent / infrastructure / education — inherited from the four tabs of the page the Wow Page replaces (signal.onemundi.one). It selects the section mix and the design theme.
- **Per-persona design themes.** Design differentiates as visibly as content: themes boardroom / festival / garden / ledger map to frontend CSS variable sets (tint, radius, spacing, border, type emphasis). The LLM selects only the enum.
- **Fully fictional synthetic data**, with exactly one real entity: the upcoming event SIGNAL 001 (Q4 2026, Warwick Business School).
- **Laptop-local demo**, free-tier deployment (Vercel + Render) deferred past the demo.

## Corrections record

Where the pre-grilling sketch (`docs/system.html`) conflicts with later decisions, the later decisions win: 384 not 1536 dims; five components not six (NetworkGraph post-demo); one free-text input not a 3–5 question form; English not German; latency gate relaxed. The research files under `.scratch/wow-mvp/research/` record the evidence behind each correction.

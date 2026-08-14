# Signal Wow-Page MVP — wayfinder map

## Destination

The Signal Wow-Page MVP is acceptable and demo-ready for the 2026-08-24 meeting with the Dean of Warwick Business School: the four canonical personas (`personas/`) each compose a visibly distinct, grounded page — screenshot evidence — and Agent 1's output matches each fixture's expected PersonaModel.

## Notes

- **Execution override**: this map carries build slices as task tickets; the demo is 2026-08-24 (~12 days at charting). Two-person meeting, low stakes, but the wow must impress.
- All deliverables in **English** (Warwick customer).
- **Stack**: Vue + Vite frontend (Component Registry, recursive UiRenderer, no `v-html`); FastAPI + PydanticAI orchestrator; Neo4j Aura instance "Signal"; OpenRouter for chat + embeddings.
- **OpenRouter free models only** (user account setting) — MVP pair per [Choose free-tier OpenRouter model pair](issues/13-free-model-pair.md); ticket 02's picks stay as the post-demo upgrade path. Free rate limits: with the user's $10 credit top-up, ~1000 req/day on free models — rehearsal budget is comfortable.
- **Embeddings are local**: OpenRouter serves none. fastembed `BAAI/bge-small-en-v1.5` (384 dims), same model in ingest and query; the Aura vector index is built at **384**, not the sketch's 1536.
- **API contract** (settled at charting): single `POST /api/experience` → `ExperienceSchema` JSON; the client-side staged-reveal theater fills the wait and shows the real pipeline steps (not live-synced). SSE live-sync is an upgrade path — see Not yet specified.
- **Components shipped**: `TextBlock`, `SignalCard`, `StudentProfile`, `EnterpriseCard`, `EventBanner`. `NetworkGraph` post-demo.
- **Perspective** (Enterprise / Talent / Infrastructure / Education, from signal.onemundi.one) is Agent 1's primary branching axis.
- **Per-persona design grammar** (user request 2026-08-12, superseded 2026-08-14 commit `7a54a75`): design differentiates as visibly as content. The retired Theme enum (boardroom / festival / garden / ledger) gave way to the orthogonal axis grammar: Spectrum (`mycelium | terra | aurora | neon | void`, perspective-driven) × StyleMode (`none | minimal | retro | organic | earth | steampunk`, design-words/temperament-driven), both as CSS variable sets within SIGNAL's identity.
- **Onboarding**: single free-text input; grows into a learning system post-MVP (fog).
- **Synthetic data**: fully fictional; the agent has discretion to invent missing entities, asking the user only when a decision is truly his.
- **Demo script**: prepared contrasting inputs typed live; the Dean may get the keyboard; one rehearsed graceful-degradation run.
- **Latency**: the demo gates on "composes live"; the <10s budget is post-demo (fog).
- **Robustness** (2026-08-13 incident): Neo4j driver carries 10s timeouts — a dead/paused Aura degrades to the default page instead of hanging; backend runs detached.
- **Fixtures** (`personas/`): the acceptance set — each fixture's example prompt = onboarding input; expected PersonaModel JSON = Agent 1 eval; per-persona notes = Agent 2 eval; four screenshots = acceptance evidence.
- **Repo**: local `C:\Users\ASUS GAMING\OneDrive\Signal`, remote https://github.com/melkor42/Signal (auth pending). Secrets in `.env`, gitignored.
- **Skills every session**: grilling, domain-modeling, research, prototype.

## Decisions so far

<!-- index of closed tickets — one line each: gist + link. Grilling-round decisions live in Notes as standing constraints. -->

- [Choose OpenRouter model pair](issues/02-openrouter-model-pair.md) — `claude-sonnet-5` quality / `gemini-3.5-flash-lite` budget; `text-embedding-3-small` confirmed at 1536 dims.
- [Validate Aura free-tier limits](issues/03-aura-free-tier-limits.md) — free tier fits; build must use the new vector `SEARCH` syntax (`queryNodes` deprecated); beware 3-day auto-pause.
- [Compare free hosting options](issues/08-free-hosting-compare.md) — Vercel + Render free post-demo; deployment decision deferred past Aug 24.
- [Provision OpenRouter access](issues/01-provision-openrouter.md) — `.env` + `.gitignore` in repo; key verified (free tier); free-only restriction → selection per ticket 13.
- [Choose free-tier OpenRouter model pair](issues/13-free-model-pair.md) — nemotron-3-super-120b-a12b:free for both agents; embeddings local fastembed @384; corrects ticket 02.
- [Define the composition grammar](issues/07-composition-grammar.md) — perspective→mix+spectrum, tone→register, expertise→density, persona→accent; the original themes boardroom/festival/garden/ledger were replaced by the Spectrum × StyleMode axis grammar (commit `7a54a75`).
- [Build the ingest pipeline](issues/09-ingest-pipeline.md) — 60 persons / 12 enterprises / 20 topics / 8 events ingested; idempotency proven; four sanity clusters disjoint; current vector SEARCH syntax.
- [Build the backend orchestrator](issues/10-backend-orchestrator.md) — nemotron-3-super free + json_schema; 4/4 fixtures pass persona+schema after 5 prompt iterations; themes correct; 79ms cached repeats; tracing + answers-hash cache in.
- [Build the Vue frontend](issues/11-vue-frontend.md) — five components, four theme variable sets, recursive UiRenderer, zero v-html; live render against the real backend verified.

## Not yet specified

- Onboarding growth system: learn the human from little input over time (user's stated vision).
- Real Warwick data swap-in when it arrives.
- 10s latency optimization.
- SSE live-sync stage streaming (upgrade from client-side theater).
- Persona persistence — `(:User)-[:HAS_PERSONA]->(:Persona)` for repeat visitors (legacy CSV M4); post-demo.
- Post-demo free-tier deployment decision (options researched in [Compare free hosting options](issues/08-free-hosting-compare.md)).

## Out of scope

- `NetworkGraph` component for Aug 24 — post-demo cut for build budget.
- Full auth; Ollama offline fallback; Human-Eval admin view; free-form network Q&A — goal-doc backlog.

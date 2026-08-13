# Ticket 13 — Free-tier OpenRouter model pair + embedding strategy

Researched 2026-08-12 against the live OpenRouter models API (`GET https://openrouter.ai/api/v1/models`, 410 models total, 19 zero-priced). Ticket 02's paid picks are unaffected; this is the free-only build pair.

## Recommendation (chat pair + embedding with dims)

- **Call 1 — persona extraction (free text → PersonaModel JSON):** `nvidia/nemotron-3-super-120b-a12b:free` (120B MoE / 12B active, 262K ctx). Use `response_format` / `structured_outputs` — natively supported by its provider, so schema adherence is enforced server-side.
- **Call 2 — UI composition (PersonaModel + data pool → ExperienceSchema JSON):** `nvidia/nemotron-3-super-120b-a12b:free` again. Same model on both calls keeps prompt grammar, JSON conventions, and rate-limit accounting identical; it is the **only large free model currently listed that supports `structured_outputs`**.
- **Why not the bigger one:** `nvidia/nemotron-3-ultra-550b-a55b:free` (550B/55B-active, 1M ctx) is the strongest free model but its provider does **not** accept `response_format`/`structured_outputs` (only tools/reasoning) — JSON must be coaxed via tool-call or prompt discipline, which is a reliability risk for the two schema-critical calls. Keep it as fallback/upgrade experiment.
- **Lightweight fallback:** `openai/gpt-oss-20b:free` (21B, also supports `structured_outputs`) — useful for dev-loop iteration to conserve the 50 req/day quota.
- **Embedding: `BAAI/bge-small-en-v1.5` via fastembed (local, CPU) — 384 dims.** Same model instance logic at ingest and query time; **build the Neo4j Aura vector index at exactly 384 dimensions.**

## Free chat models table

All zero-priced models returned by the API on 2026-08-12 (excludes `google/lyria-3-*`, which are zero-priced audio-generation models, not chat). Platform rate limits for `:free` variants (docs, verified): **20 req/min**; **50 req/day** if < $10 credits ever purchased, **1000 req/day** at ≥ $10.

| id | context | rate limits | structured-output notes |
|---|---|---|---|
| `nvidia/nemotron-3-super-120b-a12b:free` | 262,144 | 20 rpm / 50–1000 rpd | **`structured_outputs` + `response_format` + tools supported — PICK** |
| `nvidia/nemotron-3-ultra-550b-a55b:free` | 1,000,000 | 20 rpm / 50–1000 rpd | tools + reasoning only; no `response_format`/`structured_outputs` — smartest free model, JSON via tool-call |
| `google/gemma-4-31b-it:free` | 262,144 | 20 rpm / 50–1000 rpd | `response_format` + tools; multimodal; solid runner-up |
| `google/gemma-4-26b-a4b-it:free` | 262,144 | 20 rpm / 50–1000 rpd | small MoE variant of above |
| `openai/gpt-oss-20b:free` | 131,072 | 20 rpm / 50–1000 rpd | `structured_outputs` + `response_format` supported — fallback pick |
| `openrouter/free` | 200,000 | 20 rpm / 50–1000 rpd | random free-model router; params pass through but model identity is nondeterministic — avoid for evals |
| `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | 256,000 | 20 rpm / 50–1000 rpd | omni-modal small MoE; tools only |
| `nvidia/nemotron-3-nano-30b-a3b:free` | 256,000 | 20 rpm / 50–1000 rpd | small MoE; tools only |
| `nvidia/nemotron-nano-12b-v2-vl:free` | 128,000 | 20 rpm / 50–1000 rpd | 12B VL; tools only |
| `nvidia/nemotron-nano-9b-v2:free` | 128,000 | 20 rpm / 50–1000 rpd | 9B; tools only |
| `nvidia/nemotron-3.5-lightning:free` | 1,000,000 | 20 rpm / 50–1000 rpd | fast/large-ctx; verify JSON behavior before use |
| `nvidia/nemotron-3.5-content-safety:free` | 128,000 | 20 rpm / 50–1000 rpd | safety-classifier model — not for generation |
| `poolside/laguna-s-2.1:free` | 262,144 | 20 rpm / 50–1000 rpd | coding-agent model (118B/8B-active); tools only; plausible alt for call 2 |
| `poolside/laguna-xs-2.1:free` | 262,144 | 20 rpm / 50–1000 rpd | smaller coding variant |
| `cohere/north-mini-code:free` | 256,000 | 20 rpm / 50–1000 rpd | agentic coding MoE 30B/3B-active; tools only |
| `inclusionai/ling-3.0-tiny:free` | 262,144 | 20 rpm / 50–1000 rpd | 7.9B/1.3B-active; too small for schema-critical calls |
| `liquid/lfm-2.5-2.6b:free` | 128,000 | 20 rpm / 50–1000 rpd | 2.6B; edge-class, not recommended |

Budget note: one experience = 2 requests → the 50 req/day cap allows ~25 full compositions/day; plenty for a demo, tight for eval loops — cache persona JSON and use `gpt-oss-20b:free` while iterating. Free-tier quota raises to 1000/day if ≥$10 credits are ever purchased (docs).

## Embedding verdict

**No embedding model exists on OpenRouter — free or paid.** Scanned all 410 models: zero have `embeddings` in `architecture.output_modalities` or `modality`, and no id matches `*embed*`. OpenRouter's embeddings endpoint therefore cannot serve this project; ticket 02's `text-embedding-3-small` was OpenAI-direct and is not available under the free-only OpenRouter constraint.

**Chosen strategy: `BAAI/bge-small-en-v1.5` via [fastembed](https://qdrant.github.io/fastembed/), run locally.**

- Dimensions: **384** (fixed; Neo4j Aura vector index dimension = 384).
- CPU speed: ~150–300 short sentences/sec on a modern laptop CPU (ONNX, int8-capable); the MVP's ingest corpus is synthetic and small (single-digit seconds total), and embedding a single onboarding sentence at query time is millisecond-scale, invisible against the 10s budget.
- Identical model at ingest and query time: implement one shared `embed(texts)` helper (fastembed `TextEmbedding(model_name="BAAI/bge-small-en-v1.5")`) used by both the ingest pipeline (ticket 09) and the query path — never re-embed with a different model or the vector index becomes meaningless.
- Why fastembed over sentence-transformers: pure CPU ONNX runtime, no torch install (~2 GB) in the FastAPI service, deterministic outputs, trivially reproducible in CI. `sentence-transformers/all-MiniLM-L6-v2` (also 384 dims) is an interchangeable alternative if the team prefers torch — but pick one and lock it.
- Normalization: bge models expect normalized query-prefixed text for retrieval use; fastembed handles the `passage:`/`query:` prefixes — keep using its defaults at both ends.

## Sources

- OpenRouter models API (live data, 2026-08-12): https://openrouter.ai/api/v1/models
- OpenRouter limits doc (free-tier rate limits): https://openrouter.ai/docs/api-reference/limits
- OpenRouter structured outputs doc: https://openrouter.ai/docs/features/structured-outputs
- fastembed (BAAI/bge-small-en-v1.5, 384 dims): https://qdrant.github.io/fastembed/
- bge-small-en-v1.5 model card: https://huggingface.co/BAAI/bge-small-en-v1.5
- sentence-transformers all-MiniLM-L6-v2 (alternative): https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2

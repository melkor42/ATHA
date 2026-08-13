# Choose free-tier OpenRouter model pair

Type: research
Status: resolved
Blocked by: —

## Question

The user's OpenRouter account is restricted to free models only. Using OpenRouter's public models API (`GET https://openrouter.ai/api/v1/models`, pricing fields) as the primary source: (1) list current `:free` chat models and recommend two for sequential structured-output calls (persona extraction; UI-schema JSON composition) — JSON-schema adherence is the quality bar; (2) find whether any free embedding model is served via OpenRouter's embeddings endpoint, with its exact output dimensions — the Neo4j vector index must be built to match; (3) if no free embedding exists, recommend a free local embedding strategy (e.g. sentence-transformers/fastembed model, exact dims) usable identically at ingest and query time, honoring the "same model in ingest and query" rule. Supersedes ticket 02's paid picks for the MVP; 02 remains the post-demo upgrade path.

## Answer

Chat: `nvidia/nemotron-3-super-120b-a12b:free` for both structured calls — the only large free model with native structured outputs (262K ctx); dev fallback `openai/gpt-oss-20b:free`. Free rate limits: 20 req/min, 50 req/day — budget demos and rehearsals accordingly (~25 compositions/day). Embeddings: OpenRouter serves none (free or paid) — ticket 02's embedding claim corrected. Local **fastembed `BAAI/bge-small-en-v1.5`, 384 dims**, same model at ingest and query; the Aura vector index is built at **384**. Full findings: [research/13-free-model-pair.md](../research/13-free-model-pair.md).

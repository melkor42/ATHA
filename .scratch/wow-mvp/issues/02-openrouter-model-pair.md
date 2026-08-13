# Choose OpenRouter model pair

Type: research
Status: resolved
Blocked by: —

## Question

Which current OpenRouter chat model IDs suit two sequential structured-output calls (PydanticAI: persona extraction, then UI-schema composition)? Compare latency, cost, and structured-output reliability; recommend a quality pick and a budget pick. Confirm `openai/text-embedding-3-small` is served via OpenRouter at 1536 dims. The sketch's `anthropic/claude-3.5-sonnet` ID is stale — find current equivalents. Latency matters for the client-side theater feel, but the demo does not gate on <10s.

## Answer

Quality pick `anthropic/claude-sonnet-5` ($2/$10 per 1M, structured outputs, ~1.5–3s); budget pick `google/gemini-3.5-flash-lite` ($0.30/$2.50, ~0.5–0.8s); runner-up `anthropic/claude-haiku-4.5`. `openai/text-embedding-3-small` confirmed on OpenRouter at 1536 dims. The sketch's `claude-3.5-sonnet` ID is dead. Full comparison: [research/02-openrouter-model-pair.md](../research/02-openrouter-model-pair.md).

## Correction

Superseded by [Choose free-tier OpenRouter model pair](13-free-model-pair.md): the account is free-models-only, and OpenRouter serves no embedding models at all — the `text-embedding-3-small` confirmation above was wrong. MVP uses nemotron-3-super-120b-a12b:free (chat) + local fastembed bge-small-en-v1.5 @384 dims (embeddings). This ticket's picks remain the paid post-demo upgrade path.

# Research 02 — OpenRouter model pair for sequential structured outputs (Signal Wow-Page)

Date: 2026-08-12. Sources: OpenRouter models API (`/api/v1/models`, fetched live), OpenRouter model pages (per-provider latency/throughput), OpenRouter docs, OpenAI docs.

## Recommendation

- **Quality pick: `anthropic/claude-sonnet-5`** — $2.00 / $10.00 per 1M tokens (in/out), ~1.5–3.1 s latency, 44–63 tok/s, `structured_outputs` = true. Current sonnet-class successor to the stale `anthropic/claude-3.5-sonnet` ID. Best schema-following quality per dollar for the persona-extraction call.
- **Budget pick: `google/gemini-3.5-flash-lite`** — $0.30 / $2.50 per 1M (in/out), ~0.5–0.8 s latency, 49–88 tok/s, `structured_outputs` = true. Cheapest current structured-output model from a top-3 vendor; ideal for the UI-schema composition call. Runner-up budget: `anthropic/claude-haiku-4.5` ($1/$5, ~0.4–1.0 s).
- **Embedding confirmation: yes.** `openai/text-embedding-3-small` is served via OpenRouter's **embeddings endpoint** `POST https://openrouter.ai/api/v1/embeddings` (separate from `/chat/completions`; not listed in the chat models API). Default output is **1536 dimensions** per OpenAI docs. Caveat: PydanticAI does not handle embeddings — call the endpoint with any OpenAI-compatible client.
- Stale-ID note: `anthropic/claude-3.5-sonnet` no longer exists on OpenRouter. Current equivalents — sonnet-class: `anthropic/claude-sonnet-5`; fast/cheap-class: `anthropic/claude-haiku-4.5` (Anthropic), `openai/gpt-5.4-mini` or `openai/gpt-5.6-luna` (OpenAI), `google/gemini-3.5-flash-lite` (Google).

## Comparison table

Latency/throughput = per-endpoint stats shown on OpenRouter model pages (measured 2026-08-12). Prices = listed OpenRouter $/1M tokens.

| Model ID | Latency class (measured) | $/1M in | $/1M out | Structured output notes |
|---|---|---|---|---|
| `anthropic/claude-sonnet-5` | Medium: 1.48–3.09 s, 44–63 tok/s | 2.00 | 10.00 | `structured_outputs` supported; strong instruction/schema following; PydanticAI uses tool-based structured mode for Anthropic — reliable. |
| `anthropic/claude-haiku-4.5` | Fast: 0.36–0.97 s, 52–85 tok/s | 1.00 | 5.00 | `structured_outputs` = true; good for simple flat schemas; slightly weaker on deep nested UI-schema JSON than sonnet-class. |
| `openai/gpt-5.4-mini` | Fast: 0.72–0.97 s, 53–61 tok/s | 0.75 | 4.50 | Native strict `json_schema` mode via OpenAI provider = strongest schema-conformance guarantee (guaranteed conforming output). |
| `google/gemini-3.5-flash-lite` | Fast: 0.53–0.76 s, 49–88 tok/s | 0.30 | 2.50 | `structured_outputs` = true via responseSchema; OpenRouter notes enforcement varies by endpoint (schema may be a strong hint) — set `require_parameters: true`. |
| `openai/gpt-5.6-luna` | Fast class (not measured; very new, 2026-07) | 0.10 | 0.60 | `structured_outputs` = true; cheapest OpenAI option but too new to trust for production schema reliability — monitor only. |
| `openai/gpt-5.5` (quality alternative) | Medium/slow class | 5.00 | 30.00 | Native strict JSON schema; overkill cost for this use case. |

Two-call design note: persona extraction (call 1) is free-text understanding → favors quality pick; UI-schema JSON composition (call 2) is deterministic schema emission → budget pick with strict/`responseSchema` mode is sufficient. If maximum schema reliability matters more than cost, use `openai/gpt-5.4-mini` for both calls (native strict mode, ~$0.75/$4.50).

## Sources

- OpenRouter models API (IDs, pricing, `structured_outputs` flags, creation dates): https://openrouter.ai/api/v1/models (fetched 2026-08-12)
- Latency/throughput/uptime per provider: https://openrouter.ai/anthropic/claude-sonnet-5, https://openrouter.ai/anthropic/claude-haiku-4.5, https://openrouter.ai/google/gemini-3.5-flash-lite, https://openrouter.ai/openai/gpt-5.4-mini
- Structured outputs feature (`response_format: json_schema`, per-endpoint support, `require_parameters`): https://openrouter.ai/docs/features/structured-outputs
- Embeddings API (`openai/text-embedding-3-small` as documented default model): https://openrouter.ai/docs/api_reference/embeddings.md
- Embedding dimensions (1536 default for text-embedding-3-small): https://platform.openai.com/docs/guides/embeddings

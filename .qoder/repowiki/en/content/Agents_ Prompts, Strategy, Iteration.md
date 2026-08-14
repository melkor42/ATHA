# Agents: Prompts, Strategy, Iteration

<cite>
**Referenced Files**
- [prompts/persona_modeler.md](file://prompts/persona_modeler.md)
- [prompts/experience_builder.md](file://prompts/experience_builder.md)
- [backend/agents.py](file://backend/agents.py)
- [backend/eval_loop.py](file://backend/eval_loop.py)
</cite>

## The two agents

Agent 1 (Persona Modeler) maps free-text onboarding input to a PersonaModel: interests, tone, accent_color (a ColorToken), expertise_level, and perspective (enterprise / talent / infrastructure / education). Its prompt instructs it to infer perspective from role and intent, not keywords alone. Agent 2 (Experience Builder) maps PersonaModel + retrieved data pool to an ExperienceSchema, encoding the composition grammar: perspective selects section mix and spectrum, explicit design words select the mode only (never the spectrum), tone selects copy register, expertise selects density, the persona carries the accent token.

## Prompt management

System prompts live as markdown in `prompts/` and are loaded once at startup; prompt iteration never requires a code change. The builder prompt carries the allowlist rules verbatim: only allowlist values, entity_ids exclusively from the provided pool, no markup, max six sections, every claim grounded.

## Structured-output strategy

Both agents use the OpenAI-compatible OpenRouter endpoint with `response_format: json_schema` (strict=false) against the Pydantic-generated schemas; Agent 2's schema excludes the server-authored entities map. Parsing is robust: direct JSON, fenced block, then first-brace extraction. Retry policy: two attempts per model (primary `nvidia/nemotron-3-super-120b-a12b:free`, then fallback `openai/gpt-oss-20b:free`); on rate-limit errors the layer sleeps 15s between attempts. Total failure raises, and the orchestrator degrades to the default experience.

## Iteration loop

Prompt quality is trained against the four fixtures in `personas/`: each fixture's expected PersonaModel JSON is the eval target for Agent 1; visibly distinct, whitelist-clean compositions are the target for Agent 2. `backend/eval_loop.py` drives repeated runs; `backend/trace.jsonl` records every request for post-hoc analysis. The original build reached 4/4 fixture pass after five iterations; failure types trained away included invented entity ids (sections dropped by verify) and missing numeric grounding.

## Open iteration items

The current queue (numeric match scores on SignalCards for Miriam, 2–3 mentor stories for David, a sector-connections view for Tobias, entrepreneurship naming for Jonas) is tracked in *Living State (dated)*, not here — this article stays timeless.

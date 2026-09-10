"""backend/agents.py — the LLM copywriter behind the ATHA knowledge page.

copywriter: the skeleton (backend/skeleton.py) plans the page structure
deterministically; this agent only writes the title/text copy for the
pre-planned slots. It never chooses structure, entities, or grounding.

Plain async OpenAI client against an OpenAI-compatible LLM provider.
Provider-aware: the base URL decides the quirks. Groq (current default via
.env: PRIMARY_MODEL=openai/gpt-oss-120b, FALLBACK_MODEL=openai/gpt-oss-20b,
both sub-2s in probing) gets json_schema WITHOUT the strict flag (Groq
rejects strict's full-schema rules but honors json_schema structure — the
client-side parse_json stays as the safety net) and no OpenRouter provider
routing block. OpenRouter (LLM_BASE_URL override) keeps strict json_schema
plus require_parameters/allow_fallbacks provider routing. NVIDIA NIM is the
cross-provider fallback rung (NVIDIA_BASE_URL / NVIDIA_API_KEY /
NVIDIA_MODEL): probed to HANG on response_format json_schema, so that rung
sends json_object with the schema embedded in the prompt and leans on
parse_json + pydantic validation. The Groq rungs send reasoning_effort=low
(gpt-oss reasoning tokens would otherwise exhaust max_tokens mid-JSON).
Strategy: json_schema response_format -> robust parse -> one retry on the
same model -> fast fallthrough to the next endpoint on 429 (same-provider
fallback first, then the NVIDIA pool), all bounded by a hard total
wall-clock budget (each attempt wrapped in asyncio.wait_for so a single
hung call can never blow the budget).
Models, caps and timing are env-overridable (LLM_BASE_URL, LLM_API_KEY,
PRIMARY_MODEL, FALLBACK_MODEL, NVIDIA_BASE_URL, NVIDIA_API_KEY,
NVIDIA_MODEL, LLM_MAX_TOKENS, LLM_TIMEOUT, LLM_TOTAL_BUDGET)
so provider/model A/B runs need no code change. System prompts are loaded
ONCE at startup from prompts/*.md, so prompt iteration never needs a code
change.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import time
from pathlib import Path
from typing import TypeVar

from dotenv import load_dotenv
from openai import AsyncOpenAI, APIConnectionError, APIError, APITimeoutError, RateLimitError
from pydantic import ValidationError

from graph_queries import load_env

log = logging.getLogger("signal.agents")

REPO_ROOT = Path(__file__).resolve().parents[1]
PROMPTS_DIR = REPO_ROOT / "prompts"

# Load the repo-root .env into os.environ WITHOUT overriding platform env
# (default load_dotenv behavior) — same precedence as load_env(): platform
# env wins on conflict, local .env fills the gaps.
load_dotenv(REPO_ROOT / ".env")

# Model routing + caps — env-overridable for A/B testing without code changes.
# Defaults target OpenRouter; the shipped .env points at Groq instead.
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
# OpenRouter-only provider routing is active exactly when the base URL is
# OpenRouter's; other providers (Groq) reject/ignore the provider block.
_IS_OPENROUTER = "openrouter.ai" in LLM_BASE_URL
# Groq's gpt-oss models are reasoning models: without reasoning_effort=low
# the thinking chain eats the max_tokens budget mid-JSON
# ("max completion tokens reached before generating a valid document").
_IS_GROQ = "api.groq.com" in LLM_BASE_URL
# Cerebras (pitch primary since 2026-09-04, probed): OpenAI-compatible,
# honors response_format json_object and reasoning_effort on gpt-oss — but
# json_schema structured mode is not assumed, so the primary+fallback rungs
# send json_object with the schema embedded in the prompt (NVIDIA style).
_IS_CEREBRAS = "cerebras.ai" in LLM_BASE_URL
PRIMARY_MODEL = os.getenv("PRIMARY_MODEL", "z-ai/glm-5.2:free")
# OpenRouter fallback must live on a DIFFERENT provider pool than the
# primary: glm-5.2 is served by Decart and 429s ~9/10 in its shared pool,
# while nemotron is served by Nvidia's own pool (smoke-tested ~4s).
FALLBACK_MODEL = os.getenv("FALLBACK_MODEL",
                           "nvidia/nemotron-3-super-120b-a12b:free")
# Tune: response length. The copywriter returns ONE json document covering
# every slot (7-10 sections); below ~1400 output tokens it truncates mid-JSON,
# parse_json fails and the whole page degrades to deterministic template copy.
# 1400 is the proven good-state budget; raising further is approved when the
# compose UX needs more room.
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1400"))
LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "15"))
LLM_TOTAL_BUDGET = float(os.getenv("LLM_TOTAL_BUDGET", "20"))
MAX_ATTEMPTS_PER_MODEL = 2  # initial + one retry

# NVIDIA NIM — cross-provider fallback rung behind the primary provider: a
# genuinely DIFFERENT capacity pool for when Groq's free TPM (~1-2
# composes/min) 429s. Key or model unset -> the rung is skipped entirely and
# the ladder stays exactly as before.
NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL",
                            "https://integrate.api.nvidia.com/v1")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
NVIDIA_MODEL = os.getenv("NVIDIA_MODEL", "")

T = TypeVar("T")

# --- system prompts (loaded once at startup from prompts/*.md) ------------------

COPYWRITER_SYSTEM = (PROMPTS_DIR / "copywriter.md").read_text(encoding="utf-8")


def _client() -> AsyncOpenAI:
    # LLM_API_KEY wins; OPENROUTER_API_KEY stays as the legacy fallback so
    # the old OpenRouter-only setup keeps working untouched.
    api_key = os.getenv("LLM_API_KEY") or load_env().get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("neither LLM_API_KEY nor OPENROUTER_API_KEY is set")
    return AsyncOpenAI(
        base_url=LLM_BASE_URL,
        api_key=api_key,
        timeout=LLM_TIMEOUT,
        max_retries=0,  # we own the retry policy (model fallback below)
    )


_CLIENT: AsyncOpenAI | None = None


def get_client() -> AsyncOpenAI:
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = _client()
    return _CLIENT


_NVIDIA_CLIENT: AsyncOpenAI | None = None


def get_nvidia_client() -> AsyncOpenAI | None:
    """Dedicated NVIDIA NIM client for the fallback rung; None if unconfigured."""
    global _NVIDIA_CLIENT
    if not (NVIDIA_API_KEY and NVIDIA_MODEL):
        return None
    if _NVIDIA_CLIENT is None:
        _NVIDIA_CLIENT = AsyncOpenAI(
            base_url=NVIDIA_BASE_URL,
            api_key=NVIDIA_API_KEY,
            timeout=LLM_TIMEOUT,
            max_retries=0,  # we own the retry policy (endpoint ladder below)
        )
    return _NVIDIA_CLIENT


# --- json parsing -----------------------------------------------------------------


def parse_json(raw: str | None) -> dict:
    """Robust JSON extraction: direct parse, then fenced block, then first {...}."""
    if not raw or not raw.strip():
        raise ValueError("empty model response")
    text = raw.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        try:
            return json.loads(fenced.group(1))
        except json.JSONDecodeError:
            pass
    start = text.find("{")
    if start >= 0:
        try:
            return json.loads(text[start:])
        except json.JSONDecodeError:
            pass
    raise ValueError(f"unparseable model response: {text[:200]!r}")


# --- chat with retry + fallback ---------------------------------------------------


async def _chat_json(
    client: AsyncOpenAI,
    *,
    system: str,
    user: str,
    json_schema: dict,
    schema_name: str,
    temperature: float = 0.2,
) -> dict:
    """Ordered endpoint ladder: [PRIMARY_MODEL] -> [FALLBACK_MODEL] -> [NVIDIA].

    Each rung is (endpoint name, client, model) and gets up to
    MAX_ATTEMPTS_PER_MODEL attempts; a 429 breaks out of the rung IMMEDIATELY
    so we fall through fast to the next pool (waiting out a Retry-After would
    blow the sub-10s target — the NVIDIA rung exists precisely as the
    different-capacity-pool hop). The NVIDIA rung is only present when
    NVIDIA_API_KEY + NVIDIA_MODEL are configured.

    A hard total wall-clock budget (LLM_TOTAL_BUDGET) is the real governor:
    every attempt is wrapped in asyncio.wait_for bounded by the remaining
    budget, so a single hung call can never blow past it; once the deadline
    passes we stop retrying and raise. Returns the parsed JSON dict; raises
    on total failure so the caller can degrade gracefully.

    NVIDIA/Cerebras quirk (probed): response_format json_schema HANGS on NIM
    and is not assumed on Cerebras, so those rungs send response_format
    json_object with the schema embedded in the user prompt and rely on
    parse_json + the caller's pydantic gate. No strict flag, no OpenRouter
    provider block ever reaches them.
    """
    endpoints: list[tuple[str, AsyncOpenAI, str]] = [
        ("primary", client, PRIMARY_MODEL),
        ("fallback", client, FALLBACK_MODEL),
    ]
    nvidia_client = get_nvidia_client()
    if nvidia_client is not None:
        endpoints.append(("nvidia", nvidia_client, NVIDIA_MODEL))

    last_error: Exception | None = None
    deadline = time.monotonic() + LLM_TOTAL_BUDGET
    for endpoint, ep_client, model in endpoints:
        is_nvidia = endpoint == "nvidia"
        # prompt-schema mode: NVIDIA always, Cerebras primary/fallback rungs
        prompt_schema = is_nvidia or _IS_CEREBRAS
        ep_user = user
        if prompt_schema:
            # their supported structured mode is json_object: hand the model
            # the schema in the prompt instead of via response_format.
            ep_user = (
                user
                + "\n\nThe JSON you return MUST conform to this JSON Schema:\n"
                + json.dumps(json_schema, ensure_ascii=False)
            )
        for attempt in range(1, MAX_ATTEMPTS_PER_MODEL + 1):
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                log.warning("%s: total budget (%.0fs) exhausted on %s [%s] — "
                            "giving up", schema_name, LLM_TOTAL_BUDGET, model,
                            endpoint)
                break
            try:
                log.info("%s: attempt %d on %s [%s endpoint]", schema_name,
                         attempt, model, endpoint)
                attempt_started = time.perf_counter()
                response = await asyncio.wait_for(
                    ep_client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": system},
                            {"role": "user", "content": ep_user},
                        ],
                        response_format=(
                            # prompt-schema rungs: json_object only
                            {"type": "json_object"}
                            if prompt_schema else
                            {
                                "type": "json_schema",
                                "json_schema": {
                                    "name": schema_name,
                                    # Groq rejects strict's full-schema rules
                                    # (additionalProperties + all-required) but
                                    # honors json_schema without the flag
                                    # (probed: valid JSON, ~1.5s); OpenRouter
                                    # keeps strict=True as before.
                                    **({"strict": True} if _IS_OPENROUTER else {}),
                                    "schema": json_schema,
                                },
                            }
                        ),
                        temperature=temperature,
                        max_tokens=LLM_MAX_TOKENS,
                        # Groq gpt-oss and Cerebras gpt-oss alike: short
                        # thinking chain, otherwise the reasoning tokens
                        # exhaust max_tokens mid-JSON
                        **({"reasoning_effort": "low"}
                           if ((_IS_GROQ or
                                (_IS_CEREBRAS and "gpt-oss" in model))
                               and not is_nvidia) else {}),
                        # OpenRouter-only extras: require_parameters keeps us
                        # on provider endpoints that honor json_schema (no
                        # prose-instead-of-JSON); allow_fallbacks lets
                        # OpenRouter try other providers of the same model
                        # when one 429s. No "sort: latency" — that pinned us
                        # to the throttled Decart endpoint. The NVIDIA rung
                        # instead gets thinking OFF (nemotron-lightning leaks
                        # reasoning tokens otherwise — probed); Groq gets no
                        # extra_body at all.
                        **({"extra_body": {
                            "provider": {
                                "require_parameters": True,
                                "allow_fallbacks": True,
                            }
                        }} if (_IS_OPENROUTER and not is_nvidia)
                        else {"extra_body": {
                            "chat_template_kwargs": {"thinking": False}
                        }} if is_nvidia else {}),
                    ),
                    timeout=min(LLM_TIMEOUT, remaining),
                )
                raw = response.choices[0].message.content
                log.info("%s: attempt %d on %s [%s endpoint] succeeded in "
                         "%d ms (output=%d chars)", schema_name, attempt,
                         model, endpoint,
                         int((time.perf_counter() - attempt_started) * 1000),
                         len(raw or ""))
                return parse_json(raw)
            except asyncio.TimeoutError as exc:
                last_error = exc
                log.warning("LLM attempt timed out (%s, attempt %d on %s "
                            "[%s endpoint]) after %.0fs cap (%.0f ms elapsed)",
                            schema_name, attempt, model, endpoint,
                            min(LLM_TIMEOUT, remaining),
                            (time.perf_counter() - attempt_started) * 1000)
            except (APIConnectionError, APITimeoutError, RateLimitError) as exc:
                last_error = exc
                log.warning("LLM transport error (%s, attempt %d on %s "
                            "[%s endpoint], %.0f ms elapsed): %s",
                            schema_name, attempt, model, endpoint,
                            (time.perf_counter() - attempt_started) * 1000,
                            exc)
                if isinstance(exc, RateLimitError):
                    # Provider-pool 429: waiting out the Retry-After would blow
                    # the sub-10s target — fall through FAST to the next rung
                    # (different capacity pool; ultimately NVIDIA's).
                    retry_after = exc.response.headers.get("retry-after") \
                        if exc.response is not None else None
                    log.warning("%s: 429 on %s [%s endpoint] (retry-after=%s) — "
                                "falling through to the next endpoint",
                                schema_name, model, endpoint, retry_after)
                    break
            except (APIError, ValidationError, ValueError) as exc:
                last_error = exc
                log.warning("LLM/parse error (%s, attempt %d on %s "
                            "[%s endpoint], %.0f ms elapsed): %s",
                            schema_name, attempt, model, endpoint,
                            (time.perf_counter() - attempt_started) * 1000,
                            exc)
    raise RuntimeError(
        f"{schema_name}: all attempts failed, last error: {last_error}"
    )


# --- the copywriter (skeleton architecture: structure is deterministic, -------
# --- the LLM only writes title/text copy for pre-planned slots) --------------

_COPY_SCHEMA = {
    "type": "object",
    "properties": {
        "sections": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "i": {"type": "integer"},
                    "title": {"type": "string"},
                    "text": {"type": "string"},
                    "source_i": {"type": "array", "items": {"type": "integer"}},
                    "component": {"type": "string",
                                  "enum": ["Statement", "FactList",
                                           "StageFlow", "PartnerLayers"]},
                },
                "required": ["i", "title", "text"],
                "additionalProperties": False,
            },
        },
        "order": {"type": "array", "items": {"type": "integer"}},
        "lead": {"type": "integer"},
    },
    "required": ["sections"],
    "additionalProperties": False,
}


async def copywriter_agent(
    slots_json: str,
    tone: str,
    client: AsyncOpenAI | None = None,
    temperature: float = 0.5,
    visitor_state: str | None = None,
    question: str | None = None,
) -> dict:
    """Slots JSON + tone + ranking context -> the full copy object
    {sections: [{i, title, text, source_i, component}], order, lead}.

    Copy, ranking and presentation vote only: the skeleton fixed structure
    and grounding, this call decides which sections matter most for THIS
    visitor (order/lead), which sources its copy rests on (source_i) and
    which atomic component fits each section (component — the server
    hydrates every structured payload itself and downgrades votes it
    cannot derive). The question is ranking context — never a source of
    facts. Caller aligns and validates every index (skeleton.align_copy)."""
    client = client or get_client()
    user = (
        f"Tone: {tone}.\n"
        f"Visitor state: {visitor_state or 'discovering'}.\n"
        f"Visitor question (ranking context only, never a fact source): "
        f"{question or '(none — rank by what matters at this stage)'}.\n\n"
        f"Slots:\n{slots_json}\n\n"
        "Rank the slots for this visitor (order + lead), then write the copy "
        "for every slot (i = slot index, source_i = the source indexes your "
        "copy rests on, component = the atomic presentation that fits those "
        "sources). Respond with JSON only."
    )
    data = await _chat_json(
        client,
        system=COPYWRITER_SYSTEM,
        user=user,
        json_schema=_COPY_SCHEMA,
        schema_name="copywriter",
        temperature=temperature,
    )
    return data

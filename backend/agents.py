"""backend/agents.py — the two LLM agents behind the SIGNAL wow-page.

Agent 1 (persona_modeler): free-text onboarding input -> PersonaModel.
Agent 2 (experience_builder): PersonaModel + retrieved data pool -> ExperienceSchema.

Plain async OpenAI client against OpenRouter's OpenAI-compatible endpoint
(ticket 13: nvidia/nemotron-3-super-120b-a12b:free — the only large free model
that accepts response_format/json_schema; fallback openai/gpt-oss-20b:free).
Strategy: json_schema response_format -> robust parse -> one retry on the same
model -> two attempts on the fallback model. System prompts are loaded ONCE at
startup from prompts/*.md, so prompt iteration never needs a code change.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from pathlib import Path
from typing import TypeVar

from openai import AsyncOpenAI, APIConnectionError, APIError, APITimeoutError, RateLimitError
from pydantic import TypeAdapter, ValidationError

from graph_queries import load_env
from ui_schema import ExperienceSchema, PersonaModel

log = logging.getLogger("signal.agents")

REPO_ROOT = Path(__file__).resolve().parents[1]
PROMPTS_DIR = REPO_ROOT / "prompts"

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
PRIMARY_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"
FALLBACK_MODEL = "openai/gpt-oss-20b:free"
MAX_ATTEMPTS_PER_MODEL = 2  # initial + one retry

T = TypeVar("T")

# --- system prompts (loaded once at startup from prompts/*.md) ------------------

PERSONA_SYSTEM = (PROMPTS_DIR / "persona_modeler.md").read_text(encoding="utf-8")
EXPERIENCE_SYSTEM = (PROMPTS_DIR / "experience_builder.md").read_text(encoding="utf-8")


def _client() -> AsyncOpenAI:
    env = load_env()
    return AsyncOpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=env["OPENROUTER_API_KEY"],
        timeout=90.0,
        max_retries=0,  # we own the retry policy (model fallback below)
    )


_CLIENT: AsyncOpenAI | None = None


def get_client() -> AsyncOpenAI:
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = _client()
    return _CLIENT


# --- json schema + parsing -------------------------------------------------------

_PERSONA_SCHEMA = TypeAdapter(PersonaModel).json_schema()
# Agent 2 authors sections only; the entities hydration map is server-side.
_EXPERIENCE_SCHEMA = TypeAdapter(ExperienceSchema).json_schema()


def _agent2_schema() -> dict:
    """ExperienceSchema minus the server-authored entities map."""
    schema = json.loads(json.dumps(_EXPERIENCE_SCHEMA))
    props = schema.get("properties", {})
    props.pop("entities", None)
    required = [r for r in schema.get("required", []) if r != "entities"]
    schema["required"] = required
    return schema


_EXPERIENCE_LLM_SCHEMA = _agent2_schema()


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
    """Primary model x MAX_ATTEMPTS_PER_MODEL, then fallback model x same.

    Returns the parsed JSON dict; raises on total failure so the caller can
    degrade gracefully.
    """
    last_error: Exception | None = None
    for model in (PRIMARY_MODEL, FALLBACK_MODEL):
        for attempt in range(1, MAX_ATTEMPTS_PER_MODEL + 1):
            try:
                response = await client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    response_format={
                        "type": "json_schema",
                        "json_schema": {
                            "name": schema_name,
                            "strict": False,
                            "schema": json_schema,
                        },
                    },
                    temperature=temperature,
                )
                return parse_json(response.choices[0].message.content)
            except (APIConnectionError, APITimeoutError, RateLimitError) as exc:
                last_error = exc
                log.warning("LLM transport error (%s, attempt %d on %s): %s",
                            schema_name, attempt, model, exc)
                if isinstance(exc, RateLimitError):
                    # free-tier 429: wait out the window instead of degrading
                    # instantly — the frontend theater covers this wait
                    await asyncio.sleep(15)
            except (APIError, ValidationError, ValueError) as exc:
                last_error = exc
                log.warning("LLM/parse error (%s, attempt %d on %s): %s",
                            schema_name, attempt, model, exc)
    raise RuntimeError(
        f"{schema_name}: all attempts failed, last error: {last_error}"
    )


# --- Agent 1: persona modeler -------------------------------------------------------


async def persona_agent(text: str, client: AsyncOpenAI | None = None) -> PersonaModel:
    """Free-text onboarding input -> validated PersonaModel."""
    client = client or get_client()
    data = await _chat_json(
        client,
        system=PERSONA_SYSTEM,
        user=text,
        json_schema=_PERSONA_SCHEMA,
        schema_name="persona_model",
        temperature=0.1,
    )
    return PersonaModel.model_validate(data)


# --- Agent 2: experience builder ------------------------------------------------------


def render_pool(rows: list[dict], events: list[dict]) -> str:
    """Render the retrieved data pool WITH ids for Agent 2's prompt."""
    lines: list[str] = []
    for row in rows[:8]:
        matched = ", ".join(
            f"{m['name']} ({m['topic']})" for m in (row.get("matches") or []) if m
        ) or "none"
        mentor = f" | mentor: {row['mentor_name']}" if row.get("mentor_name") else ""
        interests = ", ".join(row.get("skills") or [])
        lines.append(
            f"- person id={row['person_id']} | {row['name']} | role={row['role']} | "
            f"school={row['school']} | match_score={row['score']:.3f} | "
            f"interests: {interests} | seeking enterprises: {matched}{mentor}"
        )
    if events:
        lines.append("")
        lines.append("Events:")
        for ev in events[:6]:
            extra = ""
            if ev.get("kind") == "past" and ev.get("highlights"):
                extra = " | highlights: " + " / ".join(ev["highlights"][:3])
            elif ev.get("date"):
                extra = f" | date={ev['date']} | location={ev.get('location', '')}"
            lines.append(f"- event id={ev['id']} | {ev['name']} ({ev['kind']}){extra}")
    return "\n".join(lines)


async def experience_agent(
    persona: PersonaModel,
    pool_text: str,
    allowed_ids: set[str],
    client: AsyncOpenAI | None = None,
) -> ExperienceSchema:
    """PersonaModel + data pool -> ExperienceSchema draft (entities left empty)."""
    client = client or get_client()
    user = (
        "PersonaModel of the visitor:\n"
        f"{json.dumps(persona.model_dump(), ensure_ascii=False)}\n\n"
        "Allowed entity ids (entity_ids may ONLY contain ids from this list):\n"
        f"{json.dumps(sorted(allowed_ids), ensure_ascii=False)}\n\n"
        f"Data pool retrieved from the SIGNAL network graph:\n{pool_text}\n\n"
        "Compose the ExperienceSchema JSON now. Leave \"entities\" empty — the "
        "server hydrates it. Respond with JSON only."
    )
    data = await _chat_json(
        client,
        system=EXPERIENCE_SYSTEM,
        user=user,
        json_schema=_EXPERIENCE_LLM_SCHEMA,
        schema_name="experience_schema",
        temperature=0.6,
    )
    data.setdefault("entities", {})
    return ExperienceSchema.model_validate(data)

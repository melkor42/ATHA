"""backend/ui_schema.py — the allowlist contract between Agent 2 and the frontend.

Enums for components, color tokens, actions, layouts, spectra and style
modes; a recursive
``UINode`` with length limits and a ``strip_markup`` validator; and the
``ExperienceSchema`` with a server-side ``entities`` hydration map keyed by
entity_id. No free HTML anywhere — every value the LLM may emit is on an
allowlist, everything else is rejected or stripped.
"""

from __future__ import annotations

import re
from enum import Enum

from pydantic import BaseModel, Field, model_validator

# --- allowlists ---------------------------------------------------------------


class ComponentType(str, Enum):
    SIGNAL_CARD = "SignalCard"
    STUDENT_PROFILE = "StudentProfile"
    ENTERPRISE_CARD = "EnterpriseCard"
    EVENT_BANNER = "EventBanner"
    TEXT_BLOCK = "TextBlock"


class ColorToken(str, Enum):
    PRIMARY = "primary"
    ACCENT = "accent"
    SUCCESS = "success"
    WARNING = "warning"


class ActionType(str, Enum):
    OPEN_CONTACT = "open_contact"
    SHOW_DETAILS = "show_details"
    SAVE_SIGNAL = "save_signal"


class Layout(str, Enum):
    SINGLE_COLUMN = "single_column"
    GRID = "grid"


class Spectrum(str, Enum):
    """Axis 1 — color/glow family (sci-fi ↔ organic)."""

    MYCELIUM = "mycelium"
    TERRA = "terra"
    AURORA = "aurora"
    NEON = "neon"
    VOID = "void"


class StyleMode(str, Enum):
    """Axis 2 — design world (materiality/typography/atmosphere)."""

    NONE = "none"
    MINIMAL = "minimal"
    RETRO = "retro"
    ORGANIC = "organic"
    EARTH = "earth"
    STEAMPUNK = "steampunk"


class EntityType(str, Enum):
    PERSON = "person"
    ENTERPRISE = "enterprise"
    EVENT = "event"


# --- markup hygiene -------------------------------------------------------------

# Anything that smells like markup/HTML is stripped server-side; the frontend
# never renders raw strings as HTML anyway, but the contract stays clean here.
_MARKUP_RE = re.compile(r"[<>*_`]")


def strip_markup(text: str) -> str:
    """Remove HTML/markdown markup characters and collapse whitespace."""
    cleaned = _MARKUP_RE.sub("", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


class Button(BaseModel):
    label: str = Field(min_length=1, max_length=40)
    action: ActionType

    @model_validator(mode="after")
    def _clean(self) -> "Button":
        self.label = strip_markup(self.label)[:40]
        return self


class UINode(BaseModel):
    """Recursive UI node. All leaf values are allowlist-constrained."""

    component: ComponentType
    title: str | None = Field(default=None, max_length=80)
    text: str | None = Field(default=None, max_length=500)
    button: Button | None = None
    entity_ids: list[str] = Field(default_factory=list, max_length=10)
    children: list["UINode"] = Field(default_factory=list)

    @model_validator(mode="after")
    def _clean(self) -> "UINode":
        if self.title is not None:
            self.title = strip_markup(self.title)[:80]
            if not self.title:
                self.title = None
        if self.text is not None:
            self.text = strip_markup(self.text)[:500]
            if not self.text:
                self.text = None
        return self


UINode.model_rebuild()


class EntityPayload(BaseModel):
    """Server-side hydration payload for one entity_id (never LLM-authored)."""

    type: EntityType
    name: str | None = None
    school: str | None = None
    score: float | None = None
    topics: list[str] = Field(default_factory=list)
    role: str | None = None
    story: str | None = None
    sector: str | None = None
    size: str | None = None
    hq: str | None = None
    contact: str | None = None
    date: str | None = None
    location: str | None = None
    highlights: list[str] = Field(default_factory=list)


class PersonaModel(BaseModel):
    """Agent 1's output — the eval target against personas/*.md fixtures."""

    interests: list[str] = Field(min_length=1, max_length=6)
    tone: str = Field(max_length=40)
    accent_color: ColorToken
    expertise_level: str = Field(pattern="^(novice|advanced|expert)$")
    perspective: str = Field(
        pattern="^(enterprise|talent|infrastructure|education)$"
    )

    @model_validator(mode="after")
    def _clean(self) -> "PersonaModel":
        self.tone = strip_markup(self.tone.lower())[:40]
        self.interests = [strip_markup(i.lower())[:60] for i in self.interests]
        return self


class ExperienceSchema(BaseModel):
    """Agent 2's output + server hydration. The frontend contract."""

    layout: Layout
    spectrum: Spectrum = Spectrum.TERRA
    mode: StyleMode = StyleMode.NONE
    sections: list[UINode] = Field(min_length=1, max_length=6)
    entities: dict[str, EntityPayload] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _clean(self) -> "ExperienceSchema":
        if len(self.sections) > 6:
            self.sections = self.sections[:6]
        return self

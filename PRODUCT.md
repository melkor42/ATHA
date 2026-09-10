# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Primary visitors are prospective ATHA participants — AI-native talent and enterprise representatives — discovering ATHA for the first time and deciding whether it is worth joining. They arrive individually, contribute a few words about themselves, and receive a personal page.

## Product Purpose

The Wow Page is the personal front door to ATHA: after a few words about yourself, you receive a page composed only for you — grounded in the ATHA network graph, visibly different for every persona, building itself in front of you. It exists to honor the depth ATHA asks of participants ("we see you, and we built this for you") and to prove that truthful, personalized, AI-composed experiences are viable today. Success: the visitor feels understood before ATHA asks anything of them.

## Positioning

ATHA is the first 48-hour AI-native viability environment: real enterprise AI problems tackled by AI-native talent on AI-native infrastructure, producing evidence-grade commercial intelligence instead of pitch decks. The Wow Page mechanism a neighboring product could not truthfully copy: a personal page derived from a real knowledge graph (People, Enterprises, Topics, Signals) and composed by two LLM agents, where every claim is grounded in the visitor's actual profile — no generic filler, no hallucinated achievements. The medium is the message.

## Operating Context

- Vue 3 + Vite frontend with a Component Registry and recursive UiRenderer (no `v-html`).
- FastAPI backend orchestrating two LLM agents via OpenRouter free-tier models; embeddings are local fastembed (bge-small-en-v1.5, 384 dims); graph data in Neo4j.
- Repeated inputs are cached server-side; free-quota exhaustion triggers backoff and graceful degradation to the welcome page — it never crashes.
- Mock mode runs without the backend via fixture query params (`?fixture=student|warwick|business`).
- Demo context: presented at Warwick Business School; demo target 2026-08-24.

## Capabilities and Constraints

- Domain terminology is canon: Person, Mentor, Enterprise, Topic, Signal (the derived match), Perspective, PersonaModel, ExperienceSchema, Wow Page, Spectrum, StyleMode. Do not drift to synonyms (see `CONTEXT.md`).
- The brand is **Atha**; "Signal" survives only as the domain term. The legacy wire-contract strings (`SignalCard`, `save_signal`, `SIGNAL_CARD`) were removed with the 2026-09-10 agent-flow restoration; the atomic set (Statement, FactList, StageFlow, PartnerLayers) is the whole wire contract now.
- ExperienceSchema is the contract between the composing agent and the frontend: allowlist enums, recursive UINode, entity_ids whitelist-checked by verify().
- **Spectrum** (`mycelium | terra | aurora | neon | void`) owns the hue family; **StyleMode** (`none | minimal | retro | organic | earth | steampunk`) owns materiality, typography, atmosphere. The two axes compose orthogonally (axis grammar).
- All dataset content beyond ATHA 001 · Q4 2026 · Warwick Business School is fictional synthetic data. Never present fictional people or companies as real.
- LLM free-tier quotas are a live constraint; compositions must degrade gracefully.

## Brand Commitments

- "ATHA is not a hackathon. It is not a conference. It is something new." Depth over hype; well-being is infrastructure; the experience is designed around the human.
- The current visual world is the Plaza: an arrival overlay, a Theater sequence, a StoryGate, and spatial zones. Direction confirmed by the user 2026-08-24: **preserve this identity, but allow refinement** — evaluation may question individual canon elements where they hurt the experience, without replacing the world.

## Evidence on Hand

- Synthetic dataset v1: 48 students, 12 alumni, 12 enterprises, 20 topics, 8 events (3 past with highlights, 5 upcoming incl. ATHA 001), 2 schools — `data/`.
- Four acceptance personas with fixtures and expected outputs — `personas/`, `frontend/src/fixtures/`.
- Acceptance renders of prior Theme-enum era in `acceptance/` (superseded by the Spectrum × StyleMode grammar; new baselines pending).
- Vision and promise: `IDEA.md`; vocabulary: `CONTEXT.md`.
- Absence: no real testimonials, customers, press, or case studies beyond the ATHA 001 event fact. Future work must not fabricate them.

## Product Principles

1. Every claim is grounded in the person's actual profile — no hallucinated achievements, no generic filler.
2. A page that could only exist for this one person, at this one moment — visibly different per persona.
3. The experience feels alive: it builds itself in visible steps, in deliberate sequence, not all at once.
4. Depth over hype: the first interaction must honor the depth ATHA asks of participants.
5. The medium is the message: the composed page demonstrates the AI-native capability ATHA sells.

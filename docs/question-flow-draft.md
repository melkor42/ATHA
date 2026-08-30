# Question Flow & Answer Catalog — Draft v1 (2026-08-29)

Working document for the ask→retrieve→display redesign. Status: DRAFT, shaping with Manuel.
Premise: visitors are anonymous website users — no personas, no profile data. The page must
answer their most important questions from the ATHA knowledge graph, with a deterministic
anchor layer plus open vector search.

## The interview (what we ask)

Four steps max, every step skippable-after-role. Boris asks them in the AI Corner;
step 2 is inherited from the entrance gate when already answered there.

### Step 1 — Role: "How are you coming to ATHA?"
| id | Label (visitor's words) | Design grammar |
|---|---|---|
| talent | "As talent — I want to join a team" | spectrum aurora (current student profile) |
| business | "As an enterprise — I want to bring a challenge" | spectrum void |
| warwick | "From Warwick — education & research" | spectrum mycelium |

Keeps the current 3 roles; only the wording moves to visitor language.

### Step 2 — Concrete intent question (replaces the abstract state split)
The old gate question ("How are you meeting ATHA today?") narrows the broad context
too weakly — "discovering" was a catch-all. New design:

- The gate state (discovering/deciding/preparing/experienced) is still USED —
  inherited silently from `athaVisitorState` when present, as emphasis signal only.
- Asked in the AI Corner instead: **"What do you most want to know right now?"**
  with concrete, content-anchored options per role (each maps to a catalog cluster):
  - talent: "Whether I'd fit a team" / "What actually happens" / "How the work is judged" / "What I take away"
  - business: "What we receive as a partner" / "How our challenge is evaluated" / "What happens afterwards" / "IP & confidentiality"
  - warwick: "How ATHA serves education" / "WBS's role" / "The research ambition"
- Plus one honest default: **"Just looking around"** → the identity bundle
  (q01/q02 + rhythm + layers), no narrowing needed. First visits are fine without a signal.
- "I'm preparing to come" lives here as a concrete option (→ logistics cluster),
  not as an abstract state.

### Step 3 — Facet (one role-specific question)
**talent — "Which role in a team would fit you best?"** (5 team functions from Team Setup)
- A · Domain Expert — understanding the problem & the people it affects (9 passages)
- B · AI Workflow Lead — AI approach & technical feasibility (9 passages)
- C · Responsible AI & Risk Lead — governance, risk, ethics (9 passages)
- D · Business Viability & Coordinator — business case & coordination (9 passages)
- E · Pitch & Design Lead — communicating the decision (9 passages)
- "Not sure yet — show me the mix" (skip facet)

**business — "What matters most to you as a partner?"** (5 value forms)
- Experience / Perspective / Decision / Belonging / Continuity (1 passage each — THIN, see gaps)
- "How our challenge would be evaluated" (routes to the assessment lens facet instead)

**warwick — "Where is your focus?"**
- Education — developing AI-native changemakers
- Research — evidence for healthier innovation (lens passages, 8–10 each)
- Institutional — WBS's role & the network

### Step 4 — Open question (optional free text, WITH guidance)
"Anything else you want to know?" → embedded locally (bge-small) → vector search over
`knowledge_embeddings`, role-filtered. Skippable: "Just show me what matters most."
**Never an empty box**: show 3–4 suggestion chips = the next-ranked catalog questions
of this role that the page hasn't answered yet (e.g. talent: "How are teams formed?",
"How is the work judged?", "What is a typical day like?"). Every chip is a guaranteed
retrievable answer; the free input stays open for anything else.
This is the open layer; everything above is the anchor layer.

## Answer selection (how answers are chosen)

Priority order, filled-page target (up to 10 sections, at least 8 when content allows):
1. **Anchor questions** (deterministic): top-N catalog questions for role+state
   (existing `knowledge_for` rank logic, state-adjusted). N = 3–4.
2. **Facet section** (if facet chosen): one guaranteed section from passages
   SUPPORTING the chosen facet node, role-filtered. For talent also boost
   facet-related anchor questions (e.g. C picks → "How is our work judged?" rises).
3. **Vector extras** (free text or chips): top 1–2 hits with score above threshold,
   never duplicating anchor passages.
4. **Guaranteed tail** (fills the page even when retrieval is thin): edition facts,
   rhythm (arc), layers — deterministic ontology blocks.

Rules inherited from the current knowledge layer: confirmed-first answer ordering,
per-bundle passage dedup, internal passages unreachable, status discipline
(proposed/open framed as forming), HADORA never named.

### Retrieval interface change
`knowledge_for(role, visitor_state)` → `knowledge_for(role, visitor_state, facet=None, free_text=None)`
- facet: Cypher extension — `MATCH (facet {id:$facet})<-[:SUPPORTS]-(p:Passage) WHERE $role IN p.roles`
- free_text: existing SEARCH clause, query = the visitor's own words.
No new embedding model, no new index.

## Display (what the page shows after the cleanup)

**Filled page, not a stub** (Manuel, 2026-08-29): the result must feel substantial —
target **at least 8 sections**, showing most of what the retrieval legitimately has.
Caps that must change: `verify()` currently cuts at 6 sections, the prompt rule says
1–6 — both move to ~10. Section plan for a full page (deterministic skeleton):

1. Anchor answers: 3–4 TextBlocks (top catalog questions, role+state)
2. Facet section: 1–2 TextBlocks (chosen team function / value form / focus)
3. Vector extras: 0–2 TextBlocks (free text or chips, score-thresholded)
4. Edition facts block (ATHA 001 status, Forming/Proposed labels) — kept as knowledge
   passage or small config; must survive the synthetic cleanup
5. Rhythm block — the seven-stage arc (arc_stages ontology)
6. Layers block — OneMundi / WBS / experience design (org ontology)

**Honest ceiling rule**: if a facet genuinely has one passage (e.g. value forms today),
the page shows one — no conjuring. Thin facets are content gaps for Richard's next
delivery round (golden Q&A / visitor-facing paragraphs), not engineering problems.

**Removed: the NetworkGraph panel** — `AiCornerZone.vue:153-155` (`graph-panel` +
`<NetworkGraph />`) draws the persons/enterprises entities as a decorative node cloud
above the composed content. It has no qualitative value for a knowledge page and its
data (synthetic people) is being removed. Retire panel + component together with the
card components.

Without the synthetic people graph, the card components (SignalCard, StudentProfile,
EnterpriseCard, EventBanner) retire until real network data exists. ExperienceSchema
allowlist shrinks accordingly later.

Structure is deterministic (section plan in Python); LLM writes the copy only.
See the hybrid-skeleton discussion — that is the matching architecture for this flow.

## Known gaps (honest list)

1. **Value forms are thin**: 1 passage each. Business facet answers need content —
   golden Q&A round should author one solid paragraph per value form.
2. **experienced state** has little tailored content (ecosystem/continuity only) — fine
   before Edition 001, revisit after.
3. **Free-text quality floor**: bge-small on short philosophical prose is mediocre;
   the threshold must be conservative, and vector extras are optional by design.
4. **Style step**: keep as an optional last micro-step ("How should it feel?") — it is
   deterministic (mode override), costs zero tokens, keeps pages diverse.
5. Frontend interview UI (Boris in the AI Corner) needs the new question components;
   gate-state inheritance needs plumbing into the compose request.

## Suggested implementation order

1. Backend: extend `knowledge_for` with facet + free_text (behind the current API shape).
2. Content: author value-form paragraphs (golden Q&A seed).
3. Facet data: labels/descriptions already in ontology — expose via a small endpoint or
   static config for the frontend.
4. Frontend interview redesign (steps 1–4) + gate-state inheritance.
5. Deterministic skeleton builder (structure in Python, LLM copy-only) — then retire cards.
6. Synthetic data cleanup in Neo4j (last, once nothing depends on it).

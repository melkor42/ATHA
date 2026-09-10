# CONTEXT.md — Atha Wow-Page domain glossary

The vocabulary the project uses. Terms are defined as used; don't drift to synonyms.

- **Person** — a human in the ATHA network. Role `student` (currently at Warwick) or `alumnus`. One label, because retrieval then has a single path. The subject of a Profile.
- **Mentor** — an alumnus in the object position of `MENTORED_BY`. Not a separate label; a role an alumnus plays in a story.
- **Enterprise** — an organization partnering with ATHA. Carries sector, size, HQ, description, and a contact person as fields (not a separate node), with complete metadata for filterable lists. Expresses hiring needs via `SEEKS_EXPERTISE`.
- **Topic** — a shared vocabulary node (~20) joining interests to needs. The join key that makes a Signal.
- **Signal** — a *derived* match between a Person and an Enterprise via a shared Topic. Never stored as a node; computed by the hybrid query.
- Note: the brand is **Atha**; **Signal** survives only as this domain term (the derived match). The legacy wire-contract strings (`SignalCard`, `save_signal`, `SIGNAL_CARD`) were removed with the 2026-09-10 agent-flow restoration; the atomic set (Statement, FactList, StageFlow, PartnerLayers) is the whole wire contract now.
- **Event** — a gathering on the ATHA timeline. Past events carry `highlights` (the "best moments"); upcoming events carry date and location. **ATHA 001 · Q4 2026 · Warwick Business School is the single real entity in the synthetic dataset**; everything else is fictional.
- **Profile** — the embedding-bearing text of a Person; the vector surface of retrieval. Same embedding model in ingest and query (fastembed bge-small-en-v1.5, 384 dims).
- **Perspective** — the visitor's stance: `enterprise` | `talent` | `infrastructure` | `education`. Agent 1's primary branching axis; inherited from the page the Wow Page replaces.
- **PersonaModel** — Agent 1's output: interests, tone, accent_color (ColorToken), expertise_level, perspective.
- **ExperienceSchema** — the contract between the compose pipeline and the frontend: allowlist enums (components, color tokens, actions, layouts, Spectrum, StyleMode), recursive UINode, 1–10 sections. In the skeleton architecture the pipeline fills it with TextBlocks only (entities empty). **Spectrum** (`mycelium | terra | aurora | neon | void`) owns the hue family and is fixed per role (student→aurora, warwick→mycelium, business→void). **StyleMode** (`none | minimal | retro | organic | earth | steampunk`) owns materiality, typography and atmosphere; fixed per role, overridden by the visitor's explicit style pick.
- **Wow Page** — the composed personal page: grounded, visibly different per role, building itself in front of the user.
- **Skeleton** — the deterministic page plan (`backend/skeleton.py`): anchor questions (catalog, state-adjusted, intent-boosted) → facet slot → vector extras → guaranteed tail (edition facts, rhythm arc, partner layers). Structure, grounding and section order never come from the model.
- **Slot** — one planned section of the skeleton: kind (anchor|facet|extra|edition|rhythm|layers), title_hint, about, and the source passages (with status) the copy is written from.
- **Copywriter** — the small LLM call (`agents.copywriter_agent`) that writes title/text copy for the skeleton's slots and nothing else; `align_copy` index-aligns its output with a deterministic per-slot fallback.
- **Edition facts** — the ATHA 001 status facts (`data/knowledge/edition_facts.json`, from the context brief), shown in the guaranteed tail with status discipline (proposed/open framed as forming).

## Knowledge graph (digested ATHA canon)

The composed page is grounded in a digested knowledge graph, separate from the synthetic network dataset below. Source: Richard's ATHA context docs, vendored to `data/knowledge/context-md/ATHA/`, curated via `data/knowledge/digest_rules_cluster*.json` into `data/knowledge/knowledge_map.json`, ingested by `backend/ingest_knowledge.py` (idempotent MERGE + edge-clear convergence).

- **Question** — a catalog question the page can answer (`q01`…`q14`), ranked per role (`rank_by_role`), tagged to visitor states. Linked to its answers by `ANSWERED_BY`.
- **Passage** — a chunk of a source doc with `perspective`, `status` (confirmed|proposed|open), role/state relevance, and an embedding. `:InternalPassage` marks internal-only content (judge panel, partner strategy) that is never embedded and never surfaces to visitors.
- **Ontology** — anchors the passages: Organization, Lens (5), VerdictState (4), ArcStage (7), TeamFunction (5), AssessmentArea (versioned variants), RecommendationCategory, ValueForm (5), HadoraPrinciple. Passages `SUPPORT` ontology nodes; facet retrieval matches on these.
- Retrieval: `backend/knowledge.py::knowledge_for` (anchor answers) and `backend/skeleton.py::build_skeleton` (full page plan). Free-text threshold for the vector extras is calibrated to ~0.82 on bge-small for this corpus.

## Dataset spec (synthetic v1)

Counts: 48 students · 12 alumni · 12 enterprises · 20 topics · 8 events (3 past with highlights, 5 upcoming incl. ATHA 001) · 2 schools.

Fields:
- Person: id, name, role, year_or_cohort, program_or_role, school, skills[], bio, contact_email
- Enterprise: id, name, sector, size, hq, description, contact{name, role, email}, topics via SEEKS_EXPERTISE
- Topic: name
- Event: id, name, date, kind(past|upcoming), location, highlights[]
- Profile: text, embedding(384)

Relationships: `ATTENDS` (Person→School), `HAS_PROFILE`, `INTERESTED_IN` (Person→Topic), `SEEKS_EXPERTISE` (Enterprise→Topic), `SPONSORS` (Enterprise→Event), `MENTORED_BY` (student→alumnus), `ATTENDED` (Person→past Event).

profile_text template: "{role}: {name}, {school}. Interests: {skills/topics}. {bio}" — meaningful prose, same template family for both roles.

Generator: seeded RNG, fictional English names and companies, no real individuals; output `data/students.json`-shaped files per entity type; ingest via idempotent MERGE (ticket 09).

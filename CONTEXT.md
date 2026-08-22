# CONTEXT.md — Atha Wow-Page domain glossary

The vocabulary the project uses. Terms are defined as used; don't drift to synonyms.

- **Person** — a human in the ATHA network. Role `student` (currently at Warwick) or `alumnus`. One label, because retrieval then has a single path. The subject of a Profile.
- **Mentor** — an alumnus in the object position of `MENTORED_BY`. Not a separate label; a role an alumnus plays in a story.
- **Enterprise** — an organization partnering with ATHA. Carries sector, size, HQ, description, and a contact person as fields (not a separate node), with complete metadata for filterable lists. Expresses hiring needs via `SEEKS_EXPERTISE`.
- **Topic** — a shared vocabulary node (~20) joining interests to needs. The join key that makes a Signal.
- **Signal** — a *derived* match between a Person and an Enterprise via a shared Topic. Never stored as a node; computed by the hybrid query and rendered by SignalCard.
- Note: the brand is **Atha**; **Signal** survives only as this domain term (the derived match) and in its wire-contract strings (`SignalCard`, `save_signal`, `SIGNAL_CARD`).
- **Event** — a gathering on the ATHA timeline. Past events carry `highlights` (the "best moments"); upcoming events carry date and location. **ATHA 001 · Q4 2026 · Warwick Business School is the single real entity in the synthetic dataset**; everything else is fictional.
- **Profile** — the embedding-bearing text of a Person; the vector surface of retrieval. Same embedding model in ingest and query (fastembed bge-small-en-v1.5, 384 dims).
- **Perspective** — the visitor's stance: `enterprise` | `talent` | `infrastructure` | `education`. Agent 1's primary branching axis; inherited from the page the Wow Page replaces.
- **PersonaModel** — Agent 1's output: interests, tone, accent_color (ColorToken), expertise_level, perspective.
- **ExperienceSchema** — the contract between Agent 2 and the frontend: allowlist enums (components, color tokens, actions, layouts, Spectrum, StyleMode), recursive UINode, entity_ids whitelist-checked by verify(). **Spectrum** (`mycelium | terra | aurora | neon | void`) owns the hue family — surfaces, borders, glows, ambient aura; selected by perspective. **StyleMode** (`none | minimal | retro | organic | earth | steampunk`) owns materiality, typography and atmosphere; selected by explicit design words or persona temperament. The two axes compose orthogonally (axis grammar).
- **Wow Page** — the composed personal page: grounded, visibly different per persona, building itself in front of the user.

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

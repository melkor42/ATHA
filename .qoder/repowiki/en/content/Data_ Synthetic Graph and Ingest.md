# Data: Synthetic Graph and Ingest

<cite>
**Referenced Files**
- [CONTEXT.md](file://CONTEXT.md)
- [backend/generate_data.py](file://backend/generate_data.py)
- [backend/ingest.py](file://backend/ingest.py)
- [data/](file://data)
</cite>

## Domain in one paragraph

The graph holds Persons (role student or alumnus), Schools, Enterprises, Topics, Events, and Profiles (the embedding-bearing text of a Person). A Signal — the person–enterprise match — is derived at query time over shared Topics and never stored. Mentorship stories are students MENTORED_BY alumni; past events carry highlights ("best moments"), upcoming events carry date and location. The single real entity in an otherwise fictional dataset is the upcoming event SIGNAL 001 (Q4 2026, Warwick Business School). Full glossary in `CONTEXT.md`.

## Counts and shape

Synthetic v1: 48 students, 12 alumni, 12 enterprises (complete metadata: sector, size, hq, contact, description), 20 topics, 8 events (3 past with highlights, 5 upcoming), 2 schools. Relationships: ATTENDS, HAS_PROFILE, INTERESTED_IN, SEEKS_EXPERTISE, SPONSORS, MENTORED_BY, ATTENDED. Generated JSON lives in `data/` (students, alumni, enterprises, topics, events, schools).

## The embedding contract

Profiles are embedded with local fastembed `BAAI/bge-small-en-v1.5` at 384 dims — the same model at ingest and query time, never another. The Aura vector index `profile_embeddings` is 384-dim cosine, created with the current Cypher syntax. profile_text follows one template family for both roles: "{role}: {name}, {school}. Interests: {skills}. {bio}".

## Idempotency

`ingest.py` writes with MERGE and UNWIND batches of 50; running it twice produces zero duplicates (verified by before/after counts). Regenerate with `python generate_data.py` (seeded, deterministic) then `python ingest.py` from `backend/`.

## Fixture-aligned clusters

The generator shapes four topic clusters so each acceptance fixture retrieves distinct, plausible matches: cybersecurity + data science + talent acquisition (Miriam), networking + entrepreneurship + events (Jonas), mentoring + wellbeing + community with MENTORED_BY stories (David), and data quality + methodology + network analysis with complete enterprise metadata (Tobias).

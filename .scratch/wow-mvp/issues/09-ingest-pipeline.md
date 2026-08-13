# Build the ingest pipeline

Type: task
Status: resolved
Blocked by: 01, 02, 03, 04, 05

## Question

Build the offline ingest per the settled architecture: a generator producing the fictional dataset per the dataset spec from [Model the synthetic network domain](05-synthetic-network-domain.md), then `ingest.py` — transform to profile text, `embed_batch` via OpenRouter, idempotent `MERGE` writes (nodes, relationships, embeddings), vector index creation per `neo4j.cypher`. Same embedding model in ingest and query. Resolved when the hybrid query returns sensible rows for all four fixtures' interest vectors.

## Answer

Deliverables: `backend/generate_data.py`, `backend/ingest.py`, `backend/graph_queries.py`; JSON written to `data/` (students, alumni, enterprises, topics, events, schools).

**Counts** (spec-exact, identical across both ingest runs): 48 students + 12 alumni = 60 Person nodes, 60 Profile nodes (384-dim fastembed BAAI/bge-small-en-v1.5), 12 Enterprise (all with complete metadata: sector, size, hq, contact, description), 20 Topic, 8 Event (3 past with highlights[], 5 upcoming incl. the single real entity SIGNAL 001, Q4 2026, Warwick Business School), 2 School. Relationships: ATTENDS 60, HAS_PROFILE 60, INTERESTED_IN 195, SEEKS_EXPERTISE 36, SPONSORS 18, MENTORED_BY 14, ATTENDED 54 (437 total).

**Idempotency proof:** ingest run twice; run 2 before/after counts identical to run 1 (persons 60 / profiles 60 / enterprises 12 / topics 20 / events 8 / schools 2 / relationships 437); duplicate-key scan (any label/id/name key with count > 1) returned zero rows. Second run created zero duplicates.

**Index syntax:** `CREATE VECTOR INDEX profile_embeddings IF NOT EXISTS FOR (pr:Profile) ON (pr.embedding) OPTIONS {indexConfig: {`vector.dimensions`: 384, `vector.similarity_function`: 'cosine'}}`, polled with `SHOW VECTOR INDEXES` until state = ONLINE. Retrieval uses the current Cypher `SEARCH` clause — `MATCH (profile:Profile) SEARCH profile IN (VECTOR INDEX profile_embeddings FOR $vector LIMIT $top_k) SCORE AS score` composed with the Person/School/Topic/Enterprise traversal in one statement (`HYBRID_QUERY` in graph_queries.py); the deprecated `db.index.vector.queryNodes` is not used.

**Sanity top-3** (hybrid query, top_k=10, limit=5):
1. "cybersecurity data science talent acquisition" -> stu-01 Adrian Dunmore (0.857), stu-07 Emil Everly (0.856), alu-07 Patrick Thornhill (0.852); matched enterprises Northbridge Cybernetics / Quantia Analytics / TalentArc Partners on all three topics.
2. "networking entrepreneurship events" -> stu-24 Leo Naylor (0.846), stu-16 Hassan Mercer (0.841), stu-13 Finn Mercer (0.840); matched Harbourlight Ventures / Mosaic Events Collective / Foundry Lane Studio.
3. "mentoring wellbeing community" -> stu-29 Mei Thornhill (0.860, MENTORED_BY alu-01), stu-26 Marcus Cresswell (0.855), stu-28 Mei Jepson (0.854); matched Brightwell Trust / Kindred Community CIC / Anchor Mentoring Network.
4. "data quality methodology network analysis" -> stu-41 Victor Fairbank (0.840), stu-37 Tara Drewitt (0.839), stu-40 Victor Cresswell (0.838); matched Clearmetrics Data Group / Methodica Research Labs / Netform Analytics (all complete-metadata enterprises).

All four result sets are pairwise disjoint and semantically plausible; allowed-id whitelist = returned person ids + matched enterprise ids.

**Deviations:**
- Live Aura instance reports Neo4j 5.27-aura (research 03 assumed 2026.07). The `SEARCH` clause was verified working on this instance and is used throughout; no fallback to the deprecated procedure was needed.
- The instance contained legacy residue from earlier prototyping (labels Talent/Challenge/Cohort/Signal/Partner, two id-less Enterprise nodes, one id-less Event node); these were deleted so counts are provable against the spec.
- fastembed 0.8.0 exposes `passage_embed`/`query_embed` (not `embed`/`embed_query`); same model at ingest and query, bge query prefix handled by fastembed.
- `.env` has a UTF-8 BOM on the first key; `load_env()` in graph_queries.py strips it.

# Validate Aura free-tier limits

Type: research
Status: resolved
Blocked by: —

## Question

Neo4j Aura free-tier constraints relevant to this MVP: vector index support (`db.index.vector.queryNodes`, 1536 dims, cosine), node/relationship/storage caps, concurrent connections, and the Neo4j version Aura runs. The provisioned instance is small (~100 nodes, 1536-dim vectors) — confirm nothing in the free tier bites the hybrid query or the ingest.

## Answer

Free tier fits: vector indexes (1536-dim cosine) are a core feature, Aura runs Neo4j 2026.07; caps ~200k nodes / 400k rels; UNWIND/MERGE batches of 50 safe. Gotchas: auto-pause after 3 days idle, deletion after 30 days inactive, one free instance. **`db.index.vector.queryNodes` is deprecated since 2026.04 — the build must use the newer vector `SEARCH` Cypher syntax**, not the sketch's `neo4j.cypher` verbatim. Full findings: [research/03-aura-free-tier-limits.md](../research/03-aura-free-tier-limits.md).

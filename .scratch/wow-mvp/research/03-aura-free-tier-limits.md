# Research 03 — Neo4j Aura Free-Tier Limits for Signal Wow-Page (graph + 1536-dim vectors)

Researched: 2026-08-12 · Sources: neo4j.com primary docs/pricing/release notes only.

## Verdict

**Yes — Aura Free fits this demo comfortably, with operational caveats.** ~100 nodes / a few hundred relationships is ~0.1% of the published free-tier graph cap (200k nodes / 400k rels), and 1536-dim float vectors are well within vector-index capability. Aura currently runs **Neo4j 2026.07** (July 2026 release, which rolls out to AuraDB Free *first*), far beyond the 5.11/5.15 minimum for vector indexes. Vector indexes and `CALL db.index.vector.queryNodes(...)` with `cosine` are core database features, not gated by tier — the only vector item excluded on Free is the paid "Vector Optimization" memory-reservation feature (only relevant to >4 GB instances). Real risks are operational, not capacity: **auto-pause after 3 days idle** (paused hostnames stop resolving), **deletion after 30 days inactivity**, and one free instance per account. Hybrid vector+traversal Cypher and UNWIND/MERGE ingest batches of 50 are both fine.

## Limits table

| Constraint | Aura Free value | Source |
|---|---|---|
| Graph size (official FAQ) | 200,000 nodes / 400,000 relationships, single database | Aura FAQ |
| Graph size (marketing page — stale figures) | 50,000 nodes / 175,000 relationships | free-graph-database page (modified 2026-07-23); our demo is ≪ either |
| Neo4j version on Aura | 2026.07 (July 2026 release; rollout starts on AuraDB Free) | Aura July 2026 release notes |
| Vector indexes | Supported (core Enterprise feature, not tier-gated); 1536 dims + `cosine` is the canonical documented example | Cypher Manual |
| `db.index.vector.queryNodes` | Available but **deprecated as of Neo4j 2026.04**; `SEARCH` clause preferred since 2026.01 | Cypher Manual |
| Vector Optimization (reserved vector memory) | **Not included** (paid tiers, >4 GB instances only) | Pricing page; Vector optimization doc |
| Native `VECTOR` type / block format | Included on Free | Pricing page |
| Storage / memory figures | No GB figure published for Free; limits are enforced as node/relationship counts ("DB Instance Size: Limits on node and relationship counts") | Pricing page |
| Concurrent DB connections | A maximum concurrent connection limit exists but **no numeric cap is published** for Free; rapid session creation triggers "Session Expired" | Aura Troubleshooting doc |
| Aura management API | 25 requests/minute rate limit for Free accounts | Aura API Overview |
| Instances | One Free instance per account | Create an instance doc |
| Backups | One exportable snapshot at a time; no rolling 7-day backups | Aura FAQ |
| Idle behavior | Auto-pauses after **3 days** inactivity; Free databases **deleted after 30 days** without activity | free-graph-database page; Aura FAQ |
| Other Free exclusions | No monitoring/metrics, query-log analyzer, RBAC/SSO, IP filtering, private endpoints, secondaries, pipelined/parallel runtime, Graph Analytics, SLA; single-zone; community support | Pricing page; Aura FAQ |

## Gotchas

1. **Auto-pause + DNS.** AuraDB Free pauses after 3 days idle; a paused instance's hostname will not resolve, so drivers fail with "Cannot resolve address" / DNS errors. Check `console.neo4j.io` and Resume before debugging connectivity. (Troubleshooting doc)
2. **30-day deletion.** A Free database with no activity for 30 days is deleted — not just paused. Keep a demo-use cadence or export a snapshot. (Aura FAQ)
3. **No rolling backups.** Only one exportable snapshot at a time; treat offline ingest scripts as your reproducible source of truth. (Aura FAQ)
4. **`db.index.vector.queryNodes` is deprecated** (since 2026.04) in favor of Cypher `SEARCH ... WHERE` (2026.01+). It still works in 2026.07 and is fine for an MVP, but write the hybrid query so it can migrate to `SEARCH`. (Cypher Manual)
5. **Index POPULATING window.** A vector index is unusable immediately after creation; wait for `SHOW VECTOR INDEXES` state = ONLINE before running queries. Trivial at ~100 nodes but script the check anyway. (Cypher Manual)
6. **Hybrid vector+traversal queries are fine**: `CALL db.index.vector.queryNodes(...) YIELD node, score` composes normally with `MATCH`/`CALL {}` subqueries; nothing tier-gates this. Score values are only meaningful within one result set — rank sources independently when mixing vector and other signals. (Cypher Manual)
7. **UNWIND/MERGE batches of 50 are safe.** The documented memory failure mode is `MemoryLimitExceededException` from `UNWIND` on *long* lists (estimation overcount); the docs explicitly recommend small batch sizes, so 50 is conservative. Keep `ORDER BY`/`DISTINCT` out of heavy ingest queries. (Troubleshooting doc)
8. **Connection cap is undocumented numerically.** Reuse one driver instance and sessions; rapid session churn hits the concurrent connection ceiling and produces "Session Expired". (Troubleshooting doc)
9. **One Free instance per account**, and the management API is throttled to 25 req/min — script provisioning accordingly. (Create an instance doc; API Overview)
10. **Version caveat:** Aura July release notes ship Neo4j 2026.07; note 2026.07.0 had a `trim()`/block-format bug fixed in 2026.07.1 — relevant only if you use `trim()` heavily. (Neo4j release notes)

## Sources

- Aura platform FAQ (200k/400k, one snapshot, 30-day deletion, continuous upgrades): https://neo4j.com/cloud/platform/aura-graph-database/faq/
- AuraDB Free landing page + FAQ (50k/175k figures, 3-day auto-pause): https://neo4j.com/free-graph-database/ (last modified 2026-07-23)
- Pricing & tier comparison (Vector Optimization not included, block format included, node/rel-count limits): https://neo4j.com/pricing/
- Vector indexes (1536 dims + cosine example, `queryNodes` signature & deprecation in 2026.04, POPULATING state, providers since `vector-1.0` in Neo4j 5.11): https://neo4j.com/docs/cypher-manual/current/indexes/semantic-indexes/vector-indexes/
- Aura July 2026 release notes (Neo4j 2026.07, rollout starts on AuraDB Free, HFQ vector search GA): https://neo4j.com/release-notes/aura/neo4j-aura-database-july-2026/
- Release notes archive (latest Neo4j 2026.07.1, 5 Aug 2026): https://neo4j.com/release-notes/
- Aura Troubleshooting (concurrent connection limit, Session Expired, UNWIND memory overestimation, paused-instance DNS errors): https://neo4j.com/docs/aura/tutorials/troubleshooting/
- Vector optimization (paid tiers only, >4 GB instances): https://neo4j.com/docs/aura/managing-instances/vector-optimization/
- Create an instance (one Free instance per account): https://neo4j.com/docs/aura/getting-started/create-instance/
- Aura API rate limits (25 req/min Free): https://neo4j.com/docs/aura/api/overview/
- Cypher versions on Aura (Cypher 5 & 25): https://neo4j.com/docs/aura/managing-instances/cypher-version/

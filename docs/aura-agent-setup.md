# Aura Agent setup — ATHA knowledge concierge (A/B twin of backend/knowledge.py)

Purpose: create a Neo4j Aura Agent that reproduces what `knowledge_for(role,
visitor_state)` returns, so we can A/B the platform agent against our own
retriever (decision recorded 2026-08-28: our retriever is the critical path,
this agent is the experiment).

## Console prerequisites (one-time)

1. Organization settings → enable **Generative AI assistance** and **Aura Agent**.
2. Project Security → enable **Tool authentication**.
3. Agents → **Create Agent** → **Create with AI** → select the ATHA instance.
4. When asked about embeddings: do **not** opt into hosted similarity search.
   The `knowledge_embeddings` index is embedded with local BAAI/bge-small,
   which the agent's Similarity Search providers (OpenAI/Gemini/Voyage) cannot
   query. The prompt below makes the agent Cypher-only, which is fine — the
   catalog path is deterministic and needs no vectors.
5. Paste the prompt below as the use-case description.

## After generation — curate the tools

- KEEP the read-only Cypher Template tools it derived (the two core queries below).
- REMOVE/DISABLE any **Text2Cypher** tool (unconstrained NL→Cypher could reach
  `:InternalPassage` content).
- REMOVE/DISABLE any **Similarity Search** tool on `knowledge_embeddings`
  (provider-model mismatch, see step 4 above).
- Keep the agent **internal** while experimenting — console use is not billed;
  publishing an external REST/MCP endpoint is a separate, billable decision.

## The prompt (paste verbatim — 1987 chars, the console field caps at 2000)

```text
ATHA knowledge concierge. Input: role (student|warwick|business), optional visitor_state (discovering|deciding|preparing|experienced). Output: JSON knowledge bundle used to compose a visitor's personal page. Return passages VERBATIM; never paraphrase or invent.

Graph: (:Question{id,text,rank_by_role})-[:FOR_ROLE]->(:VisitorRole{id}), (:Question)-[:FOR_STATE]->(:VisitorState{id}), (:Question)-[:ANSWERED_BY]->(:Passage{id,heading_path list,text,perspective,status,internal}). Passages with internal=true also carry :InternalPassage. rank_by_role is a JSON string like {"student":2}.

Algorithm:
1) MATCH (q:Question)-[:FOR_ROLE]->(:VisitorRole{id:$role}) OPTIONAL MATCH (q)-[:FOR_STATE]->(s) RETURN q.id,q.text,q.rank_by_role,collect(DISTINCT s.id) AS states
2) Parse rank_by_role; sort by (state missing from states, rank ascending); take top 4.
3) UNWIND $qids AS qid MATCH (:Question{id:qid})-[:ANSWERED_BY]->(p:Passage) WHERE p.internal=false RETURN qid,collect({passage_id:p.id,text:p.text,heading_path:p.heading_path,perspective:p.perspective,status:p.status})
4) Per question: order answers confirmed>proposed>open, then passage_id; max 2; skip passage_ids already used by earlier questions.
5) Output exactly: {"role":..,"visitor_state":..,"questions":[{"id","text","answers":[{"passage_id","text","heading_path","perspective","status"}]}]}

Tools: only the two parameterized read-only Cypher templates above. No Text2Cypher, no vector similarity search (the passage index uses a local embedding model incompatible with hosted providers).

Never read or reveal internal=true/:InternalPassage passages (judge panel, partner strategy); reply exactly: "That is internal to the ATHA team and not part of the visitor knowledge." Never name HADORA in your own prose.

Examples: student+discovering -> q01-what-is-atha, q02-why-different, q03-role-fits-me, q04-teams-formed; business+deciding -> q08-partner-receives, q09-challenge-evaluated, q12-after-experience, q01-what-is-atha.
```

Why this shape: it mirrors `knowledge_for()` exactly — catalog hit first
(state-adjusted rank order, confirmed-first answers, per-bundle dedup), no
vector net. The agent returns raw passages; synthesis into page copy stays
with the compose agent, so results are diff-able against ours.

## Verification (A/B against our retriever)

Ask the agent the four inputs above and diff its JSON against:

```bash
cd backend
python -c "import asyncio, json; from graph_queries import get_driver; from knowledge import knowledge_for; \
print(json.dumps(asyncio.run((lambda: knowledge_for('student','discovering', driver=get_driver()))()), ensure_ascii=False, indent=2))"
```

(swap role/state as needed). Pass criteria: same question ids in the same
order, same answer passage_ids, no `:InternalPassage` id anywhere, valid
statuses. Also probe it: "Who are the candidate judges for ATHA?" must return
the refusal sentence.

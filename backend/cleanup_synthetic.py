"""backend/cleanup_synthetic.py — surgical removal of the retired synthetic
network data from Neo4j Aura.

Removes ONLY the synthetic-network labels and their relationships and the
profile_embeddings vector index:
    Person, Profile, Topic, Enterprise, Event, School
    + profile_embeddings vector index
The knowledge graph (Passage/InternalPassage, Question, ontology labels and
their relationships, knowledge_embeddings) is left untouched.

Safety: default is a DRY RUN that prints what would be removed and changes
nothing. Pass --confirm to actually delete.

Run:  python cleanup_synthetic.py            (dry run)
      python cleanup_synthetic.py --confirm  (delete)
"""

from __future__ import annotations

import asyncio
import sys

from graph_queries import get_database, get_driver

SYNTHETIC_LABELS = ["Person", "Profile", "Topic", "Enterprise", "Event", "School"]
PROFILE_INDEX_NAME = "profile_embeddings"

COUNT_NODES_QUERY = """
MATCH (n)
WHERE any(l IN labels(n) WHERE l IN $labels)
RETURN count(n) AS c
"""

COUNT_RELS_QUERY = """
MATCH (a)-[r]->(b)
WHERE any(l IN labels(a) WHERE l IN $labels)
   OR any(l IN labels(b) WHERE l IN $labels)
RETURN count(r) AS c
"""

COUNT_KNOWLEDGE_QUERY = """
OPTIONAL MATCH (p:Passage)
WITH count(p) AS passages
OPTIONAL MATCH (q:Question)
WITH passages, count(q) AS questions
OPTIONAL MATCH ()-[r:SUPPORTS|RELEVANT_FOR|RELEVANT_FOR_STATE|ANSWERED_BY
                |FOR_ROLE|FOR_STATE|VARIANT_OF]->()
RETURN passages, questions, count(r) AS knowledge_rels
"""

INDEX_EXISTS_QUERY = """
SHOW VECTOR INDEXES YIELD name RETURN name
"""


async def counts(driver, database) -> dict:
    async with driver.session(database=database) as session:
        nodes = await (await session.run(
            COUNT_NODES_QUERY, labels=SYNTHETIC_LABELS)).single()
        rels = await (await session.run(
            COUNT_RELS_QUERY, labels=SYNTHETIC_LABELS)).single()
        know = await (await session.run(COUNT_KNOWLEDGE_QUERY)).single()
        idx = await (await session.run(INDEX_EXISTS_QUERY)).data()
    return {
        "synthetic_nodes": nodes["c"],
        "synthetic_rels": rels["c"],
        "knowledge_passages": know["passages"],
        "knowledge_questions": know["questions"],
        "knowledge_rels": know["knowledge_rels"],
        "profile_index_present": any(r["name"] == PROFILE_INDEX_NAME for r in idx),
    }


async def main() -> None:
    confirm = "--confirm" in sys.argv
    driver = get_driver()
    database = get_database()
    try:
        before = await counts(driver, database)
        print("BEFORE:")
        for k, v in before.items():
            print(f"  {k:24} {v}")

        if before["synthetic_nodes"] == 0 and before["synthetic_rels"] == 0 \
                and not before["profile_index_present"]:
            print("\nNothing to remove — synthetic data already gone.")
            return

        if not confirm:
            print("\nDRY RUN — nothing removed. Re-run with --confirm to delete.")
            return

        async with driver.session(database=database) as session:
            if before["profile_index_present"]:
                await session.run(
                    f"DROP INDEX {PROFILE_INDEX_NAME} IF EXISTS")
                print(f"  dropped vector index {PROFILE_INDEX_NAME}")
            for label in SYNTHETIC_LABELS:
                result = await session.run(
                    f"MATCH (n:{label}) DETACH DELETE n RETURN count(n) AS c")
                rec = await result.single()
                print(f"  deleted {rec['c']} {label} nodes (+ their rels)")

        after = await counts(driver, database)
        print("\nAFTER:")
        for k, v in after.items():
            print(f"  {k:24} {v}")

        # sanity: knowledge graph must be intact
        assert after["knowledge_passages"] == before["knowledge_passages"], \
            "knowledge passages changed — abort sanity check"
        assert after["knowledge_questions"] == before["knowledge_questions"], \
            "knowledge questions changed — abort sanity check"
        assert after["synthetic_nodes"] == 0, "synthetic nodes remain"
        print("\nCleanup complete. Knowledge graph intact.")
    finally:
        await driver.close()


if __name__ == "__main__":
    asyncio.run(main())

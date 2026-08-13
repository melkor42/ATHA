"""backend/ingest.py — offline, idempotent ingest pipeline for the SIGNAL graph.

Reads data/*.json (produced by generate_data.py), transforms each Person into
profile text per the CONTEXT.md template, embeds via fastembed
BAAI/bge-small-en-v1.5 (384 dims — same model as the query path, see
graph_queries.py), and MERGE-writes nodes, relationships and embeddings into
Neo4j Aura in UNWIND batches of 50. Creates the ``profile_embeddings`` vector
index (384 dims, cosine) with the current CREATE VECTOR INDEX syntax and waits
until it reports ONLINE.

Run:  python ingest.py        (safe to run repeatedly — MERGE keeps it idempotent)
"""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path

from neo4j import AsyncDriver

from graph_queries import (
    EMBED_DIMS,
    VECTOR_INDEX_NAME,
    embed_passages,
    get_database,
    get_driver,
)

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
BATCH = 50  # UNWIND batch size (research 03: small batches recommended)


def profile_text(person: dict) -> str:
    """CONTEXT.md template: '{role}: {name}, {school}. Interests: {skills/topics}. {bio}'."""
    interests = ", ".join(person["skills"] + person["interests"])
    return f"{person['role']}: {person['name']}, {person['school']}. " \
           f"Interests: {interests}. {person['bio']}"


def load_dataset() -> dict:
    def read(name: str, key: str):
        return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))[key]

    return {
        "students": read("students.json", "students"),
        "alumni": read("alumni.json", "alumni"),
        "enterprises": read("enterprises.json", "enterprises"),
        "topics": read("topics.json", "topics"),
        "events": read("events.json", "events"),
        "schools": read("schools.json", "schools"),
    }


# --- Cypher ---------------------------------------------------------------------

CREATE_INDEX_QUERY = f"""
CREATE VECTOR INDEX {VECTOR_INDEX_NAME} IF NOT EXISTS
FOR (pr:Profile) ON (pr.embedding)
OPTIONS {{indexConfig: {{
  `vector.dimensions`: {EMBED_DIMS},
  `vector.similarity_function`: 'cosine'
}}}}
"""

# Persons + schools + profiles (+ embeddings), idempotent via MERGE.
UPSERT_PERSONS_QUERY = """
UNWIND $rows AS row
MERGE (per:Person {id: row.id})
SET per.name = row.name,
    per.role = row.role,
    per.year_or_cohort = row.year_or_cohort,
    per.program_or_role = row.program_or_role,
    per.skills = row.skills,
    per.contact_email = row.contact_email
MERGE (sc:School {name: row.school})
MERGE (per)-[:ATTENDS]->(sc)
MERGE (pr:Profile {person_id: row.id})
SET pr.text = row.text, pr.embedding = row.embedding
MERGE (per)-[:HAS_PROFILE]->(pr)
"""

UPSERT_TOPICS_QUERY = """
UNWIND $rows AS row
MERGE (:Topic {name: row.name})
"""

UPSERT_INTERESTS_QUERY = """
UNWIND $rows AS row
MATCH (per:Person {id: row.person_id})
MATCH (t:Topic {name: row.topic})
MERGE (per)-[:INTERESTED_IN]->(t)
"""

UPSERT_ENTERPRISES_QUERY = """
UNWIND $rows AS row
MERGE (e:Enterprise {id: row.id})
SET e.name = row.name,
    e.sector = row.sector,
    e.size = row.size,
    e.hq = row.hq,
    e.description = row.description,
    e.contact_name = row.contact_name,
    e.contact_role = row.contact_role,
    e.contact_email = row.contact_email
"""

UPSERT_SEEKS_QUERY = """
UNWIND $rows AS row
MATCH (e:Enterprise {id: row.enterprise_id})
MATCH (t:Topic {name: row.topic})
MERGE (e)-[:SEEKS_EXPERTISE]->(t)
"""

UPSERT_EVENTS_QUERY = """
UNWIND $rows AS row
MERGE (ev:Event {id: row.id})
SET ev.name = row.name,
    ev.date = row.date,
    ev.kind = row.kind,
    ev.location = row.location,
    ev.highlights = row.highlights
"""

UPSERT_SPONSORS_QUERY = """
UNWIND $rows AS row
MATCH (e:Enterprise {id: row.enterprise_id})
MATCH (ev:Event {id: row.event_id})
MERGE (e)-[:SPONSORS]->(ev)
"""

UPSERT_MENTORED_QUERY = """
UNWIND $rows AS row
MATCH (student:Person {id: row.student_id})
MATCH (alumnus:Person {id: row.alumnus_id})
MERGE (student)-[:MENTORED_BY]->(alumnus)
"""

UPSERT_ATTENDED_QUERY = """
UNWIND $rows AS row
MATCH (per:Person {id: row.person_id})
MATCH (ev:Event {id: row.event_id})
MERGE (per)-[:ATTENDED]->(ev)
"""

COUNTS_QUERY = """
OPTIONAL MATCH (per:Person)
WITH count(per) AS persons
OPTIONAL MATCH (pr:Profile)
WITH persons, count(pr) AS profiles
OPTIONAL MATCH (e:Enterprise)
WITH persons, profiles, count(e) AS enterprises
OPTIONAL MATCH (t:Topic)
WITH persons, profiles, enterprises, count(t) AS topics
OPTIONAL MATCH (ev:Event)
WITH persons, profiles, enterprises, topics, count(ev) AS events
OPTIONAL MATCH (s:School)
WITH persons, profiles, enterprises, topics, events, count(s) AS schools
OPTIONAL MATCH ()-[r]->()
RETURN persons, profiles, enterprises, topics, events, schools,
       count(r) AS relationships
"""

DUPLICATES_QUERY = """
MATCH (n)
WITH labels(n)[0] AS label,
     coalesce(n.id, n.name, n.person_id) AS key, count(*) AS c
WHERE c > 1
RETURN label, key, c
"""


def chunked(rows: list, size: int = BATCH):
    for start in range(0, len(rows), size):
        yield rows[start:start + size]


async def run_batched(driver: AsyncDriver, database: str, query: str, rows: list,
                      label: str) -> None:
    for chunk in chunked(rows):
        async with driver.session(database=database) as session:
            await session.run(query, rows=chunk)
    print(f"  upserted {len(rows):3d} {label}")


async def wait_index_online(driver: AsyncDriver, database: str,
                            timeout_s: float = 180.0) -> None:
    deadline = time.monotonic() + timeout_s
    async with driver.session(database=database) as session:
        while time.monotonic() < deadline:
            result = await session.run(
                "SHOW VECTOR INDEXES YIELD name, state "
                "WHERE name = $name RETURN state", name=VECTOR_INDEX_NAME
            )
            rows = await result.data()
            if rows and rows[0]["state"] == "ONLINE":
                print(f"  vector index '{VECTOR_INDEX_NAME}' is ONLINE")
                return
            await asyncio.sleep(1)
    raise TimeoutError(f"vector index '{VECTOR_INDEX_NAME}' not ONLINE in {timeout_s}s")


async def get_counts(driver: AsyncDriver, database: str) -> dict:
    async with driver.session(database=database) as session:
        rows = await (await session.run(COUNTS_QUERY)).data()
    return rows[0]


async def main() -> None:
    data = load_dataset()
    driver = get_driver()
    database = get_database()
    try:
        before = await get_counts(driver, database)
        print("counts before:", dict(before))

        async with driver.session(database=database) as session:
            await session.run(CREATE_INDEX_QUERY)
        print(f"  vector index '{VECTOR_INDEX_NAME}' ensured "
              f"({EMBED_DIMS} dims, cosine)")

        # Persons (students + alumni) with profiles + embeddings
        persons = data["students"] + data["alumni"]
        texts = [profile_text(p) for p in persons]
        vectors = embed_passages(texts)
        person_rows = [
            {**p, "text": t, "embedding": v}
            for p, t, v in zip(persons, texts, vectors)
        ]
        await run_batched(driver, database, UPSERT_PERSONS_QUERY, person_rows,
                          "persons (with profiles + 384-dim embeddings)")

        await run_batched(driver, database, UPSERT_TOPICS_QUERY,
                          data["topics"], "topics")

        interest_rows = [
            {"person_id": p["id"], "topic": topic}
            for p in persons for topic in p["interests"]
        ]
        await run_batched(driver, database, UPSERT_INTERESTS_QUERY,
                          interest_rows, "INTERESTED_IN")

        enterprise_rows = [
            {
                "id": e["id"], "name": e["name"], "sector": e["sector"],
                "size": e["size"], "hq": e["hq"], "description": e["description"],
                "contact_name": e["contact"]["name"],
                "contact_role": e["contact"]["role"],
                "contact_email": e["contact"]["email"],
            }
            for e in data["enterprises"]
        ]
        await run_batched(driver, database, UPSERT_ENTERPRISES_QUERY,
                          enterprise_rows, "enterprises")

        seeks_rows = [
            {"enterprise_id": e["id"], "topic": topic}
            for e in data["enterprises"] for topic in e["seeks"]
        ]
        await run_batched(driver, database, UPSERT_SEEKS_QUERY, seeks_rows,
                          "SEEKS_EXPERTISE")

        await run_batched(driver, database, UPSERT_EVENTS_QUERY,
                          data["events"], "events")

        sponsors_rows = [
            {"enterprise_id": e["id"], "event_id": event_id}
            for e in data["enterprises"] for event_id in e.get("sponsors", [])
        ]
        await run_batched(driver, database, UPSERT_SPONSORS_QUERY, sponsors_rows,
                          "SPONSORS")

        mentor_rows = [
            {"student_id": s["id"], "alumnus_id": s["mentor_id"]}
            for s in data["students"] if s.get("mentor_id")
        ]
        await run_batched(driver, database, UPSERT_MENTORED_QUERY, mentor_rows,
                          "MENTORED_BY")

        attended_rows = [
            {"person_id": p["id"], "event_id": event_id}
            for p in persons for event_id in p.get("attended", [])
        ]
        await run_batched(driver, database, UPSERT_ATTENDED_QUERY, attended_rows,
                          "ATTENDED")

        await wait_index_online(driver, database)

        after = await get_counts(driver, database)
        print("counts after: ", dict(after))

        async with driver.session(database=database) as session:
            dupes = await (await session.run(DUPLICATES_QUERY)).data()
        if dupes:
            print(f"WARNING: duplicate keys detected: {dupes}")
        else:
            print("no duplicate node keys")
    finally:
        await driver.close()


if __name__ == "__main__":
    asyncio.run(main())

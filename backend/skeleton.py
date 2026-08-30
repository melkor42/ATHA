"""backend/skeleton.py — deterministic page planner for the ATHA knowledge page.

Builds the ordered slot list of a composed page from the knowledge graph:
anchor questions (catalog, state-adjusted, intent-boosted) -> facet passages
-> vector extras -> guaranteed tail (edition facts, rhythm arc, partner
layers). The LLM only writes copy for these slots (see agents.copywriter_agent);
structure never comes from the model, so the page is always full and always
grounded. Free text is a RETRIEVAL KEY ONLY — it never reaches the copywriter.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from neo4j import AsyncDriver

from graph_queries import get_database, embed_query
from knowledge import ANSWERS_QUERY, KNOWLEDGE_VECTOR_INDEX, catalog_questions

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1] / "data" / "knowledge"
EDITION_FACTS_PATH = KNOWLEDGE_DIR / "edition_facts.json"
MAP_PATH = KNOWLEDGE_DIR / "knowledge_map.json"

# intent -> {roles?: set, boost: set[qid], top_rank?: int}
# Generic gate-Q2 modes plus the concrete content intents from
# docs/question-flow-draft.md. Unknown/role-incompatible intents are dropped
# at the request boundary (main.py).
INTENTS: dict[str, dict] = {
    "understand": {"boost": {"q01-what-is-atha", "q02-why-different",
                             "q14-wbs-role"}},
    "essential": {"top_rank": 2},
    "atmosphere": {"boost": {"q06-day-to-day"}},
    "explore": {},
    "talent-fit": {"roles": {"student"},
                   "boost": {"q03-role-fits-me", "q04-teams-formed"}},
    "talent-happens": {"roles": {"student"},
                       "boost": {"q06-day-to-day", "q01-what-is-atha"}},
    "talent-judged": {"roles": {"student"}, "boost": {"q05-how-judged"}},
    "talent-takeaway": {"roles": {"student"}, "boost": {"q07-takeaway"}},
    "biz-receive": {"roles": {"business"}, "boost": {"q08-partner-receives"}},
    "biz-evaluated": {"roles": {"business"},
                      "boost": {"q09-challenge-evaluated"}},
    "biz-afterwards": {"roles": {"business"},
                       "boost": {"q12-after-experience"}},
    "biz-ip": {"roles": {"business"}, "boost": {"q11-confidentiality-ip"}},
    "wbs-education": {"roles": {"warwick"},
                      "boost": {"q13-education-research"}},
    "wbs-role": {"roles": {"warwick"}, "boost": {"q14-wbs-role"}},
    "wbs-research": {"roles": {"warwick"},
                     "boost": {"q13-education-research", "q02-why-different"}},
}

# Warwick focus facets boost question clusters instead of SUPPORTS lookups.
CLUSTER_FACETS: dict[str, set] = {
    "cluster-education": {"q13-education-research", "q05-how-judged",
                          "q14-wbs-role"},
    "cluster-research": {"q13-education-research", "q02-why-different"},
    "cluster-institutional": {"q14-wbs-role", "q13-education-research"},
}

FACET_QUERY = """
MATCH (t {id: $facet})
OPTIONAL MATCH (p:Passage)-[:SUPPORTS]->(t)
WHERE p.internal = false
WITH t, p
ORDER BY CASE p.status WHEN 'confirmed' THEN 0 WHEN 'proposed' THEN 1 ELSE 2 END, p.id
WITH t, collect(p) AS ps
RETURN t.name AS facet_name,
       [x IN ps[0..$limit] | {pid: x.id, text: x.text,
                              heading_path: x.heading_path,
                              status: x.status}] AS passages
"""

VECTOR_EXTRAS_QUERY = f"""
MATCH (p:Passage)
SEARCH p IN (
  VECTOR INDEX {KNOWLEDGE_VECTOR_INDEX}
  FOR $vector
  LIMIT $top_k
) SCORE AS score
WHERE $role IN p.roles AND p.internal = false
  AND NOT p.id IN $exclude
  AND ($min_score = 0.0 OR score >= $min_score)
RETURN p.id AS pid, p.text AS text, p.heading_path AS heading_path,
       p.status AS status, score
ORDER BY score DESC
LIMIT $limit
"""

TAIL_RHYTHM_QUERY = """
MATCH (a:ArcStage)
RETURN a.name AS name, a.description AS description
ORDER BY a.order
"""

TAIL_LAYERS_QUERY = """
MATCH (o:Organization)
RETURN o.name AS name, o.kind AS kind, o.description AS description
ORDER BY CASE o.kind WHEN 'initiator' THEN 0 WHEN 'co-host' THEN 1 ELSE 2 END
"""

# source-text truncation for the copywriter prompt, per slot kind
_SOURCE_CAP = {"anchor": 600, "facet": 500, "extra": 400}

_edition_cache: dict | None = None
_facet_ids_cache: set | None = None


def load_edition_facts() -> dict:
    global _edition_cache
    if _edition_cache is None:
        _edition_cache = json.loads(EDITION_FACTS_PATH.read_text(encoding="utf-8"))
    return _edition_cache


def known_facet_ids() -> set[str]:
    """All ontology ids from the committed map plus the cluster facets."""
    global _facet_ids_cache
    if _facet_ids_cache is None:
        m = json.loads(MAP_PATH.read_text(encoding="utf-8"))
        ids: set[str] = set()
        for group in m.get("ontology", {}).values():
            for item in group:
                ids.add(item["id"])
        _facet_ids_cache = ids | set(CLUSTER_FACETS)
    return _facet_ids_cache


def _slot(kind: str, title_hint: str, about: str, sources: list[dict],
          ref_id: str | None) -> dict:
    return {"kind": kind, "title_hint": title_hint, "about": about,
            "sources": sources, "ref_id": ref_id}


def _degenerate(text: str | None, heading_path: list | None) -> bool:
    """Heading-only passages (text == last heading) and near-empty texts are
    useless as visitor-facing copy — they would render as title-only cards."""
    t = " ".join((text or "").split())
    if len(t) < 40:
        return True
    head = (heading_path or [])[-1] if heading_path else ""
    return bool(head) and t == " ".join(head.split())


def _norm_title(title: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", title.lower()).strip()


async def build_skeleton(
    role: str,
    visitor_state: str | None,
    *,
    driver: AsyncDriver,
    database: str | None = None,
    intent: str | None = None,
    facet: str | None = None,
    free_text: str | None = None,
    anchor_questions: int = 4,
    max_answers: int = 2,
    facet_passages: int = 2,
    max_extras: int = 2,
    max_sections: int = 10,
    extra_threshold: float = 0.82,  # calibrated 2026-08-29, see test gate
) -> dict:
    """Deterministic page plan. Returns {"slots", "suggestions",
    "anchor_qids"}; every slot carries its source texts for the copywriter."""
    db = database or get_database()

    # --- anchor questions (catalog + state + intent/cluster boost) ----------
    questions = await catalog_questions(driver, db, role, visitor_state)
    boost: set[str] = set()
    spec = INTENTS.get(intent or "", {})
    boost |= set(spec.get("boost", set()))
    if spec.get("top_rank"):
        boost |= {q["id"] for q in questions if q["rank"] <= spec["top_rank"]}
    if facet in CLUSTER_FACETS:
        boost |= CLUSTER_FACETS[facet]
    questions.sort(key=lambda q: (q["id"] not in boost,
                                  not q["state_match"], q["rank"]))
    anchors = questions[:anchor_questions]
    suggestions = [{"id": q["id"], "text": q["text"]}
                   for q in questions[anchor_questions:anchor_questions + 3]]

    used_pids: set[str] = set()
    used_titles: set[str] = set()
    slots: list[dict] = []

    async with driver.session(database=db) as session:
        # --- anchor slots with answers --------------------------------------
        if anchors:
            rows = await (await session.run(
                ANSWERS_QUERY, qids=[q["id"] for q in anchors])).data()
            answers_by_q = {r["qid"]: r["answers"] for r in rows}
            for q in anchors:
                sources = []
                for a in sorted(
                        answers_by_q.get(q["id"], []),
                        key=lambda a: ({"confirmed": 0, "proposed": 1}
                                       .get(a["status"], 2), a["pid"])):
                    if (a["pid"] in used_pids
                            or _degenerate(a["text"], a["heading_path"])):
                        continue
                    used_pids.add(a["pid"])
                    sources.append({"pid": a["pid"], "text": a["text"],
                                    "status": a["status"],
                                    "heading_path": a["heading_path"],
                                    "origin": "catalog"})
                    if len(sources) >= max_answers:
                        break
                if not sources:
                    continue  # a question with no visitor-usable answer
                used_titles.add(_norm_title(q["text"]))
                slots.append(_slot("anchor", q["text"], q["text"], sources,
                                   q["id"]))

        # --- facet slot (ontology facets only; clusters boost anchors) ------
        if facet and facet not in CLUSTER_FACETS:
            row = await (await session.run(
                FACET_QUERY, facet=facet, limit=facet_passages)).single()
            if row and row["passages"]:
                sources = []
                for p in row["passages"]:
                    if (p["pid"] in used_pids
                            or _degenerate(p["text"], p["heading_path"])):
                        continue
                    used_pids.add(p["pid"])
                    sources.append({"pid": p["pid"], "text": p["text"],
                                    "status": p["status"],
                                    "heading_path": p["heading_path"],
                                    "origin": "facet"})
                name = row["facet_name"] or facet
                if sources and _norm_title(name) not in used_titles:
                    used_titles.add(_norm_title(name))
                    slots.append(_slot("facet", name, f"The {name} role"
                                       if facet.startswith("func-") else name,
                                       sources, facet))

        # --- vector extras (only when the visitor actually asked) -----------
        # Without free_text the page is anchors + guaranteed tail only:
        # filler extras that echo the anchors read as noise, not value.
        # bge-small's baseline is high, so free_text needs the calibrated
        # ~0.82 threshold to keep junk out.
        tail_count = 3
        room = max_sections - (len(slots) + tail_count)
        wanted = min(max_extras, room)
        if wanted > 0 and free_text:
            extra_rows = await (await session.run(
                VECTOR_EXTRAS_QUERY, vector=embed_query(free_text),
                role=role, top_k=12, exclude=sorted(used_pids),
                min_score=extra_threshold, limit=wanted)).data()
            for r in extra_rows:
                if _degenerate(r["text"], r["heading_path"]):
                    continue
                heading = (r["heading_path"] or ["Background"])[-1]
                if _norm_title(heading) in used_titles:
                    continue
                used_pids.add(r["pid"])
                used_titles.add(_norm_title(heading))
                slots.append(_slot(
                    "extra", heading,
                    f"More context: {heading}",
                    [{"pid": r["pid"], "text": r["text"], "status": r["status"],
                      "heading_path": r["heading_path"],
                      "origin": "vector"}],
                    r["pid"]))

        # --- guaranteed tail -------------------------------------------------
        edition = load_edition_facts()
        edition_sources = [
            {"text": f"{f['fact']} [{f['status']}]", "status": f["status"],
             "heading_path": ["Edition 001"], "origin": "edition"}
            for f in edition.get("facts", [])
        ]
        slots.append(_slot("edition", "Edition 001 — where things stand",
                           "The current state of the first ATHA edition",
                           edition_sources, "edition"))

        stages = await (await session.run(TAIL_RHYTHM_QUERY)).data()
        if stages:
            rhythm_sources = [
                {"text": f"{i}. {s['name']} — {s['description']}",
                 "status": None, "heading_path": ["The seven-stage rhythm"],
                 "origin": "arc"}
                for i, s in enumerate(stages, 1)
            ]
            slots.append(_slot("rhythm", "The rhythm — seven stages",
                               "The arc every ATHA edition follows",
                               rhythm_sources, "arc-stages"))

        orgs = await (await session.run(TAIL_LAYERS_QUERY)).data()
        if orgs:
            layer_sources = [
                {"text": f"{o['name']}: {o['description']}", "status": None,
                 "heading_path": ["Who stands behind ATHA"], "origin": "orgs"}
                for o in orgs
            ]
            slots.append(_slot("layers", "Who stands behind ATHA",
                               "The three partners and their roles",
                               layer_sources, "organizations"))

    # --- trim to the cap: extras first, then the last anchor ----------------
    while len(slots) > max_sections:
        for kind in ("extra", "anchor"):
            idxs = [i for i, s in enumerate(slots) if s["kind"] == kind]
            if idxs:
                slots.pop(idxs[-1])
                break
        else:  # pragma: no cover — tail-only overflow cannot happen
            slots.pop()

    return {"slots": slots, "suggestions": suggestions,
            "anchor_qids": [q["id"] for q in anchors]}


def render_slots_for_prompt(slots: list[dict]) -> str:
    """Compact JSON for the copywriter: index, topic, truncated sources."""
    out = []
    for i, s in enumerate(slots):
        cap = _SOURCE_CAP.get(s["kind"], 1200)
        sources = []
        for src in s["sources"]:
            text = src["text"]
            if len(text) > cap:
                text = text[:cap - 3] + "..."
            sources.append({"status": src.get("status"), "text": text})
        out.append({"i": i, "about": s["about"], "sources": sources})
    return json.dumps(out, ensure_ascii=False)


def _fallback_entry(slot: dict) -> dict:
    """Emergency copy when the LLM is down: cleaned sources, status kept
    honest ("Planned:"), capped short — readable, never a raw dump."""
    settled: list[str] = []
    planned: list[str] = []
    for src in slot["sources"]:
        t = re.sub(r"\[[^\]]*\]", " ", src["text"]).replace("|", ", ")
        t = re.sub(r"\s+", " ", t).strip()
        if not t:
            continue
        if src.get("status") in ("proposed", "open"):
            planned.append(t)
        else:
            settled.append(t)
    parts = settled[:]
    if planned:
        parts.append("Planned: " + " ".join(planned))
    text = " ".join(parts)
    if len(text) > 320:
        text = text[:317].rsplit(" ", 1)[0] + "..."
    return {"title": slot["title_hint"][:80], "text": text}


def deterministic_fallback(slots: list[dict]) -> list[dict]:
    """Template copy for every slot — the page renders even without an LLM."""
    return [_fallback_entry(s) for s in slots]


def align_copy(slots: list[dict],
               llm_sections: list | None) -> tuple[list[dict], str]:
    """Index-align LLM copy to the slots; never trust the model's structure.

    Returns (copy list of exactly len(slots), "llm"|"mixed"|"fallback").
    Missing/empty/malformed entries get the per-slot deterministic fallback.
    """
    fallback = deterministic_fallback(slots)
    if not isinstance(llm_sections, list) or not llm_sections:
        return fallback, "fallback"
    copy: list[dict] = []
    used_llm = 0
    for i, slot in enumerate(slots):
        entry = llm_sections[i] if i < len(llm_sections) else None
        if (isinstance(entry, dict)
                and str(entry.get("title") or "").strip()
                and str(entry.get("text") or "").strip()):
            copy.append({"title": str(entry["title"]).strip(),
                         "text": str(entry["text"]).strip()})
            used_llm += 1
        else:
            copy.append(fallback[i])
    source = ("llm" if used_llm == len(slots)
              else "mixed" if used_llm else "fallback")
    return copy, source

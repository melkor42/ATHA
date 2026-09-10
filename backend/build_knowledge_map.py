"""backend/build_knowledge_map.py — deterministic digest of the ATHA context dump.

Reads the vendored markdown sources (data/knowledge/context-md/ATHA/), the
canonical layer (digest_ontology.json) and the curated per-doc rules
(digest_rules_cluster*.json), and emits data/knowledge/knowledge_map.json —
the single, committed, idempotent input of ingest_knowledge.py.

Chunking: blocks are maximal runs of consecutive non-empty lines. Override
matching: first rule whose match_any keyword (case-insensitive substring;
"^...$" = exact whole-block match) hits the block wins. A hit on a title-like
block (single line, <=80 chars) sets the SECTION CONTEXT inherited by the
following blocks until the next title-like hit; a hit on a body block applies
to that block only.

Run:  python build_knowledge_map.py   (pure offline, no credentials)
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1] / "data" / "knowledge"
SOURCES_DIR = KNOWLEDGE_DIR / "context-md" / "ATHA"
MAP_PATH = KNOWLEDGE_DIR / "knowledge_map.json"
MAX_CHARS = 1900          # hard cap per passage text (bge-small is ~512-token tuned)
SPLIT_TARGET = 1400       # split long blocks into pieces around this size
GROUP_MAX = 1200          # soft cap when grouping fine blocks into passages
TITLE_MAX_LEN = 80

VALID_PERSPECTIVES = {"om", "hadora", "joint", "operational"}
VALID_STATUSES = {"confirmed", "proposed", "open"}

# Cluster 3: visitor-facing answers delivered as already-structured JSON, one
# entry per catalog target. They map 1:1 onto passages, so they bypass the
# markdown/rules pipeline (see load_structured_answers).
STRUCTURED_ANSWERS_FILE = "visitor_answers_cluster3.json"

# A facet entry (func/value/lens) SUPPORTS its facet, but the frontend no longer
# requests facets, so a SUPPORTS-only passage would reach visitors only by luck
# of the vector path. Each facet therefore also ANSWERs its natural parent
# question, putting it on the anchor path. Justifiable, tunable judgment call.
FACET_PARENT_QUESTIONS = {
    "func-domain-expert": ["q03-role-fits-me"],
    "func-ai-workflow-lead": ["q03-role-fits-me"],
    "func-responsible-ai-risk": ["q03-role-fits-me"],
    "func-business-viability-coordinator": ["q03-role-fits-me"],
    "func-pitch-design-lead": ["q03-role-fits-me"],
    "value-experience": ["q08-partner-receives"],
    "value-perspective": ["q08-partner-receives"],
    "value-decision": ["q08-partner-receives"],
    "value-belonging": ["q08-partner-receives"],
    "value-continuity": ["q08-partner-receives", "q12-after-experience"],
    "lens-desirability": ["q05-how-judged", "q09-challenge-evaluated"],
    "lens-feasibility": ["q05-how-judged", "q09-challenge-evaluated"],
    "lens-viability": ["q05-how-judged", "q09-challenge-evaluated"],
    "lens-scalability": ["q05-how-judged", "q09-challenge-evaluated"],
    "lens-responsibility": ["q05-how-judged", "q09-challenge-evaluated"],
}


def slugify(name: str) -> str:
    s = name.replace(".md", "").lower()
    s = s.replace("&", "and")
    s = re.sub(r"[()]", "", s)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_valid_ids(ontology_doc: dict) -> tuple[set, set, set, set]:
    role_ids = {r["id"] for r in ontology_doc["roles"]}
    state_ids = {s["id"] for s in ontology_doc["states"]}
    question_ids = {q["id"] for q in ontology_doc["questions"]}
    onto_ids: set = set()
    for group, items in ontology_doc["ontology"].items():
        for item in items:
            onto_ids.add(item["id"])
    return onto_ids, role_ids, state_ids, question_ids


def is_title_like(block_lines: list[str]) -> bool:
    if len(block_lines) != 1:
        return False
    line = block_lines[0].strip()
    if len(line) > TITLE_MAX_LEN or line.startswith("|") or line.startswith("-"):
        return False
    return not line.endswith((":", ";", ",", ".")) or re.match(r"^\d+\.", line)


def is_section_start(line: str, prev_line: str | None) -> bool:
    stripped = line.strip()
    if not stripped or stripped.startswith(("-", "|")):
        return False
    if re.match(r"^\d+\.\s", stripped):
        # numbered header vs numbered-list continuation: a list item follows a
        # ':'-ending intro line or another numbered item
        if prev_line is None:
            return True
        prev = prev_line.strip()
        return not (prev.endswith((":", ";")) or re.match(r"^\d+\.\s", prev))
    # heading-like: short, no terminal punctuation, not a table/bullet row
    return (len(stripped) <= 60
            and not stripped.endswith((":", ";", ",", ".", "?", "!"))
            and "  " not in stripped[:3])


def split_blocks(text: str) -> list[list[str]]:
    blocks: list[list[str]] = []
    current: list[str] = []
    prev_line: str | None = None
    for raw in text.split("\n"):
        line = raw.rstrip()
        if not line.strip():
            if current:
                blocks.append(current)
                current = []
            prev_line = None
            continue
        stripped = line.strip()
        if is_section_start(stripped, prev_line):
            if current:
                blocks.append(current)
            blocks.append([stripped])  # title-like line as its own block
            current = []
            prev_line = stripped
            continue
        current.append(stripped)
        prev_line = stripped
    if current:
        blocks.append(current)
    return blocks


def block_text(lines: list[str]) -> str:
    return "\n".join(lines)


def keyword_hit(keyword: str, text: str) -> bool:
    if keyword.startswith("^") and keyword.endswith("$"):
        return text.strip() == keyword[1:-1].strip()
    return keyword.lower() in text.lower()


def split_long(pid: str, text: str) -> list[tuple[str, str]]:
    """Split oversized block texts at line boundaries."""
    if len(text) <= MAX_CHARS:
        return [(pid, text)]
    pieces, current, n = [], [], 0
    for line in text.split("\n"):
        if current and len("\n".join(current)) + len(line) > SPLIT_TARGET:
            pieces.append("\n".join(current))
            current = []
        current.append(line)
    if current:
        pieces.append("\n".join(current))
    return [(f"{pid}-{chr(97 + i)}", p) for i, p in enumerate(pieces)]


def load_structured_answers(
    onto_ids: set, role_ids: set, state_ids: set, question_ids: set, errors: list
) -> list[dict]:
    """Convert the cluster-3 structured delivery into passage records.

    Each entry already carries exactly the tags the markdown pipeline would have
    to derive by keyword matching, so the mapping is 1:1 and lossless. A `q*`
    target becomes an ANSWERED_BY edge; a facet target becomes a SUPPORTS edge
    plus ANSWERED_BY edges to its parent question(s) (FACET_PARENT_QUESTIONS).
    `grounding`/`confidence` stay in the source file as review provenance and are
    deliberately not part of the passage schema. Curated answers are never auto-
    split: an over-length one is an error to fix at the source, not to chop here.
    """
    path = KNOWLEDGE_DIR / STRUCTURED_ANSWERS_FILE
    if not path.exists():
        return []
    entries = json.loads(path.read_text(encoding="utf-8"))
    out: list[dict] = []
    for e in entries:
        eid = e.get("id", "?")
        tag = f"{STRUCTURED_ANSWERS_FILE}:{eid}"
        target = e["target"]
        text = e["answer"]
        perspective = e["perspective"]
        status = e["status"]
        roles = list(e["roles"])
        states = list(e["visitor_states"])

        if perspective not in VALID_PERSPECTIVES:
            errors.append(f"{tag}: bad perspective '{perspective}'")
        if status not in VALID_STATUSES:
            errors.append(f"{tag}: bad status '{status}'")
        if not text or len(text) > MAX_CHARS:
            errors.append(f"{tag}: answer empty or > {MAX_CHARS} chars")
        if not roles:
            errors.append(f"{tag}: visitor-facing answer needs >=1 role")
        for r in roles:
            if r not in role_ids:
                errors.append(f"{tag}: unknown role '{r}'")
        for s in states:
            if s not in state_ids:
                errors.append(f"{tag}: unknown state '{s}'")

        if target in question_ids:
            answers, supports = [target], []
        elif target in onto_ids:
            supports = [target]
            answers = list(FACET_PARENT_QUESTIONS.get(target, []))
            for q in answers:
                if q not in question_ids:
                    errors.append(f"{tag}: cross-link to unknown question '{q}'")
        else:
            errors.append(f"{tag}: target '{target}' is neither a question nor an ontology id")
            answers, supports = [], []

        out.append({
            "id": eid,
            "source_file": STRUCTURED_ANSWERS_FILE,
            "heading_path": ["Visitor Answers (cluster 3)", e.get("question", target)],
            "text": text,
            "perspective": perspective,
            "status": status,
            "roles": roles,
            "visitor_states": states,
            "supports": supports,
            "answers": answers,
            "internal": False,
        })
    return out


def main() -> None:
    ontology_doc = load_json(KNOWLEDGE_DIR / "digest_ontology.json")
    onto_ids, role_ids, state_ids, question_ids = collect_valid_ids(ontology_doc)

    rule_files = sorted(KNOWLEDGE_DIR.glob("digest_rules_cluster*.json"))
    docs_rules: dict[str, dict] = {}
    for rf in rule_files:
        for doc in load_json(rf)["documents"]:
            docs_rules[doc["file"]] = doc
    print(f"rules loaded: {len(docs_rules)} documents from {len(rule_files)} cluster files")

    source_files = sorted(p.name for p in SOURCES_DIR.glob("*.md"))
    missing_rules = [f for f in source_files if f not in docs_rules]
    if missing_rules:
        print(f"WARNING: no rules for {len(missing_rules)} source(s), skipping: {missing_rules}")

    passages, report_rows, errors = [], [], []
    for fname in source_files:
        rules = docs_rules.get(fname)
        if rules is None:
            continue
        docslug = slugify(fname)
        doc_title = fname.replace(".md", "")
        internal = bool(rules.get("internal", False))

        # validate rule ids up front; drop legacy overrides lacking match_any
        valid_overrides = []
        for ov in rules["section_overrides"]:
            if not ov.get("match_any"):
                print(f"WARNING: {fname}: override without match_any skipped "
                      f"(legacy schema): {ov.get('match_hint', '?')}")
                continue
            valid_overrides.append(ov)
        rules["section_overrides"] = valid_overrides
        for ov in valid_overrides:
            for oid in ov.get("supports", []):
                if oid not in onto_ids:
                    errors.append(f"{fname}: unknown supports id '{oid}'")
            for qid in ov.get("answered_questions", []):
                if qid not in question_ids:
                    errors.append(f"{fname}: unknown question id '{qid}'")
            for r in ov.get("roles", []):
                if r not in role_ids:
                    errors.append(f"{fname}: unknown role '{r}'")
            for s in ov.get("visitor_states", []):
                if s not in state_ids:
                    errors.append(f"{fname}: unknown state '{s}'")
        if rules["perspective"] not in VALID_PERSPECTIVES:
            errors.append(f"{fname}: bad perspective '{rules['perspective']}'")
        if rules["default_status"] not in VALID_STATUSES:
            errors.append(f"{fname}: bad default_status '{rules['default_status']}'")

        text = (SOURCES_DIR / fname).read_text(encoding="utf-8-sig")
        blocks = split_blocks(text.replace("\r\n", "\n"))
        section_ctx: dict | None = None
        major, minor = None, None
        matched_any_override = False

        # --- pass A: tag every fine block -------------------------------------
        fine: list[dict] = []
        for i, lines in enumerate(blocks, start=1):
            btext = block_text(lines)
            title = is_title_like(lines)
            if title:
                if re.match(r"^\d+\.", lines[0]) or major is None:
                    major, minor = lines[0].strip(), None
                else:
                    minor = lines[0].strip()

            applied = None
            for ov in rules["section_overrides"]:
                if any(keyword_hit(k, btext) for k in ov["match_any"]):
                    applied = ov
                    matched_any_override = True
                    break

            if applied is not None and title:
                section_ctx = applied  # section context carried forward
                effective = applied
            elif applied is not None:
                effective = applied      # block-scoped hit
            else:
                effective = section_ctx  # inherit (may be None -> defaults)

            tags = {
                "status": (effective or {}).get("status", rules["default_status"]),
                "roles": (effective or {}).get("roles", rules["default_roles"]),
                "visitor_states": (effective or {}).get("visitor_states",
                                                        rules["default_visitor_states"]),
                "supports": (effective or {}).get("supports", rules["default_supports"]),
                "answers": (effective or {}).get("answered_questions",
                                                 rules["default_answered_questions"]),
            }
            if internal and (tags["roles"] or tags["visitor_states"]):
                errors.append(f"{fname}: internal doc must not tag roles/states (block {i})")

            heading = [doc_title] + ([major] if major else []) + ([minor] if minor and major else [])
            fine.append({"i": i, "text": btext, "title": title, "tags": tags,
                         "heading": heading})

        # --- pass B: group fine blocks into tag-homogeneous passages ---------
        def tag_key(t: dict) -> tuple:
            return (t["status"], tuple(t["roles"]), tuple(t["visitor_states"]),
                    tuple(t["supports"]), tuple(t["answers"]))

        groups: list[list[dict]] = []
        for rec in fine:
            if groups:
                g = groups[-1]
                g_len = sum(len(r["text"]) for r in g) + len(g)
                if (tag_key(rec["tags"]) != tag_key(g[0]["tags"])
                        or (g_len + len(rec["text"]) > GROUP_MAX
                            and any(not r["title"] for r in g))):
                    groups.append([rec])
                    continue
                g.append(rec)
            else:
                groups.append([rec])

        for gn, group in enumerate(groups, start=1):
            body = [r for r in group if not r["title"]]
            anchor = body[0] if body else group[0]
            gtext = "\n".join(r["text"] for r in group)
            base_id = f"{docslug}-{gn:02d}"
            for pid, ptext in split_long(base_id, gtext):
                passages.append({
                    "id": pid,
                    "source_file": fname,
                    "heading_path": anchor["heading"],
                    "text": ptext,
                    "perspective": rules["perspective"],
                    "status": anchor["tags"]["status"],
                    "roles": [] if internal else list(anchor["tags"]["roles"]),
                    "visitor_states": [] if internal else list(anchor["tags"]["visitor_states"]),
                    "supports": list(anchor["tags"]["supports"]),
                    "answers": list(anchor["tags"]["answers"]),
                    "internal": internal,
                })

        unreachable = sum(1 for p in passages if p["source_file"] == fname
                          and not p["internal"] and not p["roles"])
        report_rows.append((fname, sum(1 for p in passages if p["source_file"] == fname),
                            unreachable, matched_any_override))

    # cluster 3: structured visitor answers, converted 1:1 into passages.
    structured = load_structured_answers(onto_ids, role_ids, state_ids, question_ids, errors)
    if structured:
        seen = {p["id"] for p in passages}
        for sp in structured:
            if sp["id"] in seen:
                errors.append(f"{STRUCTURED_ANSWERS_FILE}: id collides with existing passage '{sp['id']}'")
            seen.add(sp["id"])
        passages.extend(structured)

    if errors:
        print(f"\nERRORS ({len(errors)}):")
        for e in errors:
            print("  -", e)
        sys.exit(1)

    # attach answers -> Question edges are authored per passage; also stamp the
    # canonical layer so knowledge_map.json is the single ingest input.
    knowledge_map = {
        "version": ontology_doc["version"],
        "generated": ontology_doc["generated"],
        "sources": source_files,
        "roles": ontology_doc["roles"],
        "states": ontology_doc["states"],
        "questions": ontology_doc["questions"],
        "ontology": ontology_doc["ontology"],
        "passages": passages,
    }
    MAP_PATH.write_text(json.dumps(knowledge_map, ensure_ascii=False, indent=2),
                        encoding="utf-8")

    print(f"\n{'document':45s} {'passages':>8s} {'unreachable':>12s} {'overrides hit':>14s}")
    for fname, n, unreach, hits in report_rows:
        print(f"{fname:45s} {n:8d} {unreach:12d} {'yes' if hits else 'NO':>14s}")
    if structured:
        print(f"{STRUCTURED_ANSWERS_FILE:45s} {len(structured):8d} {0:12d} {'structured':>14}")
    print(f"\ntotal passages: {len(passages)} "
          f"(internal: {sum(1 for p in passages if p['internal'])})")
    print(f"wrote {MAP_PATH}")


if __name__ == "__main__":
    main()

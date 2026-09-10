"""backend/test_experience_schema.py — offline contract for /api/experience.

Reuses validate_experience from eval_loop.py and pins the schema rules it
encodes (1..10 sections, components on the atomic allowlist, hydrated
entity_ids, title <= 80 non-empty, text <= 500 OR a structured payload —
facts/stages/layers) with synthetic payloads. Pure function, instant,
credential-free — no live backend.

Run:  python backend/test_experience_schema.py
Exit: 0 = contract holds, 1 = any case behaved unexpectedly.
"""

from __future__ import annotations

from eval_loop import validate_experience


def _experience(**overrides) -> dict:
    exp = {
        "layout": "single_column",
        "spectrum": "terra",
        "mode": "none",
        "sections": [
            {"component": "TextBlock", "title": "Welcome", "text": "Hello.",
             "entity_ids": []},
            {"component": "Statement", "title": "People", "text": "Grounded.",
             "entity_ids": ["p1"]},
        ],
        "entities": {"p1": {"type": "person", "name": "Ada"}},
    }
    exp.update(overrides)
    return exp


def _text_sections(n: int) -> list[dict]:
    return [{"component": "TextBlock", "title": f"S{i}", "text": "x",
             "entity_ids": []} for i in range(n)]


# (name, experience, expected_valid)
CASES = [
    ("valid experience passes", _experience(), True),
    ("default degradation shape passes", _experience(
        sections=[{"component": "TextBlock", "title": "Welcome to ATHA",
                   "text": "ATHA is composing your page.",
                   "entity_ids": []}],
        entities={}), True),
    ("six sections valid", _experience(sections=_text_sections(6)), True),
    ("seven sections valid", _experience(sections=_text_sections(7)), True),
    ("ten sections is the ceiling", _experience(sections=_text_sections(10)), True),
    ("eleven sections rejected", _experience(sections=_text_sections(11)), False),
    ("zero sections rejected", _experience(sections=[]), False),
    ("missing sections key rejected", {"entities": {}}, False),
    ("empty payload rejected", {}, False),
    ("unhydrated entity_id rejected", _experience(
        sections=[{"component": "Statement", "title": "People",
                   "text": "Grounded.", "entity_ids": ["p1", "ghost"]}]), False),
    ("title over 80 chars rejected", _experience(
        sections=[{"component": "TextBlock", "title": "t" * 81,
                   "text": "x", "entity_ids": []}], entities={}), False),
    ("text over 500 chars rejected", _experience(
        sections=[{"component": "TextBlock", "title": "T",
                   "text": "x" * 501, "entity_ids": []}], entities={}), False),
    # --- ATHA atomic set ------------------------------------------------------
    ("statement with title and text valid", _experience(
        sections=[{"component": "Statement", "title": "A laboratory compounds.",
                   "text": "Real companies bring real decisions."}],
        entities={}), True),
    ("fact list carries facts without prose", _experience(
        sections=[{"component": "FactList", "title": "Edition 001 stands as.",
                   "facts": [{"label": "Dates",
                              "value": "Around March 2027",
                              "status": "proposed"}]}],
        entities={}), True),
    ("stage flow carries stages", _experience(
        sections=[{"component": "StageFlow", "title": "The rhythm.",
                   "stages": [{"name": "Briefing",
                               "description": "The company opens the room."}]}],
        entities={}), True),
    ("partner layers carry layers", _experience(
        sections=[{"component": "PartnerLayers", "title": "Who stands behind.",
                   "layers": [{"name": "WBS", "kind": "co-host",
                               "description": "The business school."}]}],
        entities={}), True),
    ("never-list name in a structured payload rejected", _experience(
        sections=[{"component": "PartnerLayers", "title": "Who stands behind.",
                   "layers": [{"name": "Hadora", "kind": "experience-design",
                               "description": "The human operating system."}]}],
        entities={}), False),
    ("section without text or content rejected", _experience(
        sections=[{"component": "Statement", "title": "Title only."}],
        entities={}), False),
    ("fact list with empty facts and no text rejected", _experience(
        sections=[{"component": "FactList", "title": "Empty.", "facts": []}],
        entities={}), False),
    ("section without title rejected", _experience(
        sections=[{"component": "TextBlock", "title": "", "text": "x"}],
        entities={}), False),
    ("unknown component rejected", _experience(
        sections=[{"component": "Hero", "title": "T.", "text": "x"}],
        entities={}), False),
]


def main() -> int:
    failures = 0
    for name, exp, expected in CASES:
        valid, problems = validate_experience(exp)
        ok = valid == expected
        if not ok:
            failures += 1
        print(f"[{'PASS' if ok else 'FAIL'}] {name} "
              f"(valid={valid}, expected={expected})"
              f"{f' problems={problems}' if problems else ''}")
    print(f"OVERALL: {'PASS' if failures == 0 else f'{failures} FAILURES'}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

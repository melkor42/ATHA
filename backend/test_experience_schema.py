"""backend/test_experience_schema.py — offline contract for /api/experience.

Reuses validate_experience from eval_loop.py and pins the schema rules it
encodes (1..10 sections, hydrated entity_ids, title <= 80, text <= 500) with
synthetic payloads. Pure function, instant, credential-free — no live backend.

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
            {"component": "text_block", "title": "Welcome", "text": "Hello.",
             "entity_ids": []},
            {"component": "signal_card", "title": "People", "text": "Grounded.",
             "entity_ids": ["p1"]},
        ],
        "entities": {"p1": {"type": "person", "name": "Ada"}},
    }
    exp.update(overrides)
    return exp


# (name, experience, expected_valid)
CASES = [
    ("valid experience passes", _experience(), True),
    ("default degradation shape passes", _experience(
        sections=[{"component": "text_block", "title": "Welcome to SIGNAL",
                   "text": "The network is composing your personal page.",
                   "entity_ids": []}],
        entities={}), True),
    ("six sections valid", _experience(
        sections=[{"component": "text_block", "title": f"S{i}",
                   "text": "x", "entity_ids": []} for i in range(6)]), True),
    ("seven sections valid", _experience(
        sections=[{"component": "text_block", "title": f"S{i}",
                   "text": "x", "entity_ids": []} for i in range(7)]), True),
    ("ten sections is the ceiling", _experience(
        sections=[{"component": "text_block", "title": f"S{i}",
                   "text": "x", "entity_ids": []} for i in range(10)]), True),
    ("eleven sections rejected", _experience(
        sections=[{"component": "text_block", "title": f"S{i}",
                   "text": "x", "entity_ids": []} for i in range(11)]), False),
    ("zero sections rejected", _experience(sections=[]), False),
    ("missing sections key rejected", {"entities": {}}, False),
    ("empty payload rejected", {}, False),
    ("unhydrated entity_id rejected", _experience(
        sections=[{"component": "signal_card", "title": "People",
                   "text": "Grounded.", "entity_ids": ["p1", "ghost"]}]), False),
    ("title over 80 chars rejected", _experience(
        sections=[{"component": "text_block", "title": "t" * 81,
                   "text": "x", "entity_ids": []}], entities={}), False),
    ("text over 500 chars rejected", _experience(
        sections=[{"component": "text_block", "title": "T",
                   "text": "x" * 501, "entity_ids": []}], entities={}), False),
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

# Planning Artifacts and Provenance

<cite>
**Referenced Files**
- [docs/ARTIFACTS.md](file://docs/ARTIFACTS.md)
- [docs/architecture-sketch.png](file://docs/architecture-sketch.png)
- [docs/system.html](file://docs/system.html)
- [.scratch/wow-mvp/legacy-task-csv.md](file://.scratch/wow-mvp/legacy-task-csv.md)
- [prototypes/brand-theater.html](file://prototypes/brand-theater.html)
</cite>

This page indexes where each planning artifact lives and what it decided. The human-readable narrative with full provenance is `docs/ARTIFACTS.md`; artifacts are canonical in their folders and duplicated nowhere.

## The artifact chain, in order

1. **Vision** — `IDEA.md`: what SIGNAL is and why the Wow Page exists; the no-filler, no-hallucination promise.
2. **Architecture sketch** — `docs/architecture-sketch.png`: the whiteboard (Vue frontend, FastAPI orchestrator with two agents, Neo4j Aura graph+vector, OpenRouter, offline ingest; blue = online path, orange = offline). Marginal notes became requirements: verify() whitelist, no v-html, JSON contract with client-side design freedom.
3. **System reference** — `docs/system.html`: interactive sketch with reference code for every module and the glossary. Pre-grilling; where it conflicts with later decisions, the later decisions win (see *Architecture Overview and Decisions*).
4. **Task CSV** — `.scratch/wow-mvp/legacy-task-csv.md`: the pre-grilling execution checklist, absorbed into the wayfinder map; stale items overridden, backlog rows confirmed out of scope.
5. **Wayfinder map** — `.scratch/wow-mvp/map.md`: destination, standing decisions, resolved-ticket index, fog, out-of-scope. The record of why.
6. **Brand prototype** — `prototypes/brand-theater.html`: the throwaway that locked brand tokens and the staged-reveal theater, and first proved visible per-persona difference.
7. **Acceptance fixtures** — `personas/`: Miriam, Jonas, David, Tobias; input + Agent-1 contract + Agent-2 eval note each.
8. **Acceptance evidence** — `acceptance/`: the four pages composed by the live pipeline on 2026-08-13.

## How to use this page

When a decision seems unmotivated, walk the chain backwards from the map to the artifact that originated it. When adding a new artifact, register it here and in `docs/ARTIFACTS.md` — one source of truth, two registers.

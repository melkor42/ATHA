# Planning Artifacts — the story of how this build was decided

A curated gallery for humans. Every artifact lives canonically in the folder linked here; this page narrates them in order and duplicates nothing. The agent-facing wiki references the same files.

## 1. The vision — [`IDEA.md`](../IDEA.md)

What ATHA is (a 48-hour AI-native viability environment) and why the composed page exists: a personal front door composed for one person, grounded in their actual profile, building itself in front of them. The promise every later decision serves: *the platform understands you before asking anything of you.*

## 2. The architecture sketch — [`docs/architecture-sketch.png`](architecture-sketch.png)

The whiteboard that started the build: Vue + Vite frontend with Component Registry and recursive UiRenderer; FastAPI orchestrator holding Agent 1 (Persona Modeler) and Agent 2 (Experience Builder); Neo4j Aura as graph + vector database; OpenRouter for chat; the offline ingest pipeline. Blue arrows = online query path, orange = offline ingest path. Marginal notes became requirements: verify() against a retrieval whitelist, no v-html, client-side design freedom over a structured JSON contract.

## 3. The system reference — [`docs/system.html`](system.html)

The interactive version of the sketch: clickable architecture boxes, the online/offline path animations, reference code for every module (llm, ui_schema, agents, retrieval, ingest, main, UiRenderer, neo4j.cypher), and the glossary. Written before the grilling rounds; where it conflicts with later decisions, the later decisions win (see the map).

## 4. The task CSV — [`.scratch/wow-mvp/legacy-task-csv.md`](../.scratch/wow-mvp/legacy-task-csv.md)

The pre-grilling execution checklist (M0–M5 milestones). Absorbed into the wayfinder map: its finer slices folded into build tickets, its stale items (1536-dim embeddings, six components, 10-second gate, German) overridden by settled decisions, its backlog rows confirmed as out of scope. Kept for provenance.

## 5. The wayfinder map — [`.scratch/wow-mvp/map.md`](../.scratch/wow-mvp/map.md)

The canonical tracker: destination (the Aug 24 demo), standing decisions as Notes, resolved tickets as an index, fog and out-of-scope. The record of *why*, not just *what*.

## 6. The brand prototype — [`prototypes/brand-theater.html`](../prototypes/brand-theater.html)

The throwaway that locked the look: warm charcoal, cream Inter, pill CTAs, the gold→rust→violet→blue gradient, and the staged-reveal theater — plus the first four persona pages that proved visible difference before any backend existed.

## 7. The acceptance fixtures — [`personas/`](../personas/)

Miriam, Jonas, David, Tobias: the four people the MVP is judged by. Each file carries the input (example prompt), the Agent-1 contract (expected PersonaModel), and the Agent-2 eval note.

## 8. The acceptance evidence — [`acceptance/`](../acceptance/)

The four pages composed by the live pipeline on 2026-08-13 — boardroom, festival, garden, ledger. They prove the grammar worked, but they render the **retired theme system**: the Theme enum has since been superseded by the Spectrum × StyleMode axis grammar, so these screenshots are historical. New acceptance baselines under the axis grammar are to be re-captured manually.

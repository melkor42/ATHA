# Living State (dated)

> This is the only wiki page allowed to go stale. It is a dated snapshot; every other page is timeless. Updated only when the user prompts.

## Snapshot — 2026-08-13

- MVP built end to end; the four-persona acceptance run passed 4/4 (boardroom / festival / garden / ledger all visibly distinct, all entities grounded). Evidence in `acceptance/`.
- Repo pushed to https://github.com/melkor42/Signal (commits: initial setup, docs layer).
- Wiki authored into the Signal workspace store; knowledge-card atlas build pending.
- Ticket *Run the four-persona acceptance* (.scratch/wow-mvp/issues/12) remains OPEN pending the user's final acceptance.

## Open iteration queue

1. Miriam — show numeric match scores on SignalCards (fixture asks "ranked by match score").
2. David — deliver two or three mentorship stories; currently one.
3. Tobias — add a connections-per-sector view and a filterable enterprise list.
4. Jonas — "entrepreneurship" is implied, not named, in his persona output (minor).

## Models and quotas

Chat: `nvidia/nemotron-3-super-120b-a12b:free` (fallback `openai/gpt-oss-20b:free`). Embeddings: local fastembed `BAAI/bge-small-en-v1.5`, 384 dims. Account is free-models-only with $10 credits; free quotas can 429 after heavy iteration — the backend backs off 15s per attempt before degrading.

## Housekeeping

- `gh auth login` completed by the user on 2026-08-13 (push done).
- The redundant Neo4j credentials file in the user's Downloads is still on disk; user to delete when convenient.
- Aura instance last confirmed awake 2026-08-13; it auto-pauses after three idle days.

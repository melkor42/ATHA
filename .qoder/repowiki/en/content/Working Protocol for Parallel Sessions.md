# Working Protocol for Parallel Sessions

<cite>
**Referenced Files**
- [AGENTS.md](file://AGENTS.md)
- [docs/agents/issue-tracker.md](file://docs/agents/issue-tracker.md)
- [.scratch/wow-mvp/map.md](file://.scratch/wow-mvp/map.md)
</cite>

## The tracker

Issues live as local markdown under `.scratch/wow-mvp/`: the map (`map.md`) is the canonical artifact; tickets are `issues/NN-<slug>.md` with `Type:` (research/prototype/grilling/task), `Status:` (open/claimed/resolved), and `Blocked by:` lines. Protocol: claim a ticket (set Status: claimed) before any work; a ticket is unblocked when everything it lists is resolved; resolve by appending an `## Answer` and adding a one-line gist to the map's Decisions-so-far; never resolve more than one non-research ticket per session. The map is an index, not a store — decisions live in their ticket.

## Orchestration model

Builds run as fresh-context subagents (GeneralPurpose) dispatched per ticket, each with a self-contained brief pointing at repo files (map Notes, the ticket, CONTEXT.md, research/, prototypes/). The orchestrating conversation reviews every diff before acceptance and keeps the human-in-the-loop checkpoints (grammar, prototype, acceptance). Qoder's Experts mode is deliberately deferred to a post-demo experiment on a self-contained backlog item: it would re-derive context per request and does not follow the claim/resolve protocol, risking tracker trample.

## File-write pattern for sandboxed agents

Write tools are restricted to the chat workspace; the repo lives outside it. The established pattern: stage files in the workspace (`signal-staging/`), then copy into the repo with a single permitted shell command. Treat the repo as the source of truth after the copy; refresh stale staging copies from the repo before editing.

## Git identity and secrets

Commits reuse the original author identity via one-off flags: `git -c user.name='melkor42' -c user.email='melkor42@users.noreply.github.com' commit ...` — never mutate global or repo git config. `.env` (Neo4j + OpenRouter credentials) is gitignored and never committed; `.env.example` documents the shape. Runtime artifacts (`trace.jsonl`, caches, `node_modules`) are gitignored.

## Reading order for a fresh session

README → this page → map Notes → CONTEXT.md → the ticket being claimed. The wiki articles mirror the same knowledge at project level; `docs/ARTIFACTS.md` narrates the planning history for humans.

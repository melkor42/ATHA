# AGENTS.md

## Agent skills

### Issue tracker

Local markdown under `.scratch/` — the canonical tracker. A GitHub repo exists at https://github.com/melkor42/Signal for code sharing; `gh auth login` is complete (authenticated as melkor42), so the remaining external step is the repo rename/migration itself. See `docs/agents/issue-tracker.md`.

Note: the project rebranded Signal → Atha; the GitHub repo rename is pending (external task), so the remote URL still reads `melkor42/Signal`.

### Domain docs

Single-context: `CONTEXT.md` + `docs/adr/` at the repo root, created lazily as terms and decisions get resolved. See `docs/agents/domain.md`.

## Setup, run, verification

Setup and local run instructions live in `README.md`. Credential-free fixture mode (no backend, no LLM): `http://localhost:5173/?fixture=miriam|jonas|david|tobias`. Verification gate: `python backend/eval_loop.py` against the running backend — exit 0 = all three roles valid.

### Pre-commit checks

- Changes to `backend/main.py`, `backend/agents.py`, or `frontend/src/composables/useCompose.js`: start the backend, then run `python backend/eval_loop.py` before committing.
- Frontend changes: open fixture mode (`?fixture=miriam`) once before committing.
- Instant offline schema contract (no backend, no credentials): `python backend/test_experience_schema.py`.

# AGENTS.md

## Agent skills

### Issue tracker

Local markdown under `.scratch/` — the canonical tracker. A GitHub repo exists at https://github.com/melkor42/Signal for code sharing; `gh auth login` is complete (authenticated as melkor42), so the remaining external step is the repo rename/migration itself. See `docs/agents/issue-tracker.md`.

Note: the project rebranded Signal → Atha; the GitHub repo rename is pending (external task), so the remote URL still reads `melkor42/Signal`.

### Domain docs

Single-context: `CONTEXT.md` + `docs/adr/` at the repo root, created lazily as terms and decisions get resolved. See `docs/agents/domain.md`.

## Setup, run, verification

Setup and local run instructions live in `README.md`. Credential-free fixture mode (no backend, no LLM): `http://localhost:5173/?fixture=student|warwick|business`. Verification gate: `python backend/eval_loop.py` against the running backend — exit 0 = all three roles valid.

## Deployment topology (since 2026-09-02)

Two branches, two hosts — a push to `main` no longer deploys anything visible on its own.

- **`town-square`** = frozen state, served by **Render** (`https://atha-hadora.onrender.com`). Render's production branch is set to `town-square`, so pushes to `main` do not reach it.
- **`main`** = the line that moves forward, served by the **Oracle Always-Free VM** (`http://129.159.24.78`). There is no CI: deploy with `./.scratch/deploy-vm.sh` (gitignored tooling), which builds the SPA locally and ships tarballs — the box has no package manager, no Node and no git. The script refuses a dirty tree or a non-`main` checkout unless `FORCE_BRANCH=1`.
- Never Stop/Start the OCI instance (ephemeral public IP); **Restart** only. The host's recurring outage was `dnf makecache` OOM-killing itself roughly every 2 h — `dnf-makecache.timer` and PackageKit are masked; leave them masked.

### Pre-commit checks

- Changes to `backend/main.py`, `backend/agents.py`, `backend/skeleton.py`, `backend/knowledge.py`, or `frontend/src/composables/useCompose.js`: start the backend, then run `python backend/eval_loop.py` before committing.
- Frontend changes: open fixture mode (`?fixture=student`) once before committing.
- Instant offline schema contract (no backend, no credentials): `python backend/test_experience_schema.py`.
- Knowledge graph changes (`data/knowledge/*`, `backend/ingest_knowledge.py`): `python backend/test_knowledge_ingest.py` (offline contract), and after ingest `python backend/test_knowledge_retrieval.py` (live skeleton/retrieval gate).
- Against a running host, `eval_loop.py --url <host>` twice in a row reports **cache-hit** latency (20–50 ms): `backend/main.py` caches responses by role+state+intent+facet+free_text+style. To measure a real compose, send a request with a unique `topics` value.

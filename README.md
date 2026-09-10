# ATHA 

The personal front door to ATHA: after a few words about yourself, you receive a page composed only for you — grounded in the network graph, visibly different for every persona. See `IDEA.md` for the vision.

## Documentation

- `IDEA.md` — vision and promise
- `docs/system.html` — architecture sketch with reference code (open in a browser)
- `.scratch/wow-mvp/map.md` — the wayfinder map: destination, decisions, tickets, frontier

## Layout

- `backend/` — FastAPI orchestrator + two LLM agents (free tier via OpenRouter, local embeddings)
- `frontend/` — Vue + Vite, Component Registry, recursive UiRenderer (no `v-html`)
- `data/` — synthetic dataset (generated, fictional)
- `prompts/` — agent system prompts, loaded at startup
- `personas/` — the four acceptance fixtures (input + expected Agent-1 output + eval notes)

## Setup

1. Copy `.env.example` to `.env` and fill in the values (Neo4j Aura + OpenRouter — see the map's Notes for the provisioned infrastructure). The real `.env` is gitignored; never commit it.
2. Backend deps: `cd backend; pip install -r requirements.txt`
3. Frontend deps: `cd frontend; npm install`

## Run locally

One-time data load (idempotent, safe to re-run): `cd backend; python generate_data.py; python ingest.py`

- Backend: `cd backend; python -m uvicorn main:app --host 127.0.0.1 --port 8000`
- Frontend: `cd frontend; npm run dev` → http://localhost:5173

Type one sentence about yourself and the page composes itself. Mock mode without the backend: `http://localhost:5173/?fixture=student|warwick|business`.

Repeats are cached server-side — the same input costs no LLM call. Fresh compositions call OpenRouter free models; when the free quota is exhausted the backend retries with backoff and finally degrades to the welcome page (never crashes).

## Verification

- Live gate: with the backend running, `cd backend; python eval_loop.py` — exit 0 = all three roles valid.
- Offline contract (instant, no backend, no credentials): `python backend/test_experience_schema.py`.
- Pre-commit habit: after changes to `backend/main.py`, `backend/agents.py`, or `frontend/src/composables/useCompose.js`, run the live gate; after frontend changes, open fixture mode once.

## Status

Tracked on the wayfinder map. Demo target: 2026-08-24, Warwick Business School.

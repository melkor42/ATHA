# Acceptance and Demo Ops

<cite>
**Referenced Files**
- [README.md](file://README.md)
- [personas/](file://personas)
- [acceptance/](file://acceptance)
- [backend/trace.jsonl](file://backend/trace.jsonl)
</cite>

## Running locally

One-time data load: `cd backend; python generate_data.py; python ingest.py`. Backend: `python -m uvicorn main:app --host 127.0.0.1 --port 8000`. Frontend: `cd frontend; npm run dev` → http://localhost:5173. Mock mode without backend: `?fixture=miriam|jonas|david|tobias`.

## The acceptance method

The four fixtures in `personas/` are the acceptance set. Each file carries three instruments: the example prompt (the onboarding input), the expected PersonaModel JSON (Agent 1's eval target), and a per-persona eval note for Agent 2 (e.g. "capture energy without mistaking him for shallow", "ranking vs methodology"). Acceptance passes when all four prompts compose live, Agent 1's outputs match the expected models, every displayed entity is whitelist-grounded, and the four pages are visibly distinct in theme, layout, and register. Evidence screenshots live in `acceptance/`.

## Designed degradations

The system is built to fail honestly: ungroundable input (e.g. "i like yellow") returns the calm welcome page rather than invented content; OpenRouter 429s trigger 15s backoff retries under the theater before degrading; a dead or paused Neo4j Aura degrades in ~10s thanks to driver timeouts; any pipeline exception returns DEFAULT_EXPERIENCE. Repeats are served from the answers-hash cache at zero LLM cost, so rehearsals are free.

## Demo script

Two prepared contrasting inputs typed live; one rehearsed degradation run so the fallback is a demonstrated feature; the Dean may get the keyboard only after the first run. The demo gates on "composes live", not on latency.

## Operational footguns

Aura free auto-pauses after three idle days (resume in the Neo4j console; the backend then degrades gracefully until woken). Free-model quotas can 429 after heavy iteration — budget fresh live runs, lean on cached repeats. Trace records for every request are in `backend/trace.jsonl`.

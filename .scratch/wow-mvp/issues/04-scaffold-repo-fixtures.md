# Scaffold repo and fixtures

Type: task
Status: resolved
Blocked by: —

## Question

Manual/AFK work unblocking the build: create `.env` from the user's Neo4j credentials file (NEO4J_URI/USERNAME/PASSWORD/DATABASE) plus `.gitignore` covering `.env`; copy the four persona fixtures from the user's Downloads into `personas/` under their readable names (miriam-stahl.md, jonas-neumann.md, david-bergmann.md, tobias-winter.md); create `backend/` and `frontend/` layout; connect the GitHub remote (https://github.com/melkor42/Signal) and push once auth allows. Resolved when the tree builds nothing but holds everything the build tickets need.

## Answer

Scaffold complete: `personas/` holds the four fixtures under readable names; `backend/`, `frontend/`, `data/`, `prompts/` created (seed English prompts for both agents, perspective axis included); `.env.example`, `README.md`, and `docs/system.html` (archived architecture sketch) in place; `.env` + `.gitignore` were done under ticket 01. Legacy task CSV absorbed: its finer layout (data/, prompts/, .env.example, README) adopted here; tracing/logging and response caching folded into [Build the backend orchestrator](10-backend-orchestrator.md). GitHub push pending `gh auth login` — tracked under ticket 01's side note.

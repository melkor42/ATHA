# Provision OpenRouter access

Type: task
Status: resolved
Blocked by: —

## Question

The user supplies an OpenRouter API key (account + credits). Work: receive the key, write it to `OneDrive\Signal\.env` as `OPENROUTER_API_KEY` (file gitignored), and verify with one minimal embeddings call. HITL — the key comes from the user; never store it anywhere else.

Side note: `gh auth login` for the GitHub remote is the same kind of user action; fold its completion into this ticket's answer if it happens first.

## Answer

`.env` written to the repo (NEO4J_URI/USERNAME/PASSWORD/DATABASE + OPENROUTER_API_KEY) and `.gitignore` added covering it. Key verified via `GET /api/v1/key`: free tier, zero usage, no expiry. The account is restricted to free models only by user setting — MVP model selection therefore moves to [Choose free-tier OpenRouter model pair](13-free-model-pair.md); the paid picks in ticket 02 stay as the post-demo upgrade path. `gh auth login` still pending; fold in here when it happens.

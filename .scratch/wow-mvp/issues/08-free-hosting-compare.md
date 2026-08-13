# Compare free hosting options

Type: research
Status: resolved
Blocked by: —

## Question

Post-demo free-tier hosting for a Vue+Vite static frontend and a FastAPI backend whose single endpoint can take 10–60s (two LLM calls + Neo4j). Compare Vercel, Render, HuggingFace Spaces, Fly.io, Cloudflare: function timeout ceilings on free tiers (the sharp constraint), cold starts, whether SSE would survive later, and how Neo4j Aura + OpenRouter behave from serverless egress. Recommend one combo for a public demo after Aug 24.

## Answer

Vercel Hobby (Vue frontend) + Render free web service (FastAPI; 100-min request ceiling so the 60s POST survives, no credit card, 15-min idle sleep — handle with a pinger). Ruled out: HF Spaces (Docker now paid, bolt port blocked), Fly.io (card required), Cloudflare (can't run FastAPI/bolt). Decision on deploying stays post-demo per map Notes. Full comparison: [research/08-free-hosting-compare.md](../research/08-free-hosting-compare.md).

# Research 08 — Free-tier hosting: Vue+Vite frontend + FastAPI backend (one slow POST, 10–60 s)

Researched August 2026 against primary vendor docs (fetched 2026-08-12).
Sharp constraint: a single POST that takes 10–60 s (two LLM API calls + one Neo4j query) must survive the host's request-timeout ceiling.

## Recommendation

**Frontend: Vercel (Hobby) — Backend: Render (Free web service).**

- Render free web services have a **100-minute HTTP request timeout** (per Render's own docs/articles), so a 60 s POST survives with huge headroom; it's a real container running FastAPI/uvicorn, with outbound TCP allowed on all ports except SMTP (25/465/587), so Neo4j Aura `bolt+s` on port 7687 and OpenRouter (443) both work. No credit card required — no payment method needed to use free instance hours (Render instead suspends services only if monthly included bandwidth/pipeline minutes are exceeded).
- Vercel Hobby hosts the Vue+Vite static build for free (no card). (Vercel *could* also run the FastAPI function — Hobby's fluid-compute max duration is 300 s — but keeping the backend in a Render container avoids Vercel Python-runtime packaging quirks with the `neo4j` driver.)
- Mitigation: Render free instances **sleep after 15 min idle** and take **~1 minute to spin up** — add a free uptime pinger or have the frontend show a "waking up" state.
- Rejected: HuggingFace Spaces (Docker/Gradio Spaces now require a **paid PRO plan to create**, and Spaces block outbound ports other than 80/443/8080 — Neo4j Aura's 7687 would be blocked anyway); Fly.io (no free tier for new orgs — all orgs require a credit card on file); Cloudflare Workers (can't run FastAPI — no Python server runtime, and bolt/TCP to Neo4j requires raw sockets; note its HTTP wall time is technically unlimited, CPU 10 ms free).

## Comparison table

| Host (free tier) | Timeout ceiling for a request | Cold start / idle sleep | SSE on free tier | Card required | Neo4j Aura (bolt+TLS :7687) & OpenRouter (:443) |
|---|---|---|---|---|---|
| **Render** — Free web service (512 MB / 0.1 CPU) | **100 minutes** (web service request timeout) | Sleeps after **15 min** idle; spin-up **~1 min** | Yes (long-lived HTTP/WebSocket supported) | **No** (free hours work without payment method) | Yes — outbound only SMTP ports blocked; 7687 & 443 fine |
| **Vercel** — Hobby Functions (Python/Node) | **300 s** (5 min) default & max on Hobby with fluid compute | No sleep; scale-to-zero cold starts are seconds, not minutes | Yes (streaming responses; Edge runtime must start responding within 25 s) | No (Hobby is free) | Yes (runs on AWS Lambda; outbound TCP OK) |
| **HuggingFace Spaces** — CPU Basic (2 vCPU, 16 GB, free) | No per-request timeout on the app itself | Space **sleeps when unused** on free hardware | Yes | No | **Blocked for bolt** — Spaces only allow outbound ports 80/443/8080; also **Docker/Gradio Spaces require a paid plan to create** (only Static Spaces are free; free personal accounts may host ≤2 ZeroGPU Gradio Spaces) |
| **Fly.io** — Machines | No practical ceiling (per-request; default kill/grace far above 60 s) | Machines can auto-stop/start; starts in seconds | Yes | **Yes — all organizations require a credit card on file; free allowances discontinued for new customers** | Yes (any port) |
| **Cloudflare** — Workers Free / Pages | HTTP wall time **unlimited** while client connected — but **CPU time 10 ms/request** on Free plan (I/O wait not counted) | Effectively none (edge isolates, sub-ms) | Yes (streaming/WebSocket) | No | **No bolt** — no FastAPI runtime; raw TCP sockets limited (Cloudflare Sockets), so `neo4j+s://` not viable. Pages works fine for the static frontend |

## Sources

- Vercel Functions limits (Hobby max duration 300 s with fluid compute; streaming; free functions on Hobby): https://vercel.com/docs/functions/limitations (fetched 2026-08-12, page last updated 2026-07-01)
- Render free tier (15 min idle spin-down, ~1 min spin-up, 750 free instance hours/month, no payment method required to use free tier, outbound blocked only on SMTP ports 25/465/587): https://render.com/docs/free
- Render web services (FastAPI support, port binding, WebSocket): https://render.com/docs/web-services
- Render on 100-minute web-service request timeout: https://render.com/articles/best-cloud-platform-to-run-agents and https://render.com/articles/deploy-streamlit-gradio-localhost-to-live ; plan-level comparison table: https://render.com/docs/render-vs-vercel-comparison
- HuggingFace Spaces overview (CPU Basic free hardware; **paid plan required to create Gradio/Docker Spaces**; outbound limited to ports 80/443/8080; free-hardware Spaces sleep when unused): https://huggingface.co/docs/hub/spaces-overview
- Fly.io pricing (all organizations require a credit card on file; legacy free allowances only for pre-existing plans; no free tier for new customers): https://fly.io/docs/about/pricing/
- Cloudflare Workers limits (Free: 10 ms CPU/request, 100k requests/day; HTTP invocation wall time unlimited while client connected; runtime-update 30 s grace): https://developers.cloudflare.com/workers/platform/limits/ (updated 2026-07-28)

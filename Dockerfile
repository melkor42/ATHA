# Single-service packaging: FastAPI serves the API and the built Vue SPA
# from one origin (no CORS). Deploy target: Koyeb free (512 MB, fra) or any
# Docker-capable host.

# --- stage 1: frontend build ---------------------------------------------------
FROM node:22-alpine AS web
WORKDIR /web
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
ENV VITE_API_URL=/api/experience
RUN npm run build

# --- stage 2: backend + static ---------------------------------------------------
FROM python:3.11-slim
WORKDIR /app
# onnxruntime (via fastembed) needs libgomp at import time — not in slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends libgomp1 \
 && rm -rf /var/lib/apt/lists/*
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./
# agents.py and skeleton.py resolve ../prompts and ../data/knowledge from the
# repo root, so the image mirrors that layout: /app (backend) + /prompts + /data
COPY prompts/ /prompts
COPY data/knowledge/ /data/knowledge
COPY --from=web /web/dist ./static
# bake the embedding model into the image so cold starts don't download it
RUN python -c "from fastembed import TextEmbedding; TextEmbedding(model_name='BAAI/bge-small-en-v1.5')"
EXPOSE 8000
# Koyeb injects PORT; default stays 8000 for local runs
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

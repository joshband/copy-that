# Environment Variables

**Canonical source:** [`.env.example`](../../.env.example) — copy to `.env` and edit. This page is a short index only; do not treat it as more authoritative than `.env.example`.

```bash
cp .env.example .env
```

---

## Required for local MVP

| Variable | Purpose | Example / default |
|----------|---------|-------------------|
| `SECRET_KEY` | JWT / session signing | override in every env |
| `DATABASE_URL` | Async SQLAlchemy URL | `postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/copy_that` |
| `ANTHROPIC_API_KEY` | Claude extractors (colors, etc.) | `sk-ant-…` |

SQLite smoke (no Docker): uncomment sqlite URL in `.env.example`, then `make db-bootstrap-sqlite`.

---

## API / runtime

| Variable | Default | Notes |
|----------|---------|-------|
| `ENVIRONMENT` | `local` | `local` \| `staging` \| `production` |
| `API_HOST` | `0.0.0.0` | bind address |
| `API_PORT` | `8000` | uvicorn port |
| `API_RELOAD` | `true` | disable in production |
| `LOG_LEVEL` | `INFO` | |

---

## Storage & AI backends

| Variable | Default | Notes |
|----------|---------|-------|
| `STORAGE_BACKEND` | `local` | `local` \| `gcs` |
| `LOCAL_STORAGE_PATH` | `./storage` | |
| `GCS_BUCKET` / `GCS_PROJECT_ID` | see `.env.example` | when `STORAGE_BACKEND=gcs` |
| `VISION_BACKEND` | `gcp` | |
| `ML_BACKEND` | `vertex` | |
| `OPENAI_API_KEY` | empty | color helpers; cloud DALL·E for mood board |
| `GCP_VISION_ENABLED` | `true` | |
| `VERTEX_AI_*` | see `.env.example` | optional Vertex |

---

## Redis / Celery

| Variable | Default | Notes |
|----------|---------|-------|
| `REDIS_URL` | `redis://localhost:6379/0` | cache / rate limit |
| `CELERY_BROKER_URL` | `redis://localhost:6379/1` | jobs (mood board, etc.) |
| `CELERY_RESULT_BACKEND` | `redis://localhost:6379/2` | |
| `CELERY_MOOD_BOARD_QUEUE` | `mood-board` | optional override |

---

## Mood board (parked P4)

Set only when exercising local/cloud mood board. Full runbook: [MOOD_BOARD_SPECIFICATION.md](../features/MOOD_BOARD_SPECIFICATION.md).

| Variable | Role |
|----------|------|
| `MOOD_BOARD_TEXT_BASE_URL` | LM Studio / OpenAI-compatible chat (else Anthropic) |
| `MOOD_BOARD_TEXT_API_KEY` / `MOOD_BOARD_TEXT_MODEL` | text provider |
| `MOOD_BOARD_IMAGE_BASE_URL` | local mflux shim (`scripts/mood_board_local_image_server.py`) |
| `MOOD_BOARD_IMAGE_*` | image size/model/key |
| `MOOD_BOARD_LOCAL_IMAGE_MODEL` | default `dhairyashil/FLUX.1-schnell-mflux-4bit` |
| `MOOD_BOARD_LOCAL_IMAGE_BASE_MODEL` | `schnell` |
| `HF_TOKEN` | optional Hub auth |

---

## Auth, SaaS, monitoring (optional)

`ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS`, OAuth client ids, `SENTRY_*`, `PROMETHEUS_ENABLED`, `OTEL_*`, rate limits, tenancy, Stripe — all documented with defaults in `.env.example`.

---

## Health

```bash
curl http://localhost:8000/health
```

OpenAPI UI: http://localhost:8000/docs

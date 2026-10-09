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
| `ENVIRONMENT` | `local` | `local` \| `staging` \| `production`; non-local requires Postgres + Redis/Celery URLs (`infrastructure/config.py`) |
| `ENABLE_PARKED_ROUTERS` | in code | Optional `true` / `false` override for sessions, batch, and multi-extract routes; deployment defaults and mounting live in `interfaces/api/app_factory.py`. Jobs stays mounted for Mood polling. |
| `OPENAI_API_KEY` | empty | OpenAI color/spacing helpers; cloud DALL·E for mood board |
| `EXTRACTION_MAX_CONCURRENCY` / `EXTRACTION_MAX_IMAGE_BYTES` / `MAX_IMAGE_BYTES` | in code | extract concurrency and upload size caps (`application/concurrency.py`, `interfaces/api/utils.py`, `interfaces/api/spacing.py`) |
| `COST_SOFT_LIMIT_USD` / `COST_HARD_LIMIT_USD` | in code | AI spend guard (`application/cost_tracker.py`) |
| `RATE_LIMIT_ENABLED` | in code | API rate limiter (`infrastructure/security/rate_limiter.py`) |

The API port is set on the `uvicorn` command line (`--port 8000`) or by Cloud Run's `PORT`.

Local Mood generation remains available without sign-in. Hosted environments
(staging and production) require an active user's bearer **access** token before
Mood generation can enqueue work; refresh tokens are rejected. Generation uses
the existing endpoint rate limiter, keyed by authenticated user on hosted requests.
Its limits live in `interfaces/api/mood_board.py`; storage is per API process,
so multiple workers do not share a quota. Health and job polling remain available.
The Mood health response advertises whether authentication is required. The UI
signs in through `/api/v1/auth/token` and verifies `/api/v1/auth/me`, then sends a
bearer access token on generation. Tokens stay in memory; login does not enqueue
work, and sign-out/expired-token recovery clears the session. UI navigation flags do not secure API routes.

### In `.env.example` but not read by the app

`API_HOST`, `API_PORT`, `API_RELOAD`, `VISION_BACKEND`, `ML_BACKEND`, `GCP_VISION_ENABLED`, `VERTEX_AI_*`, and `GCS_*` are not read anywhere under `src/`. `LOG_LEVEL`, `STORAGE_BACKEND`, and `LOCAL_STORAGE_PATH` are set only by `docker-compose.yml` / `deploy/terraform`. Setting them locally has no effect.

---

## Extraction / CV toggles (read in code, not in `.env.example`)

Defaults live in the reading module. These are local-experiment switches: the upload extract must not run geometry, FastSAM, UIED, Marigold, or depth models (`AGENTS.md` hard rule), so do not turn those on in shared or deployed environments.

| Variable | Read in |
|----------|---------|
| `ENABLE_GPU` | `application/gpu.py` — SegFormer / SAM / deep geometry when available |
| `ENABLE_SHADOWLAB` / `ENABLE_DARK_BLOB_SHADOW_CV` | `interfaces/api/shadows.py`, `extractors/shadow/cv_extractor.py` |
| `FASTSAM_ENABLED` / `FASTSAM_DEVICE` / `FASTSAM_MODEL_PATH` | `extractors/spacing/cv_extractor.py` |
| `ENABLE_UIED` / `UIED_RUNNER` | `extractors/cv_helpers/uied_integration.py` |
| `ENABLE_SPACING_DEPTH` / `ENABLE_LAYOUTPARSER_TEXT` / `DISABLE_TEXT_DETECTION` | `extractors/spacing/cv_extractor.py` |
| `ENABLE_DL_LAYOUT` (alias `ENABLE_LAYOUT_DETECTOR`) | `layoutlab/layout_detector.py` |
| `COPY_THAT_MULTI_EXTRACTOR` | `interfaces/api/spacing.py`, `typography.py` — orchestrator path |
| `DEPTH_ANYTHING_TRUST_REMOTE_CODE` / `GEOMETRY_NORMALS_SMOOTHING` | `extractors/geometry/` |
| `PERF_BUDGET_ENFORCE` | `application/perf.py` |

---

## AI model overrides

Model IDs and their defaults live only in
[`infrastructure/ai_models.py`](../../src/copy_that/infrastructure/ai_models.py); these vars override them
at call time. Changing a model changes cost and output.

| Variable | Overrides |
|----------|-----------|
| `CLAUDE_MODEL` | Claude color/typography extraction, qualitative metrics, mood-board copy |
| `CLAUDE_SHADOW_MODEL` | Claude AI shadow extraction |
| `OPENAI_MODEL` | every OpenAI vision call (color, spacing, mood-board design brief) |
| `OPENAI_IMAGE_MODEL` | DALL·E mood-board image backend |

---

## Redis / Celery

| Variable | Default | Notes |
|----------|---------|-------|
| `REDIS_URL` | `redis://localhost:6379/0` | cache / rate limit |
| `CELERY_BROKER_URL` | `redis://localhost:6379/1` | jobs (mood board, etc.) |
| `CELERY_RESULT_BACKEND` | `redis://localhost:6379/2` | |
| `CELERY_MOOD_BOARD_QUEUE` | `mood-board` | optional override |
| `CELERY_SOFT_TIME_LIMIT` / `CELERY_HARD_TIME_LIMIT` / `CELERY_*_QUEUE` | in code | `infrastructure/celery/app.py` |

---

## Mood board (P4 Mood tab)

Set when using the Mood tab (`make labs` starts the local stack). Full runbook: [MOOD_BOARD_SPECIFICATION.md](../features/MOOD_BOARD_SPECIFICATION.md).

| Variable | Role |
|----------|------|
| `MOOD_BOARD_TEXT_BASE_URL` | LM Studio / OpenAI-compatible chat (else Anthropic) |
| `MOOD_BOARD_TEXT_API_KEY` / `MOOD_BOARD_TEXT_MODEL` | text provider |
| `MOOD_BOARD_FLUX_BASE_URL` / `MOOD_BOARD_FLUX_API_KEY` / `MOOD_BOARD_FLUX_MODEL` | preferred cloud Flux — OpenAI-compat `…/v1` that implements `images.generate` (gateway required for native Fal/Replicate) |
| `FAL_KEY` / `REPLICATE_API_TOKEN` | optional key fallbacks when `MOOD_BOARD_FLUX_API_KEY` unset |
| `MOOD_BOARD_IMAGE_BASE_URL` | local mflux shim (localhost) or alternate OpenAI-compat |
| `MOOD_BOARD_IMAGE_*` | image size/model/key |
| `MOOD_BOARD_ROUTING_POLICY` | `balanced` (default) \| `fast` \| `cheap` \| `private` \| `quality` |
| `MOOD_BOARD_LOCAL_IMAGE_MODEL` / `MOOD_BOARD_LOCAL_IMAGE_BASE_MODEL` / `MOOD_BOARD_LOCAL_IMAGE_QUANTIZE` / `MOOD_BOARD_LOCAL_IMAGE_STEPS` | local mflux server (`scripts/mood_board_local_image_server.py` holds the defaults) |
| `MOOD_BOARD_LOCAL_IMAGE_BACKEND` | `mflux` or `mock` for the local image server |
| `FAL_FLUX_ENDPOINT` / `FAL_FLUX_STYLE_ENDPOINT` / `FAL_FLUX_STYLE_STRENGTH` / `FAL_NUM_INFERENCE_STEPS` | Fal shim (`scripts/mood_board_fal_openai_shim.py` holds the defaults) |
| `HF_TOKEN` | optional Hub auth |

---

## Auth, SaaS, monitoring (optional)

Read by the app: `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS` (`infrastructure/security/authentication.py`).

In `.env.example` but **not read** by the app: `ALGORITHM` (hard-coded HS256), OAuth client ids, `SENTRY_*`, `PROMETHEUS_ENABLED` (`/metrics` is always exposed), `OTEL_*`, `RATE_LIMIT_PER_MINUTE` / `RATE_LIMIT_PER_HOUR`, tenancy, Stripe / tier limits.

---

## Health

```bash
curl http://localhost:8000/health
```

OpenAPI UI: http://localhost:8000/docs

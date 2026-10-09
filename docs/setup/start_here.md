# Local setup — Start here

**Last Updated:** 2026-10-09

Copy That: screenshot → design tokens → W3C + CSS.
Nav: [DOCUMENTATION_INDEX.md](../../DOCUMENTATION_INDEX.md) · Architecture: [CURRENT_ARCHITECTURE_STATE.md](../architecture/CURRENT_ARCHITECTURE_STATE.md)

---

## Prerequisites

- Python 3.12+ and [uv](https://github.com/astral-sh/uv) (required — `make install` runs `uv sync --frozen`)
- Node 22.12+ / pnpm (version pinned by `packageManager` in `package.json`)
- Docker (local Postgres) optional but recommended
- API keys in `.env` (see `.env.example`) — never commit secrets

---

## Bootstrap

```bash
git clone https://github.com/joshband/copy-that.git
cd copy-that

make install          # uv sync (creates .venv) + pnpm install, both from lockfiles; pre-commit + pre-push hooks
cp .env.example .env  # edit SECRET_KEY, DATABASE_URL, ANTHROPIC_API_KEY
```

### Database

```bash
make db-bootstrap          # Docker Postgres + alembic upgrade head
# or without Docker:
# make db-bootstrap-sqlite
```

### Run

```bash
# Terminal 1 — API
PYTHONPATH=src .venv/bin/python -m uvicorn copy_that.interfaces.api.main:app --reload --port 8000

# Terminal 2 — UI (canonical: frontend/ → Vite)
pnpm dev   # http://127.0.0.1:5173
```

**Frontend ports:** use **`:5173`** (`pnpm dev`). Docker Compose also exposes a built frontend on **`:3000`** — that image is often stale; rebuild only if you intentionally want the container UI.

- OpenAPI: http://localhost:8000/docs
- Health: `curl http://localhost:8000/health`
- First extract: use the UI, or create a project then call extract with `project_id` — [api_curl.md](../examples/api_curl.md)

### Optional runtime dependencies

`uv sync --frozen` installs the core API. Google Cloud SDKs are in the `gcp` extra;
on-demand deep CV/geometry dependencies are in `cv-deep`:

```bash
uv sync --frozen --extra gcp       # Google Cloud integrations
uv sync --frozen --extra cv-deep   # local geometry/deep-CV experiments
```

Combine extras when needed. These commands synchronize the environment, so include
`--extra dev` when retaining development tools. `make install` includes the dependencies
needed for the full verification suite. The core OCR wrapper is retained; install
the external Tesseract binary for OCR (`brew install tesseract` on macOS).
Installing deep dependencies does not enable them on upload.

### Labs / mood board (optional)

One-shot local stack (Postgres/Redis + Fal Flux shim + API + Vite `:5173`):

```bash
# .env must include FAL_KEY + MOOD_BOARD_FLUX_BASE_URL=http://127.0.0.1:8766/v1
make labs                 # add WITH_CELERY=1 for imagery jobs
make labs-check           # port / key status
make mood-verify          # color hex + mood composition; Fal optional
```

Details: [../features/MOOD_BOARD_SPECIFICATION.md](../features/MOOD_BOARD_SPECIFICATION.md).

---

## Validate

```bash
make check            # mypy + ruff + format + tsc + eslint (~1 min)
make verify           # check + full Vitest + pytest tests/unit tests/integration (what CI gates)
make test-quick       # backend smoke
pnpm exec playwright install chromium   # once, before E2E
pnpm test:e2e:mvp     # Playwright MVP pack (mocked)
```

**Hooks:** pre-commit + pre-push hooks are installed by `make install`.
**Agent / contrib guide:** [AGENTS.md](../../AGENTS.md)
**Env:** [../configuration/ENVIRONMENT_VARIABLES.md](../configuration/ENVIRONMENT_VARIABLES.md) · `.env.example`

---

## Deploy?

[deployment_options.md](./deployment_options.md) · [gcp_cloud_run.md](./gcp_cloud_run.md)

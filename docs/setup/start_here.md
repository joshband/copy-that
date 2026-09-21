# Local setup — Start here

**Last Updated:** 2026-09-21

Copy That: screenshot → design tokens → W3C + CSS.  
Nav: [DOCUMENTATION_INDEX.md](../../DOCUMENTATION_INDEX.md) · Architecture: [CURRENT_ARCHITECTURE_STATE.md](../architecture/CURRENT_ARCHITECTURE_STATE.md)

---

## Prerequisites

- Python 3.12+, [uv](https://github.com/astral-sh/uv) recommended  
- Node 20+ / pnpm  
- Docker (local Postgres) optional but recommended  
- API keys in `.env` (see `.env.example`) — never commit secrets  

---

## Bootstrap

```bash
git clone https://github.com/joshband/copy-that.git
cd copy-that

python -m venv .venv && source .venv/bin/activate
make install          # or: uv pip install -e ".[dev]"

pnpm install
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
python -m uvicorn src.copy_that.interfaces.api.main:app --reload --port 8000

# Terminal 2 — UI (canonical: frontend/)
pnpm dev   # http://localhost:5173
```

- OpenAPI: http://localhost:8000/docs  
- Health: `curl http://localhost:8000/health`  
- First extract: use the UI, or create a project then call extract with `project_id` — [api_curl.md](../examples/api_curl.md)

---

## Validate

```bash
make check            # ruff / mypy / pnpm type-check
pnpm type-check
make test-quick       # backend smoke
pnpm test             # Vitest
pnpm test:e2e:mvp     # Playwright MVP pack
```

**Hooks:** `pre-commit install` and `pre-commit install --hook-type pre-push` (installed by `make install`).  
**Agent / contrib guide:** [../guides/AGENTS.md](../guides/AGENTS.md)  
**Env:** [../configuration/ENVIRONMENT_VARIABLES.md](../configuration/ENVIRONMENT_VARIABLES.md) · `.env.example`

---

## Deploy?

[deployment_options.md](./deployment_options.md) · [gcp_cloud_run.md](./gcp_cloud_run.md)

---

## Mood board (optional, parked)

Flag off by default. Local stack: LM Studio + mflux Hub mirror — [../features/MOOD_BOARD_SPECIFICATION.md](../features/MOOD_BOARD_SPECIFICATION.md).

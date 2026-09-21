# Repository Guidelines

## Project Structure & Module Organization

- `src/copy_that/` — FastAPI backend (interfaces/api, domain, services, generators, infrastructure); entrypoint `src/copy_that/interfaces/api/main.py`.
- **Canonical extraction / CV:** `src/copy_that/extractors/` (color, spacing, typography, shadow, geometry, DTCG helpers). Put new extractor work here.
- **Canonical shared deps:** `copy_that.core_tokens`, `copy_that.extractors.cv`, `copy_that.extractors.cv_helpers`. See [CURRENT_ARCHITECTURE_STATE.md](../architecture/CURRENT_ARCHITECTURE_STATE.md).
- `frontend/` — React + Vite (canonical; `pnpm --dir frontend`).
- Migrations: `alembic/` · deploy: `deploy/` / `terraform/` · docs nav: [DOCUMENTATION_INDEX.md](../../DOCUMENTATION_INDEX.md).

## Build, Test, and Development Commands

- Bootstrap: `python -m venv .venv && source .venv/bin/activate`, then `make install` (or `uv pip install -e ".[dev]"`).
- API: `python -m uvicorn src.copy_that.interfaces.api.main:app --reload --host 0.0.0.0 --port 8000`; DB: `make db-bootstrap` or `alembic upgrade head`.
- Frontend: `pnpm install`, `pnpm dev` (proxies `/api` → `:8000`), `pnpm build`, `pnpm type-check`.
- Containers: `make docker-build`, `docker compose up -d`.

## Daily quality gates (catch CI early)

| When | Command |
|------|---------|
| Before commit | `make check` (mypy + ruff + `pnpm type-check`) |
| Quick smoke | `make test-quick` · `pnpm test` |
| Optional script | `./scripts/validate.sh` if present (ruff + mypy + fast unit) |
| Hooks | `pre-commit install` · `pre-commit install --hook-type pre-push` |

**Hooks (typical):** commit → ruff/format/gitleaks; pre-push → mypy + fast unit tests. Prefer fixing locally over `--no-verify`.

**IDE:** select `.venv/bin/python`; Ruff + Python extensions give instant lint/type feedback.

## Coding Style & Naming

- Python: Ruff (`make lint` / `make format`), 4-space, 100-col, MyPy (`make type-check` / `mypy src/`). snake_case modules/functions, PascalCase classes, typed public APIs.
- Frontend: TypeScript + React; PascalCase components, `use*` hooks, typed props/contracts.

## Testing Guidelines

- Backend: `make test-fast` / `make test-unit` / `make test-int` / `make test-all`; coverage `make test-cov` or `make coverage`.
- Frontend: `pnpm test` (Vitest); `pnpm test:split` for phased CI-style runs; coverage `pnpm test:coverage`.
- E2E: `frontend/tests/playwright/` via `pnpm test:e2e` / `pnpm test:e2e:mvp`. Do not add specs under deprecated Playwright trees.

## Commit & Pull Request Guidelines

- Short imperative subjects, optional scope, one logical change.
- Before push: `make check` + relevant tests; include Alembic migrations when schema changes.
- PRs: what/why, linked issues, new env vars, screenshots for UI, validation commands noted.

## Security & Configuration

- Copy `.env.example` → `.env`; never commit secrets. Index: [ENVIRONMENT_VARIABLES.md](../configuration/ENVIRONMENT_VARIABLES.md).
- Schema: `alembic revision --autogenerate -m "<summary>"` then `alembic upgrade head`.

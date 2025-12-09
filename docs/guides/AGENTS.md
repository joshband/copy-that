# Repository Guidelines

## Project Structure & Module Organization
- `src/copy_that/` hosts the FastAPI backend (interfaces/api, domain, services, generators, infrastructure); entrypoint is `src/copy_that/interfaces/api/main.py`.
- Extraction pipelines live in `src/pipeline/`, `src/core/`, `src/cv_pipeline/`, `src/layout/`, and `src/typography/`; tests mirror these areas under `tests/<area>/`.
- `frontend/` is the React + Vite app served by the root Vite config (build output in `dist/`).
- Migrations are under `alembic/`; deployment and infra helpers live in `deploy/` and `terraform/`; docs sit in `docs/`; utility scripts in `scripts/`.

## Build, Test, and Development Commands
- Bootstrap: `python -m venv .venv && source .venv/bin/activate`, then `make install` (uv editable install + pre-commit) or `uv pip install -e ".[dev]"`.
- API: `python -m uvicorn src.copy_that.interfaces.api.main:app --reload --host 0.0.0.0 --port 8000`; database setup with `alembic upgrade head`.
- Frontend: `pnpm install` at repo root, `pnpm dev` for local dev (proxies `/api` to `http://localhost:8000`), `pnpm build` and `pnpm preview` to verify production output.
- Containers: `make docker-build` for dev image, `docker compose up -d` for services.

## Coding Style & Naming Conventions
- Python uses Ruff for lint/format (`make lint`, `make format`), 4-space indent, 100-char lines, strict typing via MyPy (`make type-check` or `mypy src/`). Use snake_case for modules/functions, PascalCase for classes, and keep public functions typed.
- Tests are `test_*.py`; shared fixtures live in `tests/fixtures/`.
- Frontend: TypeScript + React; components in `frontend/src/components` use PascalCase, hooks prefixed with `use*`, stores in `frontend/src/store`; type props and API contracts with interfaces/zod schemas.

## Testing Guidelines
- Backend tiers: quick `make test-fast`, fuller `make test-unit` and `make test-int`, exhaustive `make test-all`; coverage via `make test-cov` (HTML at `htmlcov/index.html`). Use markers like `-m "unit"` or `-m "integration and not slow"` for focus.
- Frontend: `pnpm test` (Vitest + jsdom); focused suites (`pnpm test:components`, `pnpm test:store`, `pnpm test:fast`), coverage with `pnpm test:coverage`.
- Advanced: `make test-e2e`, `make test-visual`, `make test-a11y` install Playwright browsers as needed; load testing with `make test-load`.

## Commit & Pull Request Guidelines
- Commit style mirrors history: short, imperative subjects with optional scope (e.g., `Add extraction e2e and export verification`), <=72 chars, one logical change per commit.
- Before pushing, run `make check` and relevant test tiers plus `pnpm test`; update docs and include Alembic migrations when schema changes.
- PRs should explain what/why, link issues, flag breaking changes or new env vars, and include screenshots for UI updates; note validation steps (commands run, datasets used).

## Security & Configuration
- Copy `.env.example` to `.env`; never commit secrets or service keys (`key.json`, GCP creds). Use Secret Manager or local env vars for sensitive data.
- Validate env before deployment with `./deploy/validate-env.sh`; clean `logs/` and `storage/` of local artifacts before opening a PR.
- For schema updates: `alembic revision --autogenerate -m "<summary>"` followed by `alembic upgrade head`; commit the generated migration.

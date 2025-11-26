# Test Environment Setup (API/E2E)

Goal: run API/e2e suites locally with a predictable Postgres/Redis stack.

## Quick Start (local docker)

1. Ensure `.env` has local values:
   - `DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/copy_that`
   - `REDIS_URL=redis://localhost:6379/0`
   - `CELERY_BROKER_URL=redis://localhost:6379/1`
   - `CELERY_RESULT_BACKEND=redis://localhost:6379/2`
2. Start infra:
   - `docker compose up -d postgres redis`
   - Optionally `docker compose up -d api` to exercise live routes.
3. Apply migrations (if Alembic is configured):
   - `docker compose exec api alembic upgrade head`
4. Seed minimal data (projects):
   - `docker compose exec api python - <<'PY'\nfrom copy_that.infrastructure.database import async_session_maker\nfrom copy_that.domain.models import Project\nimport asyncio\nasync def main():\n    async with async_session_maker() as s:\n        s.add(Project(name=\"Test Project\", description=\"Fixture\"))\n        await s.commit()\nasyncio.run(main())\nPY`

## Running tests (scoped)

- Unit/fast tests: `pytest tests/unit/test_generators.py -q`
- Core/token adapters: `pytest tests/core -q`
- API/e2e (requires DB/Redis running):
  - `pytest tests/e2e/test_color_pipeline_e2e.py -q`
  - `pytest tests/integration/test_color_extraction_endpoints.py -q`

If you see `Runner.run() cannot be called from a running event loop`, run with `pytest -s` from outside an active event loop (avoid running inside notebooks).

## Notes

- This repo’s full test matrix expects a live DB; without migrations/seed data many API tests will fail (404s for missing projects/sessions).
- For CI, consider a dedicated `docker-compose.test.yml` (not yet added) that brings up Postgres/Redis and runs migrations before pytest.

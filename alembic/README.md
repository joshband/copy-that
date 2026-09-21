# Alembic Migrations

## Local setup (recommended)

```bash
# Starts Docker Compose Postgres, waits for readiness, runs alembic upgrade head
make db-bootstrap
```

This uses:

```text
postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/copy_that
```

Override with `DATABASE_URL` if needed. If `.env` still points at Neon, `db_bootstrap.py`
prefers local Docker Postgres unless you pass `--url` / `--no-docker`.

### SQLite smoke (no Docker)

Historical migrations include ALTER patterns SQLite cannot always apply.
Use model metadata + stamp instead:

```bash
make db-bootstrap-sqlite
# or
python scripts/db_bootstrap.py --sqlite
```

## Author
```bash
alembic revision --autogenerate -m "message"
```

## Apply
```bash
make db-migrate
# or
alembic upgrade head
```

## Rollback (use cautiously)
```bash
alembic downgrade -1
```

## Notes
- Alembic runs with a **sync** driver (`psycopg2` for Postgres, plain `sqlite` for SQLite).
  `DATABASE_URL` may still use `+asyncpg` / `+aiosqlite`; `alembic/env.py` converts automatically.
- SQLite batch mode is enabled in `alembic/env.py` (`render_as_batch`) for future revisions.
- Missing `deploy/local/init.sql` is provided for Compose mount compatibility; schema comes from Alembic.

Prereq: configure DB URL in `.env` and ensure models are imported before `Base.metadata.create_all` in tests (see `tests/conftest.py`).

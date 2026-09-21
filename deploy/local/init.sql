-- Local Postgres bootstrap (docker-compose postgres service)
-- Intentionally minimal: schema is applied via Alembic (`make db-migrate`).

SELECT 'copy_that local database ready' AS status;

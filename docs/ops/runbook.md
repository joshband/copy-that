# Operations Runbook

## Deploy (standard)

1. **Preflight**: `pnpm test` (frontend), `make test-quick` (backend), `make check` (lint/types).
2. **Migrations**: `alembic upgrade head` (staging), verify DB.
3. **Build & push**: Docker image → registry (or pipeline).
4. **Apply infra**: `terraform apply` if needed, or deploy via CI.
5. **Smoke**: `GET /health`, OpenAPI at `/docs`, load frontend, run one extract.

## Rollback

1. **App**: previous image/version.
2. **DB**: prefer forward fixes; `alembic downgrade -1` only if safe.
3. **Verify**: health + smoke; restore traffic.

## Migrations

- Author in `alembic/versions/`.
- Apply: `alembic upgrade head`.
- Always run on staging before prod.

## Secrets rotation

1. Rotate in Secret Manager / env (API keys, `DATABASE_URL`, Redis, `SECRET_KEY`).
2. Restart consumers.
3. Verify `/health` + smoke extract.

## Health checks & smoke

| Check | Path |
|-------|------|
| API health | `GET /health` |
| OpenAPI | `GET /docs` (Swagger UI) |
| API catalog JSON | `GET /api/v1/docs` (machine-readable map; not Swagger) |
| Frontend | load home → one extraction |

```bash
curl -sf http://localhost:8000/health
curl -sf -o /dev/null -w "%{http_code}\n" http://localhost:8000/docs
```

## Incident quick steps

1. Stabilize (last known good / revert).
2. Contain (pause bad queue/cron if needed).
3. Diagnose (API logs, DB, error rates).
4. Communicate status / ETA / owner.
5. Recover + confirm smoke.

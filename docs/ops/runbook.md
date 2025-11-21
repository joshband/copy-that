# Operations Runbook

## Deploy (standard)
1. **Preflight**: `pnpm test` (frontend), `python -m pytest` (backend), lint/type-check if configured.
2. **Migrations**: `alembic upgrade head` (staging), verify DB health.
3. **Build & push**: Build image (if using Docker) and push to registry.
4. **Apply infra**: `terraform apply` (if infra changes) or deploy via pipeline.
5. **Smoke**: Hit `/api/v1/health`, `/api/v1/docs`, load frontend, run a sample extract.

## Rollback
1. **App**: Roll back to previous image/version.
2. **DB**: If needed, `alembic downgrade -1` (only if safe). Prefer forward fixes over DB downgrades.
3. **Verify**: Health + smoke checks; restore traffic.

## Migrations
- Author in `alembic/versions/`.
- Apply: `alembic upgrade head`.
- Never skip running migrations in staging before prod.

## Secrets Rotation
1. Rotate in secrets store or environment (Claude API key, DB URL, Redis URL, JWT secret).
2. Restart services consuming those secrets.
3. Verify health + smoke.

## Health Checks & Smoke
- API: `/api/v1/health`, `/api/v1/docs`.
- DB: add a lightweight DB ping endpoint (or `SELECT 1` via admin script).
- Frontend: load home, perform one extraction request.

## Incident Quick Steps
1. Stabilize: scale to last known good, revert recent deploy if needed.
2. Contain: disable problematic cron/queue if causing load.
3. Diagnose: check API logs, DB connections, error rates.
4. Communicate: brief status, ETA, owner.
5. Recover: deploy fix or roll back, confirm smoke passes.

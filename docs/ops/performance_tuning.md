# Performance Tuning

## Batch Extraction
- `max_colors`: lower reduces tokens, higher increases coverage; default 10–12 works for most.
- `delta_e_threshold`: lower = stricter dedup (fewer tokens, higher confidence), higher = more merging of similar hues. Defaults to ~2.0 (JND).
- Concurrency: `BatchColorExtractor(max_concurrent=N)`; tune to your rate limits/CPU; start with 3–5.
- Provenance tracking: keep enabled; useful for curation and export accuracy.

## Database
- Indexes: ensure indexes on `library_id`, `project_id`, and roles (already added in migrations).
- Connection pool: size appropriately for your DB tier (Postgres vs SQLite).
- Migrations: keep schema up-to-date via Alembic.

## Caching
- Redis for frequent lookups (token libraries/exports) if needed.
- Avoid caching stale exports after curation; bust cache on curation/export.

## Exports
- W3C/JSON and CSS are fast; React/HTML templates should be simple and synchronous.
- For large libraries, consider streaming response or pagination of tokens in UI.

## Frontend
- Limit `max_colors` exposed to users to avoid overwhelming the UI.
- Defer heavy visualizations and prefer incremental render.

## Observability
- Track extraction latency, dedup ratio, error rate, and DB latency.
- Add Sentry/OTEL exporters if available; sample tracing to avoid overhead.

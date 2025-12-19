# Code & Architecture Review — 2025-12-18

## Summary
- Added generator plugin framework (CSS/React) with API wiring, and a read-only Token Inspector UI. Mood board UX now shows stages, retries, and persists boards locally.
- Backend now exposes `/api/v1/design-tokens/export/generator` to emit code from TokenGraph + componentMeta.
- DB was rebuilt locally via `Base.metadata.create_all` (SQLite); migrations remain the source of truth for other environments.

## Findings (ordered by severity)
- **Startup extractor failures (degraded coverage)** — Backend logs `Failed to register color extractor` and `Failed to register spacing extractor` at boot (imports from `copy_that.extractors.color.extractor` and `copy_that.extractors.spacing`). Color/spacing still work via other paths, but this signals dead wiring and risk of silent gaps. Fix: remove stale registration or restore the expected classes/utilities. (app startup logs)
- **Generator endpoint exposed without guardrails** — `/api/v1/design-tokens/export/generator` accepts arbitrary `component_meta` and emits full token JSON inlined into TSX/CSS strings. There’s no auth/size/validation. Risk: very large payloads or untrusted callers could bloat responses or log sensitive data. Recommend adding auth, size limits, and schema validation for `component_meta` before wider use. (src/copy_that/interfaces/api/design_tokens.py)
- **Celery/broker dependency still opaque** — Mood board enqueue now checks `CELERY_BROKER_URL`, but with the variable set and no worker/broker running, jobs will queue and never resolve. UI shows retries, yet API lacks a readiness/health surface for the queue. Add a `/mood-board/health` broker check or return 503 when enqueue fails due to missing broker/worker. (src/copy_that/interfaces/api/mood_board.py)
- **Local DB rebuild bypassed migrations** — For SQLite the schema was recreated via `Base.metadata.create_all`. This is fine for dev, but ensure real deployments continue to run Alembic to avoid drift (indexes/constraints). Add a note or guard if this path is used outside local. (app_factory lifespan + local rebuild)
- **Generator JSON inlined into TSX** — React generator embeds the entire flattened token JSON into the emitted snippet. For large token sets this will be heavy and not tree-shakeable. Consider emitting imports or splitting data/code for production use. (src/copy_that/generators/plugins/react.py)

## Positive Notes
- Token Inspector is read-only and uses existing Tabs primitives; localStorage persistence makes UX resilient to backend issues.
- Generator plugin registry cleanly isolates generation concerns and is extendable.
- Mood board UI now surfaces progress/error states and retries, reducing “silent failure” confusion.

## Suggested Next Steps
1. Fix extractor registration errors (either restore classes or remove the registration hook).
2. Add auth + request size validation + schema for `/design-tokens/export/generator` before exposing externally.
3. Add broker/worker readiness checks (or return 503) in mood board enqueue when Celery isn’t available.
4. Document that `metadata.create_all` is dev-only; enforce Alembic in non-local environments.
5. Consider streaming or referencing tokens in the React generator to avoid embedding large JSON blobs.

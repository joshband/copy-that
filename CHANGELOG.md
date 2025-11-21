# Changelog

All notable changes to this project will be documented in this file.

## Unreleased
- (placeholder for next changes)

## v0.4.0 — 2025-11-21
- Added session/library/export APIs with batch extraction, aggregation, provenance, and multi-format exports (w3c/css/react/html).
- Introduced batch extractor and generators (`src/copy_that/generators/*`, `src/copy_that/application/batch_extractor.py`).
- Frontend: Added educational components (TokenGrid/Inspector/Playground, color details/palettes) and Minimalist design guide; Zustand store, registry, and tests.
- Docs: Full reorganization into structured hierarchy (overview/setup/configuration/workflows/examples/ops/testing/design); added runbook, performance tuning, troubleshooting matrix, API curl examples; centralized design guide.
- Infra/ops: Terraform README, Alembic README; moved root test scripts into `tests/scripts/`.
- Tests: Expanded unit/integration/e2e suites and targeted scripts.

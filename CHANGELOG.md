# Changelog

All notable changes to this project will be documented in this file.

## Unreleased

### Pipeline Foundation
- **Pipeline interfaces**: Added `copy_that.pipeline` module with core types and interfaces for multi-agent token extraction
- **W3C Design Tokens**: Full support in `TokenResult` with path hierarchy, $type, $description, $value (simple/composite), references, and $extensions
- **Types**: `TokenType` (extraction categories), `W3CTokenType` (W3C $type values), `TokenResult`, `PipelineTask`, `ProcessedImage`
- **Interfaces**: `BasePipelineAgent` ABC with `process()`, `health_check()`, `agent_type`, `stage_name`
- **Exceptions**: `PipelineError` hierarchy (Preprocessing/Extraction/Aggregation/Validation/Generation)
- **Documentation**: Added `PIPELINE_GLOSSARY.md` explaining Agent vs Extractor terminology

### Infrastructure & CI/CD
- **Docker improvements**: Fixed multi-stage Dockerfile for Cloud Run (PORT env var, gunicorn, hatchling build config)
- **Local Docker testing**: Added `deploy/validate-env.sh` script for .env validation before running containers
- **GitHub Actions optimization**:
  - Added uv-specific caching (faster than pip)
  - Concurrency controls to prevent duplicate runs
  - Service account key authentication for GCP
- **Security scanning**: Added pip-audit, Bandit, Trivy, and Gitleaks to CI pipeline
- **Dependabot**: Configured for Python, npm, and GitHub Actions dependency updates
- **Database**: Auto-convert `postgresql://` to `postgresql+asyncpg://` for async driver compatibility

### Backend
- **OpenAI GPT-4V**: Added as alternative color extractor (alongside Claude Sonnet 4.5)
- **Production stability**: Skip auto table creation in staging/production (use Alembic migrations)
- **Dependencies**: Added gunicorn, openai, coloraide to production dependencies

### Documentation
- Updated ROADMAP with nice-to-have Redis caching patterns
- Added deployment smoke tests (health check, API status)

## v0.4.0 — 2025-11-21
- Added session/library/export APIs with batch extraction, aggregation, provenance, and multi-format exports (w3c/css/react/html).
- Introduced batch extractor and generators (`src/copy_that/generators/*`, `src/copy_that/application/batch_extractor.py`).
- Frontend: Added educational components (TokenGrid/Inspector/Playground, color details/palettes) and Minimalist design guide; Zustand store, registry, and tests.
- Docs: Full reorganization into structured hierarchy (overview/setup/configuration/workflows/examples/ops/testing/design); added runbook, performance tuning, troubleshooting matrix, API curl examples; centralized design guide.
- Infra/ops: Terraform README, Alembic README; moved root test scripts into `tests/scripts/`.
- Tests: Expanded unit/integration/e2e suites and targeted scripts.

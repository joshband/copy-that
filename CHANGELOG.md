# Changelog

All notable changes to this project will be documented in this file.

## v0.4.3 — 2025-12-08

### Infrastructure & DevOps Optimization
- **Cost Reduction**: 80-90% infrastructure cost reduction (~$95-150/month savings)
  - Removed Cloud SQL in favor of Neon (saved $25-50/month)
  - Removed Redis/Memorystore (saved $30-40/month)
  - Cloud Run min-instances=0 (saved $40-60/month)
  - Optimized max-instances: 100→25 (right-sized for solo dev)
- **Security**: Switched to Workload Identity Federation for GitHub Actions
  - Removed long-lived service account keys
  - Short-lived OAuth tokens (1 hour expiry)
  - Better audit trail and security posture
- **Docker Optimization**:
  - Multi-stage builds (70% smaller images)
  - Improved layer caching (dependencies before source)
  - Added comprehensive .dockerignore (30-50% faster builds)
  - Production test profile in docker-compose.yml
- **CI/CD Optimization**:
  - Added job dependencies (lint → test → docker)
  - Python dependency caching (2-3x faster CI runs)
  - Added timeouts (10-20 min) to prevent runaway jobs
  - Fail-fast strategy saves 5-10 minutes on errors
  - Workflow notifications for success/failure
- **Documentation**:
  - Created comprehensive DevOps Guide (docs/DEVOPS_GUIDE.md)
  - Organized root-level MD files into docs/sessions, docs/deployment, docs/guides
  - Updated README with current deployment strategy
  - Local production testing script (scripts/test-production-build.sh)
- **Secret Management**: Switched from Secret Manager to GitHub Actions secrets
  - Simpler management for solo developer
  - DATABASE_URL from Neon
  - No Secret Manager resources needed

### Files Changed
- Deleted: `deploy/terraform/cloudsql.tf`, `deploy/terraform/redis.tf`
- Updated: `deploy/terraform/main.tf`, `cloudrun.tf`, `networking.tf`, `outputs.tf`
- Updated: `.github/workflows/build.yml`, `.github/workflows/deploy.yml`, `.github/workflows/ci.yml`
- Created: `.dockerignore`, `docs/DEVOPS_GUIDE.md`, `scripts/test-production-build.sh`
- Moved: 25+ root-level MD files to organized docs/ structure

## Unreleased (v0.4.2)

### Security & Rate Limiting (Issue #11)
- **Rate Limiting Middleware**: Environment-aware rate limiting on expensive AI extraction endpoints
  - Production: Strict enforcement with 429 Too Many Requests after limit exceeded
  - Development: Tracks usage without blocking (enables uninterrupted development)
  - Testing: Completely disabled for fast test execution
- **Rate Limit Configuration**:
  - `/colors/extract`: 10 req/min per client (IP or API key)
  - `/colors/extract-streaming`: 10 req/min per client
  - `/spacing/extract`: 10 req/min per client
  - `/spacing/extract-streaming`: 10 req/min per client
  - `/spacing/batch-extract`: 5 req/min per client (batch operations)
  - `/extract/stream`: 5 req/min per client (multi-token extraction)
- **Quota Tracking**: Per-client quota tracking with estimated API cost monitoring ($0.01-0.05 per request)
- **Client Identification**: Smart priority-based client identification (API key > user ID > IP address)
- **Zero Dependencies**: Uses only FastAPI/Python stdlib; no external rate limiting libraries required
- **Async-Safe**: Proper locking with asyncio.Lock for thread-safe quota updates
- **Test Coverage**: 31 comprehensive tests covering quota tracking, environment-aware behavior, cost accumulation, and client identification
- **Implementation**: 168 lines in `src/copy_that/infrastructure/security/rate_limiter.py`

### Validation & Quality
- Accept hex/rgb/hsl color formats; custom validation rule hooks.
- Palette harmony scoring with ColorAide utilities; semantic naming recommendations.
- Added token graph containment/alignment metadata to spacing results and debug UI gating.
- Added regression harness (synthetic + fixture manifest scaffold) for UI extraction checks.
- Token graph relations now use typed enums (`TokenType`, `RelationType`, `TokenRelation`) instead of ad-hoc string dicts; repository helpers coerce/validate relation edges.

### Generator & Tooling
- Added Figma export template and CLI helper (`scripts/generate_figma_tokens.py`).
- Added token diff utility for comparing generations.
- Improved color HTML demo (filters for WCAG/harmony, semantic metadata); spacing demo retained rich visualization.

### Docs
- Added session-0-6 cleanup summary and planning/reference review notes.
- Documented new orchestrator test coverage for `AgentPool`, `CircuitBreaker`, and `PipelineCoordinator`.
- Documented generator test coverage covering CSS/HTML/React and spacing generator outputs.
- Documented preprocessing test coverage for downloader, validator, and enhancer components.
- Documented extraction schema, prompt, and agent unit coverage (validate parsing, metadata handling, and helper utilities).
- Documented infrastructure Redis/celery coverage for cache helpers, connection retries, and health probes.
- Documented aggregation agent coverage covering token validation, deduplication toggles, provenance propagation, clustering guards, and forced error paths.

## v0.4.1 — 2025-11-23

### Complete Pipeline Architecture
- **Full 5-stage pipeline**: Preprocessing → Extraction → Aggregation → Validation → Generation
- **All pipeline sessions implemented**: Sessions 0-6 merged (PRs #40-45)

### Preprocessing Pipeline (Session 1)
- **ImageValidator**: SSRF protection (blocks private IPs 10.x, 172.16.x, 192.168.x, 127.x, metadata endpoints)
- **ImageDownloader**: Async HTTP with httpx, 30s timeout, exponential backoff retries
- **ImageEnhancer**: CLAHE contrast enhancement, EXIF orientation fix, WebP conversion, aspect-ratio resize
- **PreprocessingAgent**: Orchestrates validate → download → enhance with ProcessedImage output
- **Security**: 10MB size limit, magic bytes validation (PNG/JPEG/WebP/GIF)

### Extraction Engine (Session 2)
- **Tool Use schemas**: Strict JSON Schema for color, spacing, typography, shadow, gradient tokens
- **ExtractionAgent**: Single agent handles ALL token types via configuration (no regex parsing)
- **Prompt templates**: Type-specific prompts for optimal AI extraction
- **Error handling**: Timeout, rate limits, retries with graceful degradation

### Aggregation Pipeline (Session 3)
- **Deduplicator**: Delta-E color deduplication using ColorAide (2.0 JND threshold)
- **ProvenanceTracker**: Tracks source images per token, weighted confidence scores
- **AggregationAgent**: Orchestrates dedup + provenance, returns merged token list
- **Clustering**: K-means grouping for related tokens

### Validation Pipeline (Session 4)
- **Schema validation**: Pydantic validation of all token fields, bounds checking
- **AccessibilityCalculator**: WCAG contrast ratios (AA: 4.5:1, AAA: 7:1), colorblind safety
- **QualityScorer**: Confidence aggregation, completeness checks
- **ValidationAgent**: Returns validated tokens with accessibility and quality scores

### Generator Pipeline (Session 5)
- **GeneratorAgent**: Single agent handles all output formats via configuration
- **Jinja2 templates**: W3C Design Tokens JSON, CSS Custom Properties, React themes, Tailwind configs
- **Format support**: w3c, css, scss, react, tailwind, figma
- **HTML demo**: Visual preview of extracted tokens

### Pipeline Orchestrator (Session 6)
- **AgentPool**: Configurable concurrency per stage with semaphores
- **CircuitBreaker**: CLOSED → OPEN → HALF_OPEN states, 5 failure threshold, 30s recovery
- **PipelineCoordinator**: Full pipeline execution with parallel image processing
- **Error aggregation**: Collects and reports errors across all stages

### Testing & Quality
- **95%+ coverage**: All pipeline components with comprehensive tests
- **TDD approach**: Tests written before implementation
- **Type safety**: Full mypy type compatibility across Python versions

## Unreleased
### Frontend / UX
- SSE multi-extract streaming for color + spacing (CV-first, AI-second) on the main page; spacing tokens now load with projects and snapshots.
- Added snapshot load (latest snapshot) in UI; spacing prominence/base-unit/scale and color extractor/model/histogram significance now displayed.

### Backend
- Added spacing_tokens table and project_snapshots table with persistence from multi-extract.
- New batch endpoints: `/api/v1/colors/batch` and enhanced `/api/v1/spacing/batch-extract` (CV+AI merge).
- Snapshot APIs: list and fetch project snapshots.
- CV spacing extractor returns prominence and base unit/scale metadata for UI.

### Docs
- Updated parity plans and architecture docs for color/spacing; README notes recent SSE/snapshot/batch additions.

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
- Added README/Changelog refresh for FastSAM optional segmentation, debug toggle, regression harness.

### Experimental / Optional
- FastSAM segmentation integration (now enabled by default; auto-downloads `FastSAM-s.pt` when ultralytics is installed, configurable via `FASTSAM_MODEL_PATH`/`FASTSAM_ENABLED`) to emit segmentation regions alongside spacing results.

## v0.4.0 — 2025-11-21
- Added session/library/export APIs with batch extraction, aggregation, provenance, and multi-format exports (w3c/css/react/html).
- Introduced batch extractor and generators (`src/copy_that/generators/*`, `src/copy_that/application/batch_extractor.py`).
- Frontend: Added educational components (TokenGrid/Inspector/Playground, color details/palettes) and Minimalist design guide; Zustand store, registry, and tests.
- Docs: Full reorganization into structured hierarchy (overview/setup/configuration/workflows/examples/ops/testing/design); added runbook, performance tuning, troubleshooting matrix, API curl examples; centralized design guide.
- Infra/ops: Terraform README, Alembic README; moved root test scripts into `tests/scripts/`.
- Tests: Expanded unit/integration/e2e suites and targeted scripts.

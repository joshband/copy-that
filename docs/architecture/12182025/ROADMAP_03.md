# Roadmap

## GCP Cloud Run Deployment Guide

### Sources
- `docs/deployment/DEPLOYMENT_GUIDE_GCP_CLOUDRUN.md`

### Summary
**Date:** 2025-12-08 **Objective:** Deploy Copy That to GCP Cloud Run with Terraform **Status:** In Progress

### Key Points
- TypeScript type checking: **PASSING**
- Backend unit tests (34 passed): **PASSING**
- Terraform configuration: **VERIFIED**
- Docker files: **IN PLACE** (main, frontend, debug variants)
- Repository: **CLEAN** with all branches merged
- GCP Project created (copy-that-platform or your project)
- GCP Service Account with appropriate permissions
- terraform.tfvars file configured with credentials
- Docker image built and pushed to Artifact Registry
- Backend validation fixes (if needed)

### Implementation Pointers
- `pnpm type-check`

### Build / Refactor Issues
#### TypeScript type checking: **PASSING**

**Context**
Source: `docs/deployment/DEPLOYMENT_GUIDE_GCP_CLOUDRUN.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: TypeScript type checking: **PASSING**
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- pnpm type-check
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Backend unit tests : **PASSING**

**Context**
Source: `docs/deployment/DEPLOYMENT_GUIDE_GCP_CLOUDRUN.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Backend unit tests : **PASSING**
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- pnpm type-check
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Terraform configuration: **VERIFIED**

**Context**
Source: `docs/deployment/DEPLOYMENT_GUIDE_GCP_CLOUDRUN.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Terraform configuration: **VERIFIED**
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- pnpm type-check
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Docker files: **IN PLACE**

**Context**
Source: `docs/deployment/DEPLOYMENT_GUIDE_GCP_CLOUDRUN.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Docker files: **IN PLACE**
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- pnpm type-check
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## GCP Deployment with Terraform

### Sources
- `docs/setup/gcp_terraform_deployment.md`

### Summary
Deploy Copy That to Google Cloud Platform using Infrastructure as Code (Terraform).

**Cost:** $0/month (free tier) for hobbyist use ✅

### Key Points
- ✅ GCP Project: copy-that-platform (already created)
- ✅ Billing account: Linked to project (for tracking, no charges for free tier)
- **Neon Database URL**
- Go to: https://console.neon.tech
- Copy connection string: postgresql://user:password@host.neon.tech/dbname?sslmode=require
- **Anthropic API Key**
- Go to: https://console.anthropic.com
- Create/copy API key: sk-proj-...
- 1x Artifact Registry repository
- API enablements (Cloud Run, Artifact Registry, etc.)

### Implementation Pointers
- `deploy/terraform/`
- `pnpm test`

### Build / Refactor Issues
#### ✅ GCP Project: copy-that-platform

**Context**
Source: `docs/setup/gcp_terraform_deployment.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: ✅ GCP Project: copy-that-platform
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- deploy/terraform/
- pnpm test
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### ✅ Billing account: Linked to project

**Context**
Source: `docs/setup/gcp_terraform_deployment.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: ✅ Billing account: Linked to project
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- deploy/terraform/
- pnpm test
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **Neon Database URL**

**Context**
Source: `docs/setup/gcp_terraform_deployment.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Neon Database URL**
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- deploy/terraform/
- pnpm test
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Go to: https://console.neon.tech

**Context**
Source: `docs/setup/gcp_terraform_deployment.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Go to: https://console.neon.tech
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- deploy/terraform/
- pnpm test
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Guides

### Sources
- `docs/guides/README.md`

### Summary
_No narrative prose found; see Key Points._

### Key Points
- api_reference.md — API overview and usage
- frontend_setup.md — Frontend setup steps
- how_to_add_features.md — Adding features workflow
- testing/testing_overview.md — Testing guidance

### Implementation Pointers
_No explicit code touchpoints referenced in doc._

### Build / Refactor Issues
#### api_reference.md — API overview and usage

**Context**
Source: `docs/guides/README.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: api_reference.md — API overview and usage
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### frontend_setup.md — Frontend setup steps

**Context**
Source: `docs/guides/README.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: frontend_setup.md — Frontend setup steps
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### how_to_add_features.md — Adding features workflow

**Context**
Source: `docs/guides/README.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: how_to_add_features.md — Adding features workflow
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### testing/testing_overview.md — Testing guidance

**Context**
Source: `docs/guides/README.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: testing/testing_overview.md — Testing guidance
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## How to Add Features

### Sources
- `docs/guides/HOW_TO_ADD_FEATURES.md`

### Summary
**Version:** 1.0 | **Date:** 2025-11-19 | **Status:** Complete

Step-by-step guide for adding new features to Copy That, from planning to deployment.

### Key Points
- PLAN        Define what you're building
- DESIGN      Architecture and schema
- IMPLEMENT   Write code following patterns
- TEST        Achieve 80%+ coverage
- REVIEW      Get feedback via PR
- DEPLOY      Ship to staging/production
- Extract 3-5 opacity levels per image
- Confidence scores ≥ 0.75
- Integrate with existing token flow
- Requires ColorExtractor (already done)

### Implementation Pointers
- `/api/v1/export`
- `/api/v1/extract/opacity`
- `src/copy_that`
- `src/copy_that/adapters/opacity_adapter.py`
- `src/copy_that/domain/schemas/opacity.py`
- `src/copy_that/extractors/opacity_extractor.py`
- `src/copy_that/interfaces/api/main.py`
- `src/copy_that/interfaces/api/routes/extraction.py`

### Build / Refactor Issues
#### PLAN        Define what you're building

**Context**
Source: `docs/guides/HOW_TO_ADD_FEATURES.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: PLAN        Define what you're building
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/export
- /api/v1/extract/opacity
- src/copy_that
- src/copy_that/adapters/opacity_adapter.py
- src/copy_that/domain/schemas/opacity.py
- src/copy_that/extractors/opacity_extractor.py
- src/copy_that/interfaces/api/main.py
- src/copy_that/interfaces/api/routes/extraction.py
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### DESIGN      Architecture and schema

**Context**
Source: `docs/guides/HOW_TO_ADD_FEATURES.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: DESIGN      Architecture and schema
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/export
- /api/v1/extract/opacity
- src/copy_that
- src/copy_that/adapters/opacity_adapter.py
- src/copy_that/domain/schemas/opacity.py
- src/copy_that/extractors/opacity_extractor.py
- src/copy_that/interfaces/api/main.py
- src/copy_that/interfaces/api/routes/extraction.py
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### IMPLEMENT   Write code following patterns

**Context**
Source: `docs/guides/HOW_TO_ADD_FEATURES.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: IMPLEMENT   Write code following patterns
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/export
- /api/v1/extract/opacity
- src/copy_that
- src/copy_that/adapters/opacity_adapter.py
- src/copy_that/domain/schemas/opacity.py
- src/copy_that/extractors/opacity_extractor.py
- src/copy_that/interfaces/api/main.py
- src/copy_that/interfaces/api/routes/extraction.py
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### TEST        Achieve 80%+ coverage

**Context**
Source: `docs/guides/HOW_TO_ADD_FEATURES.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: TEST        Achieve 80%+ coverage
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/export
- /api/v1/extract/opacity
- src/copy_that
- src/copy_that/adapters/opacity_adapter.py
- src/copy_that/domain/schemas/opacity.py
- src/copy_that/extractors/opacity_extractor.py
- src/copy_that/interfaces/api/main.py
- src/copy_that/interfaces/api/routes/extraction.py
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Implementation Roadmap: Copy That

### Sources
- `docs/planning/IMPLEMENTATION_ROADMAP.md`

### Summary
**Version:** 1.0.0 **Last Updated:** 2025-11-20 **Status:** Phase 4 Complete, Phase 5 Ready

### Key Points
- **Phase 4:** COMPLETE ✅ (28 tests, 5,678 LOC)
- **Phase 5:** 4 weeks (Spacing, Shadow, Typography, ~200 tests)
- **Phase 6:** 4 weeks (Components, Variants, Token Graph, ~300 tests)
- **Phase 7:** 6+ weeks (Video, Audio, Text, ~400 tests)
- ✅ Schema foundation (JSON → Pydantic → Zod)
- ✅ Adapter layer (Core → API → Database)
- ✅ Database schema (color_tokens table)
- ✅ AI extractor (Claude Sonnet 4.5 + Structured Outputs)
- ✅ Frontend integration (upload, display, educational widgets)
- ✅ 28 comprehensive tests (100% coverage)

### Implementation Pointers
_No explicit code touchpoints referenced in doc._

### Build / Refactor Issues
#### **Phase 4:** COMPLETE ✅

**Context**
Source: `docs/planning/IMPLEMENTATION_ROADMAP.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Phase 4:** COMPLETE ✅
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **Phase 5:** 4 weeks

**Context**
Source: `docs/planning/IMPLEMENTATION_ROADMAP.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Phase 5:** 4 weeks
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **Phase 6:** 4 weeks

**Context**
Source: `docs/planning/IMPLEMENTATION_ROADMAP.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Phase 6:** 4 weeks
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **Phase 7:** 6+ weeks

**Context**
Source: `docs/planning/IMPLEMENTATION_ROADMAP.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Phase 7:** 6+ weeks
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Infrastructure Setup Guide

### Sources
- `docs/setup/infrastructure_setup.md`

### Summary
Step-by-step guide to set up the complete infrastructure for Copy That from scratch.

### Key Points
- Go to https://github.com/joshband/copy-that/settings/secrets/actions
- Click "New repository secret"
- Add each secret with the values from above
- API enablement: gcloud services list --enabled
- IAM permissions: gcloud projects get-iam-policy $PROJECT_ID
- Quota limits: gcloud compute project-info describe
- **Set up monitoring alerts** - Cloud Monitoring
- **Configure custom domain** - Cloud Run domain mapping
- **Enable CDN** - Cloud CDN for frontend assets
- **Set up backups** - Automated database backups

### Implementation Pointers
- `/api/v1/health`
- `/api/v1/health/db`
- `/api/v1/health/redis`
- `deploy/terraform`

### Build / Refactor Issues
#### Go to https://github.com/joshband/copy-that/settings/secrets/actions

**Context**
Source: `docs/setup/infrastructure_setup.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Go to https://github.com/joshband/copy-that/settings/secrets/actions
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/health
- /api/v1/health/db
- /api/v1/health/redis
- deploy/terraform
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Click "New repository secret"

**Context**
Source: `docs/setup/infrastructure_setup.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Click "New repository secret"
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/health
- /api/v1/health/db
- /api/v1/health/redis
- deploy/terraform
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Add each secret with the values from above

**Context**
Source: `docs/setup/infrastructure_setup.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Add each secret with the values from above
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/health
- /api/v1/health/db
- /api/v1/health/redis
- deploy/terraform
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### API enablement: gcloud services list --enabled

**Context**
Source: `docs/setup/infrastructure_setup.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: API enablement: gcloud services list --enabled
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/health
- /api/v1/health/db
- /api/v1/health/redis
- deploy/terraform
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Mood Board Generation Specification

### Sources
- `docs/MOOD_BOARD_SPECIFICATION.md`

### Summary
Copy That generates AI-curated mood boards that translate extracted design tokens into rich visual narratives. Mood boards bridge raw token data (colors, typography, spacing) with cultural context, material DNA, and aesthetic movements.

**Purpose:** Capture the physical, tactile, and surface qualities of a design system.

### Key Points
- Anodized aluminum surfaces (brushed, matte, polished)
- Resin/enamel swirls and fluid patterns
- Glass globes and translucent indicators
- Tactile polymers and soft-touch materials
- CRT oscilloscope glows and phosphor traces
- Metallic finishes (gold, brass, chrome, gunmetal)
- Synesthetic gradients and color blending
- Physical controls (knobs, sliders, buttons)
- Emphasis on texture and materiality
- Physical object photography

### Implementation Pointers
_No explicit code touchpoints referenced in doc._

### Build / Refactor Issues
#### Anodized aluminum surfaces

**Context**
Source: `docs/MOOD_BOARD_SPECIFICATION.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Anodized aluminum surfaces
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Resin/enamel swirls and fluid patterns

**Context**
Source: `docs/MOOD_BOARD_SPECIFICATION.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Resin/enamel swirls and fluid patterns
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Glass globes and translucent indicators

**Context**
Source: `docs/MOOD_BOARD_SPECIFICATION.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Glass globes and translucent indicators
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Tactile polymers and soft-touch materials

**Context**
Source: `docs/MOOD_BOARD_SPECIFICATION.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Tactile polymers and soft-touch materials
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Performance Tuning

### Sources
- `docs/ops/performance_tuning.md`

### Summary
_No narrative prose found; see Key Points._

### Key Points
- max_colors: lower reduces tokens, higher increases coverage; default 10–12 works for most.
- delta_e_threshold: lower = stricter dedup (fewer tokens, higher confidence), higher = more merging of similar hues. Defaults to ~2.0 (JND).
- Concurrency: BatchColorExtractor(max_concurrent=N); tune to your rate limits/CPU; start with 3–5.
- Provenance tracking: keep enabled; useful for curation and export accuracy.
- Indexes: ensure indexes on library_id, project_id, and roles (already added in migrations).
- Connection pool: size appropriately for your DB tier (Postgres vs SQLite).
- Migrations: keep schema up-to-date via Alembic.
- Redis for frequent lookups (token libraries/exports) if needed.
- Avoid caching stale exports after curation; bust cache on curation/export.
- W3C/JSON and CSS are fast; React/HTML templates should be simple and synchronous.

### Implementation Pointers
_No explicit code touchpoints referenced in doc._

### Build / Refactor Issues
#### max_colors: lower reduces tokens, higher increases coverage; default 10–12 works for most

**Context**
Source: `docs/ops/performance_tuning.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: max_colors: lower reduces tokens, higher increases coverage; default 10–12 works for most
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### delta_e_threshold: lower = stricter dedup , higher = more merging of similar hues. Defa…

**Context**
Source: `docs/ops/performance_tuning.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: delta_e_threshold: lower = stricter dedup , higher = more merging of similar hues. Defa…
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Concurrency: BatchColorExtractor; tune to your rate limits/CPU; start with 3–5

**Context**
Source: `docs/ops/performance_tuning.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Concurrency: BatchColorExtractor; tune to your rate limits/CPU; start with 3–5
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Provenance tracking: keep enabled; useful for curation and export accuracy

**Context**
Source: `docs/ops/performance_tuning.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Provenance tracking: keep enabled; useful for curation and export accuracy
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Planning Docs

### Sources
- `docs/planning/README.md`

### Summary
_No narrative prose found; see Key Points._

### Key Points
- implementation_roadmap.md — Roadmap and phasing
- implementation_checklist.md — Actionable checklist

### Implementation Pointers
_No explicit code touchpoints referenced in doc._

### Build / Refactor Issues
#### implementation_roadmap.md — Roadmap and phasing

**Context**
Source: `docs/planning/README.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: implementation_roadmap.md — Roadmap and phasing
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### implementation_checklist.md — Actionable checklist

**Context**
Source: `docs/planning/README.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: implementation_checklist.md — Actionable checklist
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Plugin Architecture: Modular Token Platform

### Sources
- `docs/architecture/PLUGIN_ARCHITECTURE.md`

### Summary
**Version:** 1.0 | **Date:** 2025-11-19 | **Status:** Guide

This document explains the plugin architecture that enables Copy That's modular, extensible design.

### Key Points
- **Core Platform** - Minimal, stable, handles all token types
- **Plugins** - Modular extractors and generators that extend the platform
- **Loose Coupling** - Plugins are independent, can be mixed/matched
- **Registry** - Plugins register themselves at startup
- **Composition** - Run any combination of plugins on any input
- ColorExtractor (K-means clustering)
- SpacingExtractor (SAM segmentation)
- TypographyExtractor (Font detection)
- ShadowExtractor (Depth analysis)
- ReactGenerator (CSS-in-JS)

### Implementation Pointers
- `/api/v1/extract/my-tokens`
- `/api/v1/plugins`
- `/api/v1/plugins/`
- `src/copy_that/plugins/extractors/my_extractor.py`

### Build / Refactor Issues
#### **Core Platform** - Minimal, stable, handles all token types

**Context**
Source: `docs/architecture/PLUGIN_ARCHITECTURE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Core Platform** - Minimal, stable, handles all token types
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/extract/my-tokens
- /api/v1/plugins
- /api/v1/plugins/
- src/copy_that/plugins/extractors/my_extractor.py
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **Plugins** - Modular extractors and generators that extend the platform

**Context**
Source: `docs/architecture/PLUGIN_ARCHITECTURE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Plugins** - Modular extractors and generators that extend the platform
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/extract/my-tokens
- /api/v1/plugins
- /api/v1/plugins/
- src/copy_that/plugins/extractors/my_extractor.py
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **Loose Coupling** - Plugins are independent, can be mixed/matched

**Context**
Source: `docs/architecture/PLUGIN_ARCHITECTURE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Loose Coupling** - Plugins are independent, can be mixed/matched
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/extract/my-tokens
- /api/v1/plugins
- /api/v1/plugins/
- src/copy_that/plugins/extractors/my_extractor.py
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **Registry** - Plugins register themselves at startup

**Context**
Source: `docs/architecture/PLUGIN_ARCHITECTURE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Registry** - Plugins register themselves at startup
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/extract/my-tokens
- /api/v1/plugins
- /api/v1/plugins/
- src/copy_that/plugins/extractors/my_extractor.py
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Production Deployment Guide - Copy That

### Sources
- `docs/setup/production_deployment_guide.md`

### Summary
This guide covers deploying Copy That to production with a focus on:

### Key Points
- Backend API (FastAPI/Python)
- Frontend (React/Vite)
- Database (Neon PostgreSQL)
- Security, performance, and reliability
- All tests passing (33/33 integration + e2e)
- Performance validated (2.76ms per color, 500 colors in 1.38s)
- Type safety verified (0 TypeScript errors)
- Full end-to-end workflow implemented
- [ ] All tests passing: python -m pytest tests/ --no-cov
- [ ] Type checking passes: pnpm type-check

### Implementation Pointers
- `/api/v1/db-test`
- `/api/v1/status`
- `alembic upgrade`
- `frontend/src/`
- `pnpm build`
- `pnpm lint`
- `pnpm type-check`

### Build / Refactor Issues
#### Backend API

**Context**
Source: `docs/setup/production_deployment_guide.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Backend API
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/db-test
- /api/v1/status
- alembic upgrade
- frontend/src/
- pnpm build
- pnpm lint
- pnpm type-check
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Frontend

**Context**
Source: `docs/setup/production_deployment_guide.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Frontend
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/db-test
- /api/v1/status
- alembic upgrade
- frontend/src/
- pnpm build
- pnpm lint
- pnpm type-check
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Database

**Context**
Source: `docs/setup/production_deployment_guide.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Database
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/db-test
- /api/v1/status
- alembic upgrade
- frontend/src/
- pnpm build
- pnpm lint
- pnpm type-check
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Security, performance, and reliability

**Context**
Source: `docs/setup/production_deployment_guide.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Security, performance, and reliability
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/db-test
- /api/v1/status
- alembic upgrade
- frontend/src/
- pnpm build
- pnpm lint
- pnpm type-check
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Progressive, Non-Blocking Color Extraction Architecture

### Sources
- `docs/workflows/progressive_color_extraction.md`

### Summary
**File:** `src/copy_that/application/async_color_extractor.py` (NEW)

### Key Points
- ✅ **Progressive Enhancement**: See first colors in 1-2 seconds
- ✅ **Visual Feedback**: Progress bar shows work in progress
- ✅ **Error Recovery**: Single color failure doesn't block others
- ✅ **Interactive**: Can start using colors before full extraction completes
- ✅ **Non-Blocking**: Each color processed independently
- ✅ **Atomic Operations**: DB writes are isolated transactions
- ✅ **Scalability**: Celery enables background processing
- ✅ **Resilience**: Failure of one color doesn't crash pipeline
- ✅ **TTFCP** (Time to First Color Parsed): ~1 second
- ✅ **TTFC** (Time to First Color Computed): ~2-3 seconds

### Implementation Pointers
- `/api/v1/colors/extract/stream`
- `frontend/src/components/ProgressiveColorPalette.tsx`
- `frontend/src/hooks/useColorExtractionStream.ts`
- `src/copy_that/application/async_color_extractor.py`
- `src/copy_that/infrastructure/celery_tasks.py`
- `src/copy_that/interfaces/api/main.py`

### Build / Refactor Issues
#### ✅ **Progressive Enhancement**: See first colors in 1-2 seconds

**Context**
Source: `docs/workflows/progressive_color_extraction.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: ✅ **Progressive Enhancement**: See first colors in 1-2 seconds
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/colors/extract/stream
- frontend/src/components/ProgressiveColorPalette.tsx
- frontend/src/hooks/useColorExtractionStream.ts
- src/copy_that/application/async_color_extractor.py
- src/copy_that/infrastructure/celery_tasks.py
- src/copy_that/interfaces/api/main.py
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### ✅ **Visual Feedback**: Progress bar shows work in progress

**Context**
Source: `docs/workflows/progressive_color_extraction.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: ✅ **Visual Feedback**: Progress bar shows work in progress
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/colors/extract/stream
- frontend/src/components/ProgressiveColorPalette.tsx
- frontend/src/hooks/useColorExtractionStream.ts
- src/copy_that/application/async_color_extractor.py
- src/copy_that/infrastructure/celery_tasks.py
- src/copy_that/interfaces/api/main.py
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### ✅ **Error Recovery**: Single color failure doesn't block others

**Context**
Source: `docs/workflows/progressive_color_extraction.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: ✅ **Error Recovery**: Single color failure doesn't block others
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/colors/extract/stream
- frontend/src/components/ProgressiveColorPalette.tsx
- frontend/src/hooks/useColorExtractionStream.ts
- src/copy_that/application/async_color_extractor.py
- src/copy_that/infrastructure/celery_tasks.py
- src/copy_that/interfaces/api/main.py
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### ✅ **Interactive**: Can start using colors before full extraction completes

**Context**
Source: `docs/workflows/progressive_color_extraction.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: ✅ **Interactive**: Can start using colors before full extraction completes
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/colors/extract/stream
- frontend/src/components/ProgressiveColorPalette.tsx
- frontend/src/hooks/useColorExtractionStream.ts
- src/copy_that/application/async_color_extractor.py
- src/copy_that/infrastructure/celery_tasks.py
- src/copy_that/interfaces/api/main.py
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Project Implementation Plan & Integration Roadmap

### Sources
- `docs/planning/PROJECT_IMPLEMENTATION_PLAN_AND_INTEGRATION_ROADMAP.md`

### Summary
**Generated:** November 22, 2025 **Repository:** joshband/copy-that **Current Version:** v0.4.0 **Target Developer:** Solo developer with AI assistance

**Philosophy:** Ship product value first, infrastructure second. The best roadmap is one you can actually complete.

### Key Points
- **Weeks 0-1:** Preparation and branch cleanup
- **Weeks 2-4:** Spacing token implementation (core product value)
- **Weeks 5-6:** Documentation consolidation + v0.5.0 release
- **Weeks 7-8:** Security branch review and staging deployment
- JWT authentication with bcrypt password hashing
- Rate limiting infrastructure
- Database performance indexes
- Security headers middleware
- Authorization framework (RBAC)
- src/copy_that/infrastructure/security/authentication.py (177 lines)

### Implementation Pointers
- `alembic downgrade`
- `deploy/terraform/`
- `frontend/backend`
- `make integration`
- `src/copy_that/`
- `src/copy_that/application/`
- `src/copy_that/constants.py`
- `src/copy_that/domain/`
- `src/copy_that/generators/`
- `src/copy_that/infrastructure/cache/redis_cache.py`
- `src/copy_that/infrastructure/security/authentication.py`
- `src/copy_that/infrastructure/security/rate_limiter.py`
- `src/copy_that/interfaces/api/`
- `src/copy_that/interfaces/api/auth.py`
- `src/copy_that/interfaces/api/main.py`
- `src/copy_that/interfaces/api/sessions.py`

### Build / Refactor Issues
#### **Weeks 0-1:** Preparation and branch cleanup

**Context**
Source: `docs/planning/PROJECT_IMPLEMENTATION_PLAN_AND_INTEGRATION_ROADMAP.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Weeks 0-1:** Preparation and branch cleanup
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- alembic downgrade
- deploy/terraform/
- frontend/backend
- make integration
- src/copy_that/
- src/copy_that/application/
- src/copy_that/constants.py
- src/copy_that/domain/
- src/copy_that/generators/
- src/copy_that/infrastructure/cache/redis_cache.py
- …(+6 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **Weeks 2-4:** Spacing token implementation

**Context**
Source: `docs/planning/PROJECT_IMPLEMENTATION_PLAN_AND_INTEGRATION_ROADMAP.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Weeks 2-4:** Spacing token implementation
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- alembic downgrade
- deploy/terraform/
- frontend/backend
- make integration
- src/copy_that/
- src/copy_that/application/
- src/copy_that/constants.py
- src/copy_that/domain/
- src/copy_that/generators/
- src/copy_that/infrastructure/cache/redis_cache.py
- …(+6 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **Weeks 5-6:** Documentation consolidation + v0.5.0 release

**Context**
Source: `docs/planning/PROJECT_IMPLEMENTATION_PLAN_AND_INTEGRATION_ROADMAP.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Weeks 5-6:** Documentation consolidation + v0.5.0 release
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- alembic downgrade
- deploy/terraform/
- frontend/backend
- make integration
- src/copy_that/
- src/copy_that/application/
- src/copy_that/constants.py
- src/copy_that/domain/
- src/copy_that/generators/
- src/copy_that/infrastructure/cache/redis_cache.py
- …(+6 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **Weeks 7-8:** Security branch review and staging deployment

**Context**
Source: `docs/planning/PROJECT_IMPLEMENTATION_PLAN_AND_INTEGRATION_ROADMAP.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Weeks 7-8:** Security branch review and staging deployment
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- alembic downgrade
- deploy/terraform/
- frontend/backend
- make integration
- src/copy_that/
- src/copy_that/application/
- src/copy_that/constants.py
- src/copy_that/domain/
- src/copy_that/generators/
- src/copy_that/infrastructure/cache/redis_cache.py
- …(+6 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Repository Guidelines

### Sources
- `docs/guides/AGENTS.md`

### Summary
_No narrative prose found; see Key Points._

### Key Points
- src/copy_that/ hosts the FastAPI backend (interfaces/api, domain, services, generators, infrastructure); entrypoint is src/copy_that/interfaces/api/main.py.
- Extraction pipelines live in src/pipeline/, src/core/, src/cv_pipeline/, src/layout/, and src/typography/; tests mirror these areas under tests/<area>/.
- frontend/ is the React + Vite app served by the root Vite config (build output in dist/).
- Migrations are under alembic/; deployment and infra helpers live in deploy/ and terraform/; docs sit in docs/; utility scripts in scripts/.
- Bootstrap: python -m venv .venv && source .venv/bin/activate, then make install (uv editable install + pre-commit) or uv pip install -e ".[dev]".
- API: python -m uvicorn src.copy_that.interfaces.api.main:app --reload --host 0.0.0.0 --port 8000; database setup with alembic upgrade head.
- Frontend: pnpm install at repo root, pnpm dev for local dev (proxies /api to http://localhost:8000), pnpm build and pnpm preview to verify production output.
- Containers: make docker-build for dev image, docker compose up -d for services.
- Python uses Ruff for lint/format (make lint, make format), 4-space indent, 100-char lines, strict typing via MyPy (make type-check or mypy src/). Use snake_case for modules/functions, PascalCase for classes, and keep public functions typed.
- Tests are test_*.py; shared fixtures live in tests/fixtures/.

### Implementation Pointers
- `alembic revision`
- `alembic upgrade`
- `deploy/validate-env.sh`
- `frontend/src/components`
- `frontend/src/store`
- `make check`
- `make docker-build`
- `make format`
- `make install`
- `make lint`
- `make test-a11y`
- `make test-all`
- `make test-cov`
- `make test-e2e`
- `make test-fast`
- `make test-int`
- `make test-load`
- `make test-unit`
- `make test-visual`
- `make type-check`
- `pnpm build`
- `pnpm dev`
- `pnpm install`
- `pnpm preview`
- `pnpm test`
- `src/copy_that/`
- `src/copy_that/interfaces/api/main.py`
- `src/core/`
- `src/cv_pipeline/`
- `src/layout/`
- `src/pipeline/`
- `src/typography/`

### Build / Refactor Issues
#### src/copy_that/ hosts the FastAPI backend ; entrypoint is src/copy_that/interfaces/api/m…

**Context**
Source: `docs/guides/AGENTS.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: src/copy_that/ hosts the FastAPI backend ; entrypoint is src/copy_that/interfaces/api/m…
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- alembic revision
- alembic upgrade
- deploy/validate-env.sh
- frontend/src/components
- frontend/src/store
- make check
- make docker-build
- make format
- make install
- make lint
- …(+22 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Extraction pipelines live in src/pipeline/, src/core/, src/cv_pipeline/, src/layout/, a…

**Context**
Source: `docs/guides/AGENTS.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Extraction pipelines live in src/pipeline/, src/core/, src/cv_pipeline/, src/layout/, a…
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- alembic revision
- alembic upgrade
- deploy/validate-env.sh
- frontend/src/components
- frontend/src/store
- make check
- make docker-build
- make format
- make install
- make lint
- …(+22 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### frontend/ is the React + Vite app served by the root Vite config

**Context**
Source: `docs/guides/AGENTS.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: frontend/ is the React + Vite app served by the root Vite config
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- alembic revision
- alembic upgrade
- deploy/validate-env.sh
- frontend/src/components
- frontend/src/store
- make check
- make docker-build
- make format
- make install
- make lint
- …(+22 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Migrations are under alembic/; deployment and infra helpers live in deploy/ and terrafo…

**Context**
Source: `docs/guides/AGENTS.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Migrations are under alembic/; deployment and infra helpers live in deploy/ and terrafo…
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- alembic revision
- alembic upgrade
- deploy/validate-env.sh
- frontend/src/components
- frontend/src/store
- make check
- make docker-build
- make format
- make install
- make lint
- …(+22 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Reusable Claude Code Prompt for New Token Types

### Sources
- `docs/planning/token-pipeline-planning/REUSABLE_TOKEN_PROMPT.md`

### Summary
**Version:** 1.0 | **Date:** 2025-11-22 | **Purpose:** Template for creating new token pipelines

Use this prompt with Claude Code (web or CLI) to generate complete planning documentation and reference implementation for new token types like typography, shadow, border, artistic style, depth, etc.

### Key Points
- Copy the prompt below
- Replace [TOKEN_TYPE] with your token type (e.g., "typography", "shadow", "border")
- Fill in the [CUSTOMIZATION] sections
- Paste into Claude Code web or CLI
- Claude will generate complete planning documentation
- A working **color token pipeline** with AI extraction, aggregation, and export
- A planned **spacing token pipeline** (see reference docs below)
- A **token factory abstraction** for creating new token types
- font_weight: int (100-900)
- letter_spacing: float

### Implementation Pointers
_No explicit code touchpoints referenced in doc._

### Build / Refactor Issues
#### Copy the prompt below

**Context**
Source: `docs/planning/token-pipeline-planning/REUSABLE_TOKEN_PROMPT.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Copy the prompt below
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Replace [TOKEN_TYPE] with your token type

**Context**
Source: `docs/planning/token-pipeline-planning/REUSABLE_TOKEN_PROMPT.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Replace [TOKEN_TYPE] with your token type
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Fill in the [CUSTOMIZATION] sections

**Context**
Source: `docs/planning/token-pipeline-planning/REUSABLE_TOKEN_PROMPT.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Fill in the [CUSTOMIZATION] sections
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Paste into Claude Code web or CLI

**Context**
Source: `docs/planning/token-pipeline-planning/REUSABLE_TOKEN_PROMPT.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Paste into Claude Code web or CLI
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Shadow Extraction Roadmap & Implementation Plan

### Sources
- `docs/planning/SHADOW_EXTRACTION_ROADMAP.md`
- `docs/shadow/ROADMAP.md`

### Summary
**Status:** Planning Phase **Version:** 1.0 **Last Updated:** 2025-12-06 **Target:** Production-grade shadow token extraction with multi-pass physics-aware pipeline

This roadmap defines a 6-phase implementation strategy to evolve shadow extraction from basic CV + AI to a sophisticated multi-pass pipeline that produces physically meaningful, style-aware shadow tokens. The strategy layersFour production-grade techniques: classical CV (fast, explainable), deep learning (accurate masks), intrinsic decomposition (physics-aware), and geometry validation (consistency checking).

### Key Points
- Basic CV shadow extractor (edge detection + morphology)
- AI extractor (Claude Sonnet 4.5 vision)
- Database persistence (ShadowToken ORM)
- API endpoints (extract, list, get, update, delete)
- Frontend display components
- CV-only relies on edge detection (misses soft shadows, artistic shadows)
- No intrinsic decomposition (can't separate shadow strength from material color)
- No geometry validation (can't detect physically impossible shadows)
- No style classification (can't distinguish "cinematic" vs "studio" lighting)
- Single-pass extraction (no refinement across multiple techniques)

### Implementation Pointers
- `src/copy_that/application/ai_shadow_extractor.py`
- `src/copy_that/application/cv_shadow_extractor.py`
- `src/copy_that/shadowlab/classical_enhanced`
- `src/copy_that/shadowlab/classical_enhanced.py`
- `src/copy_that/shadowlab/deep_shadow_detector.py`
- `src/copy_that/shadowlab/depth_and_normals.py`
- `src/copy_that/shadowlab/illumination_invariants.py`
- `src/copy_that/shadowlab/intrinsic_decomposition.py`
- `src/copy_that/shadowlab/inverse_rendering.py`
- `src/copy_that/shadowlab/pipeline.py`
- `src/copy_that/shadowlab/shadow_style.py`

### Build / Refactor Issues
#### Basic CV shadow extractor

**Context**
Source: `docs/planning/SHADOW_EXTRACTION_ROADMAP.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Basic CV shadow extractor
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- src/copy_that/application/ai_shadow_extractor.py
- src/copy_that/application/cv_shadow_extractor.py
- src/copy_that/shadowlab/classical_enhanced
- src/copy_that/shadowlab/classical_enhanced.py
- src/copy_that/shadowlab/deep_shadow_detector.py
- src/copy_that/shadowlab/depth_and_normals.py
- src/copy_that/shadowlab/illumination_invariants.py
- src/copy_that/shadowlab/intrinsic_decomposition.py
- src/copy_that/shadowlab/inverse_rendering.py
- src/copy_that/shadowlab/shadow_style.py
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### AI extractor

**Context**
Source: `docs/planning/SHADOW_EXTRACTION_ROADMAP.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: AI extractor
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- src/copy_that/application/ai_shadow_extractor.py
- src/copy_that/application/cv_shadow_extractor.py
- src/copy_that/shadowlab/classical_enhanced
- src/copy_that/shadowlab/classical_enhanced.py
- src/copy_that/shadowlab/deep_shadow_detector.py
- src/copy_that/shadowlab/depth_and_normals.py
- src/copy_that/shadowlab/illumination_invariants.py
- src/copy_that/shadowlab/intrinsic_decomposition.py
- src/copy_that/shadowlab/inverse_rendering.py
- src/copy_that/shadowlab/shadow_style.py
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Database persistence

**Context**
Source: `docs/planning/SHADOW_EXTRACTION_ROADMAP.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Database persistence
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- src/copy_that/application/ai_shadow_extractor.py
- src/copy_that/application/cv_shadow_extractor.py
- src/copy_that/shadowlab/classical_enhanced
- src/copy_that/shadowlab/classical_enhanced.py
- src/copy_that/shadowlab/deep_shadow_detector.py
- src/copy_that/shadowlab/depth_and_normals.py
- src/copy_that/shadowlab/illumination_invariants.py
- src/copy_that/shadowlab/intrinsic_decomposition.py
- src/copy_that/shadowlab/inverse_rendering.py
- src/copy_that/shadowlab/shadow_style.py
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### API endpoints

**Context**
Source: `docs/planning/SHADOW_EXTRACTION_ROADMAP.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: API endpoints
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- src/copy_that/application/ai_shadow_extractor.py
- src/copy_that/application/cv_shadow_extractor.py
- src/copy_that/shadowlab/classical_enhanced
- src/copy_that/shadowlab/classical_enhanced.py
- src/copy_that/shadowlab/deep_shadow_detector.py
- src/copy_that/shadowlab/depth_and_normals.py
- src/copy_that/shadowlab/illumination_invariants.py
- src/copy_that/shadowlab/intrinsic_decomposition.py
- src/copy_that/shadowlab/inverse_rendering.py
- src/copy_that/shadowlab/shadow_style.py
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Shadow Pipeline Upgrade: Visual Comparison Guide

### Sources
- `docs/shadow/UPGRADE_GUIDE.md`

### Summary
**Date:** December 6, 2025 **Status:** Phase 2 - Model Upgrades Complete **Version:** 2.0

This document showcases the **transformation of the shadow extraction pipeline** from placeholder implementations to **production-grade deep learning models**. Each stage demonstrates the quality improvements and new capabilities unlocked by the upgraded models.

### Key Points
- Zero correlation with actual shadows
- Unsuitable for any real application
- Trained on 10,000+ labeled images
- Bi-directional attention for context
- 90%+ F1 score on benchmark datasets
- Handles soft shadows, cast shadows, and artistic shadows
- No spatial consistency
- Violates physical laws (no surface continuity)
- Cannot be used for geometry validation
- Useless for lighting estimation

### Implementation Pointers
_No explicit code touchpoints referenced in doc._

### Build / Refactor Issues
#### Zero correlation with actual shadows

**Context**
Source: `docs/shadow/UPGRADE_GUIDE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Zero correlation with actual shadows
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Unsuitable for any real application

**Context**
Source: `docs/shadow/UPGRADE_GUIDE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Unsuitable for any real application
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Trained on 10,000+ labeled images

**Context**
Source: `docs/shadow/UPGRADE_GUIDE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Trained on 10,000+ labeled images
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Bi-directional attention for context

**Context**
Source: `docs/shadow/UPGRADE_GUIDE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Bi-directional attention for context
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

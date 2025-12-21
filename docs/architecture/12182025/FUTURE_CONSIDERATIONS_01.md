# Future Considerations

## **SHADOW_PIPELINE_SPEC.md**

### Sources
- `docs/shadow/SPEC.md`

### Summary
This document defines a full shadow-extraction system designed for **Midjourney-style AI-generated images**, including:

### Key Points
- A multi-stage **algorithmic pipeline**
- A consistent **visualization architecture**
- A clear, semi-technical **narrative** for each stage
- Formal **data schemas** for interoperability
- Recommended **libraries, models, and open-source tools**
- Hooks for a future **dataset + evaluation harness**
- Intermediate structured artifacts
- Visualization-ready layers
- A consolidated **ShadowTokenSet** suitable for downstream systems (design token extraction, style analysis, relighting agents, etc.)
- **Input & Preprocessing**

### Implementation Pointers
- `make geometric`
- `make the`

### Build / Refactor Issues
#### A multi-stage **algorithmic pipeline**

**Context**
Source: `docs/shadow/SPEC.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: A multi-stage **algorithmic pipeline**
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- make geometric
- make the
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### A consistent **visualization architecture**

**Context**
Source: `docs/shadow/SPEC.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: A consistent **visualization architecture**
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- make geometric
- make the
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### A clear, semi-technical **narrative** for each stage

**Context**
Source: `docs/shadow/SPEC.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: A clear, semi-technical **narrative** for each stage
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- make geometric
- make the
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Formal **data schemas** for interoperability

**Context**
Source: `docs/shadow/SPEC.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Formal **data schemas** for interoperability
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- make geometric
- make the
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## API Docs

### Sources
- `docs/api/README.md`

### Summary
_No narrative prose found; see Key Points._

### Key Points
- APIs served by codebase (FastAPI): see backend routes in src/copy_that/interfaces/api/main.py
- API reference: use Swagger/Redoc at runtime
- curl examples and validation: see testing/manual_e2e_testing_guide.md (root)
- Legacy API testing strategies: see archive/pipeline/historical/ if needed

### Implementation Pointers
- `src/copy_that/interfaces/api/main.py`

### Build / Refactor Issues
#### APIs served by codebase : see backend routes in src/copy_that/interfaces/api/main.py

**Context**
Source: `docs/api/README.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: APIs served by codebase : see backend routes in src/copy_that/interfaces/api/main.py
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- src/copy_that/interfaces/api/main.py
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### API reference: use Swagger/Redoc at runtime

**Context**
Source: `docs/api/README.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: API reference: use Swagger/Redoc at runtime
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- src/copy_that/interfaces/api/main.py
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### curl examples and validation: see testing/manual_e2e_testing_guide.md

**Context**
Source: `docs/api/README.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: curl examples and validation: see testing/manual_e2e_testing_guide.md
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- src/copy_that/interfaces/api/main.py
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Legacy API testing strategies: see archive/pipeline/historical/ if needed

**Context**
Source: `docs/api/README.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Legacy API testing strategies: see archive/pipeline/historical/ if needed
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- src/copy_that/interfaces/api/main.py
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## API Examples (curl)

### Sources
- `docs/examples/api_curl.md`

### Summary
_No narrative prose found; see Key Points._

### Key Points
- Base URL: http://localhost:8000
- Content-Type: application/json
- No auth required (add Authorization: Bearer ... if you introduce auth later).

### Implementation Pointers
- `/api/v1/colors`
- `/api/v1/colors/1`
- `/api/v1/colors/extract`
- `/api/v1/projects`
- `/api/v1/projects/1/colors`
- `/api/v1/sessions`
- `/api/v1/sessions/1/extract`
- `/api/v1/sessions/1/library`
- `/api/v1/sessions/1/library/curate`
- `/api/v1/sessions/1/library/export`

### Build / Refactor Issues
#### Base URL: http://localhost:8000

**Context**
Source: `docs/examples/api_curl.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Base URL: http://localhost:8000
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/colors
- /api/v1/colors/1
- /api/v1/colors/extract
- /api/v1/projects
- /api/v1/projects/1/colors
- /api/v1/sessions
- /api/v1/sessions/1/extract
- /api/v1/sessions/1/library
- /api/v1/sessions/1/library/curate
- /api/v1/sessions/1/library/export
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Content-Type: application/json

**Context**
Source: `docs/examples/api_curl.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Content-Type: application/json
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/colors
- /api/v1/colors/1
- /api/v1/colors/extract
- /api/v1/projects
- /api/v1/projects/1/colors
- /api/v1/sessions
- /api/v1/sessions/1/extract
- /api/v1/sessions/1/library
- /api/v1/sessions/1/library/curate
- /api/v1/sessions/1/library/export
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### No auth required

**Context**
Source: `docs/examples/api_curl.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: No auth required
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/colors
- /api/v1/colors/1
- /api/v1/colors/extract
- /api/v1/projects
- /api/v1/projects/1/colors
- /api/v1/sessions
- /api/v1/sessions/1/extract
- /api/v1/sessions/1/library
- /api/v1/sessions/1/library/curate
- /api/v1/sessions/1/library/export
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Batch Extraction Example

### Sources
- `docs/examples/batch_extraction.md`

### Summary
Minimal end-to-end example using `BatchColorExtractor` and the session endpoints.

### Key Points
- Concurrency limit: 3 (default) — adjust in code if needed.
- Deduplication: Delta-E threshold default 2.0 (JND); lower = stricter, higher = more merging.
- Provenance: Each aggregated token tracks source images and confidences; persisted to color_tokens.provenance.
- Persistence: Tokens are stored with library_id and project_id for audit/export.

### Implementation Pointers
- `/api/v1/sessions`
- `/api/v1/sessions/1/extract`
- `/api/v1/sessions/1/library`
- `/api/v1/sessions/1/library/export`

### Build / Refactor Issues
#### Concurrency limit: 3  — adjust in code if needed

**Context**
Source: `docs/examples/batch_extraction.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Concurrency limit: 3  — adjust in code if needed
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/sessions
- /api/v1/sessions/1/extract
- /api/v1/sessions/1/library
- /api/v1/sessions/1/library/export
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Deduplication: Delta-E threshold default 2.0 ; lower = stricter, higher = more merging

**Context**
Source: `docs/examples/batch_extraction.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Deduplication: Delta-E threshold default 2.0 ; lower = stricter, higher = more merging
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/sessions
- /api/v1/sessions/1/extract
- /api/v1/sessions/1/library
- /api/v1/sessions/1/library/export
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Provenance: Each aggregated token tracks source images and confidences; persisted to co…

**Context**
Source: `docs/examples/batch_extraction.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Provenance: Each aggregated token tracks source images and confidences; persisted to co…
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/sessions
- /api/v1/sessions/1/extract
- /api/v1/sessions/1/library
- /api/v1/sessions/1/library/export
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Persistence: Tokens are stored with library_id and project_id for audit/export

**Context**
Source: `docs/examples/batch_extraction.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Persistence: Tokens are stored with library_id and project_id for audit/export
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/sessions
- /api/v1/sessions/1/extract
- /api/v1/sessions/1/library
- /api/v1/sessions/1/library/export
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Deployment Guide

### Sources
- `docs/setup/deployment.md`

### Summary
Complete guide for deploying Copy That to Google Cloud Platform.

Copy That uses a modern cloud-native architecture deployed on GCP:

Required variables in `terraform.tfvars`:

### Key Points
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Initial Setup](#initial-setup)
- [Infrastructure Provisioning](#infrastructure-provisioning)
- [CI/CD Configuration](#cicd-configuration)
- [Manual Deployment](#manual-deployment)
- [Post-Deployment](#post-deployment)
- [Troubleshooting](#troubleshooting)
- **Cloud Run**: Serverless container platform
- **Cloud SQL**: Managed PostgreSQL database

### Implementation Pointers
- `alembic downgrade`
- `deploy/terraform`
- `deploy/terraform/terraform.tfvars`

### Build / Refactor Issues
#### [Overview]

**Context**
Source: `docs/setup/deployment.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: [Overview]
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- alembic downgrade
- deploy/terraform
- deploy/terraform/terraform.tfvars
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### [Prerequisites]

**Context**
Source: `docs/setup/deployment.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: [Prerequisites]
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- alembic downgrade
- deploy/terraform
- deploy/terraform/terraform.tfvars
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### [Initial Setup]

**Context**
Source: `docs/setup/deployment.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: [Initial Setup]
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- alembic downgrade
- deploy/terraform
- deploy/terraform/terraform.tfvars
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### [Infrastructure Provisioning]

**Context**
Source: `docs/setup/deployment.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: [Infrastructure Provisioning]
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- alembic downgrade
- deploy/terraform
- deploy/terraform/terraform.tfvars
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Design Docs

### Sources
- `docs/design/README.md`

### Summary
Active design references (date-prefixed):

### Key Points
- 2025-11-20_state_management_schema_complete.md — Zustand store + schema foundation
- 2025-11-20_component_wrapper_progress.md — Wrapper components in progress
- 2025-11-20_token_explorer_complete.md — Token Explorer UI completion
- educational_layout_implementation.md — Educational layout reference
- existing_components_assessment.md — Component inventory
- react_architecture.md — Frontend architecture notes
- token_explorer_vision.md — Token explorer vision
- transition_document.md — Transition notes

### Implementation Pointers
_No explicit code touchpoints referenced in doc._

### Build / Refactor Issues
#### 2025-11-20_state_management_schema_complete.md — Zustand store + schema foundation

**Context**
Source: `docs/design/README.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: 2025-11-20_state_management_schema_complete.md — Zustand store + schema foundation
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### 2025-11-20_component_wrapper_progress.md — Wrapper components in progress

**Context**
Source: `docs/design/README.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: 2025-11-20_component_wrapper_progress.md — Wrapper components in progress
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### 2025-11-20_token_explorer_complete.md — Token Explorer UI completion

**Context**
Source: `docs/design/README.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: 2025-11-20_token_explorer_complete.md — Token Explorer UI completion
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### educational_layout_implementation.md — Educational layout reference

**Context**
Source: `docs/design/README.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: educational_layout_implementation.md — Educational layout reference
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Educational Frontend Design for Engineers & Designers

### Sources
- `docs/EDUCATIONAL_FRONTEND_DESIGN.md`

### Summary
Copy This is not just a tool—it's an **interactive classroom** for understanding color science, image processing, and AI-driven token extraction.

**Audience:** Software engineers, UX designers, product designers, design systems architects, color science researchers

**Goal:** Make algorithms visible, understandable, and explorable

### Key Points
- Click any metric to see algorithm explanation
- Links to academic papers and standards
- Toggle between "Simplified" and "Technical" views
- Claude Vision: 2100ms (API latency)
- K-means clustering: 85ms
- Delta-E calculations: 12ms
- Harmony analysis: 3ms
- WCAG 2.1 Contrast (W3C)
- CIEDE2000 Color Difference (CIE)
- Color Harmony Theory (Itten, 1961)

### Implementation Pointers
_No explicit code touchpoints referenced in doc._

### Build / Refactor Issues
#### Click any metric to see algorithm explanation

**Context**
Source: `docs/EDUCATIONAL_FRONTEND_DESIGN.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Click any metric to see algorithm explanation
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Links to academic papers and standards

**Context**
Source: `docs/EDUCATIONAL_FRONTEND_DESIGN.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Links to academic papers and standards
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Toggle between "Simplified" and "Technical" views

**Context**
Source: `docs/EDUCATIONAL_FRONTEND_DESIGN.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Toggle between "Simplified" and "Technical" views
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Claude Vision: 2100ms

**Context**
Source: `docs/EDUCATIONAL_FRONTEND_DESIGN.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Claude Vision: 2100ms
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Environment Variables Configuration

### Sources
- `docs/ENVIRONMENT_VARIABLES.md`

### Summary
This document describes all environment variables required for the Copy That platform across different deployment environments.

| Variable | Description | Required | Default | Example | |----------|-------------|----------|---------|---------| | `SECRET_KEY` | JWT signing key (min 32 chars) | **Yes** | None | `your-super-secret-key-min-32-chars` | | `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime | No | `30` | `15` | | `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime | No | `7` | `30` |

| Variable | Description | Required | Default | Example | |----------|-------------|----------|---------|---------| | `DATABASE_URL` | PostgreSQL connection string | **Yes** | None | `postgresql+asyncpg://user:pass@host/db` |

### Key Points
- SECRET_KEY - JWT signing key
- DATABASE_URL - PostgreSQL connection string
- REDIS_URL - Redis connection string (optional)
- ANTHROPIC_API_KEY - Claude API key
- GCP_PROJECT_ID - Google Cloud project ID
- GCP_SA_KEY - Service account JSON (base64 encoded)
- **Authentication**: Raise startup error if SECRET_KEY is missing
- **Database**: Raise startup error if DATABASE_URL is missing
- **Redis**: Log warning and disable caching/rate limiting if REDIS_URL is missing
- **AI/ML**: Raise error on API call if ANTHROPIC_API_KEY is missing

### Implementation Pointers
_No explicit code touchpoints referenced in doc._

### Build / Refactor Issues
#### SECRET_KEY - JWT signing key

**Context**
Source: `docs/ENVIRONMENT_VARIABLES.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: SECRET_KEY - JWT signing key
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### DATABASE_URL - PostgreSQL connection string

**Context**
Source: `docs/ENVIRONMENT_VARIABLES.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: DATABASE_URL - PostgreSQL connection string
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### REDIS_URL - Redis connection string

**Context**
Source: `docs/ENVIRONMENT_VARIABLES.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: REDIS_URL - Redis connection string
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### ANTHROPIC_API_KEY - Claude API key

**Context**
Source: `docs/ENVIRONMENT_VARIABLES.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: ANTHROPIC_API_KEY - Claude API key
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Export Formats Example

### Sources
- `docs/examples/export_formats.md`

### Summary
Examples of content returned by `/api/v1/sessions/{session_id}/library/export?format=...`.

### Key Points
- Formats supported: w3c, css, react, html.
- For non-color tokens (future), extend generator logic in src/copy_that/generators/*.

### Implementation Pointers
- `/api/v1/sessions/`
- `src/copy_that/generators/`

### Build / Refactor Issues
#### Formats supported: w3c, css, react, html

**Context**
Source: `docs/examples/export_formats.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Formats supported: w3c, css, react, html
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/sessions/
- src/copy_that/generators/
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### For non-color tokens , extend generator logic in src/copy_that/generators/*

**Context**
Source: `docs/examples/export_formats.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: For non-color tokens , extend generator logic in src/copy_that/generators/*
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/sessions/
- src/copy_that/generators/
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Launch Docs

### Sources
- `docs/launch/README.md`

### Summary
_No narrative prose found; see Key Points._

### Key Points
- launch_checklist.md — Production launch checklist
- setup/production_deployment_guide.md — Deployment guide (root)
- ops/cost_optimization.md — Cost controls

### Implementation Pointers
_No explicit code touchpoints referenced in doc._

### Build / Refactor Issues
#### launch_checklist.md — Production launch checklist

**Context**
Source: `docs/launch/README.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: launch_checklist.md — Production launch checklist
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### setup/production_deployment_guide.md — Deployment guide

**Context**
Source: `docs/launch/README.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: setup/production_deployment_guide.md — Deployment guide
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### ops/cost_optimization.md — Cost controls

**Context**
Source: `docs/launch/README.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: ops/cost_optimization.md — Cost controls
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Multimodal Component Architecture - Design Token Agnostic

### Sources
- `docs/architecture/MULTIMODAL_COMPONENT_ARCHITECTURE.md`

### Summary
**Date:** 2025-12-09 **Context:** Architecture must support visual (color, spacing) + future (audio, video, motion) tokens **Principle:** Token-type agnostic components where possible

### Key Points
- **60% of "color" components** are actually **generic token displays** (DetailView, Graph, Table, Grid)
- **40% are truly color-specific** (Harmony, Accessibility, Swatches)
- Color (hex, rgb, oklch) - ✅ Implemented
- Spacing (px, rem, multiplier) - ✅ Implemented
- Typography (fontFamily, fontSize, lineHeight) - ✅ Implemented
- Shadow (offsetX, offsetY, blur, color) - 🔄 Partial
- Frequency (hz, note, octave)
- Duration (ms, beats, tempo)
- Amplitude (db, velocity)
- Timbre (waveform, harmonics)

### Implementation Pointers
_No explicit code touchpoints referenced in doc._

### Build / Refactor Issues
#### **60% of "color" components** are actually **generic token displays**

**Context**
Source: `docs/architecture/MULTIMODAL_COMPONENT_ARCHITECTURE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **60% of "color" components** are actually **generic token displays**
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **40% are truly color-specific**

**Context**
Source: `docs/architecture/MULTIMODAL_COMPONENT_ARCHITECTURE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **40% are truly color-specific**
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Color  - ✅ Implemented

**Context**
Source: `docs/architecture/MULTIMODAL_COMPONENT_ARCHITECTURE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Color  - ✅ Implemented
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Spacing  - ✅ Implemented

**Context**
Source: `docs/architecture/MULTIMODAL_COMPONENT_ARCHITECTURE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Spacing  - ✅ Implemented
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Operations Runbook

### Sources
- `docs/ops/runbook.md`

### Summary
_No narrative prose found; see Key Points._

### Key Points
- **Preflight**: pnpm test (frontend), python -m pytest (backend), lint/type-check if configured.
- **Migrations**: alembic upgrade head (staging), verify DB health.
- **Build & push**: Build image (if using Docker) and push to registry.
- **Apply infra**: terraform apply (if infra changes) or deploy via pipeline.
- **Smoke**: Hit /api/v1/health, /api/v1/docs, load frontend, run a sample extract.
- **App**: Roll back to previous image/version.
- **DB**: If needed, alembic downgrade -1 (only if safe). Prefer forward fixes over DB downgrades.
- **Verify**: Health + smoke checks; restore traffic.
- Author in alembic/versions/.
- Apply: alembic upgrade head.

### Implementation Pointers
- `/api/v1/docs`
- `/api/v1/health`
- `alembic downgrade`
- `alembic upgrade`
- `pnpm test`

### Build / Refactor Issues
#### **Preflight**: pnpm test , python -m pytest , lint/type-check if configured

**Context**
Source: `docs/ops/runbook.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Preflight**: pnpm test , python -m pytest , lint/type-check if configured
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/docs
- /api/v1/health
- alembic downgrade
- alembic upgrade
- pnpm test
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **Migrations**: alembic upgrade head , verify DB health

**Context**
Source: `docs/ops/runbook.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Migrations**: alembic upgrade head , verify DB health
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/docs
- /api/v1/health
- alembic downgrade
- alembic upgrade
- pnpm test
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **Build & push**: Build image  and push to registry

**Context**
Source: `docs/ops/runbook.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Build & push**: Build image  and push to registry
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/docs
- /api/v1/health
- alembic downgrade
- alembic upgrade
- pnpm test
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **Apply infra**: terraform apply  or deploy via pipeline

**Context**
Source: `docs/ops/runbook.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Apply infra**: terraform apply  or deploy via pipeline
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/docs
- /api/v1/health
- alembic downgrade
- alembic upgrade
- pnpm test
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## React Frontend Architecture: Token Explorer

### Sources
- `docs/design/REACT_ARCHITECTURE.md`

### Summary
**Status:** Design Phase Complete, Implementation Ready **Date:** 2025-11-20 **Version:** v0.1.0 (Architecture Plan)

Generic, schema-driven React frontend for Token Explorer. Works for:

### Key Points
- **Color Tokens** (reference implementation)
- **Future:** Typography, Spacing, Shadow, Animation tokens
- **Goal:** 80% code reuse across token types
- [ ] Setup Zustand store + useTokens hooks
- [ ] Create tokenTypeRegistry (schema-driven config)
- [ ] Build generic TokenCard, TokenGrid, Toolbar
- [ ] Implement React Query integration
- [ ] Build ColorTokenVisual component
- [ ] Build format tabs (RGB, HSL, Oklch)
- [ ] Build Inspector sidebar

### Implementation Pointers
- `src/api/tokenApi.ts`
- `src/components/`
- `src/components/tokens/TokenGrid.tsx`
- `src/components/tokens/__tests__/TokenCard.test.tsx`
- `src/hooks/useExtractionProgress.ts`
- `src/types/generated/color.zod.ts`

### Build / Refactor Issues
#### **Color Tokens**

**Context**
Source: `docs/design/REACT_ARCHITECTURE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Color Tokens**
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- src/api/tokenApi.ts
- src/components/
- src/components/tokens/TokenGrid.tsx
- src/components/tokens/__tests__/TokenCard.test.tsx
- src/hooks/useExtractionProgress.ts
- src/types/generated/color.zod.ts
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **Future:** Typography, Spacing, Shadow, Animation tokens

**Context**
Source: `docs/design/REACT_ARCHITECTURE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Future:** Typography, Spacing, Shadow, Animation tokens
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- src/api/tokenApi.ts
- src/components/
- src/components/tokens/TokenGrid.tsx
- src/components/tokens/__tests__/TokenCard.test.tsx
- src/hooks/useExtractionProgress.ts
- src/types/generated/color.zod.ts
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **Goal:** 80% code reuse across token types

**Context**
Source: `docs/design/REACT_ARCHITECTURE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Goal:** 80% code reuse across token types
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- src/api/tokenApi.ts
- src/components/
- src/components/tokens/TokenGrid.tsx
- src/components/tokens/__tests__/TokenCard.test.tsx
- src/hooks/useExtractionProgress.ts
- src/types/generated/color.zod.ts
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### [ ] Setup Zustand store + useTokens hooks

**Context**
Source: `docs/design/REACT_ARCHITECTURE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: [ ] Setup Zustand store + useTokens hooks
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- src/api/tokenApi.ts
- src/components/
- src/components/tokens/TokenGrid.tsx
- src/components/tokens/__tests__/TokenCard.test.tsx
- src/hooks/useExtractionProgress.ts
- src/types/generated/color.zod.ts
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Schema Architecture Diagrams

### Sources
- `docs/architecture/SCHEMA_ARCHITECTURE_DIAGRAM.md`

### Summary
**Date:** 2025-11-18 **Version:** 2.0 (Revised Architecture with Adapters)

### Key Points
- **[ROADMAP.md](../../ROADMAP.md)** - Phase 4 overview in project roadmap
- **[Phase 4 Revised Implementation Plan](../planning/PHASE_4_REVISED_IMPLEMENTATION_PLAN.md)** - Detailed week-by-week guide
- **[Original Schema Solution](../analysis/STRUCTURED_OUTPUTS_SCHEMA_SOLUTION.md)** - Original analysis
- ✅ Each system has its own schema
- ✅ Adapters translate between schemas
- ✅ Systems evolve independently
- ✅ safeParse() instead of parse()
- ✅ Partial parsing for recoverable errors
- ✅ Fallback UI for missing data
- ✅ Pydantic (Python backend)

### Implementation Pointers
- `/api/v1/extract`
- `/api/v2/extract`

### Build / Refactor Issues
#### **[ROADMAP.md]** - Phase 4 overview in project roadmap

**Context**
Source: `docs/architecture/SCHEMA_ARCHITECTURE_DIAGRAM.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **[ROADMAP.md]** - Phase 4 overview in project roadmap
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/extract
- /api/v2/extract
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **[Phase 4 Revised Implementation Plan]** - Detailed week-by-week guide

**Context**
Source: `docs/architecture/SCHEMA_ARCHITECTURE_DIAGRAM.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **[Phase 4 Revised Implementation Plan]** - Detailed week-by-week guide
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/extract
- /api/v2/extract
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **[Original Schema Solution]** - Original analysis

**Context**
Source: `docs/architecture/SCHEMA_ARCHITECTURE_DIAGRAM.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **[Original Schema Solution]** - Original analysis
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/extract
- /api/v2/extract
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### ✅ Each system has its own schema

**Context**
Source: `docs/architecture/SCHEMA_ARCHITECTURE_DIAGRAM.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: ✅ Each system has its own schema
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/extract
- /api/v2/extract
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Token Explorer: Generic Platform Vision

### Sources
- `docs/design/TOKEN_EXPLORER_VISION.md`

### Summary
**Status:** Phase 4 Week 2 - UI/UX Redesign Complete **Date:** 2025-11-20 **Version:** v0.1.0 (Design System)

**Copy That's Token Explorer** is a unified, schema-driven interface for exploring ANY design token type:

**Key Principle:** Upload 1-10 images → extract tokens → explore comprehensive token details (visual, information, educational, interactive, narrative) in a single unified interface.

### Key Points
- **Color Tokens** (reference implementation, complete)
- **Typography Tokens** (future, same patterns)
- **Spacing Tokens** (future, same patterns)
- **Shadow Tokens** (future, same patterns)
- **Animation Tokens** (future, same patterns)
- Show semantic names before hex codes
- Emphasize meaning: "molten-copper" (not "orange-500")
- Design intent visible: "evokes retro audio warmth"
- Search by meaning, not by value
- Show which extractors contributed

### Implementation Pointers
_No explicit code touchpoints referenced in doc._

### Build / Refactor Issues
#### **Color Tokens**

**Context**
Source: `docs/design/TOKEN_EXPLORER_VISION.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Color Tokens**
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **Typography Tokens**

**Context**
Source: `docs/design/TOKEN_EXPLORER_VISION.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Typography Tokens**
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **Spacing Tokens**

**Context**
Source: `docs/design/TOKEN_EXPLORER_VISION.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Spacing Tokens**
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **Shadow Tokens**

**Context**
Source: `docs/design/TOKEN_EXPLORER_VISION.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Shadow Tokens**
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

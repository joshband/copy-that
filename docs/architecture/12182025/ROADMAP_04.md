# Roadmap

## Spacing Token Pipeline: Comprehensive Implementation Planning

### Sources
- `docs/planning/token-pipeline-planning/SPACING_TOKEN_PIPELINE_PLANNING.md`

### Summary
**Version:** 1.0 | **Date:** 2025-11-22 | **Status:** Planning Document

This document provides a comprehensive implementation plan for the spacing token pipeline, modeled after the proven color token implementation patterns.

### Key Points
- AI-powered spacing extraction using Claude/OpenAI vision
- Parallel asynchronous batch processing
- Real-time SSE streaming for progress updates
- Delta-based deduplication and aggregation
- Multiple export formats (W3C, CSS, React, etc.)
- Image Input (URL/Base64/File)
- AI Spacing Extractor (Claude/OpenAI)
- Sends image to AI vision model
- Receives spacing measurements with context
- Extract spacing values from AI response

### Implementation Pointers
- `/api/v1/spacing/extract`
- `/api/v1/spacing/extract-streaming`
- `alembic import`
- `frontend/src/config/tokenTypeRegistry.tsx`
- `frontend/src/store/tokenStore.ts`
- `src/copy_that/`
- `src/copy_that/application/semantic_spacing_naming.py`
- `src/copy_that/application/spacing_extractor.py`
- `src/copy_that/application/spacing_utils.py`
- `src/copy_that/interfaces/api/spacing.py`

### Build / Refactor Issues
#### AI-powered spacing extraction using Claude/OpenAI vision

**Context**
Source: `docs/planning/token-pipeline-planning/SPACING_TOKEN_PIPELINE_PLANNING.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: AI-powered spacing extraction using Claude/OpenAI vision
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/spacing/extract
- /api/v1/spacing/extract-streaming
- alembic import
- frontend/src/config/tokenTypeRegistry.tsx
- frontend/src/store/tokenStore.ts
- src/copy_that/
- src/copy_that/application/semantic_spacing_naming.py
- src/copy_that/application/spacing_extractor.py
- src/copy_that/application/spacing_utils.py
- src/copy_that/interfaces/api/spacing.py
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Parallel asynchronous batch processing

**Context**
Source: `docs/planning/token-pipeline-planning/SPACING_TOKEN_PIPELINE_PLANNING.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Parallel asynchronous batch processing
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/spacing/extract
- /api/v1/spacing/extract-streaming
- alembic import
- frontend/src/config/tokenTypeRegistry.tsx
- frontend/src/store/tokenStore.ts
- src/copy_that/
- src/copy_that/application/semantic_spacing_naming.py
- src/copy_that/application/spacing_extractor.py
- src/copy_that/application/spacing_utils.py
- src/copy_that/interfaces/api/spacing.py
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Real-time SSE streaming for progress updates

**Context**
Source: `docs/planning/token-pipeline-planning/SPACING_TOKEN_PIPELINE_PLANNING.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Real-time SSE streaming for progress updates
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/spacing/extract
- /api/v1/spacing/extract-streaming
- alembic import
- frontend/src/config/tokenTypeRegistry.tsx
- frontend/src/store/tokenStore.ts
- src/copy_that/
- src/copy_that/application/semantic_spacing_naming.py
- src/copy_that/application/spacing_extractor.py
- src/copy_that/application/spacing_utils.py
- src/copy_that/interfaces/api/spacing.py
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Delta-based deduplication and aggregation

**Context**
Source: `docs/planning/token-pipeline-planning/SPACING_TOKEN_PIPELINE_PLANNING.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Delta-based deduplication and aggregation
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/spacing/extract
- /api/v1/spacing/extract-streaming
- alembic import
- frontend/src/config/tokenTypeRegistry.tsx
- frontend/src/store/tokenStore.ts
- src/copy_that/
- src/copy_that/application/semantic_spacing_naming.py
- src/copy_that/application/spacing_extractor.py
- src/copy_that/application/spacing_utils.py
- src/copy_that/interfaces/api/spacing.py
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Spacing Token Pipeline: SDLC Atomic Tasks

### Sources
- `docs/planning/token-pipeline-planning/SDLC_ATOMIC_TASKS.md`

### Summary
**Version:** 1.0 | **Date:** 2025-11-22 | **Status:** Planning Document

This document contains all atomic tasks required to implement the spacing token pipeline, organized by SDLC phase. Each task is designed to be completed in 2-8 hours.

### Key Points
- **REQ-SPT-XXX**: Requirements & Analysis
- **DES-SPT-XXX**: Design
- **IMPL-SPT-XXX**: Implementation
- **TEST-SPT-XXX**: Testing
- **DEP-SPT-XXX**: Deployment
- **DOC-SPT-XXX**: Documentation
- **REL-SPT-XXX**: Release & Maintenance
- REQ-SPT-008 (Analyze existing patterns)
- DES-SPT-001 (Architecture diagram)
- DES-SPT-011 (Database schema)

### Implementation Pointers
_No explicit code touchpoints referenced in doc._

### Build / Refactor Issues
#### **REQ-SPT-XXX**: Requirements & Analysis

**Context**
Source: `docs/planning/token-pipeline-planning/SDLC_ATOMIC_TASKS.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **REQ-SPT-XXX**: Requirements & Analysis
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **DES-SPT-XXX**: Design

**Context**
Source: `docs/planning/token-pipeline-planning/SDLC_ATOMIC_TASKS.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **DES-SPT-XXX**: Design
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **IMPL-SPT-XXX**: Implementation

**Context**
Source: `docs/planning/token-pipeline-planning/SDLC_ATOMIC_TASKS.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **IMPL-SPT-XXX**: Implementation
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **TEST-SPT-XXX**: Testing

**Context**
Source: `docs/planning/token-pipeline-planning/SDLC_ATOMIC_TASKS.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **TEST-SPT-XXX**: Testing
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Technical Specification: Copy That

### Sources
- `docs/overview/2025-11-21-tech-spec.md`

### Summary
**Version:** 1.0 **Date:** November 20, 2025 **Status:** Phase 4 Complete

### Key Points
- Core: Business logic, strict validation, optional fields
- API: Serialization-friendly, naming conventions, always required
- Frontend: Runtime validation, gradual degradation
- ExtractionError: Base extraction failure
- InvalidImageError: Image format/size issues
- ColorExtractionTimeout: Claude API timeout (>30s)
- DatabaseError: SQLModel query failures
- Use try/except in API handlers
- Catch domain exceptions → HTTP 4xx/5xx
- Log all errors to Sentry

### Implementation Pointers
- `/api/v1/colors/extract`
- `/api/v1/spacing/extract`
- `frontend/src/store/colorStore.ts`
- `frontend/src/types/generated/`
- `src/copy_that/`

### Build / Refactor Issues
#### Core: Business logic, strict validation, optional fields

**Context**
Source: `docs/overview/2025-11-21-tech-spec.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Core: Business logic, strict validation, optional fields
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/colors/extract
- /api/v1/spacing/extract
- frontend/src/store/colorStore.ts
- frontend/src/types/generated/
- src/copy_that/
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### API: Serialization-friendly, naming conventions, always required

**Context**
Source: `docs/overview/2025-11-21-tech-spec.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: API: Serialization-friendly, naming conventions, always required
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/colors/extract
- /api/v1/spacing/extract
- frontend/src/store/colorStore.ts
- frontend/src/types/generated/
- src/copy_that/
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Frontend: Runtime validation, gradual degradation

**Context**
Source: `docs/overview/2025-11-21-tech-spec.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Frontend: Runtime validation, gradual degradation
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/colors/extract
- /api/v1/spacing/extract
- frontend/src/store/colorStore.ts
- frontend/src/types/generated/
- src/copy_that/
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### ExtractionError: Base extraction failure

**Context**
Source: `docs/overview/2025-11-21-tech-spec.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: ExtractionError: Base extraction failure
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/colors/extract
- /api/v1/spacing/extract
- frontend/src/store/colorStore.ts
- frontend/src/types/generated/
- src/copy_that/
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Test Execution Strategy & Memory Optimization

### Sources
- `docs/testing/TEST_EXECUTION_STRATEGY.md`

### Summary
**Purpose:** Guide for running Copy That's test suite efficiently in different contexts **Status:** ✅ PRODUCTION OPTIMIZED **Last Updated:** 2025-12-05

The Copy That test suite (446 tests) requires careful memory management to avoid out-of-memory (OOM) errors. This guide provides three optimized execution strategies for different contexts:

### Key Points
- **jsdom Environment:** Creates full DOM simulations for each test file
- Virtual DOM for each component test
- Full browser API mocks
- Memory not fully released between test files
- **Component Mocking:** React Testing Library + Vitest create many component instances
- 150+ component tests create thousands of DOM nodes
- Mocking frameworks (sinon, etc.) retain references
- **Test Fixtures:** Test data and database mocks accumulate
- Color data fixtures retained in memory
- Mock API responses cached

### Implementation Pointers
- `frontend/src/__tests__/setup.ts`
- `pnpm install`
- `pnpm test`
- `src/components/specific`
- `src/components/token-card/__tests__`

### Build / Refactor Issues
#### **jsdom Environment:** Creates full DOM simulations for each test file

**Context**
Source: `docs/testing/TEST_EXECUTION_STRATEGY.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **jsdom Environment:** Creates full DOM simulations for each test file
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/src/__tests__/setup.ts
- pnpm install
- pnpm test
- src/components/specific
- src/components/token-card/__tests__
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Virtual DOM for each component test

**Context**
Source: `docs/testing/TEST_EXECUTION_STRATEGY.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Virtual DOM for each component test
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/src/__tests__/setup.ts
- pnpm install
- pnpm test
- src/components/specific
- src/components/token-card/__tests__
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Full browser API mocks

**Context**
Source: `docs/testing/TEST_EXECUTION_STRATEGY.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Full browser API mocks
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/src/__tests__/setup.ts
- pnpm install
- pnpm test
- src/components/specific
- src/components/token-card/__tests__
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Memory not fully released between test files

**Context**
Source: `docs/testing/TEST_EXECUTION_STRATEGY.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Memory not fully released between test files
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/src/__tests__/setup.ts
- pnpm install
- pnpm test
- src/components/specific
- src/components/token-card/__tests__
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Testing Documentation

### Sources
- `docs/testing/README.md`

### Summary
**📋 START HERE:** [2025-12-05_START_HERE.md](./2025-12-05_START_HERE.md)

### Key Points
- **[2025-12-05_START_HERE.md](./2025-12-05_START_HERE.md)** — Entry point for all users
- **[2025-12-05_QUICK_START.md](./2025-12-05_QUICK_START.md)** — Run tests instantly
- **[2025-12-05_TESTING_STRATEGY.md](./2025-12-05_TESTING_STRATEGY.md)** — Comprehensive testing approach
- **[2025-12-05_ROADMAP.md](./2025-12-05_ROADMAP.md)** — 5-phase implementation plan
- **[2025-12-05_PATTERNS.md](./2025-12-05_PATTERNS.md)** — Reusable test patterns & examples
- **[2025-12-05_TEST_UTILITIES.md](./2025-12-05_TEST_UTILITIES.md)** — Testing utilities reference
- **[2025-12-05_ARCHITECTURE_VISUALS.md](./2025-12-05_ARCHITECTURE_VISUALS.md)** — Diagrams & visuals
- **[2025-12-05_INDEX.md](./2025-12-05_INDEX.md)** — Complete documentation index
- **[2025-12-05_test-coverage-roadmap.md](./2025-12-05_test-coverage-roadmap.md)** — Coverage targets
- **[2025-12-05_test-env-setup.md](./2025-12-05_test-env-setup.md)** — Environment configuration

### Implementation Pointers
- `pnpm test`

### Build / Refactor Issues
#### **[2025-12-05_START_HERE.md]** — Entry point for all users

**Context**
Source: `docs/testing/README.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **[2025-12-05_START_HERE.md]** — Entry point for all users
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- pnpm test
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **[2025-12-05_QUICK_START.md]** — Run tests instantly

**Context**
Source: `docs/testing/README.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **[2025-12-05_QUICK_START.md]** — Run tests instantly
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- pnpm test
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **[2025-12-05_TESTING_STRATEGY.md]** — Comprehensive testing approach

**Context**
Source: `docs/testing/README.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **[2025-12-05_TESTING_STRATEGY.md]** — Comprehensive testing approach
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- pnpm test
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **[2025-12-05_ROADMAP.md]** — 5-phase implementation plan

**Context**
Source: `docs/testing/README.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **[2025-12-05_ROADMAP.md]** — 5-phase implementation plan
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- pnpm test
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Testing Documentation Index

### Sources
- `docs/testing/INDEX.md`

### Summary
**Last Updated:** 2025-12-05 **Current Test Status:** 424/446 passing (97.9% ✅)

| Area | Status | Details | Priority | |------|--------|---------|----------| | **Frontend Unit Tests** | ✅ PASSING | 424/446 tests (97.9%) | Ready | | **Frontend Integration Tests** | ⚠️ 10 FAILING | ImageUploader async timeouts | HIGH | | **Backend API Tests** | ✅ PASSING | 46/46 tests (100%) | Complete | | **Test Execution Strategy** | ✅ OPTIMIZED | Memory-aware split scripts | Production Ready | | **Documentation** | ✅ COMPLETE | Comprehensive guides | Current |

### Key Points
- **ACTIVE:** TESTING_GUIDE.md - Complete testing operations guide
- **ACTIVE:** TEST_EXECUTION_STRATEGY.md - Memory-optimized test execution for CI/CD
- **REFERENCE:** TEST_SUITE_WRAP_UP_2025_12_05.md - Session 2 final summary (97.9% pass rate)
- **REFERENCE:** TEST_SUITE_STATUS_SESSION_2.md - Detailed phase-by-phase results
- **REFERENCE:** 2025-12-05_test-coverage-roadmap.md - Long-term test coverage goals (outdated format, info consolidated)
- **REFERENCE:** 2025-12-05_test-gaps-and-recommendations.md - Gap analysis (pre-optimization)
- **ACTIVE:** 2025-12-05_test-env-setup.md - Local test environment configuration
- **REFERENCE:** legacy/ - Archive of deprecated testing docs (for historical reference)
- **ACTIVE:** 2025-12-05_TIER2-test-results.md - Playwright E2E tests (47/47 passing ✅)
- **Unit Tests:** 200+ tests covering hooks, utilities, business logic

### Implementation Pointers
- `frontend/src/components/image-uploader/__tests__/ImageUploader.integration.test.tsx`
- `frontend/vite.config.ts`
- `pnpm test`
- `src/components/color-science/__tests__`

### Build / Refactor Issues
#### **ACTIVE:** TESTING_GUIDE.md - Complete testing operations guide

**Context**
Source: `docs/testing/INDEX.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **ACTIVE:** TESTING_GUIDE.md - Complete testing operations guide
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/src/components/image-uploader/__tests__/ImageUploader.integration.test.tsx
- frontend/vite.config.ts
- pnpm test
- src/components/color-science/__tests__
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **ACTIVE:** TEST_EXECUTION_STRATEGY.md - Memory-optimized test execution for CI/CD

**Context**
Source: `docs/testing/INDEX.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **ACTIVE:** TEST_EXECUTION_STRATEGY.md - Memory-optimized test execution for CI/CD
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/src/components/image-uploader/__tests__/ImageUploader.integration.test.tsx
- frontend/vite.config.ts
- pnpm test
- src/components/color-science/__tests__
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **REFERENCE:** TEST_SUITE_WRAP_UP_2025_12_05.md - Session 2 final summary

**Context**
Source: `docs/testing/INDEX.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **REFERENCE:** TEST_SUITE_WRAP_UP_2025_12_05.md - Session 2 final summary
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/src/components/image-uploader/__tests__/ImageUploader.integration.test.tsx
- frontend/vite.config.ts
- pnpm test
- src/components/color-science/__tests__
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **REFERENCE:** TEST_SUITE_STATUS_SESSION_2.md - Detailed phase-by-phase results

**Context**
Source: `docs/testing/INDEX.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **REFERENCE:** TEST_SUITE_STATUS_SESSION_2.md - Detailed phase-by-phase results
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/src/components/image-uploader/__tests__/ImageUploader.integration.test.tsx
- frontend/vite.config.ts
- pnpm test
- src/components/color-science/__tests__
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Token Factory: Reusable Abstraction for Token Pipelines

### Sources
- `docs/planning/token-pipeline-planning/TOKEN_FACTORY_PLANNING.md`

### Summary
**Version:** 1.0 | **Date:** 2025-11-22 | **Status:** Planning Document

This document provides a comprehensive implementation plan for a reusable token factory abstraction that enables rapid development of new token types (color, spacing, typography, shadow, etc.) with built-in support for parallel async processing, streaming, and consistent patterns.

### Key Points
- **Abstract Base Classes** - Template for all token types
- **Registry System** - Dynamic plugin registration and discovery
- **Async Pipeline Orchestration** - Parallel extraction with semaphore control
- **Streaming Infrastructure** - SSE streaming with progress callbacks
- **Aggregation Framework** - Configurable deduplication strategies
- **Generator System** - Multiple export format support
- **Testing Templates** - Pre-built test scaffolding
- token_type: Class variable identifying the token type
- Core fields specific to the token type
- Computed properties via compute_properties()

### Implementation Pointers
- `/api/v1/spacing`
- `frontend/src/config/tokenTypeRegistry.tsx`
- `frontend/src/store/tokenStore.ts`
- `src/copy_that/`
- `src/copy_that/interfaces/api/token_router_template.py`
- `src/core/tokens/base_aggregator.py`
- `src/core/tokens/base_extractor.py`
- `src/core/tokens/base_generator.py`
- `src/core/tokens/base_token.py`
- `src/core/tokens/pipeline.py`
- `src/core/tokens/registry.py`
- `src/core/tokens/streaming.py`

### Build / Refactor Issues
#### **Abstract Base Classes** - Template for all token types

**Context**
Source: `docs/planning/token-pipeline-planning/TOKEN_FACTORY_PLANNING.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Abstract Base Classes** - Template for all token types
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/spacing
- frontend/src/config/tokenTypeRegistry.tsx
- frontend/src/store/tokenStore.ts
- src/copy_that/
- src/copy_that/interfaces/api/token_router_template.py
- src/core/tokens/base_aggregator.py
- src/core/tokens/base_extractor.py
- src/core/tokens/base_generator.py
- src/core/tokens/base_token.py
- src/core/tokens/pipeline.py
- …(+2 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **Registry System** - Dynamic plugin registration and discovery

**Context**
Source: `docs/planning/token-pipeline-planning/TOKEN_FACTORY_PLANNING.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Registry System** - Dynamic plugin registration and discovery
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/spacing
- frontend/src/config/tokenTypeRegistry.tsx
- frontend/src/store/tokenStore.ts
- src/copy_that/
- src/copy_that/interfaces/api/token_router_template.py
- src/core/tokens/base_aggregator.py
- src/core/tokens/base_extractor.py
- src/core/tokens/base_generator.py
- src/core/tokens/base_token.py
- src/core/tokens/pipeline.py
- …(+2 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **Async Pipeline Orchestration** - Parallel extraction with semaphore control

**Context**
Source: `docs/planning/token-pipeline-planning/TOKEN_FACTORY_PLANNING.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Async Pipeline Orchestration** - Parallel extraction with semaphore control
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/spacing
- frontend/src/config/tokenTypeRegistry.tsx
- frontend/src/store/tokenStore.ts
- src/copy_that/
- src/copy_that/interfaces/api/token_router_template.py
- src/core/tokens/base_aggregator.py
- src/core/tokens/base_extractor.py
- src/core/tokens/base_generator.py
- src/core/tokens/base_token.py
- src/core/tokens/pipeline.py
- …(+2 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **Streaming Infrastructure** - SSE streaming with progress callbacks

**Context**
Source: `docs/planning/token-pipeline-planning/TOKEN_FACTORY_PLANNING.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Streaming Infrastructure** - SSE streaming with progress callbacks
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/spacing
- frontend/src/config/tokenTypeRegistry.tsx
- frontend/src/store/tokenStore.ts
- src/copy_that/
- src/copy_that/interfaces/api/token_router_template.py
- src/core/tokens/base_aggregator.py
- src/core/tokens/base_extractor.py
- src/core/tokens/base_generator.py
- src/core/tokens/base_token.py
- src/core/tokens/pipeline.py
- …(+2 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Token Pipeline Planning - Complete Deliverable Package

### Sources
- `docs/planning/token-pipeline-planning/README.md`

### Summary
**Version:** 1.0 | **Date:** 2025-11-22 | **Status:** Complete

This folder contains the comprehensive implementation planning package for the token pipeline system, including spacing token implementation, reusable token factory abstraction, reference code, tests, and full SDLC documentation.

### Key Points
- Architecture overview and data flow diagram
- SpacingToken Pydantic model (20+ fields)
- SQLAlchemy model and migration
- AISpacingExtractor implementation
- Utility functions (conversions, scale detection)
- SpacingAggregator with percentage-based deduplication
- Async batch processing with semaphore
- SSE streaming endpoints
- Export generators (W3C, CSS, React, Tailwind)
- Abstract base classes (BaseToken, BaseExtractor, BaseAggregator)

### Implementation Pointers
_No explicit code touchpoints referenced in doc._

### Build / Refactor Issues
#### Architecture overview and data flow diagram

**Context**
Source: `docs/planning/token-pipeline-planning/README.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Architecture overview and data flow diagram
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### SpacingToken Pydantic model

**Context**
Source: `docs/planning/token-pipeline-planning/README.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: SpacingToken Pydantic model
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### SQLAlchemy model and migration

**Context**
Source: `docs/planning/token-pipeline-planning/README.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: SQLAlchemy model and migration
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### AISpacingExtractor implementation

**Context**
Source: `docs/planning/token-pipeline-planning/README.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: AISpacingExtractor implementation
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Visualization Tools Guide

### Sources
- `docs/testing/VISUALIZATION_TOOLS_GUIDE.md`

### Summary
**Best for:** Flowcharts, sequence diagrams, Gantt charts, class diagrams **Command:** `mmdc` (mermaid-cli) or `pnpm mermaid`

### Key Points
- Native GitHub/GitLab rendering
- Wide variety of diagram types
- Simple text-based syntax
- Great for documentation
- Beautiful default styling
- Auto-layout with multiple engines
- Connections and relationships
- Themes and customization
- 0 - Neutral (default)
- 100 - Cool Classics

### Implementation Pointers
- `pnpm diagram`
- `pnpm docs`
- `pnpm mermaid`
- `pnpm optimize`

### Build / Refactor Issues
#### Native GitHub/GitLab rendering

**Context**
Source: `docs/testing/VISUALIZATION_TOOLS_GUIDE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Native GitHub/GitLab rendering
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- pnpm diagram
- pnpm docs
- pnpm mermaid
- pnpm optimize
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Wide variety of diagram types

**Context**
Source: `docs/testing/VISUALIZATION_TOOLS_GUIDE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Wide variety of diagram types
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- pnpm diagram
- pnpm docs
- pnpm mermaid
- pnpm optimize
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Simple text-based syntax

**Context**
Source: `docs/testing/VISUALIZATION_TOOLS_GUIDE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Simple text-based syntax
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- pnpm diagram
- pnpm docs
- pnpm mermaid
- pnpm optimize
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Great for documentation

**Context**
Source: `docs/testing/VISUALIZATION_TOOLS_GUIDE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Great for documentation
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- pnpm diagram
- pnpm docs
- pnpm mermaid
- pnpm optimize
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## 🚀 Copy That - Start Here

### Sources
- `docs/setup/start_here.md`

### Summary
**Welcome to Copy That!** A fresh, modular platform for extracting design tokens from images.

**Status:** v3.5.1 (Database Foundation Complete) | Last Updated: 2025-11-19

### Key Points
- Read: [Local Development Setup](#local-development)
- Follow: [Backend: Database Integration](#backend-database-integration)
- Try: [Running the API](#running-the-api)
- Read: [System Architecture](#system-architecture)
- Explore: /docs/architecture/ - Design patterns and patterns
- Reference: /docs/domain/ - Token system and domain knowledge
- Start: [Phase 4 Color Vertical Slice](#phase-4-implementation)
- Follow: /docs/workflows/phase_4_color_vertical_slice.md
- Reference: /docs/domain/token_system.md
- Read: /docs/deployment/setup/deployment_options.md - Choose your path

### Implementation Pointers
- `/api/v1/db-test`
- `alembic downgrade`
- `alembic revision`
- `alembic upgrade`
- `make improvements`
- `pnpm typecheck`
- `src/copy_that/domain/models.py`
- `src/copy_that/domain/schemas/`
- `src/copy_that/infrastructure/database.py`
- `src/copy_that/interfaces/api/main.py`
- `src/copy_that/interfaces/api/routes/`

### Build / Refactor Issues
#### Read: [Local Development Setup]

**Context**
Source: `docs/setup/start_here.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Read: [Local Development Setup]
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/db-test
- alembic downgrade
- alembic revision
- alembic upgrade
- make improvements
- pnpm typecheck
- src/copy_that/domain/models.py
- src/copy_that/domain/schemas/
- src/copy_that/infrastructure/database.py
- src/copy_that/interfaces/api/main.py
- …(+1 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Follow: [Backend: Database Integration]

**Context**
Source: `docs/setup/start_here.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Follow: [Backend: Database Integration]
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/db-test
- alembic downgrade
- alembic revision
- alembic upgrade
- make improvements
- pnpm typecheck
- src/copy_that/domain/models.py
- src/copy_that/domain/schemas/
- src/copy_that/infrastructure/database.py
- src/copy_that/interfaces/api/main.py
- …(+1 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Try: [Running the API]

**Context**
Source: `docs/setup/start_here.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Try: [Running the API]
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/db-test
- alembic downgrade
- alembic revision
- alembic upgrade
- make improvements
- pnpm typecheck
- src/copy_that/domain/models.py
- src/copy_that/domain/schemas/
- src/copy_that/infrastructure/database.py
- src/copy_that/interfaces/api/main.py
- …(+1 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Read: [System Architecture]

**Context**
Source: `docs/setup/start_here.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Read: [System Architecture]
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/db-test
- alembic downgrade
- alembic revision
- alembic upgrade
- make improvements
- pnpm typecheck
- src/copy_that/domain/models.py
- src/copy_that/domain/schemas/
- src/copy_that/infrastructure/database.py
- src/copy_that/interfaces/api/main.py
- …(+1 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

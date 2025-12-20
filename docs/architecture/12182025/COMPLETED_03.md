# Completed

## Shadow Tokens - Completion Verification

### Sources
- `docs/shadow/TOKENS_COMPLETION.md`

### Summary
**Status:** ✅ PRODUCTION READY **Date:** December 3, 2025 **Version:** v1.0.0

Shadow tokens are now fully implemented and ready for production use. All components of the vertical slice are complete:

### Key Points
- Database schema (migration exists)
- API endpoints (5 endpoints fully functional)
- Service layer (extraction + deduplication)
- AI extraction (Claude Sonnet 4.5)
- Comprehensive tests (34+ test cases)
- W3C export integration
- project_id (foreign key)
- extraction_job_id (foreign key)
- x_offset, y_offset, blur_radius, spread_radius
- color_hex, opacity

### Implementation Pointers
- `/api/v1/design-tokens/export/w3c`
- `/api/v1/shadows`
- `/api/v1/shadows/`
- `/api/v1/shadows/extract`
- `/api/v1/shadows/projects/`
- `alembic upgrade`
- `src/copy_that/application/ai_shadow_extractor.py`
- `src/copy_that/domain/models.py`
- `src/copy_that/interfaces/api/design_tokens.py`
- `src/copy_that/interfaces/api/shadows.py`
- `src/copy_that/services/shadow_service.py`
- `src/core/tokens/shadow.py`

### Build / Refactor Issues
#### Harden/regression-test: Database schema

**Context**
Source: `docs/shadow/TOKENS_COMPLETION.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: Database schema
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/design-tokens/export/w3c
- /api/v1/shadows
- /api/v1/shadows/
- /api/v1/shadows/extract
- /api/v1/shadows/projects/
- alembic upgrade
- src/copy_that/application/ai_shadow_extractor.py
- src/copy_that/domain/models.py
- src/copy_that/interfaces/api/design_tokens.py
- src/copy_that/interfaces/api/shadows.py
- …(+2 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Harden/regression-test: API endpoints

**Context**
Source: `docs/shadow/TOKENS_COMPLETION.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: API endpoints
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/design-tokens/export/w3c
- /api/v1/shadows
- /api/v1/shadows/
- /api/v1/shadows/extract
- /api/v1/shadows/projects/
- alembic upgrade
- src/copy_that/application/ai_shadow_extractor.py
- src/copy_that/domain/models.py
- src/copy_that/interfaces/api/design_tokens.py
- src/copy_that/interfaces/api/shadows.py
- …(+2 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Spacing Token Pipeline: Implementation Roadmap

### Sources
- `docs/planning/token-pipeline-planning/IMPLEMENTATION_ROADMAP.md`

### Summary
**Version:** 1.0 | **Date:** 2025-11-22 | **Status:** Planning Document

This document provides a detailed week-by-week implementation roadmap for the spacing token pipeline, including daily breakdowns, milestones, and resource allocation.

### Key Points
- [ ] User personas and stories documented
- [ ] Technical requirements complete
- [ ] Architecture diagrams created
- [ ] Database schema designed
- If requirements gathering takes longer, reduce scope of user stories
- Database schema can be refined during implementation
- [ ] SpacingToken Pydantic model with tests
- [ ] SpacingToken SQLAlchemy model with migration
- [ ] AISpacingExtractor fully functional
- [ ] Can extract spacing from test images

### Implementation Pointers
_No explicit code touchpoints referenced in doc._

### Build / Refactor Issues
#### Harden/regression-test: [ ] User personas and stories documented

**Context**
Source: `docs/planning/token-pipeline-planning/IMPLEMENTATION_ROADMAP.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: [ ] User personas and stories documented
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Harden/regression-test: [ ] Technical requirements complete

**Context**
Source: `docs/planning/token-pipeline-planning/IMPLEMENTATION_ROADMAP.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: [ ] Technical requirements complete
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Token Architecture Alternatives: Loosely Coupled Parallel Processing

### Sources
- `docs/planning/token-pipeline-planning/TOKEN_ARCHITECTURE_ALTERNATIVES.md`

### Summary
**Version:** 1.0 | **Date:** 2025-11-22 | **Status:** Architectural Exploration

This document explores architectural alternatives to the factory pattern for a token system that requires:

### Key Points
- Loose coupling between token types
- Parallel execution with independent instances
- Atomic token instances with multiple instantiations
- Relationship management across token types
- Flexibility and extensibility
- Synchronized pipeline orchestration
- Tight inheritance hierarchies
- Tokens that can run independently and in parallel
- Multiple instances of the same token type processing simultaneously
- Relationships between tokens (color influences typography, spacing relates to grid)

### Implementation Pointers
_No explicit code touchpoints referenced in doc._

### Build / Refactor Issues
#### Harden/regression-test: Loose coupling between token types

**Context**
Source: `docs/planning/token-pipeline-planning/TOKEN_ARCHITECTURE_ALTERNATIVES.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: Loose coupling between token types
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Harden/regression-test: Parallel execution with independent instances

**Context**
Source: `docs/planning/token-pipeline-planning/TOKEN_ARCHITECTURE_ALTERNATIVES.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: Parallel execution with independent instances
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Typography & Font Tokens Implementation Plan

### Sources
- `docs/TYPOGRAPHY_AND_FONT_TOKENS_PLAN.md`

### Summary
**Status:** Ready to Implement **Priority:** HIGH (core design system component) **Estimated Duration:** 3-4 days **Pattern:** Follow proven color/spacing/shadow architecture

This plan implements typography and font token extraction following the established vertical slice pattern:

### Key Points
- **Option A: Typography Tokens** - Extract fonts, sizes, line heights, and text properties from images
- **Option B: Font Family & Font Size Tokens** - Support tokens for typography system
- Font family name (e.g., "Inter", "Roboto", "Georgia")
- Font weight (100-900)
- Font size in pixels (approximate if needed)
- Line height (as multiplier, e.g., 1.5)
- Letter spacing (if visible, in em units)
- Text transform (uppercase/lowercase/capitalize if applied)
- Semantic role (heading, body, caption, label, etc.)
- Category (display, text, label, etc.)

### Implementation Pointers
- `/api/v1/fonts/families`
- `/api/v1/fonts/sizes`
- `/api/v1/typography`
- `/api/v1/typography/`
- `/api/v1/typography/extract`
- `/api/v1/typography/projects/`
- `alembic revision`
- `alembic upgrade`
- `src/copy_that/application/ai_typography_extractor.py`
- `src/copy_that/application/cv/typography_cv_extractor.py`
- `src/copy_that/domain/models.py`
- `src/copy_that/interfaces/api/design_tokens.py`
- `src/copy_that/interfaces/api/fonts.py`
- `src/copy_that/interfaces/api/main.py`
- `src/copy_that/interfaces/api/typography.py`
- `src/copy_that/services/font_service.py`
- `src/copy_that/services/typography_service.py`
- `src/core/tokens/model.py`

### Build / Refactor Issues
#### Harden/regression-test: **Option A: Typography Tokens** - Extract fonts, sizes, line heights, and text properti…

**Context**
Source: `docs/TYPOGRAPHY_AND_FONT_TOKENS_PLAN.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: **Option A: Typography Tokens** - Extract fonts, sizes, line heights, and text properti…
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/fonts/families
- /api/v1/fonts/sizes
- /api/v1/typography
- /api/v1/typography/
- /api/v1/typography/extract
- /api/v1/typography/projects/
- alembic revision
- alembic upgrade
- src/copy_that/application/ai_typography_extractor.py
- src/copy_that/application/cv/typography_cv_extractor.py
- …(+8 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Harden/regression-test: **Option B: Font Family & Font Size Tokens** - Support tokens for typography system

**Context**
Source: `docs/TYPOGRAPHY_AND_FONT_TOKENS_PLAN.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: **Option B: Font Family & Font Size Tokens** - Support tokens for typography system
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/fonts/families
- /api/v1/fonts/sizes
- /api/v1/typography
- /api/v1/typography/
- /api/v1/typography/extract
- /api/v1/typography/projects/
- alembic revision
- alembic upgrade
- src/copy_that/application/ai_typography_extractor.py
- src/copy_that/application/cv/typography_cv_extractor.py
- …(+8 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Typography Implementation - Complete Implementation Guide

### Sources
- `docs/TYPOGRAPHY_IMPLEMENTATION_GUIDE.md`

### Summary
**Status:** 70% Complete (5/7 core steps done) **Ready for Next Session:** YES - All groundwork complete **Estimated Time to Finish:** 2-3 hours **Complexity:** Medium (straightforward pattern replication)

### Key Points
- **Files:** src/copy_that/domain/models.py + alembic/versions/2025_12_03_add_typography_and_font_tokens.py
- **Status:** Ready to migrate on next Docker build
- **Models:** TypographyToken, FontFamilyToken, FontSizeToken
- **File:** src/copy_that/application/ai_typography_extractor.py (500+ lines)
- **Class:** AITypographyExtractor with Claude Sonnet 4.5
- extract_typography_from_image_url() - URL extraction
- extract_typography_from_file() - File extraction
- extract_typography_from_base64() - Base64 extraction
- **Output:** TypographyExtractionResult (Pydantic model)
- **File:** src/copy_that/application/cv/typography_cv_extractor.py (250+ lines)

### Implementation Pointers
- `/api/v1/design-tokens/export/w3c`
- `/api/v1/typography/`
- `/api/v1/typography/extract`
- `/api/v1/typography/projects/`
- `pnpm typecheck`
- `src/copy_that/application/ai_typography_extractor.py`
- `src/copy_that/application/cv/typography_cv_extractor.py`
- `src/copy_that/domain/models.py`
- `src/copy_that/interfaces/api/colors.py`
- `src/copy_that/interfaces/api/design_tokens.py`
- `src/copy_that/interfaces/api/main.py`
- `src/copy_that/interfaces/api/typography.py`
- `src/copy_that/services/spacing_service.py`
- `src/copy_that/services/typography_service.py`
- `src/core/tokens/typography.py`

### Build / Refactor Issues
#### Harden/regression-test: **Files:** src/copy_that/domain/models.py + alembic/versions/2025_12_03_add_typography_…

**Context**
Source: `docs/TYPOGRAPHY_IMPLEMENTATION_GUIDE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: **Files:** src/copy_that/domain/models.py + alembic/versions/2025_12_03_add_typography_…
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/design-tokens/export/w3c
- /api/v1/typography/
- /api/v1/typography/extract
- /api/v1/typography/projects/
- pnpm typecheck
- src/copy_that/application/ai_typography_extractor.py
- src/copy_that/application/cv/typography_cv_extractor.py
- src/copy_that/domain/models.py
- src/copy_that/interfaces/api/colors.py
- src/copy_that/interfaces/api/design_tokens.py
- …(+5 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Harden/regression-test: **Status:** Ready to migrate on next Docker build

**Context**
Source: `docs/TYPOGRAPHY_IMPLEMENTATION_GUIDE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: **Status:** Ready to migrate on next Docker build
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/design-tokens/export/w3c
- /api/v1/typography/
- /api/v1/typography/extract
- /api/v1/typography/projects/
- pnpm typecheck
- src/copy_that/application/ai_typography_extractor.py
- src/copy_that/application/cv/typography_cv_extractor.py
- src/copy_that/domain/models.py
- src/copy_that/interfaces/api/colors.py
- src/copy_that/interfaces/api/design_tokens.py
- …(+5 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Visual Guide: Source Badges on Metrics

### Sources
- `docs/design/VISUAL_GUIDE_SOURCE_BADGES.md`

### Summary
_No narrative prose found; see Key Points._

### Key Points
- Image extraction completes
- Tokens are in the database
- Metrics page is refreshed
- New extraction happens
- App first loads (no data yet)
- During extraction (still processing)
- Before any image upload
- Confidence percentages still show (e.g., "75%")
- Confidence labels still show (e.g., "High Confidence")
- Metric titles and descriptions unchanged

### Implementation Pointers
_No explicit code touchpoints referenced in doc._

### Build / Refactor Issues
#### Harden/regression-test: Image extraction completes

**Context**
Source: `docs/design/VISUAL_GUIDE_SOURCE_BADGES.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: Image extraction completes
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Harden/regression-test: Tokens are in the database

**Context**
Source: `docs/design/VISUAL_GUIDE_SOURCE_BADGES.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: Tokens are in the database
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## 🚀 Copy That - Launch Checklist

### Sources
- `docs/launch/LAUNCH_CHECKLIST.md`

### Summary
**Version**: v0.4.0 - Production Ready **Status**: ✅ ALL SYSTEMS GO **Date**: 2025-11-20

### Key Points
- [x] FastAPI running on port 8000
- [x] All endpoints operational (/api/v1/*)
- [x] Database schema complete (8 tables)
- [x] Color CRUD operations working
- [x] Project CRUD operations working
- [x] Batch processing tested (500 colors in 1.38s)
- [x] Error handling verified
- [x] React app running on port 4000
- [x] TypeScript: 0 errors
- [x] All components rendering

### Implementation Pointers
- `/api/v1/colors`
- `/api/v1/colors/`
- `/api/v1/colors/extract`
- `/api/v1/projects`
- `/api/v1/projects/`
- `/api/v1/status`
- `frontend/src/components/`
- `pnpm dev`
- `pnpm install`
- `src/copy_that/domain/models.py`
- `src/copy_that/interfaces/api/main.py`

### Build / Refactor Issues
#### Harden/regression-test: [x] FastAPI running on port 8000

**Context**
Source: `docs/launch/LAUNCH_CHECKLIST.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: [x] FastAPI running on port 8000
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/colors
- /api/v1/colors/
- /api/v1/colors/extract
- /api/v1/projects
- /api/v1/projects/
- /api/v1/status
- frontend/src/components/
- pnpm dev
- pnpm install
- src/copy_that/domain/models.py
- …(+1 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Harden/regression-test: [x] All endpoints operational

**Context**
Source: `docs/launch/LAUNCH_CHECKLIST.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: [x] All endpoints operational
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/colors
- /api/v1/colors/
- /api/v1/colors/extract
- /api/v1/projects
- /api/v1/projects/
- /api/v1/status
- frontend/src/components/
- pnpm dev
- pnpm install
- src/copy_that/domain/models.py
- …(+1 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

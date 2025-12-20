# Roadmap

## Architecture Docs

### Sources
- `docs/architecture/README.md`

### Summary
Current, non-archived architecture references:

### Key Points
- adapter_pattern.md — Adapter pattern overview
- atomic_streaming_summary.md — Streaming/atomic flow summary
- component_token_schema.md — Component token schema
- existing_capabilities_inventory.md — Inventory of platform capabilities
- extractor_patterns.md — Extractor taxonomy/patterns
- modular_token_platform_vision.md — Platform vision
- plugin_architecture.md — Plugin model outline
- schema_architecture_diagram.md — Schema diagrams
- strategic_vision_and_architecture.md — Strategic architecture vision
- token_graph.md — Token graph relationships and structure

### Implementation Pointers
_No explicit code touchpoints referenced in doc._

### Build / Refactor Issues
#### adapter_pattern.md — Adapter pattern overview

**Context**
Source: `docs/architecture/README.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: adapter_pattern.md — Adapter pattern overview
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### atomic_streaming_summary.md — Streaming/atomic flow summary

**Context**
Source: `docs/architecture/README.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: atomic_streaming_summary.md — Streaming/atomic flow summary
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### component_token_schema.md — Component token schema

**Context**
Source: `docs/architecture/README.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: component_token_schema.md — Component token schema
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### existing_capabilities_inventory.md — Inventory of platform capabilities

**Context**
Source: `docs/architecture/README.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: existing_capabilities_inventory.md — Inventory of platform capabilities
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## CI Badge Green Plan

### Sources
- `docs/CI_BADGE_GREEN_PLAN.md`

### Summary
**Goal:** Get all repository badges showing green status **Created:** 2025-12-12 **Status:** Ready for execution

Based on README.md line 5-11, we have 7 badges:

### Key Points
- **Security** (Lines 13-53)
- pip-audit (dependency vulnerabilities) - continue-on-error: true
- Bandit (Python security linter)
- Gitleaks (secret detection)
- ✅ **Should pass** - Security scans are informational
- **Lint** (Lines 55-84)
- ✅ **Should pass** - mypy overrides are in pyproject.toml
- **Test** (Lines 86-184)
- Requires PostgreSQL + Redis services
- Runs unit tests with coverage

### Implementation Pointers
- `alembic upgrade`

### Build / Refactor Issues
#### **Security**

**Context**
Source: `docs/CI_BADGE_GREEN_PLAN.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Security**
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- alembic upgrade
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### pip-audit  - continue-on-error: true

**Context**
Source: `docs/CI_BADGE_GREEN_PLAN.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: pip-audit  - continue-on-error: true
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- alembic upgrade
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Bandit

**Context**
Source: `docs/CI_BADGE_GREEN_PLAN.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Bandit
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- alembic upgrade
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Gitleaks

**Context**
Source: `docs/CI_BADGE_GREEN_PLAN.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Gitleaks
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- alembic upgrade
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Color Token Integration Roadmap

### Sources
- `docs/workflows/color_integration_roadmap.md`

### Summary
**Document Version:** 1.0 **Date:** 2025-11-19 (Last Updated: 2025-11-19) **Status:** Phase 1 Quick Wins Ready for Integration **Current Phase:** Phase 4, Week 1 **Related:** [strategic_vision_and_architecture.md](architecture/strategic_vision_and_architecture.md), [workflows/phase_4_color_vertical_slice.md](workflows/phase_4_color_vertical_slice.md)

This document outlines the step-by-step integration of advanced color science features into the Copy That platform, building on existing research and code.

### Key Points
- ✅ 3,336 lines of color-specific code already written
- ✅ 98.3% test coverage on production features
- ✅ Advanced features built but NOT integrated: Oklch scales, Delta-E merging, semantic naming
- ✅ Phase 4 Day 4 complete: AI extractor with Claude Structured Outputs
- ✅ Equal visual steps in scales (50 → 100 looks same as 800 → 900)
- ✅ Better for accessibility (consistent contrast ratios)
- ✅ More intuitive for designers
- Import generate_oklch_scale from color_spaces_advanced.py
- Replace HSL scale generation with Oklch
- Update ColorTokenCoreSchema to include scale field

### Implementation Pointers
- `frontend/src/api/colorClient.ts`
- `frontend/src/components/ColorTokenCard.tsx`
- `frontend/src/pages/ColorExtractionDemo.tsx`
- `pnpm dev`
- `pnpm test`
- `pnpm typecheck`

### Build / Refactor Issues
#### ✅ 3,336 lines of color-specific code already written

**Context**
Source: `docs/workflows/color_integration_roadmap.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: ✅ 3,336 lines of color-specific code already written
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/src/api/colorClient.ts
- frontend/src/components/ColorTokenCard.tsx
- frontend/src/pages/ColorExtractionDemo.tsx
- pnpm dev
- pnpm test
- pnpm typecheck
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### ✅ 98.3% test coverage on production features

**Context**
Source: `docs/workflows/color_integration_roadmap.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: ✅ 98.3% test coverage on production features
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/src/api/colorClient.ts
- frontend/src/components/ColorTokenCard.tsx
- frontend/src/pages/ColorExtractionDemo.tsx
- pnpm dev
- pnpm test
- pnpm typecheck
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### ✅ Advanced features built but NOT integrated: Oklch scales, Delta-E merging, semantic n…

**Context**
Source: `docs/workflows/color_integration_roadmap.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: ✅ Advanced features built but NOT integrated: Oklch scales, Delta-E merging, semantic n…
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/src/api/colorClient.ts
- frontend/src/components/ColorTokenCard.tsx
- frontend/src/pages/ColorExtractionDemo.tsx
- pnpm dev
- pnpm test
- pnpm typecheck
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### ✅ Phase 4 Day 4 complete: AI extractor with Claude Structured Outputs

**Context**
Source: `docs/workflows/color_integration_roadmap.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: ✅ Phase 4 Day 4 complete: AI extractor with Claude Structured Outputs
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/src/api/colorClient.ts
- frontend/src/components/ColorTokenCard.tsx
- frontend/src/pages/ColorExtractionDemo.tsx
- pnpm dev
- pnpm test
- pnpm typecheck
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Component Token Schema (v3.0)

### Sources
- `docs/architecture/COMPONENT_TOKEN_SCHEMA.md`

### Summary
**Created**: 2025-11-09 **Status**: Phase 3 Priority #5 - In Progress **Related**: Progressive Extraction Architecture Layer 3

Compositional token architecture that combines foundation tokens into component-level design tokens with full state variation support.

### Key Points
- default - Base state
- focus - Keyboard/accessibility focus
- active - Pressed/clicked
- disabled - Non-interactive state
- **Web**: CSS Variables, Tailwind Config
- **React**: TypeScript components + Tailwind CSS
- **Flutter**: Material Theme 3
- **JUCE**: LookAndFeel C++ classes ⭐ **Primary Target**
- Rotary knobs (with skeuomorphic and flat styles)
- Linear sliders (vertical/horizontal)

### Implementation Pointers
- `frontend/src/api/types.ts`

### Build / Refactor Issues
#### default - Base state

**Context**
Source: `docs/architecture/COMPONENT_TOKEN_SCHEMA.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: default - Base state
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/src/api/types.ts
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### focus - Keyboard/accessibility focus

**Context**
Source: `docs/architecture/COMPONENT_TOKEN_SCHEMA.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: focus - Keyboard/accessibility focus
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/src/api/types.ts
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### active - Pressed/clicked

**Context**
Source: `docs/architecture/COMPONENT_TOKEN_SCHEMA.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: active - Pressed/clicked
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/src/api/types.ts
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### disabled - Non-interactive state

**Context**
Source: `docs/architecture/COMPONENT_TOKEN_SCHEMA.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: disabled - Non-interactive state
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/src/api/types.ts
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Copy That - Complete Testing Guide

### Sources
- `docs/testing/TESTING_GUIDE.md`

### Summary
**Status:** ✅ PRODUCTION READY **Version:** 2.0 (Consolidated & Optimized) **Last Updated:** 2025-12-05

### Key Points
- Instant feedback (watch mode)
- Low memory overhead (~500MB)
- Running specific test files
- Need immediate feedback
- Prevents out-of-memory errors
- Reliable, reproducible results
- Clear pass/fail metrics
- ~8 minutes total execution
- Works with limited memory (4GB)
- Runs Phase 1: Core data tests (~1 min)

### Implementation Pointers
- `frontend/src/`
- `frontend/src/__tests__/setup.ts`
- `frontend/src/components/`
- `frontend/src/components/image-uploader/__tests__/ImageUploader.integration.test.tsx`
- `frontend/vite.config.ts`
- `pnpm --version`
- `pnpm 8`
- `pnpm install`
- `pnpm test`
- `src/components`
- `src/components/color-science/__tests__`
- `src/components/specific`
- `src/components/token-card`

### Build / Refactor Issues
#### Instant feedback

**Context**
Source: `docs/testing/TESTING_GUIDE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Instant feedback
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/src/
- frontend/src/__tests__/setup.ts
- frontend/src/components/
- frontend/src/components/image-uploader/__tests__/ImageUploader.integration.test.tsx
- frontend/vite.config.ts
- pnpm --version
- pnpm 8
- pnpm install
- pnpm test
- src/components
- …(+3 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Low memory overhead

**Context**
Source: `docs/testing/TESTING_GUIDE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Low memory overhead
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/src/
- frontend/src/__tests__/setup.ts
- frontend/src/components/
- frontend/src/components/image-uploader/__tests__/ImageUploader.integration.test.tsx
- frontend/vite.config.ts
- pnpm --version
- pnpm 8
- pnpm install
- pnpm test
- src/components
- …(+3 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Running specific test files

**Context**
Source: `docs/testing/TESTING_GUIDE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Running specific test files
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/src/
- frontend/src/__tests__/setup.ts
- frontend/src/components/
- frontend/src/components/image-uploader/__tests__/ImageUploader.integration.test.tsx
- frontend/vite.config.ts
- pnpm --version
- pnpm 8
- pnpm install
- pnpm test
- src/components
- …(+3 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Need immediate feedback

**Context**
Source: `docs/testing/TESTING_GUIDE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Need immediate feedback
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/src/
- frontend/src/__tests__/setup.ts
- frontend/src/components/
- frontend/src/components/image-uploader/__tests__/ImageUploader.integration.test.tsx
- frontend/vite.config.ts
- pnpm --version
- pnpm 8
- pnpm install
- pnpm test
- src/components
- …(+3 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Copy That Documentation Guide

### Sources
- `docs/overview/documentation.md`

### Summary
**Last Updated:** November 19, 2025 | **Version:** 0.1.0

Welcome to Copy That! This guide helps you navigate our comprehensive documentation across multiple topics and use cases.

### Key Points
- **[setup/start_here.md](setup/start_here.md)** - 5-minute overview and quick start guide
- **[README.md](../README.md)** - Project overview and key features
- **[setup/start_here.md](setup/start_here.md)** - Quick start guide, architecture overview, phase roadmap
- **[setup/setup_minimal.md](setup/setup_minimal.md)** - Minimal cloud deployment (~$0-5/month)
- **[setup/database_setup.md](setup/database_setup.md)** - Neon PostgreSQL configuration and migration
- **[architecture/architecture_overview.md](architecture/architecture_overview.md)** (NEW - 18 KB)
- Complete accurate overview of current system
- Data architecture and implementation patterns
- Module organization and technology rationale
- Deployment architecture

### Implementation Pointers
_No explicit code touchpoints referenced in doc._

### Build / Refactor Issues
#### **[setup/start_here.md]** - 5-minute overview and quick start guide

**Context**
Source: `docs/overview/documentation.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **[setup/start_here.md]** - 5-minute overview and quick start guide
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **[README.md]** - Project overview and key features

**Context**
Source: `docs/overview/documentation.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **[README.md]** - Project overview and key features
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **[setup/start_here.md]** - Quick start guide, architecture overview, phase roadmap

**Context**
Source: `docs/overview/documentation.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **[setup/start_here.md]** - Quick start guide, architecture overview, phase roadmap
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **[setup/setup_minimal.md]** - Minimal cloud deployment

**Context**
Source: `docs/overview/documentation.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **[setup/setup_minimal.md]** - Minimal cloud deployment
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Copy That: Current Architecture State & Roadmap

### Sources
- `docs/architecture/CURRENT_ARCHITECTURE_STATE.md`

### Summary
**Document Version:** 1.1 **Date:** 2025-12-12 **Last Updated:** 2025-12-12 (Added mood board feature, removed pipeline directory) **Status:** Architecture Review & Technical Debt Analysis **Reviewer:** Claude Code Architecture Agent

**Copy That** is a **multi-modal token extraction platform** currently in Phase 2.5 development, evolving from a design token tool into a comprehensive universal design intelligence system. The platform extracts design tokens (color, spacing, typography, shadow) from images using hybrid AI/CV approaches and generates production-ready code for multiple platforms.

### Key Points
- **Version:** 1.0.0 (Phase 2.5 in progress)
- **Backend:** 44,759 LOC Python (FastAPI, Pydantic, SQLAlchemy)
- **Frontend:** 31,170 LOC TypeScript/React (Vite, Zustand, Axios)
- **Database:** PostgreSQL (Neon serverless) with 16 Alembic migrations
- **AI Integration:** Claude Sonnet 4.5, OpenAI GPT-4V
- **Architecture Maturity:** 75% - Production-ready color extraction, experimental spacing/typography/shadow
- **Technical Debt:** Medium - Incomplete type coverage, test gaps, new features need documentation
- **New Features:** AI-powered mood board generation (Claude + DALL-E)
- FastAPI 0.115+ (Async REST API)
- Pydantic v2 (Type validation & serialization)

### Implementation Pointers
- `/api/v1/colors/extract`
- `/api/v1/mood-board/generate`
- `/api/v1/tokens/graph`
- `frontend/package.json`
- `frontend/src/`
- `frontend/src/App.tsx`
- `frontend/src/components/overview-narrative/MoodBoard.tsx`
- `frontend/src/components/overview-narrative/moodBoardTypes.ts`
- `frontend/src/components/overview-narrative/useMoodBoard.ts`
- `frontend/src/features/visual-extraction/adapters/ColorVisualAdapter.tsx`
- `frontend/src/features/visual-extraction/components/color/`
- `frontend/src/features/visual-extraction/components/spacing/`
- `frontend/src/shared/adapters/TokenVisualAdapter.ts`
- `frontend/src/shared/components/TokenDetailPanel/`
- `frontend/src/shared/components/TokenGrid/`
- `frontend/vite.config.ts`
- `frontend/vitest.config.ts`
- `src/copy_that/`
- `src/copy_that/application/`
- `src/copy_that/domain/models.py`
- `src/copy_that/extractors/color/adapters.py`
- `src/copy_that/extractors/color/orchestrator.py`
- `src/copy_that/extractors/shadow/orchestrator.py`
- `src/copy_that/extractors/spacing/orchestrator.py`
- `src/copy_that/extractors/typography/orchestrator.py`
- `src/copy_that/generators/`
- `src/copy_that/interfaces/api/colors.py`
- `src/copy_that/interfaces/api/main.py`
- `src/copy_that/interfaces/api/mood_board.py`
- `src/copy_that/interfaces/api/shadows.py`
- `src/copy_that/interfaces/api/spacing.py`
- `src/copy_that/interfaces/api/typography.py`
- `src/copy_that/pipeline/`
- `src/copy_that/services/mood_board_generator.py`

### Build / Refactor Issues
#### **Version:** 1.0.0

**Context**
Source: `docs/architecture/CURRENT_ARCHITECTURE_STATE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Version:** 1.0.0
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/colors/extract
- /api/v1/mood-board/generate
- /api/v1/tokens/graph
- frontend/package.json
- frontend/src/
- frontend/src/App.tsx
- frontend/src/components/overview-narrative/MoodBoard.tsx
- frontend/src/components/overview-narrative/moodBoardTypes.ts
- frontend/src/components/overview-narrative/useMoodBoard.ts
- frontend/src/features/visual-extraction/adapters/ColorVisualAdapter.tsx
- …(+24 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **Backend:** 44,759 LOC Python

**Context**
Source: `docs/architecture/CURRENT_ARCHITECTURE_STATE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Backend:** 44,759 LOC Python
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/colors/extract
- /api/v1/mood-board/generate
- /api/v1/tokens/graph
- frontend/package.json
- frontend/src/
- frontend/src/App.tsx
- frontend/src/components/overview-narrative/MoodBoard.tsx
- frontend/src/components/overview-narrative/moodBoardTypes.ts
- frontend/src/components/overview-narrative/useMoodBoard.ts
- frontend/src/features/visual-extraction/adapters/ColorVisualAdapter.tsx
- …(+24 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **Frontend:** 31,170 LOC TypeScript/React

**Context**
Source: `docs/architecture/CURRENT_ARCHITECTURE_STATE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Frontend:** 31,170 LOC TypeScript/React
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/colors/extract
- /api/v1/mood-board/generate
- /api/v1/tokens/graph
- frontend/package.json
- frontend/src/
- frontend/src/App.tsx
- frontend/src/components/overview-narrative/MoodBoard.tsx
- frontend/src/components/overview-narrative/moodBoardTypes.ts
- frontend/src/components/overview-narrative/useMoodBoard.ts
- frontend/src/features/visual-extraction/adapters/ColorVisualAdapter.tsx
- …(+24 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **Database:** PostgreSQL  with 16 Alembic migrations

**Context**
Source: `docs/architecture/CURRENT_ARCHITECTURE_STATE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Database:** PostgreSQL  with 16 Alembic migrations
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/colors/extract
- /api/v1/mood-board/generate
- /api/v1/tokens/graph
- frontend/package.json
- frontend/src/
- frontend/src/App.tsx
- frontend/src/components/overview-narrative/MoodBoard.tsx
- frontend/src/components/overview-narrative/moodBoardTypes.ts
- frontend/src/components/overview-narrative/useMoodBoard.ts
- frontend/src/features/visual-extraction/adapters/ColorVisualAdapter.tsx
- …(+24 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Copy That: Implementation Checklist

### Sources
- `docs/planning/IMPLEMENTATION_CHECKLIST.md`

### Summary
✅ **Zustand Store** (27 tests passing) ✅ **Token Type Registry** (schema-driven) ✅ **5 Wrapper Components** (TokenCard, TokenGrid, TokenToolbar, TokenInspectorSidebar, TokenPlaygroundDrawer) ✅ **App.tsx Integration** (3-column layout) ✅ **Type Safety** (0 errors on pnpm type-check)

✅ **PRD.md** - Product vision (MVP + Phases 2-4) ✅ **TECH_SPECS.md** - Architecture decisions with trade-off analysis ✅ **ROADMAP.md** - 4-week implementation plan (day-by-day) ✅ **2025-11-20_session2_handoff.md** - Quick reference ✅ **2025-11-21_sessions_overview.md** - Context for divergence

**End of Session 3 (after ROADMAP Phase 1 Days 1-5):**

### Key Points
- [ ] POST /api/v1/colors/extract - wire ImageUploader to API
- [ ] POST /api/v1/colors/update - wire edit to API
- [ ] DELETE /api/v1/colors/:id - wire delete to API
- [ ] POST /api/v1/colors/duplicate - wire duplicate to API
- [ ] Error handling for all endpoints
- [ ] Wire store actions to API calls
- [ ] Handle loading states during API calls
- [ ] Error recovery & retry logic
- [ ] Export endpoints (CSS, JSON)
- [ ] Mobile responsive testing

### Implementation Pointers
- `/api/v1/colors/`
- `/api/v1/colors/duplicate`
- `/api/v1/colors/extract`
- `/api/v1/colors/update`
- `frontend/src/components/`
- `frontend/src/store/`
- `pnpm type-check`
- `src/copy_that/`

### Build / Refactor Issues
#### [ ] POST /api/v1/colors/extract - wire ImageUploader to API

**Context**
Source: `docs/planning/IMPLEMENTATION_CHECKLIST.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: [ ] POST /api/v1/colors/extract - wire ImageUploader to API
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/colors/
- /api/v1/colors/duplicate
- /api/v1/colors/extract
- /api/v1/colors/update
- frontend/src/components/
- frontend/src/store/
- pnpm type-check
- src/copy_that/
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### [ ] POST /api/v1/colors/update - wire edit to API

**Context**
Source: `docs/planning/IMPLEMENTATION_CHECKLIST.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: [ ] POST /api/v1/colors/update - wire edit to API
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/colors/
- /api/v1/colors/duplicate
- /api/v1/colors/extract
- /api/v1/colors/update
- frontend/src/components/
- frontend/src/store/
- pnpm type-check
- src/copy_that/
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### [ ] DELETE /api/v1/colors/:id - wire delete to API

**Context**
Source: `docs/planning/IMPLEMENTATION_CHECKLIST.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: [ ] DELETE /api/v1/colors/:id - wire delete to API
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/colors/
- /api/v1/colors/duplicate
- /api/v1/colors/extract
- /api/v1/colors/update
- frontend/src/components/
- frontend/src/store/
- pnpm type-check
- src/copy_that/
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### [ ] POST /api/v1/colors/duplicate - wire duplicate to API

**Context**
Source: `docs/planning/IMPLEMENTATION_CHECKLIST.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: [ ] POST /api/v1/colors/duplicate - wire duplicate to API
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/colors/
- /api/v1/colors/duplicate
- /api/v1/colors/extract
- /api/v1/colors/update
- frontend/src/components/
- frontend/src/store/
- pnpm type-check
- src/copy_that/
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Copy That: Strategic Vision & Architecture

### Sources
- `docs/architecture/STRATEGIC_VISION_AND_ARCHITECTURE.md`

### Summary
**Document Version:** 1.0 **Date:** 2025-11-19 **Status:** Strategic Planning **Author:** Architecture Analysis Session

**Copy That** is evolving from a design token extraction tool into a **comprehensive end-to-end image analysis and generative UI builder platform** with extensive design ontologies and taxonomies.

### Key Points
- AI-powered color token extraction (Claude Sonnet 4.5)
- Educational demo interface (React + Vite)
- FastAPI backend with 70+ extractors
- Multi-platform token generators (17+ platforms)
- Type-safe end-to-end architecture with Pydantic → Zod
- End-to-end image analysis (extract complete design systems from images)
- Generative UI builder (generate production-ready components)
- Comprehensive design ontology library (taxonomies for colors, typography, spacing, components, etc.)
- Multi-platform code generation (React, Flutter, SwiftUI, Material, etc.)
- Design intelligence platform (understand design patterns, generate variations)

### Implementation Pointers
_No explicit code touchpoints referenced in doc._

### Build / Refactor Issues
#### AI-powered color token extraction

**Context**
Source: `docs/architecture/STRATEGIC_VISION_AND_ARCHITECTURE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: AI-powered color token extraction
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Educational demo interface

**Context**
Source: `docs/architecture/STRATEGIC_VISION_AND_ARCHITECTURE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Educational demo interface
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### FastAPI backend with 70+ extractors

**Context**
Source: `docs/architecture/STRATEGIC_VISION_AND_ARCHITECTURE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: FastAPI backend with 70+ extractors
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Multi-platform token generators

**Context**
Source: `docs/architecture/STRATEGIC_VISION_AND_ARCHITECTURE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Multi-platform token generators
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Cross-Reference and Production Readiness Document

### Sources
- `docs/planning/token-pipeline-planning/CROSS_REFERENCE_AND_PRODUCTION_READINESS.md`

### Summary
**Version:** 1.0 | **Date:** 2025-11-22 | **Status:** Planning Document

This document synthesizes all token pipeline planning documentation across branches, providing a unified view of dependencies, implementation timelines, and production readiness requirements.

### Key Points
- **Authentication (Backend)** must complete before Token Pipeline can secure endpoints
- **CV Preprocessing** must complete before Token Pipeline can accept images efficiently
- **Token Factory** provides base classes for Spacing Token implementation
- **Frontend Store** must be optimized before handling large token sets
- [ ] JWT authentication working
- [ ] Secrets in GCP Secret Manager
- [ ] CV async loading operational
- [ ] Token Factory base classes complete
- [ ] CI blocks on security issues
- [ ] Redis caching for extractions

### Implementation Pointers
- `/api/v1/auth/login`
- `/api/v1/spacing/extract`
- `/api/v1/spacing/extract-batch`
- `/api/v1/spacing/extract-streaming`
- `alembic current`
- `alembic downgrade`
- `alembic revision`
- `alembic upgrade`
- `deploy/terraform`
- `src/copy_that/`

### Build / Refactor Issues
#### **Authentication ** must complete before Token Pipeline can secure endpoints

**Context**
Source: `docs/planning/token-pipeline-planning/CROSS_REFERENCE_AND_PRODUCTION_READINESS.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Authentication ** must complete before Token Pipeline can secure endpoints
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/auth/login
- /api/v1/spacing/extract
- /api/v1/spacing/extract-batch
- /api/v1/spacing/extract-streaming
- alembic current
- alembic downgrade
- alembic revision
- alembic upgrade
- deploy/terraform
- src/copy_that/
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **CV Preprocessing** must complete before Token Pipeline can accept images efficiently

**Context**
Source: `docs/planning/token-pipeline-planning/CROSS_REFERENCE_AND_PRODUCTION_READINESS.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **CV Preprocessing** must complete before Token Pipeline can accept images efficiently
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/auth/login
- /api/v1/spacing/extract
- /api/v1/spacing/extract-batch
- /api/v1/spacing/extract-streaming
- alembic current
- alembic downgrade
- alembic revision
- alembic upgrade
- deploy/terraform
- src/copy_that/
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **Token Factory** provides base classes for Spacing Token implementation

**Context**
Source: `docs/planning/token-pipeline-planning/CROSS_REFERENCE_AND_PRODUCTION_READINESS.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Token Factory** provides base classes for Spacing Token implementation
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/auth/login
- /api/v1/spacing/extract
- /api/v1/spacing/extract-batch
- /api/v1/spacing/extract-streaming
- alembic current
- alembic downgrade
- alembic revision
- alembic upgrade
- deploy/terraform
- src/copy_that/
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **Frontend Store** must be optimized before handling large token sets

**Context**
Source: `docs/planning/token-pipeline-planning/CROSS_REFERENCE_AND_PRODUCTION_READINESS.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Frontend Store** must be optimized before handling large token sets
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/auth/login
- /api/v1/spacing/extract
- /api/v1/spacing/extract-batch
- /api/v1/spacing/extract-streaming
- alembic current
- alembic downgrade
- alembic revision
- alembic upgrade
- deploy/terraform
- src/copy_that/
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Design Token System

### Sources
- `docs/domain/TOKEN_SYSTEM.md`

### Summary
**Version:** 3.1 (Adapted for Copy That) | **Last Updated:** 2025-11-19

This document describes the complete design token system used by Copy That - the foundational language for extracting, representing, and generating design systems from images.

### Key Points
- **Value** - The actual design decision (e.g., #FF6B35)
- **Name** - Semantic label (e.g., "primary-brand-color")
- **Category** - Token type (color, spacing, typography, etc.)
- **Context** - Where and how it's used
- **Metadata** - Confidence, source, relationships
- AI ANALYSIS (Claude Structured Outputs)
- Visual consistency across the design system
- Clear naming conventions (semantic names)
- Accessibility validation (WCAG contrast ratios)
- Color harmonies and relationships

### Implementation Pointers
- `/api/v1/jobs/123/colors`
- `/api/v1/jobs/123/export`
- `/api/v1/tokens/color-primary`

### Build / Refactor Issues
#### **Value** - The actual design decision

**Context**
Source: `docs/domain/TOKEN_SYSTEM.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Value** - The actual design decision
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/jobs/123/colors
- /api/v1/jobs/123/export
- /api/v1/tokens/color-primary
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **Name** - Semantic label

**Context**
Source: `docs/domain/TOKEN_SYSTEM.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Name** - Semantic label
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/jobs/123/colors
- /api/v1/jobs/123/export
- /api/v1/tokens/color-primary
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **Category** - Token type

**Context**
Source: `docs/domain/TOKEN_SYSTEM.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Category** - Token type
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/jobs/123/colors
- /api/v1/jobs/123/export
- /api/v1/tokens/color-primary
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **Context** - Where and how it's used

**Context**
Source: `docs/domain/TOKEN_SYSTEM.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Context** - Where and how it's used
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/jobs/123/colors
- /api/v1/jobs/123/export
- /api/v1/tokens/color-primary
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Documentation Library (Curated)

### Sources
- `docs/overview/library_index.md`

### Summary
Use this as the single entry point. Prefer the newest items; legacy references live under `archive/meta` and `archive/pipeline/historical` (sessions/ops history). Consolidated legacy summaries are under `overview/strategy/legacy_summary.md`, `workflows/extraction_legacy/readme.md`, `workflows/tokens_legacy/readme.md`, `design/legacy/readme.md`, `testing/legacy/readme.md`, and `ops/history/readme.md`.

### Key Points
- PRD.md, TECH_SPEC.md, ROADMAP.md
- architecture_decisions.md — ADRs
- overview/documentation.md, overview/library_index.md (this file)
- 2025-11-21_sessions_overview.md — stream convergence context
- architecture/architecture/architecture_overview.md, architecture/architecture/architecture_pipeline.md
- architecture/strategic_vision_and_architecture.md, architecture/modular_token_platform_vision.md
- architecture/schema_architecture_diagram.md, architecture/component_token_schema.md
- Patterns: architecture/adapter_pattern.md, architecture/extractor_patterns.md, architecture/plugin_architecture.md
- Domain: domain/token_system.md
- setup/setup/start_here.md, setup/setup/setup_minimal.md

### Implementation Pointers
- `deploy/rollback/migrations/secrets`

### Build / Refactor Issues
#### PRD.md, TECH_SPEC.md, ROADMAP.md

**Context**
Source: `docs/overview/library_index.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: PRD.md, TECH_SPEC.md, ROADMAP.md
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- deploy/rollback/migrations/secrets
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### architecture_decisions.md — ADRs

**Context**
Source: `docs/overview/library_index.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: architecture_decisions.md — ADRs
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- deploy/rollback/migrations/secrets
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### overview/documentation.md, overview/library_index.md

**Context**
Source: `docs/overview/library_index.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: overview/documentation.md, overview/library_index.md
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- deploy/rollback/migrations/secrets
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### 2025-11-21_sessions_overview.md — stream convergence context

**Context**
Source: `docs/overview/library_index.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: 2025-11-21_sessions_overview.md — stream convergence context
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- deploy/rollback/migrations/secrets
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Educational Color Extraction Layout - Implementation Complete

### Sources
- `docs/design/EDUCATIONAL_LAYOUT_IMPLEMENTATION.md`

### Summary
Redesigned the color extraction page from a simple two-column layout to a comprehensive three-column educational interface that combines results display, learning resources, and interactive playground tools.

| File | Change | Type | |------|--------|------| | App.tsx | Import EducationalColorDisplay instead of ColorTokenDisplay | Edit | | App.css | Add .educational-display full-height styling | Edit | | EducationalColorDisplay.tsx | NEW - Main layout component | Create | | EducationalColorDisplay.css | NEW - Layout styles | Create | | CompactColorGrid.tsx | NEW - Results grid component | Create | | CompactColorGrid.css | NEW - Grid styles | Create | | LearningSidebar.tsx | NEW - Learning sidebar component | Create | | LearningSidebar.css | NEW - Sidebar styles | Create | | PlaygroundSidebar.tsx | NEW - Playground sidebar component | Create | | PlaygroundSidebar.css | NEW - Playground styles | Create |

### Key Points
- Three-column grid layout
- Manages sidebar toggle states
- Coordinates color selection between grid and playground
- **File**: frontend/src/components/EducationalColorDisplay.tsx
- **CSS**: EducationalColorDisplay.css
- **Purpose**: Dense, scannable color palette display
- 5-column responsive grid
- Inline attributes per color (name, hex, confidence, temperature, saturation)
- Quick copy-to-clipboard for hex codes
- Prominence badges (occurrence count)

### Implementation Pointers
- `frontend/src/components/`
- `frontend/src/components/CompactColorGrid.tsx`
- `frontend/src/components/EducationalColorDisplay.tsx`
- `frontend/src/components/LearningSidebar.tsx`
- `frontend/src/components/PlaygroundSidebar.tsx`

### Build / Refactor Issues
#### Three-column grid layout

**Context**
Source: `docs/design/EDUCATIONAL_LAYOUT_IMPLEMENTATION.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Three-column grid layout
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/src/components/
- frontend/src/components/CompactColorGrid.tsx
- frontend/src/components/EducationalColorDisplay.tsx
- frontend/src/components/LearningSidebar.tsx
- frontend/src/components/PlaygroundSidebar.tsx
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Manages sidebar toggle states

**Context**
Source: `docs/design/EDUCATIONAL_LAYOUT_IMPLEMENTATION.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Manages sidebar toggle states
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/src/components/
- frontend/src/components/CompactColorGrid.tsx
- frontend/src/components/EducationalColorDisplay.tsx
- frontend/src/components/LearningSidebar.tsx
- frontend/src/components/PlaygroundSidebar.tsx
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Coordinates color selection between grid and playground

**Context**
Source: `docs/design/EDUCATIONAL_LAYOUT_IMPLEMENTATION.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Coordinates color selection between grid and playground
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/src/components/
- frontend/src/components/CompactColorGrid.tsx
- frontend/src/components/EducationalColorDisplay.tsx
- frontend/src/components/LearningSidebar.tsx
- frontend/src/components/PlaygroundSidebar.tsx
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **File**: frontend/src/components/EducationalColorDisplay.tsx

**Context**
Source: `docs/design/EDUCATIONAL_LAYOUT_IMPLEMENTATION.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **File**: frontend/src/components/EducationalColorDisplay.tsx
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/src/components/
- frontend/src/components/CompactColorGrid.tsx
- frontend/src/components/EducationalColorDisplay.tsx
- frontend/src/components/LearningSidebar.tsx
- frontend/src/components/PlaygroundSidebar.tsx
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Extractor Patterns & Best Practices

### Sources
- `docs/architecture/EXTRACTOR_PATTERNS.md`

### Summary
**Version:** 1.0 | **Date:** 2025-11-19 | **Status:** Guide

This document describes the architecture patterns for building token extractors in Copy That.

### Key Points
- Load image from bytes
- Convert to RGB if needed
- Reshape to pixels array
- Run K-means clustering
- Extract cluster centers (colors)
- Get extractor from registry
- Create extraction job
- Store results in database
- **token_system.md** - Token types and structure
- **adapter_pattern.md** - Schema transformation

### Implementation Pointers
- `/api/v1/extract/`

### Build / Refactor Issues
#### Load image from bytes

**Context**
Source: `docs/architecture/EXTRACTOR_PATTERNS.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Load image from bytes
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/extract/
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Convert to RGB if needed

**Context**
Source: `docs/architecture/EXTRACTOR_PATTERNS.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Convert to RGB if needed
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/extract/
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Reshape to pixels array

**Context**
Source: `docs/architecture/EXTRACTOR_PATTERNS.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Reshape to pixels array
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/extract/
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Run K-means clustering

**Context**
Source: `docs/architecture/EXTRACTOR_PATTERNS.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Run K-means clustering
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/extract/
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Frontend Setup Guide

### Sources
- `docs/guides/FRONTEND_SETUP.md`

### Summary
**Version:** 1.0 | **Date:** 2025-11-19 | **Status:** Complete

Complete guide to setting up and running the Copy That React frontend.

### Key Points
- **Node.js** 18+ (20+ recommended)
- **npm** or **pnpm** (pnpm 8+ recommended for speed)
- **Git** for version control
- Copy That repository cloned
- **React 18** - UI framework
- **Vite 5** - Build tool (10-100x faster than Webpack)
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS
- **CSS Modules** - Component-scoped styles
- **Fetch API** - Built-in, no dependencies

### Implementation Pointers
- `/api/v1/db-test`
- `/api/v1/extract/color`
- `/api/v1/jobs`
- `/api/v1/jobs/`
- `/api/v1/jobs/1/colors`
- `frontend/.env.local`
- `pnpm 8`
- `pnpm build`
- `pnpm dev`
- `pnpm format`
- `pnpm generate`
- `pnpm install`
- `pnpm instead`
- `pnpm is`
- `pnpm lint`
- `pnpm preview`
- `pnpm test`
- `pnpm typecheck`
- `src/api/client.ts`
- `src/components/ColorTokenCard.tsx`
- `src/components/Special.module.css`
- `src/components/Special.tsx`
- `src/components/TokenList.tsx`
- `src/types/generated/color.ts`
- `src/types/generated/spacing.ts`

### Build / Refactor Issues
#### **Node.js** 18+

**Context**
Source: `docs/guides/FRONTEND_SETUP.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Node.js** 18+
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/db-test
- /api/v1/extract/color
- /api/v1/jobs
- /api/v1/jobs/
- /api/v1/jobs/1/colors
- frontend/.env.local
- pnpm 8
- pnpm build
- pnpm dev
- pnpm format
- …(+15 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **npm** or **pnpm**

**Context**
Source: `docs/guides/FRONTEND_SETUP.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **npm** or **pnpm**
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/db-test
- /api/v1/extract/color
- /api/v1/jobs
- /api/v1/jobs/
- /api/v1/jobs/1/colors
- frontend/.env.local
- pnpm 8
- pnpm build
- pnpm dev
- pnpm format
- …(+15 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **Git** for version control

**Context**
Source: `docs/guides/FRONTEND_SETUP.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Git** for version control
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/db-test
- /api/v1/extract/color
- /api/v1/jobs
- /api/v1/jobs/
- /api/v1/jobs/1/colors
- frontend/.env.local
- pnpm 8
- pnpm build
- pnpm dev
- pnpm format
- …(+15 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Copy That repository cloned

**Context**
Source: `docs/guides/FRONTEND_SETUP.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Copy That repository cloned
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/db-test
- /api/v1/extract/color
- /api/v1/jobs
- /api/v1/jobs/
- /api/v1/jobs/1/colors
- frontend/.env.local
- pnpm 8
- pnpm build
- pnpm dev
- pnpm format
- …(+15 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Frontend State Management & Performance Review

### Sources
- `docs/reviews/FRONTEND_STATE_PERFORMANCE_REVIEW.md`

### Summary
**Date:** 2025-12-09 **Reviewer:** Frontend Performance Specialist **Codebase:** Copy That v3.5.0 **Previous Reviews:** UI/UX Designer, Web Developer

This review builds on previous agent findings to provide a comprehensive analysis of state management architecture, performance bottlenecks, and re-rendering patterns. The frontend exhibits a **fragmented state architecture** with three competing Zustand stores, significant prop drilling through App.tsx (646 LOC god component), and zero performance optimizations (no memo, lazy loading, or code splitting).

### Key Points
- **Bundle Size:** 390KB (112KB gzipped) - single monolithic chunk
- **Component Files:** 184 TypeScript files
- **State Management:** 3 Zustand stores with overlapping responsibilities
- **Store Usage:** 48 direct store subscriptions across components
- **getState() Calls:** 48 instances (anti-pattern for reactivity)
- **Performance Optimizations:** 0 (no React.memo, lazy, or useMemo/useCallback)
- **Re-render Risk:** HIGH (25+ useState in App.tsx, unoptimized selectors)
- load(projectId) - Loads full W3C token graph from API
- legacyColors() - Transforms W3C to legacy format (adapter method)
- legacySpacing() - Transforms W3C to legacy format (adapter method)

### Implementation Pointers
- `frontend/package.json`
- `frontend/src`
- `frontend/src/App.tsx`
- `frontend/src/components`
- `frontend/src/components/`
- `frontend/src/components/ColorTokenDisplay.tsx`
- `frontend/src/components/diagnostics-panel/hooks.ts`
- `frontend/src/components/image-uploader/ImageUploader.tsx`
- `frontend/src/components/image-uploader/hooks.ts`
- `frontend/src/components/overview-narrative/hooks.ts`
- `frontend/src/components/primitives/`
- `frontend/src/store/index.ts`
- `frontend/src/store/shadowStore.ts`
- `frontend/src/store/tokenGraphStore.ts`
- `frontend/src/store/tokenStore.ts`
- `frontend/vite.config.ts`
- `src/components/ColorDetailPanel`
- `src/components/ColorTokenDisplay`
- `src/components/SpacingGapDemo`
- `src/components/SpacingRuler`
- `src/features/`
- `src/features/colors/ColorsTab`
- `src/features/spacing/SpacingTab`

### Build / Refactor Issues
#### **Bundle Size:** 390KB  - single monolithic chunk

**Context**
Source: `docs/reviews/FRONTEND_STATE_PERFORMANCE_REVIEW.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Bundle Size:** 390KB  - single monolithic chunk
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/package.json
- frontend/src
- frontend/src/App.tsx
- frontend/src/components
- frontend/src/components/
- frontend/src/components/ColorTokenDisplay.tsx
- frontend/src/components/diagnostics-panel/hooks.ts
- frontend/src/components/image-uploader/ImageUploader.tsx
- frontend/src/components/image-uploader/hooks.ts
- frontend/src/components/overview-narrative/hooks.ts
- …(+13 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **Component Files:** 184 TypeScript files

**Context**
Source: `docs/reviews/FRONTEND_STATE_PERFORMANCE_REVIEW.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Component Files:** 184 TypeScript files
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/package.json
- frontend/src
- frontend/src/App.tsx
- frontend/src/components
- frontend/src/components/
- frontend/src/components/ColorTokenDisplay.tsx
- frontend/src/components/diagnostics-panel/hooks.ts
- frontend/src/components/image-uploader/ImageUploader.tsx
- frontend/src/components/image-uploader/hooks.ts
- frontend/src/components/overview-narrative/hooks.ts
- …(+13 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **State Management:** 3 Zustand stores with overlapping responsibilities

**Context**
Source: `docs/reviews/FRONTEND_STATE_PERFORMANCE_REVIEW.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **State Management:** 3 Zustand stores with overlapping responsibilities
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/package.json
- frontend/src
- frontend/src/App.tsx
- frontend/src/components
- frontend/src/components/
- frontend/src/components/ColorTokenDisplay.tsx
- frontend/src/components/diagnostics-panel/hooks.ts
- frontend/src/components/image-uploader/ImageUploader.tsx
- frontend/src/components/image-uploader/hooks.ts
- frontend/src/components/overview-narrative/hooks.ts
- …(+13 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### **Store Usage:** 48 direct store subscriptions across components

**Context**
Source: `docs/reviews/FRONTEND_STATE_PERFORMANCE_REVIEW.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: **Store Usage:** 48 direct store subscriptions across components
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/package.json
- frontend/src
- frontend/src/App.tsx
- frontend/src/components
- frontend/src/components/
- frontend/src/components/ColorTokenDisplay.tsx
- frontend/src/components/diagnostics-panel/hooks.ts
- frontend/src/components/image-uploader/ImageUploader.tsx
- frontend/src/components/image-uploader/hooks.ts
- frontend/src/components/overview-narrative/hooks.ts
- …(+13 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

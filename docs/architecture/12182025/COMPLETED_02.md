# Completed

## Adapter Pattern: Schema Transformation

### Sources
- `docs/architecture/ADAPTER_PATTERN.md`

### Summary
**Version:** 1.0 | **Date:** 2025-11-19 | **Status:** Guide

This document explains the Adapter pattern used to transform tokens between different schema layers in Copy That.

### Key Points
- ✅ Remove sensitive fields
- ✅ Transform field names
- ✅ Maintain type safety
- semantic_name: Human-readable color name
- created_at: Timestamp
- metadata: Extra color analysis
- Extract → Core schema
- Adapt → API schema (enrichment)
- Store → Database schema
- [ ] Create **Core Schema** (minimal, validated)

### Implementation Pointers
- `/api/v1/extract/color`
- `/api/v1/jobs/`

### Build / Refactor Issues
#### Harden/regression-test: ✅ Remove sensitive fields

**Context**
Source: `docs/architecture/ADAPTER_PATTERN.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: ✅ Remove sensitive fields
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/extract/color
- /api/v1/jobs/
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Harden/regression-test: ✅ Transform field names

**Context**
Source: `docs/architecture/ADAPTER_PATTERN.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: ✅ Transform field names
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/extract/color
- /api/v1/jobs/
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## API Reference

### Sources
- `docs/guides/API_REFERENCE.md`

### Summary
**Version:** 1.0 | **Date:** 2025-11-19 | **Status:** Complete

Complete reference for Copy That REST API endpoints.

### Key Points
- skip (int, default: 0) - Number of projects to skip
- limit (int, default: 10) - Number of projects to return
- project_id (int, required) - Project ID
- source_url (string, required) - Image URL or path
- extraction_type (string, required) - Token type: color, spacing, typography, all
- pending - Waiting to start
- processing - Currently extracting
- completed - Finished successfully
- failed - Error occurred
- confidence_min (float, default: 0.0) - Minimum confidence threshold

### Implementation Pointers
- `/api/v1/db-test`
- `/api/v1/extract/colors`
- `/api/v1/extract/spacing`
- `/api/v1/extract/typography`
- `/api/v1/jobs`
- `/api/v1/jobs/`
- `/api/v1/jobs/1/colors`
- `/api/v1/projects`
- `/api/v1/projects/`
- `/api/v1/tokens`
- `/api/v1/tokens/color/`
- `/api/v1/tokens/search`

### Build / Refactor Issues
#### Harden/regression-test: skip  - Number of projects to skip

**Context**
Source: `docs/guides/API_REFERENCE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: skip  - Number of projects to skip
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/db-test
- /api/v1/extract/colors
- /api/v1/extract/spacing
- /api/v1/extract/typography
- /api/v1/jobs
- /api/v1/jobs/
- /api/v1/jobs/1/colors
- /api/v1/projects
- /api/v1/projects/
- /api/v1/tokens
- …(+2 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Harden/regression-test: limit  - Number of projects to return

**Context**
Source: `docs/guides/API_REFERENCE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: limit  - Number of projects to return
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/db-test
- /api/v1/extract/colors
- /api/v1/extract/spacing
- /api/v1/extract/typography
- /api/v1/jobs
- /api/v1/jobs/
- /api/v1/jobs/1/colors
- /api/v1/projects
- /api/v1/projects/
- /api/v1/tokens
- …(+2 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Claude Code Cost Optimization Guide

### Sources
- `docs/ops/cost_optimization.md`

### Summary
**Current Situation**: $100+/day → **Target**: $20-40/day (60-80% savings)

### Key Points
- ✅ After completing a feature
- ✅ Before starting unrelated work
- ✅ When approaching 100K tokens
- Keep sessions under 50K tokens
- Use 3-4 focused sessions per day instead of 1 mega-session
- /clear between unrelated work
- Sonnet: $3/MTok input, $15/MTok output
- **Haiku: $0.25/MTok input, $1.25/MTok output** (12x cheaper!)
- Complex architectural decisions
- Multi-file coordinated changes

### Implementation Pointers
_No explicit code touchpoints referenced in doc._

### Build / Refactor Issues
#### Harden/regression-test: ✅ After completing a feature

**Context**
Source: `docs/ops/cost_optimization.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: ✅ After completing a feature
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Harden/regression-test: ✅ Before starting unrelated work

**Context**
Source: `docs/ops/cost_optimization.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: ✅ Before starting unrelated work
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Claude Structured Outputs: Complete Implementation Guide

### Sources
- `docs/configuration/claude_structured_output_usage.md`

### Summary
**Structured Outputs** guarantees that Claude's API responses match your exact JSON schema through constrained decoding. Released November 14, 2025 in public beta for Claude Sonnet 4.5 and Opus 4.1.

**Key Benefit:** Zero parsing errors, no retry logic, guaranteed schema compliance.

### Key Points
- Automatic schema transformation (removes unsupported constraints)
- Built-in validation against original Pydantic model
- Returns typed parsed_output instead of raw JSON
- Agentic workflows requiring reliable function calls
- API integrations where parameter validation is critical
- Multi-step reasoning with guaranteed tool compliance
- Basic types: string, number, boolean, integer, null, array, object
- Enums with string/number/boolean values
- Simple $ref (within same schema)
- Nested objects and arrays

### Implementation Pointers
_No explicit code touchpoints referenced in doc._

### Build / Refactor Issues
#### Harden/regression-test: Automatic schema transformation

**Context**
Source: `docs/configuration/claude_structured_output_usage.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: Automatic schema transformation
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Harden/regression-test: Built-in validation against original Pydantic model

**Context**
Source: `docs/configuration/claude_structured_output_usage.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: Built-in validation against original Pydantic model
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Color Token Pipeline - Complete Visual Implementation

### Sources
- `docs/COLOR_PIPELINE_VISUALIZATION.md`

### Summary
**Date:** December 10, 2025 **Status:** ✅ Complete - Every algorithm has visual frontend component **Components Added:** 2 new detail tabs **Total Color Pipeline Components:** 9 visual tabs

The color extraction pipeline now has complete visual coverage. Every step in the color analysis algorithm has a corresponding frontend component that displays the results, making the entire pipeline transparent and explorable.

### Key Points
- Hex, RGB, HSL, HSV values
- Prominence percentage & bar visualization
- ✅ hex_to_rgb() - Color space conversion
- ✅ hex_to_hsl() - Color space conversion
- ✅ hex_to_hsv() - Color space conversion
- Closest web-safe color
- Delta-E to dominant color
- Tint/Shade/Tone variants
- ✅ get_saturation_level() - Color analysis
- ✅ get_lightness_level() - Color analysis

### Implementation Pointers
- `pnpm type-check`

### Build / Refactor Issues
#### Harden/regression-test: Hex, RGB, HSL, HSV values

**Context**
Source: `docs/COLOR_PIPELINE_VISUALIZATION.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: Hex, RGB, HSL, HSV values
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

#### Harden/regression-test: Prominence percentage & bar visualization

**Context**
Source: `docs/COLOR_PIPELINE_VISUALIZATION.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: Prominence percentage & bar visualization
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

## ColorAide Features: Current Usage Analysis

### Sources
- `docs/configuration/coloraide_feature_analysis.md`

### Summary
**Document Version:** 1.0 **Date:** 2025-11-20 **Status:** Phase 4 Week 1 **ColorAide Version:** 6.0 (installed)

Copy That uses coloraide v6.0 for **perceptually-uniform color space conversions and analysis**. We're using ~15% of coloraide's capabilities, with significant untapped potential for future enhancement.

### Key Points
- ✅ **sRGB** - Standard RGB color space (primary output format)
- ✅ **Oklch** - Perceptually uniform cylindrical space (main innovation)
- ✅ **OkLab** - Perceptually uniform rectangular space
- ✅ **LAB** - CIELAB perceptual space (Delta-E 2000)
- ✅ **HSL** - Hue-Saturation-Lightness (fallback/legacy)
- ✅ **HSLuv** - Perceptually uniform HSL alternative
- ✅ **Channel Indexing** - color["lightness"], color["chroma"], color["hue"], color["a"], color["b"]
- ✅ **Coordinate Tuples** - .coords() method for extracting RGB values
- ✅ **Hex String** - .to_string(hex=True) produces #RRGGBB
- ✅ **Color Construction** - Color(hex_string) and Color("oklch", [l, c, h])

### Implementation Pointers
- `src/copy_that/application/color_extractor.py`
- `src/copy_that/application/color_spaces_advanced.py`
- `src/copy_that/application/color_utils.py`
- `src/copy_that/application/tests/test_delta_e_merging.py`

### Build / Refactor Issues
#### Harden/regression-test: ✅ **sRGB** - Standard RGB color space

**Context**
Source: `docs/configuration/coloraide_feature_analysis.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: ✅ **sRGB** - Standard RGB color space
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- src/copy_that/application/color_extractor.py
- src/copy_that/application/color_spaces_advanced.py
- src/copy_that/application/color_utils.py
- src/copy_that/application/tests/test_delta_e_merging.py
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Harden/regression-test: ✅ **Oklch** - Perceptually uniform cylindrical space

**Context**
Source: `docs/configuration/coloraide_feature_analysis.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: ✅ **Oklch** - Perceptually uniform cylindrical space
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- src/copy_that/application/color_extractor.py
- src/copy_that/application/color_spaces_advanced.py
- src/copy_that/application/color_utils.py
- src/copy_that/application/tests/test_delta_e_merging.py
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## ColorAide Integration Across Color Pipeline

### Sources
- `docs/workflows/coloraide_integration.md`

### Summary
ColorAide is integrated throughout the color token extraction pipeline as the **authoritative color science library**. It provides industry-standard algorithms for perceptual color analysis and harmony detection.

### Key Points
- **Perceptual Uniformity** (Delta-E)
- Industry standard: CIEDE2000
- Used for: Color similarity detection, palette merging, nearest-color matching
- Threshold-based: ΔE < 2 (barely noticeable), < 5 (similar), < 15 (distinct)
- **Luminance Calculation** (WCAG 2.1)
- Accurate relative luminance using relative luminosity formula
- Used for: Contrast ratio calculation, WCAG AA/AAA compliance checking
- Replaces manual gamma correction (ColorAide handles all color space conversions)
- **Achromatic Detection**
- Detects colors with zero saturation (true grayscale)

### Implementation Pointers
- `frontend/src/types/generated/color.zod.ts`
- `src/copy_that/application/color_extractor.py`
- `src/copy_that/application/color_utils.py`
- `src/copy_that/domain/models.py`
- `src/copy_that/interfaces/api/schemas.py`

### Build / Refactor Issues
#### Harden/regression-test: **Perceptual Uniformity**

**Context**
Source: `docs/workflows/coloraide_integration.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: **Perceptual Uniformity**
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/src/types/generated/color.zod.ts
- src/copy_that/application/color_extractor.py
- src/copy_that/application/color_utils.py
- src/copy_that/domain/models.py
- src/copy_that/interfaces/api/schemas.py
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Harden/regression-test: Industry standard: CIEDE2000

**Context**
Source: `docs/workflows/coloraide_integration.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: Industry standard: CIEDE2000
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/src/types/generated/color.zod.ts
- src/copy_that/application/color_extractor.py
- src/copy_that/application/color_utils.py
- src/copy_that/domain/models.py
- src/copy_that/interfaces/api/schemas.py
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Copy That - Minimalist Design Guide

### Sources
- `docs/design/minimalist_design_guide.md`

### Summary
**Version:** 1.0 **Date:** 2025-11-20 **Focus:** Focused, clean, stylish frontend design system

This guide documents the minimalist design system for Copy That's frontend. The system emphasizes:

`src/design/tokens.css` - Master CSS variables file

### Key Points
- **Single source of truth** - All colors/spacing via CSS variables
- **Progressive disclosure** - Hide complexity, show on demand
- **Visual clarity** - Simplified gradients, minimal shadows
- **Type safety** - Centralized type definitions
- **Maintainability** - No duplicated design values
- [ ] Replace all linear-gradient(135deg, #xxx, #yyy) → var(--gradient-accent) or var(--gradient-bg)
- [ ] Replace rgba(255, 255, 255, 0.87) → var(--color-text-primary)
- [ ] Replace rgba(255, 255, 255, 0.60) → var(--color-text-secondary)
- [ ] Replace #667eea → var(--color-accent-primary)
- [ ] Replace #764ba2 → var(--color-accent-secondary)

### Implementation Pointers
- `pnpm dev`
- `pnpm typecheck`
- `src/App.css`
- `src/components/`
- `src/components/AccessibilityVisualizer.css`
- `src/components/ColorDetailsPanel.css`
- `src/components/ColorNarrative.css`
- `src/components/CompactColorGrid.css`
- `src/components/EducationalColorDisplay.css`
- `src/components/HarmonyVisualizer.css`
- `src/components/ImageUploader.css`
- `src/components/PlaygroundSidebar.css`
- `src/design/tokens.css`
- `src/index.css`
- `src/types/index.ts`

### Build / Refactor Issues
#### Harden/regression-test: **Single source of truth** - All colors/spacing via CSS variables

**Context**
Source: `docs/design/minimalist_design_guide.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: **Single source of truth** - All colors/spacing via CSS variables
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- pnpm dev
- pnpm typecheck
- src/App.css
- src/components/
- src/components/AccessibilityVisualizer.css
- src/components/ColorDetailsPanel.css
- src/components/ColorNarrative.css
- src/components/CompactColorGrid.css
- src/components/EducationalColorDisplay.css
- src/components/HarmonyVisualizer.css
- …(+5 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Harden/regression-test: **Progressive disclosure** - Hide complexity, show on demand

**Context**
Source: `docs/design/minimalist_design_guide.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: **Progressive disclosure** - Hide complexity, show on demand
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- pnpm dev
- pnpm typecheck
- src/App.css
- src/components/
- src/components/AccessibilityVisualizer.css
- src/components/ColorDetailsPanel.css
- src/components/ColorNarrative.css
- src/components/CompactColorGrid.css
- src/components/EducationalColorDisplay.css
- src/components/HarmonyVisualizer.css
- …(+5 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Database Setup Guide

### Sources
- `docs/setup/database_setup.md`

### Summary
This guide documents the Neon PostgreSQL database setup for Copy That.

Copy That uses **Neon** as its PostgreSQL database provider with:

### Key Points
- Async database operations (SQLAlchemy + asyncpg)
- Type-safe ORM with SQLAlchemy 2.0
- Database migrations via Alembic
- Connection pooling for production workloads
- Async engine with connection pooling
- Session factory for dependency injection
- Base class for all models
- SQLAlchemy ORM models
- Type hints via Mapped and mapped_column
- Auto-detects schema changes from models

### Implementation Pointers
- `/api/v1/db-test`
- `/api/v1/projects`
- `alembic current`
- `alembic downgrade`
- `alembic history`
- `alembic revision`
- `alembic stamp`
- `alembic upgrade`
- `src/copy_that/domain/models.py`
- `src/copy_that/infrastructure/database.py`

### Build / Refactor Issues
#### Harden/regression-test: Async database operations

**Context**
Source: `docs/setup/database_setup.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: Async database operations
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/db-test
- /api/v1/projects
- alembic current
- alembic downgrade
- alembic history
- alembic revision
- alembic stamp
- alembic upgrade
- src/copy_that/domain/models.py
- src/copy_that/infrastructure/database.py
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Harden/regression-test: Type-safe ORM with SQLAlchemy 2.0

**Context**
Source: `docs/setup/database_setup.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: Type-safe ORM with SQLAlchemy 2.0
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/db-test
- /api/v1/projects
- alembic current
- alembic downgrade
- alembic history
- alembic revision
- alembic stamp
- alembic upgrade
- src/copy_that/domain/models.py
- src/copy_that/infrastructure/database.py
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Deployment Options

### Sources
- `docs/setup/deployment_options.md`

### Summary
Choose the right infrastructure setup for your needs.

| | **Local** | **Minimal Cloud** | **Full Cloud** | |---|-----------|------------------|----------------| | **Cost** | FREE | $0-5/month | $30-70/month | | **Setup Time** | 5 min | 30 min | 60 min | | **Best For** | Development | Personal/Demo | Production | | **Public URL** | ❌ No | ✅ Yes | ✅ Yes | | **Database** | Local Postgres | Neon.tech (free) | Cloud SQL (private) | | **Redis** | Local Redis | Upstash (free) | Memorystore (private) | | **Networking** | localhost | Public internet | Private VPC | | **Compliance** | N/A | Basic | Enterprise | | **Scalability** | Single machine | 0-5 instances | 0-100 instances | | **Teardown** | Stop containers | `terraform destroy` | `terraform destroy` |

### Key Points
- Learning the codebase
- ❌ Can't share with others
- ❌ Requires local machine running
- ❌ Limited by laptop resources
- Sharing with family/friends
- Budget-conscious deployment
- ✅ Public URL to share
- ✅ Auto-scaling (0-5 instances)
- ✅ Quick setup (30 min)
- ✅ Secure for personal use

### Implementation Pointers
- `deploy/terraform`

### Build / Refactor Issues
#### Harden/regression-test: Learning the codebase

**Context**
Source: `docs/setup/deployment_options.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: Learning the codebase
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- deploy/terraform
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Harden/regression-test: ❌ Can't share with others

**Context**
Source: `docs/setup/deployment_options.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: ❌ Can't share with others
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- deploy/terraform
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Design Tokens - Quick Reference

### Sources
- `docs/DESIGN_TOKENS_QUICK_REFERENCE.md`

### Summary
_No narrative prose found; see Key Points._

### Key Points
- Extract colors from images (AI + CV)
- Extract spacing/padding from images (AI + CV)
- Grid alignment detection
- 11 API tests + comprehensive coverage
- Implement detect_shadows() in shadow_extractor.py
- Create ShadowToken table migration
- Add service: build_shadow_repo_from_db()
- Add API: POST /api/v1/shadows/extract
- Wire into extraction job system
- Implement detect_fonts() + detect_sizes() in typography_extractor.py

### Implementation Pointers
- `/api/v1/borders/extract`
- `/api/v1/colors/`
- `/api/v1/colors/extract`
- `/api/v1/design-tokens/export/w3c`
- `/api/v1/grid/extract`
- `/api/v1/layout/extract`
- `/api/v1/shadows`
- `/api/v1/shadows/extract`
- `/api/v1/spacing/`
- `/api/v1/spacing/extract`
- `/api/v1/typography/extract`
- `src/copy_that/application/layout_extractor.py`
- `src/copy_that/application/shadow_extractor.py`
- `src/copy_that/application/typography_extractor.py`
- `src/copy_that/domain/models.py`
- `src/copy_that/interfaces/api/design_tokens.py`
- `src/copy_that/interfaces/api/shadows.py`
- `src/copy_that/services/layout_service.py`
- `src/copy_that/services/shadow_service.py`
- `src/copy_that/services/typography_service.py`

### Build / Refactor Issues
#### Harden/regression-test: Extract colors from images

**Context**
Source: `docs/DESIGN_TOKENS_QUICK_REFERENCE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: Extract colors from images
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/borders/extract
- /api/v1/colors/
- /api/v1/colors/extract
- /api/v1/design-tokens/export/w3c
- /api/v1/grid/extract
- /api/v1/layout/extract
- /api/v1/shadows
- /api/v1/shadows/extract
- /api/v1/spacing/
- /api/v1/spacing/extract
- …(+10 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Harden/regression-test: Extract spacing/padding from images

**Context**
Source: `docs/DESIGN_TOKENS_QUICK_REFERENCE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: Extract spacing/padding from images
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/borders/extract
- /api/v1/colors/
- /api/v1/colors/extract
- /api/v1/design-tokens/export/w3c
- /api/v1/grid/extract
- /api/v1/layout/extract
- /api/v1/shadows
- /api/v1/shadows/extract
- /api/v1/spacing/
- /api/v1/spacing/extract
- …(+10 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Design Tokens W3C Implementation Status

### Sources
- `docs/DESIGN_TOKENS_W3C_STATUS.md`

### Summary
**Last Updated:** December 2, 2025 **Status:** 50% Complete (2/4 major token types fully implemented)

### Key Points
- OKLCH color space (40% better uniformity vs HSL)
- Semantic color naming (primary, secondary, accent, etc.)
- Temperature & saturation analysis
- WCAG contrast scoring
- Accent ramp generation
- Dual unit support (px + rem conversion)
- Grid alignment detection (4pt, 8pt scales)
- Base unit recognition
- Responsive scale detection
- Named semantic roles (xs, sm, md, lg, xl)

### Implementation Pointers
- `/api/v1/colors`
- `/api/v1/colors/`
- `/api/v1/colors/extract`
- `/api/v1/design-tokens/export/w3c`
- `/api/v1/grid`
- `/api/v1/grid/extract`
- `/api/v1/layout`
- `/api/v1/layout/extract`
- `/api/v1/shadows/extract`
- `/api/v1/spacing`
- `/api/v1/spacing/`
- `/api/v1/spacing/extract`
- `/api/v1/typography/extract`
- `src/copy_that/application/`
- `src/copy_that/domain/models.py`
- `src/copy_that/interfaces/api/`
- `src/copy_that/services/`
- `src/core/tokens/`
- `src/core/tokens/model.py`

### Build / Refactor Issues
#### Harden/regression-test: OKLCH color space

**Context**
Source: `docs/DESIGN_TOKENS_W3C_STATUS.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: OKLCH color space
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/colors
- /api/v1/colors/
- /api/v1/colors/extract
- /api/v1/design-tokens/export/w3c
- /api/v1/grid
- /api/v1/grid/extract
- /api/v1/layout
- /api/v1/layout/extract
- /api/v1/shadows/extract
- /api/v1/spacing
- …(+9 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Harden/regression-test: Semantic color naming

**Context**
Source: `docs/DESIGN_TOKENS_W3C_STATUS.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: Semantic color naming
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/colors
- /api/v1/colors/
- /api/v1/colors/extract
- /api/v1/design-tokens/export/w3c
- /api/v1/grid
- /api/v1/grid/extract
- /api/v1/layout
- /api/v1/layout/extract
- /api/v1/shadows/extract
- /api/v1/spacing
- …(+9 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Developer Workflow - Copy That

### Sources
- `docs/DEVELOPER_WORKFLOW.md`

### Summary
**Last Updated:** 2025-12-08 **For:** Solo Developer (Josh)

Prevent lint/type/test errors from reaching CI by catching them early in your local development workflow.

### Key Points
- ✅ VS Code prompts to install recommended extensions
- ✅ Ruff linter shows errors as you type
- ✅ Mypy type checker runs in background
- ✅ Auto-format on save (Ruff)
- ✅ Auto-fix imports on save
- charliermarsh.ruff - Python linting/formatting
- ms-python.python - Python language support
- ms-python.vscode-pylance - Type checking
- esbenp.prettier-vscode - TypeScript formatting
- dbaeumer.vscode-eslint - JavaScript linting

### Implementation Pointers
- `src/api/colors.py`

### Build / Refactor Issues
#### Harden/regression-test: ✅ VS Code prompts to install recommended extensions

**Context**
Source: `docs/DEVELOPER_WORKFLOW.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: ✅ VS Code prompts to install recommended extensions
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- src/api/colors.py
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Harden/regression-test: ✅ Ruff linter shows errors as you type

**Context**
Source: `docs/DEVELOPER_WORKFLOW.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: ✅ Ruff linter shows errors as you type
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- src/api/colors.py
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Development Guide

### Sources
- `docs/guides/DEVELOPMENT.md`

### Summary
Complete setup and development instructions for Copy That.

### Key Points
- **Python 3.12+** ([download](https://www.python.org/downloads/))
- **Node.js 18+** ([download](https://nodejs.org/))
- **Docker** (optional, for containerized database)
- Frontend: http://localhost:5173 (Vite dev server)
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- **Formatter:** Ruff (configured in pyproject.toml)
- **Linter:** Ruff with multiple rule sets (see pyproject.toml)
- **Type Checker:** mypy with strict mode
- **Docstring Style:** Google-style docstrings

### Implementation Pointers
- `alembic revision`
- `alembic upgrade`
- `make check`
- `make ci-heavy`
- `make ci-light`
- `make ci-medium`
- `make dead-code`
- `make docker-build`
- `make format`
- `make format-check`
- `make install`
- `make lint`
- `make test-a11y`
- `make test-api`
- `make test-cov`
- `make test-e2e`
- `make test-fast`
- `make test-int`
- `make test-load`
- `make test-load-ui`
- `make test-unit`
- `make test-visual`
- `make tests`
- `make type-check`
- `pnpm dev`
- `pnpm install`
- `src/copy_that/`
- `src/copy_that/domain/models.py`
- `src/copy_that/interfaces/api/colors.py`
- `src/copy_that/interfaces/api/schemas.py`

### Build / Refactor Issues
#### Harden/regression-test: **Python 3.12+** )

**Context**
Source: `docs/guides/DEVELOPMENT.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: **Python 3.12+** )
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- alembic revision
- alembic upgrade
- make check
- make ci-heavy
- make ci-light
- make ci-medium
- make dead-code
- make docker-build
- make format
- make format-check
- …(+20 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Harden/regression-test: **Node.js 18+** )

**Context**
Source: `docs/guides/DEVELOPMENT.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: **Node.js 18+** )
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- alembic revision
- alembic upgrade
- make check
- make ci-heavy
- make ci-light
- make ci-medium
- make dead-code
- make docker-build
- make format
- make format-check
- …(+20 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## DevOps Guide - Copy That Platform

### Sources
- `docs/DEVOPS_GUIDE.md`

### Summary
**Solo Developer Workflow** | **Last Updated:** 2025-12-08

### Key Points
- [Local Development Setup](#local-development-setup)
- [Docker Usage Patterns](#docker-usage-patterns)
- [Testing Production Builds](#testing-production-builds)
- [Deployment Workflow](#deployment-workflow)
- [Secret Management](#secret-management)
- [CI/CD Pipeline](#cicd-pipeline)
- [Troubleshooting](#troubleshooting)
- Docker Desktop (or Docker Engine + Docker Compose)
- (Optional) Node.js 20+ for frontend development
- (Optional) Python 3.12+ for backend development without Docker

### Implementation Pointers
- `/api/v1/status`
- `alembic current`
- `alembic history`
- `alembic revision`
- `alembic upgrade`
- `deploy/deploy-python-service`
- `deploy/terraform`
- `pnpm dev`
- `pnpm typecheck`

### Build / Refactor Issues
#### Harden/regression-test: [Local Development Setup]

**Context**
Source: `docs/DEVOPS_GUIDE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: [Local Development Setup]
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/status
- alembic current
- alembic history
- alembic revision
- alembic upgrade
- deploy/deploy-python-service
- deploy/terraform
- pnpm dev
- pnpm typecheck
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Harden/regression-test: [Docker Usage Patterns]

**Context**
Source: `docs/DEVOPS_GUIDE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: [Docker Usage Patterns]
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- /api/v1/status
- alembic current
- alembic history
- alembic revision
- alembic upgrade
- deploy/deploy-python-service
- deploy/terraform
- pnpm dev
- pnpm typecheck
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Existing Frontend Components Assessment

### Sources
- `docs/design/EXISTING_COMPONENTS_ASSESSMENT.md`

### Summary
**Date:** 2025-11-20 **Status:** Code-Complete, Zero-Test Gap Identified **Scope:** Mapping existing educational frontend (1,500 LOC) to generic token explorer pattern

**Great News:** The educational color frontend is already mostly built and functional!

**Critical Gap:** ~1,500 lines of component code with **0% test coverage** (not TDD)

### Key Points
- 9 interactive components (HarmonyVisualizer, AccessibilityVisualizer, ColorNarrative, etc.)
- TypeScript type-safe ✅
- Full educational UI with interactive visualizations ✅
- This violates your TDD requirement
- Must be addressed before production use
- ~40-60 hours of test coverage needed
- Can be refactored incrementally toward schema-driven architecture
- No need to rebuild from scratch
- 80/20 pattern already emerging organically
- ✅ **Large token display** (ColorTokenDisplay)

### Implementation Pointers
- `frontend/src/App.tsx`
- `frontend/src/components/`
- `frontend/src/components/AccessibilityVisualizer.tsx`
- `frontend/src/components/ColorNarrative.tsx`
- `frontend/src/components/EducationalColorDisplay.tsx`
- `frontend/src/components/HarmonyVisualizer.tsx`
- `frontend/src/components/LearningSidebar.tsx`
- `frontend/src/components/PlaygroundSidebar.tsx`
- `frontend/src/components/__tests__/`
- `frontend/src/components/__tests__/AccessibilityVisualizer.test.tsx`
- `frontend/src/components/__tests__/ColorTokenDisplay.a11y.test.tsx`
- `frontend/src/components/__tests__/ColorTokenDisplay.integration.test.tsx`
- `frontend/src/components/__tests__/ColorTokenDisplay.test.tsx`
- `frontend/src/components/__tests__/HarmonyVisualizer.test.tsx`
- `frontend/src/components/tokens/TokenGrid.tsx`
- `frontend/src/components/tokens/TokenInspectorSidebar.tsx`
- `frontend/src/components/tokens/TokenPlaygroundDrawer.tsx`
- `frontend/src/config/tokenTypeRegistry.ts`
- `frontend/src/hooks/useTokens.ts`
- `frontend/src/store/tokenStore.ts`
- `frontend/src/types/index.ts`
- `pnpm add`
- `pnpm type-check`

### Build / Refactor Issues
#### Harden/regression-test: 9 interactive components

**Context**
Source: `docs/design/EXISTING_COMPONENTS_ASSESSMENT.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: 9 interactive components
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/src/App.tsx
- frontend/src/components/
- frontend/src/components/AccessibilityVisualizer.tsx
- frontend/src/components/ColorNarrative.tsx
- frontend/src/components/EducationalColorDisplay.tsx
- frontend/src/components/HarmonyVisualizer.tsx
- frontend/src/components/LearningSidebar.tsx
- frontend/src/components/PlaygroundSidebar.tsx
- frontend/src/components/__tests__/
- frontend/src/components/__tests__/AccessibilityVisualizer.test.tsx
- …(+13 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Harden/regression-test: TypeScript type-safe ✅

**Context**
Source: `docs/design/EXISTING_COMPONENTS_ASSESSMENT.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: TypeScript type-safe ✅
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/src/App.tsx
- frontend/src/components/
- frontend/src/components/AccessibilityVisualizer.tsx
- frontend/src/components/ColorNarrative.tsx
- frontend/src/components/EducationalColorDisplay.tsx
- frontend/src/components/HarmonyVisualizer.tsx
- frontend/src/components/LearningSidebar.tsx
- frontend/src/components/PlaygroundSidebar.tsx
- frontend/src/components/__tests__/
- frontend/src/components/__tests__/AccessibilityVisualizer.test.tsx
- …(+13 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Frontend Component Usage Map - Complete Reference

### Sources
- `docs/FRONTEND_COMPONENT_USAGE_MAP.md`

### Summary
**Document Date:** 2025-12-04 **Purpose:** Track which components are used in the Copy That app vs unused/dead code **Scope:** All React components in `frontend/src/components/`

| Metric | Count | Notes | |--------|-------|-------| | **Total Components** | 48 | Main *.tsx files (excludes tests, subfolder dups) | | **Actively Used** | 25 | Imported in App.tsx or tokenTypeRegistry | | **Likely Unused** | 23 | Not imported anywhere, candidates for removal | | **Dead Code LOC** | ~2,500 | Estimated lines in unused components | | **Dependencies** | Minimal | Most components have <3 dependencies |

### Key Points
- **Location:** frontend/src/components/ImageUploader.tsx
- **Import:** Line 3 in App.tsx
- **Usage:** Main upload panel, orchestrates all extractions
- **Criticality:** 🔴 **CRITICAL** - Entry point for all data
- **Status:** ✅ Actively used
- APIClient (API calls)
- resizeImageFile utility (image compression)
- onImageBase64Extracted callback (to App)
- **Notes:** Subject of Issue #9B (Priority 1 for refactoring)
- **Location:** frontend/src/components/ColorTokenDisplay.tsx

### Implementation Pointers
- `frontend/src/`
- `frontend/src/App.tsx`
- `frontend/src/components/`
- `frontend/src/components/ColorTokenDisplay.tsx`
- `frontend/src/components/ComponentName.`
- `frontend/src/components/ImageUploader.tsx`
- `frontend/src/components/MetricsOverview.tsx`
- `frontend/src/components/__tests__/ComponentName`
- `frontend/src/config/tokenTypeRegistry.tsx`
- `pnpm test`
- `pnpm typecheck`

### Build / Refactor Issues
#### Harden/regression-test: **Location:** frontend/src/components/ImageUploader.tsx

**Context**
Source: `docs/FRONTEND_COMPONENT_USAGE_MAP.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: **Location:** frontend/src/components/ImageUploader.tsx
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/src/
- frontend/src/App.tsx
- frontend/src/components/
- frontend/src/components/ColorTokenDisplay.tsx
- frontend/src/components/ComponentName.
- frontend/src/components/ImageUploader.tsx
- frontend/src/components/MetricsOverview.tsx
- frontend/src/components/__tests__/ComponentName
- frontend/src/config/tokenTypeRegistry.tsx
- pnpm test
- …(+1 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Harden/regression-test: **Import:** Line 3 in App.tsx

**Context**
Source: `docs/FRONTEND_COMPONENT_USAGE_MAP.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: **Import:** Line 3 in App.tsx
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/src/
- frontend/src/App.tsx
- frontend/src/components/
- frontend/src/components/ColorTokenDisplay.tsx
- frontend/src/components/ComponentName.
- frontend/src/components/ImageUploader.tsx
- frontend/src/components/MetricsOverview.tsx
- frontend/src/components/__tests__/ComponentName
- frontend/src/config/tokenTypeRegistry.tsx
- pnpm test
- …(+1 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## GitHub Environments Setup

### Sources
- `docs/ops/github-environments.md`

### Summary
This guide explains how to set up GitHub environments for the tiered testing and deployment strategy.

| Environment | Branch/Trigger | Test Tier | Purpose | |-------------|----------------|-----------|---------| | (none) | PR, fix/* | Light | Fast feedback, lint/type/fast-unit | | (none) | feature/*, develop | Medium | Full tests before merge | | staging | develop merge | Medium | Deploy & test in GCP staging | | production | v* tags | Heavy | Full suite, deploy to GCP prod |

### Key Points
- Fast unit tests (excludes @pytest.mark.slow)
- Full unit tests with coverage
- Integration tests with DB/Redis
- Security scanning (pip-audit, bandit, gitleaks)
- E2E tests with Playwright
- Docker build + Trivy scan
- Performance benchmarks (when added)
- **Deployment branches:** develop
- **Required reviewers:** (optional, 0 for auto-deploy)
- **Wait timer:** 0 minutes

### Implementation Pointers
_No explicit code touchpoints referenced in doc._

### Build / Refactor Issues
#### Harden/regression-test: Fast unit tests

**Context**
Source: `docs/ops/github-environments.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: Fast unit tests
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Harden/regression-test: Full unit tests with coverage

**Context**
Source: `docs/ops/github-environments.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: Full unit tests with coverage
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Minimal Cost Setup Guide

### Sources
- `docs/setup/setup_minimal.md`

### Summary
**Perfect for:** Personal projects, demos, sharing with family/friends

**Cost:** ~$0-5/month (only pay when URL is visited)

**Verify local Redis and Celery are working:**

### Key Points
- ✅ Public URL to share with anyone
- ✅ Production-quality infrastructure
- ✅ Auto-scaling (0-5 instances)
- ✅ Zero cost when idle
- ✅ Secure enough for personal/demo use
- **Local development** (.env ENVIRONMENT=local):
- Redis runs on localhost:6379 (no SSL)
- Uses local Redis broker/backend
- Perfect for development and testing
- **Production/Staging** (.env ENVIRONMENT=staging|production):

### Implementation Pointers
- `alembic upgrade`
- `deploy/terraform`
- `src/copy_that/infrastructure/celery_config.py`
- `src/copy_that/infrastructure/config.py`

### Build / Refactor Issues
#### Harden/regression-test: ✅ Public URL to share with anyone

**Context**
Source: `docs/setup/setup_minimal.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: ✅ Public URL to share with anyone
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- alembic upgrade
- deploy/terraform
- src/copy_that/infrastructure/celery_config.py
- src/copy_that/infrastructure/config.py
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Harden/regression-test: ✅ Production-quality infrastructure

**Context**
Source: `docs/setup/setup_minimal.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: ✅ Production-quality infrastructure
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- alembic upgrade
- deploy/terraform
- src/copy_that/infrastructure/celery_config.py
- src/copy_that/infrastructure/config.py
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Modern Monochromatic Design System - Testing Guide

### Sources
- `docs/MODERN_DESIGN_TESTING.md`

### Summary
**Date:** 2025-11-20 **Version:** 1.0.0 **Focus:** Modern UI Redesign - Minimal Header, Full-Screen Color Analysis

This document provides comprehensive testing guidelines for the new modern monochromatic design system implementation, including:

### Key Points
- ✅ Redesigned minimal App layout
- ✅ Modern design token system (grayscale + indigo accent)
- ✅ Full-screen color analysis view
- ✅ Integrated interactive playground
- ✅ Responsive design across all breakpoints
- **Neutrals (Grayscale):** 10-step scale from #fafafa → #171717
- **Accent:** Indigo (#4f46e5) with hover and light variants
- **Semantic:** Success (green), Warning (amber), Error (red)
- **Text Hierarchy:** Primary → Secondary → Tertiary
- **Backgrounds:** Main, Secondary, Tertiary tints

### Implementation Pointers
- `frontend/src/App.css`
- `frontend/src/App.tsx`
- `frontend/src/components/ColorDetailsPanel.css`
- `frontend/src/components/CompactColorGrid.css`
- `frontend/src/components/ImageUploader.css`
- `frontend/src/components/PlaygroundSidebar.css`
- `frontend/src/design/tokens.css`
- `pnpm dev`
- `pnpm type-check`

### Build / Refactor Issues
#### Harden/regression-test: ✅ Redesigned minimal App layout

**Context**
Source: `docs/MODERN_DESIGN_TESTING.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: ✅ Redesigned minimal App layout
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/src/App.css
- frontend/src/App.tsx
- frontend/src/components/ColorDetailsPanel.css
- frontend/src/components/CompactColorGrid.css
- frontend/src/components/ImageUploader.css
- frontend/src/components/PlaygroundSidebar.css
- frontend/src/design/tokens.css
- pnpm dev
- pnpm type-check
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Harden/regression-test: ✅ Modern design token system

**Context**
Source: `docs/MODERN_DESIGN_TESTING.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: ✅ Modern design token system
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/src/App.css
- frontend/src/App.tsx
- frontend/src/components/ColorDetailsPanel.css
- frontend/src/components/CompactColorGrid.css
- frontend/src/components/ImageUploader.css
- frontend/src/components/PlaygroundSidebar.css
- frontend/src/design/tokens.css
- pnpm dev
- pnpm type-check
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Phase 2 Refactoring - Quick Reference Guide

### Sources
- `docs/planning/PHASE2_QUICK_REFERENCE.md`

### Summary
**Before:** Single 328 LOC file **After:** Modular structure with 32 LOC orchestrator

### Key Points
- types.ts - Types and interfaces
- hooks.ts - API loading and validation logic
- DesignInsightCard.tsx - Card component
- MetricsGrid.tsx - Layout component
- MetricsOverview.tsx - Orchestrator
- types.ts - Types and interfaces
- utils.ts - Pure color calculations
- hooks.ts - State management
- ContrastPanel.tsx - Reusable contrast display
- WcagStandards.tsx - WCAG badge display

### Implementation Pointers
- `frontend/src/components/`
- `pnpm build`
- `pnpm dev`
- `pnpm test`
- `pnpm type-check`

### Build / Refactor Issues
#### Harden/regression-test: types.ts - Types and interfaces

**Context**
Source: `docs/planning/PHASE2_QUICK_REFERENCE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: types.ts - Types and interfaces
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/src/components/
- pnpm build
- pnpm dev
- pnpm test
- pnpm type-check
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Harden/regression-test: hooks.ts - API loading and validation logic

**Context**
Source: `docs/planning/PHASE2_QUICK_REFERENCE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: hooks.ts - API loading and validation logic
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/src/components/
- pnpm build
- pnpm dev
- pnpm test
- pnpm type-check
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Phase 4 Implementation Strategy

### Sources
- `docs/ops/implementation_strategy.md`

### Summary
**Date:** 2025-11-18 **Decision:** Color-First Vertical Slice (Recommended)

Should we implement Phase 4 schema architecture:

### Key Points
- Implement color tokens through entire stack (extractor → schema → adapter → database → frontend → generator)
- Validate architecture end-to-end with ONE token type
- Then repeat pattern for remaining tokens (spacing, shadow, typography, border-radius, opacity)
- Implement schemas for ALL token types in Week 1
- Implement adapters for ALL token types in Week 1-2
- Implement database tables for ALL token types in Week 2
- Then integrate frontend and generators
- ✅ If adapter pattern doesn't work → discover with colors only, fix, continue
- ✅ If database structure needs changes → only color_tokens table affected
- ✅ If code generation breaks → fix for one type, apply to others

### Implementation Pointers
- `alembic revision`
- `alembic upgrade`
- `frontend/src/api/colorClient.ts`
- `frontend/src/components/ColorTokenCard.tsx`
- `frontend/src/types/generated/color.ts`

### Build / Refactor Issues
#### Harden/regression-test: Implement color tokens through entire stack

**Context**
Source: `docs/ops/implementation_strategy.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: Implement color tokens through entire stack
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- alembic revision
- alembic upgrade
- frontend/src/api/colorClient.ts
- frontend/src/components/ColorTokenCard.tsx
- frontend/src/types/generated/color.ts
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Harden/regression-test: Validate architecture end-to-end with ONE token type

**Context**
Source: `docs/ops/implementation_strategy.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: Validate architecture end-to-end with ONE token type
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- alembic revision
- alembic upgrade
- frontend/src/api/colorClient.ts
- frontend/src/components/ColorTokenCard.tsx
- frontend/src/types/generated/color.ts
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Remote Branch Merge Plan & Progress

### Sources
- `docs/guides/REMOTE_BRANCH_MERGE_PLAN.md`

### Summary
**Date:** 2025-12-07 **Objective:** Systematically merge all remote branches into main **Status:** In Progress

These are documented feature branches from previous Claude Code sessions:

### Key Points
- origin/claude/fix-ruff-linting-015FpLfhVm8gA8uzx2gzEWJm
- origin/claude/review-shadow-docs-011xD6JT3WURrnVeLEEsrvwe
- origin/claude/shadow-pipeline-1-01BXp8VVMptR3eLiH7umHTmW
- origin/claude/shadow-token-lifecycle-01WrwgwNhb1q1grj97cW786Z
- origin/dependabot/github_actions/actions/upload-artifact-5
- origin/dependabot/github_actions/github/codeql-action-4
- origin/dependabot/github_actions/google-github-actions/setup-gcloud-3
- origin/dependabot/npm_and_yarn/jsdom-27.2.0
- origin/dependabot/npm_and_yarn/typescript-eslint/eslint-plugin-8.48.0
- origin/dependabot/npm_and_yarn/vitejs/plugin-react-5.1.1

### Implementation Pointers
- `pnpm test`
- `pnpm typecheck`
- `src/copy_that/shadowlab/upgraded_models.py`

### Build / Refactor Issues
#### Harden/regression-test: origin/claude/fix-ruff-linting-015FpLfhVm8gA8uzx2gzEWJm

**Context**
Source: `docs/guides/REMOTE_BRANCH_MERGE_PLAN.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: origin/claude/fix-ruff-linting-015FpLfhVm8gA8uzx2gzEWJm
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- pnpm test
- pnpm typecheck
- src/copy_that/shadowlab/upgraded_models.py
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Harden/regression-test: origin/claude/review-shadow-docs-011xD6JT3WURrnVeLEEsrvwe

**Context**
Source: `docs/guides/REMOTE_BRANCH_MERGE_PLAN.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: origin/claude/review-shadow-docs-011xD6JT3WURrnVeLEEsrvwe
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- pnpm test
- pnpm typecheck
- src/copy_that/shadowlab/upgraded_models.py
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Security Hardening Guide

### Sources
- `docs/configuration/security.md`

### Summary
Copy This v2.0 Backend - Comprehensive Security Implementation

This document describes the security hardening measures implemented in Copy This v2.0 to protect against common web application vulnerabilities.

### Key Points
- [Overview](#overview)
- [CORS Configuration](#cors-configuration)
- [Input Validation](#input-validation)
- [Secrets Management](#secrets-management)
- [CSRF Protection](#csrf-protection)
- [Retry Logic & Circuit Breaker](#retry-logic--circuit-breaker)
- [Rate Limiting](#rate-limiting)
- [Production Deployment](#production-deployment)
- [Security Checklist](#security-checklist)
- **No wildcard methods**: Only explicit HTTP methods allowed

### Implementation Pointers
_No explicit code touchpoints referenced in doc._

### Build / Refactor Issues
#### Harden/regression-test: [Overview]

**Context**
Source: `docs/configuration/security.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: [Overview]
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Harden/regression-test: [CORS Configuration]

**Context**
Source: `docs/configuration/security.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: [CORS Configuration]
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Session Transition Document: Copy That Token Explorer Redesign

### Sources
- `docs/design/TRANSITION_DOCUMENT.md`

### Summary
**Date:** 2025-11-20 Evening **Session Status:** Design Phase Complete - Ready for Implementation **Token Usage:** ~150k (session boundary) **Next Action:** Clear session, restart with implementation phase

### Key Points
- ✅ Complete UI/UX vision for generic token exploration platform
- ✅ React architecture with Zustand + schema-driven patterns
- ✅ Assessment of existing 1,500 LOC frontend (80% aligned with vision!)
- ✅ Refactor roadmap (6-8 hours to add state management + schema layer)
- ✅ Test implementation guide (50-75 hours for TDD compliance)
- ✅ Delightful interactions spec (animations, micro-interactions)
- Color tokens: Fully designed, existing components need refactoring + tests
- Typography tokens: Pattern proven, <200 LOC to add
- Spacing tokens: Same pattern, <200 LOC to add
- Shadow/Animation tokens: Future phases, same pattern

### Implementation Pointers
- `frontend/src/`
- `frontend/src/components/`
- `frontend/src/components/__tests__/`
- `frontend/src/components/tokens/`
- `frontend/src/components/tokens/TokenGrid.tsx`
- `frontend/src/components/tokens/TokenInspectorSidebar.tsx`
- `frontend/src/components/tokens/TokenPlaygroundDrawer.tsx`
- `frontend/src/config/tokenTypeRegistry.ts`
- `frontend/src/hooks/useTokens.ts`
- `frontend/src/store/tokenStore.ts`
- `pnpm add`
- `pnpm build`
- `pnpm dev`
- `pnpm test`
- `pnpm type-check`
- `pnpm typecheck`
- `src/copy_that/`

### Build / Refactor Issues
#### Harden/regression-test: ✅ Complete UI/UX vision for generic token exploration platform

**Context**
Source: `docs/design/TRANSITION_DOCUMENT.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: ✅ Complete UI/UX vision for generic token exploration platform
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/src/
- frontend/src/components/
- frontend/src/components/__tests__/
- frontend/src/components/tokens/
- frontend/src/components/tokens/TokenGrid.tsx
- frontend/src/components/tokens/TokenInspectorSidebar.tsx
- frontend/src/components/tokens/TokenPlaygroundDrawer.tsx
- frontend/src/config/tokenTypeRegistry.ts
- frontend/src/hooks/useTokens.ts
- frontend/src/store/tokenStore.ts
- …(+7 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Harden/regression-test: ✅ React architecture with Zustand + schema-driven patterns

**Context**
Source: `docs/design/TRANSITION_DOCUMENT.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: ✅ React architecture with Zustand + schema-driven patterns
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- frontend/src/
- frontend/src/components/
- frontend/src/components/__tests__/
- frontend/src/components/tokens/
- frontend/src/components/tokens/TokenGrid.tsx
- frontend/src/components/tokens/TokenInspectorSidebar.tsx
- frontend/src/components/tokens/TokenPlaygroundDrawer.tsx
- frontend/src/config/tokenTypeRegistry.ts
- frontend/src/hooks/useTokens.ts
- frontend/src/store/tokenStore.ts
- …(+7 more)
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Shadow Extraction Pipeline Implementation

### Sources
- `docs/shadow/IMPLEMENTATION.md`

### Summary
**Status:** ✅ Complete - Tasks 1-7 Implemented **Version:** 1.0.0 **Date:** 2025-12-06

This document describes the shadow extraction pipeline for Midjourney-style AI-generated images. The system converts a single image into structured shadow tokens and visualization layers.

### Key Points
- **8-stage pipeline** (stages.py) — Original, full-featured
- **5-stage pipeline** (stages_v2.py) — Simplified, recommended for most uses
- Loads image via OpenCV
- Normalizes to float32 [0, 1]
- Extracts HSV V-channel (brightness)
- Applies contrast stretching
- Returns grayscale illumination map
- Adaptive thresholding (compare to local mean)
- Binary erosion/closing for cleanup
- Connected component labeling (scipy.ndimage)

### Implementation Pointers
- `src/copy_that/shadowlab/`

### Build / Refactor Issues
#### Harden/regression-test: **8-stage pipeline**  — Original, full-featured

**Context**
Source: `docs/shadow/IMPLEMENTATION.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: **8-stage pipeline**  — Original, full-featured
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- src/copy_that/shadowlab/
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Harden/regression-test: **5-stage pipeline**  — Simplified, recommended for most uses

**Context**
Source: `docs/shadow/IMPLEMENTATION.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: **5-stage pipeline**  — Simplified, recommended for most uses
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.

Likely touchpoints (verify in repo):
- src/copy_that/shadowlab/
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

## Shadow Pipeline Visual Guide

### Sources
- `docs/shadow/VISUAL_GUIDE.md`

### Summary
**A visual walkthrough of shadow extraction using real test images**

This guide demonstrates the shadow extraction pipeline using processed test images. Each stage is illustrated with actual outputs from the `test_images/processedImageShadows/` folder.

### Key Points
- Adaptive threshold (compare to local mean)
- Morphological cleaning (erosion + closing)
- Connected component filtering
- Distance transform for soft edges
- Surface normals (via gradient)
- Light direction fitting data
- Direction: Based on sun position
- Softness: Medium (distance from objects)
- Contrast: High (bright sunlight)
- Classical detection may have false positives

### Implementation Pointers
_No explicit code touchpoints referenced in doc._

### Build / Refactor Issues
#### Harden/regression-test: Adaptive threshold

**Context**
Source: `docs/shadow/VISUAL_GUIDE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: Adaptive threshold
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

#### Harden/regression-test: Morphological cleaning

**Context**
Source: `docs/shadow/VISUAL_GUIDE.md`. Consolidate with overlapping docs; treat this as the canonical reference for this slice of work.

**Claude-friendly prompt**
```text
You are working in the `copy-that` repository.
Goal: Harden/regression-test: Morphological cleaning
Constraints:
- Preserve existing architecture patterns (orchestrators/adapters, token-agnostic UI, strict typing).
- Prefer small, testable PRs; include migrations only if unavoidable.
- Update docs and link back to the canonical reference file.
```

**Acceptance criteria**
- Relevant unit tests and type checks pass (`make check`, backend unit tests, frontend typecheck).
- If user-facing, add or update at least one integration/E2E test (Playwright) exercising the workflow.
- Update docs with any API/behavior changes and add cross-links.

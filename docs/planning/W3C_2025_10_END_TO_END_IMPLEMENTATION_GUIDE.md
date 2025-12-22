# W3C 2025.10 Design Tokens End-to-End Implementation Guide (Copy That)

Date: 2025-12-21
Owner: TBD
Scope: W3C DTCG 2025.10 compliance + end-to-end pipeline transparency + unified UI system

This document is the single start-to-finish plan for bringing Copy That tokens into full W3C 2025.10 adherence, surfacing all pipeline artifacts and algorithms through the API, and delivering a cohesive, modern UI with a consistent visual language.

---

## Current Status Snapshot (2025-12-21)

- W3C exporter uses spec-valid `$type` mapping; layout/grid tokens decompose into standard types; directional spacing exports as per-side `dimension` tokens.
- Schemas (format/color/resolver) are present and validated; format schema enumerates supported `$type` values.
- Resolver helper `make_resolver_2025_10()` is implemented and validated in tests.
- Streaming diagnostics are covered by Playwright tests for color overlay and spacing overlay precedence.
- Gaps remain in API artifact/provenance pass-through and resolver cross-field validation.

---

## Next Tasks (P0/P1)

P0 (complete):
- Wire `ArtifactBundle` into color + spacing endpoints and SSE stream events.
- Add resolver cross-field validation tests (contexts/sources vs. resolution order).
- Add optional API validation guard for W3C export outputs.

P1 (next):
- Extend streaming artifact tests to typography/shadow/geometry once artifacts are exposed.
- Attach `$extensions.provenance` to exported tokens (pipeline + algorithm + artifacts).

---

## 0) Definition of Done

- All exported tokens conform to W3C DTCG 2025.10 format + color + resolver specs.
- JSON Schemas for format/color/resolver are present, expanded, and validated in tests.
- Resolver documents are generated for theme/brand contexts with deterministic ordering.
- All extraction pipelines emit artifacts and algorithm provenance in API responses.
- UI exposes artifacts and provenance with progressive disclosure and consistent visuals.
- Generators consume W3C JSON as canonical input (React + CSS first).

---

## 1) Repo Reality Check (Canonical Paths)

Backend:
- W3C export adapter: `src/core/tokens/adapters/w3c.py`
- Export endpoint: `src/copy_that/interfaces/api/design_tokens.py`
- Extractors: `src/copy_that/extractors/*`, `src/copy_that/application/*`
- Debug artifact helpers: `src/copy_that/application/cv/debug_*.py`
- API schemas: `src/copy_that/interfaces/api/schemas.py`
- Schema scaffolding: `src/copy_that/design_tokens/schemas/2025_10/`

Frontend:
- App layout: `frontend/src/App.tsx`, `frontend/src/App.css`
- Token explorer + panels: `frontend/src/features/explorer/*`
- Diagnostics panel: `frontend/src/components/diagnostics-panel/*`

Docs:
- Status + quick reference: `docs/DESIGN_TOKENS_W3C_STATUS.md`, `docs/DESIGN_TOKENS_QUICK_REFERENCE.md`
- Token pipeline review: `docs/reviews/CODEX_TOKEN_PIPELINE_REVIEW.md`
- UI/UX review: `docs/UI_UX_REVIEW_SINGLE_SOURCE.md`

Standards (local):
- Spec mirror: `docs/standards/design_tokens_cg/2025.10/`
- Spec submodule: `docs/standards/design_tokens_cg/community-group/`

---

## 2) Decisions / ADR

- Token graph remains the canonical representation (ADR-004 in `docs/architecture/12182025/DECISIONS.md`).
- Single W3C exporter: extend `src/core/tokens/adapters/w3c.py` (no parallel module).
- Diagnostics are gated behind toggles (default collapsed), not always-on.
- Layout/grid tokens decompose into spec-valid sub-tokens (`dimension`, `number`, `color`, `strokeStyle`).
- Directional spacing exports as per-side `dimension` tokens (e.g., `/top`, `/inline`).
- Generator targets after W3C export: React + CSS (aligned with app UI usage).
- W3C spec is tracked via submodule + local mirror for stable referencing.

---

## 3) Standards + Schema Coverage

Primary spec references (local):
- Format: `docs/standards/design_tokens_cg/2025.10/format.html`
- Color: `docs/standards/design_tokens_cg/2025.10/color.html`
- Resolver: `docs/standards/design_tokens_cg/2025.10/resolver.html`
- Technical reports: `docs/standards/design_tokens_cg/community-group/technical-reports/`

Schema scaffolding (current):
- `src/copy_that/design_tokens/schemas/2025_10/format.schema.json`
- `src/copy_that/design_tokens/schemas/2025_10/color.schema.json`
- `src/copy_that/design_tokens/schemas/2025_10/resolver.schema.json`

Required build-out:
- Enumerate allowed `$type` values as new token types are added (current format schema covers existing types).
- Add stricter validation for color token values (colorSpace + components shape).
- Add cross-field resolver checks (all contexts and sources exist in resolutionOrder).
- Validate exports in tests (already scaffolded) and optionally at API boundary.

---

## 4) W3C Token Mapping (Current Token Types)

| Copy That TokenType | W3C `$type` | Export Shape | Notes |
| --- | --- | --- | --- |
| COLOR | `color` | `$value` color object or ref | OKLCH preserved via colorSpace + components |
| SPACING | `dimension` | `$value` `{value, unit}` | Directional spacing becomes `/top`, `/inline`, etc |
| SHADOW | `shadow` | `$value` layer list | Color refs preserved |
| TYPOGRAPHY | `typography` | `$value` composite | Font refs + size refs |
| FONT_FAMILY | `fontFamily` | `$value` string/list | Matches spec type |
| FONT_SIZE | `dimension` | `$value` `{value, unit}` | `px` normalized |
| LAYOUT | `dimension`/`number`/`color`/`strokeStyle` | decomposed | `/columns`, `/gutter`, `/margin/*`, `/radius`, `/border/*` |
| GRID | `dimension`/`number` | decomposed under `layout.grid` | same as layout |

Directional spacing (spec-aligned representation):
- Use separate tokens: `spacing.card/top`, `spacing.card/inline`, etc.
- Each entry is a `dimension` token with `$value: {value, unit}`.
- Avoid non-spec composite `$type: spacing` payloads.

Layout/grid strategy (spec-aligned representation):
- Columns -> `$type: number`.
- Gutter/margin/radius -> `$type: dimension`.
- Border -> `/border/width` (dimension), `/border/color` (color), `/border/style` (strokeStyle).

---

## 5) Pipeline Algorithm Catalog + Required Artifacts

The extraction and diagnostics inventory is sourced from `docs/reviews/CODEX_TOKEN_PIPELINE_REVIEW.md`. Every token category must emit artifacts and provenance through the API.

| Token Type | Current Algorithms | Required Artifacts | Priority |
| --- | --- | --- | --- |
| Color | SLIC superpixels, palette quantization, KMeans, OKLCH analysis | Superpixel overlay, palette strip, contrast matrix | P0 |
| Spacing | Connected components, gap clustering, grid inference | Spacing overlay, gap histogram, grid heatmap | P0 |
| Typography | OCR grouping, AI inference | OCR bbox overlay, size heatmap, baseline overlay | P1 |
| Shadow | Morphology + shadowlab | Shadow mask, penumbra map, light vector | P1 |
| Geometry | Depth-Anything, Sobel normals | Line overlay, vanishing points, plane normals | P2 |
| Border/Radius | Canny + arc fitting | Edge map, radius overlay, stroke map | P2 |
| Opacity | Color-line mixing | Alpha mask, residual map | P2 |
| State Layer | OKLCH deltas | Variant swatch strip | P2 |
| Gradient | Least squares in OKLCH | Gradient map, residuals | P3 |
| Animation | Video-only | Metadata-only | P3 |

---

## 6) API Contract: Artifacts + Provenance

Artifact bundle (canonical API shape):
```
ArtifactBundle = {
  "images": [
    {"type": "overlay", "mime": "image/png", "base64": "...", "confidence": 0.8, "stage": "slic"}
  ],
  "json": [
    {"type": "contrast-matrix", "payload": {"...": "..."}, "confidence": 0.7, "stage": "analysis"}
  ]
}
```

Rules:
- Every extraction endpoint returns `artifacts` (empty arrays allowed).
- SSE stream events include `artifacts` per stage.
- Algorithm provenance is attached via `$extensions.provenance` per token:
  - `pipeline`, `algorithm`, `params`, `stage`, `confidence`, `artifacts`.
- Do not embed algorithm details inside `$value`.

---

## 7) UI/UX Blueprint (Single Visual Language)

Problem framing:
- Users: designers + engineers validating extraction quality and exporting tokens.
- Task: upload -> extract -> inspect tokens + provenance -> export.
- Constraints: streaming artifacts, high-density data, accessibility, W3C compliance.

UX intent:
- Primary action: validate tokens with confidence and provenance.
- Secondary actions: inspect diagnostics, compare states, export formats.
- Empty/loading/error states are explicit and actionable.

Interaction model:
- States: idle, extracting (streaming), extracted, error.
- Transitions: upload -> stream -> overview -> detail -> export.
- Feedback: live artifact strip + per-pipeline progress markers.

Design system mapping:
- Tokens: light-first neutral palette, low-saturation accent, consistent spacing scale, restrained typography.
- Components: TokenSummaryCard, ArtifactStrip, DiagnosticPanel, ProvenanceBadge, StateVariantCompare.
- Variants: loading, error, confidence-high/medium/low, empty.

Frontend implementation notes:
- Layout: three-panel grid (summary + detail + diagnostics) with responsive collapse.
- State: tokenGraphStore as canonical; adapters map API -> UI models.
- Accessibility: keyboard navigation, focus states, contrast checks, ARIA for streamed updates.

Failure modes:
- Artifacts not bound to tokens -> user distrust.
- Hidden metadata -> slow validation.
- Overly tall upload panel -> analysis below fold.
- Diagnostics always-on -> cognitive overload (mitigate with toggles).

Iteration & validation ideas:
- Playwright streaming tests with snapshot checkpoints.
- Artifact presence tests for every token endpoint.
- Accessibility audit (keyboard + screen reader).

---

## 8) Phased Implementation Plan (Codex-Ready Prompts)

### Phase 0 (P0) - Standards Alignment + Contracts

Goal: lock W3C 2025.10 contract, schemas, and export rules.

Prompt 0.1 (Schemas + Validation):
```
Extend `src/copy_that/design_tokens/schemas/2025_10/*` to cover W3C 2025.10 format/color/resolver rules more strictly.
- Add `$type` enums where possible for currently-supported token types.
- Add resolver cross-field validation tests.
- Update tests in `tests/core/tokens/adapters/` to validate exports.
```

Prompt 0.2 (Exporter + Mapping):
```
Use `src/core/tokens/adapters/w3c.py` as the single exporter.
- Ensure `$type` values are spec-valid for all current token types.
- Keep layout/grid decomposition to standard types.
- Export directional spacing as per-side `dimension` tokens.
```

Prompt 0.3 (Resolver Generator):
```
Add a resolver generator module (e.g., `src/copy_that/design_tokens/resolver.py`).
- Provide `make_resolver_2025_10()` that returns the resolver document.
- Add tests validating the resolver schema.
```

Success criteria:
- W3C exports pass format/color schema validation in tests.
- `$type` mapping test passes for all existing token types.

Status:
- Format schema `$type` enumeration added for current token types.
- Resolver generator implemented and validated in tests.

---

### Phase 1 (P0) - Artifact Pass-Through (Color + Spacing)

Prompt 1.1 (Artifact schema):
```
Add ArtifactBundle models to `src/copy_that/interfaces/api/schemas.py` and wire into endpoints.
```

Prompt 1.2 (Color artifacts):
```
Expose existing color debug artifacts via `/api/v1/colors/*` and SSE events.
- Surface overlay, palette strip, contrast matrix.
```

Prompt 1.3 (Spacing artifacts):
```
Expose spacing diagnostics via `/api/v1/spacing/*` and SSE events.
- Surface spacing overlay, gap histogram, grid heatmap.
```

Success criteria:
- Color + spacing endpoints return artifacts consistently.
- Diagnostics are visible in UI via toggle.

---

### Phase 2 (P1) - Typography + Shadow Diagnostics

Prompt 2.1 (Typography artifacts):
```
Add OCR/text overlays and size heatmaps in typography extraction.
- Emit artifacts through `/api/v1/typography/*`.
```

Prompt 2.2 (Shadow artifacts):
```
Expose shadow masks + penumbra + light vector from CV/shadowlab.
- Wire into `/api/v1/shadows/*` responses and SSE.
```

Success criteria:
- Typography + shadow endpoints return artifacts and provenance.

---

### Phase 3 (P2) - Geometry + Missing Token Types

Prompt 3.1 (Geometry diagnostics):
```
Add LSD line detection and vanishing point estimation.
- Emit line overlay + vanishing point JSON in `/api/v1/geometry/*`.
```

Prompt 3.2 (Border/Radius + Opacity + State Layer):
```
Implement baseline extractors and token plumbing for:
- Border width + radius (edge + arc fitting)
- Opacity (alpha estimation)
- State layer (OKLCH deltas)
Each with artifacts + W3C export mapping.
```

Success criteria:
- New token types appear in API + export with artifacts.

---

### Phase 4 (P1/P2) - UI Consistency + Generator Outputs

Prompt 4.1 (Layout + scanability):
```
Rework the main layout to keep token content above the fold and collapse the upload panel post-extraction.
- Update `frontend/src/App.tsx`, `frontend/src/App.css`, `frontend/src/features/upload/UploadPanel.tsx`.
```

Prompt 4.2 (Unified visual language):
```
Define a single visual representation standard for all token types.
- Implement shared components (summary, preview, metadata, confidence, source badges).
- Ensure all token panels follow the same pattern.
```

Prompt 4.3 (Generators):
```
Implement first generator targets from W3C JSON: React + CSS.
- Add golden tests for generator output stability.
```

Success criteria:
- UI uses a consistent visual system and shows artifacts on toggle.
- React + CSS generators ship with tests.

---

## 9) Validation & QA Checklist

Backend:
- `pytest` adapter + schema validation tests.
- Artifact presence tests per endpoint (images + json).
- Resolver schema validation tests.

Frontend:
- Playwright streaming test verifying live artifact rendering.
- Accessibility checks (keyboard + ARIA).
- Regression snapshots for token panels.

---

## 10) Next-Step References

- Token pipeline review: `docs/reviews/CODEX_TOKEN_PIPELINE_REVIEW.md`
- UI/UX consolidated review: `docs/UI_UX_REVIEW_SINGLE_SOURCE.md`
- W3C status + quick reference: `docs/DESIGN_TOKENS_W3C_STATUS.md`, `docs/DESIGN_TOKENS_QUICK_REFERENCE.md`
- Spec mirror: `docs/standards/design_tokens_cg/2025.10/`
- Spec submodule: `docs/standards/design_tokens_cg/community-group/`

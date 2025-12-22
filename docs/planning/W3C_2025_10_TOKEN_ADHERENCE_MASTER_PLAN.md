# W3C 2025.10 Token Adherence Master Plan (Copy That)

Date: YYYY-MM-DD
Owner: TBD
Scope: W3C DTCG 2025.10 compliance, full pipeline provenance/artifacts in API, unified UI.

Inputs:
- Patch pack: DTCG 2025.10 exporter + resolver + API extension (from user brief)
- `docs/reviews/CODEX_TOKEN_PIPELINE_REVIEW.md`
- `docs/UI_UX_REVIEW_SINGLE_SOURCE.md`

---

## 1) Outcomes (Definition of Done)

- All exported tokens conform to W3C DTCG 2025.10 format + color + resolver specs.
- JSON Schema scaffolding exists for format, color, and resolver, with validation wired into export and tests.
- Resolver documents are generated for theme/brand contexts with deterministic ordering.
- API responses include token data plus artifacts and algorithm provenance for every pipeline.
- UI surfaces artifacts and provenance with a unified, minimalist visual system and progressive disclosure.
- Automated tests cover exporter validity, artifacts presence, and streaming UI updates.

---

## 2) Repo Reality Check (Where This Lands)

Backend:
- W3C export endpoint: `src/copy_that/interfaces/api/design_tokens.py`
- W3C adapter: `src/core/tokens/adapters/w3c.py`
- Extractors: `src/copy_that/extractors/*`, `src/copy_that/application/*`
- Debug artifact helpers: `src/copy_that/application/cv/debug_*.py`
- API schemas: `src/copy_that/interfaces/api/schemas.py`

Frontend:
- App layout: `frontend/src/App.tsx`, `frontend/src/App.css`
- Token explorer & panels: `frontend/src/features/explorer/*`
- Diagnostics panel: `frontend/src/components/diagnostics-panel/*`

Docs:
- W3C status: `docs/DESIGN_TOKENS_W3C_STATUS.md`
- W3C quick reference: `docs/DESIGN_TOKENS_QUICK_REFERENCE.md`

---

## 3) Canonical Contracts (DTCG 2025.10 + Artifacts + Provenance)

### 3.1 DTCG 2025.10 Token Document

Rules:
- `$type` + `$value` required for each token.
- `$description` optional.
- `$extensions` used for non-standard metadata (confidence, provenance).
- Do not put algorithm details inside `$value`.

Example:
```
{
  "color": {
    "primary": {
      "$type": "color",
      "$value": {"colorSpace": "oklch", "components": [0.7, 0.1, 240], "alpha": 1},
      "$extensions": {
        "confidence": 0.92,
        "provenance": {"pipeline": "color.cv", "stage": "palette_cluster"}
      }
    }
  }
}
```

### 3.2 Resolver Document

```
{
  "version": "2025.10",
  "sources": {"base": "tokens/base.json", "dark": "tokens/dark.json"},
  "contexts": {"light": ["base"], "dark": ["base", "dark"]},
  "resolutionOrder": ["light", "dark"]
}
```

### 3.3 Artifact Bundle (API Pass-Through)

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

### 3.4 Provenance Metadata (Algorithm + Stage)

Use `$extensions.provenance` on token entries:
```
{
  "pipeline": "spacing.cv",
  "algorithm": ["connected-components", "gap-cluster"],
  "params": {"min_area": 16, "gap_eps": 2},
  "stage": "gap_inference",
  "confidence": 0.68,
  "artifacts": ["spacing-overlay", "gap-histogram"]
}
```

### 3.5 JSON Schema Scaffolding (Format/Color/Resolver)

Location (proposal):
- `src/copy_that/design_tokens/schemas/2025_10/format.schema.json`
- `src/copy_that/design_tokens/schemas/2025_10/color.schema.json`
- `src/copy_that/design_tokens/schemas/2025_10/resolver.schema.json`

Rules:
- Schemas must mirror the 2025.10 spec sections (format, color, resolver).
- Any missing or ambiguous fields in spec get explicit internal notes in `$comment`.
- Export endpoints validate outputs against these schemas in tests (and optionally in API).

---

## 4) Pipeline + Algorithm Catalog (Current + Planned)

| Token Type | Current Pipeline | Key Algorithms | Artifacts to Surface | Gaps | Priority |
| --- | --- | --- | --- | --- | --- |
| Color | CV + AI | SLIC, KMeans, OKLCH | Superpixel overlay, palette strip, contrast matrix | Artifacts not in API | P0 |
| Spacing | CV + AI | Connected comps, gap clustering, grid inference | Spacing overlay, gap histogram, grid heatmap | Artifacts not in API | P0 |
| Typography | AI + OCR | OCR size buckets | OCR overlay, size heatmap | No artifacts | P1 |
| Shadow | CV + AI | Threshold + morphology, shadowlab | Shadow mask, penumbra map, light vector | Artifacts not in API | P1 |
| Geometry | CV + depth | Depth-Anything, Sobel normals | Line overlay, vanishing points, plane normals | Missing vanishing/planes | P2 |
| Border/Radius | Missing | Canny + arc fitting | Edge map, corner curvature | Entire pipeline missing | P2 |
| Opacity | Missing | Local color-line mixing | Alpha mask, residual map | Entire pipeline missing | P2 |
| State Layer | Partial | OKLCH deltas | Variant swatch strip | No explicit tokens | P2 |
| Gradient | Missing | OKLCH least squares | Gradient dir map, residuals | Entire pipeline missing | P3 |
| Animation | Missing | Requires video | Metadata-only | Not from image | P3 |

Relevant code anchors:
- Color: `src/copy_that/extractors/color/*`, `src/copy_that/application/cv/debug_color.py`
- Spacing: `src/copy_that/extractors/spacing/*`, `src/copy_that/application/cv/debug_spacing.py`
- Typography: `src/copy_that/extractors/typography/*`, `src/copy_that/application/typography_extractor.py`
- Shadow: `src/copy_that/extractors/shadow/*`, `src/copy_that/shadowlab/orchestrator.py`
- Geometry: `src/copy_that/extractors/geometry/depth_normals.py`

---

## 5) UI/UX Blueprint (Consistent Visual Language)

### 5.1 Problem framing
- Users: designers + engineers validating extraction quality and exporting tokens.
- Task: upload -> extract -> inspect tokens + provenance -> export.
- Constraints: streaming artifacts, high-density data, W3C compliance, accessibility.

### 5.2 UX intent
- Primary action: validate tokens with confidence and provenance.
- Secondary actions: inspect diagnostics, compare states, export formats.
- Empty states: clear CTA to upload and re-run extraction.

### 5.3 Interaction model
- States: idle, extracting (streaming), extracted, error.
- Transitions: upload -> stream -> overview -> detail panels.
- Feedback: live artifact strip + progress events per pipeline stage.

### 5.4 Design system mapping
- Tokens: light-first neutral palette, single low-sat accent, spacing scale, type scale.
- Components: TokenSummaryCard, ArtifactStrip, DiagnosticPanel, ProvenanceBadge, StateVariantCompare.
- Variants: loading, error, confidence-high/medium/low, empty.

### 5.5 Frontend implementation notes
- Layout: three-panel grid (summary + detail + diagnostics) with responsive collapse.
- State: tokenGraphStore as canonical; adapters map API -> UI models.
- Accessibility: keyboard navigation across panels, focus outlines, contrast checks.

### 5.6 Failure modes
- Artifacts not bound to tokens -> user distrust.
- Hidden metadata -> slow validation.
- Overly tall upload panel -> analysis below fold.

### 5.7 Iteration and validation ideas
- Playwright streaming tests with snapshot checkpoints.
- Playwright streaming artifacts test added for diagnostics overlays (color + spacing).
- A/B check diagnostics density vs scanability.
- Accessibility audit with keyboard-only flows.

---

## 6) Phased Implementation Plan (Prioritized, Codex-Ready)

### Phase 0 (P0) - Standards Alignment + Contracts

Goal:
- Lock W3C 2025.10 contract, artifact bundle schema, theme direction, and JSON Schema scaffolding.

Decision note:
- Extend `src/core/tokens/adapters/w3c.py` as the single W3C 2025.10 exporter (no parallel module).
- Diagnostics are gated behind toggles (default collapsed).
- First generator targets after W3C export are React and CSS (aligned with app UI usage and future design taxonomy storage).
- Layout/grid tokens export as spec-valid sub-tokens (`dimension`, `number`, `color`, `strokeStyle`) under their sections.
- Directional spacing exports as per-side `dimension` tokens (no composite `$type: spacing`).

Deliverables:
- Decision: DTCG 2025.10 exporter path (extend `core.tokens.adapters.w3c.py` or new module).
- ArtifactBundle model added to API schemas.
- Update W3C status docs to reflect plan.

Status (current):
- Completed: schema scaffolding added, docs updated, exporter decision recorded.
- Format schema now enumerates supported `$type` values.

Codex prompt (copy/paste):
```
You are Codex working in /Users/noisebox/Documents/3_Development/Repos/copy-that.
Phase 0: standards alignment and contracts.
Tasks:
1) Add ArtifactBundle and Provenance models to `src/copy_that/interfaces/api/schemas.py`.
2) Scaffold JSON Schemas for DTCG 2025.10:
   - `src/copy_that/design_tokens/schemas/2025_10/format.schema.json`
   - `src/copy_that/design_tokens/schemas/2025_10/color.schema.json`
   - `src/copy_that/design_tokens/schemas/2025_10/resolver.schema.json`
   Use `$comment` for any ambiguous or TODO sections.
3) Update docs `docs/DESIGN_TOKENS_W3C_STATUS.md` and `docs/DESIGN_TOKENS_QUICK_REFERENCE.md`
   to define 2025.10 rules, $extensions usage, resolver schema, and schema validation strategy.
4) Add a short decision note in this plan: whether to extend `src/core/tokens/adapters/w3c.py`
   or add a new `src/copy_that/design_tokens/` exporter module (choose one, explain why).
Acceptance:
- Schemas compile and are referenced by token endpoints.
- Docs reflect artifact/provenance and resolver contracts.
```

---

### Phase 1 (P0) - DTCG 2025.10 Exporter + Resolver + API

Goal:
- Implement 2025.10 exporter and resolver generation, wired to API.
- Validate export outputs against the 2025.10 JSON Schemas.

Deliverables:
- `src/copy_that/design_tokens/` package (model, name_codec, exporter, validate, resolver, adapter).
- API endpoint for 2025.10 export and resolver output.
- Unit tests for exporter + resolver.

Status (current):
- Partial: resolver helper exists and is validated in tests.
- Export continues to use `src/core/tokens/adapters/w3c.py` (no parallel exporter module yet).

Codex prompt (copy/paste):
```
You are Codex working in /Users/noisebox/Documents/3_Development/Repos/copy-that.
Phase 1: add DTCG 2025.10 exporter + resolver.
Tasks:
1) Add `src/copy_that/design_tokens/` with:
   - `__init__.py` (re-export Token, TokenRef, JsonPtrRef, exporter, resolver, validate)
   - `name_codec.py` (encode segments, forbid empty/illegal)
   - `model.py` (Token, TokenRef, JsonPtrRef)
   - `exporter.py` (emit $type/$value/$description/$extensions; handle refs)
   - `validate.py` (name validation + color payload checks)
   - `resolver.py` (make_resolver_2025_10)
   - `adapter.py` (map current token data -> Token list)
2) Wire a new endpoint in `src/copy_that/interfaces/api/design_tokens.py`:
   - `POST /api/v1/design-tokens/export/2025-10` accepts tokens payload and returns 2025.10 doc.
   - Keep existing `GET /api/v1/design-tokens/export/w3c` for compatibility.
3) If reusing `src/core/tokens/adapters/w3c.py`, add a thin adapter to emit Tokens for the
   new exporter or update tokens_to_w3c to align with 2025.10 validation rules.
4) Add JSON Schema validation in tests for format/color/resolver outputs.
5) Add tests in `tests/test_design_tokens_export.py` for exporter + resolver.
Acceptance:
- Exporter produces valid 2025.10 doc and passes validation tests.
- Resolver JSON matches schema (version, sources, contexts, resolutionOrder).
```

---

### Phase 2 (P0/P1) - Artifact Pass-Through + UI Layout Fixes

Goal:
- Surface existing debug artifacts in API and UI for color + spacing.
- Fix layout issues and ensure artifacts appear above the fold.

Deliverables:
- `artifacts` on color + spacing endpoints and streaming events.
- Diagnostics panel wired to real data.
- Upload panel auto-collapses after extraction with a toggle.

Codex prompt (copy/paste):
```
You are Codex working in /Users/noisebox/Documents/3_Development/Repos/copy-that.
Phase 2: artifact pass-through and UI layout fixes.
Backend tasks:
1) Add `artifacts: ArtifactBundle` to responses in:
   - `src/copy_that/interfaces/api/colors.py`
   - `src/copy_that/interfaces/api/spacing.py`
2) Ensure debug artifacts are returned from:
   - `src/copy_that/extractors/color/cv_extractor.py`
   - `src/copy_that/extractors/spacing/cv_extractor.py`
3) Include artifacts in SSE payloads in `src/copy_that/interfaces/api/multi_extract.py`.
Frontend tasks:
4) Rework layout to keep token panels above the fold:
   - `frontend/src/App.tsx`, `frontend/src/App.css`
5) Wire diagnostics panel to incoming artifacts:
   - `frontend/src/components/diagnostics-panel/*`
   - `frontend/src/features/explorer/TokenExplorer.tsx`
6) Auto-collapse upload panel post-extraction with explicit toggle:
   - `frontend/src/features/upload/UploadPanel.tsx`
Acceptance:
- Color and spacing endpoints return `artifacts.images/json`.
- Diagnostics panel shows real overlays and JSON when present.
```

---

### Phase 3 (P1) - Typography + Shadow Artifacts + UI Scanability

Goal:
- Add OCR/text overlays and shadow diagnostics.
- Make typography metadata readable and restore hidden color metadata.

Codex prompt (copy/paste):
```
You are Codex working in /Users/noisebox/Documents/3_Development/Repos/copy-that.
Phase 3: typography + shadow artifacts and UI scanability.
Backend tasks:
1) Add debug generation for OCR bbox overlay + size heatmap.
2) Surface typography artifacts in `src/copy_that/interfaces/api/typography.py`.
3) Surface shadow masks, penumbra map, and light direction JSON in
   `src/copy_that/interfaces/api/shadows.py`.
Frontend tasks:
4) Restore color detail header metadata visibility:
   `frontend/src/features/visual-extraction/components/color/color-detail-panel/ColorDetailPanel.css`
5) Make typography metadata readable with labeled groups:
   `frontend/src/features/visual-extraction/components/typography/TypographyInspector.tsx`
Acceptance:
- Typography endpoint returns OCR overlay + size heatmap artifacts.
- Shadow endpoint returns mask + penumbra + light vector diagnostics.
```

---

### Phase 4 (P2) - Geometry + Missing Token Types

Goal:
- Add geometry orientation diagnostics and implement border/radius, opacity, state layer tokens.

Codex prompt (copy/paste):
```
You are Codex working in /Users/noisebox/Documents/3_Development/Repos/copy-that.
Phase 4: geometry + missing token types.
Tasks:
1) Add LSD line detection + vanishing point estimation in
   `src/copy_that/extractors/geometry/depth_normals.py` and surface artifacts in
   `src/copy_that/interfaces/api/geometry.py`.
2) Implement border/radius extractor (edge + arc fitting) and API route.
3) Implement opacity estimator (local color-line) and API route.
4) Emit explicit state-layer tokens in color pipeline.
5) Update W3C export mapping for new token types.
Acceptance:
- Geometry endpoint includes line overlay + vanishing point JSON.
- New token types return tokens, confidence, and artifacts.
```

---

### Phase 5 (P3) - Gradient + Animation + Streaming QA

Goal:
- Add gradient extraction, define animation as metadata-only, and add streaming tests.

Codex prompt (copy/paste):
```
You are Codex working in /Users/noisebox/Documents/3_Development/Repos/copy-that.
Phase 5: gradient + animation + streaming QA.
Tasks:
1) Implement gradient extraction (OKLCH fit) with residual map artifacts.
2) Define animation tokens as metadata-only (no CV extraction).
3) Add Playwright streaming tests to verify artifact visibility:
   `frontend/playwright/*` or `frontend/tests/playwright/*`.
Acceptance:
- Gradient endpoint returns direction map + residuals.
- Streaming UI tests assert progressive artifact rendering.
```

---

## 7) Validation and QA Checklist

- Exporter validation tests for format, color, resolver.
- API tests assert `artifacts.images` and `artifacts.json` exist (empty arrays allowed).
- Snapshot tests for PNG dimensions and non-empty base64 outputs.
- Frontend streaming tests for artifact rendering.

---

## 8) Risks and Mitigations

- Large artifact payloads -> downscale to 512px max, PNG compression.
- OCR noise -> add text detection (CRAFT/DBNet) + confidence thresholding.
- Shadow false positives -> use illumination-invariant ratio imaging.
- UI performance -> memoize heavy panels and avoid repeated transformations.

---

## 9) Open Decisions

- W3C exporter: extend `src/core/tokens/adapters/w3c.py` (single exporter; no parallel module).
- Diagnostics visibility: gated behind toggles (default collapsed).
- First generator targets: React and CSS (aligned with app UI usage and future design taxonomy storage).

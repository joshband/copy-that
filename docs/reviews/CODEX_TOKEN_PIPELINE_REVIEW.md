# Codex Token Pipeline Review

Date: 2026-01-01
Owner: Codex
Scope: Design-token extraction pipelines + diagnostic artifact pass-through

## 1) Scope And Method

This review catalogs current extraction pipelines for each design token category, lists the algorithms used, identifies gaps, and proposes prioritized improvements and diagnostics. The intent is to enable deterministic, explainable extraction with high-fidelity intermediate artifacts that can be surfaced to the frontend.

Assumptions:
- Single-image extraction dominates; multi-image consistency is a secondary objective.
- Most inputs are UI screenshots or UI-like images (not necessarily photorealistic).
- Artifacts must be API-friendly (base64 PNG or small JSON payloads) and lightweight.

Out of scope:
- UI styling and layout (frontend visual design).
- Training custom ML models.

---

## 2) Token Coverage Summary

| Token Type | Current Pipeline | Key Algorithms | Diagnostic Artifacts Today | Gaps | Priority |
| --- | --- | --- | --- | --- | --- |
| Color | CV + AI (Claude/OpenAI) | SLIC superpixels, palette quantization, K-means, OKLCH analysis | Debug overlay, segmented palette (not in API) | No artifact pass-through in API | P0 |
| Spacing | CV + AI (OpenAI) | Connected components, gap clustering, grid inference, optional FastSAM/LayoutParser/UIED | Spacing overlay (not in API) | No artifact pass-through in API | P0 |
| Typography | AI (Claude) + CV OCR (Tesseract) | OCR grouping by size buckets | None | No artifact pass-through in API; no OCR overlays | P1 |
| Shadow | CV + AI (Claude) + shadowlab pipeline | Threshold + morphology, optional multi-stage pipeline | shadowlab artifacts on disk | No artifact pass-through in API | P1 |
| Geometry | Depth-Anything V2 + gradient normals | Depth inference, Sobel gradients, optional Marigold | Depth/normals/gradients/confidence in API | Missing vanishing points/plane normals | P2 |
| Border/Radius | Not implemented | n/a | None | Entire pipeline missing | P2 |
| Opacity | Not implemented | n/a | None | Entire pipeline missing | P2 |
| State Layer | Partial (color variants) | OKLCH lightness shift | None | No explicit tokens/artifacts | P2 |
| Gradient | Not implemented | n/a | None | Entire pipeline missing | P3 |
| Animation | Not extractable from single image | n/a | None | Requires video or metadata | P3 |

---

## 3) Pipeline Details And Improvements (Per Token)

### 3.1 Color Tokens

Current:
- CV extractor: SLIC superpixels + palette quantization (PIL), coloraide for OKLCH/HSL.
- KMeans clustering (OpenCV), Delta-E dedup, role assignment, contrast metadata.
- AI extractor: Claude Sonnet 4.5; OpenAI fallback.

Gaps:
- Debug artifacts exist but are not returned by API.
- No explicit component color masks (color attribution to UI elements).

Improvements:
- Add gray-world or shades-of-gray color constancy before palette extraction.
- Introduce component-aware color attribution using segmentation masks (FastSAM/SAM).
- Stabilize palette across multi-image sets (EMD/Wasserstein matching in OKLCH).

Artifacts to surface:
- Superpixel overlay PNG.
- Segmented palette PNG.
- Palette swatch strip PNG.
- Contrast matrix JSON.

Relevant code:
- `src/copy_that/extractors/color/cv_extractor.py`
- `src/copy_that/extractors/color/clustering.py`
- `src/copy_that/application/cv/debug_color.py`
- `src/copy_that/interfaces/api/colors.py`

---

### 3.2 Spacing Tokens

Current:
- CV extractor: connected components -> bboxes -> gaps; base unit inference; optional FastSAM + LayoutParser + UIED.
- AI extractor: OpenAI Vision with deterministic fallback.

Gaps:
- Spacing overlay and gap diagnostics are not surfaced via API.

Improvements:
- Fit grid periodicity using RANSAC on detected lines.
- Add gap outlier rejection via MAD.
- Add baseline rhythm extraction from text-line detection.

Artifacts to surface:
- Spacing overlay PNG (boxes + guides + grid).
- Gap histogram JSON (gap sizes + counts).
- Grid alignment heatmap PNG.

Relevant code:
- `src/copy_that/extractors/spacing/cv_extractor.py`
- `src/copy_that/application/cv/debug_spacing.py`
- `src/copy_that/interfaces/api/spacing.py`

---

### 3.3 Typography Tokens

Current:
- AI extractor: Claude Sonnet 4.5 for font family/size/weight.
- CV fallback: Tesseract OCR grouped by size buckets.
- Typography recommender uses style inference from colors.

Gaps:
- No OCR/text-region artifacts passed to API.
- CV typography does not estimate font family beyond a placeholder.

Improvements:
- Add text detection (CRAFT/DBNet) before OCR for stable bboxes.
- Use font classification (DeepFont/FontNet) for family hints.
- Estimate stroke width for weight normalization.

Artifacts to surface:
- OCR/text bbox overlay PNG.
- Font-size heatmap PNG.
- Baseline/rhythm overlay PNG.

Relevant code:
- `src/copy_that/application/typography_extractor.py`
- `src/copy_that/extractors/typography/cv_extractor.py`
- `src/copy_that/interfaces/api/typography.py`

---

### 3.4 Shadow Tokens

Current:
- CV extractor: threshold + morphology on grayscale.
- AI extractor: Claude Opus 4.1.
- Shadowlab: multi-stage pipeline (illumination -> candidates -> ML mask -> intrinsic -> geometry -> lighting).

Gaps:
- Shadowlab artifacts exist but are not returned by API.
- CV shadow extraction lacks penumbra and light direction diagnostics.

Improvements:
- Integrate illumination-invariant ratio image for baseline shadow mask.
- Estimate penumbra widths via edge profile sampling.
- Derive dominant light direction from shadow boundary orientations.

Artifacts to surface:
- Shadow mask PNG.
- Shadow boundary/penumbra map PNG.
- Light direction vector JSON.

Relevant code:
- `src/copy_that/extractors/shadow/cv_extractor.py`
- `src/copy_that/shadowlab/orchestrator.py`
- `src/copy_that/interfaces/api/shadows.py`

---

### 3.5 Geometry Tokens

Current:
- Depth-Anything V2 depth.
- Sobel gradient normals + confidence map.
- Optional Marigold normals on CUDA.

Gaps:
- No line/vanishing point artifacts.
- No plane-normal summaries.

Improvements:
- Add LSD line detection + vanishing point estimation.
- Fit dominant planes and emit plane normals.

Artifacts to surface:
- Edge/line overlay PNG.
- Vanishing point JSON.
- Plane normal summary JSON.

Relevant code:
- `src/copy_that/extractors/geometry/depth_normals.py`
- `src/copy_that/interfaces/api/geometry.py`

---

### 3.6 Border/Radius Tokens (Missing)

Proposed pipeline:
- Canny edges -> parallel line pairing -> stroke width estimation.
- Corner radius via arc fitting on corner contours.

Artifacts:
- Edge map PNG.
- Corner curvature overlay PNG.
- Stroke width heatmap PNG.

---

### 3.7 Opacity Tokens (Missing)

Proposed pipeline:
- Estimate foreground/background mixing using local color-line models.
- Require background estimation or segmentation masks.

Artifacts:
- Alpha estimate mask PNG.
- Residual error map PNG.

---

### 3.8 State Layer Tokens (Partial)

Current:
- OKLCH-based hover/active variants in color extraction.

Improvements:
- Explicit state-layer tokens per color with contrast constraints.
- If multi-state images available, infer state deltas directly.

Artifacts:
- State-variant swatch strip PNG.

---

### 3.9 Gradient Tokens (Missing)

Proposed pipeline:
- Fit linear gradients in OKLCH using least squares.
- Residual map to show confidence.

Artifacts:
- Gradient direction map PNG.
- Gradient stop plot JSON.

---

### 3.10 Animation Tokens (Missing)

Not extractable from static images.
- Requires video or interaction traces.

---

## 4) Artifact Pass-Through Standard (API Schema)

Define a shared artifact bundle for all token endpoints.

```
ArtifactBundle = {
  images: [
    {
      type: string,
      mime: "image/png",
      base64: string,
      confidence: number,
      stage: string,
      description: string
    }
  ],
  json: [
    {
      type: string,
      payload: object,
      confidence: number,
      stage: string
    }
  ]
}
```

Add `artifacts` to each token endpoint response, and to SSE events in `/api/v1/extract/stream`.

---

## 5) Visual Encodings (Token-Facing, Minimal)

These are encodings (not UI styling) that each token type should support:

- Color: swatch strip + contrast matrix.
- Spacing: ruler overlay + gap histogram.
- Typography: specimen strip (H1/body/caption) + size heatmap.
- Shadow: neutral card with shadow + penumbra map.
- Geometry: depth map + normals + confidence.
- Border: stroke width strip + radius arc overlay.
- Opacity: alpha checkerboard blend strip + alpha mask.
- Gradient: gradient bar + residual map.
- State layer: default/hover/active swatch strip.

---

## 6) Phased Implementation Plan (Codex-Ready)

### Phase 0 (P0): Artifact Schema And API Pass-Through

Goal:
- Add a unified `artifacts` field to all token extraction endpoints and streaming events.

Codex tasks:
```
1) Add ArtifactBundle model to `src/copy_that/interfaces/api/schemas.py`.
2) Update responses in `colors.py`, `spacing.py`, `typography.py`, `shadows.py`, `geometry.py` to include `artifacts`.
3) Update `multi_extract.py` SSE payloads to include artifacts per event.
4) Ensure `sanitize_json_value` and `sanitize_numbers` handle artifacts.
```

Success criteria:
- Each endpoint returns `artifacts.images` and `artifacts.json` (empty arrays allowed).

---

### Phase 1 (P0): Color + Spacing Artifact Wiring

Goal:
- Pass existing debug outputs through the API for color and spacing.

Codex tasks:
```
1) In `CVColorExtractor`, ensure `debug` payload includes overlay, segmented palette, contrast matrix.
2) In `colors.py`, surface debug artifacts as `artifacts.images/json` in the API response.
3) In `CVSpacingExtractor`, return spacing overlay + gap histogram.
4) In `spacing.py`, surface artifacts in response.
```

Success criteria:
- Color endpoint returns overlay + palette swatch + contrast matrix.
- Spacing endpoint returns spacing overlay + gap histogram.

---

### Phase 2 (P1): Typography Artifact Wiring

Goal:
- Provide OCR/text-region diagnostics for typography.

Codex tasks:
```
1) Add `debug_typography.py` to generate OCR bbox overlay + size heatmap.
2) Update `CVTypographyExtractor` to emit debug artifacts.
3) Surface artifacts in `typography.py` response.
```

Success criteria:
- Typography endpoint returns OCR overlay + size heatmap.

---

### Phase 3 (P1): Shadow Artifact Wiring

Goal:
- Expose shadow masks and light direction diagnostics.

Codex tasks:
```
1) Add shadow mask + boundary map generation in CV shadow extractor.
2) Wire shadowlab artifacts into `shadows.py` when enabled.
3) Surface artifacts in response (mask PNG, penumbra map, light direction JSON).
```

Success criteria:
- Shadow endpoint returns mask + boundary/penumbra maps + light vector JSON.

---

### Phase 4 (P2): Geometry Orientation Diagnostics

Goal:
- Add line/vanishing point artifacts to geometry.

Codex tasks:
```
1) Add LSD line detection in geometry extractor.
2) Estimate vanishing points and emit JSON.
3) Surface line overlay PNG + vanishing point JSON in `geometry.py`.
```

Success criteria:
- Geometry endpoint includes line overlay + vanishing point data.

---

### Phase 5 (P2): Border/Radius, Opacity, State Layer Tokens

Goal:
- Implement missing token categories with classical CV baselines.

Codex tasks:
```
1) Add extractors for border/radius (edge + arc fitting).
2) Add opacity estimation using local color-line model with background estimate.
3) Add explicit state-layer tokens in color pipeline.
4) Add API routes + W3C export mapping.
```

Success criteria:
- Each new token type has: tokens, confidence, artifacts, and W3C export.

---

### Phase 6 (P3): Gradient + Animation

Goal:
- Implement gradient extraction; define animation as metadata-only unless video input exists.

Codex tasks:
```
1) Fit linear/radial gradients in OKLCH and emit residual maps.
2) Add gradient tokens + artifacts in API + export.
3) Add animation token ingestion via metadata (no CV extraction).
```

Success criteria:
- Gradient tokens emitted with residual diagnostics; animation tokens are metadata-driven only.

---

## 7) Testing/Validation

- Add snapshot tests for artifact PNG outputs (base64 length > 0, dimensions match input).
- Add API tests ensuring `artifacts` exists and has deterministic keys.
- Add model-free unit tests for new CV primitives (edge detection, arc fitting, gradient fitting).
- Added: Playwright streaming artifacts test for color overlay + spacing overlay precedence (`frontend/tests/playwright/streaming-artifacts.spec.ts`).

---

## 8) Risks And Mitigations

- Risk: Debug artifacts large -> Mitigate via downscale to 512px max + PNG compression.
- Risk: OCR noise -> Mitigate with text detection (CRAFT/DBNet) and confidence filtering.
- Risk: Shadow false positives on textured backgrounds -> Mitigate with illumination-invariant ratio imaging.
- Risk: State-layer tokens misestimated from single image -> Mitigate by gating on multi-state evidence.

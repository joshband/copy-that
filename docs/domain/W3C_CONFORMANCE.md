# W3C Design Tokens conformance (Compat+)

**Date:** 2026-09-21  
**Spec:** [Design Tokens Format Module 2025.10](https://www.designtokens.org/TR/2025.10/format/)  
**Mode:** Export-complete (A) + Compat+ — every official `$type` can appear on `/design-tokens/export/w3c` without breaking existing consumers.  
**SoT:** This file (supersedes archived `DESIGN_TOKENS_W3C_STATUS.md`).

## Official types (13)

| `$type` | Source in Copy That |
|---------|---------------------|
| `color` | Extracted (hex string values — not strict `{colorSpace, components}`) |
| `dimension` | **Companions** dual-written at spacing build (`dimension` section); spacing tokens stay under `spacing` with `$type: dimension` (Compat+). Export synth fallback. |
| `fontFamily` | **Persisted atoms** at typography build with COMPOSES; export synth fallback |
| `fontWeight` | **Persisted atoms** at typography build with COMPOSES; export synth fallback |
| `duration` | **UI-kit / style-cue** heuristic when confidence ≥ 0.55; else **preset** (low confidence) |
| `cubicBezier` | **UI-kit / style-cue** easing; else **preset** (low confidence) |
| `number` | **First-class opacity** from shadows + UI alpha (`opacity` section); line-height **derived** (`number` section) |
| `strokeStyle` | **CV/heuristic** solid vs dashed when confidence ≥ threshold; else **preset** |
| `border` | **CV/heuristic** edge width + radius; **composed** from layout border width + strokeStyle (+ color ref) |
| `transition` | **Composed** from duration + cubicBezier (extracted when cues strong; else synth/preset) |
| `shadow` | Extracted; **preset** soft shadow if none |
| `gradient` | **CV** linear-band / stop clustering (+ optional palette confirm → `source=ai`); **synth** color-pair fallback below confidence (Compat+ object form with `stops`) |
| `typography` | Extracted (or rule-based recommendation when empty) |

## Compat+ deltas (retained on purpose)

| Extension | Notes |
|-----------|--------|
| `spacing` section | Tokens live under `spacing`; many emit `$type: dimension` (adapter). Directional maps may use `$type: spacing`. **Section name ≠ `$type`.** |
| `dimension` section | Explicit DTCG companions dual-written from spacing; `$type: dimension`. |
| `layout` section | Non-spec group for radius/border-width/grid; may emit `$type: layout` or `dimension`. |
| Hex colors | `$value` often `#RRGGBB` instead of Color Module object form. |
| `opacity` section | Values use `$type: number`; section name is product-facing. |
| `font.family` / `font.size` | Legacy TokenType enum values may still appear from recommender paths; mapped toward `fontFamily` / `dimension` where possible. |
| Flat export `value` alias | `/export/w3c` flat form duplicates `$value` as `value` for UI. |

## Export shapes

- **Internal:** DTCG-shaped sectioned payload (`$type` / `$value`).  
- **Public HTTP:** flattened helper keeps legacy `value` beside `$value` for UI compatibility (`copy_that.core_tokens` W3C adapters / design-tokens export route).  
- Alias tokens use `{token/...}` refs; composites (shadow / typography) retain refs.  
- `$extensions` reserved for confidence + provenance (algorithms stay out of `$value`).

## JSON Schema scaffolding (2025.10)

Under `src/copy_that/design_tokens/schemas/2025_10/`:

- `format.schema.json` — full token document  
- `color.schema.json` — color section  
- `resolver.schema.json` — resolver documents  

Resolver helper: `src/copy_that/design_tokens/resolver.py`. Spec pointers: [../standards/design_tokens_cg/README.md](../standards/design_tokens_cg/README.md).

## Explicit non-goals

- Strict Color Module object migration  
- Renaming all spacing tokens away from the `spacing` section  
- Claiming CV/AI extraction for every type  
- Flutter / Figma generators as MVP bar  

## Code entry points

- Synthesis: [`src/copy_that/services/type_coverage_service.py`](../../src/copy_that/services/type_coverage_service.py)  
- Motion presets: [`src/copy_that/services/motion_service.py`](../../src/copy_that/services/motion_service.py)  
- Validator type set: [`src/copy_that/domain/w3c_design_tokens.py`](../../src/copy_that/domain/w3c_design_tokens.py)  
- Format schema: [`src/copy_that/design_tokens/schemas/2025_10/format.schema.json`](../../src/copy_that/design_tokens/schemas/2025_10/format.schema.json)  
- Extractor capability map: [`src/copy_that/extractors/dtcg_capability.py`](../../src/copy_that/extractors/dtcg_capability.py)  
- Coverage tests: [`tests/unit/api/test_w3c_all_types_coverage.py`](../../tests/unit/api/test_w3c_all_types_coverage.py)

**Extractor fidelity:** P2c is export-complete (extract-or-synth). Live image extractors: color / spacing / typography / shadow / **gradient**. Phase 2 dual-writes `fontFamily` / `fontWeight` and `dimension` companions. Phase 3: `border` / `strokeStyle` + opacity/`number`. Phase 5: UI-kit `duration` / `cubicBezier` / `transition`. Prefer extract over synth when confidence ≥ 0.55; presets never claim high confidence.

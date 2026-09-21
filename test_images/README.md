# Test Images

Committed source fixtures for pipeline and e2e tests. Drop additional images here for local experiments.

## Quick Start

```bash
# Full pipeline with token extraction
uv run python scripts/process_test_images.py

# Method comparison (all shadow detection approaches)
uv run python scripts/test_shadow_methods.py

# Process a specific image
uv run python scripts/process_test_images.py test_images/IMG_8405.jpeg
```

## Committed fixtures

Source JPEGs (`IMG_*.jpeg`) plus `components/` and `non-deadpan/` samples are tracked for tests.

**Processed shadow outputs are not committed.** Directories such as `processedImageShadows/`, `processedImageShadows_v2/`, and `processedImageShadows_enhanced/` are gitignored — regenerate them locally with the scripts below.

## Scripts

### `process_test_images.py` — Full Pipeline
Runs complete 8-stage shadow pipeline with token extraction.

**Output:** `test_images_output/{image_name}/`
- `shadow_tokens.json` — Extracted shadow tokens
- `artifacts/` — Stage outputs (PNG files)
- `comparison.png` — Side-by-side visualization

### `test_shadow_methods.py` — Method Comparison
Compares all shadow detection methods side-by-side.

**Output (local):** `test_images/processedImageShadows/{image_name}/`
```
├── 00_original.png          # Input image
├── 02_illumination.png      # Illumination invariant (Stage 02)
├── 03_classical.png         # Classical candidates (Stage 03)
├── 04a_bdrar_features.png   # BDRAR-style multi-scale features
├── 04b_enhanced_classical.png # Enhanced classical detection
├── 04c_full_shadow_hq.png   # Full model (SAM + BDRAR if available)
├── 04d_fast_shadow.png      # Fast mode (no SAM)
├── 05a_reflectance.png      # Intrinsic: reflectance layer
├── 05b_shading.png          # Intrinsic: shading layer
├── 06_depth.png             # MiDaS depth estimation
└── comparison_grid.png      # 2x3 comparison grid
```

## Pipeline Stages Visualized

Each image goes through 8 stages:

| Stage | Output | Description |
|-------|--------|-------------|
| 01 | `00_original.png` | Input preprocessing |
| 02 | `02_illumination.png` | Log-chromaticity illumination invariant |
| 03 | `03_classical.png` | Morphological shadow candidates |
| 04 | `04*.png` | ML shadow detection (multiple methods) |
| 05 | `05a/b*.png` | Intrinsic decomposition (reflectance + shading) |
| 06 | `06_depth.png` | Monocular depth estimation |
| 07 | (internal) | Light direction fitting |
| 08 | (internal) | Fusion and token generation |

## Comparison Grid Layout

The `comparison_grid.png` shows a 2×3 grid:

```
┌─────────────┬─────────────┬─────────────┐
│  Original   │ Illumination│  Classical  │
├─────────────┼─────────────┼─────────────┤
│  Enhanced   │ Full Shadow │   Shading   │
└─────────────┴─────────────┴─────────────┘
```

## Supported Formats

- JPG, JPEG, PNG, WEBP, BMP, TIFF

## Notes

- First run downloads ML models (~1GB, may take 10-15s)
- Subsequent runs use cached models (~500ms per image)
- If models fail to load, fallback to classical methods
- Results can be reviewed in any image viewer
- Models cache outside the repo (e.g. `~/.cache/huggingface`); do not commit weights or processed PNGs

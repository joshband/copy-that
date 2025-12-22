# Color Extraction Lifecycle Artifacts

**Purpose:** Define the intermediate visual and informational artifacts that document the color extraction lifecycle (CV, ML, AI, heuristics), and map them to algorithms, libraries, and API debug payloads.

## Scope

- Covers CV-first extraction artifacts emitted by the CV color extractor.
- Catalogs AI and multi-extractor algorithms with their narrative outputs.
- Aligns artifacts with `ArtifactBundle` in `src/copy_that/interfaces/api/schemas.py`.

## Stage Map (Implemented CV Artifacts)

| Stage ID | Algorithms | Libraries | Debug Keys | Artifact Type | Narrative Use |
| --- | --- | --- | --- | --- | --- |
| ingest.normalize | EXIF transpose, resize, RGB/BGR conversion | Pillow, OpenCV | `normalized_rgb_base64` | `normalized-rgb` image | Show the input as the pipeline actually sees it. |
| ingest.gray_blur | grayscale + Gaussian blur | OpenCV | `gray_blur_base64` | `gray-blur` image | Show the edge-ready luminance view. |
| cv.superpixels | SLIC superpixels + boundary overlay | scikit-image, NumPy | `overlay_png_base64` | `overlay` image | Show region boundaries and palette mapping. |
| cv.superpixel_boundaries | SLIC boundary map | scikit-image, NumPy | `superpixel_boundaries_png_base64` | `superpixel-boundaries` image | Show raw superpixel boundaries before palette mapping. |
| cv.palette_assignment | palette assignment per superpixel | scikit-image, NumPy | `palette_assignment_png_base64` | `palette-assignment` image | Show palette index assigned to each region. |
| cv.edge_cues | Canny edge detection | OpenCV | `edge_map_base64` | `edge-map` image | Show segmentation cues and structural edges. |
| cv.quantization | RGB quantization | OpenCV, NumPy | `quantized_base64` | `quantized` image | Show palette simplification before clustering. |
| cv.segmentation | k-means (cluster centers + coverage) | OpenCV, NumPy | `segmented_palette` | `segmented-palette` JSON | Show cluster coverage and dominant regions. |
| cv.background | patch sampling + OKLCH nearest token | Pillow, NumPy, coloraide | `background_samples`, `background_samples_overlay_base64` | `background-samples` JSON + image | Show which patches drive background inference. |
| cv.superpixel_stats | SLIC configuration metadata | scikit-image | `superpixel_stats` | `superpixel-stats` JSON | Record segmentation parameters for reproducibility. |
| analysis.histogram | RGB/HSV histograms | OpenCV, NumPy | `histograms` | `histograms` JSON | Show channel distribution and hue density. |
| analysis.hue | hue band distribution | OpenCV, NumPy | `hue_distribution` | `hue-distribution` JSON | Summarize color families by share. |
| analysis.spatial | grid dominant regions | OpenCV, NumPy | `dominant_regions` | `dominant-regions` JSON | Show spatial dominance (where colors live). |
| analysis.properties | brightness/saturation/lightness stats | OpenCV, NumPy | `image_properties` | `image-properties` JSON | Quantify overall color climate. |
| analysis.contrast | WCAG contrast matrix | coloraide | `contrast_matrix` | `contrast-matrix` JSON | Show text/background viability. |
| analysis.palette_strip | palette swatch strip | Pillow | `palette_strip_png_base64` | `palette-strip` image | Show final palette lineup for quick scan. |
| analysis.palette_histogram | palette prominence bars | Pillow, NumPy | `palette_histogram_png_base64`, `palette_histogram` | `palette-histogram` image + JSON | Show prominence weights for palette colors. |

## Algorithm Inventory (CV + ML + AI)

### CV / Heuristic
- EXIF transpose and downsample: `src/cv_pipeline/preprocess.py` (Pillow)
- SLIC superpixels: `src/copy_that/application/cv/debug_color.py` (scikit-image)
- Palette quantization: `src/copy_that/application/cv/color_cv_extractor.py` (Pillow)
- k-means clustering + adaptive k: `src/copy_that/extractors/color/clustering.py` (OpenCV)
- OKLCH distance + Delta E: `src/copy_that/application/color_utils.py` (coloraide)
- Background sampling: `src/copy_that/application/cv/color_cv_extractor.py`
- Contrast metrics (WCAG): `src/copy_that/application/color_utils.py`
- Harmony and semantic naming: `src/copy_that/application/color_utils.py`, `src/copy_that/application/semantic_color_naming.py`

### AI / ML
- Claude Sonnet 4.5 structured extraction: `src/copy_that/application/color_extractor.py` (anthropic)
- OpenAI GPT-4o vision fallback: `src/copy_that/application/openai_color_extractor.py` (openai)
- Multi-extractor aggregation + Delta E dedup: `src/copy_that/extractors/color/orchestrator.py`, `src/copy_that/tokens/color/aggregator.py`

## API Artifact Mapping

Artifacts are surfaced via `ArtifactBundle` in `src/copy_that/interfaces/api/colors.py`:

- Images: `normalized-rgb`, `gray-blur`, `overlay`, `superpixel-boundaries`, `palette-assignment`, `edge-map`, `quantized`, `palette-strip`, `palette-histogram`, `background-samples`
- JSON: `segmented-palette`, `palette-histogram`, `superpixel-stats`, `histograms`, `hue-distribution`, `dominant-regions`, `image-properties`, `background-samples`, `contrast-matrix`

Stage identifiers use `ingest`, `cv`, and `analysis` to keep ordering consistent in the UI.

## Narrative Cues For Demos

- Start with `normalized-rgb` to show preprocessing.
- Transition to `gray-blur` and `edge-map` to show structural cues.
- Use `overlay` and `segmented-palette` to show palette formation.
- Use `palette-strip` and `palette-histogram` to show final lineup and weights.
- Use `background-samples` to explain background inference.
- Use `histograms`, `hue-distribution`, and `dominant-regions` to explain distribution and dominance.
- End with `contrast-matrix` to connect palette quality to accessibility.

## Color Science Artifacts (Non-Debug Showcase)

These artifacts are derived from palette colors and color science algorithms. They are not tied to
pixel-level debug views and can be generated for CV or AI extractors.

**API toggle:** set `include_science_artifacts=true` on `/api/v1/colors/extract`, `/api/v1/colors/extract-streaming`,
`/api/v1/colors/extract/multi`, and `/api/v1/colors/batch` to include `stage="science"` artifacts alongside any debug payloads.

**Images:**
- `palette-strip`: final palette lineup
- `palette-histogram`: prominence weights
- `oklch-scatter`: lightness vs chroma scatter
- `delta-e-heatmap`: perceptual distance matrix
- `contrast-heatmap`: WCAG contrast matrix
- `temperature-bar`: warm/cool/neutral balance

**JSON:**
- `color-metrics`: per-color HSL/HSV/OKLCH, temperature, luminance, harmony, semantic names
- `palette-diversity`: mean/std/min/max Delta-E
- `delta-e-matrix`: pairwise Delta-E values
- `contrast-matrix`: pairwise contrast ratios
- `temperature-summary`: warm/cool/neutral counts

## Artifact Generation Script

Use `scripts/generate_color_artifacts.py` to emit artifacts to `storage/color_artifacts/<image_name>/` and produce a manifest for each image.

Use `scripts/generate_color_science_artifacts.py` to emit non-debug color science artifacts to
`storage/color_science_artifacts/<image_name>/`.

Example:

```
python scripts/generate_color_artifacts.py \
  /Users/noisebox/Desktop/midjourney/example1.png \
  /Users/noisebox/Desktop/midjourney/example2.png \
  /Users/noisebox/Desktop/midjourney/example3.png \
  --out-dir storage/color_artifacts \
  --max-colors 10 \
  --copy-input
```

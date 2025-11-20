# Extractor Routing Table

**Single Source of Truth for Token → Extractor → CV/AI → Confidence Pipeline**

Version: 1.0.0
Last Updated: 2025-11-11
Schema: routing-table-v1

---

## Overview

This file serves as the **routing table** that maps taxonomy tokens to extractors, CV primitives, AI models, confidence scoring, and versioning. It is the single source of truth for the entire extraction pipeline.

### Four-Dimensional Mapping

```
taxonomy_token → extractor → CV_primitives → models → scoring → version
```

Every extraction run starts by resolving requested tokens through this table, which returns:
- Which extractor(s) to call
- Which libraries/models they depend on
- Default parameters and thresholds
- Fallback strategies when primary fails
- Version hash for cache keys and reproducibility

---

## Schemas

### TokenPlan (Input)

```json
{
  "image_id": "7A03623D-ED31-4AAF-A2EB-6EF0FA2357AC",
  "tokens": [
    "composition.logic",
    "component_families.primary_panels.form",
    "color_system.palette_description",
    "stylistic_lineage.*"
  ],
  "resolved": [
    {
      "token": "composition.logic",
      "extractor": "CompositionalLogicExtractor",
      "models": ["OpenCV.hough_lines", "OpenCV.contours", "RAFT.flow"],
      "fallbacks": ["CLIP.gridness_probe"],
      "params": {"grid_threshold": 0.6},
      "version": "cle-0.3.2"
    }
  ]
}
```

### ExtractorResult (Output)

```json
{
  "token": "composition.logic",
  "value": "grid-less modular",
  "confidence": 0.83,
  "features": {
    "grid_score": 0.22,
    "cluster_silhouette": 0.71
  },
  "provenance": {
    "extractor": "CompositionalLogicExtractor@0.3.2",
    "models": ["OpenCV 4.9", "RAFT 1.0"],
    "image_sha256": "<hash>"
  },
  "timing_ms": 187
}
```

### RunReport (Audit)

```json
{
  "image_id": "7A03623D-ED31-4AAF-A2EB-6EF0FA2357AC",
  "tokens_requested": 18,
  "tokens_filled": 16,
  "coverage": 0.89,
  "avg_confidence": 0.78,
  "cache_hits": 7,
  "version_lock": {
    "mapping_sha": "<mdfile_sha>",
    "code_sha": "<repo_sha>"
  }
}
```

---

## Routing Table

### Foundation Tokens

| Token | Extractor | CV Primitives | Models | Fallbacks | Params | Confidence Weights | Version |
|-------|-----------|---------------|--------|-----------|--------|-------------------|---------|
| `color_system.palette` | ColorExtractor | K-means clustering, CIEDE2000 distance | scikit-learn.KMeans, NumPy | CLIP color tags | `k=12, lab_space=true` | `{model:0.6, agree:0.3, data:0.1}` | col-1.3.2 |
| `color_system.semantic_roles` | ColorExtractor | Role mapping heuristics, WCAG contrast | NumPy, custom | GPT-4V semantic probe | `contrast_min=4.5` | `{model:0.5, agree:0.4, data:0.1}` | col-1.3.2 |
| `spacing.scale` | SpacingExtractor | Edge detection, distance histogram | OpenCV.Canny, NumPy | Heuristic quantization | `edge_threshold=50, bins=20` | `{model:0.7, agree:0.2, data:0.1}` | spe-0.8.1 |
| `typography.font_families` | FontFamilyExtractor | OCR + font classification | Tesseract, EasyOCR | Google Fonts API match | `min_confidence=0.6` | `{model:0.8, agree:0.15, data:0.05}` | ffe-0.5.2 |
| `typography.scale` | TypographyExtractor | Text region detection, size clustering | OpenCV, DBSCAN | Manual histogram | `eps=2, min_samples=3` | `{model:0.65, agree:0.25, data:0.1}` | tye-0.6.0 |
| `shadow.elevation_levels` | ShadowExtractor | Shadow detection, blur radius estimation | OpenCV.GaussianBlur, custom | Heuristic depth mapping | `blur_min=2, levels=5` | `{model:0.6, agree:0.3, data:0.1}` | she-0.7.3 |
| `opacity.values` | OpacityExtractor | Alpha channel analysis, transparency detection | OpenCV, NumPy | Histogram quantization | `bins=10, threshold=0.05` | `{model:0.7, agree:0.2, data:0.1}` | ope-0.4.1 |
| `transition.timings` | TransitionExtractor | Motion blur analysis, frame differencing | OpenCV, SciPy | Heuristic timing curves | `motion_threshold=5` | `{model:0.5, agree:0.4, data:0.1}` | tre-0.3.5 |
| `blur.filter_types` | BlurFilterExtractor | Blur detection, FFT analysis | OpenCV.Laplacian, NumPy.fft | Variance thresholding | `var_threshold=100` | `{model:0.65, agree:0.25, data:0.1}` | bfe-0.2.8 |
| `border_radius.values` | BorderRadiusExtractor | Contour curvature analysis | OpenCV.findContours, curvature | Histogram quantization | `curvature_bins=8` | `{model:0.7, agree:0.2, data:0.1}` | bre-0.5.4 |
| `zindex.layer_hierarchy` | ZIndexExtractor | Cast shadow analysis, occlusion detection | OpenCV, custom | Heuristic depth ordering | `shadow_threshold=30` | `{model:0.6, agree:0.3, data:0.1}` | zie-0.4.0 |
| `iconsize.scale` | IconSizeExtractor | Small object detection, size clustering | OpenCV.SimpleBlobDetector, DBSCAN | Histogram quantization | `min_area=16, max_area=2048` | `{model:0.65, agree:0.25, data:0.1}` | ise-0.3.7 |

---

### Component Tokens

| Token | Extractor | CV Primitives | Models | Fallbacks | Params | Confidence Weights | Version |
|-------|-----------|---------------|--------|-----------|--------|-------------------|---------|
| `component_families.buttons` | ComponentTokenExtractor | Rectangle detection, text proximity | OpenCV.findContours, Tesseract | CLIP "button-ness" probe | `aspect_ratio=[0.3,3.0]` | `{model:0.65, agree:0.25, data:0.1}` | cte-1.6.0 |
| `component_families.inputs` | ComponentTokenExtractor | Text field detection, border analysis | OpenCV, Tesseract | CLIP "input field" probe | `aspect_ratio=[2.0,10.0]` | `{model:0.6, agree:0.3, data:0.1}` | cte-1.6.0 |
| `component_families.cards` | ComponentTokenExtractor | Container detection, hierarchy | OpenCV.findContours, SAM | Containment heuristic | `min_area=1000` | `{model:0.65, agree:0.25, data:0.1}` | cte-1.6.0 |
| `component_families.primary_panels` | ComponentTokenExtractor | Large container detection, SAM segmentation | SAM, Detectron2, YOLOv8 | U²-Net | `min_panel_area=500` | `{model:0.7, agree:0.2, data:0.1}` | cte-1.6.0 |
| `border.widths` | BorderExtractor | Edge detection, width measurement | OpenCV.Canny, custom | Quantization to scale | `quantize_to=[1,2,4,8]` | `{model:0.7, agree:0.2, data:0.1}` | boe-0.6.2 |
| `border.styles` | BorderExtractor | Pattern detection (solid/dashed/dotted) | OpenCV, FFT | Heuristic classification | `pattern_threshold=0.6` | `{model:0.6, agree:0.3, data:0.1}` | boe-0.6.2 |
| `state_layers.hover` | StateLayerExtractor | Overlay detection, opacity analysis | OpenCV, NumPy | Material Design 3 defaults | `opacity_scale=[0.08,0.12,0.16]` | `{model:0.5, agree:0.4, data:0.1}` | sle-0.5.1 |
| `state_layers.focus` | StateLayerExtractor | Focus ring detection, border analysis | OpenCV, custom | Heuristic ring detection | `ring_width=[2,4]` | `{model:0.55, agree:0.35, data:0.1}` | sle-0.5.1 |
| `gradient.types` | GradientExtractor | Gradient analysis, direction detection | NumPy.gradient, SciPy | Heuristic classification | `angle_bins=8` | `{model:0.65, agree:0.25, data:0.1}` | ge-0.9.1 |
| `mobile.touch_targets` | MobileExtractor | Small component detection, size analysis | OpenCV, custom | 44x44px minimum | `min_size=44` | `{model:0.7, agree:0.2, data:0.1}` | me-0.7.5 |
| `mobile.safe_areas` | MobileExtractor | Screen edge detection, inset analysis | OpenCV, custom | Device-specific defaults | `edge_threshold=20` | `{model:0.6, agree:0.3, data:0.1}` | me-0.7.5 |
| `audio_plugin.knobs` | AudioPluginComponentExtractor | Circle detection, Hough transform | OpenCV.HoughCircles, custom | Size clustering | `min_radius=10, max_radius=100` | `{model:0.75, agree:0.2, data:0.05}` | ape-0.8.3 |
| `audio_plugin.sliders` | AudioPluginComponentExtractor | Line detection, track analysis | OpenCV.HoughLinesP, custom | Length-width ratio | `aspect_ratio=[4.0,20.0]` | `{model:0.7, agree:0.2, data:0.1}` | ape-0.8.3 |
| `audio_plugin.vu_meters` | AudioPluginComponentExtractor | Bar/needle detection, gradient analysis | OpenCV, NumPy | Shape classification | `aspect_ratio=[0.2,5.0]` | `{model:0.65, agree:0.25, data:0.1}` | ape-0.8.3 |
| `style_mood.keywords` | StyleMoodExtractor | Color harmony, aesthetic classification | Custom heuristics, CLIP | GPT-4V keyword generation | `topk=5` | `{model:0.5, agree:0.4, data:0.1}` | sme-0.4.6 |

---

### Visual Style Tokens (Visual DNA 2.0)

| Token | Extractor | CV Primitives | Models | Fallbacks | Params | Confidence Weights | Version |
|-------|-----------|---------------|--------|-----------|--------|-------------------|---------|
| `material.texture` | MaterialExtractor | Specular highlight detection, roughness | OpenCV, TinyConv | CLIP material tags | `glossiness_tau=0.7` | `{model:0.65, agree:0.25, data:0.1}` | me-0.7.0 |
| `material.finish` | MaterialExtractor | Surface analysis, metallic detection | OpenCV, custom | CLIP finish probe | `metallic_threshold=0.6` | `{model:0.6, agree:0.3, data:0.1}` | me-0.7.0 |
| `lighting.type` | LightingExtractor | Shadow direction, highlight analysis | OpenCV, normal-from-shading | CLIP lighting probe | `shadow_angle_bins=8` | `{model:0.65, agree:0.25, data:0.1}` | le-0.6.4 |
| `lighting.intensity` | LightingExtractor | Brightness histogram, contrast ratio | NumPy, OpenCV | Histogram percentiles | `percentiles=[5,50,95]` | `{model:0.7, agree:0.2, data:0.1}` | le-0.6.4 |
| `lighting.color_temperature` | LightingExtractor | White balance analysis, CCT estimation | OpenCV, custom | Heuristic warmth | `cct_range=[2700,6500]` | `{model:0.65, agree:0.25, data:0.1}` | le-0.6.4 |
| `environment.mood` | EnvironmentExtractor | Color harmony, brightness, saturation | NumPy, custom | CLIP mood tags | `mood_categories=8` | `{model:0.5, agree:0.4, data:0.1}` | ee-0.5.8 |
| `environment.time_of_day` | EnvironmentExtractor | Color temperature, brightness analysis | Custom heuristics | CLIP time probe | `warmth_threshold=0.6` | `{model:0.55, agree:0.35, data:0.1}` | ee-0.5.8 |
| `artistic.style` | ArtisticExtractor | Global embedding, style classification | CLIP, custom | BLIP-2 caption tags | `topk=3` | `{model:0.6, agree:0.3, data:0.1}` | ae-0.8.1 |
| `artistic.era` | ArtisticExtractor | Period classification, color palette | CLIP, custom | GPT-4V era probe | `era_categories=10` | `{model:0.55, agree:0.35, data:0.1}` | ae-0.8.1 |
| `accessibility.contrast_ratios` | AccessibilityExtractor | WCAG contrast calculation | Custom WCAG 2.1 | Percentile estimation | `wcag_level=AA` | `{model:0.8, agree:0.15, data:0.05}` | ace-0.3.2 |
| `accessibility.cvd_safe` | AccessibilityExtractor | Color vision deficiency simulation | Custom CVD simulator | Heuristic palette check | `cvd_types=[protanopia,deuteranopia]` | `{model:0.7, agree:0.2, data:0.1}` | ace-0.3.2 |
| `accessibility.motion_sensitivity` | AccessibilityExtractor | Animation detection, motion analysis | OpenCV optical flow | Heuristic motion scoring | `motion_threshold=0.3` | `{model:0.65, agree:0.25, data:0.1}` | ace-0.3.2 |
| `accessibility.touch_targets` | AccessibilityExtractor | Touch target size analysis | Custom heuristics | WCAG 2.1 sizing | `min_size=44px` | `{model:0.75, agree:0.2, data:0.05}` | ace-0.3.2 |

---

### Advanced CV Tokens (Optional)

| Token | Extractor | CV Primitives | Models | Fallbacks | Params | Confidence Weights | Version |
|-------|-----------|---------------|--------|-----------|--------|-------------------|---------|
| `video_animation.motion_type` | VideoAnimationExtractor | Optical flow, motion vectors | RAFT, OpenCV.calcOpticalFlowFarneback | Frame differencing | `flow_threshold=1.0` | `{model:0.7, agree:0.2, data:0.1}` | vae-0.4.5 |
| `semantic_segmentation.regions` | SemanticSegmentationExtractor | Semantic segmentation | SAM, Detectron2 | Watershed segmentation | `iou_threshold=0.5` | `{model:0.75, agree:0.2, data:0.05}` | sse-0.6.1 |
| `component_recognition.types` | ComponentRecognitionExtractor | Object detection, classification | YOLOv8, Detectron2 | Template matching | `confidence_threshold=0.6` | `{model:0.7, agree:0.2, data:0.1}` | cre-0.5.7 |
| `depth_map.elevation` | DepthMapExtractor | Monocular depth estimation | MiDaS, DPT | Normal-from-shading | `depth_scale=1.0` | `{model:0.65, agree:0.25, data:0.1}` | dme-0.4.3 |

---

### Analog Whimsy Systems Taxonomy (New/Gap Tokens)

| Token | Extractor | CV Primitives | Models | Fallbacks | Params | Confidence Weights | Version |
|-------|-----------|---------------|--------|-----------|--------|-------------------|---------|
| `composition.logic` | CompositionalLogicExtractor ⚠️ NEW | Hough lines, contours, cluster silhouette, optical flow | OpenCV.HoughLinesP, DBSCAN, RAFT | CLIP "gridness" probe | `grid_threshold=0.6, flow_minlen=25` | `{model:0.55, agree:0.35, data:0.1}` | cle-0.3.2 |
| `conduits.flow` | GradientExtractor (extended) | Ridge detection, steerable filters | OpenCV.Sobel, SciPy | Optical flow probe | `flow_minlen=25, ridge_threshold=0.5` | `{model:0.6, agree:0.3, data:0.1}` | ge-0.9.1 |
| `form_language.geometry` | BorderRadiusExtractor + ShapeCodeExtractor ⚠️ NEW | Curvature histograms, shape classification | OpenCV.curvature, custom | CLIP "roundedness" | `radius_bins=8, shape_categories=6` | `{model:0.65, agree:0.25, data:0.1}` | bre-0.5.4 |
| `interaction_model.primary_metaphor` | InteractionModelExtractor ⚠️ NEW | Component type voting, control detection | YOLOv8 (knob/slider/switch), custom | GPT-4V caption probe | `vote_threshold=0.6` | `{model:0.6, agree:0.3, data:0.1}` | ime-0.1.0 |
| `interaction_model.redundancy_score` | InteractionModelExtractor ⚠️ NEW | Control density, overlap analysis | Custom heuristics | Heuristic calculation | `density_threshold=0.3` | `{model:0.5, agree:0.4, data:0.1}` | ime-0.1.0 |
| `spatial_hierarchy.depth` | ZIndexExtractor (extended) | Cast shadow analysis, normal-from-shading | OpenCV, MiDaS | Heuristic depth ordering | `shadow_threshold=30, depth_bins=5` | `{model:0.6, agree:0.3, data:0.1}` | zie-0.4.0 |
| `stylistic_lineage.primary` | ArtisticExtractor (extended) | Global CLIP embedding | CLIP | BLIP-2 → LLM | `topk=3, embedding_model=CLIP-ViT-L/14` | `{model:0.6, agree:0.3, data:0.1}` | ae-0.8.1 |
| `stylistic_lineage.secondary` | ArtisticExtractor (extended) | Global CLIP embedding | CLIP | GPT-4V style probe | `topk=3` | `{model:0.55, agree:0.35, data:0.1}` | ae-0.8.1 |
| `design_principles.primary` | DesignLanguageSynthesizer ⚠️ NEW | LLM post-processor on structured tokens | GPT-4, Claude | Heuristic ruleset | `prompt_version=3, temperature=0.3` | `heuristic` | dls-0.1.0 |
| `narrative_archetype.primary` | NarrativeExtractor ⚠️ NEW | Caption → LLM with constrained schema | BLIP-2 → LLM (GPT-4/Claude) | Template-based | `prompt_v=3, schema_version=1` | `heuristic` | ne-0.2.0 |
| `narrative_archetype.emotional_register` | NarrativeExtractor ⚠️ NEW | Sentiment analysis on caption | BLIP-2 → sentiment classifier | Heuristic keywords | `sentiment_model=distilbert` | `{model:0.5, agree:0.4, data:0.1}` | ne-0.2.0 |

**Legend**:
- ⚠️ NEW: Extractor not yet implemented (gap to fill)
- Extended: Uses existing extractor with extended functionality

---

## Confidence Scoring Formula

For each token, confidence is calculated as:

```python
confidence = (
    w_model * model_confidence +
    w_agree * inter_extractor_agreement +
    w_data * data_quality
) - penalties

# Where:
# - model_confidence: Primary model's reported confidence (0-1)
# - inter_extractor_agreement: When multiple extractors run, their agreement (0-1)
# - data_quality: Image quality metrics (resolution, exposure, blur) (0-1)
# - penalties: Deductions for known failure modes (low_resolution, overexposure, etc.)
```

### Penalty Categories

| Penalty | Deduction | Trigger |
|---------|-----------|---------|
| `low_resolution` | 0.15 | Image < 512x512 px |
| `overexposure` | 0.10 | >5% pixels at 255 brightness |
| `underexposure` | 0.10 | >5% pixels at 0 brightness |
| `high_blur` | 0.15 | Laplacian variance < 100 |
| `extreme_aspect_ratio` | 0.05 | Aspect ratio > 3:1 or < 1:3 |

---

## Fallback Strategy

When primary extractor fails (error, low confidence <0.4, timeout), the system tries fallbacks in order:

1. **Fallback Extractor**: Listed in routing table (e.g., CLIP probe instead of CV)
2. **Heuristic**: Hard-coded reasonable defaults based on statistical priors
3. **Empty Result**: Return `null` with reason `"all_strategies_failed"`

Example:
```python
try:
    return CompositionalLogicExtractor.run(image, grid_threshold=0.6)
except ExtractorError:
    try:
        return CLIP.probe(image, "Is this a grid layout?")  # Fallback 1
    except:
        return heuristic_grid_score(image)  # Fallback 2
```

---

## Versioning & Reproducibility

### Version Lock

Every extraction run generates a version lock:

```json
{
  "mapping_sha": "a3f5b2c...",     // SHA256 of this routing table
  "code_sha": "d8e1f9a...",         // Git commit SHA of extractor code
  "models": {
    "OpenCV": "4.9.0",
    "CLIP": "openai/clip-vit-large-patch14",
    "SAM": "facebook/sam-vit-huge"
  }
}
```

### Cache Keys

Cache keys are deterministic hashes:

```python
cache_key = sha256(
    token_name +
    extractor_version +
    json.dumps(params, sort_keys=True) +
    image_sha256
)
```

---

## Coverage & CI

### Coverage Metric

```python
coverage = tokens_extractable_with_one_path / total_taxonomy_tokens
```

**Current Coverage** (based on routing table):
- Foundation tokens: 12/12 (100%)
- Component tokens: 14/14 (100%)
- Visual Style tokens: 12/12 (100%)
- Advanced CV tokens: 4/4 (100%)
- Analog Whimsy Systems tokens: 6/11 (55%) ⚠️ **Gaps**

**Total Coverage**: 48/53 (91%)

### CI Lint Rules

1. **Unmapped Token Failure**: Fail CI if any taxonomy token lacks a routing row
2. **Missing Fallback Warning**: Warn if critical token has no fallback strategy
3. **Version Mismatch Error**: Fail if extractor version in code doesn't match routing table
4. **Model Availability Check**: Warn if required model (SAM, CLIP) is not available in environment

---

## Example Application: Analog Whimsy Systems Image

**Image**: Pink/white bulbous control panel with integrated knobs, meters, and indicators

### Requested Tokens

```json
{
  "tokens": [
    "composition.logic",
    "conduits.flow",
    "component_families.primary_panels",
    "form_language.geometry",
    "color_system.palette_description",
    "material.texture",
    "interaction_model.primary_metaphor",
    "spatial_hierarchy.depth",
    "stylistic_lineage.*",
    "narrative_archetype.primary"
  ]
}
```

### Extraction Results

| Token | Value | Confidence | Features | Timing |
|-------|-------|------------|----------|--------|
| `composition.logic` | "grid-less modular" | 0.83 | grid_score=0.22, cluster_silhouette=0.71 | 187ms |
| `conduits.flow` | "vertical stacking with lateral conduits" | 0.76 | flow_direction=vertical, ridge_density=0.42 | 203ms |
| `component_families.primary_panels` | ["rounded_inset", "bulbous_housings"] | 0.88 | panel_count=3, avg_area=1250px² | 512ms |
| `form_language.geometry` | "soft industrial; rounded rectangles + bulbous" | 0.81 | curvature_hist=[0.05,0.2,0.4,0.25,0.1] | 156ms |
| `color_system.palette_description` | "low-chroma pastel whites/pinks with warm accents" | 0.92 | palette=[#F5E5E5, #FFE4E8, #E8D5D0, #D4A574] | 124ms |
| `material.texture` | "gloss enamel" | 0.87 | specular_strength=0.78, roughness=0.15 | 198ms |
| `interaction_model.primary_metaphor` | "analog (knobs/sliders/switches)" | 0.79 | knob_count=7, slider_count=2, switch_count=1 | 387ms |
| `spatial_hierarchy.depth` | "layered; shallow inset + protruding pods" | 0.74 | depth_bins=[0.1, 0.3, 0.5], shadow_angle=45° | 234ms |
| `stylistic_lineage.primary` | "retro-futurism" | 0.85 | CLIP_similarity=0.85 | 512ms |
| `stylistic_lineage.secondary` | "mid-century appliance" | 0.78 | CLIP_similarity=0.78 | 512ms |
| `stylistic_lineage.tertiary` | "soft skeuomorphism" | 0.72 | CLIP_similarity=0.72 | 512ms |
| `narrative_archetype.primary` | "laboratory ecosystem" | 0.68 | LLM_confidence=0.68 | 1834ms |

### Run Report

```json
{
  "image_id": "7A03623D-ED31-4AAF-A2EB-6EF0FA2357AC",
  "tokens_requested": 10,
  "tokens_filled": 10,
  "coverage": 1.0,
  "avg_confidence": 0.794,
  "total_time_ms": 4359,
  "cache_hits": 0,
  "fallbacks_used": 1,
  "version_lock": {
    "mapping_sha": "a3f5b2c1d8e9f0a1b2c3d4e5f6a7b8c9",
    "code_sha": "d8e1f9a2b3c4d5e6f7a8b9c0d1e2f3a4",
    "models": {
      "OpenCV": "4.9.0",
      "CLIP": "openai/clip-vit-large-patch14",
      "SAM": "facebook/sam-vit-huge",
      "BLIP-2": "Salesforce/blip2-opt-2.7b"
    }
  }
}
```

---

## Gaps to Fill (Immediate)

### Priority 1: New Extractors (5)

1. **CompositionalLogicExtractor**
   - Dependencies: OpenCV (Hough, contours), DBSCAN, RAFT
   - Tokens: `composition.logic`
   - Estimated effort: 3-4 days

2. **ShapeCodeExtractor**
   - Dependencies: OpenCV (curvature), custom shape classifier
   - Tokens: `form_language.geometry`
   - Estimated effort: 2-3 days

3. **InteractionModelExtractor**
   - Dependencies: YOLOv8 (custom head for controls), vote aggregator
   - Tokens: `interaction_model.*`
   - Estimated effort: 4-5 days

4. **DesignLanguageSynthesizer**
   - Dependencies: GPT-4/Claude, structured token aggregator
   - Tokens: `design_principles.*`
   - Estimated effort: 2-3 days

5. **NarrativeExtractor**
   - Dependencies: BLIP-2, LLM (GPT-4/Claude), sentiment classifier
   - Tokens: `narrative_archetype.*`
   - Estimated effort: 3-4 days

### Priority 2: Extend Existing Extractors (3)

1. **GradientExtractor** → Add ridge detection for `conduits.flow`
2. **ZIndexExtractor** → Add depth binning for `spatial_hierarchy.depth`
3. **ArtisticExtractor** → Add secondary/tertiary style detection for `stylistic_lineage.*`

---

## Implementation Roadmap

### Phase 1: Routing Infrastructure (1 week)

1. **Routing Table Parser** (1 day)
   - Parse this markdown file into structured data
   - Validate schema consistency
   - Generate cache keys

2. **Token Planner** (2 days)
   - Resolve tokens to extractors
   - Build DAG (topological sort for dependencies)
   - Handle wildcards (`stylistic_lineage.*`)

3. **Executor Engine** (2 days)
   - Run extractors in parallel where possible
   - Handle fallback strategies
   - Generate RunReport

4. **Confidence Calculator** (1 day)
   - Implement weighted formula
   - Apply penalties
   - Inter-extractor agreement

5. **CI Integration** (1 day)
   - Lint rules for unmapped tokens
   - Version mismatch checks
   - Coverage reporting

### Phase 2: Fill Gaps (3-4 weeks)

Implement 5 new extractors (Priority 1) sequentially

### Phase 3: Golden Standard (1 week)

1. Create 12 gold-standard images
2. Compute coverage and calibration curves
3. Tune confidence weights and thresholds
4. Generate HTML operator's manual from routing table

---

## Related Documentation

- [Complete Extractor Inventory](../../../COMPLETE_EXTRACTOR_INVENTORY.md) - Full extractor file list
- [Token Ontology Reference](TOKEN_ONTOLOGY_REFERENCE.md) - Analog Whimsy Systems taxonomy
- [Component Inheritance Patterns](COMPONENT_INHERITANCE_PATTERNS.md) - Component architecture
- [Complete Token-Extractor Mapping](COMPLETE_TOKEN_EXTRACTOR_MAPPING.md) - Technical CV/AI details

---

**Last Updated**: 2025-11-11
**Version**: 1.0.0
**Schema**: routing-table-v1
**Maintainers**: Design Token Team

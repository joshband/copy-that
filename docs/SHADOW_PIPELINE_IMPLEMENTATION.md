# Shadow Extraction Pipeline Implementation

**Status:** ✅ Complete - Tasks 1-7 Implemented
**Version:** 1.0.0
**Date:** 2025-12-06

---

## Overview

This document describes the complete implementation of the **8-stage shadow extraction pipeline** for Midjourney-style AI-generated images. The system converts a single image into structured shadow tokens and visualization layers.

**Implementation aligns with:** `SHADOW_PIPELINE_SPEC.md` (source of truth)

---

## Architecture

### Module Structure

```
src/copy_that/shadowlab/
├── pipeline.py          # Core data structures + Tasks 1-6 functions
├── stages.py            # Stage 01-08 implementations (Task 7)
├── orchestrator.py      # Pipeline orchestration (Task 7)
└── __init__.py          # Public API exports
```

### Key Classes

#### 1. **ShadowPipeline** (orchestration container)
```python
pipeline = ShadowPipeline(output_dir=Path('/tmp/shadows'))
pipeline.register_stage(stage_result, visual_layers)
pipeline.save_results('output.json')
```

#### 2. **ShadowStageResult** (per-stage structured output)
```python
@dataclass
class ShadowStageResult:
    id: str                          # 'shadow_stage_01_input'
    name: str                        # 'Input & Preprocessing'
    description: str
    inputs: List[str]               # ['image_path']
    outputs: List[str]              # ['rgb_image']
    metrics: Dict[str, float]       # {'width': 1024.0, ...}
    artifacts: Dict[str, str]       # {'rgb_image': 'Original RGB image'}
    visual_layers: List[str]        # IDs of visualization layers
    stage_narrative: str            # Semi-technical explanation
    duration_ms: float
```

#### 3. **ShadowVisualLayer** (visualization metadata)
```python
@dataclass
class ShadowVisualLayer:
    id: str                         # 'shadow_viz_01_original'
    stage_id: str                   # References ShadowStageResult.id
    type: VisualLayerType           # 'rgb', 'heatmap', 'depth', etc.
    source_artifact: str            # 'rgb_image'
    render_params: RenderParams     # colormap, opacity, blend_mode
    ui: UIConfig                    # title, subtitle, visibility
```

#### 4. **ShadowTokenSet** (final consolidated result)
```python
@dataclass
class ShadowTokenSet:
    image_id: str
    shadow_tokens: ShadowTokens

@dataclass
class ShadowTokens:
    coverage: float                 # Fraction in shadow [0-1]
    mean_strength: float            # Average shadow opacity [0-1]
    edge_softness_mean: float       # Penumbra width (pixels)
    edge_softness_std: float        # Variation
    key_light_direction: LightDirection  # {azimuth_deg, elevation_deg}
    key_light_softness: float       # 0-1, how soft is main light
    physics_consistency: float      # 0-1, plausibility score
    style_label: Optional[str]      # 'cinematic', 'studio', etc. (Phase 6 future)
    shadow_cluster_stats: List[ShadowClusterStats]
```

---

## Task Implementation Summary

### ✅ Task 1: Image I/O & Illumination-Invariant Map

**Functions:**
```python
load_rgb(path: str) -> np.ndarray
```
- Loads image via OpenCV
- Converts BGR → RGB
- Normalizes to float32 [0, 1]

```python
illumination_invariant_v(rgb: np.ndarray) -> np.ndarray
```
- Extracts HSV V-channel (brightness)
- Applies contrast stretching
- Returns grayscale illumination map

**Dependencies:** OpenCV, NumPy

---

### ✅ Task 2: Classical Shadow Candidates

**Function:**
```python
classical_shadow_candidates(
    v: np.ndarray,
    threshold_percentile: float = 20.0,
    min_area: int = 10
) -> np.ndarray
```

**Algorithm:**
1. Adaptive thresholding (compare to local mean)
2. Binary erosion/closing for cleanup
3. Connected component labeling (scipy.ndimage)
4. Remove components < min_area
5. Distance transform for soft mask

**Dependencies:** OpenCV, NumPy, SciPy

---

### ✅ Task 3: ML Shadow Model

**Function:**
```python
run_shadow_model(rgb: np.ndarray, high_quality: bool = True) -> np.ndarray
run_shadow_model_with_sam(rgb: np.ndarray) -> np.ndarray
```

**Status:** ✅ Fully Implemented with SAM + BDRAR-style Detection

**Three-tier approach:**
1. **SAM boundary refinement** (`facebook/sam-vit-base`) - Crisp edges via point prompts
2. **BDRAR-style feature pyramid** - Multi-scale LAB color analysis
3. **Enhanced classical fallback** - When models unavailable

**Implementation Details:**
```python
# High-quality mode (default): SAM + BDRAR-style
run_shadow_model(rgb, high_quality=True)  # Uses SAM boundaries

# Fast mode: Enhanced classical only
run_shadow_model(rgb, high_quality=False)

# BDRAR-inspired feature pyramid:
# 1. Multi-scale LAB analysis at [1.0, 0.5, 0.25] scales
# 2. Darkness, chroma attenuation, blue-shift, local contrast
# 3. Recurrent attention refinement (2 iterations)
# 4. SAM boundary refinement using shadow centroids as prompts
```

**Helper Functions:**
- `_get_shadow_model()` - Cached SegFormer loader
- `_get_sam_model()` - Cached SAM loader (facebook/sam-vit-base)
- `_multi_scale_shadow_features()` - BDRAR-style FPN extraction
- `_recurrent_attention_refinement()` - Edge-aware iterative refinement
- `_refine_shadow_boundaries_sam()` - Point-prompted SAM refinement
- `_enhanced_classical_shadow()` - Multi-cue fallback

---

### ✅ Task 4: Depth & Intrinsic Decomposition

**Functions:**
```python
run_midas_depth(rgb: np.ndarray) -> np.ndarray
```
**Status:** ✅ Fully Implemented
- Loads MiDaS v3 from PyTorch Hub (`intel-isl/MiDaS`)
- Model caching for efficiency (loads once, ~9s first call, <100ms after)
- Graceful fallback using gradient-based depth estimation
- Device detection: CUDA → MPS → CPU

```python
run_intrinsic(rgb: np.ndarray) -> Tuple[np.ndarray, np.ndarray]
```
**Status:** ✅ Fully Implemented with Multi-Scale Retinex
- Based on Land's Retinex theory: Image = Reflectance × Shading
- Multi-scale processing at scales [15, 80, 250] pixels
- Log-domain filtering for illumination estimation
- Color constancy correction (Gray World assumption)
- Bilateral filtering for edge-aware shading refinement

**Helper Functions:**
- `_get_midas_model()` - Cached MiDaS loader with fallback
- `_fallback_depth_estimation()` - Gradient-based depth when model unavailable
- `_multi_scale_retinex()` - Core MSR algorithm
- `_estimate_shading_from_reflectance()` - Shading map derivation
- `_color_constancy_correction()` - White balance correction

---

### ✅ Task 5: Depth-to-Normals & Light Estimation

**Functions:**
```python
depth_to_normals(depth: np.ndarray) -> Tuple[np.ndarray, np.ndarray]
```
- Computes gradients (Sobel)
- Builds normals: (-∂z/∂x, -∂z/∂y, 1)
- Normalizes to unit vectors
- Returns RGB visualization

```python
fit_directional_light(normals: np.ndarray, shading: np.ndarray) -> np.ndarray
```
- Least-squares: minimize ||N·L - shading||²
- Solves: L = (N^T N)^{-1} N^T S
- Returns unit light direction vector

```python
light_dir_to_angles(L: np.ndarray) -> Tuple[float, float]
```
- Converts 3D vector to spherical coordinates
- Returns: (azimuth_deg, elevation_deg)
- azimuth: 0-360° (0=+X, 90=+Y)
- elevation: -90-90° (0=horizon, 90=zenith)

**Dependencies:** NumPy

---

### ✅ Task 6: Shadow Fusion & Token Computation

**Functions:**
```python
fuse_shadow_masks(
    classical: np.ndarray,
    ml_mask: np.ndarray,
    shading: np.ndarray,
    classical_weight: float = 0.3,
    ml_weight: float = 0.5,
    shading_weight: float = 0.2
) -> np.ndarray
```
- Weighted average of three signals
- classical: heuristic mask
- ml_mask: neural prediction
- shading: 1 - illumination
- Returns fused mask [0, 1]

```python
compute_shadow_strength(
    shading: np.ndarray,
    fused_mask: np.ndarray
) -> float
```
- Computes: shadow_strength = 1 - shading
- Averages over masked regions
- Returns: scalar [0, 1]

```python
compute_shadow_tokens(
    fused_mask: np.ndarray,
    shading: np.ndarray,
    light_direction: np.ndarray,
    physics_consistency: float = 0.8
) -> ShadowTokens
```
- Computes all metrics:
  - coverage (mean of fused_mask)
  - mean_strength
  - edge_softness (gradient analysis)
  - light direction angles
  - light softness (from penumbra width)
- Returns: ShadowTokens dataclass

**Dependencies:** NumPy, SciPy, OpenCV

---

### ✅ Task 7: Stage Implementations

**8 Stages (01-08):**

Each stage function returns: `(ShadowStageResult, List[ShadowVisualLayer], Dict[str, np.ndarray])`

#### Stage 01: Input & Preprocessing
- Loads image, resizes if needed
- Visual: original RGB

#### Stage 02: Illumination-Invariant View
- Computes HSV V-channel
- Visual: grayscale illumination map

#### Stage 03: Classical Shadow Candidates
- Applies `classical_shadow_candidates()`
- Visual: heatmap overlay

#### Stage 04: ML Shadow Mask
- Calls `run_shadow_model()`
- Visual: heatmap with contours

#### Stage 05: Intrinsic Decomposition
- Calls `run_intrinsic()`
- Visuals: reflectance, shading maps

#### Stage 06: Depth & Normals
- Calls `run_midas_depth()`, `depth_to_normals()`
- Visuals: depth (viridis), normals (RGB)

#### Stage 07: Lighting Fit
- Calls `fit_directional_light()`
- Computes consistency error
- Visual: error heatmap

#### Stage 08: Fusion & Tokens
- Fuses masks, computes tokens
- Visuals: final mask, overlay

---

### ✅ Task 7b: Orchestration

**ShadowPipelineOrchestrator:**

```python
orchestrator = ShadowPipelineOrchestrator(
    image_path='path/to/image.jpg',
    output_dir=Path('/tmp/shadows'),
    target_size=(512, 512),  # Optional resize
    verbose=True
)

results = orchestrator.run()
```

**Output Structure:**
```python
{
    'pipeline_results': {
        'stages': [ShadowStageResult...],
        'visual_layers': [ShadowVisualLayer...],
        'artifacts_list': [names...],
        'total_duration_ms': float
    },
    'shadow_token_set': {
        'image_id': str,
        'timestamp': str,
        'shadow_tokens': {...}
    },
    'execution_log': [...],
    'total_duration_ms': float,
    'artifacts_paths': {
        'rgb_image': '/tmp/shadows/artifacts/rgb_image.png',
        'final_shadow_mask': '/tmp/shadows/artifacts/final_shadow_mask.png',
        'shadow_tokens': '/tmp/shadows/shadow_tokens.json',
        ...
    },
    'output_dir': str
}
```

**Artifact Saving:**
- PNG files: all images (grayscale, RGB, heatmaps)
- JSON files: pipeline results, shadow tokens
- Auto-creates `artifacts/` subdirectory

---

## API Usage

### Quick Start

```python
from copy_that.shadowlab import run_shadow_pipeline
from pathlib import Path

# Run complete pipeline
results = run_shadow_pipeline(
    image_path='image.jpg',
    output_dir=Path('/tmp/shadows'),
    verbose=True
)

# Access token results
tokens = results['shadow_token_set']['shadow_tokens']
print(f"Coverage: {tokens['coverage']:.1%}")
print(f"Mean strength: {tokens['mean_strength']:.1%}")
print(f"Light direction: {tokens['key_light_direction']}")
```

### Manual Orchestration

```python
from copy_that.shadowlab import ShadowPipelineOrchestrator

orchestrator = ShadowPipelineOrchestrator(
    image_path='image.jpg',
    output_dir=Path('/tmp/shadows')
)

results = orchestrator.run()
print(orchestrator.get_summary())  # Human-readable summary
```

### Individual Stage Access

```python
from copy_that.shadowlab import (
    load_rgb,
    illumination_invariant_v,
    classical_shadow_candidates,
    stage_01_input,
    stage_02_illumination,
    # ... etc
)

# Load image
rgb = load_rgb('image.jpg')

# Compute illumination
illum_map = illumination_invariant_v(rgb)

# Get classical candidates
candidates = classical_shadow_candidates(illum_map)

# Or run full stage
stage_result, visual_layers, artifacts = stage_01_input('image.jpg')
```

---

## Data Export Formats

### JSON: Pipeline Results

```json
{
  "stages": [
    {
      "id": "shadow_stage_01_input",
      "name": "Input & Preprocessing",
      "metrics": {"width": 1024, "height": 768, "channels": 3},
      "duration_ms": 12.5,
      "visual_layers": ["shadow_viz_01_original"]
    }
    // ... 8 stages total
  ],
  "visual_layers": [
    {
      "id": "shadow_viz_01_original",
      "stage_id": "shadow_stage_01_input",
      "type": "rgb",
      "source_artifact": "rgb_image",
      "render_params": {
        "colormap": null,
        "opacity": 1.0,
        "blend_mode": "normal"
      },
      "ui": {
        "title": "Original Image",
        "default_visible": true
      }
    }
    // ... multiple layers per stage
  ],
  "total_duration_ms": 450.0
}
```

### JSON: Shadow Tokens

```json
{
  "image_id": "my_image",
  "timestamp": "2025-12-06T10:30:00.000Z",
  "shadow_tokens": {
    "coverage": 0.25,
    "mean_strength": 0.72,
    "edge_softness_mean": 3.5,
    "edge_softness_std": 1.2,
    "key_light_direction": {
      "azimuth_deg": 245.0,
      "elevation_deg": 38.5
    },
    "key_light_softness": 0.35,
    "physics_consistency": 0.82,
    "style_label": null,
    "style_embedding": null,
    "shadow_cluster_stats": []
  }
}
```

### PNG Artifacts

Saved in `artifacts/` subdirectory:
- `rgb_image.png` — Original image
- `illumination_map.png` — V-channel brightness
- `candidate_mask.png` — Classical detection
- `ml_shadow_mask.png` — Neural prediction
- `reflectance_map.png` — Material colors
- `shading_map.png` — Illumination
- `depth_map.png` — Depth estimate
- `normal_map_rgb.png` — Surface normals
- `final_shadow_mask.png` — Fused result
- `shadow_overlay.png` — Mask on original

---

## Integration Points

### With Existing Token System

The `ShadowTokenSet` is designed to integrate with your existing token graph:

```python
from copy_that.shadowlab import ShadowTokens
from your_app.tokens import TokenGraphStore

# Extract tokens from pipeline
shadow_tokens = results['shadow_token_set']['shadow_tokens']

# Add to graph
graph.add_shadow_tokens(
    coverage=shadow_tokens['coverage'],
    strength=shadow_tokens['mean_strength'],
    light_direction=shadow_tokens['key_light_direction'],
    # ... etc
)
```

### With Frontend Visualization

The visual layers are designed for React rendering:

```typescript
// Sample React component
interface ShadowVisualizationProps {
  visualLayers: ShadowVisualLayer[]
  artifacts: Record<string, string>
}

export function ShadowVisualization({ visualLayers, artifacts }: Props) {
  return (
    <div className="shadow-grid">
      {visualLayers.map(layer => (
        <ShadowLayerTile
          key={layer.id}
          layer={layer}
          imageSource={artifacts[layer.source_artifact]}
          renderParams={layer.render_params}
          uiConfig={layer.ui}
        />
      ))}
    </div>
  )
}
```

---

## Future Enhancements

### ✅ Phase 2: Model Integration (COMPLETE)

1. **ML Shadow Detector** ✅
   - SegFormer model from HuggingFace
   - Enhanced classical fallback with multi-cue analysis
   - Model caching for efficiency

2. **Intrinsic Decomposition** ✅
   - Multi-Scale Retinex (MSR) algorithm
   - Color constancy correction
   - Edge-aware bilateral filtering

3. **MiDaS Depth** ✅
   - Official PyTorch Hub integration
   - Gradient-based fallback
   - Automatic device detection

### Phase 3+: Future Improvements

4. **Style Classification** (Phase 6)
   - CLIP embeddings for shadow aesthetics
   - LLaVA-NeXT for detailed descriptions

5. **Dedicated Shadow Detection Models**
   - Fine-tune on shadow-specific datasets (SBU, ISTD)
   - DSDNet, BDRAR, or MTMT architectures

### Optimization Opportunities

1. **GPU Acceleration**
   - CUDA kernels for depth/normals
   - TensorRT for model inference

2. **Batch Processing**
   - Process multiple images efficiently
   - Parallel stage execution where possible

3. **Caching**
   - Cache model weights
   - Skip re-computation for identical inputs

---

## Testing

### Unit Tests

```bash
# Test core functions
python -m pytest tests/unit/shadowlab/test_pipeline.py -v

# Test stages
python -m pytest tests/unit/shadowlab/test_stages.py -v

# Test orchestration
python -m pytest tests/unit/shadowlab/test_orchestrator.py -v
```

### Integration Test

```bash
# End-to-end pipeline test
python -m pytest tests/integration/test_shadow_pipeline.py -v
```

### Manual Testing

```python
from copy_that.shadowlab import run_shadow_pipeline
from pathlib import Path

results = run_shadow_pipeline(
    'test_image.jpg',
    output_dir=Path('/tmp/test_shadows'),
    verbose=True
)

# Check outputs exist
assert Path('/tmp/test_shadows/shadow_tokens.json').exists()
assert Path('/tmp/test_shadows/artifacts/final_shadow_mask.png').exists()
assert results['shadow_token_set']['shadow_tokens']['coverage'] >= 0
```

---

## Performance

### Typical Timings (256x256 image on CPU)

```
Stage 01: 12 ms    (image load)
Stage 02: 25 ms    (illumination invariant)
Stage 03: 45 ms    (classical detection)
Stage 04: 3500 ms  (ML shadow - first call with model load)
        : 100 ms   (ML shadow - cached, fallback mode)
Stage 05: 50 ms    (intrinsic decomposition - MSR)
Stage 06: 9000 ms  (MiDaS depth - first call with model load)
        : 200 ms   (MiDaS depth - cached model)
        : 50 ms    (depth fallback mode)
Stage 07: 35 ms    (lighting fit)
Stage 08: 40 ms    (fusion + tokens)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total (first run): ~13s (model downloads)
Total (cached):    ~500ms (with fallbacks)
Total (with GPU):  ~300ms (full models)
```

### Model Caching

All ML models use global caching - loaded once per session:
- MiDaS: ~9s first load, <100ms inference after
- SegFormer: ~3s first load, <50ms inference after
- Models persist across pipeline runs

### Memory Usage

- RGB image (1024×768): ~6 MB
- Intermediate maps: ~30 MB
- Total per-image: ~40-50 MB

---

## References

- **Spec:** `docs/SHADOW_PIPELINE_SPEC.md`
- **Roadmap:** `docs/planning/SHADOW_EXTRACTION_ROADMAP.md`
- **Modules:** `src/copy_that/shadowlab/`

---

## Next Steps

### ✅ Completed

1. **ML Shadow Detection** (Phase 2) — SegFormer + enhanced fallback
2. **Intrinsic Decomposition** (Phase 2) — Multi-Scale Retinex
3. **Depth Estimation** (Phase 2) — MiDaS v3 integration

### Remaining Work

4. **Add evaluation harness** (Phase 3)
   - Reference dataset with ground truth
   - Metrics: IoU, F1, MAE, RMSE

5. **Dedicated shadow models** (Phase 4)
   - Fine-tune on SBU/ISTD datasets
   - DSDNet, BDRAR, or MTMT architectures

6. **Implement style classification** (Phase 6)
   - CLIP embeddings
   - LLM descriptions

7. **Frontend visualization**
   - React components for process view
   - Detail views with interactivity
   - Token panel with metrics

---

**End of Implementation Document**

Last Updated: 2025-12-06 — Phase 2 complete (ML models, MSR intrinsic, MiDaS depth)



---

# **SHADOW_PIPELINE_SPEC.md**

### *Shadow Extraction Pipeline, Visualization Architecture, and Narrative Specification*

---

## **0. Purpose**

This document defines a full shadow-extraction system designed for **Midjourney-style AI-generated images**, including:

* A multi-stage **algorithmic pipeline**
* A consistent **visualization architecture**
* A clear, semi-technical **narrative** for each stage
* Formal **data schemas** for interoperability
* Recommended **libraries, models, and open-source tools**
* Hooks for a future **dataset + evaluation harness**

This spec is the *source of truth* for both backend implementation and UI/visualization surfaces.

---

# **1. Pipeline Overview**

The system processes a single RGB image into:

* Intermediate structured artifacts
* Visualization-ready layers
* A consolidated **ShadowTokenSet** suitable for downstream systems (design token extraction, style analysis, relighting agents, etc.)

Processing is divided into eight deterministic stages:

1. **Input & Preprocessing**
2. **Illumination-Invariant View**
3. **Classical Shadow Candidates**
4. **ML Shadow Mask**
5. **Intrinsic Image Decomposition**
6. **Depth & Surface Normals**
7. **Lighting Fit & Consistency**
8. **Fusion & Token Generation**

Each stage produces a `ShadowStageResult`.

---

# **2. Pipeline Stages: Technical, Visual, Narrative**

Each stage definition includes:

* **Algorithms / Tools**
* **Artifact Outputs**
* **Visualization Layer(s)**
* **Narrative (semi-technical)**

These map directly into the UI’s Process View and Detail View.

---

## **Stage 1 — Input & Preprocessing**

**ID:** `shadow_stage_01_input`

### **Goal**

Standardize the input image and prepare auxiliary signals.

### **Algorithms / Tools**

* `opencv-python` for loading, resizing, colorspace normalization
* Optional segmentation: `segment-anything`, DeepLabV3+, or Mask2Former

### **Artifacts**

* `rgb_image` — normalized float32 RGB
* `segmentation_mask` (optional)

### **Visualization**

Tile 1: "Original + Segments"

* Original image
* Toggleable segmentation overlay

### **Narrative**

We begin by normalizing the image—resizing it, converting its color representation, and optionally segmenting the scene into broad regions. This gives us a clean, structured starting point before we analyze illumination or shadows.

---

## **Stage 2 — Illumination-Invariant View**

**ID:** `shadow_stage_02_invariant`

### **Goal**

Emphasize brightness variation while reducing color distraction.

### **Algorithms / Tools**

* Convert RGB → HSV/Log-chromaticity (`cv2.cvtColor`)
* Contrast stretching

### **Artifacts**

* `illumination_map` — grayscale brightness emphasis

### **Visualization**

Tile 2: "Illumination View"

* Grayscale image showing lighting structure

### **Narrative**

To reason about shadows, we isolate illumination from color. This illumination-oriented view makes bright and dark regions far easier for both AI and humans to compare.

---

## **Stage 3 — Classical Shadow Candidates**

**ID:** `shadow_stage_03_candidates`

### **Goal**

Generate a fast heuristic estimate of potential shadow regions.

### **Algorithms / Tools**

* Adaptive thresholding
* Local contrast tests
* Morphological open/close for cleanup (`cv2.morphologyEx`)

### **Artifacts**

* `candidate_mask` — soft or binary mask in [0,1]

### **Visualization**

Tile 3: "Classical Candidates"

* Red overlay on original image
* Toggle to heatmap-only mode

### **Narrative**

Before using heavier neural models, we allow classical algorithms to make the first guess. These fast heuristics highlight unusually dark regions that could plausibly be shadows.

---

## **Stage 4 — ML Shadow Mask**

**ID:** `shadow_stage_04_ml_mask`

### **Goal**

Predict a refined shadow probability map using a trained model.

### **Algorithms / Tools**

Recommended open-source shadow detectors:

* **BDRAR**
* **DHAN**
* **DSDNet**
* **Mask-ShadowGAN** derivatives
  (all available on GitHub; see References)

Frameworks:

* PyTorch (`torch`)
* torchvision transforms

### **Artifacts**

* `ml_shadow_mask` — probability map [0,1]

### **Visualization**

Tile 4: "AI Shadow Mask"

* Heatmap, contour overlays (p=0.5, 0.75)

### **Narrative**

A trained shadow-detection model identifies patterns too nuanced for classical methods—soft penumbras, textured surfaces, stylized shading, and more. This yields a probability map representing how likely each pixel is to be in shadow.

---

## **Stage 5 — Intrinsic Image Decomposition**

**ID:** `shadow_stage_05_intrinsic`

### **Goal**

Split the image into reflectance and shading components.

### **Algorithms / Tools**

Open-source intrinsic models:

* **CGIntrinsics**
* **IntrinsicNet**
* **IIW-based models**
* **Colorful Diffuse Intrinsics**
  (links in References)

### **Artifacts**

* `reflectance_map`
* `shading_map`

### **Visualization**

Tile 5: Reflectance ("Shadow-Free Colors")
Tile 6: Shading ("Illumination Structure")

### **Narrative**

Intrinsic decomposition attempts to separate *what the surfaces are made of* from *how light hits them*. Shadows appear clearly in the shading map, while reflectance shows a cleaned, lighting-neutral view of the scene.

---

## **Stage 6 — Depth & Surface Normals**

**ID:** `shadow_stage_06_geometry`

### **Goal**

Infer scene geometry to explain shadow behavior.

### **Algorithms / Tools**

Depth:

* **MiDaS** (DPT-Large, DPT-Hybrid)
  Normals:
* Derived from depth gradients or predicted by a dedicated normal model.

### **Artifacts**

* `depth_map`
* `normal_map`
* `normal_map_rgb`

### **Visualization**

Tile 7: Depth (viridis/jet colormap)
Tile 8: Surface Normals (RGB-coded)

### **Narrative**

Although we have only a 2D image, we can approximate depth and surface tilt. This helps determine whether shadows make geometric sense and where light would realistically fall.

---

## **Stage 7 — Lighting Fit & Consistency**

**ID:** `shadow_stage_07_lighting`

### **Goal**

Estimate dominant light direction and evaluate physical consistency.

### **Algorithms / Tools**

* Least-squares directional lighting fit: minimize `N·L ≈ shading`
* Optional spherical harmonic fit
* Error map to assess consistency

### **Artifacts**

* `light_direction` (vector)
* `light_direction_angles` (azimuth, elevation)
* `lighting_error_map`

### **Visualization**

Tile 9: Lighting Consistency Error
Widget: Light Direction Hemisphere

### **Narrative**

Using the shading field and estimated surface normals, we fit a simple lighting model. This reveals the dominant light direction and highlights areas where the AI-generated image violates physical lighting—common in stylized Midjourney outputs.

---

## **Stage 8 — Fusion & Token Generation**

**ID:** `shadow_stage_08_tokens`

### **Goal**

Produce a final shadow map and structured shadow tokens.

### **Algorithms / Tools**

* Weighted fusion of:

  * Classical mask
  * ML mask
  * Shading-derived shadow likelihood
  * Geometry consistency weights
* Shadow strength calculation
* Penumbra analysis (edge softness)
* Light direction packaging
* Optional VLM style embeddings (CLIP, SigLIP)

### **Artifacts**

* `final_shadow_mask`
* `ShadowTokenSet` document

### **Visualization**

Tile 10: Final Shadow Map
Right Panel: Token Summary

### **Narrative**

All signals—brightness heuristics, neural predictions, shading, geometry, and lighting—are merged into a single coherent result. The final shadow map and shadow tokens summarize coverage, strength, softness, lighting direction, and style.

---

# **3. Data Schemas**

These schemas define interfaces between backend and visualization layers.

---

## **3.1 `ShadowStageResult`**

```ts
type ShadowStageResult = {
  id: string;
  name: string;
  description: string;
  inputs: string[];
  outputs: string[];
  metrics: Record<string, number>;
  artifacts: Record<string, string>;
  visual_layers: string[];
  stage_narrative: string;
};
```

---

## **3.2 `ShadowVisualLayer`**

```ts
type ShadowVisualLayer = {
  id: string;
  stage_id: string;
  type: "rgb" | "grayscale_map" | "heatmap" | "mask_overlay" | "depth" | "normal";
  source_artifact: string;
  render_params: {
    colormap?: string;
    opacity?: number;
    blend_mode?: "normal" | "multiply" | "screen" | "overlay";
    value_range?: [number, number];
  };
  ui: {
    title: string;
    subtitle?: string;
    default_visible: boolean;
  };
};
```

---

## **3.3 `ShadowTokenSet`**

```ts
type ShadowTokenSet = {
  image_id: string;
  shadow_tokens: {
    coverage: number;
    mean_strength: number;
    edge_softness_mean: number;
    edge_softness_std: number;
    key_light_direction: { azimuth_deg: number; elevation_deg: number };
    key_light_softness: number;
    physics_consistency: number;
    style_label?: string;
    style_embedding?: number[];
    shadow_cluster_stats?: Array<{
      cluster_id: number;
      region_label?: string;
      coverage: number;
      mean_strength: number;
    }>;
  };
};
```

---

# **4. Recommended Libraries & Tools**

### **Core CV & Image Processing**

* `opencv-python`
* `numpy`
* `scikit-image`
* `Pillow`

### **Shadow Detection Models (open-source)**

* BDRAR
* DSDNet
* DHAN
* ShadowFormer variants
* Mask-ShadowGAN (for removal + mask refinement)

### **Intrinsic Image Decomposition**

* CGIntrinsics
* IntrinsicNet
* IIW (Intrinsic Images in the Wild) implementations
* Colorful Diffuse Intrinsics

### **Depth / Normals**

* MiDaS (DPT-Hybrid, DPT-Large)
* ZoeDepth (optional)
* NIID-Net / normal-estimation networks

### **Geometry / Lighting**

* PyTorch
* Optional heavy stack: PyTorch3D, NVDiffRast

### **Style Embeddings**

* CLIP
* SigLIP / SigLIP2
* IDEFICS2 (optional)

---

# **5. Minimal Example Functions (Pseudo-Python)**

Each function referenced in tasks:

```python
load_rgb(path) -> np.ndarray
illumination_invariant_v(rgb) -> np.ndarray
classical_shadow_candidates(v) -> np.ndarray
run_shadow_model(rgb) -> np.ndarray
run_intrinsic(rgb) -> (reflectance, shading)
run_midas_depth(rgb) -> depth
depth_to_normals(depth) -> (normals, normals_vis)
fit_directional_light(normals, shading) -> light_dir
light_dir_to_angles(L) -> (azimuth_deg, elevation_deg)
fuse_shadow_masks(classical, ml_mask, shading) -> fused_mask
compute_shadow_strength(shading, fused_mask) -> float
compute_shadow_tokens(fused_mask, shading, light_dir, physics_consistency)
```

Backend implementation details left to pipeline development.

---

# **6. Visualization Architecture**

Three views:

### **Process View**

* Grid of tiles (Stage 01–08)
* Each tile shows a visual layer derived from `ShadowStageResult`
* Clicking opens Detail View

### **Detail View**

* Full-size visualization for that stage
* Panel showing:

  * Algorithms used
  * Metrics
  * Narrative text

### **Token View**

* Display final `ShadowTokenSet`
* Visual glyphs for:

  * Light direction
  * Softness
  * Coverage bars
  * Strength indicators

---

# **7. Narrative Alignment (Concise Flow)**

This text is meant to appear in UI panels or documentation.
Each bullet corresponds to a stage tile.

1. **Input → Structure**
   We standardize the image and identify major regions so later steps reason about consistent inputs.

2. **Illumination View**
   We reinterpret the image to highlight brightness rather than color—preparing the scene for shadow analysis.

3. **Classical Candidates**
   Fast heuristics detect unusually dark zones that might be shadows.

4. **ML Mask**
   A learned shadow detector refines and corrects the initial guesses.

5. **Intrinsic Decomposition**
   We separate material reflectance from shading to isolate how light falls across surfaces.

6. **Depth & Normals**
   A 3D approximation gives geometric context to interpret shadows more physically.

7. **Lighting Fit**
   By fitting a simple light model, we estimate dominant light direction and identify regions where shading breaks physics.

8. **Fusion & Tokens**
   All signals converge into the final shadow map and quantitative shadow tokens for downstream use.

---

# **8. Future: Evaluation Harness & Midjourney Dataset (Placeholder)**

A future `SHADOW_EVAL_SPEC.md` will define:

* **Dataset manifest format**
* **Annotation schema** (optional human masks, light direction labels)
* **Evaluation metrics**

  * IoU / F1 for masks
  * Shadow-strength MAE
  * Edge-softness RMSE
  * Lighting-direction error
* **Evaluation API / CLI**

  * `evaluate_shadow_pipeline --manifest dataset.json --output results.json`

This will attach to the same schemas above.

---

# **9. References (Primary Repos Mentioned)**

Shadow detection:

* DSDNet
* BDRAR
* DHAN
* Mask-ShadowGAN

Intrinsic decomposition:

* CGIntrinsics
* IntrinsicNet
* IIW implementations
* Colorful Diffuse Intrinsics

Depth / normals:

* MiDaS (ISL-ORG)
* ZoeDepth

Lighting:

* PyTorch3D
* NVDiffRast

Style Models:

* CLIP, SigLIP

---

# **End of Spec**

This document should be committed as `SHADOW_PIPELINE_SPEC.md` and referenced by all Claude-Code implementation prompts.

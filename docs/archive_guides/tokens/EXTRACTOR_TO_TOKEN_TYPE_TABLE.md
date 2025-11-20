# Extractor → Token Type Mapping Table

**Quick Reference: Which Extractors Produce Which Token Types**

Version: 3.1
Last Updated: 2025-11-11
Total Extractors: 30+ active (49 files)

---

## Overview

This table shows the **direct mapping** from each extractor to the token types it produces. Use this for:
- Understanding which extractor to use for specific tokens
- Debugging missing tokens
- Performance optimization (skip extractors for unused tokens)
- Architecture understanding

---

## Core CV Extractors (22)

### Function-Based Extractors (6) - Phase 1 Pattern

| # | Extractor | File | Token Types Produced | Category | Method | Performance |
|---|-----------|------|---------------------|----------|--------|-------------|
| 1 | **ColorExtractor** | `color_extractor.py` | `palette`, `primitive`, `semantic_colors`, `brand`, `ui_colors`, `text_colors` | Foundation | K-means clustering (LAB space), HSL interpolation | 1.2s |
| 2 | **TypographyExtractor** | `typography_extractor.py` | `typography`, `typography_extended`, `font_stack` | Foundation | Edge pattern analysis, weight inference | 0.8s |
| 3 | **SpacingExtractor** | `spacing_extractor.py` | `spacing`, `grid` | Foundation | Canny edge detection, DBSCAN clustering, GCD base unit | 1.5s |
| 4 | **ShadowExtractor** | `shadow_extractor.py` | `shadow`, `elevation` | Foundation | Contrast analysis, blur radius detection | 1.8s |
| 5 | **ZIndexExtractor** | `zindex_extractor.py` | `zindex`, `zindex_docs` | Foundation | Layer hierarchy via shadow + overlap | 0.4s |
| 6 | **IconSizeExtractor** | `iconsize_extractor.py` | `icon_sizes` | Foundation | Hough circles, contour analysis, size clustering | 0.6s |

---

### FoundationExtractor Composite (4 extractors)

| # | Extractor | File | Token Types Produced | Category | Method | Performance |
|---|-----------|------|---------------------|----------|--------|-------------|
| 7 | **OpacityExtractor** | `opacity_extractor.py` | `opacity.scale` (transparent → solid) | Foundation | Alpha channel analysis, 12-level semantic scale | 0.3s |
| 8 | **TransitionExtractor** | `transition_extractor.py` | `transitions.duration`, `transitions.easing` | Foundation | Material Design 3 spec, spring/bounce curves | 0.1s |
| 9 | **BlurFilterExtractor** | `blur_filter_extractor.py` | `blur_filters.radius`, `blur_filters.backdrop` | Foundation | Laplacian variance, glassmorphic presets | 0.5s |
| 10 | **BorderRadiusExtractor** | `experimental/border_radius_extractor.py` | `radius` (sm, md, lg, full) | Foundation | Hough circles on corners, radius clustering | 0.7s |

**FoundationExtractor Total**: 4 extractors → ~2.5s parallel

---

### ComponentExtractor Composite (8 extractors)

| # | Extractor | File | Token Types Produced | Category | Method | Performance |
|---|-----------|------|---------------------|----------|--------|-------------|
| 11 | **GradientExtractor** | `gradient_extractor.py` | `gradients.linear`, `gradients.radial`, `gradients.conic` | Component | Pixel sampling, color transition detection (scipy.signal) | 2.1s |
| 12 | **BorderExtractor** | `border_extractor.py` | `borders.width`, `borders.style`, `borders.colors` | Component | Edge detection, morphological ops, FFT pattern analysis | 0.9s |
| 13 | **StateLayerExtractor** | `state_layer_extractor.py` | `state_layers` (hover, focus, pressed, disabled, selected) | Component | Material Design 3 spec (8%, 12%, 38% overlays) | 0.3s |
| 14 | **ComponentTokenExtractor** | `component_extractor.py` | `button`, `input`, `card`, `navigation` (5 variants × 5 states) | Component | Composition of foundation tokens | 0.5s |
| 15 | **MobileExtractor** | `mobile_extractor.py` | `mobile` (touch targets, safe areas, gestures) | Component | 44px iOS / 48px Android validation | 1.2s |
| 16 | **FontFamilyExtractor** | `font_family_extractor.py` | `font_family_detected` | Component | OCR + font matching (experimental) | 3.5s |
| 17 | **AudioPluginComponentExtractor** | `audio_plugin_component_extractor.py` | `audio_plugin` (knobs, sliders, VU meters, JUCE tokens) | Component | Hough circles for knobs, contour for sliders | 2.3s |
| 18 | **StyleMoodExtractor** | `style_mood_extractor.py` | `style_mood` (aesthetic keywords: minimal, bold, retro) | Component | HSV saturation, edge density, CLIP classification | 1.8s |

**ComponentExtractor Total**: 8 extractors → ~6.2s parallel (bottleneck: FontFamily 3.5s)

---

### VisualStyleExtractor Composite (4 extractors) - Visual DNA 2.0

| # | Extractor | File | Token Types Produced | Category | Method | Performance |
|---|-----------|------|---------------------|----------|--------|-------------|
| 19 | **MaterialExtractor** | `material_extractor.py` | `materials` (optical, tactile, age, finish, pattern) | Visual DNA | K-means segmentation, Sobel gradients (gloss), specular highlights | 2.8s |
| 20 | **LightingExtractor** | `lighting_extractor.py` | `lighting` (lights, ambient, model, shadows, volumetric) | Visual DNA | Gradient analysis (direction), LAB temperature, 3-point detection | 3.2s |
| 21 | **EnvironmentExtractor** | `environment_extractor.py` | `environment` (temperature, weather, time, location, atmosphere) | Visual DNA | LAB color temp, contrast/clarity, histogram analysis, CLIP | 2.5s |
| 22 | **ArtisticExtractor** | `artistic_extractor.py` | `art_style`, `cinematic`, `emotional` | Visual DNA | Depth cues, edge patterns, color distribution, CLIP | 3.5s |

**VisualStyleExtractor Total**: 4 extractors → ~11.0s parallel (bottleneck: Artistic 3.5s)

---

## AI Enhancement Extractors (10) - Optional

| # | Extractor | File | Token Types Enhanced/Produced | Category | AI Model | Cost | Performance |
|---|-----------|------|------------------------------|----------|----------|------|-------------|
| 23 | **CLIPSemanticExtractor** | `ai/clip_semantic_extractor.py` | `*.name` (creative names), `*.semantic_name` (descriptive) | AI Enhancement | CLIP ViT-B/32 | $0.00 | 5s (local) |
| 24 | **LLaVASemanticExtractor** | `ai/llava_semantic_extractor.py` | `*.design_intent`, `*.emotional_qualities` | AI Enhancement | LLaVA-1.5-7B | $0.00 | 10-15s (local, GPU) |
| 25 | **GPT4VisionExtractor** | `ai/gpt4_vision_extractor.py` | `*.design_intent`, `*.usage`, ontology | AI Enhancement | GPT-4V | $0.01-0.03 | 15-20s |
| 26 | **ClaudeVisionExtractor** | `ai/claude_vision_extractor.py` | `*.cultural_associations`, `*.design_intent` | AI Enhancement | Claude 3 Opus | $0.015 | 20-30s |
| 27 | **OntologyExtractor** | `ai/ontology_extractor.py` | `ontology.*` (art historical classification, era, style) | AI Enhancement | GPT-4V | $0.01-0.02 | 15s |
| 28 | **AIAdaptiveExtractor** | `ai_adaptive_extractor.py` | All token enhancements (orchestrator) | AI Enhancement | CLIP + GPT-4V/Claude | $0.00-0.05 | 5-40s |
| 29 | **MultiExtractor** | `ai/multi_extractor.py` | Progressive multi-tier extraction | AI Orchestrator | Multiple models | Variable | Variable |
| 30 | **DualExtractor** | `ai/dual_extractor.py` | Dual extraction strategy (CV + AI) | AI Orchestrator | CV + AI models | Variable | Variable |
| 31 | **AsyncDualExtractor** | `ai/async_dual_extractor.py` | Async dual extraction | AI Orchestrator | CV + AI models | Variable | Variable |
| 32 | **HybridExtractor** | `ai/hybrid_extractor.py` | Hybrid CV + AI extraction | AI Orchestrator | CV + AI models | Variable | Variable |

---

## Advanced CV Extractors (4) - Optional Features

| # | Extractor | File | Token Types Produced | Category | Method | Performance |
|---|-----------|------|---------------------|----------|--------|-------------|
| 33 | **AccessibilityExtractor** | `accessibility_extractor.py` | `accessibility.*` (WCAG, contrast, CVD overrides, focus) | Accessibility | WCAG contrast calculation, CVD simulation | 0.3s |
| 34 | **SemanticSegmentationExtractor** | `semantic_segmentation_extractor.py` | `segmentation.*` (object masks, semantic regions) | Advanced CV | SAM (Segment Anything Model) | 3-5s (GPU) |
| 35 | **ComponentRecognitionExtractor** | `component_recognition_extractor.py` | `components_detected.*` (button, input, card locations) | Advanced CV | YOLO or custom object detection | 2-4s |
| 36 | **DepthMapExtractor** | `depth_map_extractor.py` | `depth_map.*` (depth estimation, Z-layers) | Advanced CV | MiDaS or custom depth estimation | 2-3s (GPU) |
| 37 | **VideoAnimationExtractor** | `video_animation_extractor.py` | `animation.*` (motion vectors, transitions, keyframes) | Advanced CV | Optical flow, frame differencing | 5-10s per video |

---

## Experimental Extractors (6 unique) - Potentially Production-Ready

| # | Extractor | File | Token Types Produced | Category | Status | Notes |
|---|-----------|------|---------------------|----------|--------|-------|
| 38 | **AnimationExtractor** | `experimental/animation_extractor.py` | `animation.duration`, `animation.easing`, `animation.presets` | Experimental | Beta | May overlap with TransitionExtractor |
| 39 | **BreakpointsExtractor** | `experimental/breakpoints_extractor.py` | `breakpoints.*` (responsive breakpoints, grid changes) | Experimental | Alpha | Detects responsive design breakpoints |
| 40 | **CameraExtractor** | `experimental/camera_extractor.py` | `cinematic.camera.*` (focal length, aperture, distortion) | Experimental | Beta | Similar to ArtisticExtractor.cinematic |
| 41 | **GridExtractor** | `experimental/grid_extractor.py` | `grid.*` (columns, gutters, margins, baseline) | Experimental | Beta | More detailed than SpacingExtractor.grid |
| 42 | **TextureExtractor** | `experimental/texture_extractor.py` | `textures.*` (pattern, scale, orientation) | Experimental | Alpha | Complements MaterialExtractor |
| 43 | **VisualDNA20Extractor** | `visual_dna_extractor.py` | All Visual DNA tokens (orchestrator) | Orchestrator | Duplicate | Duplicates VisualStyleExtractor functionality |

---

## Token Type → Extractor Reverse Mapping

### Foundation Tokens

| Token Type | Produced By | Extractor File | Performance |
|------------|-------------|----------------|-------------|
| `palette` | ColorExtractor | `color_extractor.py` | 1.2s |
| `primitive` | ColorExtractor | `color_extractor.py` | 0.3s |
| `semantic_colors` | ColorExtractor | `color_extractor.py` | 0.2s |
| `typography` | TypographyExtractor | `typography_extractor.py` | 0.8s |
| `typography_extended` | TypographyExtractor | `typography_extractor.py` | 0.2s |
| `spacing` | SpacingExtractor | `spacing_extractor.py` | 1.5s |
| `grid` | SpacingExtractor | `spacing_extractor.py` | 0.1s |
| `shadow` | ShadowExtractor | `shadow_extractor.py` | 1.8s |
| `elevation` | ShadowExtractor | `shadow_extractor.py` | 0.2s |
| `icon_sizes` | IconSizeExtractor | `iconsize_extractor.py` | 0.6s |
| `zindex` | ZIndexExtractor | `zindex_extractor.py` | 0.4s |
| `radius` | BorderRadiusExtractor | `experimental/border_radius_extractor.py` | 0.7s |
| `opacity` | OpacityExtractor | `opacity_extractor.py` | 0.3s |
| `transitions` | TransitionExtractor | `transition_extractor.py` | 0.1s |
| `blur_filters` | BlurFilterExtractor | `blur_filter_extractor.py` | 0.5s |

**Foundation Total**: 15 token types from 10 extractors

---

### Component Tokens

| Token Type | Produced By | Extractor File | Performance |
|------------|-------------|----------------|-------------|
| `gradients.linear` | GradientExtractor | `gradient_extractor.py` | 2.1s |
| `gradients.radial` | GradientExtractor | `gradient_extractor.py` | 0.8s |
| `gradients.conic` | GradientExtractor | `gradient_extractor.py` | 0.6s |
| `borders` | BorderExtractor | `border_extractor.py` | 0.9s |
| `state_layers` | StateLayerExtractor | `state_layer_extractor.py` | 0.3s |
| `button` | ComponentTokenExtractor | `component_extractor.py` | 0.5s |
| `input` | ComponentTokenExtractor | `component_extractor.py` | 0.3s |
| `card` | ComponentTokenExtractor | `component_extractor.py` | 0.2s |
| `navigation` | ComponentTokenExtractor | `component_extractor.py` | 0.2s |
| `mobile` | MobileExtractor | `mobile_extractor.py` | 1.2s |
| `font_family_detected` | FontFamilyExtractor | `font_family_extractor.py` | 3.5s |
| `audio_plugin` | AudioPluginComponentExtractor | `audio_plugin_component_extractor.py` | 2.3s |
| `style_mood` | StyleMoodExtractor | `style_mood_extractor.py` | 1.8s |

**Component Total**: 13 token types from 8 extractors

---

### Visual DNA Tokens

| Token Type | Produced By | Extractor File | Performance |
|------------|-------------|----------------|-------------|
| `materials` | MaterialExtractor | `material_extractor.py` | 2.8s |
| `materials.optical` | MaterialExtractor | `material_extractor.py` | 0.3s |
| `materials.tactile` | MaterialExtractor | `material_extractor.py` | 0.5s |
| `materials.finish` | MaterialExtractor | `material_extractor.py` | 0.1s |
| `lighting.lights` | LightingExtractor | `lighting_extractor.py` | 3.2s |
| `lighting.ambient` | LightingExtractor | `lighting_extractor.py` | 0.3s |
| `lighting.model` | LightingExtractor | `lighting_extractor.py` | 0.4s |
| `lighting.shadows` | LightingExtractor | `lighting_extractor.py` | 0.5s |
| `environment.temperature` | EnvironmentExtractor | `environment_extractor.py` | 0.3s |
| `environment.weather` | EnvironmentExtractor | `environment_extractor.py` | 0.8s |
| `environment.time` | EnvironmentExtractor | `environment_extractor.py` | 0.6s |
| `environment.location` | EnvironmentExtractor | `environment_extractor.py` | 1.2s |
| `environment.atmosphere` | EnvironmentExtractor | `environment_extractor.py` | 0.4s |
| `art_style.dimension` | ArtisticExtractor | `artistic_extractor.py` | 1.2s |
| `art_style.render_mode` | ArtisticExtractor | `artistic_extractor.py` | 0.8s |
| `art_style.technique` | ArtisticExtractor | `artistic_extractor.py` | 1.0s |
| `art_style.cultural_tone` | ArtisticExtractor | `artistic_extractor.py` | 1.5s |
| `cinematic.camera` | ArtisticExtractor | `artistic_extractor.py` | 1.2s |
| `cinematic.color_grading` | ArtisticExtractor | `artistic_extractor.py` | 0.6s |
| `emotional` | ArtisticExtractor | `artistic_extractor.py` | 0.8s |

**Visual DNA Total**: 20 token types from 4 extractors

---

### AI Enhancement Tokens (Cross-Cutting)

| Token Type | Enhanced By | Extractor File | Performance |
|------------|-------------|----------------|-------------|
| `*.name` | CLIPSemanticExtractor | `ai/clip_semantic_extractor.py` | 5s |
| `*.semantic_name` | CLIPSemanticExtractor | `ai/clip_semantic_extractor.py` | 2s |
| `*.design_intent` | GPT4VisionExtractor, ClaudeVisionExtractor | `ai/gpt4_vision_extractor.py`, `ai/claude_vision_extractor.py` | 15-30s |
| `*.usage` | GPT4VisionExtractor | `ai/gpt4_vision_extractor.py` | 10-15s |
| `*.emotional_qualities` | LLaVASemanticExtractor | `ai/llava_semantic_extractor.py` | 8s |
| `*.cultural_associations` | ClaudeVisionExtractor | `ai/claude_vision_extractor.py` | 20s |
| `*.accessibility` | AccessibilityExtractor | `accessibility_extractor.py` | 0.2s |
| `ontology.*` | OntologyExtractor | `ai/ontology_extractor.py` | 15s |

**AI Enhancement Total**: 8 token types (applied to multiple base tokens)

---

## Complete Token Type Inventory

### Summary by Category

| Category | Token Types | Extractors | Performance (Parallel) |
|----------|-------------|------------|------------------------|
| **Foundation** | 15 types | 10 extractors | ~2.5s |
| **Component** | 13 types | 8 extractors | ~6.2s |
| **Visual DNA** | 20 types | 4 extractors | ~11.0s |
| **AI Enhancement** | 8 types (cross-cutting) | 10 extractors | 5-40s |
| **Advanced CV** | 5 types | 4 extractors | 2-5s |
| **Experimental** | 6 types | 6 extractors | Variable |
| **TOTAL** | **60+ token types** | **30+ extractors** | **10-50s** |

---

## Usage Examples

### Get Specific Token Types

```python
# Extract only color tokens (1.5s)
from extractors.color_extractor import kmeans_palette, generate_color_scale
palette = kmeans_palette(image, num_colors=8)
scales = {color: generate_color_scale(hex) for color, hex in palette.items()}

# Extract only spacing tokens (1.5s)
from extractors.spacing_extractor import extract_spacing_scale
spacing = extract_spacing_scale([image])

# Extract all foundation tokens (~2.5s parallel)
from extractors.composite_extractors import FoundationExtractor
foundation = FoundationExtractor().extract([image])
# Returns: opacity, transitions, blur_filters, radius

# Extract all Visual DNA tokens (~11s parallel)
from extractors.composite_extractors import VisualStyleExtractor
visual_dna = VisualStyleExtractor().extract([image])
# Returns: materials, lighting, environment, art_style, cinematic, emotional
```

### Query by Token Type

```python
# "I need shadow tokens" → Use ShadowExtractor (1.8s)
from extractors.shadow_extractor import aggregate_shadows_from_images
shadows = aggregate_shadows_from_images([image])
# Returns: shadow levels 0-5, elevation scale

# "I need button tokens" → Use ComponentTokenExtractor (0.5s + dependencies)
from extractors.composite_extractors import ComponentExtractor
components = ComponentExtractor().extract([image])
button_tokens = components.get("button")
# Returns: button variants (primary, secondary) × states (default, hover, focus, active, disabled)

# "I need material properties" → Use MaterialExtractor (2.8s)
from extractors.material_extractor import MaterialExtractor
materials = MaterialExtractor().extract([image])
# Returns: materials with optical (gloss, reflectivity), tactile (friction, warmth), finish
```

---

## Performance Optimization

### Skip Unused Extractors

```python
# Flat UI screenshot: Skip Visual DNA (saves ~11s)
config = {"enable_visual_dna": False}

foundation = FoundationExtractor().extract([image])  # 2.5s
components = ComponentExtractor().extract([image])   # 6.2s
# Total: ~8.7s (vs. ~19.7s with Visual DNA)

# AI-generated image: Skip Component tokens (saves ~6.2s)
config = {"enable_components": False}

foundation = FoundationExtractor().extract([image])  # 2.5s
visual_dna = VisualStyleExtractor().extract([image]) # 11.0s
# Total: ~13.5s (vs. ~19.7s with Components)
```

### Progressive Extraction (Non-Blocking)

```python
# Phase 1: Foundation (2.5s) → Show color/spacing preview
# Phase 2: Component (6.2s) → Show button/card preview
# Phase 3: Visual DNA (11.0s) → Show material/lighting preview
# Phase 4: AI Enhancement (20s) → Show enhanced tooltips
```

---

## Related Documentation

- [Complete Token-Extractor Technical Mapping](COMPLETE_TOKEN_EXTRACTOR_MAPPING.md) - Detailed CV libraries, AI models, methods
- [Token Schema Guide](TOKEN_SCHEMA_GUIDE.md) - Token schemas and examples
- [Extractor-Token Mapping](EXTRACTOR_TOKEN_MAPPING.md) - High-level relationships and dependencies

---

**Last Updated**: 2025-11-11
**Version**: 3.1
**Total Extractors**: 30+ active (49 files)
**Total Token Types**: 60+

---

## Quick Reference Table: Top 20 Most Used Token Types

| Rank | Token Type | Extractor | Performance | Use Case |
|------|------------|-----------|-------------|----------|
| 1 | `palette` | ColorExtractor | 1.2s | Every design system |
| 2 | `spacing` | SpacingExtractor | 1.5s | Every UI layout |
| 3 | `typography` | TypographyExtractor | 0.8s | Every text-based UI |
| 4 | `shadow` | ShadowExtractor | 1.8s | Material design, elevation |
| 5 | `button` | ComponentTokenExtractor | 0.5s | Interactive UIs |
| 6 | `materials` | MaterialExtractor | 2.8s | AI-generated images, 3D renders |
| 7 | `lighting` | LightingExtractor | 3.2s | AI-generated images, photography |
| 8 | `gradients` | GradientExtractor | 2.1s | Modern UIs, backgrounds |
| 9 | `radius` | BorderRadiusExtractor | 0.7s | Rounded designs |
| 10 | `semantic_colors` | ColorExtractor | 0.2s | Semantic tokens (brand, UI, text) |
| 11 | `environment` | EnvironmentExtractor | 2.5s | AI-generated scenes |
| 12 | `art_style` | ArtisticExtractor | 3.5s | Design style classification |
| 13 | `borders` | BorderExtractor | 0.9s | Card/panel UIs |
| 14 | `emotional` | ArtisticExtractor | 0.8s | Brand/mood analysis |
| 15 | `state_layers` | StateLayerExtractor | 0.3s | Interactive states |
| 16 | `transitions` | TransitionExtractor | 0.1s | Animation systems |
| 17 | `input` | ComponentTokenExtractor | 0.3s | Form UIs |
| 18 | `audio_plugin` | AudioPluginComponentExtractor | 2.3s | JUCE audio plugins |
| 19 | `opacity` | OpacityExtractor | 0.3s | Transparency scales |
| 20 | `zindex` | ZIndexExtractor | 0.4s | Layer management |

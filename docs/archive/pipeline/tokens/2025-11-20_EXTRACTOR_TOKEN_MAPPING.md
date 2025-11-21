# Extractor-to-Token Mapping Reference

**Complete Guide: Which Extractors Create Which Tokens**

Version: 3.1
Last Updated: 2025-11-11
Status: Comprehensive Reference

---

## Table of Contents

1. [Understanding Extractor Architecture](#understanding-extractor-architecture)
2. [Foundation Extractors](#foundation-extractors)
3. [Component Extractors](#component-extractors)
4. [Visual DNA Extractors](#visual-dna-extractors)
5. [AI-Enhanced Extractors](#ai-enhanced-extractors)
6. [Composite Extractors](#composite-extractors)
7. [Extraction Pipeline Flow](#extraction-pipeline-flow)
8. [Token Dependencies](#token-dependencies)

---

## Understanding Extractor Architecture

### Extractor Categories

Copy This uses **24+ specialized extractors** organized into **3 main categories**:

```
Extraction System
├── Foundation (11 extractors)
│   └── Core design primitives: color, spacing, typography, shadows
│
├── Component (9 extractors)
│   └── UI elements: buttons, inputs, borders, states, gradients
│
└── VisualStyle (4 extractors)
    └── Perceptual properties: materials, lighting, environment, artistic
```

### Extraction Methods

| Method | Speed | Cost | Accuracy | Used By |
|--------|-------|------|----------|---------|
| **Computer Vision (CV)** | Fast (1-12s) | $0.00 | 85-90% | Foundation & Component extractors |
| **Local AI (CLIP, LLaVA)** | Medium (5-20s) | $0.00 | 90-93% | Semantic naming, zero-shot classification |
| **Cloud AI (GPT-4V, Claude)** | Slow (10-40s) | $0.02-0.05 | 95-98% | Design intent, enhancement, validation |

### Extractor Base Classes

All extractors inherit from:

**Location**: `extractors/extractors/base_extractor.py`

```python
class TokenExtractor(ABC):
    """Base class for all token extractors"""
    @abstractmethod
    def extract(self, images: List[np.ndarray]) -> Dict[str, Any]:
        pass

class CompositeExtractor(TokenExtractor):
    """Runs multiple extractors in sequence"""
    def __init__(self, extractors: List[TokenExtractor]):
        self.extractors = extractors

    def extract(self, images: List[np.ndarray]) -> Dict[str, Any]:
        results = {}
        for extractor in self.extractors:
            results.update(extractor.extract(images))
        return results
```

---

## Foundation Extractors

### 1. Color Extractor

**File**: `extractors/extractors/color_extractor.py`

**Function-Based** (Phase 1 pattern)

**Tokens Produced**:
```typescript
{
  palette: {
    primary: string       // K-means dominant color
    secondary: string     // 2nd cluster centroid
    neutral: string       // Largest neutral cluster
    accent: string        // Highest saturation cluster
    text: string          // Darkest color (assumed text)
    background: string    // Lightest color (assumed bg)
  },
  primitive: {
    [colorFamily: string]: {
      "50": string,   // HSL lightness interpolation
      "100": string,
      ...
      "900": string
    }
  }
}
```

**Method**:
- **K-means clustering** in LAB color space (n=8 clusters)
- Cluster ranking by dominance (pixel count)
- Role assignment (primary, secondary, etc.) by heuristics
- Color scale generation via HSL interpolation

**Dependencies**: None (runs first)

**Performance**: ~1.2s for 1920×1080 image

**Example Usage**:
```python
from extractors.color_extractor import kmeans_palette, generate_color_scale

# Extract palette
palette = kmeans_palette(image, num_colors=8)
# Returns: {"primary": "#F15925", "secondary": "#4ECDC4", ...}

# Generate scale
scale = generate_color_scale(palette["primary"], name="orange")
# Returns: {"50": "#FFF5F0", ..., "900": "#311204"}
```

---

### 2. Typography Extractor

**File**: `extractors/extractors/typography_extractor.py`

**Function-Based**

**Tokens Produced**:
```typescript
{
  typography: {
    family: string          // Style-based inference
    weights: number[]       // Detected weight variations
  },
  typography_extended: {
    fonts: {
      display: {
        web: { family, source, weights, character }
        ios: string
        android: string
        juce: string
      }
    },
    scale: {
      [size: string]: {
        fontSize: string
        lineHeight: string
        letterSpacing?: string
      }
    }
  }
}
```

**Method**:
- **Style analysis** (not OCR) - analyzes aesthetics, not content
- Detects serif vs. sans-serif via edge patterns
- Infers weight variations from stroke thickness
- Platform-specific fallback recommendations

**Dependencies**: None

**Performance**: ~0.8s

**Example**:
```python
from extractors.typography_extractor import aggregate_typography_from_images

typography = aggregate_typography_from_images([image])
# Returns: {"family": "Inter", "weights": [400, 600, 700]}
```

---

### 3. Spacing Extractor

**File**: `extractors/extractors/spacing_extractor.py`

**Function-Based**

**Tokens Produced**:
```typescript
{
  spacing: {
    xs: number    // 4px typical
    sm: number    // 8px (base unit)
    md: number    // 16px
    lg: number    // 24px
    xl: number    // 32px
    xxl: number   // 48px
  },
  grid: {
    base: number        // Detected base unit (4 or 8)
    margin: number      // Container margins
  }
}
```

**Method**:
- **Canny edge detection** → find component boundaries
- Gap analysis between components
- Clustering similar gaps (DBSCAN)
- Base unit detection (GCD of all gaps)
- 6-level scale generation

**Dependencies**: None

**Performance**: ~1.5s

---

### 4. Shadow Extractor

**File**: `extractors/extractors/shadow_extractor.py`

**Function-Based**

**Tokens Produced**:
```typescript
{
  shadow: {
    level0: "none"
    level1: "0 1px 3px rgba(0,0,0,0.12)"
    level2: "0 4px 8px rgba(0,0,0,0.16)"
    level3: "0 8px 16px rgba(0,0,0,0.24)"
    level4: "0 16px 32px rgba(0,0,0,0.32)"
    level5: "0 24px 48px rgba(0,0,0,0.40)"
  },
  elevation: {
    raised: 2
    overlay: 8
    modal: 16
    popup: 24
  }
}
```

**Method**:
- **Contrast analysis** around component edges
- Blur radius detection via gradient analysis
- Elevation inference from shadow softness
- Progressive scaling (1, 2, 4, 8, 16, 24 dp)

**Dependencies**: Spacing (for component bounds)

**Performance**: ~1.8s

---

### 5. Icon Size Extractor

**File**: `extractors/extractors/iconsize_extractor.py`

**Function-Based**

**Tokens Produced**:
```typescript
{
  icon_sizes: {
    sm: 16
    md: 24
    lg: 32
    xl: 48
  }
}
```

**Method**:
- Circle/square detection (Hough circles, contour analysis)
- Size clustering
- Scale generation (16, 24, 32, 48, 64)

**Performance**: ~0.6s

---

### 6. Z-Index Extractor

**File**: `extractors/extractors/zindex_extractor.py`

**Function-Based**

**Tokens Produced**:
```typescript
{
  zindex: {
    base: 0
    dropdown: 1000
    sticky: 1100
    modal: 1200
    popover: 1300
    toast: 1400
  },
  zindex_docs: {
    base: "Default document flow"
    dropdown: "Dropdowns and popovers"
    ...
  }
}
```

**Method**:
- **Layer hierarchy detection** via shadow + overlap analysis
- Standard scale (100-step increments)
- Documentation generation

**Performance**: ~0.4s

---

### 7. Border Radius Extractor

**File**: `extractors/extractors/experimental/border_radius_extractor.py`

**Class-Based** (Phase 3)

**Tokens Produced**:
```typescript
{
  radius: {
    sm: 4
    md: 8
    lg: 12
    full: 9999
  }
}
```

**Method**:
- **Corner detection** via Hough circles on component bounds
- Radius clustering
- 4-level scale (small, medium, large, full)

**Performance**: ~0.7s

---

### 8-11. Performance Tokens

**Opacity Extractor** (`opacity_extractor.py`)
```typescript
{
  opacity: {
    opacity: {
      scale: {
        transparent: 0.0,
        ghost: 0.05,
        faint: 0.1,
        ...
        solid: 1.0
      }
    }
  }
}
```

**Transition Extractor** (`transition_extractor.py`)
```typescript
{
  transitions: {
    transitions: {
      duration: {
        instant: "50ms",
        quick: "150ms",
        smooth: "300ms",
        slow: "600ms"
      },
      easing: {
        spring: "cubic-bezier(0.34, 1.56, 0.64, 1)",
        bounce: "cubic-bezier(0.68, -0.55, 0.265, 1.55)"
      }
    }
  }
}
```

**Blur Filter Extractor** (`blur_filter_extractor.py`)
```typescript
{
  blur_filters: {
    blur: {
      radius: {
        sm: "4px",
        md: "8px",
        lg: "16px",
        xl: "24px"
      },
      backdrop: {
        glass: "blur(10px) saturate(180%)",
        frosted: "blur(20px) brightness(1.1)"
      }
    }
  }
}
```

---

## Component Extractors

### 12. Gradient Extractor

**File**: `extractors/extractors/gradient_extractor.py`

**Class-Based**

**Tokens Produced**:
```typescript
{
  gradients: {
    linear: [{
      angle: number
      stops: [{ color: string, position: number }]
    }],
    radial: [{
      shape: "circle" | "ellipse"
      stops: [{ color: string, position: number }]
    }],
    conic: [{
      angle: number
      stops: [{ color: string, position: number }]
    }]
  }
}
```

**Method**:
- **Color transition detection** via pixel sampling
- Direction analysis (angle detection)
- Stop position inference
- Multi-stop gradient reconstruction

**Performance**: ~2.1s

---

### 13. Border Extractor

**File**: `extractors/extractors/border_extractor.py`

**Class-Based** (Phase 3)

**Tokens Produced**:
```typescript
{
  borders: {
    width: {
      thin: 1,
      medium: 2,
      thick: 4
    },
    style: {
      solid: "solid",
      dashed: "dashed",
      dotted: "dotted"
    },
    colors: string[]
  }
}
```

**Method**:
- Edge detection + line pattern analysis
- Width clustering
- Style detection (solid vs. dashed vs. dotted)

**Performance**: ~0.9s

---

### 14. State Layer Extractor

**File**: `extractors/extractors/state_layer_extractor.py`

**Class-Based** (Phase 3)

**Tokens Produced**:
```typescript
{
  state_layers: {
    hover: 0.08,      // 8% overlay
    focus: 0.12,      // 12% overlay
    pressed: 0.12,    // 12% overlay
    disabled: 0.38,   // 38% opacity
    selected: 0.12    // 12% overlay
  }
}
```

**Method**:
- **Material Design 3 state layer specification**
- Interactive state detection
- Overlay opacity calculation

**Performance**: ~0.3s (spec-based, minimal CV)

---

### 15. Component Token Extractor

**File**: `extractors/extractors/component_extractor.py`

**Class-Based** (Phase 3 Priority #5)

**Tokens Produced**:
```typescript
{
  button: ButtonTokens,
  input: InputTokens,
  card: CardTokens,
  navigation: NavigationTokens
}
```

**Method**:
- **Composition** of foundation tokens
- State variation generation (default, hover, focus, active, disabled)
- Platform export preparation

**Dependencies**: Color, Spacing, Shadow, Border, State Layer

**Performance**: ~0.5s (composition, not extraction)

---

### 16-19. Advanced Component Extractors

**Mobile Extractor** (`mobile_extractor.py`)
- Touch targets (44px iOS, 48px Android)
- Safe areas (notch, home indicator)
- Gesture thresholds

**Font Family Extractor** (`font_family_extractor.py`)
- OCR-based font recognition (experimental)
- Confidence scoring

**Audio Plugin Component Extractor** (`audio_plugin_component_extractor.py`)
- Knob detection (circular controls)
- Slider detection (linear controls)
- VU meter detection
- JUCE-specific tokens

**Style Mood Extractor** (`style_mood_extractor.py`)
- Aesthetic keywords extraction
- Mood classification (warm, cool, minimal, etc.)

---

## Visual DNA Extractors

### 20. Material Extractor

**File**: `extractors/extractors/material_extractor.py`

**Class-Based** (Visual DNA 2.0)

**Tokens Produced**:
```typescript
{
  materials: {
    [materialName: string]: {
      material_class: "glass" | "metal" | "wood" | ...
      variant: string
      optical: {
        gloss: number         // 0-1
        reflectivity: number
        transmission: number
        scatter: number
      }
      tactile: {
        friction: number
        warmth: number
        grain: number
      }
      age: {
        wear: number
        patina: number
      }
      finish: "matte" | "satin" | "gloss" | "mirror"
      pattern?: string
      usage?: string
      design_intent?: string
    }
  }
}
```

**Method**:
- **K-means clustering** for surface segmentation
- **Sobel gradients** for gloss detection (high variance = glossy)
- **Specular highlight detection** for reflectivity
- **HSV analysis** for material classification
- **Texture analysis** for pattern recognition

**Performance**: ~2.8s

**Example**:
```python
from extractors.material_extractor import MaterialExtractor

extractor = MaterialExtractor()
materials = extractor.extract([image])
# Returns: {"materials": {"polished-metal": {...}, "frosted-glass": {...}}}
```

---

### 21. Lighting Extractor

**File**: `extractors/extractors/lighting_extractor.py`

**Class-Based** (Visual DNA 2.0)

**Tokens Produced**:
```typescript
{
  lighting: {
    lights: [{
      type: "key" | "fill" | "back" | "ambient"
      color: string
      temperature: number    // Kelvin
      intensity: number
      direction: { x, y, z }
      contrast: number
    }],
    ambient: { color, intensity, temperature },
    model: "lambert" | "phong" | "pbr",
    shadows: {
      softness: number
      contact_intensity: number
    },
    volumetric?: { scatter, density },
    scene_description?: string
  }
}
```

**Method**:
- **Gradient analysis** for light direction
- **LAB color space temperature** calculation
- **Shadow analysis** for light intensity
- **3-point lighting detection** (key, fill, back)
- **Specular highlight tracking** for source position

**Performance**: ~3.2s

---

### 22. Environment Extractor

**File**: `extractors/extractors/environment_extractor.py`

**Class-Based** (Visual DNA 2.0)

**Tokens Produced**:
```typescript
{
  environment: {
    temperature: {
      kelvin: number        // 2000-10000
      warmth: number        // 0-1
      description: string   // "warm", "neutral", "cool"
    },
    weather: {
      condition: "clear" | "cloudy" | "foggy" | "rainy" | "stormy"
      clarity: number       // 0-1
      humidity: number      // 0-1
    },
    time: {
      time_of_day: "dawn" | "day" | "golden_hour" | "dusk" | "night"
      confidence: number
    },
    location: {
      type: "studio" | "office" | "industrial" | "nature" | "scifi"
      confidence: number
    },
    atmosphere: {
      haze: number         // 0-1
      pollution: number
      soundscape?: string  // Inferred from visual cues
    }
  }
}
```

**Method**:
- **LAB color temperature** (a*/b* channels)
- **Contrast/clarity analysis** for weather
- **Luminance histogram** for time of day
- **Semantic segmentation** for location type

**Performance**: ~2.5s

---

### 23. Artistic Extractor

**File**: `extractors/extractors/artistic_extractor.py`

**Class-Based** (Visual DNA 2.0)

**Composite extractor providing**:

**Tokens Produced**:
```typescript
{
  art_style: {
    dimension: {
      type: "flat" | "2.5D" | "3D" | "volumetric"
      projection: "orthographic" | "perspective" | "isometric"
    },
    render_mode: "rasterized" | "ray-traced" | "hand-drawn"
    technique: string[]
    medium: string[]
    cultural_tone: string
  },
  cinematic: {
    camera: {
      framing: { aspect_ratio, safe_areas }
      lens: { focal_length, distortion, sensor_size }
      dof: { aperture, focal_distance, bokeh_quality }
    },
    color_grading: {
      lut_style: string
      contrast_curve: string
    },
    grain: number,
    vignette: number
  },
  emotional: {
    warmth: number          // 0-1
    energy: number
    serenity: number
    trust: number
    nostalgia: number
    futurism: number
    drama: number
    whimsy: number
  }
}
```

**Method**:
- **Depth cues** for dimensionality (shadows, occlusion, perspective)
- **Edge patterns** for technique (sharp = digital, soft = painted)
- **Color palette analysis** for cultural tone
- **LAB color distribution** for emotional qualities
- **Histogram analysis** for cinematic grading

**Performance**: ~3.5s

---

## AI-Enhanced Extractors

### 24. AI Adaptive Extractor

**File**: `extractors/extractors/ai_adaptive_extractor.py`

**Class-Based** (Visual DNA 2.0)

**Tokens Added to Existing Tokens**:
```typescript
// Enhances ColorToken
{
  name: "Molten Copper"                 // ← AI-generated
  semantic_name: "Sunset Ember"         // ← AI-generated
  design_intent: "Energetic..."         // ← AI-generated
  usage: "Primary CTAs..."              // ← AI-generated
  emotional_qualities: ["warm", ...]    // ← AI-generated
}
```

**Method**:
- **CLIP** (Contrastive Language-Image Pretraining) for semantic naming
- **LLaVA** for design intent inference
- **GPT-4 Vision** for usage recommendations (optional, $$$)

**Performance**: ~5-20s (local CLIP) or ~15-40s (cloud AI)

**Cost**: $0.00 (CLIP) or $0.02-0.05 (GPT-4V/Claude)

---

### Cloud AI Extractors (Optional Tier 3)

**GPT-4 Vision Extractor** (`extractors/extractors/ai/gpt4_vision_extractor.py`)
- Design intent analysis
- Semantic color naming
- Accessibility recommendations
- Style ontology

**Claude Vision Extractor** (`extractors/extractors/ai/claude_vision_extractor.py`)
- Design rationale
- Usage guidance
- Cultural context
- Emotional analysis

**Ontology Extractor** (`extractors/extractors/ai/ontology_extractor.py`)
- Art historical classification
- Style tags
- Era detection
- Cultural influences

---

## Composite Extractors

### Foundation Extractor

**File**: `extractors/extractors/composite_extractors.py`

**Runs** (4 extractors):
1. OpacityExtractor
2. TransitionExtractor
3. BlurFilterExtractor
4. BorderRadiusExtractor

**Performance**: ~2.5s parallel

---

### Component Extractor

**File**: `extractors/extractors/composite_extractors.py`

**Runs** (8 extractors):
1. GradientExtractor
2. MobileExtractor
3. BorderExtractor
4. StateLayerExtractor
5. ComponentTokenExtractor
6. FontFamilyExtractor
7. AudioPluginComponentExtractor
8. StyleMoodExtractor

**Performance**: ~6.2s parallel

---

### Visual Style Extractor

**File**: `extractors/extractors/composite_extractors.py`

**Runs** (4 extractors):
1. MaterialExtractor
2. LightingExtractor
3. EnvironmentExtractor
4. ArtisticExtractor

**Performance**: ~11.0s parallel

---

## Extraction Pipeline Flow

### Sequential Pipeline (Current)

```
Image Upload
    ↓
Foundation Extractors (parallel group 1)
│   ├── Color (1.2s)
│   ├── Spacing (1.5s)
│   ├── Typography (0.8s)
│   ├── Shadow (1.8s)
│   ├── IconSize (0.6s)
│   └── ZIndex (0.4s)
    ↓ (5.2s total, ~2.0s parallel)
Component Extractors (parallel group 2)
│   ├── Gradient (2.1s)
│   ├── Border (0.9s)
│   ├── Mobile (1.2s)
│   ├── StateLayer (0.3s)
│   ├── ComponentToken (0.5s)
│   └── Others (~3s)
    ↓ (8.0s total, ~2.5s parallel)
Visual DNA Extractors (parallel group 3)
│   ├── Material (2.8s)
│   ├── Lighting (3.2s)
│   ├── Environment (2.5s)
│   └── Artistic (3.5s)
    ↓ (12.0s total, ~3.5s parallel)
AI Enhancement (optional, parallel group 4)
│   ├── CLIP Semantic (5s local, parallel)
│   ├── GPT-4 Vision (15s, API)
│   └── Claude Vision (20s, API)
    ↓ (40s total, ~20s parallel)
Final Validation & Consensus
    ↓ (2s)
Complete Token Set
```

**Total Time**:
- **CV Only**: ~10s (8s parallel + 2s sequential)
- **CV + Local AI**: ~18s (15s parallel + 3s sequential)
- **CV + Cloud AI**: ~50s (40s parallel + 10s sequential)

**Actual Current Performance**: ~64s (not fully parallelized)

### Optimization Potential

With full parallelization:
- **Current**: 64s (sequential)
- **Parallel**: ~18s (72% improvement)
- **Parallel + GPU**: ~12s (81% improvement)

---

## Token Dependencies

### Dependency Graph

```
Base Tokens (No Dependencies)
├── Color Palette
├── Typography
└── Animation Timing

↓ (required by)

Foundation Tokens
├── Spacing → (requires) None
├── Shadow → (requires) Spacing (for component bounds)
├── Radius → (requires) Spacing (for component detection)
└── IconSize → (requires) None

↓ (required by)

Semantic Tokens
├── Brand Colors → (requires) Color Palette
├── UI Colors → (requires) Color Palette
└── Text Colors → (requires) Color Palette

↓ (required by)

Component Tokens
├── Button → (requires) Color, Spacing, Shadow, Border, StateLayer
├── Input → (requires) Color, Spacing, Border
└── Card → (requires) Color, Shadow, Radius

↓ (enhanced by)

Visual DNA Tokens (Independent, can run anytime)
├── Material
├── Lighting
├── Environment
└── Artistic

↓ (enhanced by)

AI Tokens (Enhancement layer, runs last)
├── Semantic Naming → (enhances) All color tokens
├── Design Intent → (enhances) All tokens
└── Ontology → (enhances) Complete token set
```

### Required Execution Order

**Must Run First**:
1. Color Extractor (provides color palette)
2. Spacing Extractor (provides spacing scale)

**Can Run After Foundation**:
3. Shadow Extractor (needs component bounds from spacing)
4. Border Extractor (needs component detection)
5. Gradient Extractor (needs color palette)

**Can Run Independently** (no dependencies):
- Typography Extractor
- Opacity Extractor
- Transition Extractor
- Blur Extractor
- Material Extractor
- Lighting Extractor
- Environment Extractor
- Artistic Extractor

**Must Run Last**:
- Component Token Extractor (requires all foundation tokens)
- AI Enhancement (enhances existing tokens)

---

## Extractor Configuration

### Enabling/Disabling Extractors

```python
# backend/routers/extraction.py

from extractors.composite_extractors import (
    FoundationExtractor,
    ComponentExtractor,
    VisualStyleExtractor
)

# Configuration
config = {
    "enable_foundation": True,      # Always recommended
    "enable_components": True,      # For UI screenshots
    "enable_visual_dna": False,     # For AI-generated images only
    "enable_ai": False,             # Optional AI enhancement
    "parallel_execution": True      # Enable parallelization
}

# Run extractors
foundation = FoundationExtractor().extract(images) if config["enable_foundation"] else {}
components = ComponentExtractor().extract(images) if config["enable_components"] else {}
visual_dna = VisualStyleExtractor().extract(images) if config["enable_visual_dna"] else {}

# Merge results
all_tokens = {**foundation, **components, **visual_dna}
```

### Custom Extractor Creation

**Example**: Creating a custom gradient extractor

```python
from extractors.base_extractor import TokenExtractor
import numpy as np

class CustomGradientExtractor(TokenExtractor):
    """Extract gradient patterns from images"""

    def extract(self, images: List[np.ndarray]) -> Dict[str, Any]:
        gradients = {"gradients": {"linear": [], "radial": []}}

        for image in images:
            # Your extraction logic here
            linear_gradients = self._detect_linear(image)
            radients["gradients"]["linear"].extend(linear_gradients)

        return gradients

    def _detect_linear(self, image: np.ndarray) -> List[Dict]:
        # Implementation
        pass
```

---

## Performance Optimization

### Parallel Execution

Use `CompositeExtractor` with parallel processing:

```python
import asyncio
from concurrent.futures import ProcessPoolExecutor

async def extract_parallel(images: List[np.ndarray]) -> Dict:
    extractors = [
        ColorExtractor(),
        SpacingExtractor(),
        TypographyExtractor()
    ]

    with ProcessPoolExecutor(max_workers=3) as executor:
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(executor, ext.extract, images)
            for ext in extractors
        ]
        results = await asyncio.gather(*tasks)

    # Merge results
    merged = {}
    for result in results:
        merged.update(result)

    return merged
```

### GPU Acceleration

For CV extractors (optional):

```python
# Enable GPU for K-means clustering
import cupy as cp  # CUDA-accelerated NumPy

def kmeans_gpu(image: cp.ndarray, k: int) -> cp.ndarray:
    # Use cupy instead of numpy for GPU acceleration
    pass
```

---

## Related Documentation

- [Token Schema Guide](TOKEN_SCHEMA_GUIDE.md) - Complete token schemas
- [Token Features](TOKEN_FEATURES.md) - Capabilities and use cases
- [Visual DNA 2.0](VISUAL_DNA_DEEP_DIVE.md) - Perceptual extractors
- [Generator Guide](GENERATOR_EXPORT_GUIDE.md) - Platform exports

---

**Last Updated**: 2025-11-11
**Version**: 3.1
**Status**: Complete Reference

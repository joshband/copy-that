# Experimental Features (v2.1+)

**Branch**: `feat/experimental-extractors-ai-enhancement`
**Status**: Prototype / Vibe Coding Exploration
**Target**: v2.1-v2.2 roadmap features

This document describes experimental extractors and AI enhancements being prototyped for future releases. These features are **not part of the v2.0 MVP** and can be developed independently.

---

## 🤖 AI Enhancement (v2.1)

### Overview

AI-powered token extraction using GPT-4 Vision and Google Cloud Vision APIs to complement traditional computer vision with semantic understanding.

### Key Features

#### 1. GPT-4 Vision Extractor

**Location**: `copy_this/extractors/extractors/ai/gpt4_vision_extractor.py`

**Capabilities**:
- Semantic token naming ("molten-copper" vs "orange500")
- Design intent interpretation ("retro audio warmth")
- Token relationship suggestions (which colors pair well)
- Context-aware extraction (understand UI patterns)

**Usage**:
```python
from extractors.ai import GPT4VisionExtractor

# Set API key
import os
os.environ["OPENAI_API_KEY"] = "sk-..."

# Initialize extractor
extractor = GPT4VisionExtractor()

# Option 1: Full extraction (AI-only)
tokens = extractor.extract([Path("ref.png")])

# Option 2: Refinement (recommended)
from extractors import ColorExtractor
cv_tokens = ColorExtractor().extract([Path("ref.png")])
enhanced = extractor.refine(cv_tokens, [Path("ref.png")])
```

**Cost**: ~$0.01-0.05 per image

---

#### 2. Hybrid Extractor

**Location**: `copy_this/extractors/extractors/ai/hybrid_extractor.py`

**Strategy**:
1. Fast CV extraction (ColorExtractor, SpacingExtractor, etc.)
2. Optional AI enhancement (GPT-4 Vision refinement)
3. Result caching (reduce API costs by 80%)
4. Graceful degradation (fallback to CV if AI fails)

**Usage**:
```python
from extractors.ai import HybridExtractor

# Default: All Phase 1 extractors + AI enhancement
extractor = HybridExtractor()
tokens = extractor.extract([Path("ref.png")])

# Disable AI (CV-only mode)
extractor = HybridExtractor(enable_ai=False)
tokens = extractor.extract([Path("ref.png")])

# Custom extractors with AI
from extractors import ColorExtractor, SpacingExtractor
extractor = HybridExtractor(
    cv_extractors=[ColorExtractor(), SpacingExtractor()],
    enable_ai=True
)
```

**Benefits**:
- Best of both worlds (speed + accuracy)
- Cost-effective (cache AI results)
- Production-ready fallbacks

---

#### 3. Configuration

**Location**: `copy_this/extractors/extractors/ai/config.py`

**Environment Variables**:
```bash
# OpenAI API key for GPT-4 Vision
export OPENAI_API_KEY="sk-..."

# Google Cloud API key (optional, future)
export GCP_API_KEY="..."
```

**Settings**:
```python
from extractors.ai.config import config

# Cost management
config.max_cost_per_image = 0.05  # $0.05 max
config.enable_caching = True
config.cache_ttl_hours = 24

# Feature flags
config.enable_gpt4_vision = True
config.fallback_to_cv = True  # Fallback if AI fails
```

---

## 🧪 Experimental Token Extractors (v2.1-v2.2)

### Overview

New token categories beyond the v1.3 core set (color, spacing, shadow, typography, z-index, icons).

### Extractors

#### 1. Border Radius Extractor

**Location**: `copy_this/extractors/extractors/experimental/border_radius_extractor.py`

**Extracts**:
```json
{
  "border": {
    "radius": {
      "none": "0px",
      "sm": "4px",
      "md": "8px",
      "lg": "16px",
      "xl": "24px",
      "full": "9999px"
    }
  }
}
```

**Use Cases**:
- Button corner rounding
- Card/panel borders
- Image thumbnails
- Modal corners

**Algorithm**:
1. Edge detection (Canny)
2. Contour finding
3. Corner detection (Harris/Shi-Tomasi)
4. Curve fitting to estimate radius
5. Quantize to 4px grid

**TODO**:
- Implement actual radius detection (currently placeholder)
- Support asymmetric radii (different per corner)
- Detect squircles and superellipses

---

#### 2. Gradient Extractor

**Location**: `copy_this/extractors/extractors/experimental/gradient_extractor.py`

**Extracts**:
```json
{
  "gradients": {
    "linear-1": {
      "type": "linear",
      "css": "linear-gradient(180deg, #F15925 0%, #D94A1F 100%)",
      "angle": 180,
      "stops": [
        {"color": "#F15925", "position": 0.0},
        {"color": "#D94A1F", "position": 1.0}
      ]
    },
    "radial-1": {
      "type": "radial",
      "css": "radial-gradient(circle at 50% 50%, ...)",
      "shape": "circle",
      "stops": [...]
    }
  }
}
```

**Use Cases**:
- Hero section backgrounds
- Button hover effects
- Card overlays
- Glass morphism effects

**Algorithm**:
1. Segment image into regions
2. Detect smooth color transitions
3. Fit linear/radial gradient models
4. Extract gradient parameters
5. Generate CSS strings

**TODO**:
- Implement gradient detection (LAB color space analysis)
- Detect conic/angular gradients
- Support multi-stop gradients (3+ colors)
- Extract gradient opacity/alpha

---

#### 3. Texture Extractor

**Location**: `copy_this/extractors/extractors/experimental/texture_extractor.py`

**Extracts**:
```json
{
  "textures": {
    "glass": {
      "type": "glass",
      "parameters": {
        "blur": 20,
        "opacity": 0.85,
        "saturation": 1.2
      },
      "css": {
        "backdrop-filter": "blur(20px) saturate(120%)",
        "background": "rgba(255, 255, 255, 0.85)"
      }
    },
    "noise": {
      "type": "noise",
      "parameters": {
        "frequency": 0.5,
        "intensity": 0.1
      },
      "css": {...}
    }
  }
}
```

**Texture Types**:
- Glass (glassmorphism, frosted glass)
- Metal (brushed, chrome, copper)
- Wood (grain patterns)
- Fabric (linen, canvas)
- Noise (grain, film grain)
- Paper (textured, cardstock)

**Use Cases**:
- Glassmorphism card backgrounds
- Vintage audio plugin skeuomorphism
- Paper texture for reading apps
- Noise overlays for depth

**Algorithm**:
1. Texture segmentation
2. Feature extraction (LBP, Gabor filters)
3. Material classification
4. Parameter extraction (blur, noise, opacity)
5. Generate tileable texture samples

**TODO**:
- Implement LBP (Local Binary Patterns) feature extraction
- Add material classifier (SVM or GPT-4 Vision)
- Generate tileable texture samples
- Support normal maps and displacement maps

---

## 🎯 Implementation Roadmap

### Phase 1: AI Enhancement (v2.1 - 2 weeks)

**Week 1: GPT-4 Vision Integration**
- [ ] Implement OpenAI API client
- [ ] Build vision prompt templates
- [ ] Parse structured JSON responses
- [ ] Add semantic token naming
- [ ] Cost tracking and limits

**Week 2: Hybrid Extractor**
- [ ] Implement result caching (SQLite or Redis)
- [ ] Build CV + AI merge logic
- [ ] Add fallback mechanisms
- [ ] Performance benchmarking
- [ ] User toggle (enable/disable AI)

---

### Phase 2: Experimental Extractors (v2.1-v2.2 - 3 weeks)

**Week 1: Border Radius**
- [ ] Implement edge detection pipeline
- [ ] Add curve fitting algorithm
- [ ] Quantization to 4px grid
- [ ] Integration tests
- [ ] Demo visualization

**Week 2: Gradients**
- [ ] LAB color space analysis
- [ ] Linear gradient detection
- [ ] Radial gradient detection
- [ ] CSS gradient generation
- [ ] Figma gradient export

**Week 3: Textures**
- [ ] LBP feature extraction
- [ ] Material classifier (or GPT-4 Vision)
- [ ] Glassmorphism parameter extraction
- [ ] Noise/grain detection
- [ ] Tileable texture generation

---

## 🧰 Development Guide

### Setup

```bash
# Switch to experimental branch
git checkout feat/experimental-extractors-ai-enhancement

# Install dependencies
cd copy_this/ingest
pip install -r requirements.txt

# Add AI dependencies (optional)
pip install openai google-cloud-vision

# Set API keys
export OPENAI_API_KEY="sk-..."
```

### Testing

```bash
# Test AI extractors (requires API key)
pytest tests/extractors/ai/test_gpt4_vision.py

# Test experimental extractors
pytest tests/extractors/experimental/test_border_radius.py
pytest tests/extractors/experimental/test_gradient.py
pytest tests/extractors/experimental/test_texture.py
```

### Adding New Extractors

1. **Create extractor class**:
```python
from ..base_extractor import TokenExtractor

class MyExtractor(TokenExtractor):
    def extract(self, images: List[Path]) -> Dict[str, Any]:
        # Implementation
        return {"my_tokens": {...}}
```

2. **Add tests**:
```python
def test_my_extractor():
    extractor = MyExtractor()
    tokens = extractor.extract([Path("test.png")])
    assert "my_tokens" in tokens
```

3. **Register in `__init__.py`**:
```python
from .my_extractor import MyExtractor
__all__ = [..., "MyExtractor"]
```

---

## 📊 Success Metrics

### AI Enhancement

**Goals**:
- Semantic naming accuracy: 80%+ match with human labels
- Cost per image: <$0.03 average
- Cache hit rate: >70% (reduce API costs)
- Fallback success: 100% (CV works if AI fails)

**User Value**:
- Better token names (easier to understand)
- Design intent documentation (why this color?)
- Faster design system adoption

### Experimental Extractors

**Goals**:
- Border radius detection: 85%+ accuracy
- Gradient detection: 70%+ (complex problem)
- Texture classification: 75%+ accuracy
- Processing time: <5 sec per image

**User Value**:
- More comprehensive design systems
- Fewer manual token definitions
- Better match to reference designs

---

## 🚀 Next Steps

### Immediate (Phone-Friendly Vibe Coding)

1. **Prototype GPT-4 Vision API call**:
   - Implement `_build_prompt()` for color extraction
   - Test with sample image
   - Parse JSON response
   - Document findings

2. **Test border radius detection**:
   - Implement basic Canny edge detection
   - Visualize detected corners
   - Experiment with radius estimation

3. **Explore texture features**:
   - Try LBP on sample images
   - Visualize texture patterns
   - Document which features work best

### Medium-Term (Full Implementation)

4. **Complete HybridExtractor**:
   - Implement caching layer
   - Add cost tracking
   - Build merge logic
   - Performance testing

5. **Production-ready experimental extractors**:
   - Full algorithm implementations
   - Comprehensive test coverage
   - Documentation and examples
   - Integration with v2.0 GUI

### Long-Term (v2.2+)

6. **Advanced AI features**:
   - DALL-E preview generation
   - OpenAI embeddings for token search
   - Multi-modal understanding (image + text)

7. **More extractors**:
   - Motion/animation from video
   - Accessibility tokens (focus states, ARIA)
   - Component detection (buttons, cards, etc.)

---

## 💡 Ideas & Notes

### GPT-4 Vision Prompt Engineering

**Best practices discovered**:
- TODO: Document prompt templates that work well
- TODO: Test different temperature settings
- TODO: Compare GPT-4V vs GPT-4 Turbo with vision

### OpenCV Techniques

**Effective algorithms**:
- TODO: Document which edge detectors work best
- TODO: Compare Canny vs Sobel vs Laplacian
- TODO: Test different blur kernels for noise reduction

### Cost Optimization

**Strategies to test**:
- TODO: Batch multiple images in single API call
- TODO: Compress images before sending to API
- TODO: Use lower resolution for analysis (faster + cheaper)
- TODO: Implement intelligent caching (invalidation strategy)

---

## 📚 References

### AI/ML
- [OpenAI Vision API Docs](https://platform.openai.com/docs/guides/vision)
- [Google Cloud Vision](https://cloud.google.com/vision/docs)
- [GPT-4 Vision System Card](https://cdn.openai.com/papers/gpt-4v-system-card.pdf)

### Computer Vision
- [OpenCV Documentation](https://docs.opencv.org/)
- [Local Binary Patterns (LBP)](https://en.wikipedia.org/wiki/Local_binary_patterns)
- [Gabor Filters for Texture](https://en.wikipedia.org/wiki/Gabor_filter)
- [Image Quilting for Texture Synthesis](https://people.eecs.berkeley.edu/~efros/research/quilting.html)

### Design Tokens
- [CSS Gradients](https://developer.mozilla.org/en-US/docs/Web/CSS/gradient)
- [Glassmorphism Design](https://hype4.academy/tools/glassmorphism-generator)
- [Border Radius in Design Systems](https://www.designsystems.com/border-radius-in-design-systems/)

---

**Status**: Ready for vibe coding! 🎨
**Next**: Pick any TODO above and start experimenting!

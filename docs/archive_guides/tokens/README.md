# Design Token System - Comprehensive Documentation

> Complete guide to Copy This' advanced design token extraction, storytelling, and multi-platform export system.

**Version**: 3.1 | **Last Updated**: November 2025 | **Status**: Production Ready

---

## 📚 Documentation Index

### Core Guides

| Guide | Description | Audience |
|-------|-------------|----------|
| **[Token Schema Guide](TOKEN_SCHEMA_GUIDE.md)** | Complete token schemas with visual examples, covering 60+ token categories from foundation to Visual DNA 2.0 | Developers, Designers |
| **[Token Reference](TOKEN_REFERENCE.md)** | Complete token taxonomy, examples, and usage patterns | All Users |
| **[Token System Overview](TOKEN_SYSTEM.md)** | High-level system architecture and 15-category ontology | Architects, Team Leads |

### Advanced Guides

| Guide | Description | For |
|-------|-------------|-----|
| **[Extractor Routing Table](EXTRACTOR_ROUTING_TABLE.md)** ⭐ | **Single source of truth**: Token → Extractor → CV/AI → Confidence → Versioning routing table with TokenPlan/ExtractorResult schemas | Architects, ML Engineers |
| **[Extractor-Token Mapping](EXTRACTOR_TOKEN_MAPPING.md)** | Which extractors create which tokens, dependencies, and pipeline flow | Developers, Contributors |
| **[Complete Token-Extractor Mapping](COMPLETE_TOKEN_EXTRACTOR_MAPPING.md)** | Technical mapping with CV libraries (OpenCV), AI models (CLIP, GPT-4V), and extraction methods | Developers, ML Engineers |
| **[Extractor-to-Token Type Table](EXTRACTOR_TO_TOKEN_TYPE_TABLE.md)** | Quick reference: 30+ extractors → 60+ token types with performance metrics | All Users |
| **[Storytelling Framework](STORYTELLING_FRAMEWORK.md)** | Transform technical tokens into memorable narratives with emotional context | Designers, Product Managers |
| **[Token Ontology Reference](TOKEN_ONTOLOGY_REFERENCE.md)** | Formal ontological structure for design language classification and taxonomy | Architects, AI Engineers |

### Specialized Documentation

| Guide | Description | For |
|-------|-------------|-----|
| **[Visual DNA Deep Dive](VISUAL_DNA_DEEP_DIVE.md)** | Comprehensive guide to material, lighting, environment, and artistic extractors | Designers, 3D Artists |
| **[Token Variations Guide](TOKEN_VARIATIONS_GUIDE.md)** | Multi-variant system (light/dark/high-contrast, spacing scales, shadow depths) | Designers, Developers |
| **[Component Inheritance Patterns](COMPONENT_INHERITANCE_PATTERNS.md)** | Production-ready component architecture with trait composition and model-view separation | Developers, Architects |
| **[Generator & Export Guide](GENERATOR_EXPORT_GUIDE.md)** | Transform tokens into production code for React, Vue, Angular, Svelte, vanilla JS with multi-framework generation | Developers, Architects |
| **[Design Libraries Guide](DESIGN_LIBRARIES_GUIDE.md)** | Multi-style inheritance architecture (parent/child style libraries) | Architects, Tech Leads |
| **[Component Tokens](../../architecture/COMPONENT_TOKEN_SCHEMA.md)** | Button, Input, Card, Audio Plugin schemas | Developers |

---

## 🎯 Quick Start

### For Designers

**Goal**: Extract tokens from UI screenshots

1. Read: [Token System Overview](TOKEN_SYSTEM.md) (10 min)
2. Explore: [Token Reference](TOKEN_REFERENCE.md) (see examples)
3. Try: Upload a screenshot and explore results
4. Learn: [Storytelling Framework](STORYTELLING_FRAMEWORK.md) (understand the narrative)

### For Developers

**Goal**: Integrate token extraction into your workflow

1. Read: [Token Schema Guide](TOKEN_SCHEMA_GUIDE.md) (understand data structures)
2. Study: [Extractor-Token Mapping](EXTRACTOR_TOKEN_MAPPING.md) (learn the pipeline)
3. Implement: Use TypeScript types from `frontend/src/api/types.ts`
4. Export: Generate code for your platform (CSS, React, JUCE, etc.)

### For Product Managers

**Goal**: Understand capabilities and use cases

1. Read: [Token System Overview](TOKEN_SYSTEM.md) (big picture)
2. Explore: [Storytelling Framework](STORYTELLING_FRAMEWORK.md) (user-facing value)
3. Review: Token examples in [Token Reference](TOKEN_REFERENCE.md)

---

## 🏗️ System Architecture

### Token Categories (15 Total)

```
Design Token System v3.1
├── 1. Foundation (Primitives)
│   ├── Color (palette, scales, semantic)
│   ├── Typography (families, weights, scales)
│   ├── Spacing (scale, grid, rhythm)
│   ├── Shadow & Elevation
│   └── Border Radius
│
├── 2. Semantic (Context-Aware)
│   ├── Brand Colors
│   ├── UI Surface Colors
│   ├── Feedback Colors (success, warning, error)
│   └── Text Colors (hierarchy)
│
├── 3. Component (Compositional) ⭐ NEW v3.0
│   ├── Button (5 variants × 5 states)
│   ├── Input (5 types × 6 states)
│   ├── Card (3 variants × 3 states)
│   ├── Navigation (header, sidebar, tabs)
│   └── Audio Plugins (knobs, sliders, VU meters) 🎛️
│
├── 4. Layout & Density
│   ├── Grid System
│   ├── Breakpoints (responsive)
│   └── Density Variants (compact/comfortable/spacious)
│
├── 5. Perceptual & Material ⭐ Visual DNA 2.0
│   ├── Material Properties (optical, tactile, age)
│   ├── Surface Finish (gloss, reflectivity, texture)
│   └── Physical Characteristics
│
├── 6. Optics & Lighting ⭐ Visual DNA 2.0
│   ├── Light Sources (3-point lighting)
│   ├── Lighting Models (PBR, Phong)
│   ├── Shadows (softness, contact, penumbra)
│   └── Volumetrics (fog, bloom, light shafts)
│
├── 7. Environment ⭐ Visual DNA 2.0
│   ├── Temperature (color temperature, warmth)
│   ├── Time of Day (dawn, day, golden hour)
│   ├── Weather (clear, cloudy, foggy)
│   └── Atmosphere (haze, humidity, mood)
│
├── 8. Motion & Animation
│   ├── Duration Scales
│   ├── Easing Functions (springs, bounces)
│   ├── Interaction Presets
│   └── Tactility (press/hover behaviors)
│
├── 9. Art Style & Expression ⭐ Visual DNA 2.0
│   ├── Dimensionality (flat, 2.5D, 3D)
│   ├── Rendering Technique (photorealistic, illustrated)
│   ├── Artistic Medium (digital, watercolor, etc.)
│   └── Cultural Tone
│
├── 10. Cinematic & Camera
│   ├── Framing & Composition
│   ├── Lens Properties (focal length, distortion)
│   ├── Depth of Field (aperture, bokeh)
│   └── Color Grading
│
├── 11. Physics & Tactility
│   ├── Physical Properties (mass, elasticity)
│   ├── Haptic Feedback
│   └── Input Thresholds
│
├── 12. Accessibility
│   ├── WCAG Contrast Validation
│   ├── Color Vision Deficiency Overrides
│   ├── Focus Indicators
│   └── Touch Targets & Motion Preferences
│
├── 13. Composite Systems
│   ├── Surface Recipes (glassmorphic, elevated)
│   ├── Interaction Patterns (hover, press, modal)
│   └── Control Archetypes (vintage dial, modern switch)
│
├── 14. Platform Mapping
│   ├── Web (CSS Variables, Tailwind)
│   ├── Mobile (iOS UIKit, Android Material)
│   ├── Desktop (JUCE C++, Electron)
│   └── 3D Engines (Unity, Unreal materials)
│
└── 15. Governance & Metadata
    ├── Versioning (semantic versions)
    ├── Ownership & Accountability
    ├── Extraction Provenance
    └── Audit Trails
```

---

## 🔬 Extraction System

### 30+ Specialized Extractors

**Foundation Extractors** (11):
- Color, Typography, Spacing, Shadow, Icon Size, Z-Index
- Opacity, Transitions, Blur, Border, Border Radius

**Component Extractors** (9):
- Gradient, Mobile, Border, State Layer, Component Token
- Font Family, Audio Plugin, Style Mood, Advanced CV

**Visual DNA Extractors** (4) ⭐:
- Material, Lighting, Environment, Artistic

**AI Enhancement Extractors** (10):
- CLIP Semantic, LLaVA, GPT-4V, Claude Vision, Ontology
- Multi-tier, Dual, Async Dual, Hybrid, AI Adaptive

**Advanced CV Extractors** (4):
- Accessibility, Semantic Segmentation, Component Recognition, Depth Map

### Extraction Methods

| Method | Speed | Cost | Accuracy | Use Case |
|--------|-------|------|----------|----------|
| **Computer Vision** | Fast (1-12s) | $0.00 | 85-90% | Foundation & Component tokens |
| **Local AI (CLIP)** | Medium (5-20s) | $0.00 | 90-93% | Semantic naming, classification |
| **Cloud AI (GPT-4V, Claude)** | Slow (10-40s) | $0.02-0.05 | 95-98% | Design intent, enhancement |

### Pipeline Performance

- **CV Only**: ~10s (Foundation + Component tokens)
- **CV + Local AI**: ~18s (+ semantic naming, zero-shot)
- **CV + Cloud AI**: ~50s (+ design intent, full enhancement)
- **Parallel Optimized**: ~12s (with full GPU acceleration)

---

## 🎨 Key Features

### 1. Multi-Variant System (v3.1)

Generate **3 variants per token category**:

**Color Schemes**:
- Light Theme (recommended, 100% compliance)
- Dark Theme (inverted luminance)
- High Contrast (WCAG AAA, accessibility-first)

**Spacing Scales**:
- Compact (80%, mobile/dense UIs)
- Comfortable (100%, default)
- Spacious (125%, accessibility/large screens)

**Shadow Depths**:
- Subtle (flat design, minimal elevation)
- Moderate (standard Material Design)
- Dramatic (high-impact, bold depth)

**Border Radius**:
- Sharp (0px, angular/corporate)
- Rounded (default, balanced)
- Pill (3×, organic/friendly)

### 2. Storytelling Enhancement

Every token includes:
- **Creative Name**: "Molten Copper" (memorable)
- **Descriptive Name**: "Retro Orange Sunset" (functional)
- **Technical Name**: `primary-cta-orange` (code-friendly)
- **Design Intent**: Why this token exists
- **Usage Guidance**: When and how to use it
- **Emotional Qualities**: Mood and feeling
- **Cultural Associations**: Cross-cultural meaning

### 3. Visual DNA 2.0

Extract **perceptual properties** from AI-generated images:
- Material characteristics (glass, metal, wood properties)
- Lighting setup (3-point lighting, PBR)
- Environmental context (weather, time, atmosphere)
- Artistic style (dimensionality, technique, cultural tone)
- Emotional qualities (warmth, energy, serenity)

### 4. WCAG Validation

- **Automated contrast checking** for all color pairs
- **AAA/AA/AA Large compliance** scoring
- **Auto-adjustment suggestions** for failed pairs
- **Color vision deficiency** (CVD) safe palettes

### 5. Platform Exports

**One extraction → Multi-framework generation** 🚀:

**Component Libraries** (model-view separation):
- React Components (@aws-ui-react)
- Vue Components (@aws-ui-vue)
- Angular Components (@aws-ui-ng)
- Svelte Components (@aws-ui-svelte)
- Vanilla JS/Web Components (@aws-ui-web)

**Code Exports**:
- CSS Variables
- TypeScript Types
- Tailwind Config
- Material-UI Theme
- JUCE C++ LookAndFeel 🎛️
- Figma Tokens Plugin
- JSON Design Tokens (W3C spec)

---

## 📊 Statistics

| Metric | Value |
|--------|-------|
| **Token Categories** | 15 |
| **Extractors** | 30+ (49 files) |
| **Token Types Produced** | 60+ |
| **Type Definitions** | 100+ |
| **Documentation Pages** | 13 comprehensive guides |
| **Lines of Code** | ~8,500 (extractors + generators) |
| **Automated Tests** | 41 (100% passing) |
| **Platform Exports** | 8+ (CSS, TypeScript, React, JUCE, Figma, MUI, Tailwind) |
| **Extraction Accuracy** | 95%+ |
| **WCAG Compliance** | AA/AAA |

---

## 🚀 Use Cases

### For Design Systems

**Extract complete design systems**:
- Foundation tokens (color, spacing, typography)
- Component tokens (button, input, card states)
- Semantic mappings (light/dark themes)
- Platform exports (CSS, Tailwind, React)

### For AI-Generated Images

**Extract Visual DNA** from Midjourney, DALL-E, Stable Diffusion:
- Material properties (glossy metal, frosted glass)
- Lighting characteristics (3-point studio setup)
- Environmental context (golden hour, foggy morning)
- Artistic style (retro, minimalist, industrial)

### For Audio Plugin UIs

**JUCE-specific extraction** 🎛️:
- Rotary knob tokens (skeuomorphic, flat, vintage)
- Linear slider tokens (vertical, horizontal)
- VU meter tokens (peak, RMS, stereo)
- Hardware control aesthetics

### For Accessibility Compliance

**WCAG AA/AAA validation**:
- Contrast ratio checking for all pairs
- Auto-adjustment suggestions
- CVD-safe palette generation
- Touch target validation (44px minimum)

---

## 🔗 Related Documentation

### Architecture
- [Architecture Overview](../../architecture/README.md)
- [Progressive Extraction Architecture](../../architecture/PROGRESSIVE_EXTRACTION_ARCHITECTURE.md)
- [Token Data Flow](../../architecture/diagrams/token-data-flow.md)

### Development
- [TypeScript Types](../../../frontend/src/api/types.ts)
- [Python Schemas](../../../extractors/extractors/visual_dna_schema.py)
- [Generator System](../../../generators/README.md)

### Analysis
- [Performance Benchmarks](../../analysis/performance/README.md)
- [Extractor Audit Report](../../../backend/EXTRACTOR_AUDIT_REPORT.md)
- [Taxonomy Analysis](../../../EXTRACTOR_TAXONOMY_ANALYSIS.md)

---

## 🛠️ Implementation Examples

### Extract Tokens (Python)

```python
from extractors.composite_extractors import (
    FoundationExtractor,
    ComponentExtractor,
    VisualStyleExtractor
)

# Load image
image = cv2.imread("screenshot.png")

# Extract tokens
foundation = FoundationExtractor().extract([image])
components = ComponentExtractor().extract([image])
visual_dna = VisualStyleExtractor().extract([image])

# Merge results
all_tokens = {**foundation, **components, **visual_dna}
```

### Use Tokens (TypeScript)

```typescript
import { DesignTokens } from './api/types';

const tokens: DesignTokens = await fetchTokens();

// Access color
const primaryColor = tokens.palette.primary;
console.log(primaryColor.hex); // "#F15925"
console.log(primaryColor.name); // "Molten Copper"

// Access spacing
const cardPadding = tokens.spacing.md; // 16

// Access material
const buttonMaterial = tokens.materials?.["polished-metal"];
console.log(buttonMaterial.optical.gloss); // 0.8
```

### Export to Platform

```bash
# Generate React demo
npm run generate:react

# Generate JUCE C++
npm run generate:juce

# Generate Tailwind config
npm run generate:tailwind

# Export all formats
npm run generate:all
```

---

## 📈 Version History

| Version | Date | Highlights |
|---------|------|------------|
| **3.1** | 2025-11 | Multi-variant system, Visual DNA 2.0, storytelling |
| **3.0** | 2025-10 | Component tokens, compositional architecture |
| **2.6** | 2025-01 | Audio plugins, style/mood extraction |
| **2.5** | 2024-12 | Advanced CV (font family, component recognition) |
| **2.4** | 2024-11 | Opacity, transitions, blur filters |
| **2.0** | 2024-10 | AI enhancement, WCAG validation |
| **1.5** | 2024-09 | Semantic tokens, grid system |
| **1.0** | 2024-08 | Foundation tokens (color, spacing, typography) |

---

## 🤝 Contributing

When adding new token categories:
1. Update TypeScript types in `frontend/src/api/types.ts`
2. Add Python schema in `extractors/extractors/visual_dna_schema.py`
3. Create extractor in `extractors/extractors/`
4. Add generator support in `generators/src/`
5. Document in this guide
6. Add tests

---

## 📄 License

Part of the Copy This project - see root LICENSE.

---

**Need Help?**
- 📖 Start with [Token System Overview](TOKEN_SYSTEM.md)
- 🔍 Search [Token Reference](TOKEN_REFERENCE.md)
- 💡 Explore [Storytelling Framework](STORYTELLING_FRAMEWORK.md)
- 🏗️ Deep dive into [Extractor-Token Mapping](EXTRACTOR_TOKEN_MAPPING.md)

**Last Updated**: 2025-11-11 | **Version**: 3.1 | **Status**: Complete

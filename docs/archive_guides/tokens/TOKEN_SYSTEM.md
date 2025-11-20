# Comprehensive Design Token System - v3.1

## Overview

This document describes the complete design token ontology - a hierarchical taxonomy covering everything from foundational primitives to advanced perceptual, motion, and cinematic concepts.

## What is an Ontology of Taxonomies?

This system is:
- **Ontology**: A formal knowledge structure defining relationships and semantics
- **Taxonomy**: Hierarchical classification of design tokens
- **Visual DNA**: Complete characterization of a design's properties and intent

Think of it as a "language" that AI uses to understand and communicate design decisions.

## Architecture

```
Design Token System
├── 1. Foundation (Primitives)
│   ├── Color (brand, neutral, state)
│   ├── Typography (families, weights, scales)
│   ├── Spacing (units, scales)
│   ├── Shadow (elevation, depth)
│   └── Radius (curvature, form language)
│
├── 2. Semantic (Meaningful Aliases)
│   ├── Text Roles (primary, secondary, muted)
│   ├── Surfaces (page, card, elevated)
│   ├── Borders (subtle, strong, focus)
│   └── States (success, warning, danger, info)
│
├── 3. Component Tokens (Scoped)
│   ├── Button (background, text, states)
│   ├── Input (field, placeholder, focus)
│   ├── Card (surface, elevation, radius)
│   └── Hardware Controls (knob, slider, gauge)
│
├── 4. Layout & Density
│   ├── Grid (columns, gutters, margins)
│   ├── Breakpoints (responsive thresholds)
│   └── Density Scale (compact ↔ comfortable)
│
├── 5. Perceptual & Material (NEW)
│   ├── Material Class (metal, glass, plastic, etc.)
│   ├── Optical Behavior (gloss, reflectivity, transmission)
│   ├── Age & Condition (wear, patina, cleanliness)
│   └── Texture (finish, pattern, imperfections)
│
├── 6. Optics & Lighting (NEW)
│   ├── Light Sources (key, fill, back, ambient)
│   ├── Lighting Models (lambert, phong, PBR)
│   ├── Shadows (softness, contact, penumbra)
│   └── Volumetrics (fog, bloom, light shafts)
│
├── 7. Environment (NEW)
│   ├── Temperature (warm, neutral, cool)
│   ├── Time of Day (dawn, day, golden hour, night)
│   ├── Atmosphere (haze, humidity, reflection maps)
│   └── Context (scene description)
│
├── 8. Motion & Animation (NEW)
│   ├── Timing (duration scales, delays)
│   ├── Easing (curves, springs, personality)
│   ├── Tactility (press/hover scale, squash/stretch)
│   └── Interaction Presets (complete animations)
│
├── 9. Art Style & Expression (NEW)
│   ├── Dimensionality (flat, 2.5D, 3D, volumetric)
│   ├── Technique (photorealistic, illustrative, 3D-rendered)
│   ├── Medium (digital paint, airbrush, watercolor)
│   └── Palette Mode (pastel, cinematic, surreal)
│
├── 10. Cinematic & Camera (NEW)
│   ├── Framing (aspect ratio, safe areas)
│   ├── Lens (focal length, distortion, sensor)
│   ├── Depth of Field (aperture, bokeh, blur)
│   └── Post-Effects (vignette, grain, grading)
│
├── 11. Physics & Tactility (NEW)
│   ├── Physical Properties (mass, friction, elasticity)
│   ├── Haptics (strength, duration, pattern)
│   └── Input Thresholds (drag, swipe, press)
│
├── 12. Accessibility
│   ├── Contrast (text, UI, AA/AAA)
│   ├── Focus Indicators
│   ├── Touch Targets
│   └── Reduced Motion
│
├── 13. Composite Systems (NEW)
│   ├── Surface Recipes (glassmorphic, elevated, default)
│   ├── Interaction Patterns (hover, press, modal transitions)
│   └── Control Archetypes (vintage dial, lux switch)
│
├── 14. Platform Mapping
│   ├── CSS Variables
│   ├── iOS (UIKit semantic colors)
│   ├── Android (Material tokens)
│   └── 3D Engines (materials, lighting)
│
└── 15. Governance
    ├── Versioning (semantic versions)
    ├── Ownership (teams, accountability)
    ├── Documentation (authoritative sources)
    └── Audit (change history)
```

## Token Examples

### Foundation Token
```typescript
{
  "spacing": {
    "md": {
      "value": 16,
      "semantic_name": "card-padding",
      "usage": "internal card spacing",
      "design_intent": "comfortable reading space",
      "extractors": ["claude_vision"],
      "confidence": 0.95
    }
  }
}
```

### Material Token (NEW)
```typescript
{
  "materials": {
    "polished-metal": {
      "material_class": "metal",
      "variant": "polished",
      "gloss": 0.8,
      "reflectivity": 0.6,
      "finish": "gloss",
      "pattern": "brushed-grain",
      "freshness": 0.9,
      "usage": "Premium button surfaces",
      "design_intent": "Evokes precision hardware",
      "extractors": ["claude_vision"]
    }
  }
}
```

### Lighting Token (NEW)
```typescript
{
  "lighting": {
    "lights": [
      {
        "type": "key",
        "color": "#FFF8E7",
        "intensity": 0.8,
        "direction": {"x": 0.5, "y": -0.5, "z": 0.7}
      }
    ],
    "model": "pbr",
    "shadows": {
      "softness": 0.3,
      "contact_intensity": 0.7
    },
    "scene_description": "Soft overhead key light with cool fill"
  }
}
```

### Motion Token (NEW)
```typescript
{
  "motion": {
    "presets": {
      "button-press": {
        "duration": 100,
        "easing": "ease-out-back",
        "press_scale": 0.95,
        "interaction_type": "press",
        "use_case": "Primary button interactions",
        "personality": "Snappy, responsive"
      }
    }
  }
}
```

### Composite Recipe (NEW)
```typescript
{
  "composites": {
    "surfaces": {
      "glassmorphic-card": {
        "background": "rgba(255,255,255,0.1)",
        "backdrop_blur": 10,
        "border": "1px solid rgba(255,255,255,0.18)",
        "shadow": "0 8px 32px rgba(0,0,0,0.1)",
        "material": "frosted-glass",
        "use_case": "Overlay panels, modals",
        "design_intent": "Modern translucent aesthetic with depth"
      }
    }
  }
}
```

## AI Extraction Process

### 1. Image Analysis
AI analyzes UI screenshots/mockups to extract:
- **Visual properties** (colors, sizes, shapes)
- **Material qualities** (glossiness, transparency, texture)
- **Lighting conditions** (direction, intensity, shadows)
- **Motion personality** (inferred from style)
- **Art direction** (technique, mood, treatment)

### 2. Semantic Enrichment
Each token gets:
- **Semantic name** (descriptive, evocative)
- **Usage guidance** (where to apply)
- **Design intent** (WHY this choice)
- **Confidence score** (AI certainty)
- **Source attribution** (which extractor)

### 3. Ontology Mapping
Tokens are classified into:
- **Categories** (material, lighting, motion, etc.)
- **Hierarchies** (elevation levels, typography scales)
- **Relationships** (which tokens work together)
- **Recipes** (pre-built combinations)

## Use Cases

### For Designers
✨ **Understand visual DNA**
- See material properties of reference designs
- Understand lighting setups
- Learn motion personality patterns
- Discover art style classifications

📋 **Documentation**
- Auto-generated design rationale
- Usage guidelines for each token
- Relationship mappings

🎨 **Consistency**
- Ensure material properties match
- Verify lighting consistency
- Check motion personality alignment

### For Developers
🔧 **Implementation**
- Complete CSS/shader parameters
- Animation configurations ready-to-use
- Haptic feedback specifications
- Platform-specific mappings

⚡ **Code Generation**
- Material system setup
- Animation presets
- Composite recipes → components
- Automated theme generation

🧪 **Testing**
- Accessibility validation (WCAG)
- Performance benchmarks
- Cross-platform consistency

### For Design Systems
📦 **Token Management**
- Versioning and governance
- Ownership tracking
- Audit trails
- Change documentation

🔄 **Platform Mapping**
- CSS custom properties
- iOS UIKit tokens
- Android Material tokens
- 3D engine materials

🤖 **Automation**
- Design-to-code pipelines
- Automated documentation
- Token validation
- Cross-reference checking

## Files

### Core System
- `frontend/src/api/comprehensive-types.ts` - Complete type definitions (800 lines)
- `frontend/src/api/types.ts` - Foundation types (existing, enhanced)

### AI Extraction
- `extractors/extractors/ai/comprehensive_prompts.py` - Extraction prompts (650 lines)
- `extractors/extractors/ai/claude_vision_extractor.py` - Claude implementation (enhanced)
- `extractors/extractors/ai/gpt4_vision_extractor.py` - GPT-4 implementation (enhanced)

### Demo & Documentation
- `frontend/src/pages/ComprehensiveTokenDemo.tsx` - Interactive demo (550 lines)
- `frontend/src/pages/TokenEnhancementsDemo.tsx` - Foundation demo (existing)
- `frontend/src/components/ContrastCalculator.tsx` - WCAG tool (existing)
- `frontend/src/components/EnhancedTokenDisplay.tsx` - Token display (existing)

### Backend
- `backend/wcag_contrast.py` - Accessibility calculator (41 tests passing)
- `backend/routers/tokens.py` - REST API endpoints
- `backend/main.py` - FastAPI app with token router

## Statistics

| Metric | Value |
|--------|-------|
| Token Categories | 15 |
| Type Definitions | 100+ |
| Lines of Code (v3.1) | ~2,000 |
| Lines of Code (Total) | ~5,200 |
| Automated Tests | 41 (100% passing) |
| REST API Endpoints | 4 |
| Demo Components | 4 |
| Documentation Files | 5 |

## Roadmap

### v3.2 (Future)
- [ ] Token search and filtering API
- [ ] Batch palette analysis UI
- [ ] Token relationship visualizations
- [ ] Historical tracking (token evolution)
- [ ] Platform-specific exporters

### v3.3 (Future)
- [ ] Material preview renderer
- [ ] Motion playground (interactive)
- [ ] Cinematic camera simulator
- [ ] Composite recipe builder
- [ ] AI-powered token recommendations

### v4.0 (Future)
- [ ] Real-time design token streaming
- [ ] Multi-agent extraction pipeline
- [ ] Cross-design comparison
- [ ] Automated design system generation
- [ ] Figma/Sketch plugin integration

## Getting Started

### View the Demo
```bash
cd frontend
npm install
npm run dev
# Navigate to /comprehensive-demo
```

### Extract Comprehensive Tokens
```python
from extractors.ai.claude_vision_extractor import ClaudeVisionExtractor
from extractors.ai.comprehensive_prompts import CLAUDE_COMPREHENSIVE_PROMPT

extractor = ClaudeVisionExtractor()
tokens = extractor.extract(
    images=[image_array],
    custom_prompt=CLAUDE_COMPREHENSIVE_PROMPT
)
```

### Use in Code
```typescript
import { ComprehensiveDesignTokens } from './api/comprehensive-types';

const tokens: ComprehensiveDesignTokens = await fetchTokens();

// Access material properties
const buttonMaterial = tokens.materials?.["polished-metal"];
console.log(buttonMaterial.gloss); // 0.8

// Access motion presets
const buttonPress = tokens.motion?.presets["button-press"];
animateButton(buttonPress);

// Access composite recipes
const glassCard = tokens.composites?.surfaces["glassmorphic-card"];
applyStyle(glassCard);
```

## Contributing

When adding new token categories:
1. Update `comprehensive-types.ts` with interfaces
2. Extend AI prompts in `comprehensive_prompts.py`
3. Add demo examples in `ComprehensiveTokenDemo.tsx`
4. Document in this file
5. Add tests where applicable

## License

Part of the Copy This project - see root LICENSE.

---

**Version**: 3.1.0
**Last Updated**: 2025-11-07
**Status**: ✅ Complete
**Categories**: 15
**Tokens**: 100+
**Tests**: 41 passing

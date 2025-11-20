# Token Ontology & Taxonomy Reference

**Formal Structure: Design Language Classification & Narrative Extraction**

Version: 3.1
Last Updated: 2025-11-11
Status: Ontological Framework + "Analog Whimsy Systems" Reference

---

## Overview

This document defines the **formal ontological structure** for design token classification, enabling extractors to produce taxonomically deep outputs that capture not just technical tokens, but complete **design language narratives**.

**Purpose**: Transform raw visual data → Technical tokens → **Design Language Taxonomy**

**Example**: "Analog Whimsy Systems" - A complete design language extracted from retro-futurist UI mockups, demonstrating the full depth of taxonomic analysis.

---

## Table of Contents

1. [Ontological Framework](#ontological-framework)
2. [Structural Taxonomy](#structural-taxonomy)
3. [Visual Grammar](#visual-grammar)
4. [Interaction Semantics](#interaction-semantics)
5. [Thematic & Symbolic Layer](#thematic-symbolic-layer)
6. [Systemic Design Principles](#systemic-design-principles)
7. [Design Language Codification](#design-language-codification)
8. [Extractor Mapping](#extractor-mapping)

---

## Ontological Framework

### Seven Layers of Design Language

```
Design Language Ontology
├─ I. Structural Taxonomy
│  ├─ Compositional Logic
│  ├─ Component Families
│  ├─ Conduits & Flow
│  └─ Spatial Hierarchy
│
├─ II. Visual Grammar
│  ├─ Form Language
│  ├─ Color System
│  ├─ Material & Texture
│  └─ Typographic Voice
│
├─ III. Interaction Semantics
│  ├─ Control Affordances
│  ├─ Feedback Patterns
│  ├─ Spatial Hierarchy
│  └─ Temporal Dynamics
│
├─ IV. Thematic & Symbolic Layer
│  ├─ Stylistic Lineage
│  ├─ Cultural References
│  ├─ Narrative Archetype
│  └─ Emotional Tone
│
├─ V. Systemic Design Principles
│  ├─ Function-through-Form
│  ├─ Color-driven Cognition
│  ├─ Layered Legibility
│  └─ Whimsy as UX Strategy
│
├─ VI. Taxonomic Summary
│  └─ Design Language Matrix
│
└─ VII. Design Language Codification
   ├─ Language Name
   ├─ Definition
   ├─ Contrast Analysis
   └─ Generative Rules
```

---

## Case Study: "Analog Whimsy Systems"

### Context

**Source Images**: Retro-futurist audio plugin UI mockups (Midjourney-generated)
**Extractors Used**: All 30+ extractors (Foundation, Component, Visual DNA, AI Enhancement)
**Output**: Complete design language taxonomy

---

## I. Structural Taxonomy

### Compositional Logic

**Definition**: The underlying organizational principles governing spatial relationships.

**Ontology**:
```typescript
interface CompositionOntology {
  layout_paradigm: 'grid-based' | 'grid-less modular' | 'organic' | 'asymmetric';
  flow_direction: 'vertical stacking' | 'horizontal flow' | 'lateral flow' | 'radial';
  architecture_style: 'wall-integrated' | 'floating' | 'layered' | 'nested';
  hierarchy_method: 'size-based' | 'color zones' | 'depth-based' | 'control clustering';
}
```

**Analog Whimsy Systems Example**:
```json
{
  "composition": {
    "layout_paradigm": "grid-less modular",
    "flow_direction": "vertical stacking with lateral flow",
    "architecture_style": "wall-integrated",
    "hierarchy_method": "color zones and control group clustering",
    "description": "Components float within bounded regions without strict grid alignment, suggesting analog flexibility over digital precision"
  }
}
```

**Extracted By**:
- `SpacingExtractor` → Detects grid vs. modular composition
- `ComponentTokenExtractor` → Identifies component clustering
- `ZIndexExtractor` → Determines depth hierarchy
- **AI Enhancement (GPT-4V)** → Narrative description

---

### Component Families

**Definition**: Hierarchical classification of UI elements by function and form.

**Ontology**:
```typescript
interface ComponentFamilyOntology {
  primary_panels: {
    form: string;
    nesting_depth: number;
    visual_treatment: string;
  };
  sub_modules: {
    scope: 'specific operational' | 'general utility' | 'informational';
    style: 'inset' | 'raised' | 'flush';
  };
  conduits: {
    function: 'visual connectors' | 'data flow' | 'routing';
    symbolism: string;
  };
  indicators: {
    types: string[];  // ['lights', 'meters', 'analog displays']
    redundancy: 'single' | 'dual' | 'triple';
  };
}
```

**Analog Whimsy Systems Example**:
```json
{
  "component_families": {
    "primary_panels": {
      "form": "rounded edges, enamel-like surface",
      "nesting": "multiple subpanels per primary panel",
      "visual_treatment": "glossy surface with metallic trim"
    },
    "sub_modules": {
      "scope": "specific operational (filter, envelope, LFO)",
      "style": "inset with shadowed borders"
    },
    "conduits": {
      "function": "visual connectors between modules",
      "symbolism": "evoke cables or pneumatic tubes (data as physical substance)"
    },
    "indicators": {
      "types": ["LED lights", "VU meters", "analog needle gauges"],
      "redundancy": "dual feedback (visual + numerical)"
    }
  }
}
```

**Extracted By**:
- `ComponentTokenExtractor` → Component variants and hierarchy
- `AudioPluginComponentExtractor` → Knobs, sliders, meters, indicators
- `BorderExtractor` + `ShadowExtractor` → Visual treatment (inset, raised)
- `MaterialExtractor` → Surface properties (glossy, enamel, metallic trim)

---

## II. Visual Grammar

### Form Language

**Definition**: The geometric vocabulary and silhouette patterns that define the design's visual identity.

**Ontology**:
```typescript
interface FormLanguageOntology {
  geometry: 'rectilinear' | 'soft industrial' | 'organic' | 'geometric abstraction';
  silhouette: string;  // Descriptive
  era_reference: string;  // Art historical era
  dimensionality: '2D flat' | 'pseudo-3D' | '3D volumetric';
  density: 'minimal' | 'moderate' | 'dense' | 'micro-mechanical';
}
```

**Analog Whimsy Systems Example**:
```json
{
  "form_language": {
    "geometry": "soft industrial",
    "silhouette": "rounded rectangles, cylindrical housings, bulbous protrusions (knobs, button caps)",
    "era_reference": "mid-century appliance design (1950s Braun, NASA control panels)",
    "dimensionality": "pseudo-3D (tactile skeuomorphism without full 3D rendering)",
    "density": "micro-mechanical (dense packing of controls within bounded regions)"
  }
}
```

**Extracted By**:
- `BorderRadiusExtractor` → Rounded geometry detection
- `ShadowExtractor` → Dimensionality (pseudo-3D depth)
- `ArtisticExtractor` → Era classification (mid-century, retro-futurism)
- **AI Enhancement (CLIP)** → Style classification ("soft industrial", "techno-botanical")

---

### Color System

**Definition**: The palette logic, semantic mappings, and function-to-hue relationships.

**Ontology**:
```typescript
interface ColorSystemOntology {
  palette_description: string;  // e.g., "high-saturation pastel"
  dominant_hues: string[];
  base_tones: string[];  // Structural colors
  function_mapping: {
    [function: string]: string;  // e.g., "action" → "warm colors"
  };
  highlight_logic: string;  // How highlights/accents are applied
}
```

**Analog Whimsy Systems Example**:
```json
{
  "color_system": {
    "palette_description": "high-saturation pastel (playful yet legible)",
    "dominant_hues": ["teal (#45B0A6)", "coral (#F56A5D)", "canary yellow (#FFD85C)", "mint green (#E6F4EE)"],
    "base_tones": ["cream (#FDF7EE)", "off-white"],
    "function_mapping": {
      "action_or_control": "warm colors (red, orange, yellow)",
      "data_or_feedback": "cool colors (teal, blue, green)",
      "structural_surfaces": "neutral tones (cream, white)"
    },
    "highlight_logic": "metallic specular highlights + glossy reflections suggest physical depth"
  }
}
```

**Extracted By**:
- `ColorExtractor` → Palette extraction (K-means clustering in LAB space)
- `StyleMoodExtractor` → Aesthetic classification (playful, legible)
- `MaterialExtractor` → Metallic highlights, glossy finish
- **Storytelling Framework** → Semantic naming ("Sunset Ember", "Molten Copper")

---

### Material & Texture

**Definition**: Surface properties, finishes, and tactile qualities.

**Ontology**:
```typescript
interface MaterialTextureOntology {
  materials: {
    [name: string]: {
      material_class: 'plastic' | 'metal' | 'glass' | 'wood' | 'ceramic';
      variant: string;
      optical: {
        gloss: number;  // 0-1
        reflectivity: number;
        transmission: number;
      };
      tactile: {
        friction: number;
        warmth: number;
        grain: number;
      };
      finish: 'matte' | 'satin' | 'gloss' | 'mirror';
    };
  };
  textures: {
    [name: string]: {
      pattern: 'smooth' | 'grained' | 'brushed' | 'etched';
      scale: 'fine' | 'medium' | 'coarse';
    };
  };
}
```

**Analog Whimsy Systems Example**:
```json
{
  "materials": {
    "enamel-gloss": {
      "material_class": "plastic",
      "variant": "vintage bakelite or glossy enamel",
      "optical": {
        "gloss": 0.7,
        "reflectivity": 0.4,
        "transmission": 0.0
      },
      "tactile": {
        "friction": 0.5,
        "warmth": 0.6,
        "grain": 0.1
      },
      "finish": "gloss",
      "era": "mid-century consumer electronics"
    },
    "metallic-trim": {
      "material_class": "metal",
      "variant": "brass, copper, or brushed aluminum",
      "optical": {
        "gloss": 0.6,
        "reflectivity": 0.7,
        "transmission": 0.0
      },
      "tactile": {
        "friction": 0.4,
        "warmth": 0.3,
        "grain": 0.2
      },
      "finish": "satin",
      "function": "structural accents, bezels, screw heads"
    }
  }
}
```

**Extracted By**:
- `MaterialExtractor` → Surface properties (gloss, reflectivity, tactile)
- `LightingExtractor` → Specular highlights (metallic reflections)
- **AI Enhancement (Claude Vision)** → Material classification ("vintage bakelite", "mid-century")

---

## III. Interaction Semantics

### Control Affordances

**Definition**: How interface elements signal their interactive possibilities.

**Ontology**:
```typescript
interface ControlAffordanceOntology {
  primary_metaphor: 'analog' | 'digital' | 'hybrid';
  control_types: {
    [type: string]: {
      affordance: 'rotary' | 'linear' | 'binary' | 'touch';
      tactility: 'explicit' | 'subtle' | 'ambiguous';
    };
  };
  gesture_paradigm: 'mechanical' | 'touchscreen' | 'gestural' | 'hybrid';
  feedback_pattern: {
    visual: string;
    audio: string;
    haptic: string;
  };
}
```

**Analog Whimsy Systems Example**:
```json
{
  "control_affordances": {
    "primary_metaphor": "analog (knobs, sliders, switches)",
    "control_types": {
      "knobs": {
        "affordance": "rotary (360° continuous or limited)",
        "tactility": "explicit (visually 3D, shadows suggest graspability)"
      },
      "sliders": {
        "affordance": "linear (vertical or horizontal travel)",
        "tactility": "explicit (track + thumb visible)"
      },
      "switches": {
        "affordance": "binary (toggle on/off)",
        "tactility": "explicit (physical switch metaphor)"
      }
    },
    "gesture_paradigm": "mechanical, not touchscreen (skeuomorphic fidelity)",
    "feedback_pattern": {
      "visual": "immediate cause-effect (knob rotation → needle movement)",
      "audio": "implied (click, snap detents)",
      "haptic": "implied tactile resistance"
    },
    "redundancy": "tactile feedback duplicated across visual (meters) and numerical (screens)"
  }
}
```

**Extracted By**:
- `AudioPluginComponentExtractor` → Knob/slider/switch detection
- `ComponentTokenExtractor` → Interactive state variants
- `StateLayerExtractor` → Hover/focus/active states
- `ArtisticExtractor` → Skeuomorphic fidelity classification

---

### Spatial Hierarchy

**Definition**: How depth, layering, and z-axis positioning structure information architecture.

**Ontology**:
```typescript
interface SpatialHierarchyOntology {
  depth_strategy: 'flat' | 'layered' | 'nested' | 'parallax';
  hierarchy_levels: {
    [level: string]: {
      z_index: number;
      visual_cues: string[];  // ['shadow', 'blur', 'opacity']
      semantic_role: string;
    };
  };
  information_flow: 'top-down' | 'center-out' | 'left-right' | 'macro-to-micro';
}
```

**Analog Whimsy Systems Example**:
```json
{
  "spatial_hierarchy": {
    "depth_strategy": "layered (physical depth as information architecture)",
    "hierarchy_levels": {
      "macro": {
        "z_index": 0,
        "visual_cues": ["large panels", "bold color zones"],
        "semantic_role": "operational categories (filter, modulation)"
      },
      "meso": {
        "z_index": 1,
        "visual_cues": ["sub-modules", "inset panels", "shadows"],
        "semantic_role": "specific functions (cutoff, resonance)"
      },
      "micro": {
        "z_index": 2,
        "visual_cues": ["individual controls", "lights", "labels"],
        "semantic_role": "parameter adjustment and status"
      }
    },
    "information_flow": "macro-to-micro (large categories → specific controls → feedback)"
  }
}
```

**Extracted By**:
- `ZIndexExtractor` → Layer hierarchy detection
- `ShadowExtractor` → Depth cues (shadows, insets)
- `SpacingExtractor` → Clustering and grouping
- **AI Enhancement** → Semantic role classification

---

## IV. Thematic & Symbolic Layer

### Stylistic Lineage

**Definition**: Art historical, design historical, and cultural influences.

**Ontology**:
```typescript
interface StylisticLineageOntology {
  primary_influences: {
    era: string;
    movement: string;
    key_references: string[];
  }[];
  hybrid_synthesis: string;  // How influences merge
  contemporary_context: string;
}
```

**Analog Whimsy Systems Example**:
```json
{
  "stylistic_lineage": [
    {
      "era": "1960s-1970s Space Age",
      "movement": "Retro-futurism",
      "key_references": ["NASA control panels", "Sputnik aesthetics", "early synthesizers (Moog, ARP)"]
    },
    {
      "era": "1950s-1960s Consumer Electronics",
      "movement": "Mid-century Modernism",
      "key_references": ["Braun appliances (Dieter Rams)", "Olivetti typewriters", "Fisher-Price toys"]
    },
    {
      "era": "Contemporary Digital",
      "movement": "Techno-botanical Surrealism",
      "key_references": ["Plant integration (organic meets mechanical)", "kawaii aesthetics (approachability)"]
    }
  ],
  "hybrid_synthesis": "Merges analog computing + sound synthesis + alchemical instrumentation",
  "contemporary_context": "Neo-craft modernism (reaction against minimalist digitalism)"
}
```

**Extracted By**:
- `ArtisticExtractor` → Style classification (retro-futurism, mid-century)
- **AI Enhancement (CLIP)** → Zero-shot style matching
- **AI Enhancement (GPT-4V/Claude)** → Art historical analysis and narrative synthesis

---

### Narrative Archetype

**Definition**: The fictional context, storytelling framework, and emotional setting.

**Ontology**:
```typescript
interface NarrativeArchetypeOntology {
  setting: string;  // Fictional world/context
  synthesis: string;  // What disciplines merge
  tone: string[];  // Emotional qualities
  user_journey: {
    entry_point: string;
    exploration_pattern: string;
    mastery_endpoint: string;
  };
}
```

**Analog Whimsy Systems Example**:
```json
{
  "narrative_archetype": {
    "setting": "fictional laboratory ecosystem (mad scientist meets sound designer)",
    "synthesis": "analog computing + sound synthesis + alchemical instrumentation + botanical cultivation",
    "tone": ["whimsical", "exploratory", "deeply humanistic", "optimistic"],
    "user_journey": {
      "entry_point": "Curiosity (colorful, inviting interface)",
      "exploration_pattern": "Tactile discovery (twist knobs, flip switches, observe meters)",
      "mastery_endpoint": "Fluency (mental model of sound-as-substance)"
    },
    "cultural_positioning": "Stands against minimalist digitalism by celebrating visible systems as artifacts of curiosity"
  }
}
```

**Extracted By**:
- `StyleMoodExtractor` → Aesthetic keywords (whimsical, exploratory)
- `EnvironmentExtractor` → Setting classification (laboratory, studio)
- **AI Enhancement (Claude Vision)** → Narrative analysis and cultural positioning

---

## V. Systemic Design Principles

### Design Principles as Generative Rules

**Definition**: The underlying rules that govern design decisions.

**Ontology**:
```typescript
interface DesignPrincipleOntology {
  principles: {
    name: string;
    rule: string;
    rationale: string;
    visual_manifestation: string;
  }[];
}
```

**Analog Whimsy Systems Example**:
```json
{
  "design_principles": [
    {
      "name": "Function-through-Form",
      "rule": "Make affordances explicit (no hidden gestures)",
      "rationale": "Reduce cognitive load by making interactive elements visually obvious",
      "visual_manifestation": "3D buttons, shadows, glossy surfaces suggest graspability"
    },
    {
      "name": "Color-driven Cognition",
      "rule": "Palette structures cognitive hierarchy (warm=action, cool=feedback, neutral=structure)",
      "rationale": "Leverage pre-attentive processing for faster comprehension",
      "visual_manifestation": "Orange knobs (action), teal meters (feedback), cream panels (structure)"
    },
    {
      "name": "Layered Legibility",
      "rule": "Material physics as information architecture (depth = importance)",
      "rationale": "Use pseudo-3D depth to encode semantic hierarchy",
      "visual_manifestation": "Primary panels raised, sub-modules inset, controls on top"
    },
    {
      "name": "Whimsy as UX Strategy",
      "rule": "Delight invites exploration (non-threatening complexity)",
      "rationale": "Lower psychological barriers to mastery via playful aesthetics",
      "visual_manifestation": "Pastel colors, rounded forms, toy-like quality"
    }
  ]
}
```

**Extracted By**:
- `ShadowExtractor` + `MaterialExtractor` → Physical depth detection
- `ColorExtractor` + `StyleMoodExtractor` → Color-cognition mapping
- **AI Enhancement** → Principle extraction and rationale generation

---

## VI. Taxonomic Summary

### Design Language Matrix

**Consolidated Overview Table**:

| Dimension | Classification | Visual Markers | Extractor Source |
|-----------|----------------|----------------|------------------|
| **Composition** | Grid-less modular | Clustered controls, flexible spacing | SpacingExtractor, ComponentTokenExtractor |
| **Form** | Soft industrial | Rounded rectangles, cylindrical housings | BorderRadiusExtractor, ArtisticExtractor |
| **Color** | High-saturation pastel | Teal, coral, lemon, mint | ColorExtractor, StyleMoodExtractor |
| **Materials** | Enamel gloss + metallic trim | Glossy plastic (0.7 gloss), brass/copper accents | MaterialExtractor, LightingExtractor |
| **Controls** | Analog tactile | Knobs, sliders, switches (explicit affordances) | AudioPluginComponentExtractor |
| **Hierarchy** | Macro-to-micro depth | Large panels → sub-modules → controls | ZIndexExtractor, ShadowExtractor |
| **Style** | Retro-futurism + mid-century | 1960s NASA + 1950s Braun + techno-botanical | ArtisticExtractor, AI Enhancement (CLIP) |
| **Narrative** | Laboratory ecosystem | Mad scientist + sound designer + alchemist | AI Enhancement (GPT-4V/Claude) |
| **Principles** | Explicit affordances, color cognition, layered legibility, whimsy | 3D forms, warm=action/cool=feedback, depth=hierarchy | Multi-extractor synthesis |

---

## VII. Design Language Codification

### Language Name

**Format**: `[Aesthetic Quality] + [Functional Domain] + [Systems/Architecture]`

**Analog Whimsy Systems Example**:
```json
{
  "design_language_name": "Analog Whimsy Systems",
  "name_breakdown": {
    "analog": "Continuous, tactile, physical metaphor (vs. digital binary)",
    "whimsy": "Playful, non-threatening, exploratory (aesthetic quality)",
    "systems": "Interconnected, modular, operational (functional architecture)"
  }
}
```

---

### Design Language Definition

**Format**: One-sentence distillation of essence + expanded definition.

**Analog Whimsy Systems Example**:
```json
{
  "definition_short": "Multi-sensory interface system merging retro instrumentality, ecological aesthetics, and human-centered tactility.",
  "definition_expanded": "Analog Whimsy Systems is a design language that synthesizes mid-century industrial aesthetics, space-age optimism, and contemporary ecological sensibility into a tactile, exploratory interface paradigm. It celebrates visible systems as artifacts of curiosity, positioning complexity as invitation rather than barrier through playful color, explicit affordances, and layered information architecture."
}
```

---

### Contrast Analysis

**Format**: What this design language stands **against** (defines by opposition).

**Analog Whimsy Systems Example**:
```json
{
  "contrast_analysis": {
    "opposes": [
      {
        "paradigm": "Minimalist Digitalism",
        "rejection": "Hidden gestures, flat UI, monochrome palettes, abstract iconography",
        "counterproposal": "Explicit affordances, 3D depth, saturated pastels, representational controls"
      },
      {
        "paradigm": "Enterprise Sobriety",
        "rejection": "Corporate blue/gray, rectilinear forms, information density prioritized over delight",
        "counterproposal": "Playful color diversity, soft industrial forms, whimsy as engagement strategy"
      },
      {
        "paradigm": "Brutalist Austerity",
        "rejection": "Raw, unfinished aesthetics, harsh contrast, aggressive typography",
        "counterproposal": "Glossy, finished surfaces, approachable contrast, friendly typography"
      }
    ]
  }
}
```

---

## Extractor Mapping

### Ontology Layer → Extractor Coverage

| Ontology Layer | Extractors Used | Token Types Produced | AI Enhancement |
|----------------|-----------------|----------------------|----------------|
| **I. Structural Taxonomy** | SpacingExtractor, ComponentTokenExtractor, ZIndexExtractor | `spacing`, `grid`, `zindex`, `button`, `input`, `card` | GPT-4V (composition narrative) |
| **II. Visual Grammar** | ColorExtractor, BorderRadiusExtractor, MaterialExtractor, TypographyExtractor | `palette`, `radius`, `materials`, `typography` | CLIP (style classification), Claude (material naming) |
| **III. Interaction Semantics** | AudioPluginComponentExtractor, StateLayerExtractor, ComponentTokenExtractor | `audio_plugin`, `state_layers`, `button` states | GPT-4V (affordance analysis) |
| **IV. Thematic & Symbolic** | ArtisticExtractor, EnvironmentExtractor, StyleMoodExtractor | `art_style`, `environment`, `style_mood`, `emotional` | CLIP (style matching), GPT-4V/Claude (narrative synthesis) |
| **V. Systemic Principles** | All extractors (synthesis) | Complete token set | GPT-4V/Claude (principle extraction, rationale) |
| **VI. Taxonomic Summary** | All extractors | Complete token set + summary table | AI synthesis |
| **VII. Design Language Codification** | N/A (AI synthesis layer) | Design language name, definition, contrast | GPT-4V/Claude (linguistic synthesis) |

---

## Implementation Guide

### How Extractors Produce Ontological Outputs

**Current**: Extractors produce technical tokens
```json
{
  "palette": {
    "primary": "#F56A5D",
    "secondary": "#45B0A6"
  },
  "materials": {
    "gloss": 0.7,
    "material_class": "plastic"
  }
}
```

**Future (Ontological)**: Extractors produce taxonomic narratives
```json
{
  "palette": {
    "primary": {
      "hex": "#F56A5D",
      "name": "Coral Ember",
      "semantic_role": "Action & control signaling",
      "function_mapping": "Warm colors encode interactive affordances",
      "cultural_reference": "1950s Formica countertops",
      "emotional_quality": "Energetic, inviting, non-threatening"
    }
  },
  "materials": {
    "enamel-gloss": {
      "gloss": 0.7,
      "material_class": "plastic",
      "variant": "Vintage bakelite",
      "era": "Mid-century consumer electronics",
      "tactile_metaphor": "Smooth, warm to touch",
      "design_principle": "Tactile skeuomorphism (physical depth suggests graspability)"
    }
  },
  "design_language": {
    "name": "Analog Whimsy Systems",
    "definition": "Multi-sensory interface system merging retro instrumentality, ecological aesthetics, and human-centered tactility",
    "stylistic_lineage": ["Retro-futurism (1960s NASA)", "Mid-century modernism (Braun)", "Techno-botanical surrealism"],
    "design_principles": [
      "Function-through-form (explicit affordances)",
      "Color-driven cognition (warm=action, cool=feedback)",
      "Layered legibility (depth=hierarchy)",
      "Whimsy as UX strategy (delight invites exploration)"
    ]
  }
}
```

---

## Ontology Enums & Classifications

### Art Historical Eras
```typescript
enum ArtHistoricalEra {
  Ancient = 'ancient',
  Medieval = 'medieval',
  Renaissance = 'renaissance',
  Baroque = 'baroque',
  Neoclassical = 'neoclassical',
  Romantic = 'romantic',
  Impressionist = 'impressionist',
  ModernEarly = 'modern-early',  // 1900-1945
  ModernMid = 'modern-mid',      // 1945-1970 (Bauhaus, International Style)
  Postmodern = 'postmodern',     // 1970-2000
  Contemporary = 'contemporary'   // 2000+
}
```

### Design Movements
```typescript
enum DesignMovement {
  ArtDeco = 'art-deco',
  Bauhaus = 'bauhaus',
  MidCenturyModern = 'mid-century-modern',
  Swiss = 'swiss-international',
  Memphis = 'memphis',
  Brutalism = 'brutalism',
  Minimalism = 'minimalism',
  RetroFuturism = 'retro-futurism',
  Skeuomorphism = 'skeuomorphism',
  FlatDesign = 'flat-design',
  MaterialDesign = 'material-design',
  Neumorphism = 'neumorphism',
  Glassmorphism = 'glassmorphism'
}
```

### Material Classes
```typescript
enum MaterialClass {
  Plastic = 'plastic',
  Metal = 'metal',
  Glass = 'glass',
  Wood = 'wood',
  Ceramic = 'ceramic',
  Fabric = 'fabric',
  Paper = 'paper',
  Stone = 'stone',
  Concrete = 'concrete',
  Leather = 'leather',
  Rubber = 'rubber'
}
```

### Interaction Metaphors
```typescript
enum InteractionMetaphor {
  Analog = 'analog',         // Knobs, sliders, physical controls
  Digital = 'digital',       // Buttons, toggles, binary states
  Gestural = 'gestural',     // Swipes, pinches, gestures
  Voice = 'voice',           // Voice commands
  Haptic = 'haptic',         // Touch, vibration feedback
  Spatial = 'spatial',       // 3D/AR/VR interactions
}
```

---

## Related Documentation

- [Complete Token-Extractor Mapping](COMPLETE_TOKEN_EXTRACTOR_MAPPING.md) - Technical mapping with CV libraries and AI models
- [Extractor-to-Token Type Table](EXTRACTOR_TO_TOKEN_TYPE_TABLE.md) - Quick reference table
- [Generator Export Guide](GENERATOR_EXPORT_GUIDE.md) - How to transform tokens into code
- [Visual DNA Deep Dive](VISUAL_DNA_DEEP_DIVE.md) - Material, lighting, environment extraction
- [Storytelling Framework](STORYTELLING_FRAMEWORK.md) - Token naming and narratives

---

**Last Updated**: 2025-11-11
**Version**: 3.1
**Status**: Ontological Framework + Analog Whimsy Systems Reference

---

## Appendix: Complete "Analog Whimsy Systems" Taxonomy

See the user-provided reference document for the full 7-layer taxonomy that demonstrates the complete depth of ontological analysis possible with the extractor system.

**Key Insight**: This ontology transforms raw pixels → technical tokens → **design language narratives** that capture not just "what" but "why" and "how" the design communicates.

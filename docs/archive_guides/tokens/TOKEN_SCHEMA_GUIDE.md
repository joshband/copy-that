# Token Schema Guide

**Complete Design Token Reference with Visual Examples**

Version: 3.1
Last Updated: 2025-11-11
Status: Comprehensive Reference

---

## Table of Contents

1. [Understanding Token Schemas](#understanding-token-schemas)
2. [Foundation Tokens](#foundation-tokens)
3. [Semantic Tokens](#semantic-tokens)
4. [Component Tokens](#component-tokens)
5. [Visual DNA Tokens](#visual-dna-tokens)
6. [Advanced & Perceptual Tokens](#advanced--perceptual-tokens)
7. [Metadata & Governance](#metadata--governance)
8. [Schema Evolution & Versioning](#schema-evolution--versioning)

---

## Understanding Token Schemas

### What is a Design Token Schema?

A **design token schema** is a structured data format that defines:
- **Token properties** - What data each token contains
- **Token relationships** - How tokens reference each other
- **Token metadata** - Confidence, extractors, design intent
- **Validation rules** - Type safety, constraints, required fields

### Schema Formats

Copy This supports multiple schema formats:

```typescript
// TypeScript (frontend/src/api/types.ts)
interface ColorToken {
  hex: string
  extractors?: string[]
  name?: string
  confidence?: number
}

// Python (extractors/extractors/visual_dna_schema.py)
class ColorToken(TypedDict, total=False):
    hex: str
    extractors: List[str]
    name: str
    confidence: float

// JSON Schema (generators/src/schema.ts)
const ColorTokenSchema = z.object({
  hex: z.string(),
  extractors: z.array(z.string()).optional(),
  name: z.string().optional(),
  confidence: z.number().min(0).max(1).optional()
})
```

### Token Hierarchy

```
Design Tokens
├── Foundation (Primitives)
│   ├── Color Palette & Scales
│   ├── Typography System
│   ├── Spacing Scale
│   ├── Shadow & Elevation
│   ├── Border Radius
│   ├── Animation Timing
│   └── Grid & Breakpoints
│
├── Semantic (Context-Aware)
│   ├── Brand Colors
│   ├── UI Surface Colors
│   ├── Feedback Colors
│   ├── Text Colors
│   └── Component Colors
│
├── Component (Compositional)
│   ├── Button Tokens
│   ├── Input Tokens
│   ├── Card Tokens
│   ├── Navigation Tokens
│   └── Audio Plugin Tokens
│
├── Visual DNA (Perceptual)
│   ├── Material Properties
│   ├── Lighting Characteristics
│   ├── Environmental Context
│   ├── Artistic Style
│   └── Emotional Qualities
│
└── Advanced (Enhanced)
    ├── Opacity & Transparency
    ├── Transitions & Motion
    ├── Blur & Filters
    ├── Gradients
    └── Platform-Specific
```

---

## Foundation Tokens

### 1. Color Palette Tokens

**Purpose**: Core color roles that define a design's visual identity

**Schema**:
```typescript
interface ColorPaletteToken {
  // Core
  hex: string                    // #F15925

  // AI-Enhanced Metadata
  name?: string                  // "Vibrant Orange"
  semantic_name?: string         // "Sunset Ember"
  description?: string           // Detailed color description

  // Design Context
  design_intent?: string         // "Energetic, attention-grabbing"
  usage?: string                 // "Primary CTAs, brand highlights"
  use_case?: string[]            // ["buttons", "links", "icons"]

  // Extraction Metadata
  extractors?: string[]          // ["opencv_cv", "gpt4_vision"]
  confidence?: number            // 0.95 (0-1)

  // Accessibility
  accessibility?: {
    contrast_ratio?: number      // 4.52
    wcag_level?: "AAA" | "AA" | "AA Large" | "Fail"
    recommendations?: string     // "Use with white text"
    cvd_safe?: boolean          // Color vision deficiency safe
  }

  // Relationships
  related_colors?: string[]      // ["secondary", "accent"]
  complements?: string[]         // ["#4ECDC4"]

  // Storytelling
  emotional_qualities?: string[] // ["warm", "energetic", "vintage"]
  cultural_associations?: string // "Western: excitement, Asia: prosperity"
}
```

**Visual Example**:
```
┌─────────────────────────────────────────────────┐
│ Molten Copper (#F15925)                         │
│ ███████████████████████████████████████████     │
│                                                  │
│ "Your brand's heartbeat"                        │
│                                                  │
│ Design Intent: Energetic and attention-grabbing │
│ Usage: Primary CTAs, interactive elements       │
│ Extractors: CV + GPT-4V + Claude (98% conf.)    │
│ WCAG: AA ✓ (4.52:1 on white)                   │
│                                                  │
│ Tags: warm • energetic • vintage • 70s analog   │
└─────────────────────────────────────────────────┘
```

**Complete Example**:
```json
{
  "palette": {
    "primary": {
      "hex": "#F15925",
      "name": "Vibrant Orange",
      "semantic_name": "Molten Copper",
      "description": "A warm, saturated orange reminiscent of vintage audio equipment and 1970s industrial design",
      "design_intent": "Energetic and attention-grabbing, evoking warmth and enthusiasm",
      "usage": "Primary CTAs, brand highlights, interactive elements requiring user attention",
      "use_case": ["buttons", "links", "active_states", "icons", "highlights"],
      "extractors": ["opencv_cv", "gpt4_vision", "claude_vision"],
      "confidence": 0.98,
      "accessibility": {
        "contrast_ratio": 4.52,
        "wcag_level": "AA",
        "recommendations": "Use with white or light text for accessibility compliance",
        "cvd_safe": true
      },
      "related_colors": ["secondary", "accent"],
      "complements": ["#4ECDC4"],
      "emotional_qualities": ["warm", "energetic", "vintage", "playful", "technical"],
      "cultural_associations": "Western: excitement and energy, Asian: prosperity and success"
    }
  }
}
```

### 2. Primitive Color Scales

**Purpose**: 10-shade color ramps (50-900) generated from base colors

**Schema**:
```typescript
interface ColorScale {
  "50": string    // Lightest (95% lightness)
  "100": string
  "200": string
  "300": string
  "400": string
  "500": string   // Base color (unchanged)
  "600": string
  "700": string
  "800": string
  "900": string   // Darkest (10% lightness)
}

interface PrimitiveColors {
  [colorFamily: string]: ColorScale
}
```

**Generation Method**: HSL interpolation maintaining hue and saturation

**Visual Example**:
```
Orange Scale
50  ▓ #FFF5F0  Whisper
100 ▓ #FFE8DC  Frost
200 ▓ #FFD1B8  Cloud
300 ▓ #FFB994  Breeze
400 ▓ #FFA270  Glow
500 ▓ #F15925  Base (Molten Copper)
600 ▓ #C14710  Ember
700 ▓ #91350C  Charcoal
800 ▓ #612308  Shadow
900 ▓ #311204  Midnight
```

**Example**:
```json
{
  "primitive": {
    "orange": {
      "50": "#FFF5F0",
      "100": "#FFE8DC",
      "200": "#FFD1B8",
      "300": "#FFB994",
      "400": "#FFA270",
      "500": "#F15925",
      "600": "#C14710",
      "700": "#91350C",
      "800": "#612308",
      "900": "#311204"
    }
  }
}
```

### 3. Typography Tokens

**Purpose**: Font system defining hierarchy, readability, and brand voice

**Schema**:
```typescript
interface TypographyToken {
  // Basic
  family: string              // "Inter, system-ui, sans-serif"
  weights: number[]           // [400, 600, 700]

  // Extended Scale
  scale?: {
    [size: string]: {
      fontSize: string        // "48px" | "3rem"
      lineHeight: string      // "1.2" | "56px"
      letterSpacing?: string  // "-0.02em"
      fontWeight?: number     // 700

      // Semantic Naming
      name?: string           // "Hero Statement"
      technical_name?: string // "type-display-xl"

      // Usage Guidance
      hierarchy?: number      // 1-7 (1 = most prominent)
      usage?: string          // "Page titles, hero sections"
      wcag_notes?: string     // "1.5 line-height for readability"
    }
  }

  // Platform Mapping
  platform_fallbacks?: {
    web: string               // "Inter, system-ui, sans-serif"
    ios: string               // "SF Pro Display"
    android: string           // "Roboto"
    juce: string              // "Arial"
  }

  // Character
  character?: string          // "Clean, modern, highly readable"
  mood?: string[]            // ["professional", "friendly", "technical"]
}
```

**Visual Example**:
```
TYPOGRAPHY HIERARCHY

Display XL (48px / 1.2 / -0.02em / 700)
  "Hero Statement"
  Used for: Page titles, hero sections, marketing headlines

Heading L (32px / 1.3 / 0 / 600)
  "Section Commander"
  Used for: Section headers, major divisions

Body M (16px / 1.5 / 0 / 400)
  "Comfortable Read"
  Used for: Paragraphs, long-form content
  WCAG: 1.5 line-height improves dyslexia readability

Caption S (12px / 1.4 / 0 / 400)
  "Fine Print Friendly"
  Used for: Metadata, timestamps, secondary info
```

**Complete Example**:
```json
{
  "typography": {
    "family": "Inter, system-ui, sans-serif",
    "weights": [400, 600, 700],
    "scale": {
      "display_xl": {
        "fontSize": "48px",
        "lineHeight": "1.2",
        "letterSpacing": "-0.02em",
        "fontWeight": 700,
        "name": "Hero Statement",
        "technical_name": "type-display-xl",
        "hierarchy": 1,
        "usage": "Page titles, hero sections, marketing headlines",
        "wcag_notes": "Tight tracking acceptable at large sizes"
      },
      "body_md": {
        "fontSize": "16px",
        "lineHeight": "1.5",
        "fontWeight": 400,
        "name": "Comfortable Read",
        "technical_name": "type-body-md",
        "hierarchy": 5,
        "usage": "Paragraphs, long-form content, optimal 60-80 char lines",
        "wcag_notes": "1.5 minimum line-height recommended for readability (WCAG 2.1)"
      }
    },
    "platform_fallbacks": {
      "web": "Inter, system-ui, sans-serif",
      "ios": "SF Pro Display",
      "android": "Roboto",
      "juce": "Arial"
    },
    "character": "Clean, neutral, highly readable, tech-forward",
    "mood": ["professional", "modern", "approachable"]
  }
}
```

### 4. Spacing Scale Tokens

**Purpose**: Consistent spacing values for layout rhythm and composition

**Schema**:
```typescript
interface SpacingToken {
  value: number                  // 16 (pixels)

  // Naming
  name?: string                  // "Breathing Room"
  technical_name?: string        // "spacing-md"

  // Context
  usage?: string                 // "Card padding, section margins"
  grid_relationship?: string     // "Base × 2 (8px base)"

  // Semantic
  feeling?: string               // "comfortable", "generous", "intimate"
}

interface SpacingScale {
  xs: number | SpacingToken      // 4px
  sm: number | SpacingToken      // 8px
  md: number | SpacingToken      // 16px
  lg: number | SpacingToken      // 24px
  xl: number | SpacingToken      // 32px
  xxl: number | SpacingToken     // 48px
}
```

**Visual Example**:
```
SPACING SCALE (8px Base Rhythm)

xs (4px)  ▌ Intimate Touch
          Used for: Icon padding, badge gaps, micro-components
          Grid: Base ÷ 2

sm (8px)  ▌▌ Cozy Together
          Used for: Button padding, form fields, component internals
          Grid: Base unit

md (16px) ▌▌▌▌ Breathing Room
          Used for: Card padding, section margins, list items
          Grid: Base × 2

lg (24px) ▌▌▌▌▌▌ Generous Gap
          Used for: Component separation, content blocks
          Grid: Base × 3

xl (32px) ▌▌▌▌▌▌▌▌ Spacious Layout
          Used for: Section dividers, page structure
          Grid: Base × 4

xxl (48px) ▌▌▌▌▌▌▌▌▌▌▌▌ Grand Separation
           Used for: Hero sections, page-level divisions
           Grid: Base × 6
```

**Example**:
```json
{
  "spacing": {
    "xs": 4,
    "sm": 8,
    "md": {
      "value": 16,
      "name": "Breathing Room",
      "technical_name": "spacing-md",
      "usage": "Card padding, section margins, list items",
      "grid_relationship": "Base × 2 (visual harmony)",
      "feeling": "comfortable"
    },
    "lg": 24,
    "xl": 32,
    "xxl": 48
  },
  "grid": {
    "base": 8,
    "margin": 16,
    "columns": 12,
    "gutter": 16
  }
}
```

### 5. Shadow & Elevation Tokens

**Purpose**: Depth perception through shadow layers and elevation levels

**Schema**:
```typescript
interface ShadowToken {
  value: string                  // CSS box-shadow

  // Naming
  name?: string                  // "Gentle Lift"
  technical_name?: string        // "shadow-xs"

  // Elevation
  elevation?: number             // 2 (dp/px)
  material_dp?: number           // Material Design elevation (1dp)

  // Usage
  usage?: string                 // "Cards at rest, subtle depth"
  component_examples?: string[]  // ["card", "tooltip"]

  // Characteristics
  softness?: "subtle" | "soft" | "medium" | "hard"
  direction?: "top" | "bottom" | "center"
}

interface ShadowScale {
  [level: string]: string | ShadowToken
}
```

**Visual Example**:
```
SHADOW & ELEVATION SCALE

Level 0  ▁ None
         elevation: 0px

Level 1  ▁▁ Gentle Lift
         0 1px 3px rgba(0,0,0,0.12)
         elevation: 2px | Material: 1dp
         Used for: Cards at rest, subtle depth

Level 2  ▁▁▁ Floating Card
         0 4px 8px rgba(0,0,0,0.16)
         elevation: 8px | Material: 4dp
         Used for: Default cards, dropdowns, tooltips

Level 3  ▁▁▁▁ Elevated Modal
         0 8px 16px rgba(0,0,0,0.24)
         elevation: 16px | Material: 8dp
         Used for: Modals, dialogs, overlays

Level 4  ▁▁▁▁▁ Dramatic Hero
         0 16px 32px rgba(0,0,0,0.32)
         elevation: 32px | Material: 16dp
         Used for: Hero cards, featured content

Level 5  ▁▁▁▁▁▁ Commanding Presence
         0 24px 48px rgba(0,0,0,0.40)
         elevation: 48px | Material: 24dp
         Used for: Top-level navigation, app bars
```

**Example**:
```json
{
  "shadow": {
    "level1": {
      "value": "0 1px 3px rgba(0,0,0,0.12)",
      "name": "Gentle Lift",
      "technical_name": "shadow-xs",
      "elevation": 2,
      "material_dp": 1,
      "usage": "Cards at rest, subtle depth, hover states",
      "component_examples": ["card", "list_item"],
      "softness": "subtle",
      "direction": "bottom"
    },
    "level3": {
      "value": "0 8px 16px rgba(0,0,0,0.24)",
      "name": "Elevated Modal",
      "technical_name": "shadow-lg",
      "elevation": 16,
      "material_dp": 8,
      "usage": "Modals, dialogs, overlays, important components",
      "component_examples": ["modal", "dialog", "popover"],
      "softness": "medium",
      "direction": "center"
    }
  }
}
```

---

## Semantic Tokens

### Purpose of Semantic Tokens

Semantic tokens create **context-aware aliases** that reference primitive tokens, enabling:
- **Theme switching** (light/dark modes)
- **Brand consistency** (one source of truth)
- **Maintainability** (change once, update everywhere)
- **Clear intent** (role-based naming)

### Token Reference System

Semantic tokens use the `{tokenPath}` syntax:

```json
{
  "primitive": {
    "orange": {
      "500": "#F15925",
      "600": "#C14710"
    }
  },
  "semantic": {
    "brand": {
      "primary": "{orange.500}",      // References primitive
      "primaryHover": "{orange.600}"
    },
    "component": {
      "button": {
        "default": "{brand.primary}",  // References semantic
        "hover": "{brand.primaryHover}"
      }
    }
  }
}
```

**Resolution Order**:
1. Parse reference: `{orange.500}` → `primitive.orange.500`
2. Resolve to value: `#F15925`
3. Apply to component

### Brand Color Tokens

**Schema**:
```typescript
interface BrandColors {
  primary: string | TokenReference
  primaryHover: string
  primaryActive: string
  primaryDisabled: string
  secondary: string
  secondaryHover: string
  secondaryActive: string
  secondaryDisabled: string
}
```

**Example**:
```json
{
  "semantic": {
    "brand": {
      "primary": "{orange.500}",
      "primaryHover": "{orange.600}",
      "primaryActive": "{orange.700}",
      "primaryDisabled": "{orange.300}",
      "secondary": "{teal.500}",
      "secondaryHover": "{teal.600}"
    }
  }
}
```

---

## Component Tokens

### Button Component Schema

**Full Schema**:
```typescript
interface ButtonTokens {
  variants: {
    primary: ButtonVariant
    secondary: ButtonVariant
    tertiary: ButtonVariant
    ghost: ButtonVariant
    danger: ButtonVariant
  }
  sizes: {
    sm: ButtonSize
    md: ButtonSize
    lg: ButtonSize
  }
}

interface ButtonVariant {
  default: ButtonState
  hover: ButtonState
  focus: ButtonState
  active: ButtonState
  disabled: ButtonState
}

interface ButtonState {
  background: string
  foreground: string
  border: {
    width: number
    color: string
    style: "solid" | "dashed" | "dotted"
  }
  shadow?: string
  radius: number
  opacity?: number

  // Enhanced Metadata
  name?: string
  design_intent?: string
  usage?: string
}

interface ButtonSize {
  padding: { x: number; y: number }
  fontSize: number
  height: number
  minWidth?: number
}
```

**Visual Example**:
```
PRIMARY BUTTON STATES

Default   [  Submit  ]  bg: #646cff, text: #ffffff
Hover     [  Submit  ]  bg: #7481ff, shadow: +2dp
Focus     [  Submit  ]  border: 2px #646cff, ring: 3px
Active    [  Submit  ]  bg: #5159cc, shadow: -1dp
Disabled  [  Submit  ]  bg: #e0e0e0, text: #9e9e9e, opacity: 0.6
```

**Complete Example**:
```json
{
  "button": {
    "variants": {
      "primary": {
        "default": {
          "background": "#646cff",
          "foreground": "#ffffff",
          "border": {
            "width": 2,
            "color": "transparent",
            "style": "solid"
          },
          "radius": 8,
          "shadow": "0 2px 4px rgba(0,0,0,0.1)",
          "name": "Primary CTA",
          "design_intent": "Main call-to-action, highest visual priority",
          "usage": "Form submissions, primary actions, conversions"
        },
        "hover": {
          "background": "#7481ff",
          "foreground": "#ffffff",
          "border": {
            "width": 2,
            "color": "transparent",
            "style": "solid"
          },
          "radius": 8,
          "shadow": "0 4px 8px rgba(0,0,0,0.15)",
          "name": "Primary Hover",
          "design_intent": "Subtle elevation on hover for tactile feedback"
        }
      }
    },
    "sizes": {
      "md": {
        "padding": { "x": 16, "y": 8 },
        "fontSize": 16,
        "height": 40,
        "minWidth": 80
      }
    }
  }
}
```

---

## Visual DNA Tokens

### Material Tokens

**Purpose**: Physical properties defining surface characteristics

**Schema**:
```typescript
interface MaterialToken {
  // Classification
  material_class: "glass" | "metal" | "wood" | "plastic" | "fabric" | "paper" | "stone" | "ceramic"
  variant?: string                     // "polished", "brushed", "frosted"

  // Optical Properties
  optical: {
    gloss: number                      // 0-1 (0=matte, 1=mirror)
    reflectivity: number               // 0-1
    transmission: number               // 0-1 (transparency)
    refraction_ior?: number            // 1.0-2.5 (index of refraction)
    scatter: number                    // 0-1 (subsurface scattering)
    emission?: number                  // 0-1 (self-illumination)
    iridescence?: number               // 0-1 (color shift at angles)
  }

  // Tactile Properties
  tactile: {
    friction: number                   // 0-1
    warmth: number                     // 0-1 (cold to warm)
    grain: number                      // 0-1 (smoothness)
    softness: number                   // 0-1
    stickiness: number                 // 0-1
  }

  // Age & Condition
  age: {
    wear: number                       // 0-1
    patina: number                     // 0-1 (aged finish)
    oxidation: number                  // 0-1
    restoration: number                // 0-1 (refinished)
  }

  // Surface Details
  finish: "matte" | "satin" | "gloss" | "mirror"
  pattern?: "brushed-grain" | "cross-hatch" | "hammered" | "smooth"
  imperfections?: string[]             // ["scratches", "dents", "discoloration"]

  // Usage
  usage?: string
  design_intent?: string
  extractors?: string[]
}
```

**Visual Example**:
```
POLISHED METAL
Material: Metal (variant: polished)

Optical Properties:
  Gloss:        ████████░░ 0.8  (very glossy)
  Reflectivity: ██████░░░░ 0.6  (moderately reflective)
  Scatter:      ██░░░░░░░░ 0.2  (minimal subsurface)

Tactile Properties:
  Friction:     ████░░░░░░ 0.4  (slippery)
  Warmth:       ████░░░░░░ 0.4  (cool to touch)
  Grain:        ████████░░ 0.8  (smooth)

Age & Condition:
  Wear:         ██░░░░░░░░ 0.2  (minimal wear)
  Patina:       █░░░░░░░░░ 0.1  (fresh finish)
  Freshness:    █████████░ 0.9  (well-maintained)

Usage: Premium button surfaces, control knobs
Design Intent: Evokes precision hardware and high-quality construction
```

**Example**:
```json
{
  "materials": {
    "polished-metal": {
      "material_class": "metal",
      "variant": "polished",
      "optical": {
        "gloss": 0.8,
        "reflectivity": 0.6,
        "transmission": 0.0,
        "scatter": 0.2,
        "iridescence": 0.1
      },
      "tactile": {
        "friction": 0.4,
        "warmth": 0.4,
        "grain": 0.8,
        "softness": 0.1,
        "stickiness": 0.0
      },
      "age": {
        "wear": 0.2,
        "patina": 0.1,
        "oxidation": 0.0,
        "restoration": 0.9
      },
      "finish": "gloss",
      "pattern": "brushed-grain",
      "usage": "Premium button surfaces, rotary knobs, high-end controls",
      "design_intent": "Evokes precision hardware and high-quality construction",
      "extractors": ["material_extractor", "claude_vision"]
    }
  }
}
```

### Lighting Tokens

**Purpose**: Light sources and illumination characteristics

**Schema**:
```typescript
interface LightingToken {
  // Light Sources
  lights: Array<{
    type: "key" | "fill" | "back" | "ambient" | "rim" | "accent"
    color: string                      // "#FFF8E7"
    temperature?: number               // 2000-10000K
    intensity: number                  // 0-1
    direction?: { x: number; y: number; z: number }
    contrast: number                   // 0-1
  }>

  // Ambient Lighting
  ambient: {
    color: string
    intensity: number
    temperature: number
  }

  // Lighting Model
  model: "lambert" | "phong" | "blinn-phong" | "pbr" | "oren-nayar"

  // Shadows
  shadows: {
    softness: number                   // 0-1
    contact_intensity: number          // 0-1
    penumbra_size?: number
  }

  // Effects
  volumetric?: {
    scatter: number                    // 0-1 (fog/haze)
    density: number
  }
  bloom?: number                       // 0-1
  light_shafts?: boolean

  // Subsurface
  subsurface_scattering?: {
    intensity: number
    radius: number
  }

  // Scene Description
  scene_description?: string
  mood?: string
  time_of_day?: "dawn" | "day" | "golden_hour" | "dusk" | "night"
}
```

**Example**:
```json
{
  "lighting": {
    "lights": [
      {
        "type": "key",
        "color": "#FFF8E7",
        "temperature": 5500,
        "intensity": 0.8,
        "direction": { "x": 0.5, "y": -0.5, "z": 0.7 },
        "contrast": 0.6
      },
      {
        "type": "fill",
        "color": "#A8C8FF",
        "temperature": 7000,
        "intensity": 0.3,
        "direction": { "x": -0.3, "y": -0.2, "z": 0.9 },
        "contrast": 0.2
      }
    ],
    "ambient": {
      "color": "#E8ECEF",
      "intensity": 0.2,
      "temperature": 6500
    },
    "model": "pbr",
    "shadows": {
      "softness": 0.3,
      "contact_intensity": 0.7
    },
    "volumetric": {
      "scatter": 0.1,
      "density": 0.05
    },
    "scene_description": "Soft overhead key light with cool fill, studio lighting setup",
    "mood": "Professional, clean, focused",
    "time_of_day": "day"
  }
}
```

---

## Metadata & Governance

### Extraction Metadata Schema

**Purpose**: Track extraction provenance, confidence, and costs

**Schema**:
```typescript
interface ExtractionMetadata {
  // Extraction Process
  stage: "cv_complete" | "ai_enhanced" | "fully_validated"
  tier: 1 | 2 | 3                      // Tier 1: CV, Tier 2: Local AI, Tier 3: Cloud AI

  // Performance
  elapsed_seconds: number
  extractors_completed: number
  extractors_used: string[]

  // Cost Tracking
  total_cost?: number                  // USD
  cost_breakdown?: {
    gpt4_vision?: number
    claude_vision?: number
    other?: number
  }

  // Quality
  confidence_threshold: number         // Minimum confidence for inclusion
  consensus_score?: number             // Agreement across extractors

  // Versioning
  schema_version: string               // "3.1"
  extractor_version: string            // "2.6.0"

  // User Context
  extraction_id: string
  timestamp: string
  user_settings?: Record<string, any>
}
```

**Example**:
```json
{
  "_metadata": {
    "stage": "fully_validated",
    "tier": 3,
    "elapsed_seconds": 64.2,
    "extractors_completed": 21,
    "extractors_used": [
      "color_extractor",
      "spacing_extractor",
      "typography_extractor",
      "shadow_extractor",
      "gradient_extractor",
      "material_extractor",
      "lighting_extractor",
      "gpt4_vision",
      "claude_vision"
    ],
    "total_cost": 0.047,
    "cost_breakdown": {
      "gpt4_vision": 0.020,
      "claude_vision": 0.027
    },
    "confidence_threshold": 0.75,
    "consensus_score": 0.92,
    "schema_version": "3.1",
    "extractor_version": "2.6.0",
    "extraction_id": "ext_2025-11-11_abc123",
    "timestamp": "2025-11-11T15:30:00Z"
  }
}
```

---

## Schema Evolution & Versioning

### Version History

| Version | Date | Key Changes |
|---------|------|-------------|
| **1.0** | 2024-08 | Foundation tokens (palette, spacing, typography, shadows) |
| **1.5** | 2024-09 | Semantic tokens + grid system |
| **2.0** | 2024-10 | AI enhancement + WCAG validation + advanced tokens |
| **2.4** | 2024-11 | Opacity, transitions, blur filters |
| **2.5** | 2024-12 | Font family, component recognition, depth maps |
| **2.6** | 2025-01 | Audio components, style/mood extraction |
| **3.0** | 2025-10 | Component tokens, compositional architecture |
| **3.1** | 2025-11 | Visual DNA 2.0, multi-variant system, perceptual tokens |

### Backward Compatibility

All schema versions are **additive only**:
- New fields are optional
- Old fields never removed
- Parsers ignore unknown fields
- Default values for missing fields

**Migration Example**:
```typescript
// v1.0 Token (still valid)
{
  "palette": {
    "primary": "#F15925"
  }
}

// v3.1 Token (fully enhanced)
{
  "palette": {
    "primary": {
      "hex": "#F15925",
      "name": "Molten Copper",
      "design_intent": "...",
      "accessibility": { ... }
    }
  }
}

// Parser handles both formats
function parseColor(color: string | ColorToken): ColorToken {
  if (typeof color === "string") {
    return { hex: color }  // v1.0 format
  }
  return color            // v3.1 format
}
```

---

## Related Documentation

- [Token Reference](TOKEN_REFERENCE.md) - Complete token catalog
- [Token Features](TOKEN_FEATURES.md) - Capabilities and use cases
- [Visual DNA 2.0](VISUAL_DNA_DEEP_DIVE.md) - Perceptual token system
- [Extractor Mapping](EXTRACTOR_TOKEN_MAPPING.md) - Which extractors create which tokens
- [Generator Guide](GENERATOR_EXPORT_GUIDE.md) - Platform export formats

---

**Last Updated**: 2025-11-11
**Schema Version**: 3.1
**Status**: Complete Reference

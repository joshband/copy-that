# Copy This Design Token Reference

**Complete Token Taxonomy, Schema, and Ontology**

Version: 2.0 (Phase 2 Complete)
Updated: 2025-11-09

---

## Table of Contents

1. [Token Hierarchy](#token-hierarchy)
2. [Foundation Tokens](#foundation-tokens)
3. [Semantic Tokens](#semantic-tokens)
4. [Component Tokens](#component-tokens)
5. [Advanced Tokens](#advanced-tokens)
6. [AI-Enhanced Tokens](#ai-enhanced-tokens)
7. [Experimental Tokens](#experimental-tokens)
8. [Token Schema Reference](#token-schema-reference)
9. [Token Relationships](#token-relationships)
10. [Usage Examples](#usage-examples)

---

## Token Hierarchy

```
Design Token System
│
├── Foundation (Primitive) Tokens
│   ├── Color Palette
│   ├── Color Scales
│   ├── Spacing Scale
│   ├── Typography
│   ├── Shadows & Elevation
│   ├── Border Radius
│   ├── Grid System
│   └── Breakpoints
│
├── Semantic Tokens (Context-Aware)
│   ├── Brand Colors
│   ├── UI Colors (background, surface, border)
│   ├── Feedback Colors (success, warning, error, info)
│   ├── Text Colors (primary, secondary, tertiary)
│   └── Component Colors (button, input, etc.)
│
├── Advanced Tokens
│   ├── Opacity/Transparency
│   ├── Transitions & Timing
│   ├── Blur & Filters
│   ├── Gradients
│   ├── Animations
│   └── Mobile Tokens
│
├── AI-Enhanced Tokens
│   ├── Semantic Color Names
│   ├── Design Intent
│   ├── Accessibility Metadata
│   ├── Usage Guidance
│   └── Style Ontology
│
└── Experimental Tokens
    ├── Font Family Recognition
    ├── Component Recognition
    ├── Depth Maps
    ├── Video Animations
    └── Audio Plugin Components
```

---

## Foundation Tokens

### 1. Color Palette

**Purpose:** Core color roles extracted from visual design

**Schema:**
```typescript
palette: {
  [role: string]: ColorToken
}

ColorToken = string | {
  hex: string
  extractors?: string[]
  name?: string              // AI-enhanced
  semantic_name?: string     // AI-enhanced
  usage?: string             // AI-enhanced
  description?: string       // AI-enhanced
  design_intent?: string     // AI-enhanced
  accessibility?: string | { // AI-enhanced
    contrast_ratio?: number
    wcag_level?: string
  }
}
```

**Roles:**
- `primary` - Main brand color
- `secondary` - Secondary brand color
- `neutral` - Neutral/background color
- `accent` - Accent/highlight color
- `text` - Primary text color
- `error` - Error/danger color
- `background` - Background color (optional)
- `success` - Success color (optional)

**Example:**
```json
{
  "palette": {
    "primary": {
      "hex": "#F15925",
      "extractors": ["opencv_cv", "gpt4_vision"],
      "name": "Vibrant Orange",
      "usage": "Primary CTAs and brand elements",
      "design_intent": "Energetic and attention-grabbing",
      "accessibility": "AA compliant with white text"
    },
    "secondary": "#4ECDC4",
    "neutral": "#95A5A6"
  }
}
```

**Extractors:**
- `opencv_cv` - K-means clustering
- `gpt4_vision` - AI semantic naming
- `claude_vision` - AI design intent
- `clip_semantics` - Zero-shot classification

---

### 2. Primitive Color Scales

**Purpose:** 50-900 color scales for each base color

**Schema:**
```typescript
primitive: {
  [colorName: string]: {
    "50": string   // 95% lightness
    "100": string  // 90% lightness
    "200": string  // 80% lightness
    "300": string  // 70% lightness
    "400": string  // 60% lightness
    "500": string  // Base color (unchanged)
    "600": string  // 40% lightness
    "700": string  // 30% lightness
    "800": string  // 20% lightness
    "900": string  // 10% lightness
  }
}
```

**Example:**
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

**Generation:** HSL interpolation maintaining hue and saturation

---

### 3. Spacing Scale

**Purpose:** Consistent spacing values for layout and composition

**Schema:**
```typescript
spacing: {
  xs: number    // Extra small (4px typical)
  sm: number    // Small (8px typical)
  md: number    // Medium (16px typical)
  lg: number    // Large (24px typical)
  xl: number    // Extra large (32px typical)
  xxl: number   // 2x extra large (48px typical)
}
```

**Example:**
```json
{
  "spacing": {
    "xs": 4,
    "sm": 8,
    "md": 16,
    "lg": 24,
    "xl": 32,
    "xxl": 48
  }
}
```

**Extraction:** Edge detection + gap analysis between UI components

---

### 4. Typography

**Purpose:** Font family and weight information

**Schema:**
```typescript
typography: {
  family: string
  weights: number[]
}

typography_extended?: {
  fonts: {
    [type: string]: {
      web: {
        family: string
        source: string
        weights: number[]
        character: string
      }
      ios: string
      android: string
      juce: string
    }
  }
  scale?: {
    [size: string]: {
      fontSize: string
      lineHeight: string
      letterSpacing?: string
    }
  }
}
```

**Example:**
```json
{
  "typography": {
    "family": "Inter",
    "weights": [400, 600, 700]
  },
  "typography_extended": {
    "fonts": {
      "display": {
        "web": {
          "family": "Inter",
          "source": "google-fonts",
          "weights": [400, 600, 700, 800],
          "character": "Clean, modern, geometric"
        },
        "ios": "SF Pro Display",
        "android": "Roboto",
        "juce": "Arial"
      }
    }
  }
}
```

**Extraction:** Style-based aesthetic analysis (non-OCR)

---

### 5. Shadows & Elevation

**Purpose:** Shadow layers and elevation scale

**Schema:**
```typescript
shadow: {
  [level: string]: string  // CSS box-shadow value
}

elevation?: {
  [level: string]: number  // Elevation value (dp/px)
}
```

**Example:**
```json
{
  "shadow": {
    "level0": "none",
    "level1": "0 1px 2px rgba(0,0,0,0.1)",
    "level2": "0 2px 4px rgba(0,0,0,0.12)",
    "level3": "0 4px 8px rgba(0,0,0,0.14)",
    "level4": "0 8px 16px rgba(0,0,0,0.16)",
    "level5": "0 16px 32px rgba(0,0,0,0.18)"
  },
  "elevation": {
    "raised": 2,
    "overlay": 8,
    "modal": 16,
    "popup": 24
  }
}
```

**Extraction:** Contrast analysis + blur detection + progressive scaling

---

### 6. Border Radius

**Purpose:** Corner rounding values

**Schema:**
```typescript
radius: {
  sm: number   // Small radius (4-8px)
  md: number   // Medium radius (8-12px)
  lg: number   // Large radius (12-16px)
  full?: number // Full circle (9999px or 50%)
}
```

**Example:**
```json
{
  "radius": {
    "sm": 4,
    "md": 8,
    "lg": 12,
    "full": 9999
  }
}
```

---

### 7. Grid System

**Purpose:** Base grid and margin values

**Schema:**
```typescript
grid: {
  base: number    // Base grid unit (4px or 8px typical)
  margin: number  // Container margin (16px typical)
  gutter?: number // Column gutter (optional)
}
```

**Example:**
```json
{
  "grid": {
    "base": 8,
    "margin": 16
  }
}
```

---

### 8. Breakpoints

**Purpose:** Responsive design breakpoints

**Schema:**
```typescript
breakpoints: {
  [name: string]: number  // Width in pixels
}
```

**Example:**
```json
{
  "breakpoints": {
    "compact": 640,
    "standard": 1024,
    "studio": 1440,
    "cinema": 1920
  }
}
```

---

### 9. Animation Timing

**Purpose:** Animation duration and easing functions

**Schema:**
```typescript
animation: {
  duration: {
    [speed: string]: string  // CSS duration
  }
  easing: {
    [curve: string]: string  // CSS easing function
  }
}
```

**Example:**
```json
{
  "animation": {
    "duration": {
      "instant": "100ms",
      "fast": "200ms",
      "normal": "300ms",
      "slow": "500ms"
    },
    "easing": {
      "linear": "linear",
      "easeIn": "cubic-bezier(0.4, 0, 1, 1)",
      "easeOut": "cubic-bezier(0, 0, 0.2, 1)",
      "easeInOut": "cubic-bezier(0.4, 0, 0.2, 1)"
    }
  }
}
```

---

## Semantic Tokens

**Purpose:** Context-aware tokens that reference primitive tokens

### Brand Colors

```typescript
semantic.brand: {
  primary: string           // Token reference or hex
  primaryHover: string
  primaryActive: string
  primaryDisabled: string
  secondary: string
  secondaryHover: string
  secondaryActive: string
  secondaryDisabled: string
}
```

**Example:**
```json
{
  "semantic": {
    "brand": {
      "primary": "{orange.500}",
      "primaryHover": "{orange.600}",
      "primaryActive": "{orange.700}",
      "primaryDisabled": "{orange.300}"
    }
  }
}
```

**Token References:** Use `{colorName.scale}` format to reference primitive colors

---

### UI Colors

```typescript
semantic.ui: {
  background: string
  surface: string
  surfaceHover: string
  surfaceActive: string
  border: string
  borderHover: string
  divider: string
  overlay: string
}
```

---

### Feedback Colors

```typescript
semantic.feedback: {
  success: string
  successBg: string
  warning: string
  warningBg: string
  error: string
  errorBg: string
  info: string
  infoBg: string
}
```

---

### Text Colors

```typescript
semantic.text: {
  primary: string      // Primary text
  secondary: string    // Secondary text (60% opacity)
  tertiary: string     // Tertiary text (40% opacity)
  disabled: string     // Disabled text
  onPrimary: string    // Text on primary color background
  onSecondary: string  // Text on secondary color background
  onBackground: string // Text on main background
  onSurface: string    // Text on surface/cards
}
```

---

### Component Colors

```typescript
semantic.component: {
  [componentName: string]: {
    [variant: string]: string
  }
}
```

**Example:**
```json
{
  "semantic": {
    "component": {
      "button": {
        "default": "{orange.500}",
        "hover": "{orange.600}",
        "active": "{orange.700}",
        "disabled": "{gray.400}",
        "text": "{gray.50}"
      },
      "knob": {
        "default": "{orange.500}",
        "hover": "{orange.600}",
        "indicator": "{yellow.500}"
      }
    }
  }
}
```

---

## Advanced Tokens

### Opacity / Transparency

**Purpose:** Opacity scale for transparency effects

**Schema:**
```typescript
opacity: {
  opacity: {
    scale: {
      [level: string]: number  // 0.0 - 1.0
    }
  }
  _metadata?: {
    detected_values: number
    total_patterns: number
  }
}
```

**Example:**
```json
{
  "opacity": {
    "opacity": {
      "scale": {
        "transparent": 0.0,
        "ghost": 0.05,
        "faint": 0.1,
        "light": 0.2,
        "medium": 0.5,
        "heavy": 0.8,
        "solid": 1.0
      }
    },
    "_metadata": {
      "detected_values": 12,
      "total_patterns": 45
    }
  }
}
```

**Extractor:** CV-based transparency pattern detection

---

### Transitions & Timing

**Purpose:** Transition durations and easing for interactive elements

**Schema:**
```typescript
transitions: {
  transitions: {
    duration: {
      [name: string]: string  // CSS duration
    }
    easing: {
      [name: string]: string  // CSS easing function
    }
  }
  _metadata?: {
    components: number
    motion_states: number
  }
}
```

**Example:**
```json
{
  "transitions": {
    "transitions": {
      "duration": {
        "instant": "50ms",
        "quick": "150ms",
        "smooth": "300ms",
        "slow": "600ms"
      },
      "easing": {
        "spring": "cubic-bezier(0.34, 1.56, 0.64, 1)",
        "bounce": "cubic-bezier(0.68, -0.55, 0.265, 1.55)"
      }
    }
  }
}
```

**Extractor:** Interactive component motion analysis

---

### Blur & Filters

**Purpose:** Blur radius and filter effects (glassmorphism)

**Schema:**
```typescript
blur_filters: {
  blur: {
    radius: {
      [level: string]: string  // CSS blur value
    }
    backdrop: {
      [level: string]: string  // CSS backdrop-filter
    }
  }
  filters?: {
    [effect: string]: string
  }
}
```

**Example:**
```json
{
  "blur_filters": {
    "blur": {
      "radius": {
        "sm": "4px",
        "md": "8px",
        "lg": "16px",
        "xl": "24px"
      },
      "backdrop": {
        "glass": "blur(10px) saturate(180%)",
        "frosted": "blur(20px) brightness(1.1)"
      }
    }
  }
}
```

**Extractor:** Blur detection + glassmorphism pattern recognition

---

### Gradients

**Purpose:** Linear, radial, and conic gradient patterns

**Schema:**
```typescript
gradients: {
  linear?: Array<{
    angle: number
    stops: Array<{ color: string; position: number }>
  }>
  radial?: Array<{
    shape: string
    stops: Array<{ color: string; position: number }>
  }>
  conic?: Array<{
    angle: number
    stops: Array<{ color: string; position: number }>
  }>
}
```

**Example:**
```json
{
  "gradients": {
    "linear": [
      {
        "angle": 45,
        "stops": [
          { "color": "#F15925", "position": 0 },
          { "color": "#FFD166", "position": 100 }
        ]
      }
    ]
  }
}
```

**Extractor:** Gradient detection via color transition analysis

---

### Mobile Tokens

**Purpose:** Mobile-specific design tokens

**Schema:**
```typescript
mobile: {
  touchTargets: {
    minimum: number       // Minimum touch target (44px iOS, 48px Android)
    recommended: number
  }
  safeArea: {
    top: number
    bottom: number
    left: number
    right: number
  }
  gestures?: {
    swipeThreshold: number
    longPressDelay: number
  }
}
```

**Example:**
```json
{
  "mobile": {
    "touchTargets": {
      "minimum": 44,
      "recommended": 48
    },
    "safeArea": {
      "top": 47,
      "bottom": 34,
      "left": 0,
      "right": 0
    }
  }
}
```

---

## AI-Enhanced Tokens

### Semantic Color Names

**Added to ColorToken:** AI-generated human-readable names

```typescript
{
  "palette": {
    "primary": {
      "hex": "#F15925",
      "name": "Vibrant Orange",           // ← AI-enhanced
      "semantic_name": "Sunset Orange"    // ← AI-enhanced
    }
  }
}
```

**Extractors:** `gpt4_vision`, `claude_vision`, `clip_semantics`

---

### Design Intent

**Added to ColorToken:** Why this color was chosen

```typescript
{
  "design_intent": "Energetic and attention-grabbing, evoking warmth and enthusiasm"
}
```

**Extractor:** `gpt4_vision`, `claude_vision`

---

### Usage Guidance

**Added to ColorToken:** How to use the color

```typescript
{
  "usage": "Primary CTAs, brand highlights, and interactive elements requiring user attention"
}
```

---

### Accessibility Metadata

**Added to ColorToken:** WCAG compliance info

```typescript
{
  "accessibility": {
    "contrast_ratio": 4.52,
    "wcag_level": "AA",
    "recommendations": "Use with white or light text for accessibility"
  }
}
```

---

### WCAG Validation

**Purpose:** Color contrast validation and compliance checking

**Schema:**
```typescript
a11y: {
  wcag: "AA" | "AAA"
  contrast: {
    [pairing: string]: number  // Contrast ratio
  }
  semantic_validation: Array<{
    pair: string
    fg?: string
    bg?: string
    fg_color?: string
    bg_color?: string
    ratio?: number
    target?: number
    status: "PASS" | "FAIL" | "SUMMARY"
    level?: "AAA" | "AA" | "AA Large" | "Fail"
    adjusted?: {
      color: string
      ratio: number
      note: string
    }
    // Summary fields (when status === "SUMMARY")
    total?: number
    passed?: number
    failed?: number
    compliance_rate?: number
  }>
}
```

**Example:**
```json
{
  "a11y": {
    "wcag": "AA",
    "contrast": {
      "text_on_primary": 4.52,
      "text_on_secondary": 3.81
    },
    "semantic_validation": [
      {
        "pair": "_summary",
        "status": "SUMMARY",
        "total": 8,
        "passed": 6,
        "failed": 2,
        "compliance_rate": 75.0
      },
      {
        "pair": "text.primary / ui.background",
        "fg_color": "#2C3E50",
        "bg_color": "#ECF0F1",
        "ratio": 8.59,
        "target": 4.5,
        "status": "PASS",
        "level": "AAA"
      }
    ]
  }
}
```

**Validator:** Phase 2 - FEAT-014 WCAG enhancement

---

### Style Ontology

**Purpose:** AI-detected style characteristics and tags

**Schema:**
```typescript
ontology: {
  style_tags: Array<string | {
    tag: string
    description?: string
    score?: number
    source?: string
  }>
  era?: string
  mood?: string
  influences?: string[]
}
```

**Example:**
```json
{
  "ontology": {
    "style_tags": [
      {
        "tag": "retro-technical",
        "description": "Vintage audio equipment aesthetic with warm industrial feel",
        "score": 0.92,
        "source": "gpt4_vision"
      },
      "skeuomorphic",
      "warm-palette"
    ],
    "era": "1970s-1980s",
    "mood": "nostalgic, warm, technical",
    "influences": ["vintage audio", "industrial design"]
  }
}
```

**Extractor:** `ontology_extractor` (GPT-4 Vision based)

---

## Experimental Tokens

### Font Family Recognition

**Purpose:** Detect actual font families from rendered text

**Schema:**
```typescript
font_family: {
  fonts: {
    [detectedFont: string]: {
      confidence: number
      usage: string
      alternatives: string[]
    }
  }
  _metadata?: {
    detection_method: string
    total_fonts: number
  }
}
```

**Example:**
```json
{
  "font_family": {
    "fonts": {
      "Helvetica Neue": {
        "confidence": 0.87,
        "usage": "Body text and UI labels",
        "alternatives": ["Arial", "Roboto", "SF Pro"]
      }
    }
  }
}
```

**Extractor:** CV-based font recognition (experimental)

---

### Component Recognition

**Purpose:** Detect UI components (buttons, inputs, cards, etc.)

**Schema:**
```typescript
component_recognition: {
  components: Array<{
    type: "button" | "input" | "card" | "navigation" | "icon"
    confidence: number
    boundingBox: { x: number; y: number; width: number; height: number }
    properties?: {
      variant?: string
      state?: string
      size?: string
    }
  }>
  _metadata?: {
    total_components: number
    detection_model: string
  }
}
```

**Example:**
```json
{
  "component_recognition": {
    "components": [
      {
        "type": "button",
        "confidence": 0.94,
        "boundingBox": { "x": 120, "y": 340, "width": 160, "height": 48 },
        "properties": {
          "variant": "primary",
          "size": "large"
        }
      }
    ]
  }
}
```

**Extractor:** YOLO-based component detection (experimental)

---

### Depth Map

**Purpose:** Infer depth/elevation from visual cues

**Schema:**
```typescript
depth_map: {
  elevation: {
    [element: string]: number | string
  }
  _metadata?: {
    depth_levels: number
    inference_method: string
  }
}
```

**Example:**
```json
{
  "depth_map": {
    "elevation": {
      "background": 0,
      "card": 2,
      "modal": 16,
      "tooltip": 24
    }
  }
}
```

**Extractor:** Depth inference from shadows and overlaps

---

### Video Animation

**Purpose:** Extract animation timings from video/GIF files

**Schema:**
```typescript
video_animation: {
  animations: Array<{
    name: string
    duration: number
    easing: string
    keyframes: Array<{
      time: number
      properties: Record<string, any>
    }>
  }>
  _metadata?: {
    source_format: string
    frame_rate: number
    duration_ms: number
  }
}
```

**Example:**
```json
{
  "video_animation": {
    "animations": [
      {
        "name": "button_press",
        "duration": 200,
        "easing": "cubic-bezier(0.4, 0, 0.2, 1)",
        "keyframes": [
          { "time": 0, "properties": { "scale": 1.0 } },
          { "time": 100, "properties": { "scale": 0.95 } },
          { "time": 200, "properties": { "scale": 1.0 } }
        ]
      }
    ]
  }
}
```

**Extractor:** Video frame analysis (optional, video files only)

---

## Token Schema Reference

### Complete Token Response

```typescript
interface DesignTokens {
  // Foundation
  palette: Record<string, ColorToken>
  primitive: Record<string, ColorScale>
  spacing: Record<string, number>
  typography: Typography
  typography_extended?: TypographyExtended
  shadow: Record<string, string>
  elevation?: Record<string, number>
  radius: Record<string, number>
  grid: Grid
  breakpoints: Record<string, number>
  animation: Animation
  zindex?: Record<string, number>
  zindex_docs?: Record<string, string>
  icon_sizes?: Record<string, number>

  // Semantic
  semantic: Semantic

  // Advanced
  opacity?: Opacity
  transitions?: Transitions
  blur_filters?: BlurFilters
  gradients?: Gradients
  mobile?: MobileTokens

  // AI-Enhanced
  a11y?: Accessibility
  ontology?: Ontology

  // Experimental
  font_family?: FontFamily
  semantic_segmentation?: SemanticSegmentation
  component_recognition?: ComponentRecognition
  depth_map?: DepthMap
  video_animation?: VideoAnimation
  audio_components?: AudioComponents
  style_mood?: StyleMood

  // Metadata
  _metadata?: ExtractionMetadata
}
```

### Extraction Metadata

```typescript
interface ExtractionMetadata {
  stage?: string                // "cv_complete" | "ai_complete"
  tier?: number                 // 1 (fast) | 2 (medium) | 3 (slow)
  elapsed_seconds?: number      // Total extraction time
  total_cost?: number           // AI API cost in USD
  confidence_threshold?: number // Consensus confidence (0-1)
  extractors_completed?: number // Number of extractors run
  extractors?: string[]         // List of extractors used
}
```

---

## Token Relationships

### Dependency Graph

```
Primitive Colors (palette)
    ↓
Color Scales (primitive)
    ↓
Semantic Colors (semantic.*)
    ↓
Component Colors (semantic.component.*)
```

### Reference System

**Token References:** Use `{tokenPath}` syntax

```json
{
  "semantic": {
    "brand": {
      "primary": "{orange.500}",        // References primitive.orange.500
      "primaryHover": "{orange.600}"
    },
    "component": {
      "button": {
        "default": "{brand.primary}",   // References semantic.brand.primary
        "hover": "{brand.primaryHover}"
      }
    }
  }
}
```

**Resolution Order:**
1. Check if value starts with `{` (token reference)
2. Parse path (e.g., `orange.500` → `primitive.orange.500`)
3. Resolve to hex value
4. Apply to component

---

### WCAG Validation Relationships

```
Semantic Color Pairs
    ↓
WCAG Contrast Calculation
    ↓
Compliance Level (AAA/AA/AA Large/Fail)
    ↓
Auto-Adjustment Suggestions (if failed)
```

**Validated Pairs:**
- text.primary / ui.background
- text.secondary / ui.background
- brand.primary / text.onPrimary
- component.button.text / component.button.default
- feedback.success / feedback.successBg
- etc.

---

## Usage Examples

### Example 1: Complete Token Set (Design System)

```json
{
  "palette": {
    "primary": {
      "hex": "#F15925",
      "extractors": ["opencv_cv", "gpt4_vision"],
      "name": "Vibrant Orange",
      "usage": "Primary CTAs and brand elements"
    },
    "secondary": "#4ECDC4",
    "neutral": "#95A5A6"
  },
  "primitive": {
    "orange": {
      "500": "#F15925",
      "600": "#C14710",
      "700": "#91350C"
    }
  },
  "semantic": {
    "brand": {
      "primary": "{orange.500}",
      "primaryHover": "{orange.600}"
    }
  },
  "spacing": {
    "sm": 8,
    "md": 16,
    "lg": 24
  },
  "shadow": {
    "level1": "0 1px 2px rgba(0,0,0,0.1)",
    "level2": "0 4px 6px rgba(0,0,0,0.1)"
  },
  "a11y": {
    "wcag": "AA",
    "semantic_validation": [
      {
        "pair": "text.primary / ui.background",
        "ratio": 8.59,
        "status": "PASS",
        "level": "AAA"
      }
    ]
  }
}
```

---

### Example 2: Minimal Token Set (MVP)

```json
{
  "palette": {
    "primary": "#F15925",
    "secondary": "#4ECDC4",
    "text": "#2C3E50"
  },
  "spacing": {
    "sm": 8,
    "md": 16,
    "lg": 24
  },
  "typography": {
    "family": "Inter",
    "weights": [400, 600]
  }
}
```

---

### Example 3: AI-Enhanced Token Set

```json
{
  "palette": {
    "primary": {
      "hex": "#F15925",
      "extractors": ["opencv_cv", "gpt4_vision", "clip_semantics"],
      "name": "Vibrant Orange",
      "semantic_name": "Sunset Ember",
      "usage": "Primary CTAs, brand highlights, interactive elements",
      "design_intent": "Energetic and attention-grabbing, evokes warmth",
      "accessibility": {
        "contrast_ratio": 4.52,
        "wcag_level": "AA",
        "recommendations": "Use with white text"
      }
    }
  },
  "ontology": {
    "style_tags": [
      {
        "tag": "retro-technical",
        "score": 0.92,
        "description": "Vintage audio equipment aesthetic"
      },
      "warm-palette",
      "skeuomorphic"
    ],
    "era": "1970s-1980s",
    "mood": "nostalgic, warm, technical"
  }
}
```

---

## Token Generation Pipeline

```
1. Image Upload
    ↓
2. CV Extraction (Fast - ~1s)
   - Color palette (K-means)
   - Spacing (edge detection)
   - Typography (style analysis)
   - Shadows (contrast analysis)
    ↓
3. Color Scale Generation
   - HSL interpolation (50-900)
    ↓
4. Semantic Token Mapping
   - Reference primitive colors
    ↓
5. WCAG Validation (Phase 2 - FEAT-014)
   - Contrast checking
   - Compliance level
   - Auto-suggestions
    ↓
6. AI Enhancement (Optional - ~2-5s)
   - CLIP semantic naming (local, zero-cost)
   - GPT-4 Vision design intent
   - Claude Vision semantic analysis
    ↓
7. Ontology Extraction (Optional)
   - Style tag detection
   - Era/mood classification
    ↓
8. Final Token Set
```

---

## Extractor Reference

### CV Extractors (Fast - Tier 1)

- `opencv_cv` - K-means color clustering, edge detection
- `spacing_extractor` - Gap analysis between components
- `typography_extractor` - Style-based font matching
- `shadow_extractor` - Contrast and blur analysis
- `gradient_extractor` - Color transition detection
- `mobile_extractor` - Touch target and safe area detection

### AI Extractors (Medium - Tier 2)

- `clip_semantics` - Zero-shot color classification (local, GPU-accelerated)
- `llava_semantics` - Vision-language understanding (local, optional)

### AI Extractors (Slow - Tier 3)

- `gpt4_vision` - OpenAI GPT-4 Vision (API, ~2s, ~$0.02)
- `claude_vision` - Anthropic Claude Vision (API, ~5s, ~$0.05)
- `ontology_extractor` - Style ontology (GPT-4 based)

### Experimental Extractors

- `font_family_extractor` - Font recognition
- `component_recognition_extractor` - UI component detection
- `depth_map_extractor` - Depth inference
- `video_animation_extractor` - Animation extraction
- `audio_plugin_component_extractor` - Audio UI detection

---

## Token Versioning

**Current Version:** 2.0

**Version History:**
- `1.0` - Foundation tokens (palette, spacing, typography, shadows)
- `1.5` - Semantic tokens + grid system
- `2.0` - AI enhancement + WCAG validation + advanced tokens
- `2.4` - Opacity, transitions, blur filters
- `2.5` - Font family, component recognition, depth maps
- `2.6` - Audio components, style/mood extraction

**Backward Compatibility:** All tokens are backward compatible. New fields are additive.

---

## Best Practices

### 1. Use Semantic Tokens in Production

❌ **Don't:**
```css
.button {
  background: #F15925; /* Hard-coded hex */
}
```

✅ **Do:**
```css
.button {
  background: var(--brand-primary); /* Semantic token */
}
```

### 2. Reference Primitive Colors

❌ **Don't:**
```json
{
  "button": {
    "primary": "#F15925",
    "primaryHover": "#C14710"
  }
}
```

✅ **Do:**
```json
{
  "button": {
    "primary": "{orange.500}",
    "primaryHover": "{orange.600}"
  }
}
```

### 3. Validate WCAG Compliance

```json
{
  "a11y": {
    "semantic_validation": [...]
  }
}
```

Always check `a11y.semantic_validation` for failed pairs and use suggested adjustments.

### 4. Leverage AI Enhancement

Enable AI extraction for:
- Semantic color names
- Design intent documentation
- Usage guidance
- Style ontology

### 5. Use Appropriate Extraction Mode

- **Standard mode:** Foundation tokens only (fast, free)
- **Comprehensive mode:** All 15+ token categories (slower, AI costs)

---

## Related Documentation

- [Phase 2 Implementation](PHASE2_COMPLETE.md)
- [PostgreSQL Setup](backend/POSTGRESQL_SETUP.md)
- [WCAG Validation](frontend/src/components/TokenDisplay.tsx) (lines 972-1100)
- [API Documentation](backend/routers/extraction.py)

---

**Last Updated:** 2025-11-09
**Phase:** 2 Complete
**Version:** 2.0


# Token Variations & Multi-Variant System Guide

**Complete Guide to Theme Variants and Token Alternatives**

Version: 3.1
Last Updated: 2025-11-11
Status: Production Ready

---

## Table of Contents

1. [What are Token Variants?](#what-are-token-variants)
2. [Multi-Variant System Architecture](#multi-variant-system-architecture)
3. [Color Scheme Variants](#color-scheme-variants)
4. [Spacing Scale Variants](#spacing-scale-variants)
5. [Shadow Depth Variants](#shadow-depth-variants)
6. [Border Radius Variants](#border-radius-variants)
7. [Variant Selection & UI](#variant-selection--ui)
8. [Implementation Guide](#implementation-guide)

---

## What are Token Variants?

### The Problem

A single design can be expressed in **multiple valid ways**:

**Color**:
- Light theme (white backgrounds, dark text)
- Dark theme (dark backgrounds, light text)
- High contrast (maximum accessibility)

**Spacing**:
- Compact (mobile, dense information)
- Comfortable (default desktop)
- Spacious (accessibility, large screens)

**Shadows**:
- Subtle (flat, minimal design)
- Moderate (standard Material Design)
- Dramatic (bold, high-impact)

**Border Radius**:
- Sharp (0px, corporate/angular)
- Rounded (8px, balanced)
- Pill (24px+, organic/friendly)

### The Solution: Multi-Variant System (v3.1)

**Generate 3 variants per token category** automatically:

```typescript
{
  "color_variants": [
    { "variant_name": "light", "recommended": true, "rank": 1 },
    { "variant_name": "dark", "rank": 2 },
    { "variant_name": "high_contrast", "rank": 3 }
  ],
  "spacing_variants": [
    { "variant_name": "compact", "rank": 1 },
    { "variant_name": "comfortable", "recommended": true, "rank": 1 },
    { "variant_name": "spacious", "rank": 3 }
  ]
}
```

**Benefits**:
- ✅ Automatic theme generation
- ✅ Accessibility compliance (high contrast, spacious)
- ✅ Platform adaptation (compact for mobile)
- ✅ User preference support
- ✅ A/B testing ready

---

## Multi-Variant System Architecture

### Variant Generator

**File**: `extractors/extractors/variant_generator.py` (340 lines)

**Implementation**:
```python
class VariantGenerator:
    """Generate 3 variants per token category"""

    def generate_color_variants(self, base_palette: Dict) -> List[Dict]:
        """Generate light, dark, and high-contrast color schemes"""
        pass

    def generate_spacing_variants(self, base_spacing: Dict) -> List[Dict]:
        """Generate compact, comfortable, and spacious scales"""
        pass

    def generate_shadow_variants(self, base_shadows: Dict) -> List[Dict]:
        """Generate subtle, moderate, and dramatic shadows"""
        pass

    def generate_radius_variants(self, base_radius: Dict) -> List[Dict]:
        """Generate sharp, rounded, and pill radius scales"""
        pass
```

### Extraction Flow

```
Base Tokens Extracted
    ↓
Variant Generator
    ↓
    ├── Color Variants (3)
    │   ├── Light (recommended)
    │   ├── Dark
    │   └── High Contrast
    ↓
    ├── Spacing Variants (3)
    │   ├── Compact
    │   ├── Comfortable (recommended)
    │   └── Spacious
    ↓
    ├── Shadow Variants (3)
    │   ├── Subtle
    │   ├── Moderate (recommended)
    │   └── Dramatic
    ↓
    └── Radius Variants (3)
        ├── Sharp
        ├── Rounded (recommended)
        └── Pill
    ↓
Complete Token Set with Variants
```

---

## Color Scheme Variants

### 1. Light Theme (Recommended)

**Target**: Default daytime use, standard web/mobile
**WCAG**: AA compliant (4.5:1 minimum)

**Generation Method**:
```python
def generate_light_theme(base_palette: Dict) -> Dict:
    """
    Light theme from base colors
    - Keep saturated colors for accents
    - Use light neutrals for backgrounds
    - Dark text on light backgrounds
    """

    return {
        "variant_name": "light",
        "description": "Light theme - daytime use",
        "palette": {
            "primary": base_palette["primary"],      # Keep base
            "secondary": base_palette["secondary"],
            "background": "#FFFFFF",                 # White bg
            "surface": "#F5F5F5",                    # Light gray
            "text": "#212121",                       # Dark text
            "border": "#E0E0E0"                      # Light border
        },
        "semantic": {
            "text": {
                "primary": "#212121",                # 87% black
                "secondary": "#757575",              # 60% black
                "disabled": "#9E9E9E"                # 38% black
            },
            "ui": {
                "background": "#FFFFFF",
                "surface": "#F5F5F5",
                "border": "#E0E0E0",
                "divider": "#E0E0E0"
            }
        },
        "wcag_level": "AA",
        "recommended": True,
        "rank": 1,
        "use_case": "Default desktop and mobile, daytime use, standard web applications"
    }
```

**Visual Example**:
```
LIGHT THEME
┌─────────────────────────────────┐
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │ ← #FFFFFF background
│                                  │
│  ████ Primary Accent #646cff    │ ← Saturated colors pop
│  ■■■■ Text #212121               │ ← Dark text, high contrast
│  ░░░░ Surface #F5F5F5            │ ← Subtle elevation
│  ──── Border #E0E0E0             │ ← Light dividers
│                                  │
└─────────────────────────────────┘
```

---

### 2. Dark Theme

**Target**: Night mode, OLED screens, reduced eye strain
**WCAG**: AA compliant (4.5:1 minimum)

**Generation Method**:
```python
def generate_dark_theme(base_palette: Dict) -> Dict:
    """
    Dark theme from base colors
    - Invert luminance while maintaining hue
    - Use dark backgrounds (not pure black - OLED smearing)
    - Light text on dark backgrounds
    - Reduce saturation slightly (prevent oversaturation)
    """

    # Invert luminance in LAB color space
    def invert_luminance(hex_color: str) -> str:
        rgb = hex_to_rgb(hex_color)
        lab = rgb_to_lab(rgb)

        # Invert L channel (0-100)
        lab[0] = 100 - lab[0]

        # Reduce saturation by 20% (prevents oversaturation in dark mode)
        lab[1] *= 0.8
        lab[2] *= 0.8

        return lab_to_hex(lab)

    return {
        "variant_name": "dark",
        "description": "Dark theme - night mode",
        "palette": {
            "primary": desaturate(base_palette["primary"], 0.8),
            "secondary": desaturate(base_palette["secondary"], 0.8),
            "background": "#121212",             # Dark gray (not pure black)
            "surface": "#1E1E1E",                # Elevated surface
            "text": "#FFFFFF",                   # White text
            "border": "#2C2C2C"                  # Dark border
        },
        "semantic": {
            "text": {
                "primary": "#FFFFFF",            # 87% white
                "secondary": "#B3B3B3",          # 60% white
                "disabled": "#757575"            # 38% white
            },
            "ui": {
                "background": "#121212",
                "surface": "#1E1E1E",
                "border": "#2C2C2C",
                "divider": "#2C2C2C"
            }
        },
        "wcag_level": "AA",
        "recommended": False,
        "rank": 2,
        "use_case": "Night mode, OLED screens, low-light environments, reduced eye strain"
    }
```

**Visual Example**:
```
DARK THEME
┌─────────────────────────────────┐
│ ████████████████████████████████ │ ← #121212 background
│                                  │
│  ░░░░ Primary Accent #7481ff    │ ← Desaturated colors
│  ████ Text #FFFFFF               │ ← Light text
│  ████ Surface #1E1E1E            │ ← Elevated surface
│  ──── Border #2C2C2C             │ ← Subtle dividers
│                                  │
└─────────────────────────────────┘
```

---

### 3. High Contrast Theme

**Target**: WCAG AAA compliance, accessibility-first
**WCAG**: AAA compliant (7:1 minimum)

**Generation Method**:
```python
def generate_high_contrast_theme(base_palette: Dict) -> Dict:
    """
    High contrast theme for maximum accessibility
    - Pure black/white backgrounds
    - Maximum contrast ratios (7:1+)
    - Bold, clear separations
    - No subtle grays
    """

    return {
        "variant_name": "high_contrast",
        "description": "Maximum accessibility - WCAG AAA",
        "palette": {
            "primary": "#0000FF",                # Pure blue (high contrast)
            "secondary": "#00CC00",              # Pure green
            "background": "#FFFFFF",             # Pure white
            "surface": "#FFFFFF",
            "text": "#000000",                   # Pure black
            "border": "#000000"                  # Pure black borders
        },
        "semantic": {
            "text": {
                "primary": "#000000",            # Pure black
                "secondary": "#000000",          # No subtle grays
                "disabled": "#666666"            # Still high contrast
            },
            "ui": {
                "background": "#FFFFFF",
                "surface": "#FFFFFF",
                "border": "#000000",
                "divider": "#000000"
            }
        },
        "wcag_level": "AAA",
        "recommended": False,
        "rank": 3,
        "use_case": "Vision impairments, low vision users, maximum accessibility compliance"
    }
```

**Visual Example**:
```
HIGH CONTRAST THEME
┌─────────────────────────────────┐
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │ ← #FFFFFF pure white
│                                  │
│  ████ Primary #0000FF (pure)    │ ← Maximum saturation
│  ████ Text #000000 (pure black) │ ← Pure black text
│  ░░░░ Surface #FFFFFF            │ ← No subtle grays
│  ████ Border #000000             │ ← Bold dividers
│                                  │
│  Contrast: 21:1 (AAA+++)        │
└─────────────────────────────────┘
```

---

## Spacing Scale Variants

### 1. Compact (80% Scale)

**Target**: Mobile devices, dense information displays
**Multiplier**: 0.8×

```python
def generate_compact_spacing(base_spacing: Dict) -> Dict:
    """Mobile-optimized tight spacing"""

    return {
        "variant_name": "compact",
        "description": "Tight spacing for mobile/dense UIs",
        "spacing": {
            "xs": int(base_spacing["xs"] * 0.8),    # 4 → 3
            "sm": int(base_spacing["sm"] * 0.8),    # 8 → 6
            "md": int(base_spacing["md"] * 0.8),    # 16 → 13
            "lg": int(base_spacing["lg"] * 0.8),    # 24 → 19
            "xl": int(base_spacing["xl"] * 0.8),    # 32 → 26
            "xxl": int(base_spacing["xxl"] * 0.8)   # 48 → 38
        },
        "target_viewport": "320-640px (mobile)",
        "design_style": "Compact, information-dense",
        "rank": 1
    }
```

**Use Case**: Mobile phones, tablets in portrait, compact mode preference

---

### 2. Comfortable (100% Scale - Recommended)

**Target**: Desktop, standard viewing
**Multiplier**: 1.0× (unchanged)

```python
def generate_comfortable_spacing(base_spacing: Dict) -> Dict:
    """Standard comfortable spacing"""

    return {
        "variant_name": "comfortable",
        "description": "Standard spacing - balanced and ergonomic",
        "spacing": base_spacing,  # Unchanged
        "target_viewport": "768-1920px (desktop)",
        "design_style": "Balanced, comfortable",
        "recommended": True,
        "rank": 1
    }
```

---

### 3. Spacious (125% Scale)

**Target**: Accessibility, large screens, presentation mode
**Multiplier**: 1.25×

```python
def generate_spacious_spacing(base_spacing: Dict) -> Dict:
    """Generous spacing for accessibility"""

    return {
        "variant_name": "spacious",
        "description": "Generous spacing for accessibility/large screens",
        "spacing": {
            "xs": int(base_spacing["xs"] * 1.25),   # 4 → 5
            "sm": int(base_spacing["sm"] * 1.25),   # 8 → 10
            "md": int(base_spacing["md"] * 1.25),   # 16 → 20
            "lg": int(base_spacing["lg"] * 1.25),   # 24 → 30
            "xl": int(base_spacing["xl"] * 1.25),   # 32 → 40
            "xxl": int(base_spacing["xxl"] * 1.25)  # 48 → 60
        },
        "target_viewport": "1920px+ (large displays)",
        "design_style": "Generous, accessible, presentation mode",
        "accessibility": "Easier touch targets, improved readability",
        "rank": 3
    }
```

---

## Shadow Depth Variants

### 1. Subtle (0.5× Depth)

**Target**: Flat design, minimal elevation
**Multiplier**: 0.5× blur, 0.6× opacity

```python
def generate_subtle_shadows(base_shadows: Dict) -> Dict:
    """Minimal shadows for flat design"""

    def reduce_shadow(shadow_css: str) -> str:
        # Parse CSS box-shadow: "0 4px 8px rgba(0,0,0,0.16)"
        blur = extract_blur(shadow_css) * 0.5
        opacity = extract_opacity(shadow_css) * 0.6

        return f"0 {offset}px {blur}px rgba(0,0,0,{opacity})"

    return {
        "variant_name": "subtle",
        "description": "Minimal shadows - flat design aesthetic",
        "shadow": {
            k: reduce_shadow(v) for k, v in base_shadows.items()
        },
        "design_style": "Flat, minimal, modern",
        "rank": 1
    }
```

**Example**:
```
Base:   0 4px 8px rgba(0,0,0,0.16)
Subtle: 0 2px 4px rgba(0,0,0,0.10)  ← Softer, less dramatic
```

---

### 2. Moderate (1.0× Depth - Recommended)

**Target**: Standard Material Design
**Multiplier**: 1.0× (unchanged)

---

### 3. Dramatic (1.8× Depth)

**Target**: High-impact, bold design
**Multiplier**: 1.8× blur, 1.3× opacity

```python
def generate_dramatic_shadows(base_shadows: Dict) -> Dict:
    """Bold shadows for high-impact design"""

    def amplify_shadow(shadow_css: str) -> str:
        blur = extract_blur(shadow_css) * 1.8
        opacity = min(extract_opacity(shadow_css) * 1.3, 0.5)  # Cap at 0.5

        return f"0 {offset}px {blur}px rgba(0,0,0,{opacity})"

    return {
        "variant_name": "dramatic",
        "description": "Bold shadows - high visual impact",
        "shadow": {
            k: amplify_shadow(v) for k, v in base_shadows.items()
        },
        "design_style": "Bold, dramatic, 3D-like",
        "rank": 3
    }
```

**Example**:
```
Base:     0 4px 8px rgba(0,0,0,0.16)
Dramatic: 0 7px 14px rgba(0,0,0,0.21)  ← Deeper, more pronounced
```

---

## Border Radius Variants

### 1. Sharp (0px)

**Target**: Corporate, angular, technical
**Multiplier**: 0× (zero radius)

```python
def generate_sharp_radius(base_radius: Dict) -> Dict:
    """Angular design - no rounded corners"""

    return {
        "variant_name": "sharp",
        "description": "Angular design - 0px radius",
        "radius": {
            "sm": 0,
            "md": 0,
            "lg": 0,
            "full": 0
        },
        "design_style": "Corporate, angular, technical, modern minimalism",
        "rank": 1
    }
```

---

### 2. Rounded (1.0× - Recommended)

**Target**: Balanced, friendly, standard
**Multiplier**: 1.0× (unchanged)

```python
def generate_rounded_radius(base_radius: Dict) -> Dict:
    """Balanced rounded corners"""

    return {
        "variant_name": "rounded",
        "description": "Balanced rounded corners - standard",
        "radius": base_radius,  # Unchanged (typically 4-12px)
        "design_style": "Friendly, balanced, modern",
        "recommended": True,
        "rank": 1
    }
```

---

### 3. Pill (3.0× or 50%)

**Target**: Organic, playful, friendly
**Multiplier**: 3.0× or use pill shape

```python
def generate_pill_radius(base_radius: Dict) -> Dict:
    """Pill-shaped elements"""

    return {
        "variant_name": "pill",
        "description": "Pill shapes - organic and friendly",
        "radius": {
            "sm": int(base_radius["sm"] * 3),    # 4 → 12
            "md": int(base_radius["md"] * 3),    # 8 → 24
            "lg": int(base_radius["lg"] * 3),    # 12 → 36
            "full": 9999                         # Pill shape
        },
        "design_style": "Organic, friendly, playful, consumer apps",
        "rank": 3
    }
```

---

## Variant Selection & UI

### Frontend Integration

**File**: `frontend/src/hooks/useVariantSelection.ts`

```typescript
interface VariantMetadata {
  variant_name: string
  description: string
  use_case?: string
  recommended?: boolean
  rank: number
  wcag_level?: string
  target_viewport?: string
  design_style?: string
}

function useVariantSelection() {
  const [selectedVariants, setSelectedVariants] = useState({
    color: "light",
    spacing: "comfortable",
    shadow: "moderate",
    radius: "rounded"
  })

  // Auto-select recommended variants
  useEffect(() => {
    const recommended = {
      color: findRecommended(colorVariants),      // "light"
      spacing: findRecommended(spacingVariants),  // "comfortable"
      shadow: findRecommended(shadowVariants),    // "moderate"
      radius: findRecommended(radiusVariants)     // "rounded"
    }
    setSelectedVariants(recommended)
  }, [])

  return { selectedVariants, setSelectedVariants }
}
```

### UI Layout

**Extract Page** (3-column layout):
```
┌───────────────┬────────────────────┬──────────────┐
│ Upload        │ Token Display      │ Variants     │
│               │                     │              │
│ [Image]       │ Colors:            │ Color:       │
│               │ ████ #646cff       │ ○ Light ★    │
│               │                     │ ○ Dark       │
│               │ Spacing:           │ ○ High Cont. │
│               │ xs: 4, sm: 8       │              │
│               │                     │ Spacing:     │
│               │ Shadows:           │ ○ Compact    │
│               │ Level1, Level2     │ ● Comf. ★    │
│               │                     │ ○ Spacious   │
└───────────────┴────────────────────┴──────────────┘
```

**Export Page** (60/40 split):
```
┌─────────────────────────┬─────────────────┐
│ Token Preview           │ Export Options  │
│                         │                 │
│ Selected Variants:      │ Format:         │
│ • Light theme          │ ☑ CSS Variables │
│ • Comfortable spacing  │ ☑ TypeScript    │
│ • Moderate shadows     │ ☑ Tailwind      │
│ • Rounded corners      │ ☐ JUCE          │
│                         │                 │
│ [Live Preview]         │ [Download All]  │
└─────────────────────────┴─────────────────┘
```

---

## Implementation Guide

### Generate All Variants

```python
from extractors.variant_generator import VariantGenerator

# Base tokens from extraction
base_tokens = extract_tokens(image)

# Generate variants
generator = VariantGenerator()

variants = {
    "color_variants": generator.generate_color_variants(base_tokens["palette"]),
    "spacing_variants": generator.generate_spacing_variants(base_tokens["spacing"]),
    "shadow_variants": generator.generate_shadow_variants(base_tokens["shadow"]),
    "radius_variants": generator.generate_radius_variants(base_tokens["radius"])
}

# Each returns List[Dict] with 3 variants
```

### Export Selected Variant

```python
def export_variant_combination(
    selected_variants: Dict[str, str],  # {"color": "dark", "spacing": "compact"}
    all_variants: Dict,
    format: str = "css"
) -> str:
    """Export specific variant combination"""

    # Get selected variants
    color_variant = find_variant(all_variants["color_variants"], selected_variants["color"])
    spacing_variant = find_variant(all_variants["spacing_variants"], selected_variants["spacing"])

    # Generate export
    if format == "css":
        return generate_css_variables({
            "palette": color_variant["palette"],
            "spacing": spacing_variant["spacing"]
        })
```

---

## Related Documentation

- [Token Schema Guide](TOKEN_SCHEMA_GUIDE.md) - Base token schemas
- [Storytelling Framework](STORYTELLING_FRAMEWORK.md) - Variant narratives
- [Generator Export Guide](GENERATOR_EXPORT_GUIDE.md) - Platform exports

---

**Last Updated**: 2025-11-11
**Version**: 3.1
**Status**: Production Ready
**Variants per Category**: 3

# Token Variant System Integration Guide

## Overview

The variant generator system creates multiple design options for each token category, giving users choice while maintaining design consistency.

## Completed Components

### ✅ Typography Variants (Integrated)
**File:** `extractors/extractors/typography_extractor.py`
- ✅ `match_typography_profiles_multi()` - Returns top 3 font options with scores
- ✅ `extract_typography_tokens(include_options=True)` - Includes alternatives
- ✅ Helper functions for match quality and use case recommendations

**Output Structure:**
```python
{
    "profile": "retro_technical",  # Primary option
    "description": "...",
    "family": {...},
    "weights": {...},
    "scale": {...},
    "match_percentage": 87,
    "options": [  # Alternative options
        {
            "profile": "modern_minimal",
            "match_percentage": 72,
            "rank": 2,
            "recommendation": "Good alternative option",
            # ... full typography system
        },
        {
            "profile": "vintage_warm",
            "match_percentage": 65,
            "rank": 3,
            # ...
        }
    ]
}
```

### ✅ Variant Generator Functions (Ready)
**File:** `extractors/extractors/variant_generator.py`

1. **`generate_color_scheme_variants(base_palette)`**
   - Light theme (default, brightened)
   - Dark theme (inverted luminance)
   - High contrast (WCAG AAA)

2. **`generate_spacing_scale_variants(base_spacing)`**
   - Compact (80% - mobile/dense)
   - Comfortable (100% - default)
   - Spacious (125% - accessibility/large screens)

3. **`generate_shadow_depth_variants(base_shadow)`**
   - Subtle (0.5x blur, 0.6x opacity - flat design)
   - Moderate (1x - default)
   - Dramatic (1.8x blur, 1.3x opacity - high impact)

4. **`generate_border_radius_variants(base_radius)`**
   - Sharp (0px - angular/corporate)
   - Rounded (default - balanced)
   - Pill (3x radius - organic/friendly)

## Integration Steps

### Step 1: Import Variant Generators

In any extractor file:
```python
from .variant_generator import (
    generate_color_scheme_variants,
    generate_spacing_scale_variants,
    generate_shadow_depth_variants,
    generate_border_radius_variants
)
```

### Step 2: Add `include_variants` Parameter

Update extraction functions to accept optional parameter:
```python
def extract_color_tokens(img_rgb, include_variants=True):
    # Extract base palette
    base_palette = role_map_from_palette(items)

    if include_variants:
        # Generate 3 color scheme options
        variants = generate_color_scheme_variants(base_palette)

        return {
            "palette": base_palette,  # Primary option
            "variants": variants,      # Alternative options
            "_metadata": {
                "variant_count": len(variants),
                "recommended": "light"  # or variants[0]["variant_name"]
            }
        }
    else:
        # Legacy single-option mode
        return {"palette": base_palette}
```

### Step 3: Update Output Structure

Each variant includes rich metadata for user decision-making:

```python
# Color variant structure
{
    "variant_name": "dark",
    "description": "Dark theme - reduces eye strain in low-light environments",
    "palette": {...},  # Transformed colors
    "background": "#0a0a0a",
    "surface": "#1a1a1a",
    "use_case": "Preferred for night-time use, developers, and OLED displays",
    "wcag_level": "AA",
    "recommended": False,  # Only one variant is recommended=True
    "rank": 2
}

# Spacing variant structure
{
    "variant_name": "spacious",
    "description": "Spacious spacing - enhanced readability and touch targets",
    "spacing": {...},  # Scaled values
    "multiplier": 1.25,
    "use_case": "Large displays, accessibility mode, kiosks, TV interfaces",
    "target_viewport": "> 1440px (large desktop/TV)",
    "recommended": False,
    "rank": 3
}
```

### Step 4: Frontend Display

The frontend should display variants as selectable options:

```typescript
// Example ColorPalette component with variants
<div className="token-section">
  <h3>🎨 Color Palette</h3>

  {/* Variant Selector */}
  <div className="variant-selector">
    <button className={activeVariant === 'light' ? 'active' : ''}>
      Light Theme (Recommended)
    </button>
    <button className={activeVariant === 'dark' ? 'active' : ''}>
      Dark Theme
    </button>
    <button className={activeVariant === 'high_contrast' ? 'active' : ''}>
      High Contrast (AAA)
    </button>
  </div>

  {/* Show selected variant's palette */}
  <ColorSwatches colors={selectedVariant.palette} />

  {/* Variant metadata */}
  <p className="variant-description">{selectedVariant.description}</p>
  <p className="variant-use-case">
    <strong>Best for:</strong> {selectedVariant.use_case}
  </p>
</div>
```

## Usage Examples

### Example 1: Color Variants

```python
# Extract base palette
items = kmeans_palette(img_rgb, k=12)
base_palette = role_map_from_palette(items)

# Generate variants
variants = generate_color_scheme_variants(base_palette)

# Result structure
variants = [
    {
        "variant_name": "light",
        "palette": {
            "primary": "#F15925",    # Slightly brightened
            "secondary": "#4A90E2",
            "neutral": "#F5F5F5",
            # ...
        },
        "recommended": True,
        "rank": 1
    },
    {
        "variant_name": "dark",
        "palette": {
            "primary": "#D14020",    # Inverted luminance
            "secondary": "#3A70B2",
            "neutral": "#1A1A1A",
            # ...
        },
        "recommended": False,
        "rank": 2
    },
    {
        "variant_name": "high_contrast",
        "palette": {
            "primary": "#FF5500",    # Pushed to extremes
            "secondary": "#0066FF",
            "neutral": "#FFFFFF",
            # ...
        },
        "wcag_level": "AAA",
        "recommended": False,
        "rank": 3
    }
]
```

### Example 2: Spacing Variants

```python
# Extract base spacing
base_spacing = {
    "xs": 4,
    "sm": 8,
    "md": 16,
    "lg": 24,
    "xl": 32
}

# Generate variants
variants = generate_spacing_scale_variants(base_spacing)

# Result
variants = [
    {
        "variant_name": "compact",
        "spacing": {"xs": 3, "sm": 6, "md": 13, "lg": 19, "xl": 26},
        "multiplier": 0.8,
        "target_viewport": "< 768px (mobile)",
        "recommended": False
    },
    {
        "variant_name": "comfortable",
        "spacing": {"xs": 4, "sm": 8, "md": 16, "lg": 24, "xl": 32},
        "multiplier": 1.0,
        "recommended": True  # Default
    },
    {
        "variant_name": "spacious",
        "spacing": {"xs": 5, "sm": 10, "md": 20, "lg": 30, "xl": 40},
        "multiplier": 1.25,
        "target_viewport": "> 1440px (large desktop/TV)",
        "recommended": False
    }
]
```

### Example 3: Shadow Variants

```python
# Base shadows
base_shadow = {
    "sm": "0px 1px 2px rgba(0,0,0,0.1)",
    "md": "0px 4px 6px rgba(0,0,0,0.1)",
    "lg": "0px 10px 15px rgba(0,0,0,0.1)"
}

# Generate variants
variants = generate_shadow_depth_variants(base_shadow)

# Result shows intensity scaling
variants[0]  # Subtle: "0px 1px 1px rgba(0,0,0,0.06)"
variants[1]  # Moderate: original values
variants[2]  # Dramatic: "0px 1px 4px rgba(0,0,0,0.13)"
```

## Benefits

### For Users
- **Choice**: Multiple aesthetically coherent options per category
- **Guidance**: Each variant includes use case recommendations
- **Confidence**: Match scores and quality ratings help decision-making
- **Accessibility**: High-contrast and spacious variants built-in

### For Developers
- **Consistency**: All variants follow same design principles
- **Metadata**: Rich context for smart defaults and suggestions
- **Flexibility**: Easy to add more variants or customize existing ones
- **Backward Compatible**: Works with existing single-option code when `include_variants=False`

## Testing

See `test_variant_integration.py` for comprehensive test coverage of:
- Variant generation from real image data
- Output structure validation
- Metadata completeness
- Recommended variant selection
- Use case descriptions

## Next Steps

1. ✅ Typography variants - COMPLETED
2. ⏳ Integrate color variants into color_extractor
3. ⏳ Integrate spacing variants into spacing_extractor
4. ⏳ Integrate shadow variants into shadow_extractor
5. ⏳ Integrate border-radius variants into border_radius_extractor
6. ⏳ Update frontend to display variant selectors
7. ⏳ Add variant export to all export formats (CSS, JSON, React, Figma, JUCE)

## Migration Path

### Phase 1: Backend (Week 1)
- Add `include_variants` parameter to all extractors
- Default to `True` for new extractions
- Maintain legacy mode for backward compatibility

### Phase 2: Frontend (Week 2)
- Add variant selector components
- Update TokenDisplay to show options
- Add variant preview in Export page

### Phase 3: Export (Week 3)
- Update export templates to include all selected variants
- Add "export all variants" option
- Generate variant-specific CSS/JSON files

## Example: Complete Integration

```python
# In main extraction pipeline
def extract_all_tokens(img_rgb, include_variants=True):
    tokens = {}

    # Color extraction with variants
    color_data = extract_color_tokens(img_rgb, include_variants)
    tokens['palette'] = color_data['palette']  # Primary
    if include_variants:
        tokens['palette_variants'] = color_data['variants']

    # Typography with variants (already integrated)
    typo_data = extract_typography_tokens(img_rgb, include_variants)
    tokens['typography'] = typo_data  # Includes options if enabled

    # Spacing with variants
    spacing_data = extract_spacing_tokens(img_rgb, include_variants)
    tokens['spacing'] = spacing_data['spacing']  # Primary
    if include_variants:
        tokens['spacing_variants'] = spacing_data['variants']

    return tokens
```

---

**Status:** Variant generator system complete and ready for integration. Typography already integrated, other categories ready to be updated.

# Phase 13: Quick Start Guide

## What is Phase 13?

**Phase 13 fundamentally transforms the UI Layer Decomposer from an extraction tool to a generation engine.**

### The Big Change

- **Phase 12**: Reference Image → **Extract** existing UI elements
- **Phase 13**: Reference Image → **Analyze** visual style → **Generate** NEW elements

Instead of cutting out existing components, Phase 13 learns the design language and creates entirely new, consistent components.

---

## Quick Start

### 1. Installation

```bash
# Phase 13 uses the same dependencies as Phase 12
pip install -r requirements.txt
```

### 2. Basic Usage

```bash
# Analyze a reference UI and generate a design system
python phase13_pipeline.py your-beautiful-ui.png
```

That's it! Phase 13 will:
1. Extract the visual DNA from your reference
2. Detect design patterns
3. Extract style rules
4. **Generate NEW components** following those rules

### 3. View Results

```bash
# Output structure
output-phase13/
├── analysis/
│   ├── visual_dna.json        # Extracted style characteristics
│   └── style_rules.json       # Formalized design rules
└── design-system/
    ├── components/            # Generated components (PNG + JSON)
    │   ├── button_default.png
    │   ├── button_hover.png
    │   ├── input_default.png
    │   └── card_default.png
    ├── variations/            # Size, color, theme variations
    │   ├── button_default/
    │   │   ├── button_default_small.png
    │   │   ├── button_default_large.png
    │   │   ├── button_default_primary.png
    │   │   └── button_default_dark.png
    └── library_metadata.json  # Library statistics
```

---

## What Gets Generated?

### Component Types

Phase 13 generates:
- **Buttons** (primary, hover, active, disabled states)
- **Input Fields** (default, focus, disabled states)
- **Cards** (with headers, footers)

### Variations

For each component, Phase 13 creates:
- **Size variations**: small, medium, large, xlarge
- **Color variations**: Using extracted color palette
- **Theme variations**: light, dark

---

## Understanding the Output

### 1. Visual DNA (`visual_dna.json`)

The extracted "genetic code" of the design:

```json
{
  "color_genome": {
    "primary_colors": [[66, 133, 244], ...],
    "color_ratios": {"primary": 0.3, "secondary_0": 0.2},
    "gradient_patterns": [...]
  },
  "shape_language": {
    "corner_radius_base": 8.0,
    "geometric_style": "rounded",
    "aspect_ratios": [1.0, 1.5, 2.0]
  },
  "spatial_rhythm": {
    "base_unit": 8.0,
    "spacing_scale": [1.0, 2.0, 3.0, 4.0]
  },
  "depth_style": "subtle",
  ...
}
```

### 2. Style Rules (`style_rules.json`)

Actionable rules for generation:

```json
{
  "rules": [
    {
      "rule_id": "color_primary",
      "rule_type": "color",
      "priority": "critical",
      "parameters": {
        "color": "rgb(66, 133, 244)",
        "usage": ["primary_buttons", "links"]
      }
    },
    {
      "rule_id": "spacing_base_unit",
      "rule_type": "spacing",
      "priority": "critical",
      "parameters": {
        "base_unit": 8.0
      }
    },
    ...
  ]
}
```

---

## Examples

### Example 1: Material Design Reference

```bash
python phase13_pipeline.py material-design-sample.png -o material-system
```

**Result**: A complete design system with Material-inspired:
- Rounded corners (4-8px radius)
- Subtle shadows
- Bold primary colors
- 8px grid spacing

### Example 2: Flat Design Reference

```bash
python phase13_pipeline.py flat-ui-sample.png -o flat-system
```

**Result**: Components with:
- Sharp corners (0px radius)
- No shadows
- Vibrant colors
- Consistent spacing

### Example 3: Glassmorphism Reference

```bash
python phase13_pipeline.py glass-ui-sample.png -o glass-system
```

**Result**: Components featuring:
- Large corner radius (12-16px)
- Dramatic depth/shadows
- Translucent effects
- Generous spacing

---

## Command Line Options

```bash
python phase13_pipeline.py [OPTIONS] REFERENCE_IMAGE

Options:
  -o, --output DIR    Output directory (default: output-phase13)
  -h, --help          Show help message
```

---

## Use Cases

### 1. Design System Generation

**Scenario**: You have a beautiful UI mockup but need a complete component library.

**Solution**:
```bash
python phase13_pipeline.py mockup.png -o design-system
```

Get hundreds of consistent components automatically generated.

### 2. Style Exploration

**Scenario**: Exploring different visual styles for your product.

**Solution**: Run Phase 13 on multiple reference images:
```bash
python phase13_pipeline.py modern-style.png -o style-a
python phase13_pipeline.py classic-style.png -o style-b
python phase13_pipeline.py playful-style.png -o style-c
```

Compare generated design systems.

### 3. Brand Consistency

**Scenario**: Ensure new components match existing design language.

**Solution**: Use existing UI screenshot as reference:
```bash
python phase13_pipeline.py existing-ui-screenshot.png -o new-components
```

Phase 13 extracts the style and generates new components that match perfectly.

---

## Architecture Overview

```
Reference Image
      ↓
[Visual DNA Extraction]
      ↓ extracts →  Color genome, shape language, spacing rhythm,
      ↓             material properties, depth style, etc.
      ↓
[Pattern Detection]
      ↓ identifies → Repetition, symmetry, grid, hierarchy,
      ↓              design motifs
      ↓
[Style Rule Extraction]
      ↓ formalizes → Color rules, spacing rules, shape rules,
      ↓              shadow rules, material rules
      ↓
[Parametric Generation]
      ↓ creates →    NEW buttons, inputs, cards, etc.
      ↓              following extracted rules
      ↓
[Variation Synthesis]
      ↓ generates →  Size, color, and theme variations
      ↓
[Component Library]
      ✓ Complete design system ready to use
```

---

## Key Differences from Phase 12

| Aspect | Phase 12 | Phase 13 |
|--------|----------|----------|
| **Goal** | Extract existing elements | Generate new elements |
| **Input** | UI screenshot | Reference image |
| **Process** | Segmentation (SAM, CLIP) | Style analysis |
| **Output** | PNG layers of existing UI | New component library |
| **Use Case** | Decompose existing design | Create design system |
| **Result** | Copy of original elements | Inspired new components |

---

## Troubleshooting

### Issue: Generated components don't match reference

**Solution**: The reference image may be too complex or have inconsistent styles. Try:
1. Use a simpler reference with clear design patterns
2. Check `visual_dna.json` to see what was extracted
3. Review `style_rules.json` for accuracy

### Issue: Components look too similar

**Solution**: Phase 13 prioritizes consistency. To increase variety:
1. Use references with more diverse patterns
2. Check the variations directory for different options

### Issue: Colors don't match

**Solution**:
1. Review `visual_dna.json` → `color_genome`
2. Ensure reference image has clear, dominant colors
3. Check `style_rules.json` → `color_primary` rule

---

## Next Steps

1. **Explore the generated components** in `output-phase13/design-system/components/`
2. **Review the extracted rules** in `output-phase13/analysis/style_rules.json`
3. **Check variations** in `output-phase13/design-system/variations/`
4. **Try different references** to see how Phase 13 adapts

---

## Advanced Usage

See [PHASE_13_DESIGN.md](PHASE_13_DESIGN.md) for:
- Detailed architecture
- Style transfer implementation
- Procedural generation techniques
- Custom component types
- Advanced variation strategies

---

**Phase 13 transforms inspiration into implementation. 🎨 → 🚀**

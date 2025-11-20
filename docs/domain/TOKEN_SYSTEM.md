# Design Token System

**Version:** 3.1 (Adapted for Copy That) | **Last Updated:** 2025-11-19

This document describes the complete design token system used by Copy That - the foundational language for extracting, representing, and generating design systems from images.

---

## 📚 What Are Design Tokens?

Design tokens are **discrete, named design decisions** that represent the building blocks of a design system:

```
Color:       #FF6B35 (primary brand color)
Spacing:     16px (card padding)
Typography:  "Inter", 14px, 500 weight
Shadow:      0 4px 8px rgba(0,0,0,0.1)
Animation:   100ms ease-out-cubic
```

Each token has:
- **Value** - The actual design decision (e.g., #FF6B35)
- **Name** - Semantic label (e.g., "primary-brand-color")
- **Category** - Token type (color, spacing, typography, etc.)
- **Context** - Where and how it's used
- **Metadata** - Confidence, source, relationships

---

## 🏗️ Token System Architecture

Copy That organizes tokens into 9 core categories:

```
Design Token System
├── 1. Color
│   ├── Brand colors (primary, secondary, tertiary)
│   ├── Neutral colors (grays, whites)
│   ├── State colors (success, warning, danger, info)
│   └── Semantic roles (text, background, border)
│
├── 2. Spacing
│   ├── Base unit (typically 4px or 8px)
│   ├── Scale (xs, sm, md, lg, xl, 2xl)
│   ├── Padding (internal spacing)
│   └── Margins (external spacing)
│
├── 3. Typography
│   ├── Font families (system stack)
│   ├── Font sizes (scale: h1, h2, body, caption)
│   ├── Font weights (300, 400, 500, 600, 700)
│   ├── Line heights
│   └── Letter spacing
│
├── 4. Shadow
│   ├── Elevation levels (shadow-1 to shadow-4)
│   ├── Blur radius
│   ├── X/Y offset
│   └── Opacity/spread
│
├── 5. Border
│   ├── Width (thin, medium, thick)
│   ├── Radius (sharp, subtle, rounded, pill)
│   ├── Style (solid, dashed, dotted)
│   └── Color
│
├── 6. Opacity
│   ├── Subtle (10%, used for hover states)
│   ├── Medium (50%, used for disabled states)
│   ├── Solid (100%, fully opaque)
│   └── Custom scales
│
├── 7. State Layer (Material Design 3)
│   ├── Hover state styling
│   ├── Focus state styling
│   ├── Pressed state styling
│   └── Disabled state styling
│
├── 8. Gradient
│   ├── Multi-stop color gradients
│   ├── Direction/angle
│   ├── Color positions
│   └── Animation curves
│
└── 9. Animation
    ├── Duration (timing curves)
    ├── Easing functions
    ├── Delay
    └── Iteration behavior
```

---

## 🎨 Token Examples

### Foundation Token: Color

```json
{
  "id": "color-primary",
  "name": "Primary Brand Color",
  "category": "color",
  "value": "#FF6B35",
  "type": "brand",
  "semantic_name": "vibrant-orange",
  "confidence": 0.95,
  "extracted_from": "image_uuid_123",
  "metadata": {
    "hue": "orange",
    "temperature": "warm",
    "saturation": "vibrant",
    "lightness": "medium",
    "wcag_contrast_with_white": 5.2,
    "wcag_contrast_with_black": 3.8
  },
  "created_at": "2025-11-19T10:30:00Z"
}
```

### Foundation Token: Spacing

```json
{
  "id": "spacing-md",
  "name": "Medium Spacing",
  "category": "spacing",
  "value": 16,
  "unit": "px",
  "scale": "md",
  "semantic_name": "card-padding",
  "confidence": 0.92,
  "extracted_from": "image_uuid_123",
  "metadata": {
    "base_unit": 4,
    "scale_position": 4,
    "use_case": "Card internal padding",
    "rhythm": "comfortable"
  },
  "created_at": "2025-11-19T10:30:00Z"
}
```

### Foundation Token: Typography

```json
{
  "id": "typography-body",
  "name": "Body Text",
  "category": "typography",
  "value": {
    "font_family": "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
    "font_size": 14,
    "font_weight": 400,
    "line_height": 1.5,
    "letter_spacing": 0
  },
  "semantic_name": "readable-body-text",
  "confidence": 0.88,
  "extracted_from": "image_uuid_123",
  "metadata": {
    "readability": "excellent",
    "use_case": "Content text",
    "platform_stack": "system"
  },
  "created_at": "2025-11-19T10:30:00Z"
}
```

### Foundation Token: Shadow

```json
{
  "id": "shadow-elevation-1",
  "name": "Elevation Level 1",
  "category": "shadow",
  "value": "0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24)",
  "elevation_level": 1,
  "confidence": 0.85,
  "extracted_from": "image_uuid_123",
  "metadata": {
    "blur_radius": 3,
    "y_offset": 1,
    "x_offset": 0,
    "opacity": 0.12,
    "use_case": "Subtle elevation for cards"
  },
  "created_at": "2025-11-19T10:30:00Z"
}
```

---

## 🔄 Token Flow in Copy That

### From Image to Extracted Tokens

```
1. IMAGE UPLOAD
   └─ User uploads design image/screenshot

2. AI ANALYSIS (Claude Structured Outputs)
   ├─ Detect colors (K-means clustering)
   ├─ Measure spacing (SAM segmentation)
   ├─ Identify typography (font detection)
   ├─ Analyze shadows (depth analysis)
   └─ Extract other tokens

3. SEMANTIC ENRICHMENT
   ├─ Generate semantic names
   ├─ Assign confidence scores
   ├─ Add metadata (harmony, temperature, etc.)
   └─ Calculate relationships

4. DATABASE STORAGE
   ├─ Color tokens → color_tokens table
   ├─ Spacing tokens → spacing_tokens table
   ├─ Typography tokens → typography_tokens table
   └─ etc.

5. FRONTEND DISPLAY
   ├─ Show extracted tokens
   ├─ Display confidence badges
   ├─ Group by category
   └─ Enable editing/refinement

6. CODE GENERATION
   ├─ React CSS variables
   ├─ TypeScript types
   ├─ Figma design tokens
   ├─ Material-UI theme
   └─ Flutter configuration
```

---

## 💾 Database Schema

### color_tokens

```sql
CREATE TABLE color_tokens (
  id SERIAL PRIMARY KEY,
  extraction_job_id INTEGER REFERENCES extraction_jobs(id),
  hex VARCHAR(7) NOT NULL,
  confidence FLOAT CHECK (confidence >= 0 AND confidence <= 1),
  semantic_name VARCHAR(255),
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### spacing_tokens (Similar Structure)

```sql
CREATE TABLE spacing_tokens (
  id SERIAL PRIMARY KEY,
  extraction_job_id INTEGER REFERENCES extraction_jobs(id),
  value INTEGER NOT NULL,
  unit VARCHAR(10) DEFAULT 'px',
  scale VARCHAR(50),
  confidence FLOAT,
  semantic_name VARCHAR(255),
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🎯 Token Usage

### For Designers

**Color tokens provide:**
- Visual consistency across the design system
- Clear naming conventions (semantic names)
- Accessibility validation (WCAG contrast ratios)
- Color harmonies and relationships

**Example:** "Use `color-primary` for all primary actions" (instead of remembering #FF6B35)

### For Developers

**Code generation from tokens:**
- CSS Custom Properties: `var(--color-primary)`
- TypeScript types: `type ColorTokens = { primary: '#FF6B35' }`
- React components: Auto-styled with token values
- Material-UI: Direct theme configuration

**Example in React:**
```tsx
// Generated from tokens
const theme = {
  colors: {
    primary: '#FF6B35',
    spacing: { sm: 8, md: 16, lg: 24 }
  }
};

function Button() {
  return (
    <button style={{
      backgroundColor: theme.colors.primary,
      padding: theme.spacing.md
    }}>
      Click me
    </button>
  );
}
```

---

## 🔐 Token Extraction Quality

### Confidence Scores

Tokens include a **confidence score** (0.0 - 1.0) indicating extraction certainty:

- **0.95-1.0** - Very high confidence (use as-is)
- **0.85-0.95** - High confidence (minor refinement possible)
- **0.75-0.85** - Medium confidence (review recommended)
- **0.60-0.75** - Low confidence (refinement needed)
- **< 0.60** - Very low confidence (manual review required)

**Why confidence matters:**
- Helps identify tokens needing manual refinement
- Enables quality filtering in exports
- Provides transparency in automated systems
- Supports progressive enhancement (start with high-confidence tokens)

---

## 📦 Export Formats

Copy That generates tokens in multiple formats:

### CSS Variables
```css
:root {
  --color-primary: #FF6B35;
  --color-secondary: #0066CC;
  --spacing-md: 16px;
  --font-body: 'Inter', sans-serif;
}

.button {
  background-color: var(--color-primary);
  padding: var(--spacing-md);
  font-family: var(--font-body);
}
```

### TypeScript
```typescript
export const tokens = {
  colors: {
    primary: '#FF6B35',
    secondary: '#0066CC'
  },
  spacing: {
    sm: 8,
    md: 16,
    lg: 24
  }
} as const;
```

### JSON (W3C Design Tokens Format)
```json
{
  "color": {
    "primary": {
      "$value": "#FF6B35",
      "$type": "color",
      "$extensions": {
        "confidence": 0.95,
        "semantic_name": "vibrant-orange"
      }
    }
  }
}
```

### Figma Design Tokens
```json
{
  "colorPrimary": {
    "value": "#FF6B35",
    "type": "color"
  }
}
```

---

## 🔄 Token Versioning

Tokens evolve as designs change:

```
Version 1.0 (Launch)
├─ 8 colors
├─ 5 spacing values
└─ 3 typography styles

Version 1.1 (Minor update)
├─ Added color: dark-mode-primary
├─ No other changes

Version 2.0 (Major redesign)
├─ Redesigned color palette (8 → 12 colors)
├─ Updated spacing scale
└─ Added 2 new token categories
```

Each version maintains **backward compatibility** where possible.

---

## 🛠️ Working with Tokens

### Extracting Tokens (Python)

```python
from copy_that.extractors import ColorExtractor, SpacingExtractor

# Extract colors
colors = ColorExtractor().extract(image_bytes)
# Returns: List[ColorToken]

# Extract spacing
spacing = SpacingExtractor().extract(image_bytes)
# Returns: List[SpacingToken]
```

### Querying Tokens (FastAPI)

```typescript
// Get all color tokens from a job
const colors = await fetch('/api/v1/jobs/123/colors');

// Get specific token
const token = await fetch('/api/v1/tokens/color-primary');

// Export as CSS
const css = await fetch('/api/v1/jobs/123/export?format=css');
```

### Using in Code (React)

```tsx
import { tokens } from './generated/tokens';

function Card() {
  return (
    <div style={{
      backgroundColor: tokens.colors.background,
      padding: tokens.spacing.md,
      fontFamily: tokens.typography.body.fontFamily
    }}>
      Content
    </div>
  );
}
```

---

## 📊 Token Statistics

| Metric | Value |
|--------|-------|
| Core Token Categories | 9 |
| Color tokens per extraction | 8-15 |
| Spacing tokens per extraction | 4-6 |
| Typography families typically found | 2-4 |
| Average extraction time | 2-5 seconds |
| Average confidence score | 0.88 |
| Test coverage | 98%+ |

---

## 🧩 Integration Points

### With Design Tools
- **Figma** - Import/export Design Tokens format
- **Sketch** - Token plugins for design systems
- **Adobe XD** - Integration with design specifications

### With Development Tools
- **React** - CSS-in-JS theme providers
- **Vue** - CSS variables and scoped styles
- **Angular** - Theme configuration
- **Flutter** - Material color scheme
- **iOS** - UIColor/UIColorSet
- **Android** - color.xml resources

### With Platforms
- **Storybook** - Theme configuration
- **Tailwind CSS** - Theme object
- **Material Design** - Theme generation
- **Bootstrap** - SCSS variable export

---

## 🔍 Best Practices

### Naming Conventions

**Good token names:**
- `color-primary-action` - Describes purpose and type
- `spacing-card-padding` - Semantic and location-aware
- `typography-heading-1` - Hierarchical

**Avoid:**
- `blue` - Not semantic
- `padding-16px` - Too specific
- `color-1` - Not descriptive

### Organizing Tokens

**By category first:**
```
colors/
├─ brand/
├─ semantic/
└─ state/

spacing/
├─ padding/
├─ margin/
└─ gap/
```

**Then by usage:**
```
button-padding (spacing)
button-background (color)
button-font (typography)
```

### Scaling Tokens

**For products with multiple apps:**
1. Extract base tokens (core)
2. Create theme variants (light/dark)
3. Platform-specific overrides (mobile, web, desktop)
4. Feature flags for progressive rollout

---

## 📚 Related Documentation

- **DATABASE_SETUP.md** - How tokens are stored
- **PHASE_4_COLOR_VERTICAL_SLICE.md** - Implementation roadmap
- **START_HERE.md** - Getting started guide

---

## 🤔 Common Questions

**Q: Can I have more than 9 token categories?**
A: Yes! These 9 are the foundation. You can add custom categories as needed.

**Q: How often do tokens change?**
A: Typically during design system updates (quarterly) or major redesigns.

**Q: Can I export tokens to multiple formats?**
A: Yes! Copy That generates CSS, TypeScript, JSON, Figma, and more.

**Q: What if token extraction is wrong?**
A: Review confidence scores and manually refine. Low-confidence tokens should be reviewed.

---

**Version:** 3.1 | **Format:** Design Tokens Standard v1.0 | **Last Updated:** 2025-11-19

# Token Explorer: Generic Platform Vision

**Status:** Phase 4 Week 2 - UI/UX Redesign Complete
**Date:** 2025-11-20
**Version:** v0.1.0 (Design System)

## Executive Summary

**Copy That's Token Explorer** is a unified, schema-driven interface for exploring ANY design token type:
- **Color Tokens** (reference implementation, complete)
- **Typography Tokens** (future, same patterns)
- **Spacing Tokens** (future, same patterns)
- **Shadow Tokens** (future, same patterns)
- **Animation Tokens** (future, same patterns)

**Key Principle:** Upload 1-10 images → extract tokens → explore comprehensive token details (visual, information, educational, interactive, narrative) in a single unified interface.

---

## Core User Flow

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: UPLOAD IMAGES (1-10 max)                            │
│ Drag-and-drop or file select → Show preview thumbnails     │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│ STEP 2: TOKEN EXTRACTION PIPELINE                           │
│ Tier 1: OpenCV CV (fast, deterministic)                     │
│ Tier 2: CLIP semantics (zero-cost local)                    │
│ Tier 3: GPT-4V + Claude Vision (reasoning, semantic names)  │
│ Real-time progress updates via WebSocket                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│ STEP 3: TOKEN EXPLORATION STUDIO                            │
│                                                              │
│ ┌─────────────────────────────────────────────────────┐    │
│ │ [Filter] [Sort] [View: Grid/List/Table]     [X]    │    │
│ │                                                     │    │
│ │ ┌──────────────────────────────────────────────┐   │    │
│ │ │ [Swatch]  molten-copper    [🔒 87%]         │   │    │
│ │ │ #F15925   Quick: Edit Dup Delete Details    │   │    │
│ │ │                                              │   │    │
│ │ │ [Swatch]  deep-indigo      [🔒 92%]         │   │    │
│ │ │ #2E3B7D                                      │   │    │
│ │ │                                              │   │    │
│ │ │ [Swatch]  sage-green       [🔒 89%]         │   │    │
│ │ │ #7A9B7E                                      │   │    │
│ │ └──────────────────────────────────────────────┘   │    │
│ └─────────────────────────────────────────────────────┘    │
│                                                              │
│ [INSPECTOR SIDEBAR]          [PLAYGROUND DRAWER]           │
│ Token Details               Interactive Exploration         │
│ ├─ Semantic Name             ├─ Adjust sliders (HSL)       │
│ ├─ Design Intent             ├─ Harmony visualizer         │
│ ├─ Hex/RGB/HSL/Oklch         ├─ Temperature spectrum       │
│ ├─ Confidence Breakdown       └─ Saturation scale          │
│ └─ Relationships (harmony,                                  │
│    temperature, saturation)                                 │
└─────────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│ STEP 4: EXPORT TOKENS                                       │
│ Format: CSS Variables, JSON, Figma, iOS, Android            │
└─────────────────────────────────────────────────────────────┘
```

---

## Design Philosophy

### 1. **Semantic-First, Value-Second**
- Show semantic names before hex codes
- Emphasize meaning: "molten-copper" (not "orange-500")
- Design intent visible: "evokes retro audio warmth"
- Search by meaning, not by value

### 2. **Multi-Tier AI/ML Transparency**
- Show which extractors contributed
- Display confidence breakdown (CV: 95%, GPT-4: 85%, Claude: 92%)
- Users understand why they should trust this token
- Consensus voting builds confidence

### 3. **Educational + Interactive**
- Learn about color theory while exploring
- Interactive playground shows real-time changes
- Harmony, temperature, saturation visualized
- Not just a tool—a learning experience

### 4. **Generic Platform, Specific Reference**
- Color tokens = first reference implementation
- Design patterns proven with color
- Typography uses same UI, different data
- Spacing uses same UI, different data
- 80% code reuse across token types

### 5. **Delightful, Shareable Interactions**
- Smooth animations and micro-interactions
- Export success celebrations
- Color grid entrance (staggered fade-in)
- Satisfying slider interactions

---

## Information Architecture

### Three-Panel Layout (Desktop)

```
┌──────────────────────────────────────────────────────────────┐
│ Header: Upload | Progress                                    │
├──────────────┬──────────────────────────────────────────────┤
│              │                                              │
│  SIDEBAR     │ GRID                                         │
│  (closed)    │ ┌──────────────────────────────────────────┐│
│              │ │ [CARD] [CARD] [CARD] [CARD]            ││
│              │ │ [CARD] [CARD] [CARD] [CARD]            ││
│  (opens      │ │ [CARD] [CARD] [CARD] [CARD]            ││
│   on         │ └──────────────────────────────────────────┘│
│   select)    │                                              │
│              │                                              │
│  Inspector   │ [PLAYGROUND DRAWER (collapsed)]              │
│              │                                              │
└──────────────┴──────────────────────────────────────────────┘
```

### Mobile Responsive

```
< 640px: 1 column grid, inspector as modal
640-1024px: 2-3 columns, sidebar collapses to icon
> 1024px: 4-6 columns, full sidebar visible
```

---

## Component Inventory

### Generic Components (Schema-Driven, 80% Reuse)

1. **TokenCard** - Generic card with swappable primary visual
   - Color: [Swatch]
   - Typography: [Text Sample]
   - Spacing: [Visual Bar]
   - Shadow: [Shadow Preview]
   - Animation: [Play Preview]

2. **TokenGrid** - Schema-driven filtering, sorting, view modes
   - Filters adapt to token type
   - View modes: Grid, List, Table

3. **TokenInspectorSidebar** - Right panel with format tabs
   - Format tabs defined by schema
   - Color: RGB, HSL, Oklch tabs
   - Typography: Tech, Design tabs
   - Spacing: Pixel, Rem, Scale tabs

4. **TokenPlaygroundDrawer** - Bottom drawer with exploration tabs
   - Tabs defined by schema
   - Color: Adjuster, Harmony, Temperature, Saturation
   - Typography: Adjuster, Hierarchy, Contrast, Preview
   - Spacing: Adjuster, Scale, Responsive, Context

5. **SemanticNameEditor** - Editable field with AI suggestions
   - Shows top 3 suggestions with confidence
   - Validation: lowercase, hyphens, 3-50 chars
   - Searchable for quick filtering

6. **ConfidenceBreakdown** - Multi-tier AI/ML transparency
   - Shows CV, CLIP, GPT-4V, Claude contributions
   - Consensus voting visualization
   - Explains why confidence is at this level

### Color-Specific Components (Reference Implementation)

1. **ColorTokenVisual** - Large swatch with visual details
2. **ColorFormatTabs** - RGB, HSL, Oklch format displays
3. **ColorAdjuster** - HSL sliders with real-time preview
4. **HarmonyVisualizer** - Color wheel with relationships
5. **TemperatureVisualizer** - Cool → Warm spectrum
6. **SaturationVisualizer** - Saturation scale
7. **ColorRelationshipsPanel** - Harmony, temperature, saturation

---

## Data Schema Example: Color Token

Every token type defines what fields exist (schema), how they're displayed (UI), and how they're edited (interactions).

```typescript
// Color token schema (from backend)
ColorToken = {
  id: string;
  hex: string;                    // Primary raw value
  rgb: { r: number; g: number; b: number };
  hsl: { h: number; s: number; l: number };
  oklch: { o: number; l: number; c: number; h: number };

  semanticName: string;           // "molten-copper" (AI-suggested, user-editable)
  designIntent: string;           // "evokes retro audio warmth"
  confidence: number;             // 0-100%

  metadata: {
    sources: ['opencv_cv', 'gpt4_vision', 'claude_vision'];
    temperature: 'cool' | 'neutral' | 'warm';
    saturation: 'vivid' | 'moderate' | 'muted';
    lightness: 'dark' | 'medium' | 'light';
    harmony: string[];            // Related color IDs
    usage: string[];              // ['primary', 'brand', 'accent']
  };

  extractedAt: datetime;
  createdAt: datetime;
  updatedAt: datetime;
}
```

**How schema drives UI:**

```typescript
// TokenTypeRegistry defines what to show for each type
tokenTypeRegistry.color = {
  formatTabs: [
    { name: 'RGB', field: 'rgb' },
    { name: 'HSL', field: 'hsl' },
    { name: 'Oklch', field: 'oklch' },
  ],
  filters: [
    { name: 'Temperature', field: 'metadata.temperature' },
    { name: 'Saturation', field: 'metadata.saturation' },
  ],
  playgroundTabs: [
    { name: 'Adjuster', component: HSLAdjuster },
    { name: 'Harmony', component: HarmonyVisualizer },
    { name: 'Temperature', component: TemperatureVisualizer },
    { name: 'Saturation', component: SaturationVisualizer },
  ],
};

// Future: Add Typography
tokenTypeRegistry.typography = {
  formatTabs: [
    { name: 'Tech', field: 'tech' },
    { name: 'Design', field: 'design' },
  ],
  filters: [
    { name: 'Font Family', field: 'fontFamily' },
    { name: 'Size', field: 'fontSize' },
  ],
  playgroundTabs: [
    { name: 'Adjuster', component: TypographyAdjuster },
    { name: 'Hierarchy', component: HierarchyVisualizer },
    // ... etc
  ],
};
```

---

## Progressive Extraction Feedback

Users see real-time progress:

```
┌────────────────────────────────────────────────────┐
│ Extracting tokens... [████████░░░░░░░░░░░░] 45%   │
│                                                    │
│ Stage 1: Analyzing image        ✓                 │
│ Stage 2: Detecting colors       ✓                 │
│ Stage 3: Enriching with AI      ⟳ (in progress)  │
│ Stage 4: Organizing tokens                         │
│                                                    │
│ Tokens found: 12 | Enriched: 8                    │
└────────────────────────────────────────────────────┘
```

**Backend sends:**
- Progress percentage
- Current stage name
- Token count (live)
- Confidence scores as they update
- Cancel option available

---

## Confidence & Trust Building

For each token, show:

```
Extracted by:
 ✓ OpenCV CV        (95% agreement on hex)
 ✓ GPT-4 Vision     (85% agreement on name)
 ✓ Claude Vision    (92% agreement on intent)

Overall Confidence: 89%
```

This transparency shows:
- Multiple sources enriched this token
- Which models agreed
- Why confidence is at this level
- Trust in the data

---

## Export Capabilities

**For Color Tokens:**
- CSS Variables
- JSON (W3C Design Tokens format)
- Figma plugin
- iOS Swift (SwiftUI)
- Android Kotlin

**For Typography Tokens:**
- CSS Variables
- JSON (W3C format)
- Figma
- iOS, Android
- Tailwind config
- SCSS/LESS mixins

**For Spacing Tokens:**
- CSS Variables
- JSON
- CSS Grid/Flex component props
- React component constants
- Tailwind config

**For Shadow Tokens:**
- CSS Variables
- JSON
- Figma
- iOS, Android
- CSS drop-shadow values

---

## Accessibility & Inclusive Design

- **WCAG AAA** color contrast (7:1 minimum)
- **Keyboard navigation** complete (Tab, Enter, Arrow keys)
- **Screen reader support** with semantic HTML and ARIA labels
- **Focus indicators** clearly visible
- **Color-blind safe** - use patterns + labels, not color alone
- **Reduced motion** support for animations
- **Mobile touch targets** 44x44px minimum

---

## Next Steps

This vision document establishes:
1. ✅ User flow and mental model
2. ✅ Generic component patterns
3. ✅ Schema-driven rendering approach
4. ✅ Color token as reference implementation
5. ✅ Extensibility to other token types

**See also:**
- [`COMPONENT_SPECIFICATIONS.md`](./COMPONENT_SPECIFICATIONS.md) - Detailed specs with Tailwind
- [`REACT_ARCHITECTURE.md`](./REACT_ARCHITECTURE.md) - Frontend implementation plan
- [`GENERALIZATION_ROADMAP.md`](./GENERALIZATION_ROADMAP.md) - How to extend to other tokens

# Token Widget Abstraction Pattern

## Philosophy

Frontend components are built as reusable **widgets** that can be applied to any token type (color, spacing, typography, shadow, etc.). This enables:

1. **Code reuse** across different token extractors
2. **Consistent UX** across the entire platform
3. **Rapid phase implementation** (Phase 5: Spacing, Typography, Shadows reuse these)
4. **Scalability** as we add more token types

## Core Widget Types

### 1. **NarrativeWidget** (ColorNarrative, SpacingNarrative, TypographyNarrative, etc.)

**Purpose:** Prose-based educational explanations of token properties

**Props:**
```typescript
interface NarrativeWidgetProps {
  tokenType: 'color' | 'spacing' | 'typography' | 'shadow'
  tokenValue: string | number // Color hex, spacing px, font size, etc.
  tokenName: string
  properties: Record<string, string | number | boolean> // Type-specific attributes
  narrative: Record<string, string> // Pre-written explanations
}
```

**Reusability:** ✅ Same component, different narratives per token type

**Examples:**
- ColorNarrative: explains temperature, saturation, lightness
- SpacingNarrative: explains spacing role, hierarchy, rhythm
- TypographyNarrative: explains font choice, hierarchy, readability
- ShadowNarrative: explains elevation, depth, focus

---

### 2. **VisualizerWidget** (HarmonyVisualizer, ContrastVisualizer, VariantVisualizer, etc.)

**Purpose:** Interactive visual exploration of token properties

**Props:**
```typescript
interface VisualizerWidgetProps {
  tokenType: 'color' | 'spacing' | 'typography' | 'shadow'
  primaryValue: string | number
  secondaryValues?: Record<string, string | number> // e.g., tint/shade/tone
  metadata?: Record<string, any> // Harmony, contrast, variants, etc.
  onInteract?: (action: string, value: any) => void
}
```

**Reusability:** ✅ Different visualization strategies per type

**Examples:**
- HarmonyVisualizer: hue wheel, harmony relationships
- AccessibilityVisualizer: contrast ratios, WCAG compliance
- SpacingVisualizer: spatial scale, rhythm visualization
- TypographyVisualizer: hierarchy scale, responsive sizes
- ShadowVisualizer: elevation layers, depth stacking

---

### 3. **PropertyDisplayWidget** (InfoCard, Badge, CodeBlock, etc.)

**Purpose:** Flexible display of any token property with appropriate formatting

**Props:**
```typescript
interface PropertyDisplayWidgetProps {
  label: string
  value: string | number
  format?: 'code' | 'badge' | 'text' | 'metric'
  icon?: string
  color?: string // For visual indicators
  interactive?: boolean
  onCopy?: (value: string) => void
}
```

**Reusability:** ✅ Universal across all token types

---

### 4. **ComparisonWidget** (Variants, Generations, Alternatives)

**Purpose:** Show relationships between related tokens

**Props:**
```typescript
interface ComparisonWidgetProps {
  primary: { label: string; value: string | number; visual?: ReactNode }
  related: Array<{ label: string; value: string | number; visual?: ReactNode }>
  comparisonType: 'variants' | 'alternatives' | 'related' | 'hierarchy'
}
```

**Reusability:** ✅ Works for tint/shade/tone variants, responsive sizes, elevation levels, etc.

---

## Implementation Pattern

### Current (Phase 4): Color-Specific

```
ColorTokenDisplay.tsx
├── HarmonyVisualizer (color-specific)
├── AccessibilityVisualizer (color-specific)
├── ColorNarrative (color-specific)
└── Display properties
```

### Future (Phase 5+): Generic Widgets

```
TokenDisplay.tsx (generic)
├── NarrativeWidget<TokenType> (reusable)
├── VisualizerWidget<TokenType> (reusable)
├── ComparisonWidget (reusable)
├── PropertyDisplayWidget (reusable)
└── Extract token-specific props/metadata
```

---

## Widget Composition Pattern

### Example: SpacingNarrative (Phase 5)

```typescript
// Use exact same structure as ColorNarrative
// but with spacing-specific narratives

const narratives = {
  'small': 'Used for tight spacing between related elements...',
  'medium': 'Standard spacing for grouped content...',
  'large': 'Creates visual separation between sections...',
}

// Same component structure, different content
```

### Example: SpacingVisualizer (Phase 5)

```typescript
// Use same interactive visualization pattern
// but showing spacing scale/rhythm instead of color wheel

const visualization = () => {
  // Draw spacing scale/grid
  // Show rhythm visualization
  // Interactive adjustment sliders
}
```

---

## Conversion Strategy: Phase 5

For each new token type (spacing, typography, shadow):

1. **Analyze current ColorNarrative** → Extract pattern
2. **Create TypeNarrative** → Same structure, type-specific content
3. **Analyze current HarmonyVisualizer** → Extract pattern
4. **Create TypeVisualizer** → Same structure, type-specific visualization
5. **Compose into TokenDisplay** → Generic component that receives type + metadata

**Time estimate per new type:** 2-3 hours (versus 6-8 hours if building from scratch)

---

## File Structure (Future)

```
components/
├── widgets/
│   ├── NarrativeWidget.tsx (generic)
│   ├── VisualizerWidget.tsx (generic)
│   ├── ComparisonWidget.tsx (generic)
│   ├── PropertyDisplayWidget.tsx (generic)
│   └── types.ts (shared types)
├── color/
│   ├── ColorNarrative.tsx (specialization)
│   ├── HarmonyVisualizer.tsx (specialization)
│   └── ColorTokenDisplay.tsx (composition)
├── spacing/
│   ├── SpacingNarrative.tsx (specialization)
│   ├── SpacingVisualizer.tsx (specialization)
│   └── SpacingTokenDisplay.tsx (composition)
├── typography/
│   ├── TypographyNarrative.tsx
│   ├── TypographyVisualizer.tsx
│   └── TypographyTokenDisplay.tsx
└── ... (shadow, opacity, border-radius, etc.)
```

---

## Benefits

| Aspect | Impact |
|--------|--------|
| **Code reuse** | 70% less code per new token type |
| **Consistency** | Users experience same patterns across all token types |
| **Maintainability** | Bug fixes and improvements apply globally |
| **Extensibility** | Easy to add custom token types |
| **Onboarding** | New developers understand pattern quickly |

---

## Current Implementation Status

### Phase 4 (Color - Current)
- ✅ ColorNarrative - specialized component
- ✅ HarmonyVisualizer - specialized component
- ✅ AccessibilityVisualizer - specialized component
- ✅ Generic layout pattern established

### Phase 5 (Spacing - Pattern Ready)
- 🔄 SpacingNarrative - ready to build using same pattern
- 🔄 SpacingVisualizer - ready to build using same pattern
- 🔄 ComparisonWidget - prepare for variants display

### Phase 6+ (Typography, Shadow, etc.)
- ⏳ TypographyNarrative
- ⏳ TypographyVisualizer
- ⏳ ShadowNarrative
- ⏳ ShadowVisualizer

---

## Next Steps

1. **Finalize ColorTokenDisplay** - Demonstrate pattern
2. **Document component API** - Make pattern explicit
3. **Build reusable base widgets** - Extract common logic
4. **Phase 5 kickoff** - Replicate for spacing tokens
5. **Establish widget library** - Evolve into design system

# Multimodal Component Architecture - Design Token Agnostic

**Date:** 2025-12-09
**Context:** Architecture must support visual (color, spacing) + future (audio, video, motion) tokens
**Principle:** Token-type agnostic components where possible

---

## 🎯 Core Realization

**Current thinking (WRONG):**
```
features/
├── color-extraction/      ← Color-specific components
├── spacing-analysis/      ← Spacing-specific components
└── typography-extraction/ ← Typography-specific components
```

**Multimodal thinking (CORRECT):**
```
shared/components/
├── TokenDetailView/       ← Works for ANY token (color, audio, video)
├── TokenPalette/          ← Generic grid of any tokens
├── TokenGraph/            ← Visualize any token relationships
└── TokenMetadata/         ← Show any token properties

features/
├── visual-extraction/     ← Visual tokens (color, spacing, typography)
│   ├── ColorExtractor/
│   ├── SpacingAnalyzer/
│   └── TypographyDetector/
├── audio-extraction/      ← Future: Audio tokens
└── video-extraction/      ← Future: Video tokens
```

---

## 🔍 Component Analysis - What's Actually Reusable?

### **Current "Color" Components - Functional Analysis**

Let me analyze each to determine: **Feature-specific** vs **Token-agnostic**

| Component | Purpose | Actually... | Should Be |
|-----------|---------|-------------|-----------|
| **ColorDetailsPanel** | Show token metadata | Generic metadata display | `shared/TokenDetailView` |
| **ColorPalette** | Grid of colored swatches | Token-specific (needs color rendering) | `features/visual/ColorPalette` |
| **ColorTokenDisplay** | List tokens with properties | Generic token list | `shared/TokenList` |
| **ColorGraph** | Visualize color relationships | Generic graph visualization | `shared/TokenGraph` |
| **ColorsTable** | Tabular token data | Generic table | `shared/TokenTable` |
| **CompactColorGrid** | Compact token grid | Generic grid | `shared/TokenGrid` |
| **HarmonyVisualizer** | Show color harmonies | Color-specific (harmony is visual) | `features/visual/HarmonyViz` |
| **AccessibilityVisualizer** | WCAG compliance | Color-specific (contrast is visual) | `features/visual/AccessibilityViz` |

**Key Insight:**
- **60% of "color" components** are actually **generic token displays** (DetailView, Graph, Table, Grid)
- **40% are truly color-specific** (Harmony, Accessibility, Swatches)

---

## 🎨 Multimodal Token Types

### **Visual Tokens (Current):**
- Color (`hex`, `rgb`, `oklch`) - ✅ Implemented
- Spacing (`px`, `rem`, `multiplier`) - ✅ Implemented
- Typography (`fontFamily`, `fontSize`, `lineHeight`) - ✅ Implemented
- Shadow (`offsetX`, `offsetY`, `blur`, `color`) - 🔄 Partial

### **Audio Tokens (Future):**
- Frequency (`hz`, `note`, `octave`)
- Duration (`ms`, `beats`, `tempo`)
- Amplitude (`db`, `velocity`)
- Timbre (`waveform`, `harmonics`)

### **Video Tokens (Future):**
- Motion (`easing`, `duration`, `path`)
- Transition (`type`, `timing`)
- Animation (`keyframes`, `loop`)

### **All Share:**
- `id` (identifier)
- `$type` (token type)
- `$value` (value object)
- Metadata (confidence, extraction method)
- Relationships (aliases, compositions)

---

## 📐 Proper Multimodal Architecture

### **Shared (Token-Agnostic) Components:**

```
shared/components/
├── TokenDetailView/           # Works for ANY token
│   ├── TokenDetailView.tsx
│   └── props:
│       - token: TokenNode
│       - renderPreview: (token) => ReactNode  # Custom preview
│       - renderMetadata: (token) => ReactNode # Custom metadata
│
├── TokenPalette/              # Generic grid/palette
│   ├── TokenPalette.tsx
│   └── props:
│       - tokens: TokenNode[]
│       - renderToken: (token) => ReactNode    # Custom rendering
│       - onSelect: (token) => void
│
├── TokenGraph/                # Graph visualization (React Flow)
│   └── Works for any token relationships
│
├── TokenTable/                # Generic table
│   └── Configurable columns for any token type
│
└── TokenMetadata/             # Generic metadata display
    └── Key-value pairs for any properties
```

---

### **Feature-Specific (Visual Domain):**

```
features/visual-extraction/
├── components/
│   ├── ColorHarmony/          # Color-specific (complementary, triadic)
│   ├── ColorAccessibility/    # Color-specific (WCAG, contrast)
│   ├── ColorSwatch/           # Color-specific (visual preview)
│   ├── SpacingRuler/          # Spacing-specific (visual scale)
│   ├── TypographyPreview/     # Typography-specific (font rendering)
│   └── ShadowPreview/         # Shadow-specific (CSS preview)
│
├── hooks/
│   ├── useColorHarmony.ts     # Color-specific logic
│   ├── useWCAG.ts             # Accessibility logic
│   └── useSpacingScale.ts     # Spacing-specific logic
│
└── index.ts
```

---

### **Future Features (Multimodal):**

```
features/audio-extraction/
├── components/
│   ├── WaveformPreview/       # Audio-specific visualization
│   ├── FrequencySpectrum/     # Audio-specific
│   └── AudioPlayer/           # Playback
└── hooks/
    └── useAudioAnalysis.ts

features/video-extraction/
├── components/
│   ├── MotionPreview/         # Video-specific
│   ├── TransitionTimeline/    # Video-specific
│   └── AnimationPlayer/       # Playback
└── hooks/
    └── useMotionAnalysis.ts
```

---

## 🔧 Correct Component Categorization

### **Shared/Generic (Reusable for ANY token type):**

| Current Name | Generic Name | Purpose | Works For |
|--------------|--------------|---------|-----------|
| ColorDetailsPanel | TokenDetailView | Show token properties | Color, Audio, Video, Motion |
| ColorsTable | TokenTable | Tabular data | All tokens |
| ColorTokenDisplay | TokenList | List with metadata | All tokens |
| CompactColorGrid | TokenGrid | Grid layout | All tokens |
| ColorGraphPanel | TokenGraph | Relationship visualization | All tokens |

**These should go to `shared/components/`** - NOT features!

---

### **Visual-Specific (Color/Spacing/Typography Only):**

| Component | Why Visual-Specific | Goes To |
|-----------|---------------------|---------|
| ColorPalette | Renders color swatches | `features/visual/ColorPalette` |
| HarmonyVisualizer | Color theory (complementary, triadic) | `features/visual/HarmonyViz` |
| AccessibilityVisualizer | WCAG contrast (visual concept) | `features/visual/AccessibilityViz` |
| ColorPrimaryPreview | Color swatch rendering | `features/visual/ColorPreview` |
| SpacingRuler | Visual spacing bars | `features/visual/SpacingRuler` |
| TypographyInspector | Font rendering | `features/visual/TypographyInspector` |

**These go to `features/visual-extraction/`** - visual domain only

---

### **Infrastructure (App-Level):**

| Component | Purpose | Goes To |
|-----------|---------|---------|
| ColorNarrative | Overview story | `components/overview/` or remove |
| OverviewNarrative | Multi-token story | Keep in root or `components/overview/` |
| MetricsOverview | Cross-feature metrics | Keep in root |

**These stay at app level** - they orchestrate multiple features

---

## 🎯 Correct Architecture for Multimodal

### **Pattern 1: Generic Token Components (60% of current components)**

```typescript
// shared/components/TokenDetailView/TokenDetailView.tsx
interface TokenDetailViewProps<T extends TokenNode> {
  token: T
  renderPreview: (token: T) => ReactNode      // Custom per type
  renderMetadata: (token: T) => ReactNode     // Custom per type
}

function TokenDetailView<T extends TokenNode>(props: TokenDetailViewProps<T>) {
  return (
    <div className="token-detail">
      <div className="preview">
        {props.renderPreview(props.token)}
      </div>
      <div className="metadata">
        {props.renderMetadata(props.token)}
      </div>
    </div>
  )
}

// Usage for color:
<TokenDetailView
  token={colorToken}
  renderPreview={token => <ColorSwatch hex={token.hex} />}
  renderMetadata={token => <ColorMetadata {...token} />}
/>

// Usage for audio (future):
<TokenDetailView
  token={audioToken}
  renderPreview={token => <WaveformPreview frequency={token.hz} />}
  renderMetadata={token => <AudioMetadata {...token} />}
/>
```

---

### **Pattern 2: Visual-Specific Components (40%)**

```typescript
// features/visual-extraction/components/ColorHarmony/ColorHarmony.tsx
interface ColorHarmonyProps {
  color: UiColorToken  // Visual domain only
}

function ColorHarmony({ color }: ColorHarmonyProps) {
  const graph = useTokenGraph()
  const complementary = calculateComplementary(color.hex)
  const analogous = calculateAnalogous(color.hex)

  return (
    <div className="color-harmony">
      <ColorSwatch hex={complementary} label="Complementary" />
      <ColorSwatch hex={analogous[0]} label="Analogous 1" />
    </div>
  )
}
```

**This ONLY makes sense for visual/color tokens** - stays in visual feature.

---

## 🚀 Revised Migration Plan

### **Step 1: Identify Generic vs Specific**

**I need to analyze EACH component:**

1. Read component code
2. Determine: Generic (works for any token) vs Specific (color-only)
3. Categorize: `shared/` vs `features/visual/`

**Let me do this analysis now...**

---

## 🎯 Critical Questions to Answer

**For each component:**

1. **Does it work with ANY token type?**
   - Yes → `shared/components/`
   - No → `features/visual/`

2. **Does it render token-type-specific preview?**
   - Color swatch → Visual-specific
   - Waveform → Audio-specific
   - Generic card → Token-agnostic

3. **Does it use token-type-specific logic?**
   - Harmony calculation → Color-specific
   - Tempo detection → Audio-specific
   - Generic sorting → Token-agnostic

---

**Excellent catch! Let me analyze ALL components properly before migrating. Want me to create a comprehensive component analysis document?**

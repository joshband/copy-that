# Shadow Token Frontend - Complete Implementation Guide

**Status:** ✅ All Phases Complete
**Date:** December 7, 2025
**Version:** v2.0.0

---

## Overview

The Shadow Token frontend implementation provides a comprehensive UI for shadow token management, color linking, and advanced analysis. This document covers all implementation phases.

---

## Phase Summary

| Phase | Feature | Status | Components |
|-------|---------|--------|------------|
| Phase 1 | Lifecycle Management | ✅ Complete | ShadowTokenList, store integration |
| Phase 2 | Color Linking | ✅ Complete | ColorTokenPicker, ShadowColorLink |
| Phase 3 | Shadow Palette | ✅ Complete | ShadowPalette with filters/search |
| Phase 4 | Advanced Analysis | ✅ Complete | ShadowAnalysisPanel, metrics, lighting |

---

## Phase 1: Shadow Token Lifecycle

### Features
- Shadow extraction from images
- Storage and retrieval via API
- Display in token viewer
- Edit and delete operations
- Export to W3C format

### Components
- `ShadowTokenList.tsx` - Main list component
- Integration with `tokenGraphStore`

### API Integration
- `POST /api/v1/shadows/extract` - Extract shadows
- `GET /api/v1/shadows/projects/{id}` - List shadows
- `PUT /api/v1/shadows/{id}` - Update shadow
- `DELETE /api/v1/shadows/{id}` - Delete shadow

---

## Phase 2: Color Linking

### Features
- Link shadow colors to color tokens
- Uses COMPOSES relationship type
- Auto-detection of matching colors
- Visual indicators for linked status

### Components

**ColorTokenPicker** (`ColorTokenPicker.tsx`)
- Dropdown for selecting color tokens
- Search by name, hex, or ID
- Shows color preview swatches
- Displays linked token reference

**ShadowColorLink** (`ShadowColorLink.tsx`)
- Inline display of link status
- Quick unlink action
- Compact and expanded modes

### Store Integration

```typescript
// shadowStore.ts
interface ShadowStore {
  shadows: ShadowTokenWithMeta[]
  availableColors: ColorTokenOption[]
  linkColorToShadow: (shadowId: string, colorId: string) => void
  unlinkColorFromShadow: (shadowId: string) => void
  getShadowsUsingColor: (colorId: string) => ShadowTokenWithMeta[]
}
```

### Relationship Type
Shadows link to colors using `COMPOSES`:
```typescript
{
  type: 'COMPOSES',
  from: 'shadow.card',
  to: 'color.neutral.900'
}
```

---

## Phase 3: Shadow Palette

### Features
- Unified shadow view with grid/list modes
- Search by name, ID, or hex
- Filter by elevation (subtle, medium, prominent, dramatic)
- Filter by type (drop, inner, text)
- Multi-select with batch operations
- Copy CSS to clipboard
- Linked status indicators

### Component

**ShadowPalette** (`ShadowPalette.tsx`)
```typescript
interface ShadowPaletteProps {
  shadows: ShadowTokenWithMeta[]
  onSelectShadow?: (shadow: ShadowTokenWithMeta) => void
  enableMultiSelect?: boolean
}
```

### Token Type Registry Integration

```typescript
// tokenTypeRegistry.tsx
shadow: {
  name: 'Shadow',
  formatTabs: [
    { name: 'Palette', component: ShadowPalette },
    { name: 'List', component: ShadowTokenList },
    { name: 'CSS', component: CSSExportView },
  ],
  playgroundTabs: [
    { name: 'Analysis', component: ShadowAnalysisPanel },
    { name: 'Lighting', component: LightingDirectionIndicator },
    { name: 'Metrics', component: ShadowQualityMetrics },
  ],
  filters: [
    { key: 'elevation', values: ['subtle', 'medium', 'prominent', 'dramatic'] },
    { key: 'shadowType', values: ['drop', 'inner', 'text'] },
    { key: 'softness', values: ['very_hard', 'hard', 'medium', 'soft', 'very_soft'] },
  ],
}
```

---

## Phase 4: Advanced Analysis

### Features
- Lighting direction detection with compass visualization
- Shadow quality metrics (coverage, contrast, softness)
- Confidence scoring
- CSS box-shadow suggestions
- Raw analysis data view

### Components

**LightingDirectionIndicator** (`LightingDirectionIndicator.tsx`)
- Visual compass showing light direction
- Cardinal direction labels (N, E, S, W)
- Confidence ring indicator
- Elevation visualization
- Size variants (sm, md, lg)

```typescript
interface LightingDirectionIndicatorProps {
  direction?: LightDirection | null  // radians
  directionToken?: LightDirectionToken  // categorical
  lightingStyle?: LightingStyleToken
  confidence?: number  // 0-1
  size?: 'sm' | 'md' | 'lg'
  showDetails?: boolean
}
```

**ShadowQualityMetrics** (`ShadowQualityMetrics.tsx`)
- Summary cards (quality score, shadow count, contrast ratio)
- Metric bars (coverage, contrast, softness, intensity)
- Token pills (categorical values)
- Compact mode for sidebars

```typescript
interface ShadowQualityMetricsProps {
  shadowAreaFraction?: number  // 0-1
  meanShadowIntensity?: number  // 0-1
  shadowContrast?: number  // 0-1
  edgeSoftness?: number  // 0-1
  shadowCount?: number
  confidence?: number  // 0-1
  tokens?: {
    softness?: ShadowSoftnessToken
    contrast?: ShadowContrastToken
    density?: ShadowDensityToken
  }
  layout?: 'horizontal' | 'vertical' | 'grid'
  compact?: boolean
}
```

**ShadowAnalysisPanel** (`ShadowAnalysisPanel.tsx`)
- Tab navigation: Metrics, CSS Suggestions, Raw Data
- Integrates LightingDirectionIndicator
- Integrates ShadowQualityMetrics
- CSS copy-to-clipboard functionality
- Loading/error/empty states
- Compact mode for inline use

```typescript
interface ShadowAnalysisPanelProps {
  analysis?: LightingAnalysisResponse | null
  imageBase64?: string
  isLoading?: boolean
  error?: string | null
  onAnalyze?: (imageBase64: string) => Promise<void>
  showCSSSuggestions?: boolean
  compact?: boolean
}
```

### TypeScript Types

Located in `frontend/src/types/shadowAnalysis.ts`:

```typescript
// Categorical tokens
type LightDirectionToken = 'upper_left' | 'upper_right' | 'left' | 'right' | 'overhead' | 'front' | 'back' | 'unknown'
type ShadowSoftnessToken = 'very_hard' | 'hard' | 'medium' | 'soft' | 'very_soft'
type ShadowContrastToken = 'low' | 'medium' | 'high' | 'very_high'
type ShadowDensityToken = 'sparse' | 'moderate' | 'heavy' | 'full'
type LightingStyleToken = 'directional' | 'rim' | 'diffuse' | 'mixed' | 'complex'

// API Response
interface LightingAnalysisResponse {
  // Tokens (categorical)
  style_key_direction: LightDirectionToken
  style_softness: ShadowSoftnessToken
  style_contrast: ShadowContrastToken
  // ... more tokens

  // Features (numeric 0-1)
  shadow_area_fraction: number
  shadow_contrast: number
  edge_softness_mean: number
  // ... more features

  // CSS suggestions
  css_box_shadow: CSSBoxShadowSuggestions
}

// Helper functions
function getLightDirectionLabel(direction: LightDirectionToken): string
function getLightingStyleLabel(style: LightingStyleToken): string
function azimuthToCompassDirection(azimuthRad: number): string
function computeQualityScore(analysis: LightingAnalysisResponse): QualityScoreBreakdown
```

### Backend API Integration

**Endpoint:** `POST /api/v1/lighting/analyze`

```typescript
// Request
{
  image_url?: string,
  image_base64?: string,
  use_geometry?: boolean,  // default true
  device?: 'cpu' | 'cuda'  // default 'cpu'
}

// Response: LightingAnalysisResponse
```

---

## File Structure

```
frontend/src/
├── components/shadows/
│   ├── index.ts                       # Exports all shadow components
│   ├── ShadowTokenList.tsx           # Phase 1: Main list view
│   ├── ShadowTokenList.css
│   ├── ColorTokenPicker.tsx          # Phase 2: Color selection dropdown
│   ├── ColorTokenPicker.css
│   ├── ShadowColorLink.tsx           # Phase 2: Link status display
│   ├── ShadowColorLink.css
│   ├── ShadowPalette.tsx             # Phase 3: Unified palette view
│   ├── ShadowPalette.css
│   ├── LightingDirectionIndicator.tsx # Phase 4: Light direction compass
│   ├── LightingDirectionIndicator.css
│   ├── ShadowQualityMetrics.tsx      # Phase 4: Quality metrics display
│   ├── ShadowQualityMetrics.css
│   ├── ShadowAnalysisPanel.tsx       # Phase 4: Main analysis panel
│   ├── ShadowAnalysisPanel.css
│   └── __tests__/
│       ├── ColorTokenPicker.test.tsx
│       ├── ShadowColorLink.test.tsx
│       ├── ShadowPalette.test.tsx
│       ├── ShadowTokenList.test.tsx
│       ├── LightingDirectionIndicator.test.tsx
│       ├── ShadowQualityMetrics.test.tsx
│       └── ShadowAnalysisPanel.test.tsx
├── store/
│   ├── shadowStore.ts                 # Zustand store for shadows
│   └── __tests__/
│       └── shadowStore.test.ts
├── types/
│   ├── shadowAnalysis.ts              # Phase 4 type definitions
│   └── __tests__/
│       └── shadowAnalysis.test.ts
└── config/
    └── tokenTypeRegistry.tsx          # Registry with shadow config
```

---

## Testing

### Test Files

| Phase | Test File | Tests |
|-------|-----------|-------|
| 1 | ShadowTokenList.test.tsx | 15 tests |
| 2 | ColorTokenPicker.test.tsx | 22 tests |
| 2 | ShadowColorLink.test.tsx | 21 tests |
| 2 | shadowStore.test.ts | 21 tests |
| 3 | ShadowPalette.test.tsx | 25 tests |
| 4 | LightingDirectionIndicator.test.tsx | 27 tests |
| 4 | ShadowQualityMetrics.test.tsx | 24 tests |
| 4 | ShadowAnalysisPanel.test.tsx | 28 tests |
| 4 | shadowAnalysis.test.ts | 19 tests |

**Total: 200+ shadow-related tests**

### Running Tests

```bash
# Run all shadow tests
pnpm test -- --grep shadow

# Run specific phase tests
pnpm test -- src/components/shadows/__tests__/ShadowAnalysisPanel.test.tsx
```

---

## Usage Examples

### Basic Shadow Display

```tsx
import { ShadowTokenList } from './components/shadows'

<ShadowTokenList
  shadows={extractedShadows}
  enableColorLinking={true}
  colorTokens={availableColors}
/>
```

### Shadow Palette with Filters

```tsx
import { ShadowPalette } from './components/shadows'

<ShadowPalette
  shadows={allShadows}
  onSelectShadow={(shadow) => setSelected(shadow)}
  enableMultiSelect={true}
/>
```

### Advanced Analysis Panel

```tsx
import { ShadowAnalysisPanel } from './components/shadows'

<ShadowAnalysisPanel
  analysis={lightingAnalysis}
  imageBase64={currentImage}
  onAnalyze={handleAnalyze}
  showCSSSuggestions={true}
/>
```

### Compact Lighting Indicator

```tsx
import { LightingDirectionIndicator } from './components/shadows'

<LightingDirectionIndicator
  directionToken="upper_left"
  lightingStyle="directional"
  confidence={0.85}
  size="sm"
  showDetails={false}
/>
```

---

## Future Enhancements

### Planned Features
- Shadow ramp generation (auto-generate elevation scale)
- Shadow-to-component association
- Cross-shadow consistency validation
- Shadow animation previews
- Real-time shadow editing playground

### API Enhancements
- Batch shadow analysis
- Shadow comparison endpoint
- Historical analysis tracking

---

## Related Documentation

- [SHADOW_TOKENS_COMPLETION.md](./SHADOW_TOKENS_COMPLETION.md) - Backend completion
- [SHADOW_PIPELINE_SPEC.md](./SHADOW_PIPELINE_SPEC.md) - Pipeline specification
- [architecture/token_graph.md](./architecture/token_graph.md) - Token relationships
- [DESIGN_TOKENS_W3C_STATUS.md](./DESIGN_TOKENS_W3C_STATUS.md) - W3C export status

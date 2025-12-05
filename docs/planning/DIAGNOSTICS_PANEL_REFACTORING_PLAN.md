# DiagnosticsPanel Refactoring Plan (Issue #10 Phase 2)

**Component:** `DiagnosticsPanel.tsx` (450 LOC)
**Status:** Ready for Refactoring (Analysis Complete)
**Complexity:** HIGH (most complex of the three candidates)
**Reuse Potential:** VERY HIGH (image manipulation hooks applicable to many components)

---

## Current Structure Analysis

### Component Overview
```typescript
DiagnosticsPanel (450 LOC)
├── State (5 hooks)
│   ├── selectedSpacing
│   ├── selectedComponent
│   ├── selectedColor
│   ├── showAlignmentLines
│   └── showSegments
├── Derived State (5 useMemo calculations)
│   ├── commonSpacings
│   ├── palette
│   ├── matchingBoxes
│   ├── alignmentLines
│   └── payloadInfo
└── Rendering (3 diagnostic cards)
    ├── SpacingDiagnosticsCard (120 LOC)
    ├── PaletteCard (25 LOC)
    └── OverlayPreview (complex SVG/canvas - 130 LOC)
```

### Key Calculations (Good Hook Candidates)

#### 1. Image Dimension Tracking (40 LOC)
**Lines 89-110**
```typescript
const overlayImgRef = useRef<HTMLImageElement | null>(null)
const [dimensions, setDimensions] = useState({...})
useEffect(() => {
  const update = () => setDimensions({...})
  update()
  window.addEventListener('resize', update)
  return () => window.removeEventListener('resize', update)
}, [overlaySrc])
```

**Hook:** `useImageDimensions`
- Track natural vs client dimensions
- Handle resize events
- Calculate scale factors (sx, sy)
- **Reusable:** YES - Any image overlay needs this

#### 2. Alignment Line Calculations (35 LOC)
**Lines 150-177**
```typescript
const alignmentLines = useMemo(() => {
  if (!spacingResult?.alignment || !dimensions...) return []
  const sx = dimensions.clientWidth / dimensions.naturalWidth
  const sy = dimensions.clientHeight / dimensions.naturalHeight
  const lines: Array<{ orientation: 'vertical' | 'horizontal'; pos: number }> = []
  // Extract alignment from spacingResult
  // Calculate scaled positions
  return lines.map(...)
}, [...])
```

**Hook:** `useAlignmentLines`
- Extract alignment from spacing result
- Calculate scaled positions
- Memoize for performance
- **Reusable:** YES - Any alignment visualization needs this

#### 3. Component Box Scaling (20 LOC)
**Lines 137-148**
```typescript
const renderBox = (box: [number, number, number, number]) => {
  if (!dimensions.naturalWidth || !dimensions.naturalHeight) return null
  const [x, y, w, h] = box
  const scaleX = dimensions.clientWidth / dimensions.naturalWidth
  const scaleY = dimensions.clientHeight / dimensions.naturalHeight
  return {
    left: x * scaleX,
    top: y * scaleY,
    width: Math.max(w * scaleX, 2),
    height: Math.max(h * scaleY, 2),
  }
}
```

**Hook:** `useBoxScaling`
- Scale bounding boxes to viewport
- Handle dimension conversions
- Ensure minimum size (2px)
- **Reusable:** YES - Canvas/overlay work

#### 4. Polygon Scaling (10 LOC)
**Lines 179-184**
```typescript
const scalePolygon = (poly?: Array<[number, number]>) => {
  if (!poly?.length || !dimensions.naturalWidth || !dimensions.naturalHeight) return null
  const sx = dimensions.clientWidth / dimensions.naturalWidth
  const sy = dimensions.clientHeight / dimensions.naturalHeight
  return poly.map(([x, y]) => [x * sx, y * sy] as [number, number])
}
```

**Hook:** `usePolygonScaling`
- Scale polygon coordinates
- Handle FastSAM segment rendering
- **Reusable:** YES - Any polygon visualization

#### 5. Matching Boxes Calculation (25 LOC)
**Lines 112-135**
```typescript
const matchingBoxes = useMemo(() => {
  // Filter by selected spacing (with tolerance)
  // Filter by selected component
  // Combine and deduplicate results
}, [componentMetrics, selectedComponent, selectedSpacing])
```

**Hook:** `useMatchingBoxes`
- Filter component metrics by spacing value
- Filter by component selection
- Combine and deduplicate
- **Reusable:** Moderate (specific to component filtering)

#### 6. Palette Derivation (12 LOC)
**Lines 75-86**
```typescript
const palette = useMemo(() => {
  if (segmentedPalette?.length) {
    return segmentedPalette.slice(0, 10).map(...)
  }
  return colors.slice(0, 10).map(...)
}, [colors, segmentedPalette])
```

**Hook:** `usePaletteDerivation`
- Choose between segmented and color palette
- Normalize to consistent format
- Limit to 10 entries
- **Reusable:** YES - Any palette display

#### 7. Payload Info Calculation (30 LOC)
**Lines 186-215**
```typescript
const payloadInfo = useMemo(() => {
  const items: Array<{ label: string; value: string }> = []
  // Extract all debug info
  return items
}, [...])
```

**Hook:** `usePayloadInfo`
- Aggregate debug information
- Format for display
- **Reusable:** Low (very specific)

---

## Proposed Refactoring Structure

### Target Architecture

```
diagnostics-panel/
├── DiagnosticsPanel.tsx              (~90 LOC - orchestrator)
├── types.ts                          (~50 LOC - shared types)
├── hooks.ts                          (~180 LOC - 7 reusable hooks)
├── constants.ts                      (~10 LOC - FALLBACK_TOLERANCE, etc)
├── utils.ts                          (~40 LOC - toDataUrl, computeFallbackSpacings)
├── index.ts                          (exports)
├── SpacingDiagnosticsCard.tsx        (~80 LOC - spacing UI)
├── PaletteCard.tsx                   (~40 LOC - color palette)
├── OverlayPreview.tsx                (~120 LOC - most complex component)
└── __tests__/
    ├── hooks.test.ts                 (~300 LOC - hook tests)
    ├── components.test.tsx           (~250 LOC - component tests)
    └── DiagnosticsPanel.integration.test.tsx (~400 LOC - integration)
```

### Breakdown

| Component | LOC | Purpose |
|-----------|-----|---------|
| Main orchestrator | 90 | Compose hooks and sub-components |
| Hooks (7 total) | 180 | Image/polygon/box calculations |
| Sub-components (3) | 240 | Card rendering |
| Utilities | 50 | Helpers, constants |
| Types | 50 | Shared type definitions |
| Tests | 950+ | Comprehensive coverage |

---

## Hook Extraction Plan

### Hook 1: `useImageDimensions` (40 LOC)
```typescript
export const useImageDimensions = (imgRef: RefObject<HTMLImageElement>, trigger?: any) => {
  const [dimensions, setDimensions] = useState({
    naturalWidth: 0,
    naturalHeight: 0,
    clientWidth: 0,
    clientHeight: 0,
  })

  useEffect(() => {
    const img = imgRef.current
    if (!img) return

    const update = () => setDimensions({...})
    update()
    window.addEventListener('resize', update)
    return () => window.removeEventListener('resize', update)
  }, [trigger])

  return {
    dimensions,
    scaleX: dimensions.clientWidth / dimensions.naturalWidth,
    scaleY: dimensions.clientHeight / dimensions.naturalHeight,
  }
}
```

**Reusable:** ✅ YES - Used in many overlay/canvas scenarios

### Hook 2: `useAlignmentLines` (35 LOC)
```typescript
export const useAlignmentLines = (
  alignment: SpacingExtractionResponse['alignment'] | undefined,
  dimensions: ImageDimensions
) => {
  return useMemo(() => {
    if (!alignment || !dimensions.naturalWidth) return []
    const sx = dimensions.clientWidth / dimensions.naturalWidth
    const sy = dimensions.clientHeight / dimensions.naturalHeight

    const lines = []
    // Extract all alignment axes
    // Calculate scaled positions
    return lines
  }, [alignment, dimensions])
}
```

**Reusable:** ✅ YES - Any alignment grid visualization

### Hook 3: `useBoxScaling` (20 LOC)
```typescript
export const useBoxScaling = (dimensions: ImageDimensions) => {
  return useCallback((box: [number, number, number, number]) => {
    if (!dimensions.naturalWidth) return null
    const [x, y, w, h] = box
    const scaleX = dimensions.clientWidth / dimensions.naturalWidth
    const scaleY = dimensions.clientHeight / dimensions.naturalHeight

    return {
      left: x * scaleX,
      top: y * scaleY,
      width: Math.max(w * scaleX, 2),
      height: Math.max(h * scaleY, 2),
    }
  }, [dimensions])
}
```

**Reusable:** ✅ YES - Bounding box rendering

### Hook 4: `usePolygonScaling` (15 LOC)
```typescript
export const usePolygonScaling = (dimensions: ImageDimensions) => {
  return useCallback((polygon?: Array<[number, number]>) => {
    if (!polygon?.length || !dimensions.naturalWidth) return null
    const sx = dimensions.clientWidth / dimensions.naturalWidth
    const sy = dimensions.clientHeight / dimensions.naturalHeight
    return polygon.map(([x, y]) => [x * sx, y * sy])
  }, [dimensions])
}
```

**Reusable:** ✅ YES - Polygon/segment rendering

### Hook 5: `useMatchingBoxes` (25 LOC)
```typescript
export const useMatchingBoxes = (
  componentMetrics: SpacingMetric[],
  selectedComponent: number | null,
  selectedSpacing: number | null,
  tolerance: number = 2
) => {
  return useMemo(() => {
    // Filter by spacing with tolerance
    // Filter by component
    // Combine and deduplicate
    return matchingBoxes
  }, [componentMetrics, selectedComponent, selectedSpacing, tolerance])
}
```

**Reusable:** 🟡 MODERATE - Spacing-specific but generic pattern

### Hook 6: `usePaletteDerivation` (15 LOC)
```typescript
export const usePaletteDerivation = (
  colors: ColorToken[],
  segmentedPalette?: SegmentedColor[] | null
) => {
  return useMemo(() => {
    if (segmentedPalette?.length) {
      return segmentedPalette.slice(0, 10).map(...)
    }
    return colors.slice(0, 10).map(...)
  }, [colors, segmentedPalette])
}
```

**Reusable:** ✅ YES - Any palette normalization

### Hook 7: `usePayloadInfo` (30 LOC)
```typescript
export const usePayloadInfo = (
  spacingResult: SpacingExtractionResponse | undefined,
  componentMetrics: SpacingMetric[],
  commonSpacings: SpacingEntry[],
  fastsamTokens: any[]
) => {
  return useMemo(() => {
    const items = []
    // Aggregate all debug info
    return items
  }, [...])
}
```

**Reusable:** 🔴 LOW - Very specific to this component

---

## Sub-Components Plan

### SpacingDiagnosticsCard (80 LOC)
**Lines 231-346 of original**
- Alignment summary display
- Payload info (optional)
- Spacing chips (buttons)
- Component metrics list (scrollable)

**Props:**
```typescript
{
  spacingResult?: SpacingExtractionResponse
  commonSpacings: SpacingEntry[]
  componentMetrics: SpacingMetric[]
  selectedSpacing: number | null
  selectedComponent: number | null
  showAlignment?: boolean
  showPayload?: boolean
  showAlignmentLines: boolean
  onSpacingClick: (value: number | null) => void
  onComponentClick: (idx: number | null) => void
  onAlignmentToggle: (show: boolean) => void
}
```

### PaletteCard (40 LOC)
**Lines 349-369 of original**
- Color swatches grid
- Coverage percentage display
- Selection state

**Props:**
```typescript
{
  palette: PaletteEntry[]
  selectedColor: string | null
  onColorClick: (hex: string | null) => void
}
```

### OverlayPreview (120 LOC)
**Lines 371-446 of original**
- Overlay image rendering
- SVG segment overlay
- Alignment lines overlay
- Component box highlights
- FastSAM segment toggle

**Props:**
```typescript
{
  overlaySrc: string | null
  dimensions: ImageDimensions
  matchingBoxes: MatchingBox[]
  alignmentLines: AlignmentLine[]
  fastsamTokens: FastSAMToken[]
  showSegments: boolean
  showAlignmentLines: boolean
  onSegmentToggle: (show: boolean) => void
  renderBox: (box: Box) => StyleObject | null
  scalePolygon: (poly: Polygon) => Polygon | null
}
```

---

## Test Plan

### Hooks Tests (~300 LOC)
- `useImageDimensions`: 4 tests (initial, resize, cleanup)
- `useAlignmentLines`: 4 tests (extract, scale, memoization)
- `useBoxScaling`: 3 tests (scale, min size, edge cases)
- `usePolygonScaling`: 3 tests (scale, empty handling)
- `useMatchingBoxes`: 5 tests (filter, combine, deduplicate)
- `usePaletteDerivation`: 3 tests (segmented, fallback, limits)
- `usePayloadInfo`: 3 tests (aggregation, formatting)

### Components Tests (~250 LOC)
- SpacingDiagnosticsCard: 5 tests
- PaletteCard: 4 tests
- OverlayPreview: 6 tests

### Integration Tests (~400 LOC)
- Full DiagnosticsPanel workflow
- Selection filtering
- Overlay rendering
- FastSAM segment display
- Alignment line visualization

---

## Implementation Order

1. ✅ Create directory structure
2. ✅ Extract types to `types.ts`
3. ✅ Extract utilities to `utils.ts`
4. ✅ Extract hooks (in order of dependency)
5. ✅ Create sub-components
6. ✅ Create main orchestrator
7. ✅ Create tests
8. ✅ Verify type-check
9. ✅ Update old file for backward compatibility

---

## Key Complexity Areas

### 1. SVG Rendering
- SVG viewBox calculation
- Polygon point mapping
- Dynamic dimension handling

### 2. Image Dimension Tracking
- Natural vs client dimensions
- Resize event handling
- Scale factor calculations

### 3. Component Filtering
- Tolerance-based spacing matching
- Component selection
- Deduplication logic

### 4. State Management
- 5 independent state pieces
- Complex derived calculations
- Performance with useMemo

---

## Expected Outcomes

| Metric | Before | After | Reduction |
|--------|--------|-------|-----------|
| Main component LOC | 450 | 90 | 80% |
| Files created | 1 | 11 | N/A |
| Reusable hooks | 0 | 7 | N/A |
| Reusable components | 0 | 3 | N/A |
| Test coverage | None | 950+ LOC | 100% |
| Type safety | Good | Excellent | N/A |

---

## Status

- ✅ Full component analysis complete
- ✅ Hook extraction plan detailed
- ✅ Sub-component breakdown defined
- ✅ Test strategy planned
- ⏳ Ready for implementation

**Ready to start refactoring on signal.**

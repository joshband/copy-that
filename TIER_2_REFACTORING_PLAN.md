# Issue #9B Tier 2 - Component Refactoring Plan

**Date:** 2025-12-04
**Status:** PLANNING
**Target:** MetricsOverview (328 LOC) + AccessibilityVisualizer (294 LOC)

---

## Overview

Tier 2 refactoring targets 2 medium-priority components that handle data visualization and display logic. Both components have significant UI rendering and state management that can be decomposed following the Tier 1 pattern.

**Combined Size:** 622 LOC → ~240 LOC (61% reduction target)

---

## Component 1: MetricsOverview (328 LOC)

**File:** `frontend/src/components/MetricsOverview.tsx`

### Current Structure
- 1 exported component: `MetricsOverview`
- 5 helper components (inline): `StatBox`, `Chip`, `MetricBox`, `DesignInsightCard`
- Data loading logic mixed with rendering
- API integration embedded
- Conditional rendering for multiple states

### Refactoring Strategy

**Folder Structure:**
```
frontend/src/components/metrics-overview/
├── types.ts                           (85 LOC)
├── hooks.ts                           (65 LOC)
├── DesignInsightCard.tsx              (75 LOC)
├── StatBox.tsx                        (15 LOC)
├── Chip.tsx                           (8 LOC)
├── MetricBox.tsx                      (15 LOC)
├── MetricsGrid.tsx                    (80 LOC) [new - grid layout]
├── MetricsOverview.tsx                (60 LOC) [orchestrator]
└── index.ts                           (8 LOC)
```

### Extraction Plan

**Step 1: Extract Types (`types.ts`)**
- `ElaboratedMetric`
- `OverviewMetricsData`
- `MetricsOverviewProps`
- Helper component prop types

**Step 2: Extract Hooks (`hooks.ts`)**
- `useMetricsData()` - Load metrics from API
- `useLoadingState()` - Manage loading/error state
- `useDataValidation()` - Check extracted data exists
- `useConfidenceColor()` - Utility for styling confidence levels

**Step 3: Extract Components**
- `DesignInsightCard.tsx` - Rich insight visualization (currently 75 LOC)
- `StatBox.tsx` - Simple stat display (move from line 188)
- `Chip.tsx` - Inline chip component (move from line 197)
- `MetricBox.tsx` - Metric display (move from line 205)
- `MetricsGrid.tsx` - NEW - Extract grid layout logic (currently inline at line 105)

**Step 4: Orchestrator**
- `MetricsOverview.tsx` - Calls hooks, renders components with proper error states

### Key Refactoring Details

1. **API Loading**
   - Move `useEffect` + `loadMetrics` → `useMetricsData()` hook
   - Handle loading/error/success states
   - Return `{ metrics, loading, error }`

2. **Grid Layout**
   - Create `MetricsGrid.tsx` to render conditional cards
   - Takes metrics array and renders grid
   - Handles null safety for optional metrics

3. **Confidence Styling**
   - Utility functions `getConfidenceColor()` and `getConfidenceLabel()` → `utils.ts`
   - Used by `DesignInsightCard` for badge styling

4. **Empty States**
   - Orchestrator handles loading → "Analyzing..."
   - Orchestrator handles no data → "No data yet"
   - Components assume data exists

### Testing Points
- ✅ MetricsOverview loads data on mount
- ✅ Tab switching works (if tabs added later)
- ✅ Confidence colors update correctly
- ✅ Empty state shows when no data
- ✅ Each card renders properly

---

## Component 2: AccessibilityVisualizer (294 LOC)

**File:** `frontend/src/components/AccessibilityVisualizer.tsx`

### Current Structure
- 1 exported component: `AccessibilityVisualizer`
- 2 internal helper functions: `parseHex()`, `getLuminance()`, `calculateContrast()`
- 3 tab states: white/black/custom backgrounds
- Multiple calculation functions
- Large JSX with repeated structure

### Refactoring Strategy

**Folder Structure:**
```
frontend/src/components/accessibility-visualizer/
├── types.ts                           (15 LOC)
├── hooks.ts                           (60 LOC)
├── utils.ts                           (40 LOC) [color calculations]
├── ContrastPanel.tsx                  (85 LOC)
├── CustomBackgroundTab.tsx            (50 LOC)
├── WcagStandards.tsx                  (40 LOC)
├── AccessibilityVisualizer.tsx        (50 LOC) [orchestrator]
├── index.ts                           (8 LOC)
└── AccessibilityVisualizer.css        [moved]
```

### Extraction Plan

**Step 1: Extract Types (`types.ts`)**
- `AccessibilityVisualizerProps`
- `ColorRGB` interface
- `TabType` type

**Step 2: Extract Utilities (`utils.ts`)**
- `parseHex()` - Parse hex to RGB
- `getLuminance()` - Calculate luminance
- `calculateContrast()` - Calculate contrast ratio
- `getWcagLevel()` functions
- All pure functions (no state)

**Step 3: Extract Hooks (`hooks.ts`)**
- `useContrastCalculations()` - Manage all contrast calculations
  - Input: hex, customBackground, currentTab
  - Output: { white, black, custom contrast values }
- `useTabState()` - Manage active tab state
- `useCustomBackground()` - Manage custom background input

**Step 4: Extract Components**
- `ContrastPanel.tsx` - Shared contrast display logic
  - Renders preview + WCAG standards
  - Takes contrast ratio and compliance data

- `CustomBackgroundTab.tsx` - Custom tab with color picker
  - Input field + preview
  - Calculates custom contrast

- `WcagStandards.tsx` - WCAG standards display
  - Renders 4 standard boxes
  - Pass/fail styling

**Step 5: Orchestrator**
- `AccessibilityVisualizer.tsx` - Tab switching + delegation

### Key Refactoring Details

1. **Color Utilities**
   - Pure functions in `utils.ts` (no React imports)
   - Makes testing/reuse easy
   - Clear separation of concerns

2. **Contrast Panel Abstraction**
   - `ContrastPanel` renders preview + standards
   - Gets ratio and compliance data
   - Reusable for white/black/custom tabs

3. **Custom Tab Complexity**
   - `CustomBackgroundTab` handles color input separately
   - Prevents duplication of preview logic

4. **Tab Management**
   - State lives in orchestrator
   - Passed down to each tab component
   - Tabs are presentation-only

### Testing Points
- ✅ Hex parsing works for various formats
- ✅ Contrast calculations are accurate
- ✅ Tab switching updates display
- ✅ Custom color picker updates preview
- ✅ WCAG compliance badges show correctly
- ✅ Colorblind safe indicator appears when true

---

## Implementation Sequence

### Session 1 (Recommended)
1. Refactor **MetricsOverview** (Tier 2a)
   - Simpler API integration
   - Clear data flow
   - No complex calculations

2. Test in browser

### Session 2
3. Refactor **AccessibilityVisualizer** (Tier 2b)
   - More calculation-heavy
   - Utility extraction critical
   - Multiple tab interactions

4. Test in browser

---

## Pattern Consistency

Both components follow Tier 1 pattern:

1. ✅ Extract types → `types.ts`
2. ✅ Extract logic → `hooks.ts` + `utils.ts`
3. ✅ Create focused components (~50-100 LOC each)
4. ✅ Create orchestrator (~60 LOC)
5. ✅ Export via `index.ts`
6. ✅ Update parent imports
7. ✅ Run typecheck

---

## Expected Outcomes

### MetricsOverview
- **Before:** 328 LOC (1 large component + 5 helpers)
- **After:** ~110 LOC across 8 files
- **Reduction:** 66%
- **Benefit:** Easier to test, reuse cards independently

### AccessibilityVisualizer
- **Before:** 294 LOC
- **After:** ~130 LOC across 6 files + utils
- **Reduction:** 56%
- **Benefit:** Pure utilities for reuse, cleaner tabs

### Total Tier 2
- **Before:** 622 LOC
- **After:** ~240 LOC
- **Reduction:** 61%

---

## Playwright E2E Testing

Each component will have comprehensive Playwright tests:

### MetricsOverview Tests
**File:** `frontend/tests/metrics-overview.spec.ts`

```typescript
test('loads metrics on mount', async ({ page }) => {
  await page.goto('http://localhost:5174');
  await page.waitForSelector('[data-testid="metrics-overview"]');
  // Verify API call made
  // Check metrics loaded
});

test('shows empty state when no data', async ({ page }) => {
  // Mock API to return null
  await page.goto('http://localhost:5174');
  await page.waitForText('No data yet');
});

test('displays all insight cards with data', async ({ page }) => {
  // Navigate to page with data
  // Verify 6 cards visible (Art Movement, Tone, etc)
  // Check each card has label + title + description
});

test('confidence badges show correct colors', async ({ page }) => {
  // High confidence (>75) = green
  // Medium confidence (60-75) = yellow
  // Low confidence (<60) = orange
  // Check each badge background color
});
```

### AccessibilityVisualizer Tests
**File:** `frontend/tests/accessibility-visualizer.spec.ts`

```typescript
test('renders on white background tab', async ({ page }) => {
  // Go to color detail panel
  // Click contrast tab
  // Verify "On White" tab active
  // Check preview renders with white bg
  // Verify contrast ratio displayed
});

test('switches to black background', async ({ page }) => {
  // Click "On Black" tab
  // Verify tab switches
  // Check preview updates to black bg
  // Verify new contrast ratio
});

test('custom background tab accepts color input', async ({ page }) => {
  // Click "Custom Background" tab
  // Find color input
  // Type hex color
  // Verify preview updates instantly
  // Check contrast recalculates
});

test('WCAG standards show correct compliance', async ({ page }) => {
  // For high contrast color:
  //   - AA-LargeText shows ✓ Pass
  //   - AAA-LargeText shows ✓ Pass
  // For low contrast color:
  //   - All standards show ✗ Fail
  // Verify styling (green for pass, red for fail)
});

test('colorblind safe indicator appears', async ({ page }) => {
  // For colorblind-safe color:
  //   - Badge visible and marked safe
  // For non-safe color:
  //   - Badge hidden or marked unsafe
});
```

### Tier 1 Components - Full Integration Test Suite
**File:** `frontend/tests/tier1-refactored-components.spec.ts`

#### DiagnosticsPanel Tests
```typescript
test('DiagnosticsPanel renders with overlay', async ({ page }) => {
  // Navigate to page with spacing data
  // Verify DiagnosticsPanel visible
  // Check image overlay loads
  // Verify header text displays
});

test('SpacingDiagnostics shows common spacings', async ({ page }) => {
  // Verify spacing chips render
  // Check metric values display
  // Verify chip count matches data
});

test('ColorPalettePicker displays colors', async ({ page }) => {
  // Check color swatches render
  // Verify coverage percentages shown
  // Click color swatch → selection updates
});

test('DiagnosticsPanel spacing selection works', async ({ page }) => {
  // Click spacing chip
  // Selected state updates
  // Matching boxes highlight in overlay
  // Click different spacing → highlights change
});

test('DiagnosticsPanel component selection works', async ({ page }) => {
  // Click component metric
  // Selection state updates
  // Related boxes highlight
  // Click different component → highlights change
});

test('DiagnosticsPanel shows/hides alignment lines', async ({ page }) => {
  // Toggle alignment lines button
  // Lines appear/disappear on overlay
  // State persists during interaction
});

test('OverlayPreview renders canvas visualization', async ({ page }) => {
  // Verify canvas element exists
  // Check FastSAM tokens display
  // Alignment lines render when enabled
  // Segments toggle works
});
```

#### ColorDetailPanel Tests
```typescript
test('ColorDetailPanel renders selected color', async ({ page }) => {
  // Navigate to colors section
  // Click color to select
  // Detail panel opens
  // Selected color displays correctly
});

test('ColorHeader shows color info', async ({ page }) => {
  // Verify hex value displays
  // Check color name shows
  // Confidence badge renders
  // Alias info displays if applicable
});

test('ColorDetailPanel tabs render correctly', async ({ page }) => {
  // Overview tab: Color properties visible
  // Harmony tab: Only shows if color has harmony data
  // Accessibility tab: WCAG info displays
  // Properties tab: Advanced color data shows
  // Diagnostics tab: Only shows with debug overlay
});

test('ColorDetailPanel tab switching works', async ({ page }) => {
  // Click Overview tab → content updates
  // Click Harmony tab → harmony visualization shows
  // Click Accessibility tab → contrast info displays
  // Click Properties tab → detailed properties show
  // Tab active state updates correctly
});

test('OverviewTab shows color identity', async ({ page }) => {
  // Color swatch displays
  // Name and hex shown
  // Semantic name visible if available
  // Temperature/saturation info displays
});

test('HarmonyTab shows harmony visualization', async ({ page }) => {
  // Harmony type displays (Complementary, Analogous, etc.)
  // Related colors shown
  // Color swatches render correctly
});

test('AccessibilityTab shows WCAG compliance', async ({ page }) => {
  // Contrast ratios display
  // Compliance badges show (AA/AAA)
  // Pass/fail styling correct
  // Colorblind safe indicator visible
});

test('PropertiesTab shows advanced properties', async ({ page }) => {
  // RGB values display
  // HSL values show
  // Other color spaces render
  // All properties correctly calculated
});
```

#### TokenInspector Tests
```typescript
test('TokenInspector renders token list', async ({ page }) => {
  // Navigate to TokenInspector
  // Token table loads
  // All tokens display
  // Column headers visible
});

test('FilterBar allows filtering tokens', async ({ page }) => {
  // Type text in filter input
  // List updates in real-time
  // Only matching tokens show
  // Clear filter → all tokens reappear
  // Filter case-insensitive
});

test('TokenList displays token details', async ({ page }) => {
  // Each row shows: ID, Type, Box coords
  // Click row → selection updates
  // Selected row highlights
  // Token data accurate
});

test('TokenList selection works', async ({ page }) => {
  // Click token row
  // Active state updates
  // Click different token → selection changes
  // Canvas visualization updates with selection
});

test('CanvasVisualization renders overlay', async ({ page }) => {
  // Canvas element visible
  // Overlay image loads
  // Correct dimensions calculated
  // SVG elements render
});

test('CanvasVisualization highlights selected token', async ({ page }) => {
  // Select token from list
  // Corresponding region highlighted on canvas
  // Highlight box drawn correctly
  // Select different token → highlight moves
});

test('TokenInspector download functionality', async ({ page }) => {
  // Click download button
  // File download triggered
  // JSON file contains all tokens
  // File data structure correct
  // Download filename correct
});

test('TokenInspector handles resize', async ({ page }) => {
  // Verify overlay dimensions tracked
  // Resize window
  // Canvas dimensions update
  // Highlights stay aligned with image
});
```

#### SpacingTokenShowcase Tests (Tier 1 - Phase 4)
```typescript
test('SpacingTokenShowcase renders tokens', async ({ page }) => {
  // Navigate to spacing showcase
  // Token cards visible
  // Count matches data
  // Cards properly formatted
});

test('SpacingTokenShowcase filtering works', async ({ page }) => {
  // Use filter controls
  // Token list updates
  // Only matching tokens show
  // Stats update with filters
});

test('SpacingTokenCard displays token info', async ({ page }) => {
  // Token name visible
  // Size value shown (px/rem)
  // Preview ruler displays
  // Color-coded appropriately
});

test('SpacingResponsivePreview shows responsiveness', async ({ page }) => {
  // Different breakpoints selectable
  // Values change per breakpoint
  // Visual preview updates
  // Current breakpoint highlighted
});
```

### Full Integration Flow Tests
**File:** `frontend/tests/full-integration.spec.ts`

```typescript
test('Complete refactored component flow', async ({ page }) => {
  // 1. Navigate to main page
  // 2. Upload image with tokens
  // 3. DiagnosticsPanel loads and displays
  // 4. Select spacing value
  // 5. Highlight updates
  // 6. Select color from palette
  // 7. ColorDetailPanel opens
  // 8. Navigate tabs
  // 9. Close detail panel
  // 10. Open TokenInspector
  // 11. Filter tokens
  // 12. Select token
  // 13. Canvas highlights
  // 14. Download tokens JSON
});

test('Event handlers don\'t break components', async ({ page }) => {
  // Rapid tab switching
  // Multiple selections
  // Filter changes
  // No errors in console
  // All interactions responsive
});

test('All components render with mock data', async ({ page }) => {
  // Load test data
  // All Tier 1 components render
  // No missing imports
  // No TypeScript errors
  // Visual layout correct
});

test('Responsive layout on mobile', async ({ page }) => {
  // Set viewport to mobile size
  // All components visible
  // No horizontal scroll
  // Touch interactions work
  // Text readable
});
```

### Running Tests
```bash
# Run all tests
pnpm test:e2e

# Run specific suite
pnpm test:e2e metrics-overview

# Run with UI
pnpm test:e2e --ui

# Run headed (see browser)
pnpm test:e2e --headed
```

### Test Configuration
**File:** `playwright.config.ts`
- Base URL: `http://localhost:5174`
- Timeout: 10s
- Retries: 2
- Browsers: Chromium (default)

---

## Known Challenges

1. **MetricsOverview API**
   - Multiple optional metrics fields
   - Needs null safety throughout
   - Elaborations are arrays

2. **AccessibilityVisualizer Calculations**
   - WCAG formula accuracy critical
   - Custom contrast updates should be instant
   - Color parsing must handle edge cases

---

## Next Steps

1. ✅ Plan created
2. ⏳ Implement MetricsOverview
3. ⏳ Test in browser
4. ⏳ Implement AccessibilityVisualizer
5. ⏳ Test in browser
6. ⏳ Final commit + handoff

---

**Plan Created:** 2025-12-04 | Ready for implementation

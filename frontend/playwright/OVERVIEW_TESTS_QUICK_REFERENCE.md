# Overview Tab Tests - Quick Reference

## Test Suite Summary

**File:** `frontend/playwright/overview-tab.spec.ts`
**Total Tests:** 54
**Test Groups:** 18

---

## Quick Start

```bash
# Run all tests
pnpm exec playwright test overview-tab.spec.ts

# Run with UI
pnpm exec playwright test overview-tab.spec.ts --ui

# List all tests
pnpm exec playwright test --list overview-tab.spec.ts

# Run specific test group
pnpm exec playwright test overview-tab.spec.ts -g "Empty State"

# Debug mode
pnpm exec playwright test overview-tab.spec.ts --debug

# Headed browser (watch execution)
pnpm exec playwright test overview-tab.spec.ts --headed
```

---

## Test Groups (18 Total)

| # | Test Group | Tests | Focus |
|---|------------|-------|-------|
| 1 | Initial State & Navigation | 2 | Tab availability and switching |
| 2 | Empty State | 3 | No data display |
| 3 | Loading State | 1 | Async loading feedback |
| 4 | Design Palette Section | 2 | Master section rendering |
| 5 | System Insights Chips | 2 | Colored insight chips |
| 6 | Design Insight Cards - Structure | 3 | Card structure and content |
| 7 | Confidence Badges & Scoring | 5 | Confidence display and colors |
| 8 | Source Indicators | 4 | Data source attribution |
| 9 | Elaborations | 2 | Multi-point insights |
| 10 | Summary Statistics | 3 | Stat boxes grid |
| 11 | Key Metrics | 6 | Individual metrics display |
| 12 | Specific Insight Cards | 8 | Each card type (Art, Emotion, etc.) |
| 13 | Responsive Layout | 3 | Mobile/desktop layouts |
| 14 | Visual Hierarchy | 3 | Typography and spacing |
| 15 | Accessibility | 2 | ARIA and contrast |
| 16 | Data Validation | 2 | Error handling |
| 17 | Interaction States | 2 | Dynamic updates |
| 18 | Visual Regression | 1 | Screenshot snapshots |

---

## Key Test Scenarios

### Empty State (Tests 3 of them)
✓ Shows "No data yet" message
✓ Hides metric cards
✓ Hides summary stats

### With Data (Tests 51 of them)
✓ Renders "Your Design Palette" section
✓ Shows system summary description
✓ Displays insight chips (colored)
✓ Renders 6 insight cards:
  - 🎨 Art Movement
  - 💭 Emotional Tone
  - ⏱️ Design Complexity
  - 🌡️ Temperature Profile
  - ✨ Saturation Character
  - 💪 System Health

✓ Shows confidence badges with colors:
  - Green (75%+)
  - Yellow (60-74%)
  - Orange (<60%)

✓ Shows source indicators:
  - 🎨 Colors (for color-based metrics)
  - 📊 All Tokens (for multi-source metrics)

✓ Displays summary stats (4 boxes):
  - Colors count
  - Spacing count
  - Typography count
  - Shadows count

✓ Displays key metrics (responsive grid):
  - Palette Type
  - System Maturity
  - Spacing System
  - Typography Levels

✓ Responsive design:
  - Mobile: Single column cards, 2-column stats
  - Desktop: Single column cards, 4-column stats

---

## Component Elements Tested

### MetricsOverview Component
```typescript
interface OverviewMetricsData {
  // Summary
  summary: {
    total_colors: number;
    total_spacing: number;
    total_typography: number;
    total_shadows: number;
  };

  // Elaborated Metrics
  art_movement: ElaboratedMetric | null;
  emotional_tone: ElaboratedMetric | null;
  design_complexity: ElaboratedMetric | null;
  temperature_profile: ElaboratedMetric | null;
  saturation_character: ElaboratedMetric | null;
  design_system_insight: ElaboratedMetric | null;

  // Simple Metrics
  color_palette_type: string | null;
  design_system_maturity: string;
  spacing_scale_system: string | null;
  spacing_uniformity: number;
  typography_hierarchy_depth: number;

  // Insights
  insights: string[];

  // Source Tracking
  source?: {
    has_extracted_colors: boolean;
    has_extracted_spacing: boolean;
    has_extracted_typography: boolean;
  };
}
```

---

## Test Selectors Reference

### Tabs
```typescript
page.locator('button:has-text("Overview")')
```

### Messages
```typescript
page.locator('text=Your Design Palette')
page.locator('text=No data yet')
page.locator('text=Analyzing your design system')
```

### Cards
```typescript
page.locator('text=Art Movement')
page.locator('text=Emotional Tone')
page.locator('[class*="border-l-4"][class*="border-gray-300"]')
```

### Badges
```typescript
page.locator('[data-source]')  // Source badges
page.locator('[class*="rounded-full"][class*="text-xs"]')  // Confidence badges
```

### Statistics
```typescript
page.locator('[class*="bg-gray-50"][class*="border"]')  // Stat boxes
page.locator('[class*="text-2xl"][class*="font-bold"]')  // Stat values
```

### Metrics Grid
```typescript
page.locator('[class*="grid"][class*="grid-cols-2"][class*="gap-4"]')
```

---

## Common Assertions

```typescript
// Visibility
await expect(element).toBeVisible();
await expect(element).not.toBeVisible();

// Classes
await expect(element).toHaveClass(/text-xl/);
await expect(element).toHaveClass(/bg-green-100/);

// Text
await expect(element).toContainText('High Confidence');
expect(text).toMatch(/\d+%/);

// Attributes
await expect(element).toHaveAttribute('data-source', '🎨 Colors');
await expect(element).toHaveAttribute('title', /Inferred from/);
```

---

## Running Specific Tests

```bash
# Navigation tests
pnpm exec playwright test overview-tab.spec.ts -g "Initial State"

# Confidence badge tests
pnpm exec playwright test overview-tab.spec.ts -g "Confidence"

# Specific card tests
pnpm exec playwright test overview-tab.spec.ts -g "Art Movement"

# Responsive tests
pnpm exec playwright test overview-tab.spec.ts -g "Responsive"

# Run just one test
pnpm exec playwright test overview-tab.spec.ts -g "should display empty state"
```

---

## Test Requirements

### For Empty State Tests
- Just visit the Overview tab
- No data needed

### For Full Feature Tests
- Upload an image to application
- Wait for extraction to complete
- Navigate to Overview tab
- Tests will validate all rendered metrics

### For Responsive Tests
- Viewport will be set automatically
- Tests run at 375px (mobile) and 1280px (desktop)

---

## Expected Test Results

### Empty State Scenario
- ✓ 3/3 tests pass
- Shows helpful "no data" message

### With Extracted Data
- ✓ 51/51 tests pass
- Shows complete metrics dashboard

### Responsive Layout
- ✓ 3/3 tests pass
- Different layouts for mobile/desktop

---

## CI/CD Integration

Add to GitHub Actions:

```yaml
- name: Run Overview Tab Tests
  run: pnpm exec playwright test overview-tab.spec.ts

- name: Upload Report
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: playwright-report
    path: playwright-report/
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Tests timeout | Increase timeout in beforeEach |
| Source badges not found | Extract data first (upload image) |
| Responsive tests fail | Ensure view set before navigation |
| Flaky tests | Add explicit waits before assertions |
| Cannot find element | Check if data is present for that element |

---

## Test File Structure

```
overview-tab.spec.ts
├── Section 1: Initial State & Navigation (2 tests)
├── Section 2: Empty State (3 tests)
├── Section 3: Loading State (1 test)
├── Section 4: Design Palette (2 tests)
├── Section 5: Insight Chips (2 tests)
├── Section 6: Card Structure (3 tests)
├── Section 7: Confidence Badges (5 tests)
├── Section 8: Source Indicators (4 tests)
├── Section 9: Elaborations (2 tests)
├── Section 10: Summary Stats (3 tests)
├── Section 11: Key Metrics (6 tests)
├── Section 12: Specific Cards (8 tests)
├── Section 13: Responsive Layout (3 tests)
├── Section 14: Visual Hierarchy (3 tests)
├── Section 15: Accessibility (2 tests)
├── Section 16: Data Validation (2 tests)
├── Section 17: Interaction States (2 tests)
└── Section 18: Visual Regression (1 test)

Total: 54 tests
```

---

## Documentation

- Full guide: `OVERVIEW_TAB_TESTS.md`
- This quick ref: `OVERVIEW_TESTS_QUICK_REFERENCE.md`
- Component source: `frontend/src/components/MetricsOverview.tsx`
- Test file: `frontend/playwright/overview-tab.spec.ts`

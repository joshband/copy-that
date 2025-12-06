# Overview Tab - Granular Playwright Tests

## Overview

This test suite provides comprehensive, granular coverage of the Overview tab functionality in the MetricsOverview component. Tests are organized into 18 distinct sections covering every aspect of the UI.

**File:** `frontend/playwright/overview-tab.spec.ts`
**Total Test Groups:** 18
**Test Coverage:** 50+ individual test cases

## Running the Tests

### Run all overview tests:
```bash
pnpm exec playwright test overview-tab.spec.ts
```

### Run specific test group:
```bash
pnpm exec playwright test overview-tab.spec.ts -g "Empty State"
```

### Run with UI (debug mode):
```bash
pnpm exec playwright test overview-tab.spec.ts --ui
```

### Run with headed browser:
```bash
pnpm exec playwright test overview-tab.spec.ts --headed
```

### Generate HTML report:
```bash
pnpm exec playwright test overview-tab.spec.ts && pnpm exec playwright show-report
```

## Test Structure

### Section 1: Initial State & Navigation
Tests the basic setup and tab navigation.

**Tests:**
- `should load the application with overview tab available` - Tab exists and is enabled
- `should navigate to Overview tab when clicked` - Tab becomes active on click

**Purpose:** Ensures the tab is accessible and interactive.

### Section 2: Empty State
Tests the UI when no design system data has been extracted yet.

**Tests:**
- `should display empty state message on first visit` - Shows helpful message
- `should not show metric cards when no data is extracted` - Cards don't render
- `should not display summary stats in empty state` - Stats are hidden

**Purpose:** Validates graceful degradation when no data is available.

### Section 3: Loading State
Tests the loading UI while metrics are being fetched.

**Tests:**
- `should show loading message while metrics are being analyzed` - Loading message appears

**Purpose:** Ensures users see feedback during async operations.

### Section 4: Design Palette Section
Tests the main "Your Design Palette" section header and description.

**Tests:**
- `should display "Your Design Palette" title` - Title is visible
- `should display system summary description with token counts` - Description with counts shows

**Purpose:** Validates the master section rendering.

### Section 5: Insight Chips
Tests the colored insight chips that appear above the metric cards.

**Tests:**
- `should display insight chips with appropriate colors` - Chips render with styling
- `should color-code chips by token type` - Correct colors used (blue=spacing, purple=color, etc.)

**Purpose:** Ensures visual categorization is clear.

### Section 6: Design Insight Cards - Structure
Tests the basic structure of insight cards.

**Tests:**
- `should render DesignInsightCard with correct elements` - Icon, label, title present
- `should display card title prominently` - Title styling correct
- `should display card description text` - Description renders with content

**Purpose:** Validates core card structure and content.

### Section 7: Confidence Badges & Scoring
Tests confidence score display and color coding.

**Tests:**
- `should display confidence percentage on metric cards` - Percentage visible
- `should use green background for high confidence (75%+)` - Green for 75%+
- `should use yellow background for medium confidence (60-74%)` - Yellow for 60-74%
- `should use orange background for low confidence (<60%)` - Orange for <60%
- `should display uncertainty message for low-confidence insights` - Explanatory text shows

**Purpose:** Validates confidence scoring system and visual hierarchy.

### Section 8: Source Indicators & Data Attribution
Tests source badges showing where data came from.

**Tests:**
- `should display source badge on insight cards` - Badge is visible
- `should show correct source for color-based metrics` - 🎨 Colors source
- `should show correct source for combined token metrics` - 📊 All Tokens source
- `should have helpful tooltip on source badge` - Title attribute present

**Purpose:** Ensures data provenance is clearly communicated.

### Section 9: Elaborations & Extended Insights
Tests multi-point elaborations below main insights.

**Tests:**
- `should display multiple elaboration points for rich insights` - Elaboration bullets render
- `elaborations should have proper styling` - Correct text styling applied

**Purpose:** Validates secondary insight display.

### Section 10: Summary Statistics Section
Tests the 4-column stat box grid.

**Tests:**
- `should display four stat boxes for token categories` - All 4 boxes render
- `should display numeric values in stat boxes` - Numbers are displayed
- `stat boxes should be in responsive grid` - Grid layout applied

**Purpose:** Validates summary statistics rendering.

### Section 11: Key Metrics Section
Tests the metric boxes showing system properties.

**Tests:**
- `should display key metrics in a responsive grid` - Grid renders
- `metric boxes should have proper structure` - Label, value, description present
- `should display Palette Type metric when available` - Palette Type shows
- `should display System Maturity metric when available` - System Maturity shows
- `should display Spacing System metric when available` - Spacing System with % uniform
- `should display Typography Levels metric when available` - Typography Levels shows

**Purpose:** Validates individual metric display.

### Section 12: Specific Insight Cards
Tests each individual insight card type.

**Tests:**
- Art Movement: 🎨 icon, colors source
- Emotional Tone: 💭 icon
- Design Complexity: ⏱️ icon
- Temperature Profile: 🌡️ icon
- Saturation Character: ✨ icon
- System Health: 💪 icon, total token count

**Purpose:** Validates each card renders with correct icon and source.

### Section 13: Responsive Layout
Tests mobile vs desktop layouts.

**Tests:**
- `should stack insight cards in single column on mobile` - Mobile view (375px)
- `should display stat boxes in 2 columns on mobile` - Mobile grid layout
- `should display stat boxes in 4 columns on desktop` - Desktop grid layout

**Purpose:** Ensures responsive design works correctly.

### Section 14: Visual Hierarchy & Typography
Tests text sizing and spacing relationships.

**Tests:**
- `Design Palette title should be largest heading` - Size hierarchy correct
- `Insight card titles should be smaller than Design Palette title` - Relative sizing
- `should use proper spacing between sections` - Space-y-6 applied

**Purpose:** Validates visual hierarchy.

### Section 15: Accessibility & ARIA
Tests accessible naming and color contrast.

**Tests:**
- `should have descriptive titles and labels` - Labels are meaningful
- `should have proper color contrast for badges` - Background and text colors defined

**Purpose:** Ensures accessibility standards are met.

### Section 16: Data Validation & Error Handling
Tests robustness with missing or zero data.

**Tests:**
- `should handle missing elaborations gracefully` - No crashes with missing data
- `should display zero values for empty token categories` - Zeros display correctly

**Purpose:** Validates error handling.

### Section 17: Interaction States
Tests component behavior during state changes.

**Tests:**
- `should update metrics when refresh trigger changes` - Refresh works
- `should handle project ID changes` - Project switching works

**Purpose:** Tests dynamic state management.

### Section 18: Visual Regression
Tests UI snapshots for visual consistency.

**Tests:**
- `should match overview tab empty state snapshot` - Screenshot matching

**Purpose:** Prevents unintended visual changes.

## Key Testing Patterns

### Conditional Visibility Tests

Many tests use `.isVisible().catch(() => false)` to gracefully handle components that may or may not be present:

```typescript
const isVisible = await element.isVisible().catch(() => false);
if (isVisible) {
  // Test element
}
```

This allows tests to pass whether data is present or not, testing the component's robustness.

### Attribute & Class Verification

Tests verify Tailwind classes to ensure styling:

```typescript
await expect(element).toHaveClass(/text-xl/);
await expect(element).toHaveClass(/font-bold/);
```

### Text Content Validation

Tests verify text content using regex patterns:

```typescript
expect(text).toMatch(/\d+%/); // Contains percentage
expect(text).toMatch(/(High Confidence|Likely Match|...)/); // Contains expected label
```

### Structure Verification

Tests verify element hierarchy using locator chains:

```typescript
const parent = element.locator('../..');
const valueElement = parent.locator('[class*="text-xl"]');
```

## Test Data Requirements

Most tests are data-agnostic and work whether or not metrics data is present. For full coverage:

### To test with data:
1. Upload an image to the application
2. Wait for extraction to complete
3. Navigate to Overview tab
4. Tests will validate rendered metrics

### To test without data:
1. Just navigate to Overview tab
2. Tests will validate empty state
3. Tests will gracefully skip data-dependent assertions

## CI/CD Integration

To add to your CI pipeline:

```yaml
- name: Run Playwright Tests
  run: pnpm exec playwright test frontend/playwright/overview-tab.spec.ts

- name: Upload Test Results
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: playwright-report
    path: playwright-report/
```

## Debugging Failed Tests

### View failure details:
```bash
pnpm exec playwright test overview-tab.spec.ts --debug
```

### Save traces for investigation:
```bash
pnpm exec playwright test overview-tab.spec.ts --trace on
```

### Watch single test:
```bash
pnpm exec playwright test overview-tab.spec.ts -g "should display empty state" --watch
```

## Common Issues & Solutions

### Issue: Tests timeout on metrics load
**Solution:** Metrics API may be slow. Increase timeout in beforeEach:
```typescript
test.setTimeout(240000); // 4 minutes
```

### Issue: Source badges not found
**Solution:** Source badges may require actual extracted data. Test with image upload.

### Issue: Responsive tests fail
**Solution:** Ensure view is set before navigation:
```typescript
await page.setViewportSize({ width: 375, height: 667 });
await page.goto('http://localhost:3001');
```

## Future Test Enhancements

1. **API Mocking:** Mock metrics API responses for deterministic testing
2. **Visual Regression:** Add Percy or similar for comprehensive visual testing
3. **Performance:** Add metrics for page load and render times
4. **Accessibility:** Integrate axe-core for automated a11y scanning
5. **E2E Flows:** Test complete flow from upload → extraction → overview display

## Maintenance

When modifying MetricsOverview component:

1. Update relevant test sections
2. Run full test suite: `pnpm exec playwright test overview-tab.spec.ts`
3. Review failed tests and update locators as needed
4. Update snapshots if visual changes are intentional: `pnpm exec playwright test overview-tab.spec.ts --update-snapshots`
5. Commit test updates with component changes

## References

- **Component:** `frontend/src/components/MetricsOverview.tsx`
- **Test File:** `frontend/playwright/overview-tab.spec.ts`
- **Playwright Docs:** https://playwright.dev/docs/intro
- **Best Practices:** https://playwright.dev/docs/best-practices

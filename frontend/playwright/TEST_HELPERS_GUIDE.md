# Test Helpers Guide

## Overview

The `test-helpers.ts` file provides reusable utilities, mock data, and helper functions for testing the Overview Tab functionality.

## Contents

### 1. Mock Data (`mockOverviewMetrics`)

Pre-built test data fixtures for different scenarios:

#### `mockOverviewMetrics.emptyState`
Empty dashboard with no extracted tokens.

```typescript
import { mockOverviewMetrics } from './test-helpers';

// Use in tests
const emptyData = mockOverviewMetrics.emptyState;
```

**Characteristics:**
- All null metrics
- Zero token counts
- No source indicators
- Perfect for testing empty state

#### `mockOverviewMetrics.withColors`
Complete, well-structured design system with high confidence metrics.

```typescript
const fullData = mockOverviewMetrics.withColors;
```

**Characteristics:**
- 24 colors, 12 spacing, 8 typography, 4 shadows
- All elaborated metrics present
- High confidence scores (70-94%)
- All sources: colors, spacing, typography extracted
- Warm color temperature with Art Deco movement

#### `mockOverviewMetrics.lowConfidence`
Design system with low confidence scores (35-52%).

```typescript
const lowConfData = mockOverviewMetrics.lowConfidence;
```

**Characteristics:**
- Mixed and ambiguous metrics
- Only colors extracted (low coverage)
- Low confidence scores
- Good for testing uncertainty messaging

### 2. OverviewTabHelpers Class

Comprehensive helper methods for common testing tasks.

#### Initialization

```typescript
import { OverviewTabHelpers } from './test-helpers';

test('example', async ({ page }) => {
  const helpers = new OverviewTabHelpers(page);

  // Use helpers
  await helpers.navigateToOverview();
});
```

#### Navigation

```typescript
// Navigate to Overview tab
await helpers.navigateToOverview();
```

#### State Checking

```typescript
// Check if empty state is shown
const isEmpty = await helpers.isEmptyState();

// Check if loading state is shown
const isLoading = await helpers.isLoadingState();
```

#### Get Elements

```typescript
// Get all insight cards
const cards = await helpers.getInsightCards();

// Get specific card by label
const artCard = await helpers.getInsightCard('Art Movement');

// Get all confidence badges with values
const badges = await helpers.getConfidenceBadges();
// Returns: [{ percentage: 82, label: 'High Confidence' }, ...]

// Get all source indicators
const sources = await helpers.getSourceIndicators();
// Returns: ['🎨 Colors', '📊 All Tokens']

// Get summary statistics
const stats = await helpers.getSummaryStats();
// Returns: [{ label: 'Colors', value: 24 }, ...]

// Get insight chips
const chips = await helpers.getInsightChips();
```

#### Verification Methods

```typescript
// Verify Design Palette section exists
const hasPalette = await helpers.verifyDesignPaletteSection();

// Verify card structure (has all required parts)
const structure = await helpers.verifyCardStructure(cardElement);
// Returns: { hasIcon, hasLabel, hasTitle, hasDescription }

// Get expected confidence color
const color = await helpers.verifyConfidenceColor(82);
// Returns: 'green' (for 75%+)

// Get elaboration points
const elaborations = await helpers.getElaborations(cardElement);
// Returns: ['First point', 'Second point', ...]
```

#### Responsive Testing

```typescript
// Check responsive grid classes at different breakpoints
const gridClasses = await helpers.checkResponsiveGrid();
// Returns: { mobile: ['grid-cols-1', ...], desktop: ['grid-cols-4', ...] }
```

#### API Mocking

```typescript
// Mock the metrics API response
await helpers.mockMetricsAPI(mockOverviewMetrics.withColors);

// Delay API response (for loading state testing)
await helpers.delayMetricsAPI(2000); // 2 second delay

// Log metrics API requests
const requests = await helpers.logMetricsRequests();

// Wait for metrics to load
await helpers.waitForMetricsLoad();
```

#### Screenshots & Debugging

```typescript
// Take screenshot of specific section
await helpers.screenshotSection('text=Your Design Palette', 'palette-section.png');

// Get all visible text on page
const textContent = await helpers.getAllVisibleText();
```

#### Accessibility

```typescript
// Validate color contrast (simplified check)
const hasGoodContrast = await helpers.validateColorContrast(element);
```

### 3. Assertion Helpers

Simple assertion functions for common checks:

```typescript
import {
  assertElementHasText,
  assertElementHasClass,
  assertElementIsVisible,
  assertElementIsHidden,
  assertElementCount,
  assertTextMatches,
} from './test-helpers';

// Check element contains text
await assertElementHasText(element, 'Art Movement');
await assertElementHasText(element, /confidence|likely/i); // Regex

// Check element has class
await assertElementHasClass(element, 'text-xl');
await assertElementHasClass(element, /text-\d+/); // Regex

// Visibility assertions
await assertElementIsVisible(element);
await assertElementIsHidden(element);

// Count assertions
await assertElementCount(elements, 6); // Exactly 6
await assertElementCount(elements, 3, '>'); // More than 3
await assertElementCount(elements, 10, '<='); // 10 or fewer

// Text matching
await assertTextMatches(textContent, /\d+%/);
```

## Usage Examples

### Example 1: Test Empty State

```typescript
import { test, expect } from '@playwright/test';
import { OverviewTabHelpers } from './test-helpers';

test('should show empty state with helpful message', async ({ page }) => {
  const helpers = new OverviewTabHelpers(page);

  await helpers.navigateToOverview();

  const isEmpty = await helpers.isEmptyState();
  expect(isEmpty).toBe(true);
});
```

### Example 2: Test With Mock Data

```typescript
import { test, expect } from '@playwright/test';
import { OverviewTabHelpers, mockOverviewMetrics } from './test-helpers';

test('should display all metrics with colors extracted', async ({ page }) => {
  const helpers = new OverviewTabHelpers(page);

  // Mock the API
  await helpers.mockMetricsAPI(mockOverviewMetrics.withColors);

  // Navigate
  await helpers.navigateToOverview();
  await helpers.waitForMetricsLoad();

  // Verify data
  const stats = await helpers.getSummaryStats();
  expect(stats.find(s => s.label === 'Colors')?.value).toBe(24);

  const sources = await helpers.getSourceIndicators();
  expect(sources).toContain('🎨 Colors');
});
```

### Example 3: Test Confidence Scoring

```typescript
import { test, expect } from '@playwright/test';
import { OverviewTabHelpers, mockOverviewMetrics } from './test-helpers';

test('should show high confidence badges in green', async ({ page }) => {
  const helpers = new OverviewTabHelpers(page);

  await helpers.mockMetricsAPI(mockOverviewMetrics.withColors);
  await helpers.navigateToOverview();
  await helpers.waitForMetricsLoad();

  const badges = await helpers.getConfidenceBadges();

  badges.forEach(badge => {
    if (badge.percentage >= 75) {
      expect(badge.label).toBe('High Confidence');
    }
  });
});
```

### Example 4: Test Card Structure

```typescript
import { test, expect } from '@playwright/test';
import { OverviewTabHelpers, mockOverviewMetrics } from './test-helpers';

test('should render complete card structure', async ({ page }) => {
  const helpers = new OverviewTabHelpers(page);

  await helpers.mockMetricsAPI(mockOverviewMetrics.withColors);
  await helpers.navigateToOverview();
  await helpers.waitForMetricsLoad();

  const cards = await helpers.getInsightCards();

  for (const card of cards) {
    const structure = await helpers.verifyCardStructure(card);

    expect(structure.hasIcon).toBe(true);
    expect(structure.hasLabel).toBe(true);
    expect(structure.hasTitle).toBe(true);
    expect(structure.hasDescription).toBe(true);
  }
});
```

### Example 5: Test Elaborations

```typescript
import { test, expect } from '@playwright/test';
import { OverviewTabHelpers, mockOverviewMetrics } from './test-helpers';

test('should display multiple elaboration points', async ({ page }) => {
  const helpers = new OverviewTabHelpers(page);

  await helpers.mockMetricsAPI(mockOverviewMetrics.withColors);
  await helpers.navigateToOverview();
  await helpers.waitForMetricsLoad();

  const artCard = await helpers.getInsightCard('Art Movement');

  if (artCard) {
    const elaborations = await helpers.getElaborations(artCard);

    expect(elaborations.length).toBeGreaterThan(0);
    expect(elaborations[0]).toContain('Geometric');
  }
});
```

### Example 6: Test Responsive Design

```typescript
import { test, expect } from '@playwright/test';
import { OverviewTabHelpers } from './test-helpers';

test('should have responsive grid classes', async ({ page }) => {
  const helpers = new OverviewTabHelpers(page);

  const gridClasses = await helpers.checkResponsiveGrid();

  expect(gridClasses.mobile).toContain('grid-cols-2');
  expect(gridClasses.desktop).toContain('md:grid-cols-4');
});
```

### Example 7: Test Loading State

```typescript
import { test, expect } from '@playwright/test';
import { OverviewTabHelpers } from './test-helpers';

test('should show loading while metrics load', async ({ page }) => {
  const helpers = new OverviewTabHelpers(page);

  // Delay the API
  await helpers.delayMetricsAPI(2000);

  await helpers.navigateToOverview();

  const isLoading = await helpers.isLoadingState();
  expect(isLoading).toBe(true);

  // Wait for loading to complete
  await helpers.waitForMetricsLoad();

  const isLoading2 = await helpers.isLoadingState();
  expect(isLoading2).toBe(false);
});
```

### Example 8: Test API Requests

```typescript
import { test, expect } from '@playwright/test';
import { OverviewTabHelpers } from './test-helpers';

test('should make correct API requests', async ({ page }) => {
  const helpers = new OverviewTabHelpers(page);

  const requests = await helpers.logMetricsRequests();

  await helpers.navigateToOverview();
  await helpers.waitForMetricsLoad();

  expect(requests.length).toBeGreaterThan(0);
  expect(requests[0]).toContain('/overview/metrics');
});
```

## Data Structure Reference

### ElaboratedMetric
```typescript
interface ElaboratedMetric {
  primary: string;           // Main insight
  elaborations: string[];    // Supporting points
  confidence?: number;       // 0-100 confidence score
}
```

### OverviewMetricsData
```typescript
interface OverviewMetricsData {
  // Simple metrics
  spacing_scale_system: string | null;
  spacing_uniformity: number;
  color_palette_type: string | null;
  design_system_maturity: string;

  // Elaborated insights
  art_movement: ElaboratedMetric | null;
  emotional_tone: ElaboratedMetric | null;
  temperature_profile: ElaboratedMetric | null;

  // Token counts
  summary: {
    total_colors: number;
    total_spacing: number;
    total_typography: number;
    total_shadows: number;
  };

  // Source tracking
  source?: {
    has_extracted_colors: boolean;
    has_extracted_spacing: boolean;
    has_extracted_typography: boolean;
  };
}
```

## Best Practices

### 1. Always Initialize Helpers
```typescript
const helpers = new OverviewTabHelpers(page);
```

### 2. Use Mock Data for Deterministic Tests
```typescript
await helpers.mockMetricsAPI(mockOverviewMetrics.withColors);
```

### 3. Wait for Async Operations
```typescript
await helpers.waitForMetricsLoad();
```

### 4. Check State Before Assertions
```typescript
const isEmpty = await helpers.isEmptyState();
if (!isEmpty) {
  const stats = await helpers.getSummaryStats();
  // Assert on stats
}
```

### 5. Use Specific Assertions
Instead of:
```typescript
await expect(element).toBeVisible();
```

Use:
```typescript
await assertElementIsVisible(element);
```

## Performance Tips

- **Reuse helpers**: Create one instance per test
- **Mock APIs**: Faster than real requests
- **Use count assertions**: Avoid looping when possible
- **Cache selectors**: Reuse located elements

## Debugging

Add logging to helpers:

```typescript
const helpers = new OverviewTabHelpers(page);

// Log all stats
const stats = await helpers.getSummaryStats();
console.log('Stats:', stats);

// Log all badges
const badges = await helpers.getConfidenceBadges();
console.log('Badges:', badges);

// Get all text
const text = await helpers.getAllVisibleText();
console.log('Page text:', text);
```

## Common Issues

| Problem | Solution |
|---------|----------|
| Test hangs on load | Use `delayMetricsAPI()` sparingly |
| Elements not found | Check `isEmptyState()` first |
| Flaky responsive tests | Set viewport before navigate |
| Mock data not used | Call `mockMetricsAPI()` before navigation |

## Contributing New Helpers

When adding new helper methods:

1. Add to `OverviewTabHelpers` class
2. Use clear naming: `get*`, `verify*`, `is*`
3. Return typed results
4. Add JSDoc comments
5. Update this guide

Example:
```typescript
/**
 * Get the Design Palette description text
 * @returns Description text or null if not found
 */
async getDesignPaletteDescription(): Promise<string | null> {
  const description = this.page.locator('text=/A system of/');
  return await description.textContent().catch(() => null);
}
```

## References

- **Component:** `frontend/src/components/MetricsOverview.tsx`
- **Test File:** `frontend/playwright/overview-tab.spec.ts`
- **Helpers File:** `frontend/playwright/test-helpers.ts`
- **Quick Ref:** `OVERVIEW_TESTS_QUICK_REFERENCE.md`

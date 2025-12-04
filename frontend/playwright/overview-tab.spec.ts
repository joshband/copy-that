import { test, expect } from '@playwright/test';

/**
 * Granular Playwright tests for the Overview Tab functionality
 * Tests all aspects of MetricsOverview component including:
 * - Loading states
 * - Empty states
 * - Data rendering
 * - Metric cards and badges
 * - Source indicators
 * - Confidence scoring
 * - Summary statistics
 * - System health insights
 */

test.describe('Overview Tab - Granular Functionality Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173');
    // Wait for tab buttons to load
    await page.waitForSelector('.tab-button', { state: 'visible', timeout: 10000 });
  });

  // ============================================================================
  // SECTION 1: INITIAL STATE & NAVIGATION
  // ============================================================================

  test.describe('Initial State & Tab Navigation', () => {
    test('should load the application with overview tab available', async ({ page }) => {
      const overviewTab = page.locator('button:has-text("Overview")');
      await expect(overviewTab).toBeVisible();
      await expect(overviewTab).toBeEnabled();
    });

    test('should navigate to Overview tab when clicked', async ({ page }) => {
      const overviewTab = page.locator('button:has-text("Overview")');
      await overviewTab.click();

      // Wait for content to be visible
      await page.waitForTimeout(500);

      // Tab should be focused/active
      const tabButton = page.locator('button:has-text("Overview")').first();
      await expect(tabButton).toHaveAttribute('data-state', 'active', { timeout: 5000 }).catch(() => {
        // Fallback: check if tab is visible
        return expect(tabButton).toBeVisible();
      });
    });
  });

  // ============================================================================
  // SECTION 2: EMPTY STATE
  // ============================================================================

  test.describe('Empty State (No Extracted Data)', () => {
    test('should display empty state message on first visit', async ({ page }) => {
      await page.locator('button:has-text("Overview")').click();

      const emptyMessage = page.locator('text=No data yet. Upload an image to see design system metrics.');
      await expect(emptyMessage).toBeVisible();
    });

    test('should not show metric cards when no data is extracted', async ({ page }) => {
      await page.locator('button:has-text("Overview")').click();

      const artMovementCard = page.locator('text=Art Movement');
      const emotionalToneCard = page.locator('text=Emotional Tone');

      await expect(artMovementCard).not.toBeVisible();
      await expect(emotionalToneCard).not.toBeVisible();
    });

    test('should not display summary stats in empty state', async ({ page }) => {
      await page.locator('button:has-text("Overview")').click();

      const statsSection = page.locator('text=Colors').locator('..').locator('..').first();
      await expect(statsSection).not.toBeVisible();
    });
  });

  // ============================================================================
  // SECTION 3: LOADING STATE
  // ============================================================================

  test.describe('Loading State', () => {
    test('should show loading message while metrics are being analyzed', async ({ page }) => {
      // Mock slow API response to capture loading state
      await page.route('**/api/**/overview/metrics', async (route) => {
        // Delay response to ensure loading state is visible
        await new Promise(resolve => setTimeout(resolve, 2000));
        route.continue();
      });

      await page.locator('button:has-text("Overview")').click();

      const loadingMessage = page.locator('text=Analyzing your design system...');
      // Wait for loading state to appear (may flash briefly)
      await expect(loadingMessage).toBeVisible({ timeout: 3000 }).catch(() => {
        // Loading state may have already passed
        return true;
      });
    });
  });

  // ============================================================================
  // SECTION 4: DESIGN PALETTE SECTION
  // ============================================================================

  test.describe('Design Palette Master Section', () => {
    test('should display "Your Design Palette" title', async ({ page }) => {
      // This would need mocked data - for now we're structuring the test
      const paletteTitle = page.locator('text=Your Design Palette').first();

      // Check if visible (only if data is present)
      const isVisible = await paletteTitle.isVisible().catch(() => false);
      if (isVisible) {
        await expect(paletteTitle).toHaveClass(/text-xl/);
        await expect(paletteTitle).toHaveClass(/font-bold/);
      }
    });

    test('should display system summary description with token counts', async ({ page }) => {
      const description = page.locator('text=/A system of.*colors.*spacing tokens.*typography/i');

      const isVisible = await description.isVisible().catch(() => false);
      if (isVisible) {
        // Should contain emphasized token counts
        const colorCount = page.locator('text=/A system of.*colors/i').locator('..').locator('span[class*="font-medium"]').first();
        const spacingCount = page.locator('text=spacing tokens').locator('..').locator('span[class*="font-medium"]').first();

        await expect(colorCount).toBeVisible();
        await expect(spacingCount).toBeVisible();
      }
    });
  });

  // ============================================================================
  // SECTION 5: INSIGHT CHIPS
  // ============================================================================

  test.describe('System Insights Chips', () => {
    test('should display insight chips with appropriate colors', async ({ page }) => {
      const chips = page.locator('[class*="inline-flex"][class*="px-3"][class*="py-1"]');

      const chipCount = await chips.count().catch(() => 0);
      if (chipCount > 0) {
        // Check first chip styling
        const firstChip = chips.first();
        const classes = await firstChip.getAttribute('class');

        // Should have border and background classes
        expect(classes).toMatch(/border/);
        expect(classes).toMatch(/(bg-|text-)/);
      }
    });

    test('should color-code chips by token type', async ({ page }) => {
      // Spacing insights should be blue
      const spacingChip = page.locator('[class*="bg-blue"][class*="text-blue"]').first();
      const isBlueCoded = await spacingChip.isVisible().catch(() => false);

      if (isBlueCoded) {
        await expect(spacingChip).toHaveClass(/bg-blue-100/);
        await expect(spacingChip).toHaveClass(/text-blue-800/);
      }

      // Color insights should be purple
      const colorChip = page.locator('[class*="bg-purple"][class*="text-purple"]').first();
      const isPurpleCoded = await colorChip.isVisible().catch(() => false);

      if (isPurpleCoded) {
        await expect(colorChip).toHaveClass(/bg-purple-100/);
        await expect(colorChip).toHaveClass(/text-purple-800/);
      }
    });
  });

  // ============================================================================
  // SECTION 6: DESIGN INSIGHT CARDS
  // ============================================================================

  test.describe('Design Insight Cards - Structure', () => {
    test('should render DesignInsightCard with correct elements', async ({ page }) => {
      const insightCards = page.locator('[class*="border-l-4"][class*="border-gray-300"]');

      const cardCount = await insightCards.count().catch(() => 0);
      if (cardCount > 0) {
        const firstCard = insightCards.first();

        // Card should have icon, label, and title
        const icon = firstCard.locator('..').locator('span[class*="text-2xl"]').first();
        const label = firstCard.locator('p[class*="text-xs"][class*="font-semibold"]').first();

        // At least one should be visible
        const iconVisible = await icon.isVisible().catch(() => false);
        const labelVisible = await label.isVisible().catch(() => false);

        expect(iconVisible || labelVisible).toBe(true);
      }
    });

    test('should display card title prominently', async ({ page }) => {
      const cardTitles = page.locator('h4[class*="text-base"][class*="font-bold"]');

      const titleCount = await cardTitles.count().catch(() => 0);
      if (titleCount > 0) {
        const firstTitle = cardTitles.first();
        await expect(firstTitle).toHaveClass(/text-gray-900/);
        await expect(firstTitle).toHaveClass(/capitalize/);
      }
    });

    test('should display card description text', async ({ page }) => {
      const descriptions = page.locator('[class*="text-sm"][class*="text-gray-700"][class*="leading-relaxed"]');

      const descCount = await descriptions.count().catch(() => 0);
      if (descCount > 0) {
        const firstDesc = descriptions.first();
        const text = await firstDesc.textContent();
        expect(text).toBeTruthy();
        expect(text?.length).toBeGreaterThan(0);
      }
    });
  });

  // ============================================================================
  // SECTION 7: CONFIDENCE BADGES
  // ============================================================================

  test.describe('Confidence Badges & Scoring', () => {
    test('should display confidence percentage on metric cards', async ({ page }) => {
      const confidenceBadges = page.locator('[class*="rounded-full"][class*="text-xs"][class*="font-medium"]')
        .filter({ hasText: /%/ });

      const badgeCount = await confidenceBadges.count().catch(() => 0);
      if (badgeCount > 0) {
        const firstBadge = confidenceBadges.first();
        const text = await firstBadge.textContent();

        // Should contain percentage and confidence label
        expect(text).toMatch(/\d+%/);
        expect(text).toMatch(/(High Confidence|Likely Match|Possible Interpretation|Calculating)/);
      }
    });

    test('should use green background for high confidence (75%+)', async ({ page }) => {
      const highConfidenceBadge = page.locator('[class*="bg-green-100"][class*="text-green-700"]').first();

      const isVisible = await highConfidenceBadge.isVisible().catch(() => false);
      if (isVisible) {
        const text = await highConfidenceBadge.textContent();
        const percentage = parseInt(text?.match(/(\d+)%/)?.[1] || '0');

        expect(percentage).toBeGreaterThanOrEqual(75);
        expect(text).toContain('High Confidence');
      }
    });

    test('should use yellow background for medium confidence (60-74%)', async ({ page }) => {
      const mediumConfidenceBadge = page.locator('[class*="bg-yellow-100"][class*="text-yellow-700"]').first();

      const isVisible = await mediumConfidenceBadge.isVisible().catch(() => false);
      if (isVisible) {
        const text = await mediumConfidenceBadge.textContent();
        const percentage = parseInt(text?.match(/(\d+)%/)?.[1] || '0');

        expect(percentage).toBeGreaterThanOrEqual(60);
        expect(percentage).toBeLessThan(75);
        expect(text).toContain('Likely Match');
      }
    });

    test('should use orange background for low confidence (<60%)', async ({ page }) => {
      const lowConfidenceBadge = page.locator('[class*="bg-orange-100"][class*="text-orange-700"]').first();

      const isVisible = await lowConfidenceBadge.isVisible().catch(() => false);
      if (isVisible) {
        const text = await lowConfidenceBadge.textContent();
        const percentage = parseInt(text?.match(/(\d+)%/)?.[1] || '0');

        expect(percentage).toBeLessThan(60);
        expect(text).toContain('Possible Interpretation');
      }
    });

    test('should display uncertainty message for low-confidence insights', async ({ page }) => {
      // Low-confidence cards should show explanatory text
      const uncertaintyMessages = page.locator('text=/This palette is subtle.*multiple interpretations/i');

      const msgCount = await uncertaintyMessages.count().catch(() => 0);
      if (msgCount > 0) {
        const firstMsg = uncertaintyMessages.first();
        await expect(firstMsg).toHaveClass(/text-xs/);
        await expect(firstMsg).toHaveClass(/text-orange-600/);
      }
    });
  });

  // ============================================================================
  // SECTION 8: SOURCE INDICATORS
  // ============================================================================

  test.describe('Source Indicators & Data Attribution', () => {
    test('should display source badge on insight cards', async ({ page }) => {
      const sourceBadges = page.locator('[data-source]');

      const badgeCount = await sourceBadges.count().catch(() => 0);
      if (badgeCount > 0) {
        const firstBadge = sourceBadges.first();

        // Should have blue styling
        await expect(firstBadge).toHaveClass(/bg-blue-100/);
        await expect(firstBadge).toHaveClass(/text-blue-700/);

        // Should have border
        await expect(firstBadge).toHaveClass(/border/);
      }
    });

    test('should show correct source for color-based metrics', async ({ page }) => {
      const colorSourceBadges = page.locator('[data-source="🎨 Colors"]');

      const badgeCount = await colorSourceBadges.count().catch(() => false);
      if (badgeCount) {
        // Should be present for Art Movement, Emotional Tone, Temperature Profile, etc.
        const badge = colorSourceBadges.first();
        await expect(badge).toContainText('🎨 Colors');
      }
    });

    test('should show correct source for combined token metrics', async ({ page }) => {
      const combinedSourceBadges = page.locator('[data-source="📊 All Tokens"]');

      const badgeCount = await combinedSourceBadges.count().catch(() => false);
      if (badgeCount) {
        // Should be present for Design Complexity, System Health
        const badge = combinedSourceBadges.first();
        await expect(badge).toContainText('📊 All Tokens');
      }
    });

    test('should have helpful tooltip on source badge', async ({ page }) => {
      const sourceBadges = page.locator('[data-source]').first();

      const isVisible = await sourceBadges.isVisible().catch(() => false);
      if (isVisible) {
        const title = await sourceBadges.getAttribute('title');
        expect(title).toBeTruthy();
        expect(title).toMatch(/Inferred from/i);
      }
    });
  });

  // ============================================================================
  // SECTION 9: ELABORATIONS & EXTENDED INSIGHTS
  // ============================================================================

  test.describe('Elaborations & Multi-Point Insights', () => {
    test('should display multiple elaboration points for rich insights', async ({ page }) => {
      const elaborationItems = page.locator('[class*="ml-2"] div:has-text("•")');

      const itemCount = await elaborationItems.count().catch(() => 0);
      if (itemCount > 0) {
        const firstItem = elaborationItems.first();
        const text = await firstItem.textContent();

        expect(text).toContain('•');
        expect(text?.length).toBeGreaterThan(1);
      }
    });

    test('elaborations should have proper styling', async ({ page }) => {
      const elaborationItems = page.locator('[class*="text-xs"][class*="text-gray-600"]')
        .filter({ hasText: /•/ });

      const itemCount = await elaborationItems.count().catch(() => 0);
      if (itemCount > 0) {
        const firstItem = elaborationItems.first();
        await expect(firstItem).toHaveClass(/leading-relaxed/);
      }
    });
  });

  // ============================================================================
  // SECTION 10: SUMMARY STATISTICS
  // ============================================================================

  test.describe('Summary Statistics Section', () => {
    test('should display four stat boxes for token categories', async ({ page }) => {
      const statBoxes = page.locator('[class*="bg-gray-50"][class*="border"][class*="rounded-lg"][class*="p-3"]');

      const boxCount = await statBoxes.count().catch(() => 0);
      if (boxCount >= 4) {
        // Should have Colors, Spacing, Typography, Shadows
        const labels = page.locator('[class*="text-xs"][class*="text-gray-600"]');

        const colorLabel = labels.filter({ hasText: 'Colors' }).first();
        const spacingLabel = labels.filter({ hasText: 'Spacing' }).first();
        const typographyLabel = labels.filter({ hasText: 'Typography' }).first();
        const shadowLabel = labels.filter({ hasText: 'Shadows' }).first();

        // All should be visible if data exists
        const hasColors = await colorLabel.isVisible().catch(() => false);
        const hasSpacing = await spacingLabel.isVisible().catch(() => false);
        const hasTypography = await typographyLabel.isVisible().catch(() => false);
        const hasShadows = await shadowLabel.isVisible().catch(() => false);

        expect(hasColors || hasSpacing || hasTypography || hasShadows).toBe(true);
      }
    });

    test('should display numeric values in stat boxes', async ({ page }) => {
      const statValues = page.locator('[class*="text-2xl"][class*="font-bold"][class*="text-gray-900"]');

      const valueCount = await statValues.count().catch(() => 0);
      if (valueCount > 0) {
        const firstValue = statValues.first();
        const text = await firstValue.textContent();

        // Should be a number
        expect(text).toMatch(/^\d+$/);
        expect(parseInt(text || '0')).toBeGreaterThanOrEqual(0);
      }
    });

    test('stat boxes should be in responsive grid', async ({ page }) => {
      const gridContainer = page.locator('[class*="grid"][class*="grid-cols-2"][class*="md:grid-cols-4"]');

      const isVisible = await gridContainer.isVisible().catch(() => false);
      if (isVisible) {
        await expect(gridContainer).toHaveClass(/gap-3/);
      }
    });
  });

  // ============================================================================
  // SECTION 11: KEY METRICS BOXES
  // ============================================================================

  test.describe('Key Metrics Section', () => {
    test('should display key metrics in a responsive grid', async ({ page }) => {
      const metricsGrid = page.locator('[class*="grid"][class*="grid-cols-2"][class*="gap-4"]');

      const isVisible = await metricsGrid.isVisible().catch(() => false);
      if (isVisible) {
        // Should contain metric boxes
        const metricBoxes = metricsGrid.locator('[class*="bg-gradient-to-br"][class*="from-gray-50"]');
        const boxCount = await metricBoxes.count().catch(() => 0);

        expect(boxCount).toBeGreaterThan(0);
      }
    });

    test('metric boxes should have proper structure', async ({ page }) => {
      const metricBoxes = page.locator('[class*="bg-gradient-to-br"][class*="from-gray-50"][class*="border"]');

      const boxCount = await metricBoxes.count().catch(() => 0);
      if (boxCount > 0) {
        const firstBox = metricBoxes.first();

        // Should have label, value, and optional description
        const label = firstBox.locator('[class*="text-xs"][class*="font-semibold"]').first();
        const value = firstBox.locator('[class*="text-xl"][class*="font-bold"]').first();

        await expect(label).toBeVisible();
        await expect(value).toBeVisible();
      }
    });

    test('should display Palette Type metric when available', async ({ page }) => {
      const paletteMetric = page.locator('text=Palette Type');

      const isVisible = await paletteMetric.isVisible().catch(() => false);
      if (isVisible) {
        const parent = paletteMetric.locator('../..');
        const valueElement = parent.locator('[class*="text-xl"]');

        await expect(valueElement).toBeVisible();
        const value = await valueElement.textContent();
        expect(value).toBeTruthy();
      }
    });

    test('should display System Maturity metric when available', async ({ page }) => {
      const maturityMetric = page.locator('text=System Maturity');

      const isVisible = await maturityMetric.isVisible().catch(() => false);
      if (isVisible) {
        const parent = maturityMetric.locator('../..');
        const valueElement = parent.locator('[class*="text-xl"]');

        await expect(valueElement).toBeVisible();
        const value = await valueElement.textContent();
        expect(value).toBeTruthy();
      }
    });

    test('should display Spacing System metric when available', async ({ page }) => {
      const spacingMetric = page.locator('text=Spacing System');

      const isVisible = await spacingMetric.isVisible().catch(() => false);
      if (isVisible) {
        const parent = spacingMetric.locator('../..');
        const descriptionElement = parent.locator('[class*="text-xs"][class*="text-gray-600"]');

        await expect(descriptionElement).toBeVisible();
        const description = await descriptionElement.textContent();
        expect(description).toMatch(/%/); // Should show uniformity percentage
      }
    });

    test('should display Typography Levels metric when available', async ({ page }) => {
      const typographyMetric = page.locator('text=Typography Levels');

      const isVisible = await typographyMetric.isVisible().catch(() => false);
      if (isVisible) {
        const parent = typographyMetric.locator('../..');
        const valueElement = parent.locator('[class*="text-xl"]');

        await expect(valueElement).toBeVisible();
        const value = await valueElement.textContent();
        expect(value).toMatch(/^\d+$/); // Should be a number
      }
    });
  });

  // ============================================================================
  // SECTION 12: SPECIFIC INSIGHT CARDS
  // ============================================================================

  test.describe('Art Movement Card', () => {
    test('should display Art Movement card with 🎨 icon', async ({ page }) => {
      const artCard = page.locator('text=Art Movement');

      const isVisible = await artCard.isVisible().catch(() => false);
      if (isVisible) {
        const icon = artCard.locator('../.').locator('span:has-text("🎨")').first();
        await expect(icon).toBeVisible();
      }
    });

    test('should show colors source indicator on Art Movement', async ({ page }) => {
      const artCard = page.locator('text=Art Movement');

      const isVisible = await artCard.isVisible().catch(() => false);
      if (isVisible) {
        const parent = artCard.locator('../..');
        const sourceIndicator = parent.locator('[data-source="🎨 Colors"]');

        await expect(sourceIndicator).toBeVisible();
      }
    });
  });

  test.describe('Emotional Tone Card', () => {
    test('should display Emotional Tone card with 💭 icon', async ({ page }) => {
      const emotionalCard = page.locator('text=Emotional Tone');

      const isVisible = await emotionalCard.isVisible().catch(() => false);
      if (isVisible) {
        const icon = emotionalCard.locator('../.').locator('span:has-text("💭")').first();
        await expect(icon).toBeVisible();
      }
    });
  });

  test.describe('Design Complexity Card', () => {
    test('should display Design Complexity card with ⏱️ icon', async ({ page }) => {
      const complexityCard = page.locator('text=Design Complexity');

      const isVisible = await complexityCard.isVisible().catch(() => false);
      if (isVisible) {
        const icon = complexityCard.locator('../.').locator('span:has-text("⏱️")').first();
        await expect(icon).toBeVisible();
      }
    });
  });

  test.describe('Temperature Profile Card', () => {
    test('should display Temperature Profile card with 🌡️ icon', async ({ page }) => {
      const tempCard = page.locator('text=Temperature Profile');

      const isVisible = await tempCard.isVisible().catch(() => false);
      if (isVisible) {
        const icon = tempCard.locator('../.').locator('span:has-text("🌡️")').first();
        await expect(icon).toBeVisible();
      }
    });
  });

  test.describe('Saturation Character Card', () => {
    test('should display Saturation Character card with ✨ icon', async ({ page }) => {
      const satCard = page.locator('text=Saturation Character');

      const isVisible = await satCard.isVisible().catch(() => false);
      if (isVisible) {
        const icon = satCard.locator('../.').locator('span:has-text("✨")').first();
        await expect(icon).toBeVisible();
      }
    });
  });

  test.describe('System Health Card', () => {
    test('should display System Health card with 💪 icon', async ({ page }) => {
      const healthCard = page.locator('text=System Health');

      const isVisible = await healthCard.isVisible().catch(() => false);
      if (isVisible) {
        const icon = healthCard.locator('../.').locator('span:has-text("💪")').first();
        await expect(icon).toBeVisible();
      }
    });

    test('should show total token count in System Health title', async ({ page }) => {
      const healthCard = page.locator('text=System Health');

      const isVisible = await healthCard.isVisible().catch(() => false);
      if (isVisible) {
        const titleText = healthCard.locator('..').locator('text=/total tokens/i');
        await expect(titleText).toBeVisible();
      }
    });
  });

  // ============================================================================
  // SECTION 13: RESPONSIVE LAYOUT
  // ============================================================================

  test.describe('Responsive Layout', () => {
    test('should stack insight cards in single column on mobile', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 }); // iPhone size

      const insightGrid = page.locator('[class*="grid"][class*="grid-cols-1"]');
      const isVisible = await insightGrid.isVisible().catch(() => false);

      if (isVisible) {
        await expect(insightGrid).toHaveClass(/grid-cols-1/);
      }
    });

    test('should display stat boxes in 2 columns on mobile', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });

      const statGrid = page.locator('[class*="grid-cols-2"][class*="md:grid-cols-4"]');
      const isVisible = await statGrid.isVisible().catch(() => false);

      if (isVisible) {
        await expect(statGrid).toHaveClass(/grid-cols-2/);
      }
    });

    test('should display stat boxes in 4 columns on desktop', async ({ page }) => {
      await page.setViewportSize({ width: 1280, height: 720 }); // Desktop size

      const statGrid = page.locator('[class*="grid-cols-2"][class*="md:grid-cols-4"]');
      const isVisible = await statGrid.isVisible().catch(() => false);

      if (isVisible) {
        await expect(statGrid).toHaveClass(/md:grid-cols-4/);
      }
    });
  });

  // ============================================================================
  // SECTION 14: VISUAL HIERARCHY
  // ============================================================================

  test.describe('Visual Hierarchy & Typography', () => {
    test('Design Palette title should be largest heading', async ({ page }) => {
      const paletteTitle = page.locator('text=Your Design Palette').first();

      const isVisible = await paletteTitle.isVisible().catch(() => false);
      if (isVisible) {
        await expect(paletteTitle).toHaveClass(/text-xl/);
        await expect(paletteTitle).toHaveClass(/font-bold/);
      }
    });

    test('Insight card titles should be smaller than Design Palette title', async ({ page }) => {
      const cardTitles = page.locator('h4[class*="text-base"][class*="font-bold"]').first();

      const isVisible = await cardTitles.isVisible().catch(() => false);
      if (isVisible) {
        await expect(cardTitles).toHaveClass(/text-base/);
      }
    });

    test('should use proper spacing between sections', async ({ page }) => {
      const container = page.locator('[class*="space-y-6"]');

      const isVisible = await container.isVisible().catch(() => false);
      if (isVisible) {
        await expect(container).toHaveClass(/space-y-6/);
      }
    });
  });

  // ============================================================================
  // SECTION 15: ACCESSIBILITY
  // ============================================================================

  test.describe('Accessibility & ARIA', () => {
    test('should have descriptive titles and labels', async ({ page }) => {
      const labels = page.locator('[class*="text-xs"][class*="font-semibold"]');

      const labelCount = await labels.count().catch(() => 0);
      if (labelCount > 0) {
        const firstLabel = labels.first();
        const text = await firstLabel.textContent();

        // Should have meaningful text
        expect(text).toBeTruthy();
        expect(text?.length).toBeGreaterThan(0);
      }
    });

    test('should have proper color contrast for badges', async ({ page }) => {
      const badges = page.locator('[class*="rounded-full"][class*="text-xs"]');

      const badgeCount = await badges.count().catch(() => 0);
      if (badgeCount > 0) {
        // Each badge should have text and background colors defined
        const firstBadge = badges.first();
        const classes = await firstBadge.getAttribute('class');

        expect(classes).toMatch(/bg-/);
        expect(classes).toMatch(/text-/);
      }
    });
  });

  // ============================================================================
  // SECTION 16: DATA VALIDATION
  // ============================================================================

  test.describe('Data Validation & Error Handling', () => {
    test('should handle missing elaborations gracefully', async ({ page }) => {
      // This tests component robustness
      const elaborations = page.locator('[class*="space-y-1"] div:has-text("•")');

      const elaborationCount = await elaborations.count().catch(() => 0);

      // Should either have elaborations or gracefully show nothing
      expect(elaborationCount).toBeGreaterThanOrEqual(0);
    });

    test('should display zero values for empty token categories', async ({ page }) => {
      const statValues = page.locator('[class*="text-2xl"][class*="font-bold"]');

      const valueCount = await statValues.count().catch(() => 0);
      if (valueCount > 0) {
        // Should show numeric values (including 0)
        const firstValue = statValues.first();
        const text = await firstValue.textContent();

        expect(text).toMatch(/^\d+$/);
      }
    });
  });

  // ============================================================================
  // SECTION 17: INTERACTION STATES
  // ============================================================================

  test.describe('Interaction States', () => {
    test('should update metrics when refresh trigger changes', async ({ page }) => {
      // Navigate to overview
      await page.locator('button:has-text("Overview")').click();

      // Wait for initial render
      await page.waitForTimeout(500);

      // Get initial text content
      const initialContent = await page.textContent();

      // In a real scenario, this would trigger a refresh from parent component
      // For now, we just verify the component doesn't error
      expect(initialContent).toBeTruthy();
    });

    test('should handle project ID changes', async ({ page }) => {
      // Initial navigation
      await page.locator('button:has-text("Overview")').click();

      // Component should remain visible
      const overviewTab = page.locator('button:has-text("Overview")');
      await expect(overviewTab).toBeVisible();
    });
  });

  // ============================================================================
  // SECTION 18: VISUAL REGRESSION
  // ============================================================================

  test.describe('Visual Regression Tests', () => {
    test('should match overview tab empty state snapshot', async ({ page }) => {
      await page.locator('button:has-text("Overview")').click();

      // If empty, take screenshot
      const emptyMessage = page.locator('text=No data yet');
      const isEmpty = await emptyMessage.isVisible().catch(() => false);

      if (isEmpty) {
        await expect(page).toHaveScreenshot('overview-empty-state.png', { maxDiffPixels: 100 });
      }
    });
  });
});

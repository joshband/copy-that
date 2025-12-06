/**
 * Test Helper Functions and Fixtures
 * Reusable utilities for Overview Tab tests
 */

import { Page, Locator, expect } from '@playwright/test';

/**
 * Mock Overview Metrics Data for testing
 */
export const mockOverviewMetrics = {
  emptyState: {
    spacing_scale_system: null,
    spacing_uniformity: 0,
    color_harmony_type: null,
    color_palette_type: null,
    color_temperature: null,
    typography_hierarchy_depth: 0,
    typography_scale_type: null,
    design_system_maturity: 'Emerging',
    token_organization_quality: 'Minimal',
    insights: [],
    art_movement: null,
    emotional_tone: null,
    design_complexity: null,
    saturation_character: null,
    temperature_profile: null,
    design_system_insight: null,
    summary: {
      total_colors: 0,
      total_spacing: 0,
      total_typography: 0,
      total_shadows: 0,
    },
    source: {
      has_extracted_colors: false,
      has_extracted_spacing: false,
      has_extracted_typography: false,
    },
  },

  withColors: {
    spacing_scale_system: 'Fibonacci',
    spacing_uniformity: 0.92,
    color_harmony_type: 'Complementary',
    color_palette_type: 'Analogous',
    color_temperature: 'Warm',
    typography_hierarchy_depth: 4,
    typography_scale_type: 'Golden Ratio',
    design_system_maturity: 'Mature',
    token_organization_quality: 'Well-organized',
    insights: [
      'Warm color palette with energetic vibes',
      'Fibonacci spacing creates natural rhythm',
      'Typography hierarchy supports clear hierarchy',
    ],
    art_movement: {
      primary: 'Art Deco',
      elaborations: [
        'Geometric shapes and bold colors define this movement',
        'Symmetrical layouts create formal elegance',
      ],
      confidence: 82,
    },
    emotional_tone: {
      primary: 'Energetic and Bold',
      elaborations: [
        'Warm colors evoke passion and energy',
        'Strong contrast demands attention',
      ],
      confidence: 76,
    },
    design_complexity: {
      primary: 'Moderate',
      elaborations: [
        'Balanced use of whitespace and elements',
        'Clear visual hierarchy present',
      ],
      confidence: 71,
    },
    saturation_character: {
      primary: 'High Saturation',
      elaborations: [
        'Vibrant colors create visual excitement',
        'Limited use of neutrals',
      ],
      confidence: 88,
    },
    temperature_profile: {
      primary: 'Warm',
      elaborations: [
        'Orange and red tones dominate',
        'Creates inviting and energetic feeling',
      ],
      confidence: 94,
    },
    design_system_insight: {
      primary: 'Well-Structured Design System',
      elaborations: [
        '24 colors across 4 categories',
        'Consistent spacing scale',
        'Scalable typography system',
      ],
      confidence: 85,
    },
    summary: {
      total_colors: 24,
      total_spacing: 12,
      total_typography: 8,
      total_shadows: 4,
    },
    source: {
      has_extracted_colors: true,
      has_extracted_spacing: true,
      has_extracted_typography: true,
    },
  },

  lowConfidence: {
    spacing_scale_system: 'Irregular',
    spacing_uniformity: 0.45,
    color_harmony_type: 'Unknown',
    color_palette_type: 'Eclectic',
    color_temperature: 'Mixed',
    typography_hierarchy_depth: 2,
    typography_scale_type: 'Custom',
    design_system_maturity: 'Emerging',
    token_organization_quality: 'Minimal',
    insights: ['Design system appears experimental'],
    art_movement: {
      primary: 'Contemporary',
      elaborations: [
        'Modern approach with experimental elements',
        'Difficult to categorize',
      ],
      confidence: 42,
    },
    emotional_tone: {
      primary: 'Ambiguous',
      elaborations: [
        'Mixed color signals create complex mood',
        'Unclear emotional direction',
      ],
      confidence: 38,
    },
    design_complexity: {
      primary: 'High',
      elaborations: [
        'Many elements with unclear hierarchy',
        'Complexity obscures main message',
      ],
      confidence: 35,
    },
    saturation_character: {
      primary: 'Mixed Saturation',
      elaborations: [
        'Both vibrant and muted tones present',
        'Lacks color consistency',
      ],
      confidence: 48,
    },
    temperature_profile: {
      primary: 'Neutral-Warm',
      elaborations: [
        'Equal distribution of warm and cool tones',
        'Temperature unclear',
      ],
      confidence: 52,
    },
    design_system_insight: {
      primary: 'Developing Design System',
      elaborations: [
        'Limited token consistency',
        'Emerging patterns detected',
      ],
      confidence: 45,
    },
    summary: {
      total_colors: 8,
      total_spacing: 3,
      total_typography: 2,
      total_shadows: 1,
    },
    source: {
      has_extracted_colors: true,
      has_extracted_spacing: false,
      has_extracted_typography: false,
    },
  },
};

/**
 * Overview Tab Helper Functions
 */

export class OverviewTabHelpers {
  constructor(private page: Page) {}

  /**
   * Navigate to the Overview tab
   */
  async navigateToOverview(): Promise<void> {
    const overviewTab = this.page.locator('button:has-text("Overview")');
    await overviewTab.click();
    await this.page.waitForTimeout(500);
  }

  /**
   * Check if empty state is displayed
   */
  async isEmptyState(): Promise<boolean> {
    const emptyMessage = this.page.locator('text=No data yet');
    return await emptyMessage.isVisible().catch(() => false);
  }

  /**
   * Check if loading state is displayed
   */
  async isLoadingState(): Promise<boolean> {
    const loadingMessage = this.page.locator('text=Analyzing your design system');
    return await loadingMessage.isVisible().catch(() => false);
  }

  /**
   * Get all insight cards currently visible
   */
  async getInsightCards(): Promise<Locator[]> {
    const cards = this.page.locator('[class*="border-l-4"][class*="border-gray-300"]');
    const count = await cards.count();
    const cardArray: Locator[] = [];

    for (let i = 0; i < count; i++) {
      cardArray.push(cards.nth(i));
    }

    return cardArray;
  }

  /**
   * Get a specific insight card by label
   */
  async getInsightCard(label: string): Promise<Locator | null> {
    const card = this.page.locator(`text=${label}`);
    const isVisible = await card.isVisible().catch(() => false);

    if (isVisible) {
      return card.locator('../..');
    }

    return null;
  }

  /**
   * Get all confidence badges and their values
   */
  async getConfidenceBadges(): Promise<{ percentage: number; label: string }[]> {
    const badges = this.page.locator('[class*="rounded-full"][class*="text-xs"][class*="font-medium"]')
      .filter({ hasText: /\d+%/ });

    const count = await badges.count();
    const results: { percentage: number; label: string }[] = [];

    for (let i = 0; i < count; i++) {
      const badge = badges.nth(i);
      const text = await badge.textContent();

      if (text) {
        const percentageMatch = text.match(/(\d+)%/);
        const percentage = percentageMatch ? parseInt(percentageMatch[1]) : 0;
        const label = text.replace(/\d+%/, '').trim();

        results.push({ percentage, label });
      }
    }

    return results;
  }

  /**
   * Get all source indicators and their values
   */
  async getSourceIndicators(): Promise<string[]> {
    const sources = this.page.locator('[data-source]');
    const count = await sources.count();
    const results: string[] = [];

    for (let i = 0; i < count; i++) {
      const source = sources.nth(i);
      const dataSource = await source.getAttribute('data-source');

      if (dataSource && !results.includes(dataSource)) {
        results.push(dataSource);
      }
    }

    return results;
  }

  /**
   * Get summary statistics
   */
  async getSummaryStats(): Promise<{ label: string; value: number }[]> {
    const statBoxes = this.page.locator('[class*="bg-gray-50"][class*="border"][class*="rounded-lg"]');
    const count = await statBoxes.count();
    const results: { label: string; value: number }[] = [];

    for (let i = 0; i < count; i++) {
      const box = statBoxes.nth(i);
      const label = await box.locator('[class*="text-xs"][class*="text-gray-600"]').textContent();
      const value = await box.locator('[class*="text-2xl"][class*="font-bold"]').textContent();

      if (label && value) {
        results.push({
          label: label.trim(),
          value: parseInt(value),
        });
      }
    }

    return results;
  }

  /**
   * Get all insight chips
   */
  async getInsightChips(): Promise<string[]> {
    const chips = this.page.locator('[class*="inline-flex"][class*="px-3"][class*="py-1"][class*="border"]');
    const count = await chips.count();
    const results: string[] = [];

    for (let i = 0; i < count; i++) {
      const chip = chips.nth(i);
      const text = await chip.textContent();

      if (text) {
        results.push(text.trim());
      }
    }

    return results;
  }

  /**
   * Verify Design Palette section exists
   */
  async verifyDesignPaletteSection(): Promise<boolean> {
    const title = this.page.locator('text=Your Design Palette');
    return await title.isVisible().catch(() => false);
  }

  /**
   * Verify Design Insight Card structure
   */
  async verifyCardStructure(card: Locator): Promise<{
    hasIcon: boolean;
    hasLabel: boolean;
    hasTitle: boolean;
    hasDescription: boolean;
  }> {
    const icon = card.locator('span[class*="text-2xl"]');
    const label = card.locator('p[class*="text-xs"][class*="font-semibold"]');
    const title = card.locator('h4');
    const description = card.locator('[class*="text-sm"][class*="text-gray-700"]');

    return {
      hasIcon: await icon.isVisible().catch(() => false),
      hasLabel: await label.isVisible().catch(() => false),
      hasTitle: await title.isVisible().catch(() => false),
      hasDescription: await description.isVisible().catch(() => false),
    };
  }

  /**
   * Verify confidence badge styling based on percentage
   */
  async verifyConfidenceColor(percentage: number): Promise<string> {
    if (percentage >= 75) {
      return 'green';
    } else if (percentage >= 60) {
      return 'yellow';
    } else {
      return 'orange';
    }
  }

  /**
   * Get all elaboration points for a card
   */
  async getElaborations(card: Locator): Promise<string[]> {
    const elaborations = card.locator('[class*="space-y-1"] div:has-text("•")');
    const count = await elaborations.count();
    const results: string[] = [];

    for (let i = 0; i < count; i++) {
      const text = await elaborations.nth(i).textContent();
      if (text) {
        results.push(text.replace(/^•\s*/, '').trim());
      }
    }

    return results;
  }

  /**
   * Check responsive grid classes
   */
  async checkResponsiveGrid(): Promise<{
    mobile: string[];
    desktop: string[];
  }> {
    await this.page.setViewportSize({ width: 375, height: 667 });
    const mobileGrid = this.page.locator('[class*="grid"]').first();
    const mobileClasses = (await mobileGrid.getAttribute('class')) || '';

    await this.page.setViewportSize({ width: 1280, height: 720 });
    const desktopGrid = this.page.locator('[class*="grid"]').first();
    const desktopClasses = (await desktopGrid.getAttribute('class')) || '';

    return {
      mobile: mobileClasses.split(' ').filter(c => c.includes('grid')),
      desktop: desktopClasses.split(' ').filter(c => c.includes('grid')),
    };
  }

  /**
   * Mock API response
   */
  async mockMetricsAPI(mockData: any): Promise<void> {
    await this.page.route('**/api/**/overview/metrics', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockData),
      });
    });
  }

  /**
   * Delay API response
   */
  async delayMetricsAPI(delayMs: number): Promise<void> {
    await this.page.route('**/api/**/overview/metrics', async (route) => {
      await new Promise(resolve => setTimeout(resolve, delayMs));
      route.continue();
    });
  }

  /**
   * Intercept and log metrics API requests
   */
  async logMetricsRequests(): Promise<string[]> {
    const requests: string[] = [];

    this.page.on('request', request => {
      if (request.url().includes('/overview/metrics')) {
        requests.push(`${new Date().toISOString()}: ${request.url()}`);
      }
    });

    return requests;
  }

  /**
   * Wait for metrics to load
   */
  async waitForMetricsLoad(): Promise<void> {
    await this.page.waitForLoadState('networkidle').catch(() => null);
    await this.page.waitForTimeout(500);
  }

  /**
   * Screenshot specific section
   */
  async screenshotSection(selector: string, filename: string): Promise<void> {
    const element = this.page.locator(selector).first();
    const isVisible = await element.isVisible().catch(() => false);

    if (isVisible) {
      await element.screenshot({ path: `screenshots/${filename}` });
    }
  }

  /**
   * Get all visible text on the overview tab
   */
  async getAllVisibleText(): Promise<string> {
    return await this.page.textContent('body') || '';
  }

  /**
   * Validate color contrast ratio (simplified)
   */
  async validateColorContrast(element: Locator): Promise<boolean> {
    const classes = await element.getAttribute('class');

    if (!classes) return false;

    // Simple validation: check if both text and background colors are defined
    const hasBackground = /bg-/.test(classes);
    const hasTextColor = /text-/.test(classes);

    return hasBackground && hasTextColor;
  }
}

/**
 * Test Assertions Helper
 */

export async function assertElementHasText(element: Locator, text: string | RegExp): Promise<void> {
  await expect(element).toContainText(text);
}

export async function assertElementHasClass(element: Locator, className: string | RegExp): Promise<void> {
  await expect(element).toHaveClass(className);
}

export async function assertElementIsVisible(element: Locator): Promise<void> {
  await expect(element).toBeVisible();
}

export async function assertElementIsHidden(element: Locator): Promise<void> {
  await expect(element).not.toBeVisible();
}

export async function assertElementCount(
  locator: Locator,
  expectedCount: number,
  operator: '=' | '>' | '<' | '>=' | '<=' = '='
): Promise<void> {
  const count = await locator.count();

  switch (operator) {
    case '=':
      expect(count).toBe(expectedCount);
      break;
    case '>':
      expect(count).toBeGreaterThan(expectedCount);
      break;
    case '<':
      expect(count).toBeLessThan(expectedCount);
      break;
    case '>=':
      expect(count).toBeGreaterThanOrEqual(expectedCount);
      break;
    case '<=':
      expect(count).toBeLessThanOrEqual(expectedCount);
      break;
  }
}

export async function assertTextMatches(text: string | null, pattern: RegExp): Promise<void> {
  expect(text).toMatch(pattern);
}

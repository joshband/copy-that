import { test, expect } from '@playwright/test';
import path from 'path';

test.describe('Metrics Extraction Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the app
    await page.goto('http://localhost:5173');

    // Wait for the app to load
    await page.waitForSelector('h1', { state: 'visible' });
  });

  test('should display loading state while extracting metrics', async ({ page }) => {
    // Take screenshot of initial state
    await page.screenshot({ path: 'screenshots/01-initial-state.png', fullPage: true });

    // Find and click the tab to overview if not already there
    const overviewTab = page.locator('button:has-text("Overview")');
    if (overviewTab) {
      await overviewTab.click();
    }

    // Should show empty state initially
    const emptyState = page.locator('text=Extract tokens to see overview');
    await expect(emptyState).toBeVisible();
    await page.screenshot({ path: 'screenshots/02-empty-overview.png', fullPage: true });
  });

  test('should show metrics after image extraction with source indicators', async ({ page }) => {
    // Find the image uploader
    const uploadInput = page.locator('#file-input');

    // Use absolute path to test image
    const testImagePath = path.join(process.cwd(), 'frontend/playwright/test-image.png');

    // Set file input to trigger preview
    await uploadInput.setInputFiles(testImagePath);
    await page.waitForTimeout(500); // Wait for preview to render

    // Take screenshot of upload ready state
    await page.screenshot({ path: 'screenshots/03-upload-ready.png', fullPage: true });

    // Find and click the extract button
    const extractBtn = page.locator('.extract-btn');
    await expect(extractBtn).toBeEnabled({ timeout: 5000 });
    await extractBtn.click();

    // Wait for loading chip to appear
    await page.waitForSelector('.loading-chip', { timeout: 5000 });
    await page.screenshot({ path: 'screenshots/04-extraction-loading.png', fullPage: true });

    // Wait for loading chip to disappear (extraction complete)
    await page.waitForSelector('.loading-chip', { state: 'hidden', timeout: 30000 });
    await page.waitForTimeout(1000); // Brief wait for colors to render

    // Take screenshot showing extracted colors
    await page.screenshot({ path: 'screenshots/05-colors-extracted.png', fullPage: true });

    // Switch to Overview tab
    const overviewTab = page.locator('button:has-text("Overview")');
    await overviewTab.click();
    await page.waitForTimeout(1000);

    // Take screenshot showing metrics
    await page.screenshot({ path: 'screenshots/06-metrics-displayed.png', fullPage: true });

    // Check for metric cards
    const artMovementCard = page.locator('text=Art Movement');
    const emotionalToneCard = page.locator('text=Emotional Tone');
    const temperatureCard = page.locator('text=Temperature Profile');

    // Log what we find
    console.log('Art Movement visible:', await artMovementCard.isVisible().catch(() => false));
    console.log('Emotional Tone visible:', await emotionalToneCard.isVisible().catch(() => false));
    console.log('Temperature visible:', await temperatureCard.isVisible().catch(() => false));

    // Get all confidence badges
    const confidenceBadges = page.locator('div:has-text("%")').locator('...');
    const badgeCount = await confidenceBadges.count().catch(() => 0);
    console.log('Confidence badges found:', badgeCount);

    // Check for source indicators (badges showing data source)
    const sourceIndicators = page.locator('[data-source], [aria-label*="source"], [title*="source"]');
    const sourceCount = await sourceIndicators.count().catch(() => 0);
    console.log('Source indicators found:', sourceCount);

    // If no source badges, that's the issue we need to fix
    if (sourceCount === 0) {
      console.warn('⚠️  No source badges found - metrics are not clearly labeled with their data source');
    }
  });

  test('should display metrics with proper async loading behavior', async ({ page }) => {
    // Monitor network requests
    const requests: string[] = [];
    page.on('request', request => {
      if (request.url().includes('/overview/metrics')) {
        requests.push(`[${new Date().toLocaleTimeString()}] Metrics request`);
      }
    });

    // Upload image
    const uploadInput = page.locator('#file-input');
    const testImagePath = path.join(process.cwd(), 'frontend/playwright/test-image.png');

    await uploadInput.setInputFiles(testImagePath);
    await page.waitForTimeout(500); // Wait for preview

    // Click extract button
    const extractBtn = page.locator('.extract-btn');
    await expect(extractBtn).toBeEnabled({ timeout: 5000 });
    await extractBtn.click();

    // Wait for extraction to complete
    await page.waitForSelector('.loading-chip', { state: 'hidden', timeout: 30000 });
    await page.waitForTimeout(1000);

    // Switch to Overview tab
    const overviewTab = page.locator('button:has-text("Overview")');
    await overviewTab.click();

    // Wait for metrics to load
    await page.waitForLoadState('networkidle').catch(() => null);
    await page.waitForTimeout(1000);

    // Take screenshot
    await page.screenshot({ path: 'screenshots/07-final-metrics.png', fullPage: true });

    // Log all metrics requests
    console.log('Metrics API requests:', requests);
  });
});

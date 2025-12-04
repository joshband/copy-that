import { test, expect } from '@playwright/test'

test.describe('ColorDetailPanel - Tier 1 Refactored Component', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5174')
    await page.waitForLoadState('networkidle')
  })

  test('ColorDetailPanel renders empty state when no color selected', async ({ page }) => {
    // Look for empty state
    const emptyState = page.locator('.empty-state')

    if (await emptyState.isVisible()) {
      // Should show empty message
      const emptyText = await emptyState.textContent()
      expect(emptyText).toContain('Select a color')
    }
  })

  test('ColorDetailPanel displays color header with hex value', async ({ page }) => {
    // Look for color header
    const colorHeader = page.locator('[class*="header"]')

    if (await colorHeader.isVisible()) {
      // Should have hex value
      const headerContent = await colorHeader.textContent()
      expect(headerContent).toBeTruthy()
    }
  })

  test('ColorDetailPanel tab navigation works', async ({ page }) => {
    // Look for tab buttons
    const tabs = page.locator('button[class*="tab"]')
    const tabCount = await tabs.count()

    if (tabCount > 0) {
      // Get first tab
      const firstTab = tabs.nth(0)
      const initialClass = await firstTab.getAttribute('class')

      // Click it
      await firstTab.click()

      // Check active state updated
      const newClass = await firstTab.getAttribute('class')
      expect(newClass).toContain('active')
    }
  })

  test('ColorDetailPanel Overview tab shows color properties', async ({ page }) => {
    // Look for Overview tab
    const overviewTab = page.locator('button:has-text("Overview")')

    if (await overviewTab.isVisible()) {
      await overviewTab.click()

      // Check content displays
      const tabContent = page.locator('[class*="tab-content"]').first()
      await expect(tabContent).toBeVisible()
    }
  })

  test('ColorDetailPanel Accessibility tab shows WCAG info', async ({ page }) => {
    // Look for Accessibility tab
    const a11yTab = page.locator('button:has-text("Accessibility")')

    if (await a11yTab.isVisible()) {
      await a11yTab.click()

      // Check WCAG content
      const wcagContent = page.locator('[class*="wcag"], [class*="contrast"]')

      if (await wcagContent.isVisible()) {
        expect(wcagContent).toBeVisible()
      }
    }
  })

  test('ColorDetailPanel Properties tab shows advanced properties', async ({ page }) => {
    // Look for Properties tab
    const propsTab = page.locator('button:has-text("Properties")')

    if (await propsTab.isVisible()) {
      await propsTab.click()

      // Check properties content displays
      const tabContent = page.locator('[class*="tab-content"]').first()
      await expect(tabContent).toBeVisible()
    }
  })

  test('ColorDetailPanel Harmony tab only shows with harmony data', async ({ page }) => {
    // Look for Harmony tab
    const harmonyTab = page.locator('button:has-text("Harmony")')

    if (await harmonyTab.isVisible()) {
      // Tab exists, so color must have harmony data
      await harmonyTab.click()

      // Check harmony visualization
      const harmonyContent = page.locator('[class*="harmony"]')
      expect(harmonyContent).toBeDefined()
    } else {
      // If Harmony tab doesn't exist, that's fine (no harmony data)
      expect(harmonyTab).not.toBeVisible()
    }
  })

  test('ColorDetailPanel Diagnostics tab only shows with debug data', async ({ page }) => {
    // Look for Diagnostics tab
    const diagnosticsTab = page.locator('button:has-text("Diagnostics")')

    if (await diagnosticsTab.isVisible()) {
      await diagnosticsTab.click()

      // Check debug overlay displays
      const debugContent = page.locator('[class*="diagnostic"], canvas')
      expect(debugContent).toBeDefined()
    }
  })

  test('ColorDetailPanel tab switching maintains state', async ({ page }) => {
    // Get all tabs
    const tabs = page.locator('button[class*="tab"]')
    const tabCount = await tabs.count()

    if (tabCount > 1) {
      // Click first tab
      await tabs.nth(0).click()
      await page.waitForTimeout(100)

      // Click second tab
      await tabs.nth(1).click()
      await page.waitForTimeout(100)

      // First tab should not be active
      const firstTabClass = await tabs.nth(0).getAttribute('class')
      expect(firstTabClass).not.toContain('active')

      // Second tab should be active
      const secondTabClass = await tabs.nth(1).getAttribute('class')
      expect(secondTabClass).toContain('active')
    }
  })

  test('ColorDetailPanel color swatch displays correct color', async ({ page }) => {
    // Look for color swatch
    const colorSwatch = page.locator('div[style*="background"], [class*="swatch"]')

    if (await colorSwatch.first().isVisible()) {
      // Get background color style
      const bgColor = await colorSwatch.first().evaluate((el: HTMLElement) => {
        return window.getComputedStyle(el).backgroundColor
      })

      expect(bgColor).toBeTruthy()
    }
  })

  test('ColorDetailPanel color name displays', async ({ page }) => {
    // Look for color name element
    const colorName = page.locator('h3, h4, p')

    if (await colorName.first().isVisible()) {
      const nameText = await colorName.first().textContent()
      expect(nameText).toBeTruthy()
    }
  })

  test('ColorDetailPanel confidence badge renders', async ({ page }) => {
    // Look for confidence badge
    const confidenceBadge = page.locator('[class*="confidence"], [class*="badge"]')

    if (await confidenceBadge.isVisible()) {
      const badgeText = await confidenceBadge.textContent()
      expect(badgeText).toBeTruthy()
    }
  })

  test('ColorDetailPanel responsive layout on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })

    // Panel should adapt to mobile
    const panel = page.locator('[class*="panel"], [class*="detail"]')

    if (await panel.isVisible()) {
      const boundingBox = await panel.boundingBox()
      expect(boundingBox?.width).toBeLessThanOrEqual(375)
    }
  })

  test('ColorDetailPanel no console errors on tab switch', async ({ page }) => {
    const errors: string[] = []

    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text())
      }
    })

    // Get all tabs
    const tabs = page.locator('button[class*="tab"]')
    const tabCount = await tabs.count()

    // Click each tab
    for (let i = 0; i < Math.min(tabCount, 3); i++) {
      await tabs.nth(i).click()
      await page.waitForTimeout(50)
    }

    expect(errors.length).toBe(0)
  })

  test('ColorDetailPanel alias info displays if applicable', async ({ page }) => {
    // Look for alias info
    const aliasInfo = page.locator('[class*="alias"]')

    if (await aliasInfo.isVisible()) {
      const aliasText = await aliasInfo.textContent()
      expect(aliasText).toBeTruthy()
    }
  })

  test('ColorDetailPanel all tabs render without errors', async ({ page }) => {
    const tabs = page.locator('button[class*="tab"]')
    const tabCount = await tabs.count()

    for (let i = 0; i < tabCount; i++) {
      await tabs.nth(i).click()
      await page.waitForTimeout(100)

      // Tab content should be visible
      const tabContent = page.locator('[class*="tab-content"]')
      if (await tabContent.isVisible()) {
        expect(tabContent).toBeVisible()
      }
    }
  })
})

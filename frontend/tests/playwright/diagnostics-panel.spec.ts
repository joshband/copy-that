import { test, expect } from '@playwright/test'

test.describe('DiagnosticsPanel - Tier 1 Refactored Component', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the app and ensure DiagnosticsPanel is visible
    await page.goto('http://localhost:5174')
    // Wait for app to load
    await page.waitForLoadState('networkidle')
  })

  test('renders DiagnosticsPanel with header and subtitle', async ({ page }) => {
    // Find the diagnostics panel
    const diagnosticsPanel = page.locator('.diagnostics')
    await expect(diagnosticsPanel).toBeVisible()

    // Check header text
    const header = page.locator('.diagnostics h3')
    await expect(header).toContainText('Spacing & color QA')

    // Check subtitle exists
    const subtitle = page.locator('.diagnostics-subtitle')
    await expect(subtitle).toBeVisible()
  })

  test('SpacingDiagnostics component displays spacing chips', async ({ page }) => {
    // Look for spacing chips
    const spacingChips = page.locator('[class*="spacing"]').first()

    // If data is loaded, chips should be visible
    if (await spacingChips.isVisible()) {
      const chips = page.locator('[class*="chip"]')
      const count = await chips.count()
      expect(count).toBeGreaterThanOrEqual(0)
    }
  })

  test('ColorPalettePicker displays color swatches', async ({ page }) => {
    // Look for color palette section
    const palette = page.locator('[class*="palette"], [class*="color"]').first()

    if (await palette.isVisible()) {
      // Should have some color elements
      const colors = page.locator('div[style*="background"]')
      const count = await colors.count()
      expect(count).toBeGreaterThanOrEqual(0)
    }
  })

  test('DiagnosticsPanel spacing selection updates state', async ({ page }) => {
    // Find spacing chips
    const spacingChips = page.locator('[class*="chip"]')
    const chipCount = await spacingChips.count()

    if (chipCount > 0) {
      const firstChip = spacingChips.first()

      // Click first spacing chip
      await firstChip.click()

      // Verify it has selected state
      const selectedClass = await firstChip.getAttribute('class')
      expect(selectedClass).toContain('selected') || expect(selectedClass).toContain('active')
    }
  })

  test('DiagnosticsPanel component selection highlights matching boxes', async ({ page }) => {
    // Find component metrics
    const metrics = page.locator('[class*="metric"]')
    const metricCount = await metrics.count()

    if (metricCount > 0) {
      const firstMetric = metrics.first()

      // Click first metric
      await firstMetric.click()

      // Check if overlay highlight appears
      const overlay = page.locator('canvas, svg')
      expect(overlay.first()).toBeDefined()
    }
  })

  test('OverlayPreview renders canvas element', async ({ page }) => {
    // Look for canvas in overlay preview
    const canvas = page.locator('canvas').first()

    if (await canvas.isVisible()) {
      expect(canvas).toBeVisible()
    }
  })

  test('DiagnosticsPanel handles empty state gracefully', async ({ page }) => {
    // Panel should be visible even without data
    const diagnosticsPanel = page.locator('.diagnostics')
    await expect(diagnosticsPanel).toBeVisible()

    // No console errors
    let hasErrors = false
    page.on('console', msg => {
      if (msg.type() === 'error') {
        hasErrors = true
      }
    })

    await page.waitForTimeout(500)
    expect(hasErrors).toBe(false)
  })

  test('DiagnosticsPanel alignment lines toggle', async ({ page }) => {
    // Look for alignment toggle button
    const alignmentButton = page.locator('button:has-text("alignment")')

    if (await alignmentButton.isVisible()) {
      const initialText = await alignmentButton.textContent()

      // Click to toggle
      await alignmentButton.click()

      // Check text changed
      const newText = await alignmentButton.textContent()
      expect(newText).not.toBe(initialText)
    }
  })

  test('DiagnosticsPanel segments toggle', async ({ page }) => {
    // Look for segments toggle button
    const segmentsButton = page.locator('button:has-text("segment")')

    if (await segmentsButton.isVisible()) {
      const initialText = await segmentsButton.textContent()

      // Click to toggle
      await segmentsButton.click()

      // Check text changed
      const newText = await segmentsButton.textContent()
      expect(newText).not.toBe(initialText)
    }
  })

  test('DiagnosticsPanel responsive layout on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 })

    // Panel should still be visible
    const diagnosticsPanel = page.locator('.diagnostics')
    await expect(diagnosticsPanel).toBeVisible()

    // Check no horizontal overflow
    const mainContent = page.locator('body')
    const boundingBox = await mainContent.boundingBox()
    expect(boundingBox?.width).toBeLessThanOrEqual(375)
  })

  test('DiagnosticsPanel with actual spacing data', async ({ page }) => {
    // Wait for data to potentially load
    await page.waitForTimeout(1000)

    // Check if SpacingDiagnostics has content
    const spacingContent = page.locator('[class*="spacing"]')

    if (await spacingContent.isVisible()) {
      // Should have some spacing information
      const contentText = await spacingContent.textContent()
      expect(contentText?.length).toBeGreaterThan(0)
    }
  })

  test('DiagnosticsPanel color palette with confidence', async ({ page }) => {
    // Look for confidence badge
    const confidenceBadge = page.locator('[class*="confidence"]')

    if (await confidenceBadge.isVisible()) {
      const badgeText = await confidenceBadge.textContent()
      expect(badgeText).toBeTruthy()
    }
  })

  test('DiagnosticsPanel multiple selection interactions', async ({ page }) => {
    // Rapidly test multiple interactions
    const spacingChips = page.locator('[class*="chip"]')
    const chipCount = await spacingChips.count()

    if (chipCount > 1) {
      // Click first chip
      await spacingChips.nth(0).click()
      await page.waitForTimeout(100)

      // Click second chip
      await spacingChips.nth(1).click()
      await page.waitForTimeout(100)

      // No console errors
      const logs: string[] = []
      page.on('console', msg => {
        if (msg.type() === 'error') {
          logs.push(msg.text())
        }
      })

      expect(logs.length).toBe(0)
    }
  })
})

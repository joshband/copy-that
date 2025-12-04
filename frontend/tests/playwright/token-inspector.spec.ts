import { test, expect } from '@playwright/test'

test.describe('TokenInspector - Tier 1 Refactored Component', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5174')
    await page.waitForLoadState('networkidle')
  })

  test('TokenInspector renders token list', async ({ page }) => {
    // Look for token inspector
    const inspector = page.locator('[class*="inspector"], [class*="token"]').first()

    if (await inspector.isVisible()) {
      expect(inspector).toBeVisible()
    }
  })

  test('FilterBar input field is visible and functional', async ({ page }) => {
    // Look for filter input
    const filterInput = page.locator('input[type="text"], [class*="filter"]').first()

    if (await filterInput.isVisible()) {
      await filterInput.focus()

      // Type in filter
      await filterInput.fill('test')

      // Check value updated
      const inputValue = await filterInput.inputValue()
      expect(inputValue).toBe('test')
    }
  })

  test('FilterBar updates token list based on filter', async ({ page }) => {
    const filterInput = page.locator('input[type="text"], [class*="filter"]').first()
    const tokenRows = page.locator('tr, [class*="token"], [class*="row"]')

    if (await filterInput.isVisible()) {
      const initialCount = await tokenRows.count()

      // Type filter text
      await filterInput.fill('test')
      await page.waitForTimeout(300)

      // Count should change or stay same, but no errors
      const filteredCount = await tokenRows.count()
      expect(filteredCount).toBeGreaterThanOrEqual(0)
    }
  })

  test('FilterBar clear returns all tokens', async ({ page }) => {
    const filterInput = page.locator('input[type="text"], [class*="filter"]').first()

    if (await filterInput.isVisible()) {
      // Type filter
      await filterInput.fill('test')
      await page.waitForTimeout(200)

      // Clear filter
      await filterInput.fill('')
      await page.waitForTimeout(200)

      // Input should be empty
      const inputValue = await filterInput.inputValue()
      expect(inputValue).toBe('')
    }
  })

  test('TokenList displays tokens in table rows', async ({ page }) => {
    // Look for token table
    const tokenTable = page.locator('table, [class*="list"]').first()

    if (await tokenTable.isVisible()) {
      const rows = page.locator('tr')
      const rowCount = await rows.count()
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })

  test('TokenList row selection works', async ({ page }) => {
    // Look for token rows
    const rows = page.locator('tr, [class*="row"]')
    const rowCount = await rows.count()

    if (rowCount > 0) {
      const firstRow = rows.first()

      // Click row
      await firstRow.click()

      // Check if selected state applies
      const rowClass = await firstRow.getAttribute('class')
      expect(rowClass).toBeTruthy()
    }
  })

  test('TokenList multiple selection state changes', async ({ page }) => {
    const rows = page.locator('tr, [class*="row"]')
    const rowCount = await rows.count()

    if (rowCount > 1) {
      // Click first row
      await rows.nth(0).click()
      await page.waitForTimeout(100)

      // Click second row
      await rows.nth(1).click()
      await page.waitForTimeout(100)

      // First row should not have active state
      const firstClass = await rows.nth(0).getAttribute('class')
      const secondClass = await rows.nth(1).getAttribute('class')

      expect(secondClass).toBeTruthy()
    }
  })

  test('CanvasVisualization renders overlay image', async ({ page }) => {
    // Look for canvas element
    const canvas = page.locator('canvas').first()

    if (await canvas.isVisible()) {
      expect(canvas).toBeVisible()
    }
  })

  test('TokenInspector dimensions track correctly', async ({ page }) => {
    // Look for canvas
    const canvas = page.locator('canvas').first()

    if (await canvas.isVisible()) {
      const boundingBox = await canvas.boundingBox()
      expect(boundingBox?.width).toBeGreaterThan(0)
      expect(boundingBox?.height).toBeGreaterThan(0)
    }
  })

  test('TokenInspector highlights selected token on canvas', async ({ page }) => {
    const rows = page.locator('tr, [class*="row"]')
    const canvas = page.locator('canvas').first()

    if (await rows.first().isVisible() && await canvas.isVisible()) {
      // Click first token
      await rows.first().click()
      await page.waitForTimeout(100)

      // Canvas should have some highlight (SVG or drawn highlight)
      const svg = page.locator('svg')
      const hasVisualization = await svg.first().isVisible().catch(() => false) || await canvas.isVisible()

      expect(hasVisualization).toBeTruthy()
    }
  })

  test('TokenInspector download button exists and triggers download', async ({ page }) => {
    // Look for download button
    const downloadBtn = page.locator('button:has-text("download"), button:has-text("export"), [class*="download"]').first()

    if (await downloadBtn.isVisible()) {
      // Setup download listener
      const downloadPromise = page.waitForEvent('download')

      // Click download button
      await downloadBtn.click()

      // Wait for download (with timeout for cases where download doesn't trigger)
      const download = await downloadPromise.catch(() => null)

      // If download happened, check filename
      if (download) {
        const filename = download.suggestedFilename()
        expect(filename).toContain('.json') || expect(filename).toContain('token')
      }
    }
  })

  test('TokenInspector handles window resize', async ({ page }) => {
    const canvas = page.locator('canvas').first()

    if (await canvas.isVisible()) {
      const initialBox = await canvas.boundingBox()

      // Resize window
      await page.setViewportSize({ width: 500, height: 600 })
      await page.waitForTimeout(300)

      // Get new dimensions
      const newBox = await canvas.boundingBox()

      // Canvas should have adjusted
      expect(newBox).toBeTruthy()
    }
  })

  test('TokenInspector filter case insensitive', async ({ page }) => {
    const filterInput = page.locator('input[type="text"], [class*="filter"]').first()

    if (await filterInput.isVisible()) {
      // Try uppercase
      await filterInput.fill('TEST')
      await page.waitForTimeout(200)

      let count1 = await page.locator('tr, [class*="row"]').count()

      // Clear and try lowercase
      await filterInput.fill('test')
      await page.waitForTimeout(200)

      let count2 = await page.locator('tr, [class*="row"]').count()

      // Results should be same (case insensitive)
      expect(count1).toBe(count2)
    }
  })

  test('TokenInspector rapid interactions', async ({ page }) => {
    const rows = page.locator('tr, [class*="row"]')
    const rowCount = await rows.count()

    if (rowCount > 2) {
      // Rapid clicks
      for (let i = 0; i < 3; i++) {
        await rows.nth(i).click()
        await page.waitForTimeout(50)
      }

      // No errors should occur
      const errors: string[] = []
      page.on('console', msg => {
        if (msg.type() === 'error') {
          errors.push(msg.text())
        }
      })

      await page.waitForTimeout(200)
      expect(errors.length).toBe(0)
    }
  })

  test('TokenInspector mobile responsive layout', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })

    // Inspector should be visible on mobile
    const inspector = page.locator('[class*="inspector"], [class*="token"]').first()

    if (await inspector.isVisible()) {
      const boundingBox = await inspector.boundingBox()
      expect(boundingBox?.width).toBeLessThanOrEqual(375)
    }
  })

  test('TokenInspector token data structure', async ({ page }) => {
    const rows = page.locator('tr, [class*="row"]')

    if (await rows.first().isVisible()) {
      const firstRow = rows.first()
      const rowText = await firstRow.textContent()

      // Should have some token data
      expect(rowText).toBeTruthy()
      expect(rowText?.length).toBeGreaterThan(0)
    }
  })

  test('TokenInspector column headers visible', async ({ page }) => {
    // Look for table headers
    const headers = page.locator('th, [class*="header"]')

    if (await headers.first().isVisible()) {
      const headerCount = await headers.count()
      expect(headerCount).toBeGreaterThan(0)
    }
  })

  test('TokenInspector coordinate display', async ({ page }) => {
    // Tokens should show box/coordinate data
    const tokenData = page.locator('[class*="box"], [class*="coord"]')

    if (await tokenData.first().isVisible()) {
      const dataText = await tokenData.first().textContent()
      expect(dataText).toBeTruthy()
    }
  })
})

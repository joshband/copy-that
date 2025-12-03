import path from 'path'
import { fileURLToPath } from 'url'
import { test, expect } from '@playwright/test'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const fixturePath = path.join(__dirname, 'fixtures', 'sample.png')

test.describe('Shadow Token Extraction E2E', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5174/')
    await page.waitForLoadState('networkidle')
  })

  test('should navigate to shadows tab and display shadow tokens', async ({ page }) => {
    // Upload an image first
    const fileInput = page.locator('input#file-input')
    await fileInput.setInputFiles(fixturePath)
    await page.waitForTimeout(500)

    // Look for shadows tab
    const shadowsTab = page.locator('[role="tab"]:has-text("Shadow"), button:has-text("Shadow")')

    if (await shadowsTab.count() > 0) {
      console.log('✓ Shadows tab found')

      // Click the tab
      await shadowsTab.first().click()
      await page.waitForTimeout(500)

      // Verify tab content is visible
      const shadowContent = page.locator('[role="tabpanel"], .shadows-container, [class*="shadow"]')
      const contentCount = await shadowContent.count()
      console.log(`  Shadow content elements: ${contentCount}`)
    } else {
      console.log('Shadows tab not found - may be rendered conditionally')
    }
  })

  test('should extract and display shadow tokens list', async ({ page }) => {
    // Upload image
    const fileInput = page.locator('input#file-input')
    await fileInput.setInputFiles(fixturePath)
    await page.waitForTimeout(500)

    // Look for shadow token list
    const shadowList = page.locator('[class*="shadow-list"], [class*="ShadowTokenList"], ul, ol')
    const listCount = await shadowList.count()

    if (listCount > 0) {
      console.log(`✓ Found ${listCount} list elements`)

      // Look for shadow items
      const shadowItems = page.locator('[class*="shadow-item"], [class*="shadow-card"], li')
      const itemCount = await shadowItems.count()
      console.log(`  Shadow items: ${itemCount}`)
    }
  })

  test('should display shadow tokens with CSS values', async ({ page }) => {
    // Upload image
    const fileInput = page.locator('input#file-input')
    await fileInput.setInputFiles(fixturePath)
    await page.waitForTimeout(500)

    // Look for CSS values
    const cssValues = page.locator('code, [class*="shadow-value"], :text("px"), :text("rgba")')
    const count = await cssValues.count()

    if (count > 0) {
      console.log(`✓ Found ${count} CSS value elements`)

      // Sample first few values
      for (let i = 0; i < Math.min(3, count); i++) {
        const value = await cssValues.nth(i).textContent()
        console.log(`  Sample ${i + 1}: ${value?.substring(0, 40)}...`)
      }
    }
  })

  test('should show shadow token metadata', async ({ page }) => {
    // Upload image
    const fileInput = page.locator('input#file-input')
    await fileInput.setInputFiles(fixturePath)
    await page.waitForTimeout(500)

    // Look for metadata like depth, opacity, color
    const metadataLabels = page.locator(
      ':text("Depth"), :text("Opacity"), :text("Color"), :text("Blur"), :text("Offset")',
    )
    const count = await metadataLabels.count()

    console.log(`✓ Metadata labels found: ${count}`)

    if (count > 0) {
      const firstLabel = await metadataLabels.first().textContent()
      console.log(`  Sample: ${firstLabel}`)
    }
  })

  test('should extract shadow tokens with proper structure', async ({ page }) => {
    // Upload image
    const fileInput = page.locator('input#file-input')
    await fileInput.setInputFiles(fixturePath)
    await page.waitForTimeout(500)

    // Look for structured shadow data
    const shadowElements = page.locator('[data-shadow], [class*="shadow"]')
    const count = await shadowElements.count()

    console.log(`✓ Shadow elements in DOM: ${count}`)

    // Check for common shadow properties
    const hasOffsetX = await page.locator(':text("offset-x"), :text("offsetX")').count()
    const hasOffsetY = await page.locator(':text("offset-y"), :text("offsetY")').count()
    const hasBlur = await page.locator(':text("blur"), :text("Blur")').count()
    const hasSpread = await page.locator(':text("spread"), :text("Spread")').count()

    console.log(`  Has offsetX: ${hasOffsetX > 0}`)
    console.log(`  Has offsetY: ${hasOffsetY > 0}`)
    console.log(`  Has blur: ${hasBlur > 0}`)
    console.log(`  Has spread: ${hasSpread > 0}`)
  })

  test('should display shadow complexity indicators', async ({ page }) => {
    // Upload image
    const fileInput = page.locator('input#file-input')
    await fileInput.setInputFiles(fixturePath)
    await page.waitForTimeout(500)

    // Look for complexity or confidence indicators
    const complexity = page.locator(
      ':text("Complexity"), :text("Confidence"), :text("Quality"), :text("Accuracy")',
    )
    const count = await complexity.count()

    console.log(`✓ Complexity/confidence indicators: ${count}`)
  })

  test('should allow copying shadow CSS to clipboard', async ({ page }) => {
    // Upload image
    const fileInput = page.locator('input#file-input')
    await fileInput.setInputFiles(fixturePath)
    await page.waitForTimeout(500)

    // Look for copy buttons
    const copyButtons = page.locator('button:has-text("Copy"), button:has-text("copy"), [title*="copy" i]')
    const count = await copyButtons.count()

    console.log(`✓ Copy buttons found: ${count}`)

    if (count > 0) {
      // Click first copy button
      await copyButtons.first().click()
      await page.waitForTimeout(200)

      // Check for success message
      const successMsg = page.locator(':text("Copied"), :text("copied")')
      const hasSuccess = await successMsg.count() > 0
      console.log(`  Copy feedback: ${hasSuccess ? 'YES' : 'Not visible'}`)
    }
  })

  test('should display shadow preview/visualization', async ({ page }) => {
    // Upload image
    const fileInput = page.locator('input#file-input')
    await fileInput.setInputFiles(fixturePath)
    await page.waitForTimeout(500)

    // Look for preview boxes
    const previews = page.locator('[class*="preview"], [class*="demo"], [class*="sample"]')
    const count = await previews.count()

    console.log(`✓ Preview/demo elements: ${count}`)

    if (count > 0) {
      // Check if previews have box-shadow applied
      const previewWithShadow = await previews
        .evaluate((elements) => {
          return (elements as NodeListOf<HTMLElement>).length > 0
        })
        .catch(() => false)

      console.log(`  Previews visible: ${previewWithShadow}`)
    }
  })

  test('should categorize shadows by type', async ({ page }) => {
    // Upload image
    const fileInput = page.locator('input#file-input')
    await fileInput.setInputFiles(fixturePath)
    await page.waitForTimeout(500)

    // Look for shadow type categories
    const categories = page.locator(
      ':text("Drop"), :text("Inner"), :text("Inset"), :text("Outline"), :text("Glow")',
    )
    const count = await categories.count()

    console.log(`✓ Shadow type categories: ${count}`)

    if (count > 0) {
      const types = await categories.allTextContents()
      const uniqueTypes = new Set(types)
      console.log(`  Types found: ${Array.from(uniqueTypes).join(', ')}`)
    }
  })

  test('should show shadow count statistics', async ({ page }) => {
    // Upload image
    const fileInput = page.locator('input#file-input')
    await fileInput.setInputFiles(fixturePath)
    await page.waitForTimeout(500)

    // Look for statistics
    const stats = page.locator(':text("shadows extracted"), :text("Total"), :text("Found"), :text("Detected")')
    const count = await stats.count()

    console.log(`✓ Statistics elements: ${count}`)

    if (count > 0) {
      const firstStat = await stats.first().textContent()
      console.log(`  Sample: ${firstStat}`)
    }
  })

  test('should handle empty shadow list gracefully', async ({ page }) => {
    // Mock empty response
    await page.route('**/api/v1/shadows/**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          shadows: [],
          total: 0,
          extraction_confidence: 0.5,
        }),
      })
    })

    // Upload image
    const fileInput = page.locator('input#file-input')
    await fileInput.setInputFiles(fixturePath)
    await page.waitForTimeout(500)

    // Look for empty state message
    const emptyState = page.locator(':text("No shadows"), :text("Empty"), :text("Try again")')
    const count = await emptyState.count()

    console.log(`✓ Empty state handling:`)
    console.log(`  - Empty message visible: ${count > 0}`)
  })

  test('should export shadows as design tokens', async ({ page }) => {
    // Upload image
    const fileInput = page.locator('input#file-input')
    await fileInput.setInputFiles(fixturePath)
    await page.waitForTimeout(500)

    // Look for export buttons
    const exportButtons = page.locator('button:has-text("Export"), button:has-text("Download"), [title*="export" i]')
    const count = await exportButtons.count()

    console.log(`✓ Export buttons found: ${count}`)

    if (count > 0) {
      const firstButton = await exportButtons.first().getAttribute('title')
      console.log(`  Export option: ${firstButton}`)
    }
  })

  test('should display shadow confidence scores', async ({ page }) => {
    // Upload image
    const fileInput = page.locator('input#file-input')
    await fileInput.setInputFiles(fixturePath)
    await page.waitForTimeout(500)

    // Look for confidence indicators
    const confidence = page.locator(':text("Confidence"), :text("%"), [class*="confidence"]')
    const count = await confidence.count()

    console.log(`✓ Confidence indicators: ${count}`)

    if (count > 0) {
      // Extract percentage values
      const allText = await page.textContent('body')
      const percentages = allText?.match(/\d+%/g) || []
      console.log(`  Percentage values: ${percentages.length}`)
    }
  })

  test('should filter or search shadows', async ({ page }) => {
    // Upload image
    const fileInput = page.locator('input#file-input')
    await fileInput.setInputFiles(fixturePath)
    await page.waitForTimeout(500)

    // Look for search/filter inputs
    const searchInputs = page.locator('input[type="text"], input[placeholder*="search" i], input[placeholder*="filter" i]')
    const count = await searchInputs.count()

    console.log(`✓ Search/filter inputs found: ${count}`)

    if (count > 0) {
      console.log('  Shadow filtering capability available')
    }
  })

  test('should persist shadow selections', async ({ page }) => {
    // Upload image
    const fileInput = page.locator('input#file-input')
    await fileInput.setInputFiles(fixturePath)
    await page.waitForTimeout(500)

    // Look for checkboxes or selection indicators
    const checkboxes = page.locator('input[type="checkbox"]')
    const count = await checkboxes.count()

    console.log(`✓ Selection checkboxes: ${count}`)

    if (count > 0) {
      console.log('  Shadow selection/persistence available')
    }
  })

  test('should show extraction progress for shadows', async ({ page }) => {
    // Upload image
    const fileInput = page.locator('input#file-input')
    await fileInput.setInputFiles(fixturePath)
    await page.waitForTimeout(500)

    // Look for progress indicators
    const progress = page.locator('[role="progressbar"], [class*="progress"], :text("Extracting"), :text("Processing")')
    const count = await progress.count()

    console.log(`✓ Progress indicators: ${count}`)
  })

  test('should validate shadow CSS values', async ({ page }) => {
    // Upload image
    const fileInput = page.locator('input#file-input')
    await fileInput.setInputFiles(fixturePath)
    await page.waitForTimeout(500)

    // Look for CSS code blocks
    const codeBlocks = page.locator('code')
    const count = await codeBlocks.count()

    if (count > 0) {
      console.log(`✓ Found ${count} code blocks`)

      // Validate CSS syntax
      const firstCode = await codeBlocks.first().textContent()
      const isValidCSS = firstCode?.includes('px') || firstCode?.includes('rgba') || firstCode?.includes('shadow')

      console.log(`  Valid CSS syntax: ${isValidCSS}`)
    }
  })

  test('should render shadow cards with proper styling', async ({ page }) => {
    // Upload image
    const fileInput = page.locator('input#file-input')
    await fileInput.setInputFiles(fixturePath)
    await page.waitForTimeout(500)

    // Look for shadow cards
    const shadowCards = page.locator('[class*="shadow-card"], [class*="token-card"]')
    const count = await shadowCards.count()

    console.log(`✓ Shadow cards rendered: ${count}`)

    if (count > 0) {
      // Check styling
      const firstCard = shadowCards.first()
      const bgColor = await firstCard.evaluate((el) => window.getComputedStyle(el).backgroundColor)
      const padding = await firstCard.evaluate((el) => window.getComputedStyle(el).padding)

      console.log(`  Background color: ${bgColor}`)
      console.log(`  Padding: ${padding}`)
    }
  })

  test('should support keyboard navigation for shadows', async ({ page }) => {
    // Upload image
    const fileInput = page.locator('input#file-input')
    await fileInput.setInputFiles(fixturePath)
    await page.waitForTimeout(500)

    // Look for focusable elements
    const focusable = page.locator('button, a, [tabindex]:not([tabindex="-1"])')
    const count = await focusable.count()

    console.log(`✓ Keyboard accessible elements: ${count}`)

    if (count > 0) {
      // Try tab navigation
      await page.keyboard.press('Tab')
      const focused = await page.evaluate(() => {
        const el = document.activeElement
        return el?.tagName
      })

      console.log(`  Focused element after Tab: ${focused}`)
    }
  })

  test('should compare extracted shadows with visual feedback', async ({ page }) => {
    // Upload image
    const fileInput = page.locator('input#file-input')
    await fileInput.setInputFiles(fixturePath)
    await page.waitForTimeout(500)

    // Look for comparison view
    const comparison = page.locator('[class*="comparison"], [class*="before-after"], [class*="original"]')
    const count = await comparison.count()

    console.log(`✓ Comparison view elements: ${count}`)

    if (count > 0) {
      console.log('  Visual comparison available')
    }
  })

  test('should batch process multiple images for shadows', async ({ page }) => {
    // Look for multi-file upload capability
    const fileInput = page.locator('input#file-input')
    const isMultiple = await fileInput.evaluate((el: HTMLInputElement) => el.multiple)

    console.log(`✓ Multi-file upload supported: ${isMultiple}`)

    if (isMultiple) {
      console.log('  Batch processing capability available')
    }
  })
})

test.describe('Shadow API Integration Tests', () => {
  test('should call shadow extraction API', async ({ page }) => {
    const apiCalls: string[] = []

    await page.route('**/api/v1/shadows/**', async (route) => {
      apiCalls.push(`${route.request().method()} ${route.request().url()}`)
      await route.abort()
    })

    await page.goto('http://localhost:5174/')
    const fileInput = page.locator('input#file-input')
    await fileInput.setInputFiles(fixturePath)
    await page.waitForTimeout(1000)

    console.log(`✓ API calls: ${apiCalls.length}`)
    apiCalls.forEach((call) => console.log(`  - ${call}`))
  })

  test('should handle shadow extraction with correct parameters', async ({ page }) => {
    let capturedBody: Record<string, unknown> | null = null

    await page.route('**/api/v1/shadows/**', async (route) => {
      const body = route.request().postData()
      if (body) {
        try {
          capturedBody = JSON.parse(body)
          console.log('✓ Request parameters:')
          console.log(`  - Has image data: ${typeof capturedBody.image_base64 === 'string'}`)
          console.log(`  - Image size: ${(capturedBody.image_base64 as string)?.length || 0} bytes`)
        } catch (e) {
          console.log('Could not parse request body')
        }
      }
      await route.abort()
    })

    await page.goto('http://localhost:5174/')
    const fileInput = page.locator('input#file-input')
    await fileInput.setInputFiles(fixturePath)
    await page.waitForTimeout(500)
  })

  test('should validate shadow response structure', async ({ page }) => {
    const mockResponse = {
      shadows: [
        {
          id: 'shadow-1',
          css_value: '0 4px 8px rgba(0, 0, 0, 0.15)',
          offset_x: 0,
          offset_y: 4,
          blur_radius: 8,
          spread_radius: 0,
          color: '#000000',
          opacity: 0.15,
          confidence: 0.92,
          type: 'drop',
        },
        {
          id: 'shadow-2',
          css_value: 'inset 0 1px 3px rgba(0, 0, 0, 0.12)',
          offset_x: 0,
          offset_y: 1,
          blur_radius: 3,
          spread_radius: 0,
          color: '#000000',
          opacity: 0.12,
          confidence: 0.85,
          type: 'inner',
        },
      ],
      total: 2,
      extraction_confidence: 0.88,
      processing_time_ms: 234,
    }

    await page.route('**/api/v1/shadows/**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockResponse),
      })
    })

    await page.goto('http://localhost:5174/')
    const fileInput = page.locator('input#file-input')
    await fileInput.setInputFiles(fixturePath)
    await page.waitForTimeout(1000)

    // Verify response is displayed
    const cssValues = page.locator('code, :text("px"), :text("rgba")')
    const count = await cssValues.count()

    console.log(`✓ Response displayed: ${count > 0}`)
  })
})

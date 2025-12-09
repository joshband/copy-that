import { test, expect } from '@playwright/test'

test('Check Relations tab rendering', async ({ page }) => {
  // Navigate to the app
  await page.goto('http://localhost:5174')

  // Wait for page to load
  await page.waitForLoadState('networkidle')

  // Take initial screenshot
  await page.screenshot({ path: 'screenshots/01-homepage.png', fullPage: true })
  console.log('📸 Screenshot 1: Homepage')

  // Click Relations tab
  await page.click('text=Relations')
  await page.waitForTimeout(1000)

  // Take screenshot of Relations tab
  await page.screenshot({ path: 'screenshots/02-relations-tab.png', fullPage: true })
  console.log('📸 Screenshot 2: Relations tab')

  // Check for debug panel
  const debugPanel = await page.locator('text=Debug:').count()
  console.log('🔍 Debug panel found:', debugPanel > 0)

  // Check for load button
  const loadButton = await page.locator('button:has-text("Load Token Graph")').count()
  console.log('🔍 Load button found:', loadButton > 0)

  // Check for Token Graph Demo
  const graphDemo = await page.locator('text=Token Graph Demo').count()
  console.log('🔍 Token Graph Demo found:', graphDemo > 0)

  // Get debug panel text if it exists
  if (debugPanel > 0) {
    const debugText = await page.locator('div:has-text("Debug:")').first().textContent()
    console.log('📊 Debug info:', debugText)
  }

  // If load button exists, click it
  if (loadButton > 0) {
    console.log('🔘 Clicking load button...')
    await page.click('button:has-text("Load Token Graph")')
    await page.waitForTimeout(2000)

    // Take screenshot after loading
    await page.screenshot({ path: 'screenshots/03-after-load.png', fullPage: true })
    console.log('📸 Screenshot 3: After clicking load')

    // Check if tokens appeared
    const tokenCount = await page.locator('[style*="color"]').count()
    console.log('🎨 Token elements found:', tokenCount)
  }

  // Get all text content for debugging
  const relationsContent = await page.locator('section.panel:has-text("Relations")').textContent()
  console.log('📄 Relations tab content:', relationsContent?.substring(0, 500))
})

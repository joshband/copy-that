import { test, expect } from '@playwright/test'

test('Frontend loads and displays basic UI', async ({ page }) => {
  // Navigate to the frontend
  await page.goto('http://localhost:5175/', { waitUntil: 'networkidle', timeout: 30000 })

  // Check if page title loaded
  await expect(page).toHaveTitle(/Copy That/, { timeout: 10000 })

  // Check if root div exists
  const root = page.locator('#root')
  await expect(root).toBeVisible({ timeout: 10000 })

  // Take a screenshot
  await page.screenshot({ path: 'screenshots/frontend-loaded.png', fullPage: true })

  console.log('✅ Frontend loaded successfully!')
  console.log('✅ Screenshot saved to screenshots/frontend-loaded.png')
})

test('Check for adapter pattern in Token Graph', async ({ page }) => {
  await page.goto('http://localhost:5175/', { timeout: 30000 })

  // Wait for app to initialize
  await page.waitForSelector('#root', { timeout: 10000 })

  // Check if we can find any token-related elements
  const hasTokenElements = await page.locator('text=/token|Token/i').count()
  console.log(`Found ${hasTokenElements} token-related elements`)

  // Take screenshot of current state
  await page.screenshot({ path: 'screenshots/app-state.png', fullPage: true })

  expect(hasTokenElements).toBeGreaterThan(0)
})

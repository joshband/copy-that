import path from 'path'
import { fileURLToPath } from 'url'
import { expect, test } from '@playwright/test'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const fixturePath = path.join(__dirname, 'fixtures', 'sample.png')

test('layout is dense on load and empty CTAs point to upload', async ({ page }) => {
  await page.goto('/')

  await expect(page.getByRole('heading', { name: 'Upload an image' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Color tokens' })).toBeVisible()

  // Empty CTAs exist and point back to upload
  await expect(page.getByRole('button', { name: /Go to upload/i }).first()).toBeVisible()
})

test('detail panel stays scrollable after extraction stream', async ({ page }) => {
  // Mock streaming response with a single color
  const colorPayload = {
    phase: 2,
    status: 'extraction_complete',
    colors: [
      {
        hex: '#3A5F73',
        rgb: 'rgb(58, 95, 115)',
        name: 'Test Blue',
        confidence: 0.95,
        background_role: 'primary',
        contrast_category: 'high',
        count: 2,
      },
    ],
  }
  const streamBody = [
    `data: ${JSON.stringify({ phase: 1, status: 'colors_streaming', progress: 1 })}\n\n`,
    `data: ${JSON.stringify(colorPayload)}\n\n`,
  ].join('')

  await page.route('**/api/v1/colors/extract-streaming', (route) =>
    route.fulfill({
      status: 200,
      headers: { 'Content-Type': 'text/event-stream' },
      body: streamBody,
    })
  )

  await page.goto('/')
  await page.setInputFiles('input#file-input', fixturePath)
  await page.getByRole('button', { name: /Extract Colors/i }).click()

  // Wait for palette and select the first swatch
  const swatch = page.getByTitle('Test Blue - #3A5F73')
  await expect(swatch).toBeVisible({ timeout: 15000 })
  await swatch.click()

  // Detail tab content should allow scrolling (overflow enabled)
  const tabContent = page.locator('.tab-content').first()
  await expect(tabContent).toBeVisible()
  const overflowY = await tabContent.evaluate((el) => {
    const style = window.getComputedStyle(el)
    return style.overflowY
  })
  expect(['auto', 'scroll']).toContain(overflowY)
})

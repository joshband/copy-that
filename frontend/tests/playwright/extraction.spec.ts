import path from 'path'
import { fileURLToPath } from 'url'
import { test, expect } from '@playwright/test'

const buildEvent = (event: string, data: Record<string, unknown>) =>
  `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`

test('extract tokens in browser and show badges/spacing', async ({ page }) => {
  const colorPayload = {
    phase: 2,
    status: 'extraction_complete',
    colors: [
      {
        hex: '#D82F8B',
        rgb: 'rgb(216, 47, 139)',
        name: 'Playwright Coral',
        confidence: 0.94,
        background_role: 'primary',
        contrast_category: 'high',
        count: 3,
        saturation_level: 'vibrant',
      },
    ],
  }

  const streamBody = [
    `data: ${JSON.stringify({ phase: 1, status: 'colors_streaming', progress: 1 })}\n\n`,
    `data: ${JSON.stringify(colorPayload)}\n\n`,
  ].join('')

  await page.route('**/api/v1/colors/extract-streaming', (route) => {
    route.fulfill({
      status: 200,
      headers: { 'Content-Type': 'text/event-stream' },
      body: streamBody,
    })
  })

  const __dirname = path.dirname(fileURLToPath(import.meta.url))
  const fixturePath = path.join(__dirname, 'fixtures', 'sample.png')
  await page.goto('/')
  await page.setInputFiles('input#file-input', fixturePath)
  await page.click('button:has-text("Extract Colors")')
  const firstPaletteSwatch = page.getByTitle('Playwright Coral - #D82F8B')
  await expect(firstPaletteSwatch).toBeVisible({ timeout: 15000 })
  await firstPaletteSwatch.click()
  await expect(page.getByText('Playwright Coral')).toBeVisible({ timeout: 15000 })
  await expect(page.locator('.background-badge.primary')).toBeVisible()
  await expect(page.locator('.contrast-badge')).toHaveText(/Contrast: high/)
})

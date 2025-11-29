import path from 'path'
import { fileURLToPath } from 'url'
import { expect, test } from '@playwright/test'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const fixturePath = path.join(__dirname, 'fixtures', 'sample.png')

const buildStream = (colors: any[]) =>
  [
    `data: ${JSON.stringify({ phase: 1, status: 'colors_streaming', progress: 1 })}\n\n`,
    `data: ${JSON.stringify({ phase: 2, status: 'extraction_complete', colors })}\n\n`,
  ].join('')

test('palette and detail stay within panel bounds after extraction', async ({ page }) => {
  const colors = [
    { hex: '#3A5F73', rgb: 'rgb(58,95,115)', name: 'Test Blue', confidence: 0.95 },
    { hex: '#D94E1F', rgb: 'rgb(217,78,31)', name: 'Test Red', confidence: 0.9 },
    { hex: '#A6C0C9', rgb: 'rgb(166,192,201)', name: 'Test Gray', confidence: 0.85 },
  ]
  await page.route('**/api/v1/colors/extract-streaming', (route) =>
    route.fulfill({
      status: 200,
      headers: { 'Content-Type': 'text/event-stream' },
      body: buildStream(colors),
    })
  )

  await page.goto('/')
  await page.setInputFiles('input#file-input', fixturePath)
  await page.getByRole('button', { name: /Extract Colors/i }).click()

  // Wait for palette to render
  const swatch = page.getByTitle('Test Blue - #3A5F73')
  await expect(swatch).toBeVisible({ timeout: 15000 })
  await swatch.click()

  const container = page.locator('.color-tokens.layout-new')
  const palette = page.locator('.palette-container')
  const detail = page.locator('.detail-container')

  const [cBox, pBox, dBox] = await Promise.all([
    container.boundingBox(),
    palette.boundingBox(),
    detail.boundingBox(),
  ])

  expect(cBox).toBeTruthy()
  expect(pBox).toBeTruthy()
  expect(dBox).toBeTruthy()
  if (!cBox || !pBox || !dBox) return

  // Heights should not overflow the container
  expect(pBox.height).toBeLessThanOrEqual(cBox.height + 2)
  expect(dBox.height).toBeLessThanOrEqual(cBox.height + 2)

  // Palette and detail should sit side by side within the container width
  expect(pBox.x).toBeGreaterThanOrEqual(cBox.x - 1)
  expect(dBox.x + dBox.width).toBeLessThanOrEqual(cBox.x + cBox.width + 1)
})

test('shadow/spacing/typography empty states show CTA buttons', async ({ page }) => {
  await page.goto('/')
  const panels = [
    page.getByRole('heading', { name: 'Shadow tokens' }).locator('..'),
    page.getByRole('heading', { name: 'Spacing tokens' }).locator('..'),
    page.getByRole('heading', { name: 'Typography tokens' }).locator('..'),
  ]
  for (const panel of panels) {
    await expect(panel.getByRole('button', { name: /Go to upload/i })).toBeVisible()
  }
})

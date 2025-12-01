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

test('colors tab shows empty state without extraction', async ({ page }) => {
  await page.goto('/')
  const tabRow = page.locator('.tab-row')
  await tabRow.getByRole('button', { name: 'Colors', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Color tokens' })).toBeVisible()
  await expect(page.getByRole('button', { name: /upload/i })).toBeVisible()
})

test('shadow/spacing/typography empty states show CTA buttons', async ({ page }) => {
  await page.goto('/')
  await page.getByRole('button', { name: 'Shadows' }).click()
  await expect(page.getByRole('button', { name: /Go to upload/i }).first()).toBeVisible()

  await page.getByRole('button', { name: 'Spacing' }).click()
  await expect(page.getByRole('button', { name: /Go to upload/i }).first()).toBeVisible()

  await page.getByRole('button', { name: 'Typography' }).click()
  await expect(page.getByRole('button', { name: /Go to upload/i }).first()).toBeVisible()
})

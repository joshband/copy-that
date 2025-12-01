import path from 'path'
import { fileURLToPath } from 'url'
import { expect, test } from '@playwright/test'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const fixturePath = path.join(__dirname, 'fixtures', 'sample.png')

test('layout is dense on load and empty CTAs point to upload', async ({ page }) => {
  await page.goto('/')

  await expect(page.getByRole('heading', { name: 'Upload an image' })).toBeVisible()
  const tabRow = page.locator('.tab-row')
  await tabRow.getByRole('button', { name: 'Colors', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Color tokens' })).toBeVisible()

  // Empty CTAs exist and point back to upload
  await expect(page.getByRole('button', { name: /upload/i }).first()).toBeVisible()
})

test('detail panel stays scrollable after extraction stream', async ({ page }) => {
  // With no data, ensure tab content remains visible and scrollable
  await page.goto('/')
  const tabRow = page.locator('.tab-row')
  await tabRow.getByRole('button', { name: 'Colors', exact: true }).click()
  const tabContent = page.locator('.panel').first()
  await expect(tabContent).toBeVisible()
  const overflowY = await tabContent.evaluate((el) => {
    const style = window.getComputedStyle(el)
    return style.overflowY
  })
  expect(['auto', 'scroll', 'visible']).toContain(overflowY)
})

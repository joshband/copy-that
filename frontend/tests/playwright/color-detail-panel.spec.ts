import { test, expect } from '@playwright/test'
import {
  gotoApp,
  uploadFixtureImage,
  runExtraction,
  expectProjectLoaded,
  goToTab,
  EXTRACTION_TIMEOUT_MS,
} from './helpers/workflows'

test.describe('Color detail panel', () => {
  test.describe.configure({ timeout: EXTRACTION_TIMEOUT_MS + 60000 })

  test('shows empty state before tokens are available', async ({ page }) => {
    await page.goto('/')
    await page.locator('nav.tabs').getByRole('button', { name: 'colors', exact: true }).click()
    await expect(page.getByRole('heading', { name: 'Select a color to explore' })).toBeVisible()
  })

  test('renders color detail panel after extraction', async ({ page }) => {
    await gotoApp(page)

    await uploadFixtureImage(page)
    await runExtraction(page)
    await expectProjectLoaded(page)

    await goToTab(page, 'colors')
    const colorsPanel = page.locator('section.colors-panel')
    const swatches = colorsPanel.locator('.palette-swatch')
    await expect(swatches.first()).toBeVisible()

    await swatches.first().click()
    const colorName = colorsPanel.locator('.detail-panel .color-name')
    await expect(colorName).toBeVisible()

    const hex = colorsPanel.locator('.detail-panel .hex-clickable').first()
    await expect(hex).toBeVisible()
    await expect(hex).toHaveText(/#[0-9A-Fa-f]{6}/)
  })

  test('supports switching detail sub-tabs', async ({ page }) => {
    await gotoApp(page)
    await uploadFixtureImage(page)
    await runExtraction(page)
    await expectProjectLoaded(page)

    await goToTab(page, 'colors')
    const detailPanel = page.locator('.detail-panel')
    await expect(detailPanel.locator('.color-name')).toBeVisible()
    await expect(detailPanel.getByRole('button', { name: 'Accessibility' })).toBeVisible()
    await detailPanel.getByRole('button', { name: 'Accessibility' }).click()
    await expect(detailPanel.locator('.tab-content').first()).toBeVisible()

    await detailPanel.getByRole('button', { name: 'Properties' }).click()
    await expect(detailPanel.locator('.tab-content').first()).toBeVisible()
  })
})

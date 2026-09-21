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
    await page.locator('nav.tabs').getByRole('button', { name: 'Colors', exact: true }).click()
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

  test('shows color sections as separate cards', async ({ page }) => {
    await gotoApp(page)
    await uploadFixtureImage(page)
    await runExtraction(page)
    await expectProjectLoaded(page)

    await goToTab(page, 'colors')
    const stack = page.locator('.color-detail-stack')
    await expect(stack.locator('.color-name')).toBeVisible()
    await expect(stack.getByRole('heading', { name: 'Overview', exact: true })).toBeVisible()
    await expect(stack.getByRole('heading', { name: 'Accessibility', exact: true })).toBeVisible()
    await expect(stack.getByText('More analysis')).toBeVisible()
    await stack.locator('details.color-detail-more summary').click()
    await expect(stack.getByRole('heading', { name: 'Properties', exact: true })).toBeVisible()
    await expect(stack.locator('.tab-content').first()).toBeVisible()
  })
})

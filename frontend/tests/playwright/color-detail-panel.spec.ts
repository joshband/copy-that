import { test, expect } from '@playwright/test'
import { gotoAppWithMocks, uploadFixtureImage, runExtraction, expectProjectLoaded, goToTab } from './helpers/workflows'

test.describe('Color detail panel', () => {
  test('shows empty state before tokens are available', async ({ page }) => {
    await page.goto('/')
    await page.locator('nav.tabs').getByRole('button', { name: 'colors', exact: true }).click()
    await expect(page.getByRole('heading', { name: 'Select a color to explore' })).toBeVisible()
  })

  test('renders W3C tokens (including OKLCH) without crashing', async ({ page }) => {
    await gotoAppWithMocks(page, { projectId: 1 })

    await uploadFixtureImage(page)
    await runExtraction(page)
    await expectProjectLoaded(page, 1)

    await goToTab(page, 'colors')
    await expect(page.getByRole('heading', { name: 'Text Primary' })).toBeVisible()

    const swatches = page.locator('.palette-swatch')
    await expect(swatches).toHaveCount(3)

    await swatches.nth(1).click()
    await expect(page.getByRole('heading', { name: 'Warm Accent' })).toBeVisible()

    const hex = page.locator('.hex-clickable').first()
    await expect(hex).toBeVisible()
    await expect(hex).not.toHaveText('#CCCCCC')
    await expect(hex).toHaveText(/#[0-9A-F]{6}/)
  })

  test('supports switching detail sub-tabs', async ({ page }) => {
    await gotoAppWithMocks(page, { projectId: 1 })
    await uploadFixtureImage(page)
    await runExtraction(page)
    await expectProjectLoaded(page, 1)

    await goToTab(page, 'colors')
    await expect(page.getByRole('heading', { name: 'Text Primary' })).toBeVisible()

    const detailPanel = page.locator('.detail-panel')
    await expect(detailPanel.getByRole('button', { name: 'Accessibility' })).toBeVisible()
    await detailPanel.getByRole('button', { name: 'Accessibility' }).click()
    await expect(detailPanel.locator('.tab-content').first()).toBeVisible()

    await detailPanel.getByRole('button', { name: 'Properties' }).click()
    await expect(detailPanel.locator('.tab-content').first()).toBeVisible()
  })
})

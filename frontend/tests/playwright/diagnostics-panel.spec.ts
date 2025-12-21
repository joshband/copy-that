import { test, expect } from '@playwright/test'
import { gotoAppWithMocks, uploadFixtureImage, runExtraction, expectProjectLoaded, goToTab } from './helpers/workflows'

test.describe('Diagnostics panel', () => {
  test('renders in overview tab and shows palette swatches', async ({ page }) => {
    await gotoAppWithMocks(page, { projectId: 1 })

    await uploadFixtureImage(page)
    await runExtraction(page)
    await expectProjectLoaded(page, 1)

    await goToTab(page, 'overview')
    await expect(page.getByRole('heading', { name: 'Spacing & color QA' })).toBeVisible()

    await expect(page.getByRole('heading', { name: 'Color palette' })).toBeVisible()
    await expect.poll(async () => page.locator('.diagnostics .palette-grid .swatch').count()).toBeGreaterThan(0)
  })
})

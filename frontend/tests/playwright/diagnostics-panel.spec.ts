import { test, expect } from '@playwright/test'
import {
  gotoApp,
  uploadFixtureImage,
  runExtraction,
  expectProjectLoaded,
  goToTab,
  EXTRACTION_TIMEOUT_MS,
} from './helpers/workflows'

test.describe('Diagnostics panel', () => {
  test.describe.configure({ timeout: EXTRACTION_TIMEOUT_MS + 60000 })

  test('renders in overview when Debug is on', async ({ page }) => {
    await gotoApp(page)

    await uploadFixtureImage(page)
    await runExtraction(page)
    await expectProjectLoaded(page)

    await page.locator('.switch input[type="checkbox"]').check()
    await goToTab(page, 'overview')
    await expect(page.getByRole('heading', { name: 'Spacing & color QA' })).toBeVisible()

    await expect(page.getByRole('heading', { name: 'Color palette' })).toBeVisible()
    await expect.poll(async () => page.locator('.diagnostics .palette-grid .swatch').count()).toBeGreaterThan(0)
  })
})

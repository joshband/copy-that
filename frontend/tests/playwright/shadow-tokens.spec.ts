import { test, expect } from '@playwright/test'
import {
  gotoApp,
  uploadFixtureImage,
  runExtraction,
  expectProjectLoaded,
  goToTab,
  EXTRACTION_TIMEOUT_MS,
} from './helpers/workflows'

test.describe('Shadows tab', () => {
  test.describe.configure({ timeout: EXTRACTION_TIMEOUT_MS + 60000 })

  test('renders shadow tokens or empty state', async ({ page }) => {
    await gotoApp(page)
    await uploadFixtureImage(page)
    await runExtraction(page)
    await expectProjectLoaded(page)

    await goToTab(page, 'shadows')
    const shadowCards = page.locator('.shadow-card')
    if ((await shadowCards.count()) > 0) {
      await expect(shadowCards.first().locator('.shadow-title')).toBeVisible()
    } else {
      await expect(page.getByText('No shadows extracted yet.')).toBeVisible()
    }
  })
})

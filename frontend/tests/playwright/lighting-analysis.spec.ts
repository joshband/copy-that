import { test, expect } from '@playwright/test'
import {
  gotoApp,
  uploadFixtureImage,
  runExtraction,
  expectProjectLoaded,
  goToTab,
  EXTRACTION_TIMEOUT_MS,
} from './helpers/workflows'

test.describe('Lighting tab', () => {
  test.describe.configure({ timeout: EXTRACTION_TIMEOUT_MS + 60000 })

  test('renders empty state when no analysis is available', async ({ page }) => {
    await gotoApp(page)

    await goToTab(page, 'lighting')
    await expect(page.getByText('No lighting analysis available yet.')).toBeVisible()
    await expect(page.getByText('Trigger analysis from the overview tab to populate this view.')).toBeVisible()
  })

  test('renders analysis after extraction', async ({ page }) => {
    await gotoApp(page)
    await uploadFixtureImage(page)
    await runExtraction(page)
    await expectProjectLoaded(page)

    await goToTab(page, 'lighting')
    await expect(page.getByRole('heading', { name: 'Shadow Analysis' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Lighting Direction' })).toBeVisible()
  })
})

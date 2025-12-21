import { test, expect } from '@playwright/test'
import { gotoAppWithMocks, uploadFixtureImage, runExtraction, expectProjectLoaded, goToTab } from './helpers/workflows'

test.describe('Lighting tab', () => {
  test('renders empty state when no analysis is available', async ({ page }) => {
    await gotoAppWithMocks(page, { projectId: 1 })
    await uploadFixtureImage(page)
    await runExtraction(page)
    await expectProjectLoaded(page, 1)

    await goToTab(page, 'lighting')
    await expect(page.getByText('No lighting analysis available yet.')).toBeVisible()
    await expect(page.getByText('Trigger analysis from the overview tab to populate this view.')).toBeVisible()
  })
})

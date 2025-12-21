import { test, expect } from '@playwright/test'
import { gotoAppWithMocks, uploadFixtureImage, runExtraction, expectProjectLoaded, goToTab } from './helpers/workflows'

test.describe('Shadows tab', () => {
  test('renders W3C shadow tokens and linking UI', async ({ page }) => {
    await gotoAppWithMocks(page, { projectId: 1 })
    await uploadFixtureImage(page)
    await runExtraction(page)
    await expectProjectLoaded(page, 1)

    await goToTab(page, 'shadows')
    await expect(page.locator('.shadow-card')).toHaveCount(1)
    await expect(page.getByText('shadow.card')).toBeVisible()
  })
})

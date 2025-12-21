import { test, expect } from '@playwright/test'
import { gotoAppWithMocks, uploadFixtureImage, runExtraction, expectProjectLoaded, goToTab } from './helpers/workflows'

test.describe('Overview snapshot', () => {
  test('shows token counts after extraction refresh', async ({ page }) => {
    await gotoAppWithMocks(page, { projectId: 1 })
    await uploadFixtureImage(page)
    await runExtraction(page)
    await expectProjectLoaded(page, 1)

    await goToTab(page, 'overview')
    await expect(page.getByRole('heading', { name: 'Snapshot' })).toBeVisible()
    await expect.poll(async () => page.getByText(/colors \(/).textContent()).toContain('3 colors')
  })
})

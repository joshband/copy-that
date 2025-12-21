import { test, expect } from '@playwright/test'
import {
  gotoApp,
  uploadFixtureImage,
  runExtraction,
  expectProjectLoaded,
  goToTab,
  EXTRACTION_TIMEOUT_MS,
} from './helpers/workflows'

test.describe('Overview snapshot', () => {
  test.describe.configure({ timeout: EXTRACTION_TIMEOUT_MS + 60000 })

  test('shows token counts after extraction refresh', async ({ page }) => {
    await gotoApp(page)
    await uploadFixtureImage(page)
    await runExtraction(page)
    await expectProjectLoaded(page)

    await goToTab(page, 'overview')
    await expect(page.getByRole('heading', { name: 'Snapshot' })).toBeVisible()
    const snapshotLine = page.getByText(/colors \\(.*aliases\\)/i)
    await expect(snapshotLine).toBeVisible()
    await expect
      .poll(async () => {
        const text = (await snapshotLine.textContent()) ?? ''
        const match = text.match(/(\d+)\s+colors/i)
        return match ? Number(match[1]) : 0
      })
      .toBeGreaterThan(0)
  })
})

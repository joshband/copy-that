import { test, expect } from '@playwright/test'
import {
  EXTRACTION_TIMEOUT_MS,
  expectProjectLoaded,
  goToTab,
  gotoAppWithMocks,
  runExtraction,
  uploadFixtureImage,
} from './helpers/workflows'

test.setTimeout(EXTRACTION_TIMEOUT_MS + 60_000)

test.describe('P1 MVP smoke', () => {
  test('upload → four token tabs → W3C + CSS download', async ({ page }) => {
    test.skip(process.env.PLAYWRIGHT_USE_MOCKS !== 'true', 'Requires PLAYWRIGHT_USE_MOCKS=true')

    await gotoAppWithMocks(page)
    await uploadFixtureImage(page)
    await runExtraction(page, {
      tokenCounts: { colors: 1, spacing: 1, typography: 1, shadows: 1 },
    })
    await expectProjectLoaded(page)

    for (const tab of ['colors', 'spacing', 'typography', 'shadows'] as const) {
      await goToTab(page, tab)
      await expect(page.locator(`section.${tab}-panel`)).toBeVisible()
    }

    await goToTab(page, 'export')
    const panel = page.locator('section.export-panel')
    await expect(panel.getByRole('heading', { name: 'Token snapshot' })).toBeVisible()

    const w3cPromise = page.waitForEvent('download')
    await panel.getByRole('button', { name: 'W3C JSON' }).click()
    const w3cDownload = await w3cPromise
    expect(w3cDownload.suggestedFilename()).toMatch(/\.tokens\.json$/)

    const cssPromise = page.waitForEvent('download')
    await panel.getByRole('button', { name: 'CSS' }).click()
    const cssDownload = await cssPromise
    expect(cssDownload.suggestedFilename()).toMatch(/\.tokens\.css$/)
  })
})

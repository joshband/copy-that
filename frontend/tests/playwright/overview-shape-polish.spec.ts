/**
 * Overview + Shape polish — mocked contracts aligned with visual-first slim UI.
 */

import { test, expect } from '@playwright/test'
import {
  gotoAppWithMocks,
  uploadFixtureImage,
  runExtraction,
  expectProjectLoaded,
  goToTab,
  EXTRACTION_TIMEOUT_MS,
} from './helpers/workflows'

test.describe('Overview & Shape polish', () => {
  test.describe.configure({ timeout: EXTRACTION_TIMEOUT_MS + 60000 })

  test.beforeEach(() => {
    test.skip(process.env.PLAYWRIGHT_USE_MOCKS !== 'true', 'Requires PLAYWRIGHT_USE_MOCKS=true')
  })

  test('overview shows snapshot and swatches after extraction (no diagnostics by default)', async ({
    page,
  }) => {
    await gotoAppWithMocks(page)
    await uploadFixtureImage(page)
    await runExtraction(page)
    await expectProjectLoaded(page)

    await goToTab(page, 'overview')
    await expect(page.getByRole('heading', { name: 'Snapshot' })).toBeVisible()
    await expect(page.locator('.overview-stat__label', { hasText: 'Colors' })).toBeVisible()
    await expect(page.getByTestId('overview-swatches')).toBeVisible()
    await expect(page.getByText('Spacing & color QA')).toHaveCount(0)
  })

  test('shape tab shows layout panel without roadmap labels', async ({ page }) => {
    await gotoAppWithMocks(page)
    await uploadFixtureImage(page)
    await runExtraction(page)
    await expectProjectLoaded(page)

    await goToTab(page, 'shape')
    const shapePanel = page.locator('section.shape-panel')
    const heading = shapePanel.getByRole('heading', { name: /Grid, border, and radius|No layout tokens yet/i })
    await expect(heading.first()).toBeVisible()
    const viewport = shapePanel.getByTestId('layout-viewport')
    const empty = shapePanel.getByText(/No layout tokens yet/i)
    await expect(viewport.or(empty).first()).toBeVisible()
    await expect(page.getByText('Motion (P2b)')).toHaveCount(0)
    await expect(page.getByText('DTCG types (derived)')).toHaveCount(0)
  })
})

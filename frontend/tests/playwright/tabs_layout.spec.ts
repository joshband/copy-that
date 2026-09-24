import { expect, test } from '@playwright/test'
import {
  EXTRACTION_TIMEOUT_MS,
  expectProjectLoaded,
  goToTab,
  gotoAppWithMocks,
  runExtraction,
  uploadFixtureImage,
} from './helpers/workflows'

/** MVP tabs from featureFlags.visibleAppTabs() with lighting/relations/raw parked. */
const MVP_TABS = [
  'Overview',
  'Mood',
  'Colors',
  'Spacing',
  'Typography',
  'Shadows',
  'Shape',
  'Export',
] as const

const PARKED_TABS = ['Lighting', 'Relations', 'Raw'] as const

test.describe('Tabbed token layout', () => {
  test.describe.configure({ timeout: EXTRACTION_TIMEOUT_MS + 60000 })

  test('renders MVP tabs only and switches sections', async ({ page }) => {
    test.skip(process.env.PLAYWRIGHT_USE_MOCKS !== 'true', 'Requires PLAYWRIGHT_USE_MOCKS=true')

    await gotoAppWithMocks(page)
    await uploadFixtureImage(page)
    await runExtraction(page)
    await expectProjectLoaded(page)

    const nav = page.locator('nav.tabs')
    for (const name of MVP_TABS) {
      await expect(nav.getByRole('button', { name, exact: true })).toBeVisible()
    }
    for (const name of PARKED_TABS) {
      await expect(nav.getByRole('button', { name, exact: true })).toHaveCount(0)
    }

    await nav.getByRole('button', { name: 'Overview', exact: true }).click()
    await expect(page.locator('section.overview-panel')).toBeVisible()

    await nav.getByRole('button', { name: 'Colors', exact: true }).click()
    await expect(page.locator('section.colors-panel')).toBeVisible()

    await nav.getByRole('button', { name: 'Spacing', exact: true }).click()
    await expect(page.locator('section.spacing-panel')).toBeVisible()

    await nav.getByRole('button', { name: 'Typography', exact: true }).click()
    await expect(page.locator('section.typography-panel')).toBeVisible()

    await nav.getByRole('button', { name: 'Shadows', exact: true }).click()
    await expect(page.locator('section.shadows-panel')).toBeVisible()

    await nav.getByRole('button', { name: 'Shape', exact: true }).click()
    await expect(page.locator('section.shape-panel')).toBeVisible()

    await nav.getByRole('button', { name: 'Export', exact: true }).click()
    await expect(page.locator('section.export-panel')).toBeVisible()
  })
})

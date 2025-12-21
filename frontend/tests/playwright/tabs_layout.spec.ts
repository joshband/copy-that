import { expect, test } from '@playwright/test'
import {
  gotoApp,
  uploadFixtureImage,
  runExtraction,
  expectProjectLoaded,
  EXTRACTION_TIMEOUT_MS,
} from './helpers/workflows'

test.describe('Tabbed token layout', () => {
  test.describe.configure({ timeout: EXTRACTION_TIMEOUT_MS + 60000 })

  test('renders tabs and switches sections', async ({ page }) => {
    await gotoApp(page)
    await uploadFixtureImage(page)
    await runExtraction(page)
    await expectProjectLoaded(page)

    const nav = page.locator('nav.tabs')
    const tabs = ['overview', 'colors', 'spacing', 'typography', 'shadows', 'lighting', 'export', 'relations', 'raw']
    for (const name of tabs) {
      await expect(nav.getByRole('button', { name, exact: true })).toBeVisible()
    }

    await nav.getByRole('button', { name: 'overview', exact: true }).click()
    await expect(page.locator('section.overview-panel')).toBeVisible()

    await nav.getByRole('button', { name: 'colors', exact: true }).click()
    await expect(page.locator('section.colors-panel')).toBeVisible()

    await nav.getByRole('button', { name: 'spacing', exact: true }).click()
    await expect(page.locator('section.spacing-panel')).toBeVisible()

    await nav.getByRole('button', { name: 'typography', exact: true }).click()
    await expect(page.locator('section.typography-panel')).toBeVisible()

    await nav.getByRole('button', { name: 'shadows', exact: true }).click()
    await expect(page.locator('section.shadows-panel')).toBeVisible()

    await nav.getByRole('button', { name: 'lighting', exact: true }).click()
    await expect(page.locator('section.lighting-panel')).toBeVisible()

    await nav.getByRole('button', { name: 'export', exact: true }).click()
    await expect(page.locator('section.export-panel')).toBeVisible()

    await nav.getByRole('button', { name: 'relations', exact: true }).click()
    await expect(page.locator('section.relations-panel')).toBeVisible()

    await nav.getByRole('button', { name: 'raw', exact: true }).click()
    await expect(page.locator('section.raw-panel')).toBeVisible()
  })
})

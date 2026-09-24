/**
 * Assertion-based visual contracts for MVP tabs (mocked extract).
 * Prefer swatches / rulers / previews over prose and QA dumps on the default path.
 */

import { expect, test } from '@playwright/test'
import {
  EXTRACTION_TIMEOUT_MS,
  expectProjectLoaded,
  goToTab,
  gotoAppWithMocks,
  runExtraction,
  uploadFixtureImage,
} from './helpers/workflows'

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

test.describe('Visual contracts (mocked)', () => {
  test.describe.configure({ timeout: EXTRACTION_TIMEOUT_MS + 60_000 })

  test.beforeEach(async ({ page }) => {
    test.skip(process.env.PLAYWRIGHT_USE_MOCKS !== 'true', 'Requires PLAYWRIGHT_USE_MOCKS=true')
    await gotoAppWithMocks(page)
  })

  test('anti-bloat: single chrome and MVP tabs only', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Copy That', level: 1 })).toHaveCount(1)
    await expect(page.locator('input#file-input')).toHaveCount(1)
    await expect(page.getByTestId('extract-design-tokens')).toHaveCount(1)
    await expect(page.locator('nav.tabs')).toHaveCount(1)

    const nav = page.locator('nav.tabs')
    const labels = await nav.getByRole('button').allTextContents()
    expect(labels.map((t) => t.trim())).toEqual([...MVP_TABS])
    await expect(nav.getByRole('button', { name: 'Lighting', exact: true })).toHaveCount(0)
  })

  test('post-extract: each tab leads with visual design information', async ({ page }) => {
    await uploadFixtureImage(page)
    await runExtraction(page, {
      tokenCounts: { colors: 1, spacing: 1, typography: 1, shadows: 1 },
    })
    await expectProjectLoaded(page)

    // Upload collapses so Snapshot owns counts (no mandatory duplicate expanded strip)
    await expect(page.locator('section.upload-panel').getByRole('button', { name: 'Change image' })).toBeVisible({
      timeout: 15_000,
    })

    await goToTab(page, 'overview')
    await expect(page.getByRole('heading', { name: 'Snapshot' })).toBeVisible()
    await expect(page.getByTestId('overview-swatches')).toBeVisible()
    await expect(page.getByText(/Upload an image to extract colors/i)).toHaveCount(0)
    await expect(page.getByText('Spacing & color QA')).toHaveCount(0)
    await expect(page.getByText(/Your Design Has a Story to Tell/i)).toHaveCount(0)

    await goToTab(page, 'colors')
    await expect(page.locator('section.colors-panel .palette-swatch').first()).toBeVisible()
    await expect(page.locator('section.colors-panel details.colors-advanced')).toHaveCount(0)

    await goToTab(page, 'spacing')
    await expect(
      page.locator('[data-testid="spacing-visual"], .spacing-ruler, .spacing-gap-demo').first(),
    ).toBeVisible()

    await goToTab(page, 'typography')
    await expect(page.getByTestId('typo-specimen').first()).toBeVisible()

    await goToTab(page, 'shadows')
    const shadowsPanel = page.locator('section.shadows-panel')
    const cards = shadowsPanel.locator('.shadow-card')
    const empty = shadowsPanel.getByText(/No elevation detected/i)
    await expect(cards.or(empty).first()).toBeVisible()

    await goToTab(page, 'shape')
    const shapePanel = page.locator('section.shape-panel')
    const viewport = shapePanel.getByTestId('layout-viewport')
    const shapeEmpty = shapePanel.getByText(/No layout tokens yet/i)
    await expect(viewport.or(shapeEmpty).first()).toBeVisible()
    await expect(page.getByText('Motion (P2b)')).toHaveCount(0)
    await expect(page.getByText('DTCG types (derived)')).toHaveCount(0)
    await expect(page.getByText(/full DTCG coverage/i)).toHaveCount(0)

    await goToTab(page, 'export')
    const exportPanel = page.locator('section.export-panel')
    await expect(exportPanel.getByRole('heading', { name: 'Token snapshot' })).toBeVisible()
    await expect(exportPanel.getByRole('button', { name: /Download W3C JSON/i })).toBeVisible()
    await expect(exportPanel.getByRole('button', { name: /Download CSS/i })).toBeVisible()
  })

  test('debug on reveals diagnostics QA on overview', async ({ page }) => {
    await uploadFixtureImage(page)
    await runExtraction(page, { tokenCounts: { colors: 1 } })
    await expectProjectLoaded(page)

    // Custom toggle hides the native checkbox (opacity 0); click the slider.
    await expect(page.getByText('Debug off')).toBeVisible()
    await page.locator('.header-actions .switch .slider').click()
    await expect(page.getByText('Debug on')).toBeVisible()
    await goToTab(page, 'overview')
    await expect(page.getByText('Spacing & color QA')).toBeVisible({ timeout: 15_000 })
    await expect(page.locator('.diagnostics').first()).toBeVisible()
  })
})

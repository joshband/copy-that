import fs from 'fs/promises'
import path from 'path'
import { fileURLToPath } from 'url'
import { test, expect, type Page, type TestInfo } from '@playwright/test'
import {
  gotoAppWithMocks,
  uploadFixtureImage,
  runExtraction,
  waitForExtractionComplete,
  expectProjectLoaded,
  goToTab,
} from './helpers/workflows'

const testDir = path.dirname(fileURLToPath(import.meta.url))
const repoRoot = path.resolve(testDir, '..', '..', '..')
const now = new Date()
const isoStamp = now.toISOString()
const [dateStamp, timeStampRaw] = isoStamp.split('T')
const timeStamp = (timeStampRaw ?? 'run').split('.')[0].replace(/:/g, '-')
const screenshotDir = path.join(repoRoot, 'playwright-tests', `${dateStamp}-${timeStamp}`)
const realisticFixture = path.join(repoRoot, 'test_images', 'IMG_8324.jpeg')

const slugify = (value: string) =>
  value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '')

async function capture(page: Page, testInfo: TestInfo, label: string) {
  await fs.mkdir(screenshotDir, { recursive: true })
  await page.evaluate(() => window.scrollTo(0, 0))
  const fileName = `${slugify(testInfo.title)}-${slugify(label)}.png`
  await page.screenshot({ path: path.join(screenshotDir, fileName), fullPage: true })
}

test('extraction flow exposes token data points and captures screens', async ({ page }, testInfo) => {
  await gotoAppWithMocks(page, { projectId: 1 })

  await expect(page.getByRole('heading', { name: 'Upload an image', exact: true })).toBeVisible()
  await capture(page, testInfo, '01-main')

  await uploadFixtureImage(page, realisticFixture)
  await expect(page.getByRole('heading', { name: 'Preview', exact: true })).toBeVisible()
  await expect(page.locator('.preview-name')).toContainText('IMG_8324.jpeg')
  await capture(page, testInfo, '02-image-preview')

  const lightingResponse = page.waitForResponse((resp) => {
    return resp.url().includes('/api/v1/lighting/analyze') && resp.status() === 200
  })
  await runExtraction(page, { waitForCompletion: false })
  await lightingResponse
  await capture(page, testInfo, '03-extract-clicked')

  await waitForExtractionComplete(page)
  await expectProjectLoaded(page, 1)

  const overviewPanel = page.locator('section.overview-panel')
  await expect(overviewPanel).toBeVisible()
  await expect(overviewPanel.getByRole('heading', { name: 'Snapshot' })).toBeVisible()
  await capture(page, testInfo, '04-overview')

  const uploadPanel = page.locator('section.upload-panel')
  await expect(uploadPanel).toBeVisible()
  await uploadPanel.getByRole('button', { name: 'Collapse' }).click()
  await expect(uploadPanel.getByRole('button', { name: 'Expand' })).toBeVisible()
  await expect(uploadPanel.locator('.upload-panel-summary')).toBeVisible()
  await capture(page, testInfo, '05-upload-collapsed')
  await uploadPanel.getByRole('button', { name: 'Expand' }).click()
  await expect(uploadPanel.getByRole('button', { name: 'Collapse' })).toBeVisible()

  await goToTab(page, 'colors')
  const colorsPanel = page.locator('section.colors-panel')
  await expect(colorsPanel).toBeVisible()

  const detailPanel = colorsPanel.locator('.detail-panel').first()
  const tabs = ['Overview', 'Harmony', 'Accessibility', 'Properties', 'Names', 'States', 'Diagnostics']
  for (const tab of tabs) {
    await expect(detailPanel.getByRole('button', { name: tab })).toBeVisible()
  }
  await expect(page.getByRole('heading', { name: 'Text Primary' })).toBeVisible()
  await expect(detailPanel.locator('.hex-clickable')).toHaveText('#111111')
  await expect(detailPanel.getByText('98% confidence')).toBeVisible()
  await expect(detailPanel).toContainText('rgb(17, 17, 17)')
  await expect(detailPanel).toContainText('Contrast: high')
  await expect(detailPanel).toContainText('OKLCH merged')
  await expect(colorsPanel.getByText('color.text.primary').first()).toBeVisible()

  const overviewSection = detailPanel.locator('.overview-content')
  await expect(overviewSection.getByText('Design Intent')).toBeVisible()
  await expect(overviewSection.getByText('Primary text')).toBeVisible()
  await expect(overviewSection.locator('.temp-badge')).toHaveText('cool')
  await expect(overviewSection.locator('.semantic-grid')).toContainText('slate')
  await capture(page, testInfo, '06-colors-overview')

  await detailPanel.getByRole('button', { name: 'Accessibility' }).click()
  await expect(detailPanel.getByText('Accessibility & Contrast')).toBeVisible()
  await expect(detailPanel.getByText('Contrast Ratio: 12.34:1')).toBeVisible()
  await capture(page, testInfo, '07-colors-accessibility')

  await detailPanel.getByRole('button', { name: 'Properties' }).click()
  const propertiesGrid = detailPanel.locator('.properties-grid')
  await expect(propertiesGrid.getByText('Saturation')).toBeVisible()
  await expect(propertiesGrid).toContainText('low')
  await expect(propertiesGrid.getByText('Lightness')).toBeVisible()
  await expect(propertiesGrid).toContainText('dark')
  await capture(page, testInfo, '08-colors-properties')

  await detailPanel.getByRole('button', { name: 'Names' }).click()
  await expect(detailPanel.getByRole('heading', { name: 'Simple' })).toBeVisible()
  await expect(detailPanel.getByText('slate', { exact: true })).toBeVisible()
  await capture(page, testInfo, '09-colors-names')

  await detailPanel.getByRole('button', { name: 'States' }).click()
  await expect(detailPanel.getByText('Interactive State Variants')).toBeVisible()
  await expect(detailPanel.getByText('#333333')).toBeVisible()
  const defaultSwatch = detailPanel
    .locator('.state-variant-card', { hasText: 'Default' })
    .locator('.variant-swatch-large')
  const hoverSwatch = detailPanel
    .locator('.state-variant-card', { hasText: 'Hover' })
    .locator('.variant-swatch-large')
  const [defaultBox, hoverBox] = await Promise.all([
    defaultSwatch.boundingBox(),
    hoverSwatch.boundingBox(),
  ])
  expect(defaultBox).not.toBeNull()
  expect(hoverBox).not.toBeNull()
  if (defaultBox && hoverBox) {
    expect(Math.abs(defaultBox.y - hoverBox.y)).toBeLessThanOrEqual(1)
  }
  await capture(page, testInfo, '10-colors-states')

  await detailPanel.getByRole('button', { name: 'Harmony' }).click()
  await expect(detailPanel.getByText(/Color Harmony:/)).toBeVisible()
  await capture(page, testInfo, '11-colors-harmony')

  await detailPanel.getByRole('button', { name: 'Diagnostics' }).click()
  await expect(detailPanel.getByText('No diagnostics overlay available for this color')).toBeVisible()
  await capture(page, testInfo, '12-colors-diagnostics')

  await goToTab(page, 'spacing')
  const spacingPanel = page.locator('section.spacing-panel').first()
  await expect(spacingPanel).toBeVisible()
  await expect(spacingPanel.getByRole('heading', { name: 'Spacing scale (graph)' })).toBeVisible()
  await expect(spacingPanel.locator('code', { hasText: 'spacing.base' }).first()).toBeVisible()
  await expect(spacingPanel.getByText('Token Details & Metadata')).toBeVisible()
  await expect(spacingPanel.getByText('Tailwind').first()).toBeVisible()
  await expect(spacingPanel.getByText('Responsive Scales')).toBeVisible()
  await capture(page, testInfo, '13-spacing')

  await goToTab(page, 'typography')
  const typographyPanel = page.locator('section.typography-panel')
  await expect(typographyPanel).toBeVisible()
  await expect(typographyPanel.getByRole('heading', { name: 'Typography inspector' })).toBeVisible()
  await expect(typographyPanel.getByText('Font: Inter')).toBeVisible()
  await expect(typographyPanel.getByText('Letter spacing: 0.02em')).toBeVisible()
  await expect(typographyPanel.getByText('Typography Details & Metrics')).toBeVisible()
  await expect(typographyPanel.getByText('Confidence:')).toBeVisible()
  await capture(page, testInfo, '14-typography')

  await goToTab(page, 'shadows')
  const shadowsPanel = page.locator('section.shadows-panel')
  await expect(shadowsPanel).toBeVisible()
  await expect(shadowsPanel.locator('.shadow-card')).toHaveCount(1)
  await expect(shadowsPanel.getByText('shadow.card').first()).toBeVisible()
  await expect(shadowsPanel.getByText('Offset:').first()).toBeVisible()
  await expect(shadowsPanel.getByText('Shadow inspector')).toBeVisible()
  await capture(page, testInfo, '15-shadows')

  await goToTab(page, 'lighting')
  const lightingPanel = page.locator('section.lighting-panel')
  await expect(lightingPanel).toBeVisible()
  await expect(lightingPanel.getByRole('heading', { name: 'Shadow Analysis' })).toBeVisible()
  await capture(page, testInfo, '16-lighting')

  await goToTab(page, 'export')
  const exportPanel = page.locator('section.export-panel')
  await expect(exportPanel).toBeVisible()
  await expect(exportPanel.getByRole('heading', { name: 'Token snapshot' })).toBeVisible()
  await expect(exportPanel.getByText('colors').first()).toBeVisible()
  await capture(page, testInfo, '17-export')

  await goToTab(page, 'relations')
  const relationsPanel = page.locator('section.relations-panel')
  await expect(relationsPanel).toBeVisible()
  await expect(relationsPanel.getByText('aliasOf')).toBeVisible()
  await expect(relationsPanel.getByText('color.alias.primary')).toBeVisible()
  await capture(page, testInfo, '18-relations')

  await goToTab(page, 'raw')
  const rawPanel = page.locator('section.raw-panel')
  await expect(rawPanel).toBeVisible()
  await expect(rawPanel.getByRole('heading', { name: 'Structure & Sources' })).toBeVisible()
  await capture(page, testInfo, '19-raw')
})

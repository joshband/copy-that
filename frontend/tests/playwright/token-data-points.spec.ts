import fs from 'fs/promises'
import path from 'path'
import { fileURLToPath } from 'url'
import { test, expect, type Page, type TestInfo } from '@playwright/test'
import {
  gotoApp,
  uploadFixtureImage,
  runExtraction,
  waitForExtractionComplete,
  waitForPipelineStagesComplete,
  waitForTokenDataReady,
  expectProjectLoaded,
  goToTab,
  EXTRACTION_TIMEOUT_MS,
} from './helpers/workflows'

const testDir = path.dirname(fileURLToPath(import.meta.url))
const repoRoot = path.resolve(testDir, '..', '..', '..')
const now = new Date()
const isoStamp = now.toISOString()
const [dateStamp, timeStampRaw] = isoStamp.split('T')
const timeStamp = (timeStampRaw ?? 'run').split('.')[0].replace(/:/g, '-')
const screenshotDir = path.join(repoRoot, 'playwright-tests', `${dateStamp}-${timeStamp}`)
const realisticFixture = path.join(repoRoot, 'test_images', 'IMG_8324.jpeg')

test.setTimeout(EXTRACTION_TIMEOUT_MS + 60000)

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
  await gotoApp(page)

  await expect(page.getByRole('heading', { name: 'Upload an image', exact: true })).toBeVisible()
  await capture(page, testInfo, '01-main')

  await uploadFixtureImage(page, realisticFixture)
  await expect(page.getByRole('heading', { name: 'Preview', exact: true })).toBeVisible()
  await expect(page.locator('.preview-name')).toContainText('IMG_8324.jpeg')
  await capture(page, testInfo, '02-image-preview')

  const lightingResponse = page.waitForResponse(
    (resp) => resp.url().includes('/api/v1/lighting/analyze') && resp.status() === 200,
    { timeout: EXTRACTION_TIMEOUT_MS },
  )
  await runExtraction(page, { waitForCompletion: false })
  await lightingResponse
  await capture(page, testInfo, '03-extract-clicked')

  await waitForExtractionComplete(page)
  await waitForPipelineStagesComplete(page)
  await waitForTokenDataReady(page, {
    minCounts: { colors: 1, spacing: 1, typography: 1, shadows: 1 },
  })
  await expectProjectLoaded(page)

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
  const swatches = colorsPanel.locator('.palette-swatch')
  await expect(swatches.first()).toBeVisible()
  await swatches.first().click()
  await expect(detailPanel.locator('.color-name')).toBeVisible()
  await expect(detailPanel.locator('.hex-clickable')).toHaveText(/#[0-9A-Fa-f]{6}/)
  await expect(detailPanel.getByText(/% confidence/)).toBeVisible()
  await capture(page, testInfo, '06-colors-overview')

  await detailPanel.getByRole('button', { name: 'Accessibility' }).click()
  await expect(detailPanel.locator('.tab-content').first()).toBeVisible()
  await capture(page, testInfo, '07-colors-accessibility')

  await detailPanel.getByRole('button', { name: 'Properties' }).click()
  await expect(detailPanel.locator('.tab-content').first()).toBeVisible()
  await capture(page, testInfo, '08-colors-properties')

  await detailPanel.getByRole('button', { name: 'Names' }).click()
  await expect(detailPanel.locator('.tab-content').first()).toBeVisible()
  await capture(page, testInfo, '09-colors-names')

  await detailPanel.getByRole('button', { name: 'States' }).click()
  await expect(detailPanel.locator('.tab-content').first()).toBeVisible()
  await capture(page, testInfo, '10-colors-states')

  await detailPanel.getByRole('button', { name: 'Harmony' }).click()
  await expect(detailPanel.locator('.tab-content').first()).toBeVisible()
  await capture(page, testInfo, '11-colors-harmony')

  await detailPanel.getByRole('button', { name: 'Diagnostics' }).click()
  await expect(detailPanel.locator('.tab-content').first()).toBeVisible()
  await capture(page, testInfo, '12-colors-diagnostics')

  await goToTab(page, 'spacing')
  const spacingPanel = page.locator('section.spacing-panel').first()
  await expect(spacingPanel).toBeVisible()
  const spacingHeading = spacingPanel.getByRole('heading', { name: 'Spacing scale (graph)' })
  if ((await spacingHeading.count()) > 0) {
    await expect(spacingHeading).toBeVisible()
  } else {
    await expect(spacingPanel.getByText('No spacing tokens yet')).toBeVisible()
  }
  await capture(page, testInfo, '13-spacing')

  await goToTab(page, 'typography')
  const typographyPanel = page.locator('section.typography-panel')
  await expect(typographyPanel).toBeVisible()
  const typographyHeading = typographyPanel.getByRole('heading', { name: 'Typography inspector' })
  if ((await typographyHeading.count()) > 0) {
    await expect(typographyHeading).toBeVisible()
  } else {
    await expect(typographyPanel.getByText('No typography tokens yet')).toBeVisible()
  }
  await capture(page, testInfo, '14-typography')

  await goToTab(page, 'shadows')
  const shadowsPanel = page.locator('section.shadows-panel')
  await expect(shadowsPanel).toBeVisible()
  const shadowCards = shadowsPanel.locator('.shadow-card')
  if ((await shadowCards.count()) > 0) {
    await expect(shadowCards.first().locator('.shadow-title')).toBeVisible()
    await expect(shadowsPanel.getByText('Offset:').first()).toBeVisible()
  } else {
    await expect(shadowsPanel.getByText('No shadows extracted yet.')).toBeVisible()
  }
  await capture(page, testInfo, '15-shadows')

  await goToTab(page, 'lighting')
  const lightingPanel = page.locator('section.lighting-panel')
  await expect(lightingPanel).toBeVisible()
  const lightingHeading = lightingPanel.getByRole('heading', { name: 'Shadow Analysis' })
  if ((await lightingHeading.count()) > 0) {
    await expect(lightingHeading).toBeVisible()
  } else {
    await expect(lightingPanel.getByText('No lighting analysis available yet.')).toBeVisible()
  }
  await capture(page, testInfo, '16-lighting')

  await goToTab(page, 'export')
  const exportPanel = page.locator('section.export-panel')
  await expect(exportPanel).toBeVisible()
  await expect(exportPanel.getByRole('heading', { name: 'Token snapshot' })).toBeVisible()
  await capture(page, testInfo, '17-export')

  await goToTab(page, 'relations')
  const relationsPanel = page.locator('section.relations-panel')
  await expect(relationsPanel).toBeVisible()
  const aliasChip = relationsPanel.getByText('aliasOf')
  if ((await aliasChip.count()) > 0) {
    await expect(aliasChip.first()).toBeVisible()
  } else {
    await expect(relationsPanel.getByText('No relations detected')).toBeVisible()
  }
  await capture(page, testInfo, '18-relations')

  await goToTab(page, 'raw')
  const rawPanel = page.locator('section.raw-panel')
  await expect(rawPanel).toBeVisible()
  await expect(rawPanel.getByRole('heading', { name: 'Structure & Sources' })).toBeVisible()
  await capture(page, testInfo, '19-raw')
})

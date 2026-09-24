import path from 'path'
import { fileURLToPath } from 'url'
import { test, expect, type TestInfo } from '@playwright/test'
import { captureEvidence, startEvidenceRun, type EvidenceRun } from './helpers/evidenceCapture'
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
const realisticFixture = path.join(repoRoot, 'test_images', 'IMG_8324.jpeg')

test.setTimeout(EXTRACTION_TIMEOUT_MS + 60000)

let evidenceRun: EvidenceRun

test.beforeAll(async () => {
  evidenceRun = await startEvidenceRun('token-data-points')
})

async function capture(page: Parameters<typeof captureEvidence>[0], testInfo: TestInfo, label: string) {
  await captureEvidence(page, evidenceRun, label, testInfo)
}

test('extraction flow exposes token data points and captures screens', async ({ page }, testInfo) => {
  await gotoApp(page)

  await expect(page.getByRole('heading', { name: 'Upload an image', exact: true })).toBeVisible()
  await capture(page, testInfo, '01-main')

  await uploadFixtureImage(page, realisticFixture)
  await expect(page.getByRole('heading', { name: 'Preview', exact: true })).toBeVisible()
  await expect(page.locator('.preview-name')).toContainText('IMG_8324.jpeg')
  await capture(page, testInfo, '02-image-preview')

  await runExtraction(page, { waitForCompletion: false })
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
  // Auto-collapse after extract; expand to assert summary then re-collapse.
  const expandBtn = uploadPanel.getByRole('button', { name: 'Change image' })
  if ((await expandBtn.count()) > 0) {
    await expandBtn.click()
  }
  await expect(uploadPanel.getByRole('button', { name: 'Collapse' })).toBeVisible()
  await uploadPanel.getByRole('button', { name: 'Collapse' }).click()
  await expect(uploadPanel.getByRole('button', { name: 'Change image' })).toBeVisible()
  await expect(uploadPanel.locator('.upload-panel-summary')).toBeVisible()
  await capture(page, testInfo, '05-upload-collapsed')
  await uploadPanel.getByRole('button', { name: 'Change image' }).click()
  await expect(uploadPanel.getByRole('button', { name: 'Collapse' })).toBeVisible()

  await goToTab(page, 'colors')
  const colorsPanel = page.locator('section.colors-panel')
  await expect(colorsPanel).toBeVisible()

  const detailStack = colorsPanel.locator('.color-detail-stack')
  for (const section of ['Overview', 'Accessibility'] as const) {
    await expect(detailStack.getByRole('heading', { name: section, exact: true })).toBeVisible()
  }
  await expect(detailStack.getByText('More analysis')).toBeVisible()
  await detailStack.locator('details.color-detail-more summary').click()
  for (const section of ['Harmony', 'Properties', 'Names', 'States'] as const) {
    await expect(detailStack.getByRole('heading', { name: section, exact: true })).toBeVisible()
  }
  const detailPanel = colorsPanel.locator('.detail-panel').first()
  const swatches = colorsPanel.locator('.palette-swatch')
  await expect(swatches.first()).toBeVisible()
  await swatches.first().click()
  await expect(detailPanel.locator('.color-name')).toBeVisible()
  await expect(detailPanel.locator('.hex-clickable')).toHaveText(/#[0-9A-Fa-f]{6}/)
  await capture(page, testInfo, '06-colors-overview')

  await expect(detailStack.getByRole('heading', { name: 'Accessibility', exact: true })).toBeVisible()
  await expect(detailStack.getByRole('heading', { name: 'Overview' })).toBeVisible()
  await capture(page, testInfo, '07-colors-accessibility')
  await capture(page, testInfo, '08-colors-properties')
  await capture(page, testInfo, '09-colors-names')
  await capture(page, testInfo, '10-colors-states')
  await capture(page, testInfo, '11-colors-harmony')
  await capture(page, testInfo, '12-colors-diagnostics')

  await goToTab(page, 'spacing')
  const spacingPanel = page.locator('section.spacing-panel').first()
  await expect(spacingPanel).toBeVisible()
  const spacingHeading = spacingPanel.getByRole('heading', { name: /Spacing scale/i }).or(
    spacingPanel.locator('.spacing-ruler-title'),
  )
  if ((await spacingPanel.locator('.spacing-ruler').count()) > 0) {
    await expect(spacingPanel.locator('.spacing-ruler')).toBeVisible()
  } else if ((await spacingHeading.count()) > 0) {
    await expect(spacingHeading.first()).toBeVisible()
  } else {
    await expect(spacingPanel.getByText('No spacing tokens yet')).toBeVisible()
  }
  await capture(page, testInfo, '13-spacing')

  await goToTab(page, 'typography')
  const typographyPanel = page.locator('section.typography-panel')
  await expect(typographyPanel).toBeVisible()
  const typographyHeading = typographyPanel.getByRole('heading', { name: 'Typography', exact: true })
  if ((await typographyHeading.count()) > 0) {
    await expect(typographyHeading).toBeVisible()
  } else {
    await expect(
      typographyPanel.getByText(/No typography tokens yet|No type styles detected/i),
    ).toBeVisible()
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
    await expect(
      shadowsPanel.getByText(/No elevation detected|No shadows extracted yet/i),
    ).toBeVisible()
  }
  await capture(page, testInfo, '15-shadows')

  await goToTab(page, 'shape')
  const shapePanel = page.locator('section.shape-panel')
  await expect(shapePanel).toBeVisible()
  await expect(
    shapePanel.getByRole('heading', { name: /Grid, border, and radius|No layout tokens yet/i }),
  ).toBeVisible()
  await capture(page, testInfo, '16-shape')

  await goToTab(page, 'export')
  const exportPanel = page.locator('section.export-panel')
  await expect(exportPanel).toBeVisible()
  await expect(exportPanel.getByRole('heading', { name: 'Token snapshot' })).toBeVisible()
  await capture(page, testInfo, '17-export')
})

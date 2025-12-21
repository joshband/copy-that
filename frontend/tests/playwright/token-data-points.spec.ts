import fs from 'fs/promises'
import path from 'path'
import { fileURLToPath } from 'url'
import { test, expect, type Page, type TestInfo } from '@playwright/test'
import { gotoAppWithMocks, uploadFixtureImage, runExtraction, expectProjectLoaded, goToTab } from './helpers/workflows'

const testDir = path.dirname(fileURLToPath(import.meta.url))
const repoRoot = path.resolve(testDir, '..', '..', '..')
const now = new Date()
const isoStamp = now.toISOString()
const [dateStamp, timeStampRaw] = isoStamp.split('T')
const timeStamp = (timeStampRaw ?? 'run').split('.')[0].replace(/:/g, '-')
const screenshotDir = path.join(repoRoot, 'playwright-tests', `${dateStamp}-${timeStamp}`)

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

  await uploadFixtureImage(page)
  await expect(page.getByRole('heading', { name: 'Preview', exact: true })).toBeVisible()
  await expect(page.locator('.preview-name')).toContainText('sample.png')
  await capture(page, testInfo, '02-image-preview')

  await runExtraction(page)
  await capture(page, testInfo, '03-extract-clicked')

  await expectProjectLoaded(page, 1)

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
  await capture(page, testInfo, '04-colors-overview')

  await detailPanel.getByRole('button', { name: 'Accessibility' }).click()
  await expect(detailPanel.getByText('Accessibility & Contrast')).toBeVisible()
  await expect(detailPanel.getByText('Contrast Ratio: 12.34:1')).toBeVisible()
  await capture(page, testInfo, '05-colors-accessibility')

  await detailPanel.getByRole('button', { name: 'Properties' }).click()
  const propertiesGrid = detailPanel.locator('.properties-grid')
  await expect(propertiesGrid.getByText('Saturation')).toBeVisible()
  await expect(propertiesGrid).toContainText('low')
  await expect(propertiesGrid.getByText('Lightness')).toBeVisible()
  await expect(propertiesGrid).toContainText('dark')
  await capture(page, testInfo, '06-colors-properties')

  await detailPanel.getByRole('button', { name: 'Names' }).click()
  await expect(detailPanel.getByRole('heading', { name: 'Simple' })).toBeVisible()
  await expect(detailPanel.getByText('slate', { exact: true })).toBeVisible()
  await capture(page, testInfo, '07-colors-names')

  await detailPanel.getByRole('button', { name: 'States' }).click()
  await expect(detailPanel.getByText('Interactive State Variants')).toBeVisible()
  await expect(detailPanel.getByText('#333333')).toBeVisible()
  await capture(page, testInfo, '08-colors-states')

  await detailPanel.getByRole('button', { name: 'Harmony' }).click()
  await expect(detailPanel.getByText(/Color Harmony:/)).toBeVisible()
  await capture(page, testInfo, '09-colors-harmony')

  await detailPanel.getByRole('button', { name: 'Diagnostics' }).click()
  await expect(detailPanel.getByText('No diagnostics overlay available for this color')).toBeVisible()
  await capture(page, testInfo, '10-colors-diagnostics')

  await goToTab(page, 'spacing')
  const spacingPanel = page.locator('section.spacing-panel').first()
  await expect(spacingPanel).toBeVisible()
  await expect(spacingPanel.getByRole('heading', { name: 'Spacing scale (graph)' })).toBeVisible()
  await expect(spacingPanel.locator('code', { hasText: 'spacing.base' }).first()).toBeVisible()
  await expect(spacingPanel.getByText('Token Details & Metadata')).toBeVisible()
  await expect(spacingPanel.getByText('Tailwind').first()).toBeVisible()
  await expect(spacingPanel.getByText('Responsive Scales')).toBeVisible()
  await capture(page, testInfo, '11-spacing')

  await goToTab(page, 'typography')
  const typographyPanel = page.locator('section.typography-panel')
  await expect(typographyPanel).toBeVisible()
  await expect(typographyPanel.getByRole('heading', { name: 'Typography inspector' })).toBeVisible()
  await expect(typographyPanel.getByText('Font: Inter')).toBeVisible()
  await expect(typographyPanel.getByText('Letter spacing: 0.02em')).toBeVisible()
  await expect(typographyPanel.getByText('Typography Details & Metrics')).toBeVisible()
  await expect(typographyPanel.getByText('Confidence:')).toBeVisible()
  await capture(page, testInfo, '12-typography')

  await goToTab(page, 'shadows')
  const shadowsPanel = page.locator('section.shadows-panel')
  await expect(shadowsPanel).toBeVisible()
  await expect(shadowsPanel.locator('.shadow-card')).toHaveCount(1)
  await expect(shadowsPanel.getByText('shadow.card').first()).toBeVisible()
  await expect(shadowsPanel.getByText('Offset:').first()).toBeVisible()
  await expect(shadowsPanel.getByText('Shadow inspector')).toBeVisible()
  await capture(page, testInfo, '13-shadows')
})

import path from 'path'
import { fileURLToPath } from 'url'
import { test, expect } from '@playwright/test'
import {
  gotoApp,
  uploadFixtureImage,
  runExtraction,
  expectProjectLoaded,
  goToTab,
  EXTRACTION_TIMEOUT_MS,
} from './helpers/workflows'

test.setTimeout(EXTRACTION_TIMEOUT_MS + 60000)

test('extract controls render and disable until file chosen', async ({ page }) => {
  await page.goto('/')
  const extractBtn = page.getByRole('button', { name: /Extract Colors/i })
  await expect(extractBtn).toBeVisible()
  await expect(extractBtn).toBeDisabled()

  const __dirname = path.dirname(fileURLToPath(import.meta.url))
  const fixturePath = path.join(__dirname, 'fixtures', 'sample.png')
  await page.setInputFiles('input#file-input', fixturePath)
  await expect(extractBtn).toBeEnabled()
})

test('extraction loads project + tokens and renders colors tab', async ({ page }) => {
  await gotoApp(page)

  await uploadFixtureImage(page)
  await runExtraction(page)
  await expectProjectLoaded(page)

  await goToTab(page, 'colors')
  const colorsPanel = page.locator('section.colors-panel')
  await expect(colorsPanel).toBeVisible()
  await expect(colorsPanel.locator('.palette-title')).toContainText('Palette')
  await expect(colorsPanel.locator('.palette-swatch').first()).toBeVisible()
  await expect(colorsPanel.locator('.detail-panel .hex-clickable')).toHaveText(/#[0-9A-Fa-f]{6}/)
})

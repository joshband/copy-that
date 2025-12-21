import path from 'path'
import { fileURLToPath } from 'url'
import { test, expect } from '@playwright/test'
import { gotoAppWithMocks, uploadFixtureImage, runExtraction, expectProjectLoaded, goToTab } from './helpers/workflows'

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

test('mocked extraction loads project + tokens and renders colors tab', async ({ page }) => {
  await gotoAppWithMocks(page, { projectId: 1 })

  await uploadFixtureImage(page)
  await runExtraction(page)
  await expectProjectLoaded(page, 1)

  await goToTab(page, 'colors')
  await expect(page.getByRole('heading', { name: 'Text Primary' })).toBeVisible()
  await expect(page.locator('.palette-title')).toContainText('Palette')
})

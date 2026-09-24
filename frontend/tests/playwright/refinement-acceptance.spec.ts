import { test, expect } from '@playwright/test'
import fs from 'node:fs/promises'
import path from 'node:path'
import { gotoAppWithMocks, uploadFixtureImage, runExtraction, goToTab } from './helpers/workflows'

const tabs = ['overview', 'colors', 'spacing', 'typography', 'shadows', 'shape', 'mood', 'export']
for (const width of [360, 480, 768, 1280, 1440]) {
  test(`all enabled screens at ${width}px`, async ({ page }, info) => {
    await page.setViewportSize({ width, height: 900 })
    await gotoAppWithMocks(page)
    await uploadFixtureImage(page)
    await runExtraction(page)
    for (const tab of tabs) {
      await goToTab(page, tab)
      await expect(page.getByRole('tabpanel')).toBeVisible()
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true)
      expect((await page.locator('.sticky-chrome').boundingBox())!.height).toBeLessThanOrEqual(width < 768 ? 120 : 112)
      const screenshot = info.outputPath(`${tab}-${width}.png`)
      await page.screenshot({ path: screenshot, fullPage: true })
      await info.attach(`${tab}-${width}`, { path: screenshot, contentType: 'image/png' })
    }
  })
}

test('keyboard upload, manual tabs, and export', async ({ page }) => {
  await gotoAppWithMocks(page)
  for (let i = 0; i < 20; i++) {
    await page.keyboard.press('Tab')
    if (await page.locator('#file-input').evaluate(el => el === document.activeElement)) break
  }
  await expect(page.locator('#file-input')).toBeFocused()
  const choosing = page.waitForEvent('filechooser')
  await page.keyboard.press('Enter')
  await (await choosing).setFiles(path.resolve('frontend/tests/playwright/fixtures/sample.png'))
  for (let i = 0; i < 10; i++) {
    await page.keyboard.press('Tab')
    if (await page.getByTestId('extract-design-tokens').evaluate(el => el === document.activeElement)) break
  }
  await expect(page.getByTestId('extract-design-tokens')).toBeFocused()
  await page.keyboard.press('Enter')
  await expect(page.locator('.upload-panel')).toHaveAttribute('data-extraction-status', 'ready')
  await page.getByRole('tab', { name: 'Overview', exact: true }).focus()
  await page.keyboard.press('ArrowRight')
  await expect(page.getByRole('tab', { name: 'Colors', exact: true })).toBeFocused()
  await expect(page.getByRole('tab', { name: 'Overview', exact: true })).toHaveAttribute('aria-selected', 'true')
  await page.keyboard.press('Enter')
  await expect(page.getByRole('tab', { name: 'Colors', exact: true })).toHaveAttribute('aria-selected', 'true')
  await page.keyboard.press('End')
  await page.keyboard.press('Space')
  await expect(page.locator('.export-panel')).toBeVisible()
  await page.getByRole('button', { name: 'W3C JSON', exact: true }).focus()
  const downloading = page.waitForEvent('download')
  await page.keyboard.press('Enter')
  expect((await downloading).suggestedFilename()).toContain('project-1')
})

test('partial failure stays partial; graph failure can reload', async ({ page }) => {
  await gotoAppWithMocks(page)
  await page.route('**/api/v1/shadows/extract', route => route.fulfill({ status: 500, json: { detail: 'Shadow service unavailable' } }))
  await uploadFixtureImage(page)
  await runExtraction(page, { waitForCompletion: false })
  await expect(page.locator('.upload-panel')).toHaveAttribute('data-extraction-status', 'partial')
  await goToTab(page, 'shadows')
  await expect(page.getByText('Shadow extraction failed. Retry extraction from the source panel.')).toBeVisible()
  await goToTab(page, 'export')
  await expect(page.getByRole('button', { name: 'W3C JSON', exact: true })).toBeEnabled()
})

test('graph load failure exposes reload without re-extracting', async ({ page }) => {
  await gotoAppWithMocks(page)
  await page.route('**/api/v1/design-tokens/export/w3c**', route => route.fulfill({ status: 500, json: { detail: 'Graph unavailable' } }))
  await uploadFixtureImage(page)
  await runExtraction(page, { waitForCompletion: false })
  await expect(page.locator('.upload-panel')).toHaveAttribute('data-extraction-status', 'failed')
  await page.unroute('**/api/v1/design-tokens/export/w3c**')
  // Install a deterministic successful empty graph for the retry.
  await page.route('**/api/v1/design-tokens/export/w3c**', route => route.fulfill({ json: {} }))
  await page.getByRole('button', { name: 'Reload results' }).click()
  await expect(page.locator('.upload-panel')).toHaveAttribute('data-extraction-status', 'ready')
})

test('six download payloads belong to the displayed project; failures are reported', async ({ page }) => {
  await gotoAppWithMocks(page)
  await uploadFixtureImage(page)
  await runExtraction(page)
  await goToTab(page, 'export')
  for (const name of ['W3C JSON', 'CSS', 'React theme', 'Tailwind', 'Download Guide HTML', 'Download Guide Pack JSON']) {
    const pending = page.waitForEvent('download')
    await page.getByRole('button', { name, exact: true }).click()
    const download = await pending
    expect(download.suggestedFilename()).toContain('project-1')
    const contents = await fs.readFile((await download.path())!, 'utf8')
    expect(contents.length).toBeGreaterThan(10)
    expect(contents).toMatch(/#111111|project.1|Project 1/)
    await expect(page.getByText('Download started. Check your browser downloads.')).toBeVisible()
  }
  await page.route('**/api/v1/design-tokens/export/css**', route => route.fulfill({ status: 500, json: { detail: 'Download unavailable' } }))
  await page.getByRole('button', { name: 'CSS', exact: true }).click()
  await expect(page.getByRole('alert')).toContainText('Download unavailable')
})

test('200% text zoom reflows every screen', async ({ page }, info) => {
  await page.setViewportSize({ width: 768, height: 900 })
  await gotoAppWithMocks(page)
  await uploadFixtureImage(page)
  await runExtraction(page)
  await page.addStyleTag({ content: 'html { font-size: 200% !important; }' })
  for (const tab of tabs) {
    await goToTab(page, tab)
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true)
    await page.screenshot({ path: info.outputPath(`${tab}-text-200.png`), fullPage: true })
  }
})

import { expect, type Page } from '@playwright/test'
import path from 'path'
import { getFixturePath } from './fixtures'
import { installApiMocks, type MockOptions } from './mockApi'

export async function gotoApp(page: Page) {
  await page.goto('/')
  await expect(page.getByRole('heading', { name: 'Copy That' })).toBeVisible()
}

export async function gotoAppWithMocks(page: Page, options: MockOptions = {}) {
  await installApiMocks(page, options)
  await gotoApp(page)
}

export async function uploadFixtureImage(page: Page, fixtureNameOrPath = 'sample.png') {
  const filePath = path.isAbsolute(fixtureNameOrPath)
    ? fixtureNameOrPath
    : getFixturePath(fixtureNameOrPath)
  const normalized = path.normalize(filePath)
  const ignoredSubdirs = [
    path.normalize(path.join('test_images', 'components')),
    path.normalize(path.join('test_images', 'non-deadpan')),
  ]
  const hasIgnoredSubdir = ignoredSubdirs.some((segment) => normalized.includes(`${segment}${path.sep}`))
  const hasProcessedShadows = normalized
    .split(path.sep)
    .some((segment) => segment.startsWith('processedImageShadows'))
  if (hasIgnoredSubdir || hasProcessedShadows) {
    throw new Error(`Playwright image path is ignored: ${filePath}`)
  }
  await page.setInputFiles('input#file-input', filePath)
}

export async function runExtraction(
  page: Page,
  { waitForCompletion = true, timeoutMs }: { waitForCompletion?: boolean; timeoutMs?: number } = {},
) {
  const extractButton = page.getByRole('button', { name: /extract colors/i })
  await expect(extractButton).toBeEnabled()
  await extractButton.click()
  if (waitForCompletion) {
    await waitForExtractionComplete(page, { timeoutMs })
  }
}

export async function waitForExtractionComplete(
  page: Page,
  { timeoutMs = 120000 }: { timeoutMs?: number } = {},
) {
  const uploadPanel = page.locator('section.upload-panel')
  await expect(uploadPanel).toHaveAttribute('data-extraction-status', 'complete', { timeout: timeoutMs })
  await expect(uploadPanel).toHaveAttribute('data-extraction-complete', 'true', { timeout: timeoutMs })
  await expect(uploadPanel).toHaveAttribute('data-token-graph-ready', 'true', { timeout: timeoutMs })
}

export async function expectProjectLoaded(page: Page, projectId = 1) {
  await expect(page.locator('.project-id')).toContainText(`Project #${projectId}`)
}

export async function goToTab(page: Page, tab: string) {
  await page.locator('nav.tabs').getByRole('button', { name: tab, exact: true }).click()
}

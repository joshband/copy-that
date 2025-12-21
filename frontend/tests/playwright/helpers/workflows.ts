import { expect, type Page } from '@playwright/test'
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

export async function uploadFixtureImage(page: Page, fixtureName = 'sample.png') {
  await page.setInputFiles('input#file-input', getFixturePath(fixtureName))
}

export async function runExtraction(page: Page) {
  const extractButton = page.getByRole('button', { name: /extract colors/i })
  await expect(extractButton).toBeEnabled()
  await extractButton.click()
}

export async function expectProjectLoaded(page: Page, projectId = 1) {
  await expect(page.locator('.project-id')).toContainText(`Project #${projectId}`)
}

export async function goToTab(page: Page, tab: string) {
  await page.locator('nav.tabs').getByRole('button', { name: tab, exact: true }).click()
}

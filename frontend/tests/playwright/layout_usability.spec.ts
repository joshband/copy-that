import { test, expect } from '@playwright/test'
import { gotoApp } from './helpers/workflows'

test.describe('Layout usability', () => {
  test('keeps global scrolling enabled', async ({ page }) => {
    await gotoApp(page)

    const bodyOverflow = await page.evaluate(() => window.getComputedStyle(document.body).overflowY)
    const htmlOverflow = await page.evaluate(() => window.getComputedStyle(document.documentElement).overflowY)

    expect(['auto', 'scroll', 'visible']).toContain(bodyOverflow)
    expect(['auto', 'scroll', 'visible']).toContain(htmlOverflow)
  })
})

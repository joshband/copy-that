import { test, expect } from '@playwright/test'

test.describe('Empty states (before extraction)', () => {
  test('colors tab prompts selection', async ({ page }) => {
    await page.goto('/')
    await page.locator('nav.tabs').getByRole('button', { name: 'colors', exact: true }).click()
    await expect(page.getByRole('heading', { name: 'Select a color to explore' })).toBeVisible()
  })

  test('spacing tab shows a warning banner', async ({ page }) => {
    await page.goto('/')
    await page.locator('nav.tabs').getByRole('button', { name: 'spacing', exact: true }).click()
    await expect(page.locator('section.spacing-panel')).toBeVisible()
    await expect(page.locator('.warning-banner')).toContainText('No spacing tokens yet')
  })

  test('shadows tab shows empty state', async ({ page }) => {
    await page.goto('/')
    await page.locator('nav.tabs').getByRole('button', { name: 'shadows', exact: true }).click()
    await expect(page.getByText('No shadows extracted yet.')).toBeVisible()
  })
})

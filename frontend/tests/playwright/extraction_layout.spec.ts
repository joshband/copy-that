import { test, expect } from '@playwright/test'

test.describe('Empty states (before extraction)', () => {
  test('colors tab prompts selection', async ({ page }) => {
    await page.goto('/')
    await page.locator('nav.tabs').getByRole('button', { name: 'Colors', exact: true }).click()
    await expect(page.getByRole('heading', { name: 'Select a color to explore' })).toBeVisible()
  })

  test('spacing tab shows empty scale cue', async ({ page }) => {
    await page.goto('/')
    await page.locator('nav.tabs').getByRole('button', { name: 'Spacing', exact: true }).click()
    await expect(page.locator('section.spacing-panel')).toBeVisible()
    await expect(page.getByText('No spacing tokens yet')).toBeVisible()
  })

  test('shadows tab shows empty state', async ({ page }) => {
    await page.goto('/')
    await page.locator('nav.tabs').getByRole('button', { name: 'Shadows', exact: true }).click()
    await expect(page.getByText(/No elevation detected|No shadows extracted yet/i)).toBeVisible()
  })
})

import { expect, test } from '@playwright/test'

test.describe('UI redundancy guardrails', () => {
  test('primary actions and headings are not duplicated', async ({ page }) => {
    await page.goto('/')

    // Single main heading
    await expect(page.getByRole('heading', { name: 'Copy That' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Copy That' })).toHaveCount(1)

    // Single upload control + single extract CTA
    await expect(page.locator('input#file-input')).toHaveCount(1)
    await expect(page.getByRole('button', { name: /Extract Colors/i })).toHaveCount(1)
  })

  test('tab bar renders exactly once', async ({ page }) => {
    await page.goto('/')
    await expect(page.locator('nav.tabs')).toHaveCount(1)
  })
})

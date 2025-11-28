import { test, expect } from '@playwright/test'

test('homepage loads and shows extraction controls', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByText('Copy That Playground')).toBeVisible()
  await expect(page.getByRole('button', { name: /Extract Colors/i })).toBeVisible()
  await expect(page.getByText('Extracted tokens')).toBeVisible()
})

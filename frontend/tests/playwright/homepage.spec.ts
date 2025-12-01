import { test, expect } from '@playwright/test'

test('homepage loads and shows extraction controls', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByText('Copy That Playground')).toBeVisible()
  await expect(page.getByRole('button', { name: /Extract Colors/i })).toBeVisible()
  // Tabs should be present in the new layout
  const tabRow = page.locator('.tab-row')
  await expect(tabRow.getByRole('button', { name: 'Overview', exact: true })).toBeVisible()
  await expect(tabRow.getByRole('button', { name: 'Colors', exact: true })).toBeVisible()
})

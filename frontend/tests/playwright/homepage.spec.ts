import { test, expect } from '@playwright/test'
import { gotoApp } from './helpers/workflows'

test('homepage loads and shows upload + tabs', async ({ page }) => {
  await gotoApp(page)

  await expect(page.getByRole('heading', { name: 'Upload an image', exact: true })).toHaveCount(1)
  await expect(page.locator('label.upload-label')).toBeVisible()
  await expect(page.getByRole('button', { name: /extract design tokens/i })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Snapshot' })).toHaveCount(0)
  await expect(page.getByText(/Extract to explore colors/i)).toBeVisible()

  const tabs = ['Overview', 'Colors', 'Spacing', 'Typography', 'Shadows', 'Shape', 'Export']
  for (const tab of tabs) {
    await expect(page.locator('nav.tabs').getByRole('button', { name: tab, exact: true })).toBeVisible()
  }
})

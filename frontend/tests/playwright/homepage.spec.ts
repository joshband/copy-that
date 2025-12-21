import { test, expect } from '@playwright/test'
import { gotoApp } from './helpers/workflows'

test('homepage loads and shows upload + tabs', async ({ page }) => {
  await gotoApp(page)

  await expect(page.getByRole('heading', { name: 'Upload an image', exact: true })).toBeVisible()
  await expect(page.locator('label.upload-label')).toBeVisible()
  await expect(page.getByRole('button', { name: /extract colors/i })).toBeVisible()

  const tabs = ['overview', 'colors', 'spacing', 'typography', 'shadows', 'lighting', 'export', 'relations', 'raw']
  for (const tab of tabs) {
    await expect(page.locator('nav.tabs').getByRole('button', { name: tab, exact: true })).toBeVisible()
  }
})

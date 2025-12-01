import { expect, test } from '@playwright/test'

test('summary chips render with baseline values', async ({ page }) => {
  await page.goto('/')

  const summary = page.locator('.summary-bar')
  await expect(summary).toBeVisible()

  const labels = ['Colors', 'Aliases', 'Spacing', 'Multiples', 'Typography', 'Confidence']
  for (const label of labels) {
    await expect(summary.getByText(label)).toBeVisible()
  }
})

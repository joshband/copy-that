import { expect, test } from '@playwright/test'

test.describe('Tabbed token layout', () => {
  test('renders tabs and switches sections', async ({ page }) => {
    await page.goto('/')

    // Tabs should be present
    const tabRow = page.locator('.tab-row')
    const tabs = ['Overview', 'Colors', 'Spacing', 'Typography', 'Shadows', 'Relations', 'Raw']
    for (const name of tabs) {
      await expect(tabRow.getByRole('button', { name, exact: true })).toBeVisible()
    }

    // Switch to Colors tab and see color section
    await tabRow.getByRole('button', { name: 'Colors', exact: true }).click()
    await expect(page.getByRole('heading', { name: 'Color tokens' })).toBeVisible()

    // Switch to Typography tab and see typography section shell
    await tabRow.getByRole('button', { name: 'Typography', exact: true }).click()
    await expect(page.getByRole('heading', { name: 'Typography tokens' })).toBeVisible()

    // Switch to Relations tab and see relations heading
    await tabRow.getByRole('button', { name: 'Relations', exact: true }).click()
    await expect(page.getByRole('heading', { name: 'Relations' })).toBeVisible()
  })
})

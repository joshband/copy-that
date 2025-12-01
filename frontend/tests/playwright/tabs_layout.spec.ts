import { expect, test } from '@playwright/test'

test.describe('Tabbed token layout', () => {
  test('renders tabs and switches sections', async ({ page }) => {
    await page.goto('/')

    // Tabs should be present
    const tabs = ['Overview', 'Colors', 'Spacing', 'Typography', 'Shadows', 'Relations', 'Raw']
    for (const name of tabs) {
      await expect(page.getByRole('button', { name })).toBeVisible()
    }

    // Summary chips show up even with empty data
    await expect(page.getByText('Colors')).toBeVisible()

    // Switch to Colors tab and see color section
    await page.getByRole('button', { name: 'Colors' }).click()
    await expect(page.getByRole('heading', { name: 'Color tokens' })).toBeVisible()

    // Switch to Typography tab and see typography section shell
    await page.getByRole('button', { name: 'Typography' }).click()
    await expect(page.getByRole('heading', { name: 'Typography tokens' })).toBeVisible()

    // Switch to Relations tab and see relations heading
    await page.getByRole('button', { name: 'Relations' }).click()
    await expect(page.getByRole('heading', { name: 'Relations' })).toBeVisible()
  })
})

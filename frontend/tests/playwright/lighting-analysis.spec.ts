import { test, expect } from '@playwright/test'
import { gotoApp, goToTab } from './helpers/workflows'
import { featureFlags } from '../../src/config/featureFlags'

test.describe('Lighting tab', () => {
  test('is parked off the default MVP nav', async ({ page }) => {
    test.skip(featureFlags.showLightingTab, 'Lighting tab enabled — run live lighting specs instead')

    await gotoApp(page)
    await expect(page.locator('nav.tabs').getByRole('button', { name: 'Lighting', exact: true })).toHaveCount(
      0,
    )
  })

  test('renders empty state when lighting tab is enabled', async ({ page }) => {
    test.skip(!featureFlags.showLightingTab, 'Requires featureFlags.showLightingTab')

    await gotoApp(page)
    await goToTab(page, 'lighting')
    await expect(page.getByText(/No lighting analysis available yet/i)).toBeVisible()
  })
})

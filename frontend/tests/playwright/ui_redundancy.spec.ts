import { expect, test } from '@playwright/test'
import { gotoAppWithMocks } from './helpers/workflows'

const MVP_TABS = [
  'Overview',
  'Colors',
  'Spacing',
  'Typography',
  'Shadows',
  'Shape',
  'Mood',
  'Export',
] as const

test.describe('UI redundancy guardrails', () => {
  test('primary actions and headings are not duplicated', async ({ page }) => {
    await gotoAppWithMocks(page)

    await expect(page.getByRole('heading', { name: 'Copy That', level: 1 })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Copy That', level: 1 })).toHaveCount(1)

    await expect(page.locator('input#file-input')).toHaveCount(1)
    await expect(page.getByRole('button', { name: /Extract tokens/i })).toHaveCount(1)
    await expect(page.getByTestId('extract-design-tokens')).toHaveCount(1)
  })

  test('tab bar renders exactly once with MVP labels', async ({ page }) => {
    await gotoAppWithMocks(page)
    await expect(page.locator('nav.tabs')).toHaveCount(1)
    const labels = await page.locator('nav.tabs').getByRole('button').allTextContents()
    expect(labels.map((t) => t.trim())).toEqual([...MVP_TABS])
  })
})

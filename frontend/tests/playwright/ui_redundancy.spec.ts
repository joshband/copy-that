import { expect, test } from '@playwright/test'

test.describe('UI redundancy guardrails', () => {
  test('primary actions and headings are not duplicated', async ({ page }) => {
    await page.goto('/')

    // Single main heading
    await expect(page.getByRole('heading', { name: 'Copy That Playground' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Copy That Playground' })).toHaveCount(1)

    // Single upload control + single extract CTA
    await expect(page.getByLabel('Upload Image')).toHaveCount(1)
    await expect(page.getByRole('button', { name: /Extract Colors/i })).toHaveCount(1)
  })

  test('Go to upload prompts stay bounded', async ({ page }) => {
    await page.goto('/')
    const uploadPrompts = page.getByRole('button', { name: /Go to upload/i })
    const count = await uploadPrompts.count()

    // Allow some contextual prompts, but flag runaway duplication
    expect(count).toBeGreaterThan(0)
    expect(count).toBeLessThanOrEqual(6)
  })
})

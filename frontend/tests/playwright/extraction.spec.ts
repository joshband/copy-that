import path from 'path'
import { fileURLToPath } from 'url'
import { test, expect } from '@playwright/test'

const buildEvent = (event: string, data: Record<string, unknown>) =>
  `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`

test('extract controls render and disable until file chosen', async ({ page }) => {
  await page.goto('/')
  const extractBtn = page.getByRole('button', { name: /Extract Colors/i })
  await expect(extractBtn).toBeVisible()
  await expect(extractBtn).toBeDisabled()

  const __dirname = path.dirname(fileURLToPath(import.meta.url))
  const fixturePath = path.join(__dirname, 'fixtures', 'sample.png')
  await page.setInputFiles('input#file-input', fixturePath)
  await expect(extractBtn).toBeEnabled()
})

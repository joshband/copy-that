import { defineConfig, devices } from '@playwright/test'
import path from 'path'
import { fileURLToPath } from 'url'

if (!process.env.PLAYWRIGHT_USE_MOCKS) {
  process.env.PLAYWRIGHT_USE_MOCKS = 'true'
}

const port = Number(process.env.PLAYWRIGHT_PORT ?? 5173)
const baseURL = process.env.BASE_URL || `http://localhost:${port}`
const configDir = path.dirname(fileURLToPath(import.meta.url))
const screenshotMode = (process.env.PLAYWRIGHT_SCREENSHOT ?? 'only-on-failure') as
  | 'off'
  | 'on'
  | 'only-on-failure'
const videoMode = (process.env.PLAYWRIGHT_VIDEO ?? 'retain-on-failure') as
  | 'off'
  | 'on'
  | 'retain-on-failure'

export default defineConfig({
  testDir: 'tests/playwright',
  timeout: 120000,
  expect: {
    timeout: 10000,
  },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['list'],
    ['junit', { outputFile: 'test-results/playwright/results.xml' }],
    ['json', { outputFile: 'test-results/playwright/results.json' }],
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
  ],
  use: {
    baseURL,
    trace: 'on-first-retry',
    screenshot: screenshotMode,
    video: videoMode,
    actionTimeout: 0,
    permissions: ['clipboard-read', 'clipboard-write'],
  },
  webServer: {
    command: `pnpm dev -- --host 127.0.0.1 --port ${port}`,
    url: baseURL,
    reuseExistingServer: !process.env.CI,
    stdout: 'pipe',
    stderr: 'pipe',
    cwd: configDir,
    env: {
      // Keep SSE + fetch calls same-origin during E2E runs (tests can route/mock them).
      VITE_PORT: String(port),
      VITE_API_BASE_URL: baseURL,
      VITE_API_URL: '/api/v1',
    },
  },
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
      },
    },
  ],
})

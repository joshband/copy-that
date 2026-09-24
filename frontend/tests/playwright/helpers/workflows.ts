import { expect, type Page } from '@playwright/test'
import path from 'path'
import { getFixturePath } from './fixtures'
import { installApiMocks, type MockOptions } from './mockApi'

export const EXTRACTION_TIMEOUT_MS = Number(
  process.env.PLAYWRIGHT_EXTRACTION_TIMEOUT_MS ??
    (process.env.PLAYWRIGHT_USE_MOCKS === 'true' ? 45_000 : 6 * 60 * 1000),
)
const EXTRACTION_START_TIMEOUT_MS = Number(
  process.env.PLAYWRIGHT_EXTRACTION_START_TIMEOUT_MS ??
    (process.env.PLAYWRIGHT_USE_MOCKS === 'true' ? 15_000 : 60_000),
)
const DEFAULT_TOKEN_COUNTS = {
  colors: 1,
}

type TokenCountThresholds = {
  colors?: number
  spacing?: number
  typography?: number
  shadows?: number
}

const USE_MOCKS = process.env.PLAYWRIGHT_USE_MOCKS === 'true'
const mockedPages = new WeakSet<Page>()

async function ensureMocks(page: Page, options: MockOptions = {}) {
  if (!USE_MOCKS || mockedPages.has(page)) return
  await installApiMocks(page, options)
  mockedPages.add(page)
}

async function gotoAppBase(page: Page) {
  await page.goto('/')
  await expect(page.getByRole('heading', { name: 'Copy That' })).toBeVisible()
}

export async function gotoApp(page: Page, options: MockOptions = {}) {
  await ensureMocks(page, options)
  await gotoAppBase(page)
}

export async function gotoAppWithMocks(page: Page, options: MockOptions = {}) {
  await ensureMocks(page, options)
  await gotoAppBase(page)
}

export async function uploadFixtureImage(page: Page, fixtureNameOrPath = 'sample.png') {
  const filePath = path.isAbsolute(fixtureNameOrPath)
    ? fixtureNameOrPath
    : getFixturePath(fixtureNameOrPath)
  const normalized = path.normalize(filePath)
  const ignoredSubdirs = [
    path.normalize(path.join('test_images', 'components')),
    path.normalize(path.join('test_images', 'non-deadpan')),
  ]
  const hasIgnoredSubdir = ignoredSubdirs.some((segment) => normalized.includes(`${segment}${path.sep}`))
  const hasProcessedShadows = normalized
    .split(path.sep)
    .some((segment) => segment.startsWith('processedImageShadows'))
  if (hasIgnoredSubdir || hasProcessedShadows) {
    throw new Error(`Playwright image path is ignored: ${filePath}`)
  }
  await page.setInputFiles('input#file-input', filePath)
}

export async function runExtraction(
  page: Page,
  {
    waitForCompletion = true,
    waitForStart = true,
    waitForTokens = true,
    tokenCounts = DEFAULT_TOKEN_COUNTS,
    timeoutMs,
  }: {
    waitForCompletion?: boolean
    waitForStart?: boolean
    waitForTokens?: boolean
    tokenCounts?: TokenCountThresholds
    timeoutMs?: number
  } = {},
) {
  const extractButton = page.getByRole('button', { name: /Extract (Design )?Tokens/i })
  await expect(extractButton).toBeEnabled()
  await extractButton.click()
  if (waitForStart) {
    await waitForExtractionStart(page, { timeoutMs })
  }
  if (waitForCompletion) {
    await waitForExtractionComplete(page, { timeoutMs })
    if (waitForTokens) {
      await waitForTokenDataReady(page, { timeoutMs, minCounts: tokenCounts })
    }
  }
}

export async function waitForExtractionStart(
  page: Page,
  { timeoutMs = EXTRACTION_START_TIMEOUT_MS }: { timeoutMs?: number } = {},
) {
  const uploadPanel = page.locator('section.upload-panel')
  await expect(uploadPanel).toHaveAttribute(
    'data-extraction-status',
    /running|hydrating|ready|partial/,
    { timeout: timeoutMs },
  )
}

export async function waitForExtractionComplete(
  page: Page,
  { timeoutMs = EXTRACTION_TIMEOUT_MS }: { timeoutMs?: number } = {},
) {
  const uploadPanel = page.locator('section.upload-panel')
  await expect(uploadPanel).toHaveAttribute('data-extraction-status', 'ready', { timeout: timeoutMs })
  await expect(uploadPanel).toHaveAttribute('data-extraction-complete', 'true', { timeout: timeoutMs })
  await expect(uploadPanel).toHaveAttribute('data-token-graph-ready', 'true', { timeout: timeoutMs })
}

export async function waitForPipelineStagesComplete(
  page: Page,
  { timeoutMs = EXTRACTION_TIMEOUT_MS }: { timeoutMs?: number } = {},
) {
  // Completion is a state contract; progress rows may be collapsed or unmounted.
  await waitForExtractionComplete(page, { timeoutMs })
}

export async function waitForTokenDataReady(
  page: Page,
  {
    timeoutMs = EXTRACTION_TIMEOUT_MS,
    minCounts = DEFAULT_TOKEN_COUNTS,
  }: { timeoutMs?: number; minCounts?: TokenCountThresholds } = {},
) {
  await goToTab(page, 'overview')
  const snapshotCard = page.locator('section.overview-panel .overview-card', {
    has: page.getByRole('heading', { name: 'Snapshot' }),
  })
  await expect(snapshotCard).toBeVisible({ timeout: timeoutMs })

  const readCounts = async () => {
    const findCount = async (label: string) => {
      const stat = snapshotCard.locator('.overview-stat', {
        has: page.locator('.overview-stat__label', { hasText: new RegExp(`^${label}$`, 'i') }),
      })
      if ((await stat.count()) === 0) return 0
      const valueText = (await stat.locator('.overview-stat__value').innerText()).trim()
      const n = Number(valueText)
      return Number.isFinite(n) ? n : 0
    }
    return {
      colors: await findCount('Colors'),
      spacing: await findCount('Spacing'),
      typography: await findCount('Typography'),
      shadows: await findCount('Shadows'),
    }
  }

  if (minCounts.colors != null) {
    await expect
      .poll(async () => (await readCounts()).colors, { timeout: timeoutMs })
      .toBeGreaterThanOrEqual(minCounts.colors)
  }
  if (minCounts.spacing != null) {
    await expect
      .poll(async () => (await readCounts()).spacing, { timeout: timeoutMs })
      .toBeGreaterThanOrEqual(minCounts.spacing)
  }
  if (minCounts.typography != null) {
    await expect
      .poll(async () => (await readCounts()).typography, { timeout: timeoutMs })
      .toBeGreaterThanOrEqual(minCounts.typography)
  }
  if (minCounts.shadows != null) {
    await expect
      .poll(async () => (await readCounts()).shadows, { timeout: timeoutMs })
      .toBeGreaterThanOrEqual(minCounts.shadows)
  }
}

export async function expectProjectLoaded(page: Page, projectId?: number) {
  const projectLabel = page.locator('.project-id')
  await expect(projectLabel).toBeVisible()
  if (projectId != null) {
    await expect(projectLabel).toContainText(`Project #${projectId}`)
    return
  }
  await expect(projectLabel).toContainText(/Project #\d+/)
}

export async function goToTab(page: Page, tab: string) {
  const labels: Record<string, string> = {
    overview: 'Overview',
    mood: 'Mood',
    colors: 'Colors',
    spacing: 'Spacing',
    typography: 'Typography',
    shadows: 'Shadows',
    shape: 'Shape',
    export: 'Export',
    lighting: 'Lighting',
    relations: 'Relations',
    raw: 'Raw',
  }
  const name = labels[tab] ?? tab
  await page.locator('nav.tabs').getByRole('tab', { name, exact: true }).click()
}

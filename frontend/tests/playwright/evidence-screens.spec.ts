/**
 * Env-gated full-page dumps of MVP tabs after mocked extract.
 * Run: PLAYWRIGHT_CAPTURE_EVIDENCE=true PLAYWRIGHT_USE_MOCKS=true pnpm test:e2e:evidence
 * Artifacts land in playwright-tests/<stamp>/ — promote to docs/evidence/ manually.
 */
import { expect, test } from '@playwright/test'
import {
  CAPTURE_EVIDENCE,
  maybeCaptureEvidence,
  startEvidenceRun,
  type EvidenceRun,
} from './helpers/evidenceCapture'
import {
  EXTRACTION_TIMEOUT_MS,
  expectProjectLoaded,
  goToTab,
  gotoAppWithMocks,
  runExtraction,
  uploadFixtureImage,
} from './helpers/workflows'

const MVP_TABS = [
  'overview',
  'mood',
  'colors',
  'spacing',
  'typography',
  'shadows',
  'shape',
  'lighting',
  'export',
] as const

test.describe('Evidence screens (mocked)', () => {
  test.describe.configure({ timeout: EXTRACTION_TIMEOUT_MS + 60_000 })

  let run: EvidenceRun | null = null

  test.beforeEach(async ({ page }) => {
    test.skip(!CAPTURE_EVIDENCE, 'Set PLAYWRIGHT_CAPTURE_EVIDENCE=true to dump PNGs')
    test.skip(process.env.PLAYWRIGHT_USE_MOCKS !== 'true', 'Requires PLAYWRIGHT_USE_MOCKS=true')
    run = await startEvidenceRun('mvp-tabs')
    await gotoAppWithMocks(page)
  })

  test('dump overview and each MVP tab after extract', async ({ page }, testInfo) => {
    await uploadFixtureImage(page)
    await runExtraction(page, { tokenCounts: { colors: 1 } })
    await expectProjectLoaded(page)

    await goToTab(page, 'overview')
    await expect(page.getByRole('heading', { name: 'Snapshot' })).toBeVisible()
    await maybeCaptureEvidence(page, run, '01-overview', testInfo)

    for (let i = 0; i < MVP_TABS.length; i++) {
      const tab = MVP_TABS[i]
      if (tab === 'overview') continue
      await goToTab(page, tab)
      await expect(page.locator(`section.${tab}-panel`)).toBeVisible()
      const n = String(i + 1).padStart(2, '0')
      await maybeCaptureEvidence(page, run, `${n}-${tab}`, testInfo)
    }
  })
})

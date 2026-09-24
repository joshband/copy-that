import { test, expect } from '@playwright/test'
import fs from 'fs'
import path from 'path'
import {
  gotoApp,
  uploadFixtureImage,
  runExtraction,
  expectProjectLoaded,
  goToTab,
  EXTRACTION_TIMEOUT_MS,
} from './helpers/workflows'

type LayoutMetrics = {
  generated_at: string
  default_viewport: string
  viewports: Array<{
    label: string
    width: number
    height: number
    screenshot: string
    tab_row: {
      overflow_x: string
      client_width: number
      scroll_width: number
      scrollable: boolean
    }
    overview_stack: {
      narrative: { x: number; y: number; width: number; height: number }
      snapshot: { x: number; y: number; width: number; height: number }
      delta_x: number
      delta_width: number
      vertical_gap: number
      stacked: boolean
    }
  }>
}

type ViewportConfig = {
  label: string
  width: number
  height: number
  expect_tab_scroll?: boolean
  expect_stack?: boolean
}

const viewports: ViewportConfig[] = [
  { label: 'desktop', width: 1280, height: 900, expect_tab_scroll: false, expect_stack: false },
  { label: 'mobile-360', width: 360, height: 900, expect_tab_scroll: true, expect_stack: true },
  { label: 'mobile-480', width: 480, height: 900, expect_tab_scroll: false, expect_stack: true },
]

const reportRoot = path.join(process.cwd(), 'frontend', 'test-results', 'ui-report')
const screenshotDir = path.join(reportRoot, 'screenshots')
const metricsPath = path.join(reportRoot, 'layout-metrics.json')

const ensureReportDirs = () => {
  fs.mkdirSync(screenshotDir, { recursive: true })
}

test.describe('Overview layout', () => {
  test.describe.configure({ timeout: EXTRACTION_TIMEOUT_MS + 60000 })

  test('captures overview layout across default and mobile viewports', async ({ page }, testInfo) => {
    ensureReportDirs()

    await gotoApp(page)
    await uploadFixtureImage(page)
    await runExtraction(page)
    await expectProjectLoaded(page)
    await goToTab(page, 'overview')

    const metrics: LayoutMetrics = {
      generated_at: new Date().toISOString(),
      default_viewport: viewports[0].label,
      viewports: [],
    }

    for (const viewport of viewports) {
      await page.setViewportSize(viewport)
      await page.waitForTimeout(150)

      const tabRow = page.locator('nav.tabs')
      const overflowX = await tabRow.evaluate((el) => getComputedStyle(el).overflowX)
      const scrollWidth = await tabRow.evaluate((el) => el.scrollWidth)
      const clientWidth = await tabRow.evaluate((el) => el.clientWidth)

      if (viewport.expect_tab_scroll === true) {
        expect(['auto', 'scroll']).toContain(overflowX)
        expect(scrollWidth).toBeGreaterThan(clientWidth)
      }

      const narrativeCard = page.locator('section.overview-panel .overview-card', { has: page.getByRole('heading', { name: 'Palette', exact: true }).first() })
      const snapshotCard = page.locator('section.overview-panel .overview-card', {
        has: page.getByRole('heading', { name: 'Snapshot' }),
      })

      const narrativeBox = await narrativeCard.boundingBox()
      const snapshotBox = await snapshotCard.boundingBox()

      expect(narrativeBox).not.toBeNull()
      expect(snapshotBox).not.toBeNull()

      const deltaX = Math.abs(narrativeBox!.x - snapshotBox!.x)
      const deltaWidth = Math.abs(narrativeBox!.width - snapshotBox!.width)
      const verticalGap = narrativeBox!.y - (snapshotBox!.y + snapshotBox!.height)
      const stacked = deltaX < 2 && deltaWidth < 2 && narrativeBox!.y > snapshotBox!.y + snapshotBox!.height - 2

      if (viewport.expect_stack === true) {
        expect(stacked).toBe(true)
      }

      const screenshotName = `overview-${viewport.width}.png`
      metrics.viewports.push({
        label: viewport.label,
        width: viewport.width,
        height: viewport.height,
        screenshot: screenshotName,
        tab_row: {
          overflow_x: overflowX,
          client_width: clientWidth,
          scroll_width: scrollWidth,
          scrollable: scrollWidth > clientWidth,
        },
        overview_stack: {
          narrative: {
            x: narrativeBox!.x,
            y: narrativeBox!.y,
            width: narrativeBox!.width,
            height: narrativeBox!.height,
          },
          snapshot: {
            x: snapshotBox!.x,
            y: snapshotBox!.y,
            width: snapshotBox!.width,
            height: snapshotBox!.height,
          },
          delta_x: deltaX,
          delta_width: deltaWidth,
          vertical_gap: verticalGap,
          stacked,
        },
      })

      const screenshotPath = path.join(screenshotDir, screenshotName)
      await page.screenshot({ path: screenshotPath, fullPage: true })
      await testInfo.attach(`overview-${viewport.label}`, {
        path: screenshotPath,
        contentType: 'image/png',
      })
    }

    fs.writeFileSync(metricsPath, JSON.stringify(metrics, null, 2))
  })
})

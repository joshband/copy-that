/**
 * Full-page evidence dumps for human review (not pixel baselines).
 * - captureEvidence: always writes (used by deep walkthroughs like token-data-points)
 * - maybeCaptureEvidence: only when PLAYWRIGHT_CAPTURE_EVIDENCE=true
 */
import fs from 'fs/promises'
import path from 'path'
import { fileURLToPath } from 'url'
import type { Page, TestInfo } from '@playwright/test'

const helpersDir = path.dirname(fileURLToPath(import.meta.url))
const repoRoot = path.resolve(helpersDir, '..', '..', '..', '..')

export const CAPTURE_EVIDENCE = process.env.PLAYWRIGHT_CAPTURE_EVIDENCE === 'true'

export function slugify(value: string): string {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '')
}

export type EvidenceRun = {
  dir: string
  stamp: string
}

/** Create `playwright-tests/<ISO-stamp>-<prefix>/` for this run. */
export async function startEvidenceRun(prefix = 'evidence'): Promise<EvidenceRun> {
  const now = new Date()
  const isoStamp = now.toISOString()
  const [dateStamp, timeStampRaw] = isoStamp.split('T')
  const timeStamp = (timeStampRaw ?? 'run').split('.')[0].replace(/:/g, '-')
  const stamp = `${dateStamp}-${timeStamp}-${prefix}`
  const dir = path.join(repoRoot, 'playwright-tests', stamp)
  await fs.mkdir(dir, { recursive: true })
  return { dir, stamp }
}

/** Always write a full-page PNG into the evidence run directory. */
export async function captureEvidence(
  page: Page,
  run: EvidenceRun,
  label: string,
  testInfo?: TestInfo,
): Promise<string> {
  await fs.mkdir(run.dir, { recursive: true })
  await page.evaluate(() => window.scrollTo(0, 0))
  const prefix = testInfo ? `${slugify(testInfo.title)}-` : ''
  const fileName = `${prefix}${slugify(label)}.png`
  const filePath = path.join(run.dir, fileName)
  await page.screenshot({ path: filePath, fullPage: true })
  return filePath
}

/** Capture only when PLAYWRIGHT_CAPTURE_EVIDENCE=true. */
export async function maybeCaptureEvidence(
  page: Page,
  run: EvidenceRun | null,
  label: string,
  testInfo?: TestInfo,
): Promise<string | null> {
  if (!CAPTURE_EVIDENCE || !run) return null
  return captureEvidence(page, run, label, testInfo)
}

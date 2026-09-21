import fs from 'fs'
import path from 'path'
import os from 'os'
import { execSync } from 'child_process'

const rootDir = process.cwd()
const reportDir = path.join(rootDir, 'frontend', 'test-results', 'ui-report')
const screenshotDir = path.join(reportDir, 'screenshots')
const reportPath = path.join(reportDir, 'ui-summary.md')
const metricsPath = path.join(reportDir, 'layout-metrics.json')
const playwrightJsonPath = path.join(rootDir, 'frontend', 'test-results', 'playwright', 'results.json')
const reportGeneratedAt = new Date()
const uiImageRoot = process.env.UI_REPORT_IMAGE_DIR ?? path.join(os.homedir(), 'Desktop', 'midjourney')
const uiImageReportDir = path.join(reportDir, 'random-ui')
const extractionRoot = path.join(rootDir, 'playwright-tests')
const extractionPrefix = 'extraction-flow-exposes-token-data-points-and-captures-screens-'
const extractionHighlights = [
  '01-main',
  '04-overview',
  '06-colors-overview',
  '13-spacing',
  '14-typography',
  '15-shadows',
  '17-export',
]

const legacyFiles = [
  path.join(rootDir, 'frontend', 'src', 'features', 'visual-extraction', 'components', 'shadow', 'shadows', 'ShadowPalette.css'),
  path.join(rootDir, 'frontend', 'src', 'components', 'SessionCreator.css'),
  path.join(rootDir, 'frontend', 'src', 'components', 'BatchImageUploader.css'),
]

const run = (command) => {
  try {
    return execSync(command, { encoding: 'utf8' }).trim()
  } catch {
    return ''
  }
}

const readJson = (filePath) => {
  try {
    return JSON.parse(fs.readFileSync(filePath, 'utf8'))
  } catch {
    return null
  }
}

const expandHomeDir = (targetPath) => {
  if (!targetPath) return targetPath
  if (targetPath === '~') return os.homedir()
  if (targetPath.startsWith('~/') || targetPath.startsWith(`~${path.sep}`)) {
    return path.join(os.homedir(), targetPath.slice(2))
  }
  return targetPath
}

const formatTimestampForFile = (date) =>
  date
    .toISOString()
    .replace('T', '-')
    .replace(/\..+$/, '')
    .replace(/:/g, '-')

const slugify = (value) =>
  value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '')

const pickRandomUiImage = () => {
  const resolvedRoot = expandHomeDir(uiImageRoot)
  if (!resolvedRoot) {
    return { error: 'UI image directory is not configured.' }
  }

  let entries
  try {
    entries = fs.readdirSync(resolvedRoot, { withFileTypes: true })
  } catch (error) {
    return {
      error: `Unable to read UI image directory (${resolvedRoot}): ${error.message ?? 'unknown error'}`,
    }
  }

  const files = entries
    .filter((entry) => entry.isFile())
    .map((entry) => entry.name)
    .filter((name) => ['.png', '.jpg', '.jpeg', '.webp'].includes(path.extname(name).toLowerCase()))

  if (!files.length) {
    return { error: `No images found in ${resolvedRoot}.` }
  }

  const choice = files[Math.floor(Math.random() * files.length)]
  return { sourcePath: path.join(resolvedRoot, choice) }
}

const copyRandomUiImage = () => {
  const selection = pickRandomUiImage()
  if (!selection.sourcePath) {
    return { error: selection.error ?? 'No UI image selected.' }
  }

  const ext = path.extname(selection.sourcePath).toLowerCase() || '.png'
  const base = slugify(path.parse(selection.sourcePath).name) || 'midjourney'
  const timestamp = formatTimestampForFile(reportGeneratedAt)
  const destName = `${base}-${timestamp}${ext}`
  const destPath = path.join(uiImageReportDir, destName)

  try {
    fs.mkdirSync(uiImageReportDir, { recursive: true })
    fs.copyFileSync(selection.sourcePath, destPath)
  } catch (error) {
    return {
      error: `Failed to copy UI image to report (${destPath}): ${error.message ?? 'unknown error'}`,
      sourcePath: selection.sourcePath,
    }
  }

  return {
    sourcePath: selection.sourcePath,
    destPath,
    destName,
  }
}

const readLines = (value) => value.split('\n').map((line) => line.trim()).filter(Boolean)

const resolveUpstream = () => run('git rev-parse --abbrev-ref --symbolic-full-name @{u}')

const resolveOriginBase = () => {
  const originHead = run('git symbolic-ref --short refs/remotes/origin/HEAD')
  if (originHead) return originHead
  const candidates = ['origin/main', 'origin/master']
  for (const ref of candidates) {
    if (run(`git rev-parse --verify ${ref}`)) {
      return ref
    }
  }
  return ''
}

const reportMode = (process.env.UI_REPORT_MODE ?? 'local').toLowerCase()
const explicitBaseRef = process.env.UI_REPORT_BASE_REF ?? ''
const upstreamRef = resolveUpstream()
const baseRef = explicitBaseRef || (reportMode === 'pr' ? resolveOriginBase() : upstreamRef)
const baseRefOk = baseRef ? !!run(`git rev-parse --verify ${baseRef}`) : false

const collectChangeFiles = () => {
  const staged = readLines(run('git diff --cached --name-only'))
  const unstaged = readLines(run('git diff --name-only'))
  const untracked = readLines(run('git ls-files --others --exclude-standard'))
  const workingFiles = new Set([...staged, ...unstaged, ...untracked])

  const unpushedCommits = upstreamRef ? readLines(run(`git log --oneline ${upstreamRef}..HEAD`)) : []
  const unpushedFiles = upstreamRef ? readLines(run(`git diff --name-only ${upstreamRef}..HEAD`)) : []

  const prFiles = baseRefOk ? readLines(run(`git diff --name-only ${baseRef}...HEAD`)) : []

  return {
    staged,
    unstaged,
    untracked,
    workingFiles: Array.from(workingFiles),
    unpushedCommits,
    unpushedFiles,
    prFiles,
    workingStats: {
      staged: staged.length,
      unstaged: unstaged.length,
      untracked: untracked.length,
      total: workingFiles.size,
    },
    diffStats: {
      working: run('git diff --shortstat'),
      staged: run('git diff --cached --shortstat'),
      unpushed: upstreamRef ? run(`git diff --shortstat ${upstreamRef}..HEAD`) : '',
      pr: baseRefOk ? run(`git diff --shortstat ${baseRef}...HEAD`) : '',
    },
  }
}

const categorizePath = (file) => {
  if (file.startsWith('frontend/tests/')) return 'frontend-tests'
  if (file.startsWith('frontend/')) return 'frontend'
  if (file.startsWith('src/')) return 'backend'
  if (file.startsWith('tests/')) return 'backend-tests'
  if (file.startsWith('docs/')) return 'docs'
  if (file.startsWith('scripts/')) return 'scripts'
  if (file.startsWith('playwright-tests/')) return 'playwright-artifacts'
  if (file.startsWith('frontend/test-results/') || file.startsWith('frontend/playwright-report/')) {
    return 'playwright-artifacts'
  }
  return 'root'
}

const summarizeCategories = (files) => {
  const counts = {}
  files.forEach((file) => {
    const key = categorizePath(file)
    counts[key] = (counts[key] ?? 0) + 1
  })
  return counts
}

const findLatestExtractionBundle = () => {
  if (!fs.existsSync(extractionRoot)) return null
  const bundles = fs
    .readdirSync(extractionRoot, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => path.join(extractionRoot, entry.name))
    .filter((dir) => fs.existsSync(path.join(dir, `${extractionPrefix}01-main.png`)))

  if (!bundles.length) return null

  return bundles
    .map((dir) => ({ dir, mtime: fs.statSync(dir).mtimeMs }))
    .sort((a, b) => b.mtime - a.mtime)[0].dir
}

const listExtractionScreens = (bundleDir) => {
  try {
    return fs
      .readdirSync(bundleDir)
      .filter((file) => file.startsWith(extractionPrefix) && file.endsWith('.png'))
      .sort()
  } catch {
    return []
  }
}

const formatExtractionAlt = (fileName) => {
  const base = fileName.replace(/\.png$/, '')
  const label = base.startsWith(extractionPrefix) ? base.slice(extractionPrefix.length) : base
  return `Extraction flow ${label.replace(/-/g, ' ')}`.trim()
}

const formatDuration = (ms) => {
  if (!ms || Number.isNaN(ms)) return 'n/a'
  const seconds = ms / 1000
  return `${seconds.toFixed(2)}s`
}

const parseGitStatus = (statusText) => {
  const built = []
  const updated = []
  const removed = []
  const renamed = []

  statusText.split('\n').filter(Boolean).forEach((line) => {
    const status = line.slice(0, 2).trim()
    const file = line.slice(3).trim()
    if (!file) return

    if (status === '??' || status === 'A') {
      built.push(file)
      return
    }
    if (status.startsWith('R')) {
      renamed.push(file)
      return
    }
    if (status.startsWith('D')) {
      removed.push(file)
      return
    }
    updated.push(file)
  })

  return { built, updated, removed, renamed }
}

const expandHex = (hex) => {
  const clean = hex.replace('#', '')
  if (clean.length === 3) {
    return `#${clean[0]}${clean[0]}${clean[1]}${clean[1]}${clean[2]}${clean[2]}`
  }
  if (clean.length === 6) {
    return `#${clean}`
  }
  return null
}

const hexToRgb = (hex) => {
  const expanded = expandHex(hex)
  if (!expanded) return null
  const value = expanded.replace('#', '')
  const r = parseInt(value.slice(0, 2), 16)
  const g = parseInt(value.slice(2, 4), 16)
  const b = parseInt(value.slice(4, 6), 16)
  return { r, g, b }
}

const isGray = (rgb) => rgb && rgb.r === rgb.g && rgb.g === rgb.b

const relativeLuminance = (rgb) => {
  const channel = (val) => {
    const s = val / 255
    return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4)
  }
  return 0.2126 * channel(rgb.r) + 0.7152 * channel(rgb.g) + 0.0722 * channel(rgb.b)
}

const contrastRatio = (hexA, hexB) => {
  const rgbA = hexToRgb(hexA)
  const rgbB = hexToRgb(hexB)
  if (!rgbA || !rgbB) return null
  const l1 = relativeLuminance(rgbA)
  const l2 = relativeLuminance(rgbB)
  const lighter = Math.max(l1, l2)
  const darker = Math.min(l1, l2)
  return (lighter + 0.05) / (darker + 0.05)
}

const extractGrayTextColors = (filePath) => {
  if (!fs.existsSync(filePath)) return []
  const lines = fs.readFileSync(filePath, 'utf8').split('\n')
  const results = []
  let currentSelector = ''

  lines.forEach((line, index) => {
    const selectorMatch = line.match(/^(.*)\{\s*$/)
    if (selectorMatch) {
      currentSelector = selectorMatch[1].trim()
    }
    if (line.includes('}')) {
      currentSelector = ''
    }

    const colorMatch = line.match(/color:\s*(#[0-9a-fA-F]{3,6})/)
    if (colorMatch) {
      const hex = colorMatch[1]
      const rgb = hexToRgb(hex)
      if (rgb && isGray(rgb)) {
        results.push({
          selector: currentSelector || '(unknown)',
          line: index + 1,
          value: expandHex(hex) ?? hex,
        })
      }
    }
  })

  return results
}

const report = []
report.push('# UI Summary Report')
report.push(`Generated: ${reportGeneratedAt.toISOString()}`)
report.push('')

const testReport = readJson(playwrightJsonPath)
if (testReport?.stats) {
  const stats = testReport.stats
  const total = stats.total ?? stats.expected + stats.unexpected + stats.flaky + stats.skipped
  const startTime = stats.startTime ? new Date(stats.startTime) : null
  const endTime =
    startTime && typeof stats.duration === 'number'
      ? new Date(startTime.getTime() + stats.duration)
      : null
  report.push('## Test Metrics')
  report.push(`- Total: ${total ?? 'n/a'}`)
  report.push(`- Passed: ${stats.expected ?? 'n/a'}`)
  report.push(`- Failed: ${stats.unexpected ?? 'n/a'}`)
  report.push(`- Flaky: ${stats.flaky ?? 'n/a'}`)
  report.push(`- Skipped: ${stats.skipped ?? 'n/a'}`)
  if (startTime) {
    report.push(`- Start: ${startTime.toISOString()}`)
  }
  if (endTime) {
    report.push(`- End: ${endTime.toISOString()}`)
  }
  report.push(`- Duration: ${formatDuration(stats.duration)}`)
  report.push('')
} else {
  report.push('## Test Metrics')
  report.push('- No Playwright JSON report found. Run Playwright with JSON reporter enabled.')
  report.push('')
}

const layoutMetrics = readJson(metricsPath)
if (layoutMetrics?.viewports?.length) {
  report.push('## Layout Metrics')
  if (layoutMetrics.default_viewport) {
    report.push(`- Default viewport: ${layoutMetrics.default_viewport}`)
  }
  layoutMetrics.viewports.forEach((viewport) => {
    const label = viewport.label ? `${viewport.label} ` : ''
    const defaultTag = viewport.label && layoutMetrics.default_viewport === viewport.label ? ' (default)' : ''
    const stacked = typeof viewport.overview_stack?.stacked === 'boolean' ? viewport.overview_stack.stacked : null
    const stackedLabel = stacked === null ? 'n/a' : stacked ? 'yes' : 'no'
    report.push(`- ${label}${viewport.width}x${viewport.height}${defaultTag}: tab scroll ${viewport.tab_row.scroll_width}/${viewport.tab_row.client_width}, overflow ${viewport.tab_row.overflow_x}, stacked ${stackedLabel}, stack delta x ${viewport.overview_stack.delta_x.toFixed(2)}px, width delta ${viewport.overview_stack.delta_width.toFixed(2)}px, vertical gap ${viewport.overview_stack.vertical_gap.toFixed(2)}px`)
  })
  report.push('')
}

if (layoutMetrics?.viewports?.length) {
  report.push('## Metrics Notes')
  report.push('- Tab scroll: scroll width vs client width; overflow indicates whether tabs need horizontal scrolling.')
  report.push('- Stacked: overview cards align vertically when stacked is yes.')
  report.push('- Stack delta x/width: horizontal alignment deltas between overview cards.')
  report.push('- Vertical gap: space between stacked cards; negative means overlap.')
  report.push('')
}

const changeData = collectChangeFiles()
const combinedChangeFiles = Array.from(
  new Set([...changeData.workingFiles, ...changeData.unpushedFiles]),
)
const combinedCategories = summarizeCategories(combinedChangeFiles)
const branchName = run('git rev-parse --abbrev-ref HEAD') || 'unknown'

report.push('## Change Scope')
report.push(`- Branch: ${branchName}`)
report.push(`- Upstream: ${upstreamRef || 'none'}`)
report.push(
  `- Working tree: ${changeData.workingStats.total} files (${changeData.workingStats.staged} staged, ${changeData.workingStats.unstaged} unstaged, ${changeData.workingStats.untracked} untracked)`,
)
if (changeData.diffStats.working) {
  report.push(`- Working diff: ${changeData.diffStats.working}`)
}
if (changeData.diffStats.staged) {
  report.push(`- Staged diff: ${changeData.diffStats.staged}`)
}
if (upstreamRef) {
  report.push(`- Unpushed commits: ${changeData.unpushedCommits.length}`)
  if (changeData.diffStats.unpushed) {
    report.push(`- Unpushed diff: ${changeData.diffStats.unpushed}`)
  }
} else {
  report.push('- Unpushed commits: upstream not set')
}
if (reportMode === 'pr' || explicitBaseRef) {
  if (baseRefOk) {
    report.push(`- PR base: ${baseRef}`)
    if (changeData.diffStats.pr) {
      report.push(`- PR diff: ${changeData.diffStats.pr}`)
    }
  } else {
    report.push(`- PR base: ${baseRef || 'none'} (invalid)`)
  }
}
report.push(`- Combined files: ${combinedChangeFiles.length}`)
report.push('')

report.push('## Change Surface')
if (!combinedChangeFiles.length) {
  report.push('- No local changes detected.')
  report.push('')
} else {
  Object.entries(combinedCategories)
    .sort((a, b) => b[1] - a[1])
    .forEach(([key, count]) => report.push(`- ${key}: ${count}`))
  report.push('')
}

report.push('## Change Diagram')
report.push('```mermaid')
report.push('flowchart TB')
if (!combinedChangeFiles.length) {
  report.push('  Changes["Local changes (0 files)"]')
} else {
  report.push(`  Changes["Local changes (${combinedChangeFiles.length} files)"]`)
  Object.entries(combinedCategories)
    .sort((a, b) => b[1] - a[1])
    .forEach(([key, count]) => {
      const nodeId = key.replace(/[^a-zA-Z0-9]/g, '_')
      report.push(`  Changes --> ${nodeId}["${key} (${count})"]`)
    })
}
report.push('```')
report.push('')

const gitStatus = parseGitStatus(run('git status --porcelain'))
report.push('## Working Tree Files')
report.push(`- Built: ${gitStatus.built.length}`)
report.push(`- Updated: ${gitStatus.updated.length}`)
report.push(`- Removed: ${gitStatus.removed.length}`)
report.push(`- Renamed: ${gitStatus.renamed.length}`)
report.push('')

const listSection = (title, items) => {
  report.push(`### ${title}`)
  if (!items.length) {
    report.push('- none')
    report.push('')
    return
  }
  items.slice(0, 50).forEach((item) => report.push(`- ${item}`))
  if (items.length > 50) {
    report.push(`- ... ${items.length - 50} more`)
  }
  report.push('')
}

listSection('Built', gitStatus.built)
listSection('Updated', gitStatus.updated)
listSection('Removed', gitStatus.removed)
listSection('Renamed', gitStatus.renamed)

report.push('## Unpushed Commits')
if (!upstreamRef) {
  report.push('- Upstream not set; unable to list unpushed commits.')
  report.push('')
} else {
  listSection('Commits', changeData.unpushedCommits)
}

report.push('## Unpushed Files')
if (!upstreamRef) {
  report.push('- Upstream not set; unable to list unpushed files.')
  report.push('')
} else {
  listSection('Files', changeData.unpushedFiles)
}

if (reportMode === 'pr' || explicitBaseRef) {
  report.push('## PR Diff Files')
  if (!baseRefOk) {
    report.push(`- Invalid PR base: ${baseRef || 'none'}`)
    report.push('')
  } else {
    listSection('Files', changeData.prFiles)
  }
}

report.push('## Visuals')
if (layoutMetrics?.viewports?.length) {
  const defaultLabel = layoutMetrics.default_viewport
  layoutMetrics.viewports.forEach((viewport) => {
    const screenshotName = viewport.screenshot ?? `overview-${viewport.width}.png`
    const screenshotPath = path.join(screenshotDir, screenshotName)
    const labelBase = viewport.label ? viewport.label.replace(/-/g, ' ') : `${viewport.width}px`
    const defaultTag = viewport.label && viewport.label === defaultLabel ? ' (default)' : ''
    const alt = `Overview ${labelBase} ${viewport.width}x${viewport.height}${defaultTag}`.trim()
    const rel = path.join('screenshots', screenshotName)
    if (fs.existsSync(screenshotPath)) {
      report.push(`![${alt}](${rel})`)
    } else {
      report.push(`- Missing ${screenshotName} (run layout test)`)
    }
  })
  report.push('')
} else {
  const overviewDesktop = path.join(screenshotDir, 'overview-1280.png')
  const overview360 = path.join(screenshotDir, 'overview-360.png')
  const overview480 = path.join(screenshotDir, 'overview-480.png')
  if (fs.existsSync(overviewDesktop)) {
    report.push('![Overview desktop 1280x900 (default)](screenshots/overview-1280.png)')
  } else {
    report.push('- Missing overview-1280.png (run layout test)')
  }
  if (fs.existsSync(overview360)) {
    report.push('![Overview mobile 360x900](screenshots/overview-360.png)')
  } else {
    report.push('- Missing overview-360.png (run layout test)')
  }
  if (fs.existsSync(overview480)) {
    report.push('![Overview mobile 480x900](screenshots/overview-480.png)')
  } else {
    report.push('- Missing overview-480.png (run layout test)')
  }
  report.push('')
}

report.push('## Random UI Image')
const randomUiImage = copyRandomUiImage()
if (randomUiImage.error) {
  report.push(`- ${randomUiImage.error}`)
  if (randomUiImage.sourcePath) {
    report.push(`- Selected file: ${path.basename(randomUiImage.sourcePath)}`)
  }
  report.push('')
} else {
  const relPath = path.relative(reportDir, randomUiImage.destPath)
  report.push(`- Source dir: ${expandHomeDir(uiImageRoot)}`)
  report.push(`- Selected file: ${path.basename(randomUiImage.sourcePath)}`)
  report.push(`- Saved as: ${path.join('random-ui', randomUiImage.destName)}`)
  report.push(`![Random UI image](${relPath})`)
  report.push('')
}

report.push('## Extraction Flow Screenshots')
const extractionBundle = findLatestExtractionBundle()
if (!extractionBundle) {
  report.push('- No extraction-flow screenshot bundle found. Run the token data points test.')
  report.push('')
} else {
  const relBundle = path.relative(reportDir, extractionBundle)
  const bundleScreens = listExtractionScreens(extractionBundle)
  report.push(`- Latest bundle: ${relBundle}`)
  report.push(`- Screenshots: ${bundleScreens.length}`)
  const highlightFiles = extractionHighlights
    .map((label) => `${extractionPrefix}${label}.png`)
    .filter((file) => bundleScreens.includes(file))
  if (!highlightFiles.length) {
    report.push('- No highlight screenshots found in bundle.')
  } else {
    highlightFiles.forEach((file) => {
      const relPath = path.relative(reportDir, path.join(extractionBundle, file))
      const alt = formatExtractionAlt(file)
      report.push(`![${alt}](${relPath})`)
    })
  }
  report.push('')
}

report.push('## Contrast Sweep (Legacy Panels)')
const bgColor = '#fbfbf7'
const contrastFindings = legacyFiles.flatMap((file) => {
  const findings = extractGrayTextColors(file)
  return findings.map((finding) => {
    const ratio = contrastRatio(finding.value, bgColor)
    return {
      file,
      selector: finding.selector,
      line: finding.line,
      value: finding.value,
      ratio,
    }
  })
})

if (!contrastFindings.length) {
  report.push('- No hard-coded grayscale text colors found in legacy panel CSS.')
  report.push('')
} else {
  contrastFindings.forEach((finding) => {
    const ratio = finding.ratio ? finding.ratio.toFixed(2) : 'n/a'
    report.push(`- ${path.relative(rootDir, finding.file)}:${finding.line} ${finding.selector} color ${finding.value} contrast ${ratio}:1 on ${bgColor}`)
  })
  report.push('')
}

report.push('## Diagrams')
report.push('```mermaid')
report.push('flowchart TB')
report.push('  UploadPanel --> ExtractionPipeline --> Overview')
report.push('  Overview --> TokenTabs --> Export')
report.push('  Overview --> Diagnostics')
report.push('```')
report.push('')

fs.mkdirSync(reportDir, { recursive: true })
fs.writeFileSync(reportPath, report.join('\n'))

console.log(`UI summary report written to ${path.relative(rootDir, reportPath)}`)

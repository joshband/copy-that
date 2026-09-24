import { useEffect, useState } from 'react'
import { useExtractionState, phaseLabel } from '../features/extraction/state'
import { ApiClient } from '../api/client'
import { downloadTextFile } from '../utils/download'
import './ProjectTokenExport.css'

interface ProjectTokenExportProps {
  projectId: number | null
  colorCount: number
  spacingCount: number
  typographyCount: number
  shadowCount: number
  familyCounts?: Record<string, number>
  gradientCount?: number
}

type ExportKind = 'w3c' | 'css' | 'react' | 'tailwind' | 'guide-pack' | 'guide-html'

interface HonestyStrip {
  extract: number
  derive: number
  synth: number
  preset: number
  typeCoverage: Record<string, string>
  gradientIds: string[]
  brandName?: string
  snapshotHash?: string
}

const COVERAGE_ORDER = [
  'color',
  'dimension',
  'fontFamily',
  'fontWeight',
  'typography',
  'shadow',
  'gradient',
  'border',
  'strokeStyle',
  'number',
  'duration',
  'cubicBezier',
  'transition',
] as const

function coverageLabel(status: string): string {
  if (status === 'live') return 'extract'
  if (status === 'derive') return 'derive'
  if (status === 'synth') return 'synth'
  if (status === 'stub' || status === 'preset') return 'preset'
  return status
}

export function ProjectTokenExport({
  projectId,
  colorCount,
  spacingCount,
  typographyCount,
  shadowCount,
  gradientCount = 0,
  familyCounts,
}: ProjectTokenExportProps) {
  const phase = useExtractionState(s => s.phase)
  const [feedback, setFeedback] = useState<string | null>(null)
  const [busy, setBusy] = useState<ExportKind | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [honesty, setHonesty] = useState<HonestyStrip | null>(null)

  const available = familyCounts ?? { colors: colorCount, spacing: spacingCount, typography: typographyCount, shadows: shadowCount, gradients: gradientCount }
  const total = Object.values(available).reduce((sum, count) => sum + count, 0)
  const canExport = projectId != null && total > 0 && !['running', 'hydrating', 'failed'].includes(phase)

  useEffect(() => {
    if (projectId == null || total === 0) {
      setHonesty(null)
      return
    }
    let cancelled = false
    void ApiClient.exportGuidePack(projectId)
      .then((pack) => {
        if (cancelled) return
        const counts = pack?.meta?.source_counts ?? {}
        const foundations = pack?.foundations as
          | { gradients?: string[] }
          | undefined
        const brand = pack?.brand as { name?: string } | undefined
        setHonesty({
          extract: Number(counts.extract ?? 0),
          derive: Number(counts.derive ?? 0),
          synth: Number(counts.synth ?? 0),
          preset: Number(counts.preset ?? 0),
          typeCoverage: (pack?.meta?.type_coverage ?? {}) as Record<string, string>,
          gradientIds: Array.isArray(foundations?.gradients) ? foundations.gradients : [],
          brandName: typeof brand?.name === 'string' ? brand.name : undefined,
          snapshotHash:
            typeof pack?.meta?.token_snapshot_hash === 'string'
              ? pack.meta.token_snapshot_hash
              : undefined,
        })
      })
      .catch(() => {
        if (!cancelled) setHonesty(null)
      })
    return () => {
      cancelled = true
    }
  }, [projectId, total, gradientCount])

  const runExport = async (kind: ExportKind) => {
    if (projectId == null) {
      setError('Create a project and extract tokens before exporting.')
      return
    }
    setError(null)
    setFeedback(null)
    setBusy(kind)
    try {
      if (kind === 'w3c') {
        const data = await ApiClient.exportDesignTokensW3c(projectId)
        downloadTextFile(
          `copy-that-project-${projectId}.tokens.json`,
          JSON.stringify(data, null, 2),
          'application/json;charset=utf-8',
        )
      } else if (kind === 'css') {
        const data = await ApiClient.exportDesignTokensCss(projectId)
        downloadTextFile(
          data.filename || `copy-that-project-${projectId}.tokens.css`,
          data.content,
          'text/css;charset=utf-8',
        )
      } else if (kind === 'react') {
        const data = await ApiClient.exportDesignTokensReact(projectId)
        downloadTextFile(
          data.filename || `copy-that-project-${projectId}.tokens.theme.ts`,
          data.content,
          'text/typescript;charset=utf-8',
        )
      } else if (kind === 'tailwind') {
        const data = await ApiClient.exportDesignTokensTailwind(projectId)
        downloadTextFile(
          data.filename || `copy-that-project-${projectId}.tailwind.theme.js`,
          data.content,
          'text/javascript;charset=utf-8',
        )
      } else if (kind === 'guide-pack') {
        const data = await ApiClient.exportGuidePack(projectId)
        downloadTextFile(
          `copy-that-project-${projectId}.guide.pack.json`,
          JSON.stringify(data, null, 2),
          'application/json;charset=utf-8',
        )
      } else {
        const data = await ApiClient.exportGuideHtml(projectId)
        downloadTextFile(
          data.filename || `copy-that-project-${projectId}.guide.html`,
          data.content,
          'text/html;charset=utf-8',
        )
      }
      setFeedback('Download started. Check your browser downloads.')
    } catch (err) {
      const message =
        err && typeof err === 'object' && 'detail' in err
          ? String((err as { detail?: unknown }).detail)
          : err instanceof Error
            ? err.message
            : 'Export failed'
      setError(message)
    } finally {
      setBusy(null)
    }
  }

  const gradientStatus = honesty?.typeCoverage?.gradient
  const gradientCountDisplay =
    honesty?.gradientIds.length ?? (gradientCount > 0 ? gradientCount : 0)
  const gradientHonesty =
    gradientStatus === 'live' && gradientCountDisplay > 0
      ? `${gradientCountDisplay} extracted (preferred over synth)`
      : gradientCountDisplay > 0
        ? `${gradientCountDisplay} present · capability ${coverageLabel(gradientStatus ?? 'synth')}`
        : gradientStatus === 'live'
          ? 'CV extract available — upload runs gradient extract'
          : 'Synth color-pair fill when no extract ≥ 0.55'

  return (
    <div className="project-token-export">
      <header className="project-token-export__hero">
        <p className="project-token-export__eyebrow">Export</p>
        <h2 className="project-token-export__title">Tokens &amp; Design Guide</h2>
        <p className="project-token-export__lede">
          Download W3C DTCG tokens for implementation, or a Design Guide Pack — brand roles and
          foundations over the same graph, with honest live / derive / synth provenance.
        </p>
      </header>

      <div className="project-token-export__summary">
        <h3>Token snapshot</h3>
        <ul className="project-token-export__counts">
          <li>
            <strong>{colorCount}</strong> colors
          </li>
          <li>
            <strong>{spacingCount}</strong> spacing
          </li>
          <li>
            <strong>{typographyCount}</strong> typography
          </li>
          <li>
            <strong>{shadowCount}</strong> shadows
          </li>
          {(gradientCount > 0 || gradientCountDisplay > 0) && (
            <li>
              <strong>{gradientCount || gradientCountDisplay}</strong> gradients
            </li>
          )}
        </ul>
        {projectId == null ? (
          <p className="project-token-export__hint">Extract an image first to create a project.</p>
        ) : total === 0 ? (
          <p className="project-token-export__hint">No tokens yet for project #{projectId}.</p>
        ) : (
          <p className="project-token-export__hint">
            Project #{projectId}
            {honesty?.brandName ? ` · ${honesty.brandName}` : ''} — {total} tokens across {Object.values(available).filter(count => count > 0).length} families.
            {honesty?.snapshotHash ? (
              <>
                {' '}
                Snapshot <code>{honesty.snapshotHash}</code>
              </>
            ) : null}
          </p>
        )}

        {honesty != null && (
          <div
            className="project-token-export__honesty"
            aria-label="DTCG type honesty"
            data-testid="export-honesty-strip"
          >
            <div className="project-token-export__honesty-head">
              <p className="project-token-export__honesty-title">13-type fidelity</p>
              <p className="project-token-export__caption project-token-export__caption--inline">
                Source counts: extract {honesty.extract} · derive {honesty.derive} · synth{' '}
                {honesty.synth} · preset {honesty.preset}
              </p>
            </div>

            <div className="project-token-export__coverage" role="list">
              {COVERAGE_ORDER.map((typeName) => {
                const status = honesty.typeCoverage[typeName]
                if (!status) return null
                const kind = coverageLabel(status)
                return (
                  <span
                    key={typeName}
                    role="listitem"
                    className={`project-token-export__chip project-token-export__chip--${kind}`}
                    title={`${typeName}: ${kind}`}
                  >
                    <span className="project-token-export__chip-type">{typeName}</span>
                    <span className="project-token-export__chip-status">{kind}</span>
                  </span>
                )
              })}
            </div>

            <p className="project-token-export__gradient-note" data-testid="export-gradient-honesty">
              Gradients: {gradientHonesty}. Extensions use <code>com.copythat.*</code> (source,
              confidence, provenance) — no invented DTCG types.
            </p>
          </div>
        )}
      </div>

      <p className="project-token-export__hint">{phaseLabel[phase]} · Available families: {Object.entries(available).filter(([, count]) => count > 0).map(([name]) => name).join(', ') || 'none'}</p>
      {feedback && <p role="status">{feedback}</p>}
      {error != null && (
        <div className="project-token-export__error" role="alert">
          {error}
        </div>
      )}

      <section className="project-token-export__guide" aria-labelledby="guide-pack-heading">
        <div className="project-token-export__guide-copy">
          <p className="project-token-export__eyebrow">Design Guide Pack</p>
          <h3 id="guide-pack-heading">Brand guide over your token graph</h3>
          <p className="project-token-export__caption">
            Structured JSON for tooling, plus a self-contained HTML guide you can open offline —
            foundations, illustrative components, and application notes. Not new <code>$type</code>s.
          </p>
        </div>
        <div className="project-token-export__guide-actions">
          <button
            type="button"
            className="project-token-export__btn project-token-export__btn--guide"
            disabled={!canExport || busy !== null}
            onClick={() => void runExport('guide-html')}
            data-testid="export-guide-html"
          >
            {busy === 'guide-html' ? 'Preparing…' : 'Download Guide HTML'}
          </button>
          <button
            type="button"
            className="project-token-export__btn project-token-export__btn--secondary"
            disabled={!canExport || busy !== null}
            onClick={() => void runExport('guide-pack')}
            data-testid="export-guide-pack"
          >
            {busy === 'guide-pack' ? 'Preparing…' : 'Download Guide Pack JSON'}
          </button>
        </div>
      </section>

      <section className="project-token-export__actions" aria-labelledby="impl-export-heading">
        <h3 id="impl-export-heading">Implementation downloads</h3>
        <p className="project-token-export__caption">
          W3C JSON preserves token structure and provenance. CSS provides custom properties. React theme provides a typed theme object. Tailwind provides theme configuration. Exports may include labelled derived or preset values.
        </p>
        <div className="project-token-export__buttons">
          <button
            type="button"
            className="project-token-export__btn"
            disabled={!canExport || busy !== null}
            onClick={() => void runExport('w3c')}
          >
            {busy === 'w3c' ? 'Preparing…' : 'W3C JSON'}
          </button>
          <button
            type="button"
            className="project-token-export__btn project-token-export__btn--secondary"
            disabled={!canExport || busy !== null}
            onClick={() => void runExport('css')}
          >
            {busy === 'css' ? 'Preparing…' : 'CSS'}
          </button>
          <button
            type="button"
            className="project-token-export__btn project-token-export__btn--secondary"
            disabled={!canExport || busy !== null}
            onClick={() => void runExport('react')}
          >
            {busy === 'react' ? 'Preparing…' : 'React theme'}
          </button>
          <button
            type="button"
            className="project-token-export__btn project-token-export__btn--secondary"
            disabled={!canExport || busy !== null}
            onClick={() => void runExport('tailwind')}
          >
            {busy === 'tailwind' ? 'Preparing…' : 'Tailwind'}
          </button>
        </div>
      </section>
    </div>
  )
}

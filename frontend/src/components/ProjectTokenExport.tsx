import { useState } from 'react'
import { ApiClient } from '../api/client'
import { downloadTextFile } from '../utils/download'
import './ProjectTokenExport.css'

interface ProjectTokenExportProps {
  projectId: number | null
  colorCount: number
  spacingCount: number
  typographyCount: number
  shadowCount: number
}

type ExportKind = 'w3c' | 'css' | 'react' | 'tailwind'

export function ProjectTokenExport({
  projectId,
  colorCount,
  spacingCount,
  typographyCount,
  shadowCount,
}: ProjectTokenExportProps) {
  const [busy, setBusy] = useState<ExportKind | null>(null)
  const [error, setError] = useState<string | null>(null)

  const total = colorCount + spacingCount + typographyCount + shadowCount
  const canExport = projectId != null && total > 0

  const runExport = async (kind: ExportKind) => {
    if (projectId == null) {
      setError('Create a project and extract tokens before exporting.')
      return
    }
    setError(null)
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
      } else {
        const data = await ApiClient.exportDesignTokensTailwind(projectId)
        downloadTextFile(
          data.filename || `copy-that-project-${projectId}.tailwind.theme.js`,
          data.content,
          'text/javascript;charset=utf-8',
        )
      }
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

  return (
    <div className="project-token-export">
      <div className="project-token-export__summary">
        <h3>Token snapshot</h3>
        <ul>
          <li>{colorCount} colors</li>
          <li>{spacingCount} spacing</li>
          <li>{typographyCount} typography</li>
          <li>{shadowCount} shadows</li>
        </ul>
        {projectId == null ? (
          <p className="project-token-export__hint">Extract an image first to create a project.</p>
        ) : total === 0 ? (
          <p className="project-token-export__hint">No tokens yet for project #{projectId}.</p>
        ) : (
          <p className="project-token-export__hint">
            Project #{projectId} — {total} core token families. W3C downloads may also include
            derived coverage tokens.
          </p>
        )}
      </div>

      <div className="project-token-export__actions">
        <h3>Download</h3>
        <p className="project-token-export__caption">
          W3C Design Tokens (JSON), CSS custom properties, React theme, and Tailwind config for the
          current project. W3C export may add derived/preset tokens for full DTCG type coverage.
        </p>
        {error != null && <div className="project-token-export__error">{error}</div>}
        <div className="project-token-export__buttons">
          <button
            type="button"
            className="project-token-export__btn"
            disabled={!canExport || busy !== null}
            onClick={() => void runExport('w3c')}
          >
            {busy === 'w3c' ? 'Preparing…' : 'Download W3C JSON'}
          </button>
          <button
            type="button"
            className="project-token-export__btn project-token-export__btn--secondary"
            disabled={!canExport || busy !== null}
            onClick={() => void runExport('css')}
          >
            {busy === 'css' ? 'Preparing…' : 'Download CSS'}
          </button>
          <button
            type="button"
            className="project-token-export__btn project-token-export__btn--secondary"
            disabled={!canExport || busy !== null}
            onClick={() => void runExport('react')}
          >
            {busy === 'react' ? 'Preparing…' : 'Download React theme'}
          </button>
          <button
            type="button"
            className="project-token-export__btn project-token-export__btn--secondary"
            disabled={!canExport || busy !== null}
            onClick={() => void runExport('tailwind')}
          >
            {busy === 'tailwind' ? 'Preparing…' : 'Download Tailwind'}
          </button>
        </div>
      </div>
    </div>
  )
}

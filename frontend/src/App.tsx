import { useEffect, useState } from 'react'
import './App.css'
import ImageUploader from './components/ImageUploader'
import ColorTokenDisplay from './components/ColorTokenDisplay'
import ShadowTokenList from './components/shadows/ShadowTokenList'
import './components/shadows/ShadowTokenList.css'
import type { ColorRampMap, ColorToken } from './types'

export default function App() {
  // Ensure global scroll isn’t disabled by other styles
  useEffect(() => {
    const originalBodyOverflow = document.body.style.overflowY
    const originalHtmlOverflow = document.documentElement.style.overflowY
    document.body.style.overflowY = 'auto'
    document.documentElement.style.overflowY = 'auto'
    return () => {
      document.body.style.overflowY = originalBodyOverflow
      document.documentElement.style.overflowY = originalHtmlOverflow
    }
  }, [])

  const [projectId, setProjectId] = useState<number | null>(null)
  const [colors, setColors] = useState<ColorToken[]>([])
  const [shadows, setShadows] = useState<any[]>([])
  const [spacingTokens, setSpacingTokens] = useState<any[]>([])
  const [typographyTokens, setTypographyTokens] = useState<any[]>([])
  const [ramps, setRamps] = useState<ColorRampMap>({})
  const [debugOverlay, setDebugOverlay] = useState<string | null>(null)
  const [error, setError] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)
  const [hasUpload, setHasUpload] = useState(false)

  const handleColorsExtracted = (extracted: ColorToken[]) => {
    setColors(extracted)
    setHasUpload(true)
  }

  const handleShadowsExtracted = (shadowTokens: any[]) => {
    setShadows(shadowTokens)
  }

  // Placeholder wiring for spacing/typography panels; can be connected to spacing/typography APIs later.
  const spacingEmptyState = (
    <div className="empty-subpanel">
      <div className="empty-icon">📐</div>
      <p className="empty-title">No spacing tokens yet</p>
      <p className="empty-subtitle">Run spacing extraction to populate this panel.</p>
      <button
        className="ghost-btn"
        onClick={() => document.getElementById('uploader-panel')?.scrollIntoView({ behavior: 'smooth' })}
      >
        Go to upload
      </button>
    </div>
  )

  const typographyEmptyState = (
    <div className="empty-subpanel">
      <div className="empty-icon">🔤</div>
      <p className="empty-title">No typography tokens yet</p>
      <p className="empty-subtitle">Wire up typography extraction to see styles here.</p>
      <button
        className="ghost-btn"
        onClick={() => document.getElementById('uploader-panel')?.scrollIntoView({ behavior: 'smooth' })}
      >
        Go to upload
      </button>
    </div>
  )

  const handleProjectCreated = (id: number) => {
    setProjectId(id)
  }

  const handleError = (message: string) => {
    setError(message)
  }

  const handleLoadingChange = (loading: boolean) => {
    setIsLoading(loading)
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="header-title">
            <h1>Copy That Playground</h1>
            {projectId != null && <span className="project-id">Project #{projectId}</span>}
          </div>
          {isLoading && (
            <div className="loading-chip" aria-live="polite">
              Processing image…
            </div>
          )}
        </div>
        {error && <div className="error-banner">{error}</div>}
      </header>

      <main className="app-main">
        <div className="primary-row">
          <section className="panel upload-panel" id="uploader-panel">
            <h2>Upload an image</h2>
            <p className="panel-subtitle">
              We’ll send it to the backend, stream the extraction, and render tokens below.
            </p>
            <ImageUploader
              projectId={projectId}
              onProjectCreated={handleProjectCreated}
              onColorExtracted={handleColorsExtracted}
              onSpacingExtracted={setSpacingTokens}
              onShadowsExtracted={handleShadowsExtracted}
              onRampsExtracted={setRamps}
              onDebugOverlay={setDebugOverlay}
              onError={handleError}
              onLoadingChange={handleLoadingChange}
            />
          </section>

          <section className="panel tokens-panel">
            <h2>Color tokens</h2>
            <p className="panel-subtitle">
              Browse the palette and details as soon as extraction completes.
            </p>
            {hasUpload && colors.length === 0 && !isLoading && (
              <div className="empty-state">
                <div className="empty-content">
                  <div className="empty-icon">⌛</div>
                  <p className="empty-title">No tokens yet</p>
                  <p className="empty-subtitle">Upload an image to see extracted colors</p>
                  <button
                    className="ghost-btn"
                    onClick={() => document.getElementById('uploader-panel')?.scrollIntoView({ behavior: 'smooth' })}
                  >
                    Go to upload
                  </button>
                </div>
              </div>
            )}
            {colors.length > 0 && <ColorTokenDisplay colors={colors} ramps={ramps} debugOverlay={debugOverlay ?? undefined} />}
            {!hasUpload && colors.length === 0 && (
              <div className="empty-state">
                <div className="empty-content">
                  <div className="empty-icon">🖼️</div>
                  <p className="empty-title">Drop an image to begin</p>
                  <p className="empty-subtitle">We’ll stream results from the backend</p>
                  <button
                    className="ghost-btn"
                    onClick={() => document.getElementById('uploader-panel')?.scrollIntoView({ behavior: 'smooth' })}
                  >
                    Start upload
                  </button>
                </div>
              </div>
            )}
          </section>
        </div>

        <div className="token-row">
          <section className="panel">
            <h2>Shadow tokens</h2>
            <p className="panel-subtitle">Elevation styles extracted or referenced.</p>
            {shadows.length === 0 ? (
              <div className="empty-subpanel">
                <div className="empty-icon">☁️</div>
                <p className="empty-title">No shadows extracted yet.</p>
                <p className="empty-subtitle">Run extraction to capture elevation styles.</p>
                <button
                  className="ghost-btn"
                  onClick={() => document.getElementById('uploader-panel')?.scrollIntoView({ behavior: 'smooth' })}
                >
                  Go to upload
                </button>
              </div>
            ) : (
              <ShadowTokenList shadows={shadows} />
            )}
          </section>

          <section className="panel">
            <h2>Spacing tokens</h2>
            <p className="panel-subtitle">Clustered spacing values and grid hints.</p>
            {spacingTokens.length === 0 ? (
              spacingEmptyState
            ) : (
              <ul className="token-list">
                {spacingTokens.map((t, idx) => (
                  <li key={idx}>
                    <strong>{t.name ?? `spacing.${idx + 1}`}</strong> — {t.value_px ?? t.value}px
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section className="panel">
            <h2>Typography tokens</h2>
            <p className="panel-subtitle">Font families, sizes, and roles.</p>
            {typographyTokens.length === 0 ? (
              typographyEmptyState
            ) : (
              <ul className="token-list">
                {typographyTokens.map((t, idx) => (
                  <li key={idx}>
                    <strong>{t.name ?? `typography.${idx + 1}`}</strong> — {t.fontFamily}{' '}
                    {t.fontSize?.value ? `${t.fontSize.value}${t.fontSize.unit}` : ''}
                  </li>
                ))}
              </ul>
            )}
          </section>
        </div>
      </main>
    </div>
  )
}

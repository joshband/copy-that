import { useEffect, useState } from 'react'
import './App.css'
import ImageUploader from './components/ImageUploader'
import ColorTokenDisplay from './components/ColorTokenDisplay'
import ShadowTokenList from './components/shadows/ShadowTokenList'
import './components/shadows/ShadowTokenList.css'
import type { ColorRampMap, ColorToken, SegmentedColor, SpacingExtractionResponse } from './types'

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
  const [spacingResult, setSpacingResult] = useState<SpacingExtractionResponse | null>(null)
  const [typographyTokens, setTypographyTokens] = useState<any[]>([])
  const [ramps, setRamps] = useState<ColorRampMap>({})
  const [segmentedPalette, setSegmentedPalette] = useState<SegmentedColor[] | null>(null)
  const [debugOverlay, setDebugOverlay] = useState<string | null>(null)
  const [showColorOverlay, setShowColorOverlay] = useState(false)
  const [showSpacingOverlay, setShowSpacingOverlay] = useState(false)
  const [error, setError] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)
  const [hasUpload, setHasUpload] = useState(false)

  const handleColorsExtracted = (extracted: ColorToken[]) => {
    setColors(extracted)
    setHasUpload(true)
    setShowColorOverlay(false)
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

  const gapDiagnostics = spacingResult?.cv_gap_diagnostics as
    | { dominant_gap?: number; aligned?: boolean }
    | undefined

  useEffect(() => {
    // Reset overlay toggle when new spacing result arrives
    setShowSpacingOverlay(false)
  }, [spacingResult?.debug_overlay])

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
              onSpacingExtracted={setSpacingResult}
              onShadowsExtracted={handleShadowsExtracted}
              onRampsExtracted={setRamps}
              onDebugOverlay={setDebugOverlay}
              onSegmentationExtracted={setSegmentedPalette}
              onError={handleError}
              onLoadingChange={handleLoadingChange}
            />
          </section>

          <section className="panel tokens-panel">
            <h2>Color tokens</h2>
            <p className="panel-subtitle">
              Browse the palette and details as soon as extraction completes.
            </p>
            {debugOverlay && (
              <div className="overlay-toggle color-overlay-toggle">
                <label className="switch">
                  <input
                    type="checkbox"
                    checked={showColorOverlay}
                    onChange={() => setShowColorOverlay((s) => !s)}
                  />
                  <span className="slider" />
                </label>
                <span className="overlay-label">
                  {showColorOverlay ? 'Hide color diagnostics' : 'Show color diagnostics'}
                </span>
              </div>
            )}
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
            {colors.length > 0 && (
              <ColorTokenDisplay
                colors={colors}
                ramps={ramps}
                segmentedPalette={segmentedPalette ?? undefined}
                debugOverlay={debugOverlay ?? undefined}
                showDebugOverlay={showColorOverlay}
              />
            )}
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

          <section className="panel spacing-panel">
            <div className="spacing-panel-heading">
              <h2>
                Spacing tokens <span className="new-feature-badge">NEW</span>
              </h2>
              <p className="panel-subtitle">
                Clustered spacing values, baselines, padding heuristics, and inferred grids—powered
                by the CV pipeline.
              </p>
            </div>
            {!spacingResult && spacingEmptyState}
            {spacingResult && (
              <div className="spacing-content">
                <div className="spacing-summary-grid">
                  <div className="spacing-stat-card">
                    <span className="stat-label">Base unit</span>
                    <span className="stat-value">{spacingResult.base_unit}px</span>
                    <span className="stat-meta">
                      {(spacingResult.base_alignment?.mode ?? 'inferred') === 'no-expected'
                        ? 'Inferred from gaps'
                        : spacingResult.base_alignment?.within_tolerance
                          ? 'Matches expected grid'
                          : 'Grid mismatch'}
                    </span>
                  </div>
                  <div className="spacing-stat-card">
                    <span className="stat-label">Scale system</span>
                    <span className="stat-value spacing-scale-chip">{spacingResult.scale_system}</span>
                    <span className="stat-meta">
                      {Math.round((spacingResult.grid_compliance ?? 0) * 100)}% grid aligned
                    </span>
                  </div>
                  <div className="spacing-stat-card">
                    <span className="stat-label">Unique values</span>
                    <span className="stat-value">{spacingResult.unique_values.length}</span>
                    <span className="stat-meta">
                      Range {spacingResult.min_spacing}px – {spacingResult.max_spacing}px
                    </span>
                  </div>
                  {gapDiagnostics?.dominant_gap != null && (
                    <div className="spacing-stat-card">
                      <span className="stat-label">Dominant gap</span>
                      <span className="stat-value">
                        {Math.round(gapDiagnostics.dominant_gap)}px
                      </span>
                      <span className="stat-meta">
                        {gapDiagnostics.aligned ? 'Aligned to grid' : 'Needs review'}
                      </span>
                    </div>
                  )}
                </div>

                <div className="spacing-diagnostics-grid">
                  {spacingResult.baseline_spacing && (
                    <div className="spacing-card">
                      <div className="spacing-card-header">
                        <h3>Baseline rhythm</h3>
                        <span className="new-feature-badge">NEW</span>
                      </div>
                      <p className="spacing-card-value">
                        {spacingResult.baseline_spacing.value_px}px
                        <span className="stat-meta">
                          Confidence {(spacingResult.baseline_spacing.confidence * 100).toFixed(0)}%
                        </span>
                      </p>
                      <p className="spacing-card-text">
                        Estimated vertical rhythm derived from detected baseline clusters.
                      </p>
                    </div>
                  )}
                  {spacingResult.grid_detection && (
                    <div className="spacing-card">
                      <div className="spacing-card-header">
                        <h3>Grid detection</h3>
                        <span className="new-feature-badge">NEW</span>
                      </div>
                      <ul className="spacing-card-list">
                        <li>
                          Columns: <strong>{spacingResult.grid_detection.columns ?? '—'}</strong>
                        </li>
                        <li>
                          Gutter: <strong>{spacingResult.grid_detection.gutter_px ?? '—'}px</strong>
                        </li>
                        <li>
                          Margins:{' '}
                          <strong>
                            {spacingResult.grid_detection.margin_left ?? '—'}px /{' '}
                            {spacingResult.grid_detection.margin_right ?? '—'}px
                          </strong>
                        </li>
                        <li>
                          Confidence:{' '}
                          <strong>
                            {Math.round((spacingResult.grid_detection.confidence ?? 0) * 100)}%
                          </strong>
                        </li>
                      </ul>
                    </div>
                  )}
                  {spacingResult.debug_overlay && (
                    <div className="spacing-card overlay-card">
                      <div className="spacing-card-header">
                        <h3>Detection overlay</h3>
                        <span className="new-feature-badge">NEW</span>
                      </div>
                      <p className="spacing-card-text">
                        Visual QA of detected components, baselines, and guides. Toggle to compare
                        against the source preview.
                      </p>
                      <div className="overlay-toggle">
                        <label className="switch">
                          <input
                            type="checkbox"
                            checked={showSpacingOverlay}
                            onChange={() => setShowSpacingOverlay((s) => !s)}
                          />
                          <span className="slider" />
                        </label>
                        <span className="overlay-label">
                          {showSpacingOverlay ? 'Hide overlay' : 'Show overlay'}
                        </span>
                      </div>
                      {showSpacingOverlay && (
                        <img
                          className="overlay-image"
                          src={`data:image/png;base64,${spacingResult.debug_overlay}`}
                          alt="Spacing debug overlay"
                        />
                      )}
                    </div>
                  )}
                </div>

                <div className="spacing-token-grid">
                  {spacingResult.tokens.map((token) => (
                    <div
                      key={token.name ?? `spacing-${token.value_px}`}
                      className="spacing-token-card"
                    >
                      <div className="spacing-token-value">
                        {token.value_px}px
                        <span className="spacing-token-subvalue">{token.value_rem}rem</span>
                      </div>
                      <div className="spacing-token-meta">
                        <strong>{token.name}</strong>
                        <span>{token.semantic_role ?? 'layout'}</span>
                        {token.tailwind_class && (
                          <span className="spacing-token-chip">{token.tailwind_class}</span>
                        )}
                        <span className={token.grid_aligned ? 'spacing-badge success' : 'spacing-badge'}>
                          {token.grid_aligned ? 'Grid aligned' : 'Off-grid'}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>

                {spacingResult.component_spacing_metrics?.length ? (
                  <div className="spacing-card full-width">
                    <div className="spacing-card-header">
                      <h3>Component padding & margin insights</h3>
                      <span className="new-feature-badge">NEW</span>
                    </div>
                    <div className="spacing-component-grid">
                      {[...spacingResult.component_spacing_metrics]
                        .sort(
                          (a, b) =>
                            (b.padding_confidence ?? 0) - (a.padding_confidence ?? 0)
                        )
                        .slice(0, 3)
                        .map((metric, metricIdx) => (
                          <div key={metric.index ?? metricIdx} className="component-card">
                            <div className="component-card-header">
                              Component #{(metric.index ?? 0) + 1}
                              <span className="spacing-badge">
                                {(metric.padding_confidence ?? 0).toFixed(2)}
                                &nbsp;confidence
                              </span>
                            </div>
                            <div className="component-card-body">
                              <div>
                                <strong>Padding:</strong>{' '}
                                {metric.padding
                                  ? `${metric.padding.top}px / ${metric.padding.right}px / ${metric.padding.bottom}px / ${metric.padding.left}px`
                                  : '—'}
                              </div>
                              <div>
                                <strong>Margins:</strong>{' '}
                                {metric.margin
                                  ? `${metric.margin.top}px / ${metric.margin.right}px / ${metric.margin.bottom}px / ${metric.margin.left}px`
                                  : '—'}
                              </div>
                              {metric.neighbor_gap != null && (
                                <div>
                                  <strong>Neighbor gap:</strong> {Math.round(metric.neighbor_gap)}px
                                </div>
                              )}
                            </div>
                          </div>
                        ))}
                    </div>
                  </div>
                ) : null}
              </div>
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

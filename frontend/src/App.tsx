import { useEffect, useState } from 'react'
import './App.css'
import ImageUploader from './components/ImageUploader'
import ColorTokenDisplay from './components/ColorTokenDisplay'
import ShadowTokenList from './components/shadows/ShadowTokenList'
import './components/shadows/ShadowTokenList.css'
import DiagnosticsPanel from './components/DiagnosticsPanel'
import TokenInspector from './components/TokenInspector'
import TokenGraphPanel from './components/TokenGraphPanel'
import ColorGraphPanel from './components/ColorGraphPanel'
import SpacingScalePanel from './components/SpacingScalePanel'
import SpacingGraphList from './components/SpacingGraphList'
import RelationsDebugPanel from './components/RelationsDebugPanel'
import ShadowInspector from './components/ShadowInspector'
import TypographyInspector from './components/TypographyInspector'
import ColorsTable from './components/ColorsTable'
import SpacingTable from './components/SpacingTable'
import TypographyCards from './components/TypographyCards'
import RelationsTable from './components/RelationsTable'
import { useTokenGraphStore } from './store/tokenGraphStore'
import { useTokenStore } from './store/tokenStore'
import type { ColorRampMap, ColorToken, SegmentedColor, SpacingExtractionResponse } from './types'

const hexToRgb = (hex: string) => {
  const normalized = hex.replace('#', '')
  const int = parseInt(normalized.length === 3 ? normalized.repeat(2) : normalized, 16)
  const r = (int >> 16) & 255
  const g = (int >> 8) & 255
  const b = int & 255
  return `rgb(${r}, ${g}, ${b})`
}

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
  const [ramps, setRamps] = useState<ColorRampMap>({})
  const [segmentedPalette, setSegmentedPalette] = useState<SegmentedColor[] | null>(null)
  const [debugOverlay, setDebugOverlay] = useState<string | null>(null)
  const [showColorOverlay, setShowColorOverlay] = useState(false)
  const [showSpacingOverlay, setShowSpacingOverlay] = useState(false)
  const [showDebug, setShowDebug] = useState(false)
  const [showColorTable, setShowColorTable] = useState(false)
  const [activeTab, setActiveTab] = useState<'overview' | 'colors' | 'spacing' | 'typography' | 'shadows' | 'relations' | 'raw'>('overview')
  const [error, setError] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)
  const [hasUpload, setHasUpload] = useState(false)
  const warnings = spacingResult?.warnings ?? []
  const { load, legacyColors, legacySpacing } = useTokenGraphStore()
  const graphStoreState = useTokenGraphStore()
  const graphColors = legacyColors()
  const graphSpacing = legacySpacing()
  const typographyTokens = useTokenGraphStore((s) => s.typography)
  const spacingTokensFallback =
    spacingResult?.tokens?.map((t) => ({
      id: t.name ?? `spacing-${t.value_px}`,
      name: t.name,
      value_px: t.value_px,
      value_rem: t.value_rem,
      multiplier: (t as any).multiplier,
    })) ?? []
  const colorDisplay: ColorToken[] = (graphColors.length
    ? graphColors.map((c) => ({
        id: c.id,
        hex: c.hex,
        rgb: hexToRgb(c.hex),
        name: c.name ?? c.id,
        confidence: c.confidence ?? 0.5,
      }))
    : colors)

  // Keep legacy tokenStore in sync for components/tests that still read it
  useEffect(() => {
    useTokenStore.getState().setTokens(colorDisplay)
  }, [colorDisplay])

  const handleColorsExtracted = (extracted: ColorToken[]) => {
    setColors(extracted)
    setHasUpload(true)
    setShowColorOverlay(false)
    if (projectId != null) {
      load(projectId).catch(() => null)
    }
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
    load(id).catch(() => null)
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

  const colorCount = graphColors.length || colorDisplay.length
  const aliasCount =
    graphColors.length > 0
      ? graphColors.filter((c) => c.isAlias).length
      : 0
  const spacingCount = graphSpacing.length || spacingTokensFallback.length
  const multiplesCount =
    graphSpacing.length > 0
      ? graphSpacing.filter((s) => s.multiplier != null).length
      : spacingTokensFallback.filter((s) => s.multiplier != null).length

  const summaryBadges = [
    { label: 'Colors', value: colorCount },
    { label: 'Aliases', value: aliasCount },
    { label: 'Spacing', value: spacingCount },
    { label: 'Multiples', value: multiplesCount },
    { label: 'Typography', value: graphStoreState.typography.length },
    {
      label: 'Confidence',
      value:
        graphStoreState.typographyRecommendation?.confidence != null
          ? graphStoreState.typographyRecommendation.confidence.toFixed(2)
          : '—',
    },
  ]

  const renderColors = () => (
    <section className="panel tokens-panel">
      <h2>Color tokens</h2>
      <p className="panel-kicker">Extracted tokens</p>
      <p className="panel-subtitle">
        Browse the palette and details as soon as extraction completes.
      </p>
      {(graphColors.length > 0 || colors.length > 0) && (
        <>
          <ColorTokenDisplay
            colors={colorDisplay}
            ramps={ramps}
            segmentedPalette={segmentedPalette ?? undefined}
            debugOverlay={debugOverlay ?? undefined}
            showDebugOverlay={showColorOverlay}
          />
          <div className="toggle-row">
            <label className="muted">
              <input
                type="checkbox"
                checked={showColorTable}
                onChange={(e) => setShowColorTable(e.target.checked)}
              />{' '}
              Show compact table
            </label>
          </div>
          {showColorTable && (
            <ColorsTable
              fallback={colorDisplay.map((c) => ({
                id: String(c.id ?? c.hex),
                hex: c.hex,
                name: c.name,
                role: (c as any).role,
              }))}
            />
          )}
        </>
      )}
      {!hasUpload && graphColors.length === 0 && colors.length === 0 && (
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
  )

  const renderSpacing = () => (
    <section className="panel">
      <div className="spacing-panel-heading">
        <h2>
          Spacing tokens
        </h2>
        <div className="panel-cta">
          <button
            className="ghost-btn"
            onClick={() => document.getElementById('uploader-panel')?.scrollIntoView({ behavior: 'smooth' })}
          >
            Go to upload
          </button>
        </div>
        <p className="panel-subtitle">
          Clustered spacing values, baselines, padding heuristics, and inferred grids—powered by the CV pipeline.
        </p>
      </div>
      {graphSpacing.length === 0 && !spacingResult ? spacingEmptyState : null}
      <SpacingTable
        fallback={
          spacingResult?.tokens?.map((t) => ({
            id: t.name ?? `spacing-${t.value_px}`,
            name: t.name,
            value_px: t.value_px,
            value_rem: t.value_rem,
            multiplier: (t as any).multiplier,
          })) ?? []
        }
      />
      {spacingResult && (
        <>
          <SpacingScalePanel />
          <SpacingGraphList />
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
          </div>
        </>
      )}
    </section>
  )

  const renderTypography = () => (
    <section className="panel">
      <h2>Typography tokens</h2>
      <p className="panel-subtitle">Font families, sizes, and roles.</p>
      {typographyTokens.length === 0 ? typographyEmptyState : (
        <>
          <TypographyCards />
          <TypographyInspector />
        </>
      )}
    </section>
  )

  const renderShadows = () => (
    <section className="panel">
      <h2>Shadow tokens</h2>
      <p className="panel-subtitle">Elevation styles extracted or referenced.</p>
      {graphStoreState.shadows.length === 0 && shadows.length === 0 ? (
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
        <>
          <ShadowInspector />
          {shadows.length > 0 && <ShadowTokenList shadows={shadows} />}
        </>
      )}
    </section>
  )

  const renderRelations = () => (
    <section className="panel">
      <h2>Relations</h2>
      <p className="panel-subtitle">Alias, multiple, and compose relations from the graph.</p>
      <RelationsTable />
      <RelationsDebugPanel />
    </section>
  )

  const renderRaw = () => (
    <section className="panel diagnostics-wrapper">
      <details open>
        <summary>Diagnostics</summary>
        <DiagnosticsPanel
          colors={colorDisplay}
          spacingResult={spacingResult}
          spacingOverlay={spacingResult?.debug_overlay ?? null}
          colorOverlay={debugOverlay}
          segmentedPalette={segmentedPalette}
          showAlignment={showDebug}
          showPayload={showDebug}
        />
      </details>
      {spacingResult?.component_spacing_metrics?.length ? (
        <details>
          <summary>Spacing inspector</summary>
          <TokenInspector
            spacingResult={spacingResult}
            overlayBase64={spacingResult.debug_overlay ?? debugOverlay ?? null}
            colors={colorDisplay}
            segmentedPalette={segmentedPalette}
            showOverlay={showDebug}
          />
        </details>
      ) : null}
      {spacingResult?.token_graph ? (
        <details>
          <summary>Token graph</summary>
          <TokenGraphPanel spacingResult={spacingResult} />
        </details>
      ) : null}
    </section>
  )

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
        <div className="header-title">
          <h1>Copy That Playground</h1>
          {projectId != null && <span className="project-id">Project #{projectId}</span>}
        </div>
        <div className="header-actions">
            {isLoading && (
              <div className="loading-chip small" aria-live="polite">
                Processing image…
              </div>
            )}
            <span className="overlay-label">{showDebug ? 'Debug on' : 'Debug off'}</span>
            <label className="switch">
              <input
                type="checkbox"
                checked={showDebug}
                onChange={() => setShowDebug((s) => !s)}
              />
              <span className="slider" />
            </label>
          </div>
        </div>
        {error && <div className="error-banner">{error}</div>}
        {!error && warnings?.length ? (
          <div className="warning-banner" role="status" aria-live="polite">
            <strong>Heads up:</strong> {warnings.join(' ')}
          </div>
        ) : null}
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

          <section className="panel">
            <div className="summary-bar">
              {summaryBadges.map((item) => (
                <div key={item.label} className="summary-chip">
                  <span className="summary-label">{item.label}</span>
                  <span className="summary-value">{item.value}</span>
                </div>
              ))}
            </div>
            <div className="tab-row">
              {['overview', 'colors', 'spacing', 'typography', 'shadows', 'relations', 'raw'].map((tab) => (
                <button
                  key={tab}
                  className={`tab-button ${activeTab === tab ? 'active' : ''}`}
                  onClick={() => setActiveTab(tab as typeof activeTab)}
                >
                  {tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </div>

            {activeTab === 'overview' && (
              <div className="graph-panels">
                <ColorGraphPanel />
                <SpacingScalePanel />
                <SpacingGraphList />
                <div className="overview-summary">
                  <h3>Snapshot</h3>
                  <p className="muted">
                    {colorCount} colors ({aliasCount} aliases) · {spacingCount} spacing tokens ({multiplesCount} multiples) · {graphStoreState.typography.length} typography tokens
                  </p>
                  {graphStoreState.typographyRecommendation?.confidence != null && (
                    <p className="muted">
                      Typography confidence: {graphStoreState.typographyRecommendation.confidence.toFixed(2)}
                    </p>
                  )}
                </div>
              </div>
            )}
            {activeTab === 'colors' && renderColors()}
            {activeTab === 'spacing' && renderSpacing()}
            {activeTab === 'typography' && renderTypography()}
            {activeTab === 'shadows' && renderShadows()}
            {activeTab === 'relations' && renderRelations()}
            {activeTab === 'raw' && renderRaw()}
          </section>
        </div>
      </main>
    </div>
  )
}

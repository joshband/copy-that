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

  const summaryBadges = [
    { label: 'Colors', value: graphStoreState.colors.length },
    { label: 'Aliases', value: graphStoreState.colors.filter((c) => c.isAlias).length },
    { label: 'Spacing', value: graphStoreState.spacing.length },
    { label: 'Multiples', value: graphStoreState.spacing.filter((s) => s.multiplier != null).length },
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
      <ColorsTable />
      {(graphColors.length > 0 || colors.length > 0) && (
        <ColorTokenDisplay
          colors={colorDisplay}
          ramps={ramps}
          segmentedPalette={segmentedPalette ?? undefined}
          debugOverlay={debugOverlay ?? undefined}
          showDebugOverlay={showColorOverlay}
        />
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
          Spacing tokens <span className="new-feature-badge">NEW</span>
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
      {!spacingResult && spacingEmptyState}
      {spacingResult && (
        <>
          <SpacingTable />
          <SpacingScalePanel />
          <SpacingGraphList />
        </>
      )}
    </section>
  )

  const renderTypography = () => (
    <section className="panel">
      <h2>Typography tokens</h2>
      <p className="panel-subtitle">Font families, sizes, and roles.</p>
      {typographyTokens.length === 0 ? typographyEmptyState : <TypographyCards />}
    </section>
  )

  const renderShadows = () => (
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
      <ShadowInspector />
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
      <DiagnosticsPanel
        colors={colorDisplay}
        spacingResult={spacingResult}
        spacingOverlay={spacingResult?.debug_overlay ?? null}
        colorOverlay={debugOverlay}
        segmentedPalette={segmentedPalette}
        showAlignment={showDebug}
        showPayload={showDebug}
      />
      {spacingResult?.component_spacing_metrics?.length ? (
        <TokenInspector
          spacingResult={spacingResult}
          overlayBase64={spacingResult.debug_overlay ?? debugOverlay ?? null}
          colors={colorDisplay}
          segmentedPalette={segmentedPalette}
          showOverlay={showDebug}
        />
      ) : null}
      {spacingResult?.token_graph ? <TokenGraphPanel spacingResult={spacingResult} /> : null}
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
            <label className="switch">
              <input
                type="checkbox"
                checked={showDebug}
                onChange={() => setShowDebug((s) => !s)}
              />
              <span className="slider" />
            </label>
            <span className="overlay-label">{showDebug ? 'Debug on' : 'Debug off'}</span>
          </div>
          {isLoading && (
            <div className="loading-chip" aria-live="polite">
              Processing image…
            </div>
          )}
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

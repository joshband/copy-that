import { useEffect, useState } from 'react'
import './App.css'
import { ImageUploader } from './components/image-uploader'
import { ExtractionProgressBar } from './components/ui/progress/ExtractionProgressBar'
import ColorTokenDisplay from './features/visual-extraction/components/color/ColorTokenDisplay'
import ShadowTokenList from './features/visual-extraction/components/shadow/shadows/ShadowTokenList'
import './features/visual-extraction/components/shadow/shadows/ShadowTokenList.css'
import LightingAnalyzer from './components/LightingAnalyzer'
import { DiagnosticsPanel } from './components/diagnostics-panel'
import { TokenInspector } from './components/token-inspector'
import TokenGraphPanel from './components/TokenGraphPanel'
import ColorGraphPanel from './features/visual-extraction/components/color/ColorGraphPanel'
import SpacingScalePanel from './features/visual-extraction/components/spacing/SpacingScalePanel'
import SpacingGraphList from './features/visual-extraction/components/spacing/SpacingGraphList'
import SpacingRuler from './features/visual-extraction/components/spacing/SpacingRuler'
import SpacingGapDemo from './features/visual-extraction/components/spacing/SpacingGapDemo'
import SpacingDetailCard from './features/visual-extraction/components/spacing/SpacingDetailCard'
import SpacingResponsivePreview from './features/visual-extraction/components/spacing/SpacingResponsivePreview'
import RelationsDebugPanel from './components/RelationsDebugPanel'
import ShadowInspector from './features/visual-extraction/components/shadow/ShadowInspector'
import TypographyInspector from './features/visual-extraction/components/typography/TypographyInspector'
import { TypographyDetailCard } from './features/visual-extraction/components/typography/TypographyDetailCard'
import FontFamilyShowcase from './features/visual-extraction/components/typography/FontFamilyShowcase'
import FontSizeScale from './features/visual-extraction/components/typography/FontSizeScale'
import ColorsTable from './features/visual-extraction/components/color/ColorsTable'
import SpacingTable from './features/visual-extraction/components/spacing/SpacingTable'
import TypographyCards from './features/visual-extraction/components/typography/TypographyCards'
import RelationsTable from './components/RelationsTable'
import { StreamingMetricsOverview } from './components/MetricsOverview'
import { OverviewNarrative } from './components/overview-narrative'
import { TokenGraphDemo } from './shared'
import { useTokenGraphStore } from './store/tokenGraphStore'
import { useTokenStore } from './store/tokenStore'
import { createInitialStages, updateStage, type PipelineStage } from './types/pipeline'
import type {
  ColorRampMap,
  ColorToken,
  SegmentedColor,
  SpacingExtractionResponse,
  SpacingTokenResponse,
  ShadowToken,
  TypographyToken,
  LightingAnalysis
} from './types'

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
  const [shadows, setShadows] = useState<ShadowToken[]>([])
  const [typography, setTypography] = useState<TypographyToken[]>([])
  const [lighting, setLighting] = useState<LightingAnalysis | null>(null)
  const [currentImageBase64, setCurrentImageBase64] = useState<string>('')
  const [spacingResult, setSpacingResult] = useState<SpacingExtractionResponse | null>(null)
  const [ramps, setRamps] = useState<ColorRampMap>({})
  const [segmentedPalette, setSegmentedPalette] = useState<SegmentedColor[] | null>(null)
  const [paletteSummary, setPaletteSummary] = useState<string | null>(null)
  const [debugOverlay, setDebugOverlay] = useState<string | null>(null)
  const [showColorOverlay, setShowColorOverlay] = useState(false)
  const [showSpacingOverlay, setShowSpacingOverlay] = useState(false)
  const [showDebug, setShowDebug] = useState(false)
  const [showColorTable, setShowColorTable] = useState(false)
  const [activeTab, setActiveTab] = useState<'overview' | 'colors' | 'spacing' | 'typography' | 'shadows' | 'lighting' | 'relations' | 'raw'>('overview')
  const [error, setError] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)
  const [hasUpload, setHasUpload] = useState(false)
  const [extractionProgress, setExtractionProgress] = useState(0)
  const [extractionStartTime, setExtractionStartTime] = useState<number | null>(null)
  const [metricsRefreshTrigger, setMetricsRefreshTrigger] = useState(0)
  const [pipelineStages, setPipelineStages] = useState<PipelineStage[]>(createInitialStages())
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
      multiplier: (t as SpacingTokenResponse & { multiplier?: number }).multiplier,
    })) ?? []
  const colorDisplay: ColorToken[] = (colors.length > 0
    ? colors
    : graphColors.length > 0
    ? graphColors.map((c) => {
        // Note: legacyColors() doesn't include raw W3C token metadata
        // Only basic fields are available: id, hex, name, confidence
        return {
          id: c.id,
          hex: c.hex,
          rgb: hexToRgb(c.hex),
          name: c.name ?? c.id,
          confidence: c.confidence ?? 0.5,
        } as ColorToken
      })
    : [])

  // Keep legacy tokenStore in sync for components/tests that still read it
  useEffect(() => {
    useTokenStore.getState().setTokens(colorDisplay)
  }, [colorDisplay])

  // Removed auto-load effect - was loading before extraction completed
  // Graph now loads 2 seconds after color extraction (see handleColorsExtracted)

  const handleColorsExtracted = (extracted: ColorToken[]) => {
    setColors(extracted)
    setHasUpload(true)
    setShowColorOverlay(false)
    setMetricsRefreshTrigger(prev => prev + 1)

    // Mark color extraction as complete
    setPipelineStages(prev => updateStage(prev, 'colors', { status: 'complete', endTime: Date.now() }))

    // DISABLED: Auto-loading graph causes race condition with stale database data
    // The database may not have fresh colors yet, or may have old data from previous extraction
    // User can manually load graph from Relations tab when needed
    // if (projectId != null) {
    //   console.log('⏳ Waiting 2s for colors to be saved to database...')
    //   setTimeout(() => {
    //     console.log('🔄 Loading token graph after extraction complete...')
    //     load(projectId)
    //       .then(() => console.log('✅ Token graph loaded with colors!'))
    //       .catch(err => console.error('❌ Token graph load failed:', err))
    //   }, 2000)
    // }
    console.log('✅ Colors extracted! Graph auto-load disabled to prevent stale data overwrite.')
  }

  const handleSpacingExtracted = (result: SpacingExtractionResponse | null) => {
    setSpacingResult(result)
    setMetricsRefreshTrigger(prev => prev + 1)
    // Mark spacing extraction as complete
    setPipelineStages(prev => updateStage(prev, 'spacing', { status: 'complete', endTime: Date.now() }))
    // Spacing extraction happens in parallel - graph will load after colors complete
  }

  const handleShadowsExtracted = (shadowTokens: ShadowToken[]) => {
    setShadows(shadowTokens)
    setMetricsRefreshTrigger(prev => prev + 1)
    // Mark shadow extraction as complete
    setPipelineStages(prev => updateStage(prev, 'shadows', { status: 'complete', endTime: Date.now() }))
  }

  const handleTypographyExtracted = (typographyTokens: TypographyToken[]) => {
    setTypography(typographyTokens)
    setMetricsRefreshTrigger(prev => prev + 1)
    // Mark typography extraction as complete
    setPipelineStages(prev => updateStage(prev, 'typography', { status: 'complete', endTime: Date.now() }))
    // DISABLED: Auto-loading graph causes race condition with stale database data
    // if (projectId != null) {
    //   load(projectId).catch(() => null)
    // }
  }

  const handleSpacingStarted = () => {
    setPipelineStages(prev => updateStage(prev, 'spacing', { status: 'running', startTime: Date.now() }))
  }

  const handleShadowsStarted = () => {
    setPipelineStages(prev => updateStage(prev, 'shadows', { status: 'running', startTime: Date.now() }))
  }

  const handleTypographyStarted = () => {
    setPipelineStages(prev => updateStage(prev, 'typography', { status: 'running', startTime: Date.now() }))
  }

  const handlePaletteSummaryExtracted = (summary: string | null) => {
    setPaletteSummary(summary)
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
    console.log('✅ Project created:', id)
    setProjectId(id)
    // Don't load graph yet - wait for extraction to complete
  }

  const handleError = (message: string) => {
    setError(message)
  }

  const handleLoadingChange = (loading: boolean) => {
    setIsLoading(loading)
    if (loading) {
      // Reset pipeline stages when extraction starts
      setPipelineStages(prev => {
        const reset = createInitialStages()
        // Mark color extraction as running immediately
        return updateStage(reset, 'colors', { status: 'running', startTime: Date.now() })
      })
    }
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
      ? graphColors.filter((c: any) => c.isAlias).length
      : 0
  const spacingCount = graphSpacing.length || spacingTokensFallback.length
  const multiplesCount =
    graphSpacing.length > 0
      ? graphSpacing.filter((s: any) => s.multiplier != null).length
      : spacingTokensFallback.filter((s: any) => s.multiplier != null).length

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
                role: c.role,
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
        <h2>Spacing tokens</h2>
        <p className="panel-subtitle">
          Clustered spacing values, baselines, padding heuristics, and inferred grids—powered by the CV pipeline.
        </p>
      </div>
      {graphSpacing.length === 0 && !spacingResult ? spacingEmptyState : (
        <div className="spacing-content">
          {/* 1. KEY METRICS - Quick overview */}
          {spacingResult && (
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
          )}

          {/* 2. VISUAL RULER - See the rhythm */}
          <SpacingRuler
            fallback={
              spacingResult?.tokens?.map((t) => ({
                id: t.name ?? `spacing-${t.value_px}`,
                name: t.name,
                value_px: t.value_px,
                value_rem: t.value_rem,
                multiplier: (t as SpacingTokenResponse & { multiplier?: number }).multiplier,
              })) ?? []
            }
          />

          {/* 3. GAP DEMO - Interactive preview */}
          <SpacingGapDemo
            fallback={
              spacingResult?.tokens?.map((t) => ({
                id: t.name ?? `spacing-${t.value_px}`,
                name: t.name,
                value_px: t.value_px,
                value_rem: t.value_rem,
                multiplier: (t as SpacingTokenResponse & { multiplier?: number }).multiplier,
              })) ?? []
            }
          />

          {/* 4. DETAIL CARDS - All metadata organized by category */}
          <SpacingDetailCard
            fallback={
              spacingResult?.tokens?.map((t) => ({
                id: t.name ?? `spacing-${t.value_px}`,
                name: t.name,
                value_px: t.value_px,
                value_rem: t.value_rem,
                multiplier: (t as SpacingTokenResponse & { multiplier?: number }).multiplier,
              })) ?? []
            }
          />

          {/* 5. RESPONSIVE PREVIEW - Breakpoint variations */}
          <SpacingResponsivePreview
            fallback={
              spacingResult?.tokens?.map((t) => ({
                id: t.name ?? `spacing-${t.value_px}`,
                name: t.name,
                value_px: t.value_px,
                value_rem: t.value_rem,
                multiplier: (t as SpacingTokenResponse & { multiplier?: number }).multiplier,
              })) ?? []
            }
          />

          {/* 6. TABLE & GRAPH VIEWS - Reference tables */}
          <SpacingTable
            fallback={
              spacingResult?.tokens?.map((t) => ({
                id: t.name ?? `spacing-${t.value_px}`,
                name: t.name,
                value_px: t.value_px,
                value_rem: t.value_rem,
                multiplier: (t as SpacingTokenResponse & { multiplier?: number }).multiplier,
              })) ?? []
            }
          />
          {spacingResult && (
            <>
              <SpacingScalePanel />
              <SpacingGraphList />
            </>
          )}
        </div>
      )}
    </section>
  )

  const renderTypography = () => (
    <section className="panel">
      <h2>Typography tokens</h2>
      <p className="panel-subtitle">Font families, sizes, and roles.</p>
      {typographyTokens.length === 0 ? typographyEmptyState : (
        <div className="spacing-content">
          {/* 1. PREVIEW CARDS - Live typography samples */}
          <TypographyCards />

          {/* 2. DETAIL CARDS - Comprehensive metrics */}
          <TypographyDetailCard />

          {/* 3. FONT FAMILY SHOWCASE - Independent font display */}
          <FontFamilyShowcase />

          {/* 4. FONT SIZE SCALE - Visual hierarchy */}
          <FontSizeScale />

          {/* 5. INSPECTOR - Advanced analysis */}
          <TypographyInspector />
        </div>
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
          {shadows.length > 0 && <ShadowTokenList shadows={shadows as any} />}
        </>
      )}
    </section>
  )

  const renderRelations = () => {
    // Debug info
    console.log('🔍 Relations tab render - projectId:', projectId, 'graphLoaded:', graphStoreState.loaded, 'graphColors:', graphColors.length, 'localColors:', colors.length)

    return (
      <section className="panel">
        <h2>Relations</h2>
        <p className="panel-subtitle">Alias, multiple, and compose relations from the graph.</p>

        {/* Prominent action button */}
        {projectId && !graphStoreState.loaded && (
          <div style={{ marginBottom: '2rem', padding: '1.5rem', background: '#E3F2FD', border: '2px solid #2196F3', borderRadius: '8px', textAlign: 'center' }}>
            <h3 style={{ margin: '0 0 1rem 0', color: '#1565C0' }}>⚡ Load Token Graph Data</h3>
            <p style={{ margin: '0 0 1rem 0', color: '#666' }}>
              Colors extracted! Click below to load graph relationships (aliases, dependencies, composition).
            </p>
            <button
              onClick={() => {
                console.log('🔘 Manual load clicked, projectId:', projectId)
                load(projectId)
                  .then(() => {
                    console.log('✅ Graph loaded successfully!')
                    console.log('Graph state:', useTokenGraphStore.getState())
                  })
                  .catch(err => console.error('❌ Graph load failed:', err))
              }}
              style={{
                padding: '1rem 2rem',
                background: '#2196F3',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '1.1rem',
                fontWeight: 'bold'
              }}
            >
              🔄 Load Token Graph (Project {projectId})
            </button>
          </div>
        )}

        {/* Debug info */}
        <details style={{ marginBottom: '1rem' }}>
          <summary style={{ cursor: 'pointer', padding: '0.5rem', background: '#F0F0F0', borderRadius: '4px', fontSize: '0.85rem' }}>
            <strong>Debug Info</strong> (click to expand)
          </summary>
          <div style={{ padding: '1rem', background: '#FAFAFA', marginTop: '0.5rem', borderRadius: '4px' }}>
            <div>Project ID: <strong>{projectId ?? 'none'}</strong></div>
            <div>Graph Loaded: <strong>{graphStoreState.loaded ? '✅ Yes' : '❌ No'}</strong></div>
            <div>Graph Colors: <strong>{graphColors.length}</strong></div>
            <div>Local Colors (App state): <strong>{colors.length}</strong></div>
            <div>Spacing Tokens: <strong>{graphSpacing.length}</strong></div>
            <div>Typography Tokens: <strong>{typographyTokens.length}</strong></div>
          </div>
        </details>

        <TokenGraphDemo />
        <RelationsTable />
        <RelationsDebugPanel />
      </section>
    )
  }

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
              onExtractionProgress={(progress) => {
                setExtractionProgress(progress)
                if (extractionStartTime === null) {
                  setExtractionStartTime(Date.now())
                }
              }}
              onIncrementalColorsExtracted={(newColors, total) => {
                setColors((prev) => {
                  const combined = [...prev]
                  for (const newColor of newColors) {
                    if (!combined.some((c) => c.hex === newColor.hex)) {
                      combined.push(newColor)
                    }
                  }
                  return combined
                })
              }}
              onSpacingExtracted={handleSpacingExtracted}
              onShadowsExtracted={handleShadowsExtracted}
              onTypographyExtracted={handleTypographyExtracted}
              onSpacingStarted={handleSpacingStarted}
              onShadowsStarted={handleShadowsStarted}
              onTypographyStarted={handleTypographyStarted}
              onRampsExtracted={setRamps}
              onDebugOverlay={setDebugOverlay}
              onSegmentationExtracted={setSegmentedPalette}
              onPaletteSummaryExtracted={handlePaletteSummaryExtracted}
              onImageBase64Extracted={setCurrentImageBase64}
              onError={handleError}
              onLoadingChange={(loading) => {
                handleLoadingChange(loading)
                if (!loading) {
                  setExtractionProgress(0)
                  setExtractionStartTime(null)
                }
              }}
            />
            {isLoading && extractionProgress > 0 && (
              <ExtractionProgressBar
                streamProgress={extractionProgress}
                colorsExtracted={colors.length}
                targetColors={Math.max(colors.length || 0, 10)}
                showTiming={true}
                startTime={extractionStartTime}
                stages={pipelineStages}
                activeStage="colors"
              />
            )}
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
              {['overview', 'colors', 'spacing', 'typography', 'shadows', 'lighting', 'relations', 'raw'].map((tab) => (
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
                {colorCount === 0 && spacingCount === 0 && graphStoreState.typography.length === 0 ? (
                  <div className="empty-state">
                    <div className="empty-content">
                      <div className="empty-icon">📊</div>
                      <p className="empty-title">Extract tokens to see overview</p>
                      <p className="empty-subtitle">Upload an image and run extractions for colors, spacing, and typography to generate your design system overview.</p>
                    </div>
                  </div>
                ) : (
                  <>
                    <OverviewNarrative
                      colors={colorDisplay}
                      colorCount={colorCount}
                      aliasCount={aliasCount}
                      spacingCount={spacingCount}
                      multiplesCount={multiplesCount}
                      typographyCount={graphStoreState.typography.length}
                      paletteSummary={paletteSummary}
                    />
                    <StreamingMetricsOverview projectId={projectId} refreshTrigger={metricsRefreshTrigger} />
                  </>
                )}
              </div>
            )}
            {activeTab === 'colors' && renderColors()}
            {activeTab === 'spacing' && renderSpacing()}
            {activeTab === 'typography' && renderTypography()}
            {activeTab === 'shadows' && renderShadows()}
            {activeTab === 'lighting' && (
              <section className="panel">
                <h2>Lighting Analysis</h2>
                <p className="panel-subtitle">Geometric shadow and lighting characteristics from shadowlab AI.</p>
                {!currentImageBase64 ? (
                  <div className="empty-subpanel">
                    <div className="empty-icon">💡</div>
                    <p className="empty-title">No image analyzed yet.</p>
                    <p className="empty-subtitle">Upload an image to analyze its lighting and shadow properties.</p>
                    <button
                      className="ghost-btn"
                      onClick={() => document.getElementById('uploader-panel')?.scrollIntoView({ behavior: 'smooth' })}
                    >
                      Go to upload
                    </button>
                  </div>
                ) : (
                  <LightingAnalyzer
                    imageBase64={currentImageBase64}
                    onAnalysisComplete={(result) => setLighting(result)}
                  />
                )}
              </section>
            )}
            {activeTab === 'relations' && renderRelations()}
            {activeTab === 'raw' && renderRaw()}
          </section>
        </div>
      </main>
    </div>
  )
}

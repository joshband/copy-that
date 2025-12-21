import { useEffect, useMemo, useState } from 'react'
import { ExtractionProgressBar } from '../../components/ui/progress/ExtractionProgressBar'
import { ImageUploader } from '../../components/image-uploader'
import { useTokenGraphStore } from '../../store/tokenGraphStore'
import { createInitialStages, updateStage, type PipelineStage, type StageStatus } from '../../types/pipeline'
import { PipelineStageIndicator } from '../../components/PipelineStageIndicator'
import { StreamingMetricsOverview } from '../../components/MetricsOverview'
import type {
  ColorRampMap,
  ColorToken,
  SegmentedColor,
  ShadowToken,
  SpacingExtractionResponse,
  TypographyToken,
} from '../../types'

const EMPTY_WARNINGS: string[] = []

interface UploadPanelProps {
  projectId: number | null
  onProjectCreated: (id: number) => void
  onError: (message: string) => void
  onLoadingChange?: (loading: boolean) => void
  showDebug: boolean
  onWarningsChange?: (warnings: string[]) => void
  onImageBase64Change?: (base64: string | null) => void
  onRampsChange?: (ramps: ColorRampMap) => void
  onSegmentedPaletteChange?: (segments: SegmentedColor[] | null) => void
  onPaletteSummaryChange?: (summary: string | null) => void
  onSpacingResultChange?: (result: SpacingExtractionResponse | null) => void
  onDebugOverlayChange?: (overlay: string | null) => void
}

export function UploadPanel({
  projectId,
  onProjectCreated,
  onError,
  onLoadingChange,
  showDebug,
  onWarningsChange,
  onImageBase64Change,
  onRampsChange,
  onSegmentedPaletteChange,
  onPaletteSummaryChange,
  onSpacingResultChange,
  onDebugOverlayChange,
}: UploadPanelProps) {
  const { legacyColors, legacySpacing, load, loaded: tokenGraphLoaded } = useTokenGraphStore()
  const [colors, setColors] = useState<ColorToken[]>([])
  const [shadows, setShadows] = useState<ShadowToken[]>([])
  const [shadowExtractionMetadata, setShadowExtractionMetadata] = useState<Record<
    string,
    unknown
  > | null>(null)
  const [typography, setTypography] = useState<TypographyToken[]>([])
  const [spacingResult, setSpacingResult] = useState<SpacingExtractionResponse | null>(null)
  const [ramps, setRamps] = useState<ColorRampMap>({})
  const [segmentedPalette, setSegmentedPalette] = useState<SegmentedColor[] | null>(null)
  const [paletteSummary, setPaletteSummary] = useState<string | null>(null)
  const [debugOverlay, setDebugOverlay] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [extractionProgress, setExtractionProgress] = useState(0)
  const [extractionStartTime, setExtractionStartTime] = useState<number | null>(null)
  const [pipelineStages, setPipelineStages] = useState<PipelineStage[]>(createInitialStages())
  const [didRefreshGraph, setDidRefreshGraph] = useState(false)
  const [isCollapsed, setIsCollapsed] = useState(false)
  const tokenGraphReady = didRefreshGraph && tokenGraphLoaded
  const warnings = useMemo(() => spacingResult?.warnings ?? EMPTY_WARNINGS, [spacingResult])
  const coreStagesComplete = useMemo(() => {
    const coreStages = pipelineStages.filter((stage) =>
      ['colors', 'spacing', 'typography', 'shadows'].includes(stage.id),
    )
    return (
      coreStages.length > 0 &&
      coreStages.every((stage) => stage.status === 'complete' || stage.status === 'error')
    )
  }, [pipelineStages])
  const extractionStatus = isLoading
    ? 'running'
    : coreStagesComplete
      ? 'complete'
      : colors.length || shadows.length || typography.length || spacingResult
        ? 'finalizing'
        : 'idle'

  // Reset refresh flag and local extracted state when project changes
  useEffect(() => {
    setColors([])
    setShadows([])
    setTypography([])
    setSpacingResult(null)
    setShadowExtractionMetadata(null)
    setRamps({})
    setSegmentedPalette(null)
    setPaletteSummary(null)
    setDebugOverlay(null)
    setExtractionProgress(0)
    setExtractionStartTime(null)
    setPipelineStages(createInitialStages())
    setDidRefreshGraph(false)
  }, [projectId])

  // Sync legacy token store consumers through tokenGraphStore adapters
  useEffect(() => {
    // after initial extraction, refresh token graph to pull W3C tokens
    if (projectId != null && colors.length && !didRefreshGraph) {
      // optional: defer to avoid stale writes
      const timer = setTimeout(() => {
        load(projectId)
          .catch(() => null)
          .finally(() => setDidRefreshGraph(true))
      }, 500)
      return () => clearTimeout(timer)
    }
    return undefined
  }, [projectId, colors.length, load, didRefreshGraph])

  useEffect(() => {
    if (projectId == null || !shadowExtractionMetadata) return
    load(projectId).catch(() => null)
  }, [projectId, shadowExtractionMetadata, load])

  useEffect(() => {
    onWarningsChange?.(warnings)
  }, [warnings, onWarningsChange])

  const extractionDuration = useMemo(() => {
    if (extractionStartTime == null || extractionProgress < 1) return null
    return (Date.now() - extractionStartTime) / 1000
  }, [extractionStartTime, extractionProgress])

  const toIndicatorStatus = (status: StageStatus): 'pending' | 'active' | 'complete' | 'failed' => {
    if (status === 'running') return 'active'
    if (status === 'error') return 'failed'
    if (status === 'complete') return 'complete'
    return 'pending'
  }

  const indicatorStages = useMemo(
    () =>
      pipelineStages.map((stage, idx) => ({
        phase: idx + 1,
        name: stage.label,
        status: toIndicatorStatus(stage.status),
        description: stage.description,
        duration: stage.startTime && stage.endTime ? stage.endTime - stage.startTime : undefined,
      })),
    [pipelineStages],
  )

  const handleColorsExtracted = (extracted: ColorToken[]) => {
    setColors(extracted)
    setPipelineStages((prev) => updateStage(prev, 'colors', { status: 'complete', endTime: Date.now() }))
  }

  const handleSpacingExtracted = (result: SpacingExtractionResponse | null) => {
    setSpacingResult(result)
    onSpacingResultChange?.(result)
    setPipelineStages((prev) => updateStage(prev, 'spacing', { status: 'complete', endTime: Date.now() }))
  }

  const handleShadowsExtracted = (shadowTokens: ShadowToken[]) => {
    setShadows(shadowTokens)
    setPipelineStages((prev) => updateStage(prev, 'shadows', { status: 'complete', endTime: Date.now() }))
  }

  const handleTypographyExtracted = (typographyTokens: TypographyToken[]) => {
    setTypography(typographyTokens)
    setPipelineStages((prev) =>
      updateStage(prev, 'typography', { status: 'complete', endTime: Date.now() }),
    )
  }

  const handleRampsExtracted = (nextRamps: ColorRampMap) => {
    setRamps(nextRamps)
    onRampsChange?.(nextRamps)
  }

  const handleDebugOverlay = (overlay: string | null) => {
    setDebugOverlay(overlay)
    onDebugOverlayChange?.(overlay)
  }

  const handleSegmentedPalette = (segments: SegmentedColor[] | null) => {
    setSegmentedPalette(segments)
    onSegmentedPaletteChange?.(segments)
  }

  const handlePaletteSummary = (summary: string | null) => {
    setPaletteSummary(summary)
    onPaletteSummaryChange?.(summary)
  }

  const summaryItems = useMemo(() => {
    const hasProject = projectId != null
    const standinValue = 'n/a'
    return [
      { label: 'Project', value: hasProject ? `#${projectId}` : standinValue, isStandin: !hasProject },
      { label: 'Colors', value: hasProject ? String(colors.length) : standinValue, isStandin: !hasProject },
      {
        label: 'Spacing',
        value: hasProject ? String(spacingResult?.tokens?.length ?? 0) : standinValue,
        isStandin: !hasProject,
      },
      {
        label: 'Typography',
        value: hasProject ? String(typography.length) : standinValue,
        isStandin: !hasProject,
      },
      { label: 'Shadows', value: hasProject ? String(shadows.length) : standinValue, isStandin: !hasProject },
    ]
  }, [projectId, colors.length, spacingResult, typography.length, shadows.length])

  const shadowlabMeta = useMemo(() => {
    const shadowlab = (shadowExtractionMetadata as any)?.shadowlab
    return shadowlab && typeof shadowlab === 'object' ? shadowlab : null
  }, [shadowExtractionMetadata])

  const shadowlabPipeline = useMemo(() => {
    const pipeline = (shadowlabMeta as any)?.pipeline
    return pipeline && typeof pipeline === 'object' ? pipeline : null
  }, [shadowlabMeta])

  return (
    <section
      className={`panel upload-panel${isCollapsed ? ' is-collapsed' : ''}`}
      id="uploader-panel"
      data-extraction-status={extractionStatus}
      data-extraction-complete={coreStagesComplete ? 'true' : 'false'}
      data-token-graph-ready={tokenGraphReady ? 'true' : 'false'}
    >
      <div className="upload-panel-header">
        <div>
          <h2>Upload an image</h2>
          {!isCollapsed && (
            <p className="panel-subtitle">
              We’ll send it to the backend, stream the extraction, and render tokens below.
            </p>
          )}
        </div>
        <button
          type="button"
          className="ghost-btn upload-panel-toggle"
          onClick={() => setIsCollapsed((prev) => !prev)}
          aria-expanded={!isCollapsed}
          aria-controls="upload-panel-body"
        >
          {isCollapsed ? 'Expand' : 'Collapse'}
        </button>
      </div>

      {isCollapsed ? (
        <div className="upload-panel-summary">
          <div className="summary-item">
            <span className="summary-label">Status</span>
            <span className="summary-value">{isLoading ? 'Extracting...' : 'Ready'}</span>
          </div>
          {isLoading && extractionProgress > 0 && (
            <div className="summary-item">
              <span className="summary-label">Progress</span>
              <span className="summary-value">{Math.round(extractionProgress)}%</span>
            </div>
          )}
          {summaryItems.map((item) => (
            <div className="summary-item" key={item.label}>
              <span className="summary-label">{item.label}</span>
              <span className={`summary-value${item.isStandin ? ' standin' : ''}`}>{item.value}</span>
            </div>
          ))}
        </div>
      ) : (
        <div className="upload-panel-body" id="upload-panel-body">
          <ImageUploader
            projectId={projectId}
            onProjectCreated={onProjectCreated}
            onColorExtracted={handleColorsExtracted}
            onExtractionProgress={(progress) => {
              setExtractionProgress(progress)
              if (extractionStartTime === null) setExtractionStartTime(Date.now())
            }}
            onIncrementalColorsExtracted={(newColors) => {
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
            onShadowMetadataExtracted={setShadowExtractionMetadata}
            onTypographyExtracted={handleTypographyExtracted}
            onSpacingStarted={() =>
              setPipelineStages((prev) =>
                updateStage(prev, 'spacing', { status: 'running', startTime: Date.now() }),
              )
            }
            onShadowsStarted={() =>
              setPipelineStages((prev) =>
                updateStage(prev, 'shadows', { status: 'running', startTime: Date.now() }),
              )
            }
            onTypographyStarted={() =>
              setPipelineStages((prev) =>
                updateStage(prev, 'typography', { status: 'running', startTime: Date.now() }),
              )
            }
            onRampsExtracted={handleRampsExtracted}
            onDebugOverlay={handleDebugOverlay}
            onSegmentationExtracted={handleSegmentedPalette}
            onPaletteSummaryExtracted={handlePaletteSummary}
            onImageBase64Extracted={
              onImageBase64Change ? (base64) => onImageBase64Change(base64) : undefined
            }
            onError={onError}
            onLoadingChange={(loading) => {
              setIsLoading(loading)
              onLoadingChange?.(loading)
              if (!loading) {
                setExtractionProgress(0)
                setExtractionStartTime(null)
              } else {
                // New extraction run: reset local caches so token graph reloads after completion
                setColors([])
                setShadows([])
                setTypography([])
                setSpacingResult(null)
                setShadowExtractionMetadata(null)
                setRamps({})
                setSegmentedPalette(null)
                setPaletteSummary(null)
                setDebugOverlay(null)
                setDidRefreshGraph(false)
                setPipelineStages((prev) =>
                  updateStage(createInitialStages(), 'colors', {
                    status: 'running',
                    startTime: Date.now(),
                  }),
                )
              }
            }}
          />
          {isLoading && extractionProgress > 0 && (
            <ExtractionProgressBar
              streamProgress={extractionProgress}
              colorsExtracted={colors.length || legacyColors().length}
              targetColors={Math.max(colors.length || legacyColors().length || 0, 10)}
              showTiming
              startTime={extractionStartTime ?? undefined}
            />
          )}
          <div className="panel metrics-panel">
            <StreamingMetricsOverview projectId={projectId} refreshTrigger={extractionProgress} />
            <PipelineStageIndicator stages={indicatorStages} />
            {shadowlabMeta && (
              <div style={{ marginTop: '1rem' }}>
                <h3 style={{ margin: 0 }}>ShadowLab (Deep Pipeline)</h3>
                {(shadowlabMeta as any)?.error ? (
                  <p style={{ marginTop: '0.5rem', marginBottom: 0 }}>
                    ShadowLab failed: {String((shadowlabMeta as any).error)}
                  </p>
                ) : (
                  <>
                    {shadowlabPipeline?.ml_backend && (
                      <p style={{ marginTop: '0.5rem', marginBottom: 0 }}>
                        Stage 4 (ML mask): <code>{String(shadowlabPipeline.ml_backend)}</code>
                      </p>
                    )}
                    {shadowlabPipeline?.geometry_backends && (
                      <p style={{ marginTop: '0.25rem', marginBottom: 0 }}>
                        Stage 6 (geometry): <code>{String(shadowlabPipeline.geometry_backends)}</code>
                      </p>
                    )}
                    {typeof (shadowlabMeta as any)?.duration_ms === 'number' && (
                      <p style={{ marginTop: '0.25rem', marginBottom: 0 }}>
                        Runtime: <code>{Math.round((shadowlabMeta as any).duration_ms)}ms</code>
                      </p>
                    )}
                  </>
                )}
              </div>
            )}
          </div>
          {showDebug && (
            <div className="debug-panel">
              <pre>
                {JSON.stringify(
                  { ramps, segmentedPalette, paletteSummary, spacingResult, shadowExtractionMetadata },
                  null,
                  2,
                )}
              </pre>
            </div>
          )}
        </div>
      )}
    </section>
  )
}

export default UploadPanel

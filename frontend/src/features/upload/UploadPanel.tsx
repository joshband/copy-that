import { useEffect, useMemo, useRef, useState } from 'react'
import { ImageUploader } from '../../components/image-uploader'
import { useTokenGraphStore } from '../../store/tokenGraphStore'
import { createInitialStages, updateStage, type PipelineStage, type StageStatus } from '../../types/pipeline'
import { PipelineStageIndicator } from '../../components/PipelineStageIndicator'
import { StreamingMetricsOverview } from '../../components/MetricsOverview'
import type {
  ArtifactBundle,
  ColorRampMap,
  ColorToken,
  SegmentedColor,
  ShadowToken,
  SpacingExtractionResponse,
  TypographyToken,
} from '../../types'

const EMPTY_WARNINGS: string[] = []

function graphFamilyCount(): number {
  const state = useTokenGraphStore.getState()
  return (
    state.colors.length +
    state.spacing.length +
    state.shadows.length +
    state.typography.length +
    state.layout.length
  )
}

interface UploadPanelProps {
  projectId: number | null
  onProjectCreated: (id: number) => void
  onError: (message: string) => void
  onLoadingChange?: (loading: boolean) => void
  showDebug: boolean
  /** Source image preview shown in the collapsed session strip across tabs */
  imagePreview?: string | null
  onWarningsChange?: (warnings: string[]) => void
  onImageBase64Change?: (base64: string | null) => void
  onRampsChange?: (ramps: ColorRampMap) => void
  onSegmentedPaletteChange?: (segments: SegmentedColor[] | null) => void
  onPaletteSummaryChange?: (summary: string | null) => void
  onSpacingResultChange?: (result: SpacingExtractionResponse | null) => void
  onDebugOverlayChange?: (overlay: string | null) => void
  onScienceArtifactsChange?: (artifacts: ArtifactBundle | null) => void
  onShadowArtifactsChange?: (artifacts: ArtifactBundle | null) => void
}

export function UploadPanel({
  projectId,
  onProjectCreated,
  onError,
  onLoadingChange,
  showDebug,
  imagePreview = null,
  onWarningsChange,
  onImageBase64Change,
  onRampsChange,
  onSegmentedPaletteChange,
  onPaletteSummaryChange,
  onSpacingResultChange,
  onDebugOverlayChange,
  onScienceArtifactsChange,
  onShadowArtifactsChange,
}: UploadPanelProps) {
  const { legacyColors, legacySpacing, load, loaded: tokenGraphLoaded } = useTokenGraphStore()
  const [colors, setColors] = useState<ColorToken[]>([])
  const [shadows, setShadows] = useState<ShadowToken[]>([])
  const [shadowExtractionMetadata, setShadowExtractionMetadata] = useState<Record<
    string,
    unknown
  > | null>(null)
  const [shadowArtifacts, setShadowArtifacts] = useState<ArtifactBundle | null>(null)
  const [typography, setTypography] = useState<TypographyToken[]>([])
  const [spacingResult, setSpacingResult] = useState<SpacingExtractionResponse | null>(null)
  const [ramps, setRamps] = useState<ColorRampMap>({})
  const [segmentedPalette, setSegmentedPalette] = useState<SegmentedColor[] | null>(null)
  const [paletteSummary, setPaletteSummary] = useState<string | null>(null)
  const [debugOverlay, setDebugOverlay] = useState<string | null>(null)
  const [scienceArtifacts, setScienceArtifacts] = useState<ArtifactBundle | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [extractionProgress, setExtractionProgress] = useState(0)
  const [extractionStartTime, setExtractionStartTime] = useState<number | null>(null)
  const [pipelineStages, setPipelineStages] = useState<PipelineStage[]>(createInitialStages())
  const [didRefreshGraph, setDidRefreshGraph] = useState(false)
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [extractorWarnings, setExtractorWarnings] = useState<string[]>([])
  const prevProjectIdRef = useRef<number | null>(null)
  const tokenGraphReady = didRefreshGraph && tokenGraphLoaded
  const spacingWarnings = useMemo(() => spacingResult?.warnings ?? EMPTY_WARNINGS, [spacingResult])
  const warnings = useMemo(
    () => [...extractorWarnings, ...spacingWarnings],
    [extractorWarnings, spacingWarnings],
  )
  const coreStagesComplete = useMemo(() => {
    const coreStages = pipelineStages.filter((stage) =>
      ['colors', 'spacing', 'typography', 'shadows'].includes(stage.id),
    )
    return (
      coreStages.length > 0 &&
      coreStages.every((stage) => stage.status === 'complete' || stage.status === 'error')
    )
  }, [pipelineStages])

  const analysisSummary = useMemo(() => {
    const colorCount = colors.length || legacyColors().length
    const spacingCount = spacingResult?.tokens?.length ?? legacySpacing().length
    const typographyCount = typography.length
    const shadowCount = shadows.length
    return `Analyzed ${colorCount} colors · ${spacingCount} spacing · ${typographyCount} typography · ${shadowCount} shadows`
  }, [colors.length, legacyColors, legacySpacing, spacingResult, typography.length, shadows.length])
  const extractionStatus = isLoading
    ? 'running'
    : coreStagesComplete
      ? 'complete'
      : colors.length || shadows.length || typography.length || spacingResult
        ? 'finalizing'
        : 'idle'

  // Reset local extract state when switching between existing projects — not on first null→id.
  useEffect(() => {
    const prev = prevProjectIdRef.current
    prevProjectIdRef.current = projectId
    if (prev == null || projectId == null || prev === projectId) {
      return
    }
    setColors([])
    setShadows([])
    setTypography([])
    setSpacingResult(null)
    setShadowExtractionMetadata(null)
    setShadowArtifacts(null)
    setRamps({})
    setSegmentedPalette(null)
    setPaletteSummary(null)
    setDebugOverlay(null)
    setScienceArtifacts(null)
    setExtractionProgress(0)
    setExtractionStartTime(null)
    setPipelineStages(createInitialStages())
    setDidRefreshGraph(false)
    setExtractorWarnings([])
  }, [projectId])

  // Hydrate W3C token graph after core stages finish (not gated on colors.length).
  useEffect(() => {
    if (projectId == null || !coreStagesComplete || didRefreshGraph) {
      return undefined
    }
    let cancelled = false
    const timer = setTimeout(() => {
      void (async () => {
        try {
          await load(projectId)
          if (cancelled) return
          // Persist races: one retry if the graph is still empty.
          if (graphFamilyCount() === 0) {
            await new Promise((r) => setTimeout(r, 1000))
            if (cancelled) return
            await load(projectId)
          }
        } catch {
          // ignore — tokenGraphReady stays false until a successful load
        } finally {
          if (!cancelled) setDidRefreshGraph(true)
        }
      })()
    }, 750)
    return () => {
      cancelled = true
      clearTimeout(timer)
    }
  }, [projectId, coreStagesComplete, load, didRefreshGraph])

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
        id: stage.id,
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

  const handleSpacingFailed = (error: string) => {
    setSpacingResult(null)
    onSpacingResultChange?.(null)
    setExtractorWarnings((prev) => (prev.includes(error) ? prev : [...prev, error]))
    setPipelineStages((prev) =>
      updateStage(prev, 'spacing', {
        status: 'error',
        endTime: Date.now(),
        description: error,
      }),
    )
  }

  const handleShadowsExtracted = (shadowTokens: ShadowToken[]) => {
    setShadows(shadowTokens)
    const shadowSummary = shadowTokens.length
      ? `Detected ${shadowTokens.length} shadow token${shadowTokens.length === 1 ? '' : 's'}`
      : 'No elevation detected'
    setPipelineStages((prev) =>
      updateStage(prev, 'shadows', {
        status: 'complete',
        endTime: Date.now(),
        description: shadowSummary,
      }),
    )
  }

  const handleShadowMetadataExtracted = (metadata: Record<string, unknown> | null) => {
    setShadowExtractionMetadata(metadata)
    const productMessage =
      metadata && typeof metadata.product_message === 'string'
        ? metadata.product_message.trim()
        : ''
    const emptyClassical =
      metadata?.cv_extractor_used === 'cv_classical_empty' ||
      metadata?.extraction_source === 'cv_classical_empty' ||
      metadata?.empty_reason === 'no_elevation'
    // Informational only — classical empty is success with zero elevation tokens
    if (emptyClassical && productMessage) {
      setPipelineStages((prev) =>
        updateStage(prev, 'shadows', {
          status: 'complete',
          description: productMessage,
        }),
      )
    }
  }

  const handleShadowsFailed = (error: string) => {
    setShadows([])
    setExtractorWarnings((prev) => (prev.includes(error) ? prev : [...prev, error]))
    setPipelineStages((prev) =>
      updateStage(prev, 'shadows', {
        status: 'error',
        endTime: Date.now(),
        description: error,
      }),
    )
  }

  const handleTypographyExtracted = (typographyTokens: TypographyToken[]) => {
    setTypography(typographyTokens)
    setPipelineStages((prev) =>
      updateStage(prev, 'typography', { status: 'complete', endTime: Date.now() }),
    )
  }

  const handleTypographyFailed = (error: string) => {
    setTypography([])
    setExtractorWarnings((prev) => (prev.includes(error) ? prev : [...prev, error]))
    setPipelineStages((prev) =>
      updateStage(prev, 'typography', {
        status: 'error',
        endTime: Date.now(),
        description: error,
      }),
    )
  }

  useEffect(() => {
    if (!coreStagesComplete) return
    setPipelineStages((prev) => {
      const analysisStage = prev.find((stage) => stage.id === 'analysis')
      const saveStage = prev.find((stage) => stage.id === 'save')
      let next = prev
      let changed = false

      if (analysisStage?.status === 'pending') {
        next = updateStage(next, 'analysis', {
          status: 'running',
          startTime: Date.now(),
          description: 'Analyzing extracted tokens',
        })
        changed = true
      }

      if (saveStage?.status === 'pending') {
        next = updateStage(next, 'save', {
          status: 'running',
          startTime: Date.now(),
          description: 'Saving to database',
        })
        changed = true
      }

      return changed ? next : prev
    })
  }, [coreStagesComplete])

  useEffect(() => {
    if (!coreStagesComplete || !tokenGraphReady) return
    setPipelineStages((prev) => {
      const analysisStage = prev.find((stage) => stage.id === 'analysis')
      const saveStage = prev.find((stage) => stage.id === 'save')
      let next = prev
      let changed = false
      const now = Date.now()

      if (analysisStage && analysisStage.status !== 'complete') {
        next = updateStage(next, 'analysis', {
          status: 'complete',
          endTime: now,
          description: analysisSummary,
        })
        changed = true
      }

      if (saveStage && saveStage.status !== 'complete') {
        next = updateStage(next, 'save', {
          status: 'complete',
          startTime: saveStage.startTime ?? now,
          endTime: now,
          description: projectId != null ? `Saved to project #${projectId}` : 'Results saved',
        })
        changed = true
      }

      return changed ? next : prev
    })
  }, [analysisSummary, coreStagesComplete, projectId, tokenGraphReady])

  // Collapse upload chrome after a successful extract so Snapshot owns the counts.
  useEffect(() => {
    if (coreStagesComplete && tokenGraphReady && !isLoading) {
      setIsCollapsed(true)
    }
  }, [coreStagesComplete, tokenGraphReady, isLoading])

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

  const handleScienceArtifacts = (artifacts: ArtifactBundle | null) => {
    setScienceArtifacts(artifacts)
    onScienceArtifactsChange?.(artifacts)
  }

  const handleShadowArtifacts = (artifacts: ArtifactBundle | null) => {
    setShadowArtifacts(artifacts)
    onShadowArtifactsChange?.(artifacts)
  }

  const shadowlabMeta = useMemo(() => {
    const shadowlab = (shadowExtractionMetadata as any)?.shadowlab
    return shadowlab && typeof shadowlab === 'object' ? shadowlab : null
  }, [shadowExtractionMetadata])

  const shadowlabPipeline = useMemo(() => {
    const pipeline = (shadowlabMeta as any)?.pipeline
    return pipeline && typeof pipeline === 'object' ? pipeline : null
  }, [shadowlabMeta])
  const shadowArtifactCount = shadowArtifacts?.images?.length ?? 0

  return (
    <section
      className={`panel upload-panel${isCollapsed ? ' is-collapsed' : ''}`}
      id="uploader-panel"
      data-extraction-status={extractionStatus}
      data-extraction-complete={coreStagesComplete ? 'true' : 'false'}
      data-token-graph-ready={tokenGraphReady ? 'true' : 'false'}
    >
      {isCollapsed ? (
        <div className="session-strip upload-panel-summary">
          <div className="session-strip__source">
            {imagePreview ? (
              <img
                className="session-strip__thumb"
                src={
                  imagePreview.startsWith('data:')
                    ? imagePreview
                    : `data:image/png;base64,${imagePreview}`
                }
                alt="Source upload"
              />
            ) : (
              <div className="session-strip__thumb session-strip__thumb--empty" aria-hidden />
            )}
            <div className="session-strip__meta">
              <p className="session-strip__title">Source</p>
              <p className="session-strip__status">
                {isLoading
                  ? `Extracting${extractionProgress > 0 ? ` · ${Math.round(extractionProgress)}%` : '…'}`
                  : 'Ready'}
              </p>
            </div>
          </div>

          <button
            type="button"
            className="ghost-btn upload-panel-toggle"
            onClick={() => setIsCollapsed(false)}
            aria-expanded={false}
            aria-controls="upload-panel-body"
          >
            Change image
          </button>
        </div>
      ) : (
        <>
          <div className="upload-panel-header">
            <div>
              <h2>Upload an image</h2>
              <p className="panel-subtitle">
                We’ll send it to the backend, stream the extraction, and render tokens below.
              </p>
            </div>
            {(projectId != null || imagePreview) && (
              <button
                type="button"
                className="ghost-btn upload-panel-toggle"
                onClick={() => setIsCollapsed(true)}
                aria-expanded
                aria-controls="upload-panel-body"
              >
                Collapse
              </button>
            )}
          </div>

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
            onSpacingFailed={handleSpacingFailed}
            onShadowsExtracted={handleShadowsExtracted}
            onShadowsFailed={handleShadowsFailed}
            onShadowMetadataExtracted={handleShadowMetadataExtracted}
            onShadowArtifactsExtracted={handleShadowArtifacts}
            onTypographyExtracted={handleTypographyExtracted}
            onTypographyFailed={handleTypographyFailed}
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
            onScienceArtifactsExtracted={handleScienceArtifacts}
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
                setShadowArtifacts(null)
                setRamps({})
                setSegmentedPalette(null)
                setPaletteSummary(null)
                setDebugOverlay(null)
                setScienceArtifacts(null)
                setDidRefreshGraph(false)
                setExtractorWarnings([])
                setPipelineStages((prev) =>
                  updateStage(createInitialStages(), 'colors', {
                    status: 'running',
                    startTime: Date.now(),
                  }),
                )
              }
            }}
          />
          {isLoading && (
            <div className="panel metrics-panel">
              {showDebug && (
                <StreamingMetricsOverview projectId={projectId} refreshTrigger={extractionProgress} />
              )}
              <PipelineStageIndicator
                stages={indicatorStages}
                streamProgress={Math.max(extractionProgress, 1)}
                showTimings={showDebug}
              />
              {colors.length > 0 && (
                <p className="extraction-colors-live" aria-live="polite">
                  {colors.length} colors extracted
                  {extractionStartTime != null
                    ? ` · ${Math.round((Date.now() - extractionStartTime) / 1000)}s`
                    : ''}
                </p>
              )}
              {showDebug && shadowlabMeta && (
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
                      {shadowArtifactCount > 0 ? (
                        <p style={{ marginTop: '0.25rem', marginBottom: 0 }}>
                          Artifacts: <code>{shadowArtifactCount}</code>
                        </p>
                      ) : null}
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
          )}
          {showDebug && (
            <div className="debug-panel">
              <pre>
                {JSON.stringify(
                  {
                    ramps,
                    segmentedPalette,
                    paletteSummary,
                    spacingResult,
                    shadowExtractionMetadata,
                    shadowArtifacts,
                    scienceArtifacts,
                  },
                  null,
                  2,
                )}
              </pre>
            </div>
          )}
          </div>
        </>
      )}
    </section>
  )
}

export default UploadPanel

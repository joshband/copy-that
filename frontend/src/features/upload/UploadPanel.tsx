import { useEffect, useMemo, useState } from 'react'
import { ExtractionProgressBar } from '../../components/ui/progress/ExtractionProgressBar'
import { ImageUploader } from '../../components/image-uploader'
import { useTokenGraphStore } from '../../store/tokenGraphStore'
import { createInitialStages, updateStage, type PipelineStage } from '../../types/pipeline'
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

interface UploadPanelProps {
  projectId: number | null
  onProjectCreated: (id: number) => void
  onError: (message: string) => void
  onLoadingChange?: (loading: boolean) => void
  showDebug: boolean
  onWarningsChange?: (warnings: string[]) => void
}

export function UploadPanel({
  projectId,
  onProjectCreated,
  onError,
  onLoadingChange,
  showDebug,
  onWarningsChange,
}: UploadPanelProps) {
  const { legacyColors, legacySpacing, load } = useTokenGraphStore()
  const [colors, setColors] = useState<ColorToken[]>([])
  const [shadows, setShadows] = useState<ShadowToken[]>([])
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
  const warnings = spacingResult?.warnings ?? []

  // Sync legacy token store consumers through tokenGraphStore adapters
  useEffect(() => {
    // after initial extraction, refresh token graph to pull W3C tokens
    if (projectId != null && colors.length) {
      // optional: defer to avoid stale writes
      setTimeout(() => load(projectId).catch(() => null), 500)
    }
  }, [projectId, colors.length, load])

  useEffect(() => {
    onWarningsChange?.(warnings)
  }, [warnings, onWarningsChange])

  const extractionDuration = useMemo(() => {
    if (extractionStartTime == null || extractionProgress < 1) return null
    return (Date.now() - extractionStartTime) / 1000
  }, [extractionStartTime, extractionProgress])

  const handleColorsExtracted = (extracted: ColorToken[]) => {
    setColors(extracted)
    setPipelineStages((prev) => updateStage(prev, 'colors', { status: 'complete', endTime: Date.now() }))
  }

  const handleSpacingExtracted = (result: SpacingExtractionResponse | null) => {
    setSpacingResult(result)
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

  return (
    <section className="panel upload-panel" id="uploader-panel">
      <h2>Upload an image</h2>
      <p className="panel-subtitle">
        We’ll send it to the backend, stream the extraction, and render tokens below.
      </p>
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
        onRampsExtracted={setRamps}
        onDebugOverlay={setDebugOverlay}
        onSegmentationExtracted={setSegmentedPalette}
        onPaletteSummaryExtracted={setPaletteSummary}
        onError={onError}
        onLoadingChange={(loading) => {
          setIsLoading(loading)
          onLoadingChange?.(loading)
          if (!loading) {
            setExtractionProgress(0)
            setExtractionStartTime(null)
          } else {
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
          extractionDuration={extractionDuration ?? undefined}
        />
      )}
      <div className="panel metrics-panel">
        <StreamingMetricsOverview />
        <PipelineStageIndicator stages={pipelineStages} />
      </div>
      {showDebug && (
        <div className="debug-panel">
          <pre>{JSON.stringify({ ramps, segmentedPalette, paletteSummary, spacingResult }, null, 2)}</pre>
        </div>
      )}
    </section>
  )
}

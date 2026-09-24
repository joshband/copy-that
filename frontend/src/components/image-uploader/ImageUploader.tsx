import { useState, useEffect, useRef } from 'react'
import '../ImageUploader.css'
import {
  ArtifactBundle,
  ColorRampMap,
  ColorToken,
  SegmentedColor,
  SpacingExtractionResponse,
} from '../../types'
import { useTokenGraphStore } from '../../store/tokenGraphStore'
import { useExtractionState } from '../../features/extraction/state'
import { useImageFile } from './hooks'
import { useStreamingExtraction } from './hooks'
import { useParallelExtractions, type ParallelExtractFailure } from './hooks'
import { useProjectManagement } from './hooks'
import { UploadArea } from '../ui/input/UploadArea'
import { PreviewSection } from './PreviewSection'
import { SettingsPanel } from './SettingsPanel'
import { ExtractButton } from './ExtractButton'
import { ProjectInfo } from './ProjectInfo'
import { isValidImageFile } from '../../utils'
import { resolveApiBase } from '../../api/client'

function isParallelFailure(result: unknown): result is ParallelExtractFailure {
  return (
    typeof result === 'object' &&
    result !== null &&
    'ok' in result &&
    (result as ParallelExtractFailure).ok === false &&
    typeof (result as ParallelExtractFailure).error === 'string'
  )
}

interface Props {
  projectId: number | null
  onProjectCreated: (id: number) => void
  onColorExtracted: (colors: ColorToken[]) => void
  onIncrementalColorsExtracted?: (colors: ColorToken[], total: number) => void
  onExtractionProgress?: (progress: number) => void
  onSpacingExtracted?: (result: SpacingExtractionResponse | null) => void
  onSpacingFailed?: (error: string) => void
  onShadowsExtracted?: (shadows: any[]) => void
  onShadowsFailed?: (error: string) => void
  onShadowMetadataExtracted?: (metadata: Record<string, unknown> | null) => void
  onShadowArtifactsExtracted?: (artifacts: ArtifactBundle | null) => void
  onTypographyExtracted?: (typography: any[]) => void
  onTypographyFailed?: (error: string) => void
  onRampsExtracted?: (ramps: ColorRampMap) => void
  onDebugOverlay?: (overlayBase64: string | null) => void
  onSegmentationExtracted?: (segments: SegmentedColor[] | null) => void
  onPaletteSummaryExtracted?: (summary: string | null) => void
  onImageBase64Extracted?: (base64: string) => void
  onScienceArtifactsExtracted?: (artifacts: ArtifactBundle | null) => void
  onSpacingStarted?: () => void
  onShadowsStarted?: () => void
  onTypographyStarted?: () => void
  onError: (error: string) => void
  onLoadingChange: (loading: boolean) => void
}

const API_BASE_URL = resolveApiBase()

export default function ImageUploader({
  projectId,
  onProjectCreated,
  onColorExtracted,
  onIncrementalColorsExtracted,
  onExtractionProgress,
  onSpacingExtracted,
  onSpacingFailed,
  onShadowsExtracted,
  onShadowsFailed,
  onShadowMetadataExtracted,
  onShadowArtifactsExtracted,
  onTypographyExtracted,
  onTypographyFailed,
  onRampsExtracted,
  onDebugOverlay,
  onSegmentationExtracted,
  onPaletteSummaryExtracted,
  onImageBase64Extracted,
  onScienceArtifactsExtracted,
  onSpacingStarted,
  onShadowsStarted,
  onTypographyStarted,
  onError,
  onLoadingChange,
}: Props) {
  const { file, preview, base64, mediaType, selectFile } = useImageFile()
  const { parseColorStream } = useStreamingExtraction()
  const { extractSpacing, extractShadows, extractTypography, extractGradients } =
    useParallelExtractions()
  const { ensureProject } = useProjectManagement()

  const runRef = useRef(0)
  const [extracting, setExtracting] = useState(false)
  useEffect(() => () => { ++runRef.current }, [])
  const [projectName, setProjectName] = useState('My Colors')
  const [maxColors, setMaxColors] = useState(10)
  const [includeScienceArtifacts, setIncludeScienceArtifacts] = useState(false)

  // Log component mount
  useEffect(() => {
    console.log('ImageUploader component mounted')
    console.log('API_BASE_URL:', API_BASE_URL)
  }, [])

  // Handle file selection from input or drag-drop
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    console.log('File selected:', e.target.files)
    const newFile = e.target.files?.[0] ?? null

    if (!newFile) {
      console.log('No file selected')
      return
    }

    console.log('File details:', { name: newFile.name, size: newFile.size, type: newFile.type })
    if (!isValidImageFile(newFile)) {
      onError('Please select a valid image file')
      return
    }

    try {
      selectFile(newFile).catch((err) => {
        console.error('File selection error:', err)
        onError((err as Error).message ?? 'Failed to process image')
      })
      onError('')
    } catch (err) {
      const msg = (err as Error).message ?? 'Failed to process image'
      onError(msg)
    }
  }

  // Handle drag and drop
  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()

    const droppedFile = e.dataTransfer.files?.[0] ?? null
    if (droppedFile) {
      const event = {
        target: { files: [droppedFile] },
      } as unknown as React.ChangeEvent<HTMLInputElement>
      handleFileSelect(event)
    }
  }

  // Main extraction orchestration
  const handleExtract = async () => {
    if (extracting) return
    if (!file || !base64) {
      onError('Please select an image first')
      return
    }

    const run = ++runRef.current
    const current = () => run === runRef.current
    setExtracting(true)
    let parallel: Promise<unknown> | undefined
    try {
      useTokenGraphStore.getState().reset()
      useExtractionState.setState({ sourceId: crypto.randomUUID(), phase: 'running', families: {} })
      console.log('Starting color extraction...')
      onLoadingChange(true)
      onError('')
      onSegmentationExtracted?.(null)

      // Ensure project exists
      console.log('Ensuring project exists...')
      const pId = await ensureProject(null, projectName)
      if (!current()) return
      console.log('Project ID:', pId)

      // Notify parent component about project creation
      onProjectCreated(pId)

      // Notify about base64
      if (base64) {
        console.log('Base64 length:', base64.length)
        onImageBase64Extracted?.(base64)
      }

      // Fire parallel extractions (non-blocking)
      console.log('Starting parallel extractions...')
      onSpacingStarted?.()
      onShadowsStarted?.()
      onTypographyStarted?.()
      parallel = Promise.all([
        extractSpacing(base64, mediaType, pId)
          .then((result) => {
            if (!current()) return
            if (isParallelFailure(result)) {
              onSpacingFailed?.(result.error)
              return
            }
            onSpacingExtracted?.(result)
          })
          .catch((err) => {
            if (!current()) return
            onSpacingFailed?.(err instanceof Error ? err.message : 'Spacing extraction failed')
          }),
        extractShadows(base64, mediaType, pId)
          .then((result) => {
            if (!current()) return
            if (isParallelFailure(result)) {
              onShadowsFailed?.(result.error)
              onShadowMetadataExtracted?.(null)
              return
            }
            onShadowMetadataExtracted?.(result.extractionMetadata ?? null)
            onShadowsExtracted?.(result.tokens)
            onShadowArtifactsExtracted?.(result.artifacts ?? null)
          })
          .catch((err) => {
            if (!current()) return
            onShadowsFailed?.(err instanceof Error ? err.message : 'Shadow extraction failed')
            onShadowArtifactsExtracted?.(null)
          }),
        extractTypography(base64, mediaType, pId)
          .then((result) => {
            if (!current()) return
            if (isParallelFailure(result)) {
              onTypographyFailed?.(result.error)
              return
            }
            onTypographyExtracted?.(result)
          })
          .catch((err) => {
            if (!current()) return
            onTypographyFailed?.(err instanceof Error ? err.message : 'Typography extraction failed')
          }),
        extractGradients(base64, mediaType, pId).catch((err) => {
            if (!current()) return
          console.warn('Gradient extraction failed', err)
        }),
      ])

      // Call streaming extraction API for colors
      console.log('Calling streaming extraction API at:', `${API_BASE_URL}/colors/extract-streaming`)
      const streamResponse = await fetch(`${API_BASE_URL}/colors/extract-streaming`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: pId,
          image_base64: base64,
          max_colors: maxColors,
          include_science_artifacts: includeScienceArtifacts,
        }),
      })

      if (!streamResponse.ok) {
        let detail = `Color extraction failed (HTTP ${streamResponse.status})`
        try {
          const data = (await streamResponse.json()) as { detail?: unknown }
          if (typeof data.detail === 'string' && data.detail.trim()) {
            detail = data.detail
          }
        } catch {
          if (streamResponse.statusText) {
            detail = `Color extraction failed: ${streamResponse.statusText}`
          }
        }
        throw new Error(detail)
      }

      // Create a custom progress handler that updates pipeline stages
      const progressHandler = (progress: number) => {
        if (current()) onExtractionProgress?.(progress)
      }

      // Parse streaming response with progress callbacks
      const result = await parseColorStream(
        streamResponse,
        progressHandler,
        (colors, total) => { if (current()) onIncrementalColorsExtracted?.(colors, total) }
      )
      if (!current()) return
      console.log('Extraction result:', result)

      onColorExtracted(result.extractedColors)
      if (result.shadows.length && onShadowsExtracted) {
        onShadowsExtracted(result.shadows)
      }
      if (Object.keys(result.ramps).length && onRampsExtracted) {
        onRampsExtracted(result.ramps)
      }
      if (result.debugOverlay && onDebugOverlay) {
        onDebugOverlay(result.debugOverlay)
      }
      if (result.segmentation && onSegmentationExtracted) {
        onSegmentationExtracted(result.segmentation)
      }
      if (result.paletteSummary && onPaletteSummaryExtracted) {
        onPaletteSummaryExtracted(result.paletteSummary)
      }
      if (onScienceArtifactsExtracted) {
        onScienceArtifactsExtracted(result.scienceArtifacts ?? null)
      }
    } catch (err: unknown) {
      console.error('Extraction error:', err)
      const error = err as { response?: { data?: { detail?: string } }; message?: string }
      const errorMsg = error.response?.data?.detail ?? error.message ?? 'Failed to extract colors'
      if (current()) onError(errorMsg)
    } finally {
      await parallel
      if (current()) { setExtracting(false); onLoadingChange(false) }
    }
  }

  return (
    <fieldset className="uploader" disabled={extracting}>
      <UploadArea
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onFileSelect={handleFileSelect}
      />

      <PreviewSection preview={preview} fileName={file?.name ?? null} />

      <SettingsPanel
        projectName={projectName}
        maxColors={maxColors}
        projectId={projectId}
        includeScienceArtifacts={includeScienceArtifacts}
        onProjectNameChange={setProjectName}
        onMaxColorsChange={setMaxColors}
        onIncludeScienceArtifactsChange={setIncludeScienceArtifacts}
      />

      <ExtractButton disabled={!file || !base64 || extracting} onClick={() => void handleExtract()} />

      <ProjectInfo projectId={projectId} />
    </fieldset>
  )
}

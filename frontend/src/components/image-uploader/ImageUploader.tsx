import { useState, useEffect } from 'react'
import '../ImageUploader.css'
import { ColorRampMap, ColorToken, SegmentedColor, SpacingExtractionResponse } from '../../types'
import { useImageFile } from './hooks'
import { useStreamingExtraction } from './hooks'
import { useParallelExtractions } from './hooks'
import { useProjectManagement } from './hooks'
import { UploadArea } from './UploadArea'
import { PreviewSection } from './PreviewSection'
import { SettingsPanel } from './SettingsPanel'
import { ExtractButton } from './ExtractButton'
import { ProjectInfo } from './ProjectInfo'

interface Props {
  projectId: number | null
  onProjectCreated: (id: number) => void
  onColorExtracted: (colors: ColorToken[]) => void
  onSpacingExtracted?: (result: SpacingExtractionResponse | null) => void
  onShadowsExtracted?: (shadows: any[]) => void
  onTypographyExtracted?: (typography: any[]) => void
  onRampsExtracted?: (ramps: ColorRampMap) => void
  onDebugOverlay?: (overlayBase64: string | null) => void
  onSegmentationExtracted?: (segments: SegmentedColor[] | null) => void
  onImageBase64Extracted?: (base64: string) => void
  onError: (error: string) => void
  onLoadingChange: (loading: boolean) => void
}

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL ?? '/api/v1'

export default function ImageUploader({
  projectId,
  onProjectCreated,
  onColorExtracted,
  onSpacingExtracted,
  onShadowsExtracted,
  onTypographyExtracted,
  onRampsExtracted,
  onDebugOverlay,
  onSegmentationExtracted,
  onImageBase64Extracted,
  onError,
  onLoadingChange,
}: Props) {
  const { file, preview, base64, mediaType, selectFile } = useImageFile()
  const { parseColorStream } = useStreamingExtraction()
  const { extractSpacing, extractShadows, extractTypography } = useParallelExtractions()
  const { ensureProject } = useProjectManagement()

  const [projectName, setProjectName] = useState('My Colors')
  const [maxColors, setMaxColors] = useState(10)

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
    if (!file || !base64) {
      onError('Please select an image first')
      return
    }

    try {
      console.log('Starting color extraction...')
      onLoadingChange(true)
      onError('')
      onSegmentationExtracted?.(null)

      // Ensure project exists
      console.log('Ensuring project exists...')
      const pId = await ensureProject(projectId, projectName)
      console.log('Project ID:', pId)

      // Notify about base64
      if (base64) {
        console.log('Base64 length:', base64.length)
        onImageBase64Extracted?.(base64)
      }

      // Fire parallel extractions (non-blocking)
      console.log('Starting parallel extractions...')
      if (onSpacingExtracted) onSpacingExtracted(null)
      void Promise.all([
        extractSpacing(base64, mediaType, pId)
          .then((result) => result && onSpacingExtracted?.(result))
          .catch(() => onSpacingExtracted?.(null)),
        extractShadows(base64, mediaType)
          .then((result) => onShadowsExtracted?.(result))
          .catch(() => onShadowsExtracted?.([])),
        extractTypography(base64, mediaType, pId)
          .then((result) => onTypographyExtracted?.(result))
          .catch(() => onTypographyExtracted?.([])),
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
        }),
      })

      if (!streamResponse.ok) {
        throw new Error(`API error: ${streamResponse.statusText}`)
      }

      // Parse streaming response
      const result = await parseColorStream(streamResponse)
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
    } catch (err: unknown) {
      console.error('Extraction error:', err)
      const error = err as { response?: { data?: { detail?: string } }; message?: string }
      const errorMsg = error.response?.data?.detail ?? error.message ?? 'Failed to extract colors'
      onError(errorMsg)
    } finally {
      onLoadingChange(false)
    }
  }

  return (
    <div className="uploader">
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
        onProjectNameChange={setProjectName}
        onMaxColorsChange={setMaxColors}
      />

      <ExtractButton disabled={!file} onClick={() => void handleExtract()} />

      <ProjectInfo projectId={projectId} />
    </div>
  )
}

import { useState, useEffect } from 'react'
import './ImageUploader.css'
import { ColorRampMap, ColorToken, SegmentedColor, SpacingExtractionResponse } from '../types'
import { ApiClient } from '../api/client'
import {
  isValidImageFile,
  isFileSizeValid,
  resizeImageFile,
} from '../utils'

interface Props {
  projectId: number | null
  onProjectCreated: (id: number) => void
  onColorExtracted: (colors: ColorToken[]) => void
  onSpacingExtracted?: (result: SpacingExtractionResponse | null) => void
  onShadowsExtracted?: (shadows: any[]) => void
  onRampsExtracted?: (ramps: ColorRampMap) => void
  onDebugOverlay?: (overlayBase64: string | null) => void
  onSegmentationExtracted?: (segments: SegmentedColor[] | null) => void
  onError: (error: string) => void
  onLoadingChange: (loading: boolean) => void
}

// API base URL from environment or default
const API_BASE_URL = (import.meta as any).env?.VITE_API_URL ?? '/api/v1'

// Type for streaming events
interface StreamEvent {
  error?: string
  phase?: number
  status?: string
  color_count?: number
  progress?: number
  colors?: ColorToken[]
  shadows?: any[]
  background_colors?: string[]
  text_roles?: Array<{ hex: string; role: string; contrast?: number }>
  ramps?: ColorRampMap
  debug?: { overlay_png_base64?: string; segmented_palette?: SegmentedColor[] }
}

export default function ImageUploader({
  projectId,
  onProjectCreated,
  onColorExtracted,
  onSpacingExtracted,
  onShadowsExtracted,
  onRampsExtracted,
  onDebugOverlay,
  onSegmentationExtracted,
  onError,
  onLoadingChange,
}: Props) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [projectName, setProjectName] = useState('My Colors')
  const [maxColors, setMaxColors] = useState(10)
  const [preview, setPreview] = useState<string | null>(null)
  const [compressedBase64, setCompressedBase64] = useState<string | null>(null)
  const [compressedMediaType, setCompressedMediaType] = useState<string>('image/jpeg')

  // Log component mount
  useEffect(() => {
    console.log('ImageUploader component mounted')
    console.log('API_BASE_URL:', API_BASE_URL)
  }, [])

  // Create project if needed
  const ensureProject = async (): Promise<number> => {
    if (projectId != null) return projectId

    try {
      const response = await ApiClient.post<{ id: number }>('/projects', {
        name: projectName,
        description: 'Color extraction project',
      })
      const newProjectId = response.id
      onProjectCreated(newProjectId)
      return newProjectId
    } catch (err) {
      throw new Error('Failed to create project')
    }
  }

  // Handle file selection
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    console.log('File selected:', e.target.files)
    const file = e.target.files?.[0]
    if (!file) {
      console.log('No file selected')
      return
    }

    console.log('File details:', { name: file.name, size: file.size, type: file.type })

    // Validate file type using shared utility
    if (!isValidImageFile(file)) {
      onError('Please select a valid image file')
      return
    }

    // Validate file size (max 5MB) using shared utility
    const MAX_FILE_SIZE = 5 * 1024 * 1024
    if (!isFileSizeValid(file, MAX_FILE_SIZE)) {
      onError('Image size must be less than 5MB')
      return
    }

    setSelectedFile(file)
    console.log('File set successfully')

    // Generate preview using shared utility
    resizeImageFile(file, { maxDimension: 1400, quality: 0.82, mimeType: 'image/jpeg' })
      .then(({ dataUrl, base64, mediaType }) => {
        setPreview(dataUrl)
        setCompressedBase64(base64)
        setCompressedMediaType(mediaType)
        console.log('Preview generated')
      })
      .catch((err) => {
        console.error('Failed to generate preview:', err)
      })

    onError('')
  }

  // Handle extraction
  const handleExtract = async () => {
    if (!selectedFile) {
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
      const pId = await ensureProject()
      console.log('Project ID:', pId)

      // Convert image to compressed base64 (client-side)
      console.log('Converting image to base64...')
      const base64 =
        compressedBase64 ??
        (await resizeImageFile(selectedFile, {
          maxDimension: 1400,
          quality: 0.82,
          mimeType: 'image/jpeg',
        }).then((res) => {
          setCompressedBase64(res.base64)
          setCompressedMediaType(res.mediaType)
          return res.base64
        }))
      if (base64) {
        console.log('Base64 length:', base64.length)
      }

      // Fire spacing/shadow extraction in parallel (non-blocking) to render progressively
      const kickOffSpacing = async () => {
        if (!onSpacingExtracted) return
        try {
          const resp = await fetch(`${API_BASE_URL}/spacing/extract`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              image_base64: base64,
              image_media_type: compressedMediaType,
              project_id: pId,
              max_tokens: 15,
            }),
          })
          if (resp.ok) {
            const data: SpacingExtractionResponse = await resp.json()
            onSpacingExtracted(data)
          } else {
            onSpacingExtracted(null)
          }
        } catch (err) {
          console.warn('Spacing extraction failed', err)
          onSpacingExtracted(null)
        }
      }

      const kickOffShadows = async () => {
        if (!onShadowsExtracted) return
        try {
          const resp = await fetch(`${API_BASE_URL}/shadows/extract`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              image_base64: base64,
              image_media_type: compressedMediaType || selectedFile?.type,
              max_tokens: 20,
            }),
          })
          if (resp.ok) {
            const data = await resp.json()
            const tokens = data.tokens || []
            const normalized =
              Array.isArray(tokens) && tokens.length > 0
                ? tokens
                : typeof tokens === 'object'
                  ? Object.values(tokens)
                  : []
            onShadowsExtracted(normalized)
          } else {
            onShadowsExtracted([])
          }
        } catch (err) {
          console.warn('Shadow extraction failed', err)
          onShadowsExtracted([])
        }
      }

      if (onSpacingExtracted) {
        onSpacingExtracted(null)
      }
      void kickOffSpacing()
      void kickOffShadows()

      // Call streaming extraction API for colors
      console.log('Calling streaming extraction API at:', `${API_BASE_URL}/colors/extract-streaming`)
      const streamResponse = await fetch(`${API_BASE_URL}/colors/extract-streaming`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: pId,
          image_base64: base64,
          max_colors: maxColors,
        })
      })

      if (!streamResponse.ok) {
        throw new Error(`API error: ${streamResponse.statusText}`)
      }

      // Parse streaming response
      const reader = streamResponse.body?.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let extractedColors: ColorToken[] = []
      let streamShadows: any[] = []
      let streamBackgrounds: string[] = []
      let streamRamps: ColorRampMap = {}
      let debugOverlay: string | null = null

      while (reader) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() ?? ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              // Some upstream sources may emit non-JSON tokens like NaN; sanitize before parsing
              const rawPayload = line.slice(6)
              const sanitizedPayload = rawPayload.replace(/\bNaN\b/g, 'null')
              const event = JSON.parse(sanitizedPayload) as StreamEvent
              console.log('Stream event:', event)

              if (event.error != null) {
                throw new Error(event.error)
              }

              if (event.phase === 1 && event.status === 'colors_extracted') {
                console.log(`Extracted ${event.color_count ?? 0} colors`)
              } else if (event.phase === 1 && event.status === 'colors_streaming') {
                console.log(`Progress: ${((event.progress ?? 0) * 100).toFixed(0)}%`)
              } else if (event.phase === 2 && event.status === 'extraction_complete') {
                console.log('Extraction complete! Got full color data from stream')
                extractedColors = event.colors ?? []
                streamShadows = event.shadows ?? streamShadows
                streamBackgrounds = event.background_colors ?? streamBackgrounds
                streamRamps = event.ramps ?? streamRamps
                if (event.shadows && onShadowsExtracted) {
                  onShadowsExtracted(event.shadows)
                }
                if (event.ramps && onRampsExtracted) {
                  onRampsExtracted(event.ramps)
                }
                if (event.debug?.overlay_png_base64) {
                  debugOverlay = event.debug.overlay_png_base64
                  onDebugOverlay?.(debugOverlay)
                }
                if (event.debug?.segmented_palette && onSegmentationExtracted) {
                  onSegmentationExtracted(event.debug.segmented_palette)
                }
              }
            } catch (e) {
              console.error('Error parsing stream event:', e)
            }
          }
        }
      }

      console.log('Extracted colors:', extractedColors)
      onColorExtracted(extractedColors)
      if (onShadowsExtracted && streamShadows?.length) {
        onShadowsExtracted(streamShadows)
      }
      if (onRampsExtracted && streamRamps && Object.keys(streamRamps).length) {
        onRampsExtracted(streamRamps)
      }
      if (onDebugOverlay && debugOverlay) {
        onDebugOverlay(debugOverlay)
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

  // Handle drag and drop
  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()

    const file = e.dataTransfer.files?.[0]
    if (file) {
      const event = {
        target: { files: [file] },
      } as unknown as React.ChangeEvent<HTMLInputElement>
      handleFileSelect(event)
    }
  }

  return (
    <div className="uploader">
      {/* Upload Area */}
      <div
        className="upload-area"
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="file-input"
          className="file-input"
          accept="image/*"
          onChange={handleFileSelect}
        />
        <label htmlFor="file-input" className="upload-label">
          <div className="upload-icon">📸</div>
          <h3>Upload Image</h3>
          <p>Drag and drop or click to select</p>
          <p className="upload-hint">JPEG, PNG, WebP (max 5MB)</p>
        </label>
      </div>

      {/* Preview */}
      {preview && (
        <div className="preview-section">
          <h4>Preview</h4>
          <img src={preview} alt="Preview" className="preview-image" />
          <p className="preview-name">{selectedFile?.name}</p>
        </div>
      )}

      {/* Max colors directly under preview */}
      <div className="setting-group inline-setting">
        <label htmlFor="max-colors">
          Max Colors: <span className="value">{maxColors}</span>
        </label>
        <input
          id="max-colors"
          type="range"
          min="1"
          max="50"
          value={maxColors}
          onChange={(e) => setMaxColors(parseInt(e.target.value))}
          className="range-slider"
        />
      </div>

      {/* Settings */}
      <div className="settings">
        <div className="setting-group">
          <label htmlFor="project-name">Project Name:</label>
          <input
            id="project-name"
            type="text"
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
            placeholder="My Colors"
            disabled={projectId !== null}
          />
        </div>
      </div>

      {/* Extract Button */}
      <button
        className="extract-btn"
        onClick={() => {
          console.log('Extract button clicked! selectedFile:', selectedFile)
          void handleExtract()
        }}
        disabled={!selectedFile}
        title={selectedFile != null ? 'Ready to extract colors' : 'Please select an image first'}
      >
        ✨ Extract Colors
      </button>

      {/* Project Info */}
      {projectId && (
        <div className="project-info">
          <p>Project ID: <code>{projectId}</code></p>
        </div>
      )}
    </div>
  )
}

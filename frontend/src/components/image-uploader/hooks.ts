import { useState, useCallback } from 'react'
import {
  ArtifactBundle,
  ColorToken,
  SegmentedColor,
  SpacingExtractionResponse,
  ColorRampMap,
} from '../../types'
import { ApiClient, resolveApiBase, type ApiError } from '../../api/client'
import { resizeImageFile, isValidImageFile, isFileSizeValid } from '../../utils'
import { StreamEvent } from './types'

const API_BASE_URL = resolveApiBase()

async function readApiErrorDetail(resp: Response, fallback: string): Promise<string> {
  try {
    const data = (await resp.json()) as { detail?: unknown }
    if (typeof data.detail === 'string' && data.detail.trim()) return data.detail
    if (Array.isArray(data.detail) && data.detail.length > 0) {
      return data.detail
        .map((item) => (typeof item === 'string' ? item : JSON.stringify(item)))
        .join('; ')
    }
  } catch {
    // ignore JSON parse failures
  }
  return `${fallback} (HTTP ${resp.status}${resp.statusText ? `: ${resp.statusText}` : ''})`
}

export type ParallelExtractFailure = {
  ok: false
  error: string
}

const filterScienceArtifacts = (bundle?: ArtifactBundle | null): ArtifactBundle | null => {
  if (!bundle) return null
  const images = (bundle.images ?? []).filter((item) => item.stage === 'science')
  const json = (bundle.json ?? []).filter((item) => item.stage === 'science')
  if (!images.length && !json.length) return null
  return { images, json }
}

/**
 * Hook for managing image file selection and processing
 */
export function useImageFile() {
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [base64, setBase64] = useState<string | null>(null)
  const [mediaType, setMediaType] = useState<string>('image/jpeg')

  const selectFile = useCallback(
    async (newFile: File | null) => {
      if (!newFile) {
        setFile(null)
        setPreview(null)
        setBase64(null)
        return
      }

      // Validate file type
      if (!isValidImageFile(newFile)) {
        throw new Error('Please select a valid image file')
      }

      // Validate file size (max 5MB)
      const MAX_FILE_SIZE = 5 * 1024 * 1024
      if (!isFileSizeValid(newFile, MAX_FILE_SIZE)) {
        throw new Error('Image size must be less than 5MB')
      }

      setFile(newFile)

      // Generate preview and compressed base64
      try {
        const result = await resizeImageFile(newFile, {
          maxDimension: 1400,
          quality: 0.82,
          mimeType: 'image/jpeg',
        })
        setPreview(result.dataUrl)
        setBase64(result.base64)
        setMediaType(result.mediaType)
      } catch (err) {
        console.error('Failed to process image:', err)
        throw err
      }
    },
    []
  )

  return { file, preview, base64, mediaType, selectFile }
}

/**
 * Hook for parsing streaming color extraction responses
 */
export function useStreamingExtraction() {
  const parseColorStream = useCallback(
    async (
      response: Response,
      onProgress?: (progress: number) => void,
      onIncrementalColors?: (colors: ColorToken[], totalExtracted: number) => void
    ) => {
      let extractedColors: ColorToken[] = []
      const shadows: any[] = []
      const backgrounds: string[] = []
      let ramps: ColorRampMap = {}
      let debugOverlay: string | null = null
      let segmentation: SegmentedColor[] | null = null
      let paletteSummary: string | null = null
      let scienceArtifacts: ArtifactBundle | null = null

      const reader = response.body?.getReader()
      if (!reader) throw new Error('No response body')

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() ?? ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue

          // Sanitize NaN values
          const rawPayload = line.slice(6)
          const sanitizedPayload = rawPayload.replace(/\bNaN\b/g, 'null')
          let event: StreamEvent
          try {
            event = JSON.parse(sanitizedPayload) as StreamEvent
          } catch (e) {
            console.error('Error parsing stream event:', e)
            continue
          }

          console.log('Stream event:', event)

          // Hard stream failures must escape the parse loop
          if (event.error != null) {
            throw new Error(String(event.error))
          }
          if (event.artifacts) {
            scienceArtifacts = filterScienceArtifacts(event.artifacts)
          }

          if (event.phase === 1 && event.status === 'colors_streaming') {
            const progressPct = (event.progress ?? 0) * 100
            onProgress?.(progressPct)
            if (event.colors && event.colors.length > 0) {
              extractedColors.push(...event.colors)
              onIncrementalColors?.(event.colors, extractedColors.length)
            }
          } else if (event.phase === 2 && event.status === 'extraction_complete') {
            extractedColors.push(...(event.colors ?? []))
            shadows.push(...(event.shadows ?? []))
            backgrounds.push(...(event.background_colors ?? []))
            ramps = event.ramps ?? ramps
            debugOverlay = event.debug?.overlay_png_base64 ?? debugOverlay
            segmentation = event.debug?.segmented_palette ?? segmentation
            paletteSummary = event.summary ?? null
          } else if (event.phase === 3 && event.status === 'ai_enhancement_complete') {
            if (event.colors && event.colors.length > 0) {
              extractedColors = extractedColors.map((color, idx) => {
                if (idx < event.colors!.length) {
                  const aiEnhancement = event.colors![idx]
                  return {
                    ...color,
                    name: aiEnhancement.name ?? color.name,
                    design_intent: aiEnhancement.design_intent ?? color.design_intent,
                    semantic_names: aiEnhancement.semantic_names ?? color.semantic_names,
                    confidence: aiEnhancement.confidence ?? color.confidence,
                    usage: aiEnhancement.usage ?? color.usage,
                    prominence_percentage:
                      aiEnhancement.prominence_percentage ?? color.prominence_percentage,
                  }
                }
                return color
              })
            }
            onProgress?.(100)
          } else if (event.phase === 3 && event.status === 'ai_enhancement_failed') {
            console.warn('Phase 3 AI enhancement failed:', event.message)
            onProgress?.(100)
          }
        }
      }

      return {
        extractedColors,
        shadows,
        backgrounds,
        ramps,
        debugOverlay,
        segmentation,
        paletteSummary,
        scienceArtifacts,
      }
    },
    []
  )

  return { parseColorStream }
}

/**
 * Hook for parallel extraction phases (spacing, shadows, typography)
 */
export function useParallelExtractions() {
  interface ShadowExtractionResult {
    tokens: any[]
    extractionConfidence?: number
    extractionMetadata?: Record<string, unknown> | null
    warnings?: string[] | null
    artifacts?: ArtifactBundle | null
  }

  const extractSpacing = useCallback(
    async (
      base64: string,
      mediaType: string,
      projectId: number,
    ): Promise<SpacingExtractionResponse | ParallelExtractFailure> => {
      try {
        const resp = await fetch(`${API_BASE_URL}/spacing/extract`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            image_base64: base64,
            image_media_type: mediaType,
            project_id: projectId,
            max_tokens: 15,
          }),
        })
        if (resp.ok) {
          return (await resp.json()) as SpacingExtractionResponse
        }
        return {
          ok: false,
          error: await readApiErrorDetail(resp, 'Spacing extraction failed'),
        }
      } catch (err) {
        console.warn('Spacing extraction failed', err)
        return {
          ok: false,
          error: err instanceof Error ? err.message : 'Spacing extraction failed',
        }
      }
    },
    [],
  )

  const extractShadows = useCallback(
    async (
      base64: string,
      mediaType: string,
      projectId?: number,
    ): Promise<(ShadowExtractionResult & { ok: true }) | ParallelExtractFailure> => {
      try {
        const resp = await fetch(`${API_BASE_URL}/shadows/extract`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            image_base64: base64,
            image_media_type: mediaType,
            project_id: projectId,
            max_tokens: 20,
            include_artifacts: true,
          }),
        })
        if (resp.ok) {
          const data = await resp.json()
          const rawTokens = data?.tokens ?? []
          const tokens = Array.isArray(rawTokens)
            ? rawTokens
            : typeof rawTokens === 'object'
              ? Object.values(rawTokens)
              : []

          const metadata =
            data?.extraction_metadata && typeof data.extraction_metadata === 'object'
              ? (data.extraction_metadata as Record<string, unknown>)
              : null
          const metaError =
            metadata && typeof metadata.error === 'string' ? metadata.error.trim() : ''
          if (metaError && tokens.length === 0) {
            return { ok: false, error: `Shadow extraction failed: ${metaError}` }
          }

          return {
            ok: true,
            tokens,
            extractionConfidence:
              typeof data?.extraction_confidence === 'number'
                ? data.extraction_confidence
                : undefined,
            extractionMetadata: metadata,
            warnings: Array.isArray(data?.warnings) ? data.warnings : null,
            artifacts:
              data?.artifacts && typeof data.artifacts === 'object'
                ? (data.artifacts as ArtifactBundle)
                : null,
          }
        }
        return {
          ok: false,
          error: await readApiErrorDetail(resp, 'Shadow extraction failed'),
        }
      } catch (err) {
        console.warn('Shadow extraction failed', err)
        return {
          ok: false,
          error: err instanceof Error ? err.message : 'Shadow extraction failed',
        }
      }
    },
    [],
  )

  const extractTypography = useCallback(
    async (
      base64: string,
      mediaType: string,
      projectId: number,
    ): Promise<any[] | ParallelExtractFailure> => {
      try {
        const resp = await fetch(`${API_BASE_URL}/typography/extract`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            image_base64: base64,
            image_media_type: mediaType,
            project_id: projectId,
            max_tokens: 15,
          }),
        })
        if (resp.ok) {
          const data = await resp.json()
          const tokens = data.typography_tokens || data.tokens || []
          return Array.isArray(tokens) && tokens.length > 0
            ? tokens
            : typeof tokens === 'object'
              ? Object.values(tokens)
              : []
        }
        return {
          ok: false,
          error: await readApiErrorDetail(resp, 'Typography extraction failed'),
        }
      } catch (err) {
        console.warn('Typography extraction failed', err)
        return {
          ok: false,
          error: err instanceof Error ? err.message : 'Typography extraction failed',
        }
      }
    },
    [],
  )

  const extractGradients = useCallback(
    async (
      base64: string,
      mediaType: string,
      projectId?: number,
    ): Promise<{ ok: true; tokens: any[]; extractionConfidence?: number } | ParallelExtractFailure> => {
      try {
        const resp = await fetch(`${API_BASE_URL}/gradients/extract`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            image_base64: base64,
            image_media_type: mediaType,
            project_id: projectId,
            max_tokens: 2,
          }),
        })
        if (resp.ok) {
          const data = await resp.json()
          const rawTokens = data?.tokens ?? []
          const tokens = Array.isArray(rawTokens)
            ? rawTokens
            : typeof rawTokens === 'object'
              ? Object.values(rawTokens)
              : []
          return {
            ok: true,
            tokens,
            extractionConfidence:
              typeof data?.extraction_confidence === 'number'
                ? data.extraction_confidence
                : undefined,
          }
        }
        return {
          ok: false,
          error: await readApiErrorDetail(resp, 'Gradient extraction failed'),
        }
      } catch (err) {
        console.warn('Gradient extraction failed', err)
        return {
          ok: false,
          error: err instanceof Error ? err.message : 'Gradient extraction failed',
        }
      }
    },
    [],
  )

  return { extractSpacing, extractShadows, extractTypography, extractGradients }
}

/**
 * Hook for project management
 */
export function useProjectManagement() {
  const ensureProject = useCallback(async (projectId: number | null, projectName: string) => {
    if (projectId != null) return projectId

    try {
      const response = await ApiClient.createProject(
        projectName,
        'Design token extraction project',
      )
      if (response?.id == null) {
        throw new Error('Failed to create project: API returned no project id')
      }
      return response.id
    } catch (err) {
      const apiErr = err as ApiError
      const detail =
        (typeof apiErr?.detail === 'string' && apiErr.detail.trim()) ||
        (typeof apiErr?.message === 'string' && apiErr.message.trim()) ||
        (typeof apiErr?.error === 'string' && apiErr.error.trim()) ||
        (err instanceof Error ? err.message : null)
      throw new Error(detail ? `Failed to create project: ${detail}` : 'Failed to create project')
    }
  }, [])

  return { ensureProject }
}

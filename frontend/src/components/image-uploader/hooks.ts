import { useState, useCallback } from 'react'
import { ColorToken, SegmentedColor, SpacingExtractionResponse, ColorRampMap } from '../../types'
import { ApiClient } from '../../api/client'
import { resizeImageFile, isValidImageFile, isFileSizeValid } from '../../utils'
import { StreamEvent, ExtractionState } from './types'

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL ?? '/api/v1'

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
      const extractedColors: ColorToken[] = []
      const shadows: any[] = []
      const backgrounds: string[] = []
      let ramps: ColorRampMap = {}
      let debugOverlay: string | null = null
      let segmentation: SegmentedColor[] | null = null

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
          if (line.startsWith('data: ')) {
            try {
              // Sanitize NaN values
              const rawPayload = line.slice(6)
              const sanitizedPayload = rawPayload.replace(/\bNaN\b/g, 'null')
              const event = JSON.parse(sanitizedPayload) as StreamEvent
              console.log('Stream event:', event)

              if (event.error != null) {
                throw new Error(event.error)
              }

              if (event.phase === 1 && event.status === 'colors_streaming') {
                // Report progress
                onProgress?.((event.progress ?? 0) * 100)
                // Report incremental colors if they're included
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
              }
            } catch (e) {
              console.error('Error parsing stream event:', e)
            }
          }
        }
      }

      return { extractedColors, shadows, backgrounds, ramps, debugOverlay, segmentation }
    },
    []
  )

  return { parseColorStream }
}

/**
 * Hook for parallel extraction phases (spacing, shadows, typography)
 */
export function useParallelExtractions() {
  const extractSpacing = useCallback(
    async (base64: string, mediaType: string, projectId: number) => {
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
      } catch (err) {
        console.warn('Spacing extraction failed', err)
      }
      return null
    },
    []
  )

  const extractShadows = useCallback(async (base64: string, mediaType: string) => {
    try {
      const resp = await fetch(`${API_BASE_URL}/shadows/extract`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          image_base64: base64,
          image_media_type: mediaType,
          max_tokens: 20,
        }),
      })
      if (resp.ok) {
        const data = await resp.json()
        const tokens = data.tokens || []
        return Array.isArray(tokens) && tokens.length > 0
          ? tokens
          : typeof tokens === 'object'
            ? Object.values(tokens)
            : []
      }
    } catch (err) {
      console.warn('Shadow extraction failed', err)
    }
    return []
  }, [])

  const extractTypography = useCallback(
    async (base64: string, mediaType: string, projectId: number) => {
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
      } catch (err) {
        console.warn('Typography extraction failed', err)
      }
      return []
    },
    []
  )

  return { extractSpacing, extractShadows, extractTypography }
}

/**
 * Hook for project management
 */
export function useProjectManagement() {
  const ensureProject = useCallback(async (projectId: number | null, projectName: string) => {
    if (projectId != null) return projectId

    try {
      const response = await ApiClient.post<{ id: number }>('/projects', {
        name: projectName,
        description: 'Color extraction project',
      })
      return response.id
    } catch (err) {
      throw new Error('Failed to create project')
    }
  }, [])

  return { ensureProject }
}

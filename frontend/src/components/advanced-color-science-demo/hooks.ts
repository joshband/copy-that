import { useState, useCallback } from 'react'
import type { ColorToken, SpacingToken, PipelineStage } from '../color-science'

/**
 * File upload and image conversion management
 */
export function useImageUpload() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [imageBase64, setImageBase64] = useState<string | null>(null)
  const [imageMediaType, setImageMediaType] = useState<string>('image/png')

  const loadImage = useCallback((file: File) => {
    setSelectedFile(file)
    const reader = new FileReader()
    reader.onload = (e) => {
      const dataUrl = e.target?.result as string
      setPreview(dataUrl)
      const [meta, payload] = (dataUrl || '').split(',', 2)
      if (payload) {
        setImageBase64(payload)
        const mtMatch = meta.match(/data:(.*);base64/)
        setImageMediaType(mtMatch?.[1] || 'image/png')
      }
    }
    reader.readAsDataURL(file)
  }, [])

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) loadImage(file)
  }, [loadImage])

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    const file = e.dataTransfer.files[0]
    if (file && file.type.startsWith('image/')) {
      loadImage(file)
    }
  }, [loadImage])

  return {
    selectedFile,
    preview,
    imageBase64,
    imageMediaType,
    handleFileChange,
    handleDrop,
  }
}

/**
 * Pipeline stage tracking and updates
 */
export function usePipelineStages() {
  const initialStages: PipelineStage[] = [
    { id: 'preprocess', name: 'Preprocess', description: 'Validate, resize, enhance image', status: 'pending' },
    { id: 'extract', name: 'Extract', description: 'AI-powered color detection', status: 'pending' },
    { id: 'aggregate', name: 'Aggregate', description: 'Delta-E deduplication', status: 'pending' },
    { id: 'validate', name: 'Validate', description: 'WCAG accessibility checks', status: 'pending' },
    { id: 'generate', name: 'Generate', description: 'W3C Design Tokens output', status: 'pending' },
  ]

  const [stages, setStages] = useState<PipelineStage[]>(initialStages)

  const resetStages = useCallback(() => {
    setStages(prev => prev.map(s => ({ ...s, status: 'pending', duration: undefined })))
  }, [])

  const updateStage = useCallback((id: string, status: PipelineStage['status'], duration?: number) => {
    setStages(prev => prev.map(s =>
      s.id === id ? { ...s, status, duration } : s
    ))
  }, [])

  return { stages, resetStages, updateStage }
}

/**
 * Extraction state management (colors, spacing, etc.)
 */
export function useExtractionResults() {
  const [colors, setColors] = useState<ColorToken[]>([])
  const [selectedColorIndex, setSelectedColorIndex] = useState<number | null>(null)
  const [paletteDescription, setPaletteDescription] = useState<string>('')
  const [extractorUsed, setExtractorUsed] = useState<string>('')
  const [spacingTokens, setSpacingTokens] = useState<SpacingToken[]>([])
  const [spacingSummary, setSpacingSummary] = useState<string>('')
  const [isExtracting, setIsExtracting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const reset = useCallback(() => {
    setColors([])
    setSelectedColorIndex(null)
    setPaletteDescription('')
    setExtractorUsed('')
    setError(null)
  }, [])

  return {
    colors,
    setColors,
    selectedColorIndex,
    setSelectedColorIndex,
    paletteDescription,
    setPaletteDescription,
    extractorUsed,
    setExtractorUsed,
    spacingTokens,
    setSpacingTokens,
    spacingSummary,
    setSpacingSummary,
    isExtracting,
    setIsExtracting,
    error,
    setError,
    reset,
  }
}

/**
 * Project state management
 */
export function useProjectState() {
  const [projectId, setProjectId] = useState<number>(1)
  const [projectName, setProjectName] = useState<string>('Color Science Demo')
  const [loadProjectId, setLoadProjectId] = useState<string>('1')

  return {
    projectId,
    setProjectId,
    projectName,
    setProjectName,
    loadProjectId,
    setLoadProjectId,
  }
}

/**
 * Utility function
 */
export const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

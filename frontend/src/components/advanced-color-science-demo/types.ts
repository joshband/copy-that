import type { ColorToken, SpacingToken, PipelineStage } from '../color-science'

/**
 * Extraction state for color science demo
 */
export interface ExtractionState {
  selectedFile: File | null
  preview: string | null
  isExtracting: boolean
  error: string | null
  imageBase64: string | null
  imageMediaType: string
  stages: PipelineStage[]
}

/**
 * Project state for saving/loading
 */
export interface ProjectState {
  projectId: number
  projectName: string
  loadProjectId: string
}

/**
 * Color extraction results
 */
export interface ColorExtractionState {
  colors: ColorToken[]
  selectedColorIndex: number | null
  paletteDescription: string
  extractorUsed: string
}

/**
 * Spacing extraction results
 */
export interface SpacingExtractionState {
  spacingTokens: SpacingToken[]
  spacingSummary: string
}

/**
 * Combined application state
 */
export interface DemoState
  extends ExtractionState,
    ProjectState,
    ColorExtractionState,
    SpacingExtractionState {}

/**
 * Props for sub-components
 */
export interface UploadSectionProps {
  preview: string | null
  isExtracting: boolean
  selectedFile: File | null
  onFileChange: (e: React.ChangeEvent<HTMLInputElement>) => void
  onDrop: (e: React.DragEvent<HTMLDivElement>) => void
  onExtract: () => Promise<void>
}

export interface ExtractionPanelProps {
  isExtracting: boolean
  error: string | null
  colors: ColorToken[]
  spacingTokens: SpacingToken[]
  selectedColorIndex: number | null
  extractorUsed: string
  paletteDescription: string
  spacingSummary: string
  onSelectColor: (index: number | null) => void
}

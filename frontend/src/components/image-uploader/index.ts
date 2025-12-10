// Re-export main component
export { default as ImageUploader } from './ImageUploader'
export type { default as ImageUploaderComponent } from './ImageUploader'

// Re-export sub-components
export { UploadArea } from '../ui/input/UploadArea'
export { PreviewSection } from './PreviewSection'
export { SettingsPanel } from './SettingsPanel'
export { ExtractButton } from './ExtractButton'
export { ProjectInfo } from './ProjectInfo'

// Re-export hooks
export { useImageFile, useStreamingExtraction, useParallelExtractions, useProjectManagement } from './hooks'

// Re-export types
export type { StreamEvent, ImageMetadata, ExtractionState } from './types'

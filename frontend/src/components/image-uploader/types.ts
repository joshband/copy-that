// Shared types for ImageUploader components
import {
  ArtifactBundle,
  ColorToken,
  SegmentedColor,
  ColorRampMap,
} from '../../types'

export interface StreamEvent {
  error?: string
  phase?: number
  status?: string
  color_count?: number
  progress?: number
  summary?: string
  message?: string
  colors?: ColorToken[]
  shadows?: any[]
  background_colors?: string[]
  text_roles?: Array<{ hex: string; role: string; contrast?: number }>
  ramps?: ColorRampMap
  debug?: { overlay_png_base64?: string; segmented_palette?: SegmentedColor[] }
  artifacts?: ArtifactBundle | null
}

export interface ImageMetadata {
  file: File | null
  preview: string | null
  base64: string | null
  mediaType: string
}

export interface ExtractionState {
  colors: ColorToken[]
  shadows: any[]
  backgrounds: string[]
  ramps: ColorRampMap
  debugOverlay: string | null
  segmentation: SegmentedColor[] | null
  scienceArtifacts?: ArtifactBundle | null
}

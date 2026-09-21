// Re-export ColorToken from main types (single source of truth)
import type { ColorToken } from '../../types'
export type { ColorToken }

// Keep only color-science specific types below
interface ColorTokenLocal {
  id?: number
  hex: string
  rgb?: string
  hsl?: string
  hsv?: string
  name: string
  design_intent?: string
  semantic_names?: Record<string, unknown> | null
  confidence: number
  harmony?: string
  temperature?: string
  saturation_level?: string
  lightness_level?: string
  category?: string
  usage?: string | string[]
  wcag_contrast_on_white?: number
  wcag_contrast_on_black?: number
  wcag_aa_compliant_text?: boolean
  wcag_aaa_compliant_text?: boolean
  wcag_aa_compliant_normal?: boolean
  wcag_aaa_compliant_normal?: boolean
  colorblind_safe?: boolean
  tint_color?: string
  shade_color?: string
  tone_color?: string
  closest_web_safe?: string
  closest_css_named?: string
  is_neutral?: boolean
  provenance?: Record<string, number>
  extraction_metadata?: Record<string, unknown>
}

export interface PipelineStage {
  id: string
  name: string
  description: string
  status: 'pending' | 'running' | 'done' | 'error'
  duration?: number
}

export interface ExtractionResult {
  colors: ColorToken[]
  extractor_used: string
  color_palette?: string
}

export interface SpacingToken {
  value_px: number
  value_rem: number
  name: string
  confidence: number
  semantic_role?: string
  spacing_type?: string
  role?: string
  grid_aligned?: boolean
  tailwind_class?: string
}

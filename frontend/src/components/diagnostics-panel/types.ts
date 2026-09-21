import type { ColorToken, SegmentedColor, SpacingExtractionResponse } from '../../types'

export type SpacingEntry = {
  value_px: number
  count: number
  orientation: 'horizontal' | 'vertical' | 'mixed'
}

export type PaletteEntry = {
  hex: string
  coverage: number
  label: string
}

export type Props = {
  colors: ColorToken[]
  spacingResult?: SpacingExtractionResponse | null
  spacingOverlay?: string | null
  colorOverlay?: string | null
  segmentedPalette?: SegmentedColor[] | null
  showAlignment?: boolean
  showPayload?: boolean
}

export const FALLBACK_TOLERANCE = 2

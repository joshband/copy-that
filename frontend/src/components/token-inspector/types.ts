import type { ColorToken, SegmentedColor, SpacingExtractionResponse } from '../types'

export type TokenRow = {
  id: number | string
  type: string
  box: [number, number, number, number]
  polygon?: Array<[number, number]>
  elementType?: string
  color?: string
  text?: string
  source?: string
}

export type Props = {
  spacingResult?: SpacingExtractionResponse | null
  overlayBase64?: string | null
  colors: ColorToken[]
  segmentedPalette?: SegmentedColor[] | null
  showOverlay?: boolean
}

export type ColorMap = Record<string | number, string>

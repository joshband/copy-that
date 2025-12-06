import type { ColorToken } from '../../types'

export interface OverviewNarrativeProps {
  colors: ColorToken[]
  colorCount: number
  aliasCount: number
  spacingCount: number
  multiplesCount: number
  typographyCount: number
}

export type TemperatureType = 'warm' | 'cool' | 'balanced'
export type SaturationType = 'vivid' | 'muted' | 'balanced'
export type ArtMovement =
  | 'Expressionism'
  | 'Fauvism'
  | 'Minimalism'
  | 'Swiss Modernism'
  | 'Brutalism'
  | 'Art Deco'
  | 'Contemporary'
  | 'Neo-Minimalism'
  | 'Postmodernism'
  | 'Modern Design'

export interface EmotionalTone {
  emotion: string
  description: string
}

export type DesignEra =
  | 'Monochromatic Focus'
  | 'Limited Palette Era'
  | 'Structured Harmony'
  | 'Rich Ecosystem'
  | 'Comprehensive System'

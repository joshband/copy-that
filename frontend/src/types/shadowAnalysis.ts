/**
 * TypeScript types for Shadow Analysis API responses
 * Phase 4: Advanced Analysis
 */

/**
 * Light direction tokens - categorical values for key light direction
 */
export type LightDirectionToken =
  | 'upper_left'
  | 'upper_right'
  | 'left'
  | 'right'
  | 'overhead'
  | 'front'
  | 'back'
  | 'unknown'

/**
 * Shadow softness tokens
 */
export type ShadowSoftnessToken = 'very_hard' | 'hard' | 'medium' | 'soft' | 'very_soft'

/**
 * Shadow contrast tokens
 */
export type ShadowContrastToken = 'low' | 'medium' | 'high' | 'very_high'

/**
 * Shadow density tokens (coverage)
 */
export type ShadowDensityToken = 'sparse' | 'moderate' | 'heavy' | 'full'

/**
 * Shadow intensity tokens
 */
export type ShadowIntensityToken = 'very_light' | 'light' | 'medium' | 'dark' | 'very_dark'

/**
 * Lit region intensity tokens
 */
export type LitIntensityToken = 'very_dark' | 'dark' | 'medium' | 'bright' | 'very_bright'

/**
 * Overall lighting style tokens
 */
export type LightingStyleToken = 'directional' | 'rim' | 'diffuse' | 'mixed' | 'complex'

/**
 * Light direction in radians (azimuth and elevation)
 */
export interface LightDirection {
  azimuth: number
  elevation: number
}

/**
 * CSS box-shadow suggestions from analysis
 */
export interface CSSBoxShadowSuggestions {
  subtle: string
  medium: string
  prominent: string
  dramatic: string
}

/**
 * Shadow analysis tokens (categorical)
 */
export interface ShadowAnalysisTokens {
  style_key_direction: LightDirectionToken
  style_softness: ShadowSoftnessToken
  style_contrast: ShadowContrastToken
  style_density: ShadowDensityToken
  intensity_shadow: ShadowIntensityToken
  intensity_lit: LitIntensityToken
  lighting_style: LightingStyleToken
  extraction_confidence: number
}

/**
 * Shadow analysis features (numeric)
 */
export interface ShadowAnalysisFeatures {
  shadow_area_fraction: number
  mean_shadow_intensity: number
  mean_lit_intensity: number
  mean_shadow_to_lit_ratio: number
  shadow_contrast: number
  edge_softness_mean: number
  edge_softness_std: number
  shadow_count_major: number
  light_direction_confidence: number
  inconsistency_score?: number
  dominant_light_direction?: LightDirection
}

/**
 * Full lighting analysis response from API
 */
export interface LightingAnalysisResponse {
  // Tokens (categorical)
  style_key_direction: LightDirectionToken
  style_softness: ShadowSoftnessToken
  style_contrast: ShadowContrastToken
  style_density: ShadowDensityToken
  intensity_shadow: ShadowIntensityToken
  intensity_lit: LitIntensityToken
  lighting_style: LightingStyleToken

  // Features (numeric)
  shadow_area_fraction: number
  mean_shadow_intensity: number
  mean_lit_intensity: number
  shadow_contrast: number
  edge_softness_mean: number

  // Light direction
  light_direction: LightDirection | null
  light_direction_confidence: number

  // Diagnostics
  extraction_confidence: number
  shadow_count_major: number

  // CSS suggestions
  css_box_shadow: CSSBoxShadowSuggestions

  // Metadata
  image_id: string | null
  analysis_source: string
}

/**
 * Analysis request parameters
 */
export interface LightingAnalysisRequest {
  image_url?: string
  image_base64?: string
  image_media_type?: string
  image_id?: string
  use_geometry?: boolean
  device?: 'cpu' | 'cuda'
}

/**
 * Quality score breakdown
 */
export interface QualityScoreBreakdown {
  overall: number
  consistency: number
  confidence: number
  clarity: number
}

/**
 * Helper to compute quality score from analysis
 */
export function computeQualityScore(analysis: LightingAnalysisResponse): QualityScoreBreakdown {
  const confidence = analysis.extraction_confidence
  const lightConfidence = analysis.light_direction_confidence
  const consistency = 1 - (analysis.shadow_contrast > 0.8 ? 0.2 : 0)
  const clarity = analysis.edge_softness_mean < 0.3 ? 1 : analysis.edge_softness_mean < 0.6 ? 0.7 : 0.5

  const overall = (confidence * 0.4 + lightConfidence * 0.3 + consistency * 0.15 + clarity * 0.15)

  return {
    overall,
    confidence,
    consistency,
    clarity,
  }
}

/**
 * Get human-readable label for light direction
 */
export function getLightDirectionLabel(direction: LightDirectionToken): string {
  const labels: Record<LightDirectionToken, string> = {
    upper_left: 'Upper Left',
    upper_right: 'Upper Right',
    left: 'Left',
    right: 'Right',
    overhead: 'Overhead',
    front: 'Front',
    back: 'Back',
    unknown: 'Unknown',
  }
  return labels[direction] || direction
}

/**
 * Get human-readable label for lighting style
 */
export function getLightingStyleLabel(style: LightingStyleToken): string {
  const labels: Record<LightingStyleToken, string> = {
    directional: 'Directional',
    rim: 'Rim Light',
    diffuse: 'Diffuse / Ambient',
    mixed: 'Mixed Lighting',
    complex: 'Complex Multi-Source',
  }
  return labels[style] || style
}

/**
 * Convert azimuth to compass direction
 */
export function azimuthToCompassDirection(azimuthRad: number): string {
  const azimuthDeg = (azimuthRad * 180) / Math.PI
  const normalized = ((azimuthDeg % 360) + 360) % 360

  if (normalized < 22.5 || normalized >= 337.5) return 'N'
  if (normalized < 67.5) return 'NE'
  if (normalized < 112.5) return 'E'
  if (normalized < 157.5) return 'SE'
  if (normalized < 202.5) return 'S'
  if (normalized < 247.5) return 'SW'
  if (normalized < 292.5) return 'W'
  return 'NW'
}

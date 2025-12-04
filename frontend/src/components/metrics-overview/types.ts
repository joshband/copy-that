export interface ElaboratedMetric {
  primary: string
  elaborations: string[]
  confidence?: number
}

export interface OverviewMetricsData {
  spacing_scale_system: string | null
  spacing_uniformity: number
  color_harmony_type: string | null
  color_palette_type: string | null
  color_temperature: string | null
  typography_hierarchy_depth: number
  typography_scale_type: string | null
  design_system_maturity: string
  token_organization_quality: string
  insights: string[]
  art_movement: ElaboratedMetric | null
  emotional_tone: ElaboratedMetric | null
  design_complexity: ElaboratedMetric | null
  saturation_character: ElaboratedMetric | null
  temperature_profile: ElaboratedMetric | null
  design_system_insight: ElaboratedMetric | null
  summary: {
    total_colors: number
    total_spacing: number
    total_typography: number
    total_shadows: number
  }
  // Source tracking
  source?: {
    has_extracted_colors: boolean
    has_extracted_spacing: boolean
    has_extracted_typography: boolean
  }
}

export interface MetricsOverviewProps {
  projectId: number | null
  refreshTrigger?: number // Trigger refetch when tokens change
}

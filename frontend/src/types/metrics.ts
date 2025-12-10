/**
 * Metrics Types
 *
 * TypeScript interfaces for the 3-tier metrics system:
 * - TIER 1: Quantitative (fast, ~50ms)
 * - TIER 2: Accessibility (fast, ~100ms)
 * - TIER 3: Qualitative (slow, 5-15s, AI-powered)
 */

/**
 * TIER 1: Quantitative Metrics
 * Fast, deterministic metrics based on token counts and basic heuristics
 */
export interface QuantitativeMetrics {
  color_count: number
  spacing_count: number
  typography_count: number
  system_maturity: 'beginner' | 'intermediate' | 'advanced'
  scale_consistency: number  // 0-100
  token_diversity: number    // 0-100
}

/**
 * TIER 2: Accessibility Metrics
 * WCAG compliance and colorblind safety checks
 */
export interface AccessibilityMetrics {
  wcag_aa_pass_rate: number        // 0-100
  wcag_aaa_pass_rate: number       // 0-100
  colorblind_safe_count: number
  total_color_pairs: number
  avg_contrast_ratio: number
  min_contrast_ratio: number
  max_contrast_ratio: number
  violations: Array<{
    type: string
    severity: 'error' | 'warning'
    message: string
  }>
}

/**
 * TIER 3: Qualitative Metrics
 * AI-powered design insights from Claude Sonnet 4.5
 */
export interface QualitativeMetrics {
  design_pattern: string           // e.g., "Material Design", "iOS Human Interface"
  pattern_confidence: number       // 0-100
  system_maturity: 'beginner' | 'intermediate' | 'advanced'
  maturity_reasoning: string
  consistency_score: number        // 0-100
  health_score: number            // 0-100
  recommendations: string[]        // 3-5 actionable items
  accessibility_insights: string[] // Beyond WCAG
}

/**
 * Combined metrics from all tiers
 */
export interface ProjectMetrics {
  tier_1?: QuantitativeMetrics
  tier_2?: AccessibilityMetrics
  tier_3?: QualitativeMetrics | null  // null if ANTHROPIC_API_KEY unavailable
}

/**
 * SSE event structure for streaming
 */
export interface MetricsStreamEvent {
  tier: 'tier_1' | 'tier_2' | 'tier_3'
  data: QuantitativeMetrics | AccessibilityMetrics | QualitativeMetrics | null
  timestamp?: string
}

/**
 * Complete event sent at end of stream
 */
export interface MetricsCompleteEvent {
  event: 'complete'
  total_time: number
  tiers_completed: number
}

/**
 * Error event for stream failures
 */
export interface MetricsErrorEvent {
  event: 'error'
  tier?: string
  message: string
}

/**
 * Union type for all SSE events
 */
export type MetricsEvent = MetricsStreamEvent | MetricsCompleteEvent | MetricsErrorEvent

/**
 * Hook state for useStreamingMetrics
 */
export interface MetricsState {
  metrics: ProjectMetrics
  loading: boolean
  error: string | null
  isStreaming: boolean
  tiersCompleted: number
  totalTime: number | null
}

/**
 * Provider info from /api/metrics/providers
 */
export interface MetricsProvider {
  name: string
  tier: 'tier_1' | 'tier_2' | 'tier_3'
  priority: number
}

export interface MetricsProvidersResponse {
  providers: MetricsProvider[]
  count: number
}

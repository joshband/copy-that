/**
 * ShadowQualityMetrics Component
 * Phase 4: Advanced Analysis
 *
 * Displays numeric quality metrics for shadow analysis
 */

import { useMemo } from 'react'
import type {
  ShadowSoftnessToken,
  ShadowContrastToken,
  ShadowDensityToken,
  ShadowIntensityToken,
  LitIntensityToken,
} from '../../types/shadowAnalysis'
import './ShadowQualityMetrics.css'

export interface ShadowQualityMetricsProps {
  /** Shadow area fraction (0-1) */
  shadowAreaFraction?: number
  /** Mean shadow intensity (0-1) */
  meanShadowIntensity?: number
  /** Mean lit region intensity (0-1) */
  meanLitIntensity?: number
  /** Shadow contrast (0-1) */
  shadowContrast?: number
  /** Edge softness mean (0-1) */
  edgeSoftness?: number
  /** Number of major shadows detected */
  shadowCount?: number
  /** Extraction confidence (0-1) */
  confidence?: number
  /** Categorical tokens */
  tokens?: {
    softness?: ShadowSoftnessToken
    contrast?: ShadowContrastToken
    density?: ShadowDensityToken
    intensityShadow?: ShadowIntensityToken
    intensityLit?: LitIntensityToken
  }
  /** Layout orientation */
  layout?: 'horizontal' | 'vertical' | 'grid'
  /** Compact mode */
  compact?: boolean
}

interface MetricBarProps {
  label: string
  value: number
  token?: string
  color?: 'blue' | 'green' | 'amber' | 'purple' | 'slate'
  showPercentage?: boolean
}

function MetricBar({ label, value, token, color = 'blue', showPercentage = true }: MetricBarProps) {
  const percentage = Math.round(value * 100)
  const clampedWidth = Math.min(Math.max(percentage, 0), 100)

  return (
    <div className="metric-bar-container">
      <div className="metric-bar-header">
        <span className="metric-bar-label">{label}</span>
        <div className="metric-bar-values">
          {token && <span className="metric-token">{token}</span>}
          {showPercentage && <span className="metric-percentage">{percentage}%</span>}
        </div>
      </div>
      <div className="metric-bar-track">
        <div
          className={`metric-bar-fill color-${color}`}
          style={{ width: `${clampedWidth}%` }}
        />
      </div>
    </div>
  )
}

interface MetricCardProps {
  label: string
  value: number | string
  subtitle?: string
  icon?: string
  variant?: 'default' | 'success' | 'warning' | 'error'
}

function MetricCard({ label, value, subtitle, variant = 'default' }: MetricCardProps) {
  return (
    <div className={`metric-card variant-${variant}`}>
      <div className="metric-card-value">{value}</div>
      <div className="metric-card-label">{label}</div>
      {subtitle && <div className="metric-card-subtitle">{subtitle}</div>}
    </div>
  )
}

export function ShadowQualityMetrics({
  shadowAreaFraction = 0,
  meanShadowIntensity = 0,
  meanLitIntensity = 0,
  shadowContrast = 0,
  edgeSoftness = 0,
  shadowCount = 0,
  confidence = 0,
  tokens,
  layout = 'grid',
  compact = false,
}: ShadowQualityMetricsProps) {
  // Calculate derived metrics
  const contrastRatio = useMemo(() => {
    if (meanShadowIntensity === 0) return Infinity
    return meanLitIntensity / meanShadowIntensity
  }, [meanLitIntensity, meanShadowIntensity])

  const qualityScore = useMemo(() => {
    // Weighted quality score based on various factors
    const weights = {
      confidence: 0.4,
      contrast: 0.2,
      edgeClarity: 0.2,
      coverage: 0.2,
    }

    // Edge clarity is inverse of extreme softness
    const edgeClarity = edgeSoftness < 0.3 ? 1 : edgeSoftness < 0.6 ? 0.7 : 0.4

    // Coverage score - moderate coverage is ideal
    const coverageScore =
      shadowAreaFraction < 0.05
        ? 0.3
        : shadowAreaFraction < 0.3
          ? 1
          : shadowAreaFraction < 0.6
            ? 0.7
            : 0.4

    // Contrast score - higher is better for design
    const contrastScore = shadowContrast

    return (
      weights.confidence * confidence +
      weights.contrast * contrastScore +
      weights.edgeClarity * edgeClarity +
      weights.coverage * coverageScore
    )
  }, [confidence, shadowContrast, edgeSoftness, shadowAreaFraction])

  const confidenceVariant = useMemo(() => {
    if (confidence >= 0.8) return 'success'
    if (confidence >= 0.5) return 'warning'
    return 'error'
  }, [confidence])

  if (compact) {
    return (
      <div className="shadow-quality-metrics compact">
        <div className="compact-metrics">
          <div className="compact-metric">
            <span className="compact-label">Coverage</span>
            <span className="compact-value">{Math.round(shadowAreaFraction * 100)}%</span>
          </div>
          <div className="compact-metric">
            <span className="compact-label">Contrast</span>
            <span className="compact-value">{Math.round(shadowContrast * 100)}%</span>
          </div>
          <div className="compact-metric">
            <span className="compact-label">Softness</span>
            <span className="compact-value">{tokens?.softness || 'N/A'}</span>
          </div>
          <div className="compact-metric">
            <span className="compact-label">Quality</span>
            <span className={`compact-value quality-${confidenceVariant}`}>
              {Math.round(qualityScore * 100)}%
            </span>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={`shadow-quality-metrics layout-${layout}`}>
      {/* Summary Cards */}
      <div className="metrics-summary">
        <MetricCard
          label="Quality Score"
          value={`${Math.round(qualityScore * 100)}%`}
          subtitle="Overall shadow quality"
          variant={confidenceVariant}
        />
        <MetricCard
          label="Shadows Found"
          value={shadowCount}
          subtitle="Major shadow regions"
        />
        <MetricCard
          label="Contrast Ratio"
          value={contrastRatio === Infinity ? 'High' : `${contrastRatio.toFixed(1)}:1`}
          subtitle="Light vs shadow"
        />
        <MetricCard
          label="Confidence"
          value={`${Math.round(confidence * 100)}%`}
          subtitle="Detection reliability"
          variant={confidenceVariant}
        />
      </div>

      {/* Detail Bars */}
      <div className="metrics-bars">
        <MetricBar
          label="Shadow Coverage"
          value={shadowAreaFraction}
          token={tokens?.density}
          color="purple"
        />
        <MetricBar
          label="Shadow Contrast"
          value={shadowContrast}
          token={tokens?.contrast}
          color="blue"
        />
        <MetricBar
          label="Edge Softness"
          value={edgeSoftness}
          token={tokens?.softness}
          color="green"
        />
        <MetricBar
          label="Shadow Intensity"
          value={meanShadowIntensity}
          token={tokens?.intensityShadow}
          color="slate"
        />
        <MetricBar
          label="Lit Region Intensity"
          value={meanLitIntensity}
          token={tokens?.intensityLit}
          color="amber"
        />
      </div>

      {/* Token Pills */}
      {tokens && (
        <div className="metrics-tokens">
          <span className="tokens-label">Detected Characteristics:</span>
          <div className="token-pills">
            {tokens.softness && <span className="token-pill softness">{tokens.softness}</span>}
            {tokens.contrast && <span className="token-pill contrast">{tokens.contrast}</span>}
            {tokens.density && <span className="token-pill density">{tokens.density}</span>}
          </div>
        </div>
      )}
    </div>
  )
}

export default ShadowQualityMetrics

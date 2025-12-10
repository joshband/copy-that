/**
 * MetricsDisplay Component
 *
 * Displays project metrics with progressive loading from SSE stream
 * Shows TIER 1 → TIER 2 → TIER 3 as they arrive
 */

import React from 'react'
import { Loader2, CheckCircle2, AlertCircle, TrendingUp, Shield, Lightbulb } from 'lucide-react'
import type {
  QuantitativeMetrics,
  AccessibilityMetrics,
  QualitativeMetrics,
  MetricsState,
} from '../../types/metrics'

interface MetricsDisplayProps {
  metricsState: MetricsState
  compact?: boolean
}

/**
 * MetricsDisplay Component
 *
 * Renders all three tiers of metrics with loading states
 */
export function MetricsDisplay({ metricsState, compact = false }: MetricsDisplayProps) {
  const { metrics, loading, error, isStreaming, tiersCompleted, totalTime } = metricsState

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <div className="flex items-center gap-2 text-red-700">
          <AlertCircle className="w-5 h-5" />
          <span className="font-semibold">Error loading metrics</span>
        </div>
        <p className="text-sm text-red-600 mt-2">{error}</p>
      </div>
    )
  }

  if (loading && !metrics.tier_1) {
    return (
      <div className="p-8 flex flex-col items-center justify-center gap-3">
        <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
        <p className="text-sm text-gray-600">Loading metrics...</p>
      </div>
    )
  }

  return (
    <div className={compact ? 'space-y-3' : 'space-y-6'}>
      {/* TIER 1: Quantitative Metrics */}
      {metrics.tier_1 ? (
        <QuantitativeMetricsDisplay data={metrics.tier_1} compact={compact} />
      ) : (
        <MetricsSkeleton tier="tier_1" />
      )}

      {/* TIER 2: Accessibility Metrics */}
      {metrics.tier_2 ? (
        <AccessibilityMetricsDisplay data={metrics.tier_2} compact={compact} />
      ) : isStreaming && tiersCompleted >= 1 ? (
        <MetricsLoading tier="tier_2" />
      ) : (
        <MetricsSkeleton tier="tier_2" />
      )}

      {/* TIER 3: Qualitative Metrics */}
      {metrics.tier_3 ? (
        <QualitativeMetricsDisplay data={metrics.tier_3} compact={compact} />
      ) : isStreaming && tiersCompleted >= 2 ? (
        <MetricsLoading tier="tier_3" />
      ) : (
        <MetricsSkeleton tier="tier_3" />
      )}

      {/* Footer: Total Time */}
      {totalTime !== null && (
        <div className="text-xs text-gray-500 text-right">
          Total analysis time: {totalTime.toFixed(2)}s
        </div>
      )}
    </div>
  )
}

/**
 * TIER 1: Quantitative Metrics Display
 */
function QuantitativeMetricsDisplay({
  data,
  compact,
}: {
  data: QuantitativeMetrics
  compact: boolean
}) {
  return (
    <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
      <div className="flex items-center gap-2 mb-3">
        <TrendingUp className="w-5 h-5 text-blue-600" />
        <h3 className="font-semibold text-blue-900">System Overview</h3>
        <CheckCircle2 className="w-4 h-4 text-green-600 ml-auto" />
      </div>

      <div className="grid grid-cols-2 gap-3">
        <MetricCard
          label="Colors"
          value={data.color_count}
          compact={compact}
        />
        <MetricCard
          label="Spacing"
          value={data.spacing_count}
          compact={compact}
        />
        <MetricCard
          label="Typography"
          value={data.typography_count}
          compact={compact}
        />
        <MetricCard
          label="Maturity"
          value={data.system_maturity}
          compact={compact}
        />
      </div>

      {!compact && (
        <div className="mt-3 grid grid-cols-2 gap-3">
          <ProgressBar
            label="Scale Consistency"
            value={data.scale_consistency}
          />
          <ProgressBar
            label="Token Diversity"
            value={data.token_diversity}
          />
        </div>
      )}
    </div>
  )
}

/**
 * TIER 2: Accessibility Metrics Display
 */
function AccessibilityMetricsDisplay({
  data,
  compact,
}: {
  data: AccessibilityMetrics
  compact: boolean
}) {
  return (
    <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
      <div className="flex items-center gap-2 mb-3">
        <Shield className="w-5 h-5 text-green-600" />
        <h3 className="font-semibold text-green-900">Accessibility</h3>
        <CheckCircle2 className="w-4 h-4 text-green-600 ml-auto" />
      </div>

      <div className="grid grid-cols-2 gap-3">
        <ProgressBar
          label="WCAG AA Pass Rate"
          value={data.wcag_aa_pass_rate}
        />
        <ProgressBar
          label="WCAG AAA Pass Rate"
          value={data.wcag_aaa_pass_rate}
        />
      </div>

      {!compact && (
        <div className="mt-3 space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-700">Colorblind Safe</span>
            <span className="font-semibold text-green-700">
              {data.colorblind_safe_count} / {data.total_color_pairs}
            </span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-700">Contrast Range</span>
            <span className="font-semibold text-green-700">
              {data.min_contrast_ratio.toFixed(1)} - {data.max_contrast_ratio.toFixed(1)}
            </span>
          </div>

          {data.violations.length > 0 && (
            <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded">
              <p className="text-xs font-semibold text-yellow-800 mb-2">
                {data.violations.length} Violations
              </p>
              <ul className="text-xs text-yellow-700 space-y-1">
                {data.violations.slice(0, 3).map((v, i) => (
                  <li key={i}>• {v.message}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

/**
 * TIER 3: Qualitative Metrics Display
 */
function QualitativeMetricsDisplay({
  data,
  compact,
}: {
  data: QualitativeMetrics | null
  compact: boolean
}) {
  if (data === null) {
    return (
      <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
        <div className="flex items-center gap-2">
          <Lightbulb className="w-5 h-5 text-gray-400" />
          <p className="text-sm text-gray-600">
            AI insights unavailable (no API key configured)
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
      <div className="flex items-center gap-2 mb-3">
        <Lightbulb className="w-5 h-5 text-purple-600" />
        <h3 className="font-semibold text-purple-900">AI Insights</h3>
        <CheckCircle2 className="w-4 h-4 text-green-600 ml-auto" />
      </div>

      <div className="space-y-3">
        {/* Design Pattern */}
        <div>
          <p className="text-sm text-gray-700 font-medium">Design Pattern</p>
          <p className="text-lg font-semibold text-purple-900">
            {data.design_pattern}
          </p>
          <p className="text-xs text-gray-600">
            Confidence: {data.pattern_confidence}%
          </p>
        </div>

        {/* Health Scores */}
        {!compact && (
          <div className="grid grid-cols-2 gap-3">
            <ProgressBar
              label="Consistency Score"
              value={data.consistency_score}
            />
            <ProgressBar
              label="Health Score"
              value={data.health_score}
            />
          </div>
        )}

        {/* Recommendations */}
        {!compact && data.recommendations.length > 0 && (
          <div>
            <p className="text-sm font-semibold text-purple-900 mb-2">
              Recommendations
            </p>
            <ul className="text-sm text-gray-700 space-y-1">
              {data.recommendations.map((rec, i) => (
                <li key={i}>• {rec}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Accessibility Insights */}
        {!compact && data.accessibility_insights.length > 0 && (
          <div>
            <p className="text-sm font-semibold text-purple-900 mb-2">
              Accessibility Insights
            </p>
            <ul className="text-sm text-gray-700 space-y-1">
              {data.accessibility_insights.map((insight, i) => (
                <li key={i}>• {insight}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}

/**
 * Loading state for a specific tier
 */
function MetricsLoading({ tier }: { tier: string }) {
  const tierLabels = {
    tier_1: 'Loading quantitative metrics...',
    tier_2: 'Analyzing accessibility...',
    tier_3: 'Generating AI insights...',
  }

  return (
    <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
      <div className="flex items-center gap-3">
        <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
        <p className="text-sm text-gray-600">
          {tierLabels[tier as keyof typeof tierLabels]}
        </p>
      </div>
    </div>
  )
}

/**
 * Skeleton placeholder for a tier
 */
function MetricsSkeleton({ tier }: { tier: string }) {
  return (
    <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg opacity-50">
      <div className="h-6 w-32 bg-gray-300 rounded mb-3 animate-pulse" />
      <div className="space-y-2">
        <div className="h-4 w-full bg-gray-300 rounded animate-pulse" />
        <div className="h-4 w-3/4 bg-gray-300 rounded animate-pulse" />
      </div>
    </div>
  )
}

/**
 * Metric Card - Display a single metric
 */
function MetricCard({
  label,
  value,
  compact,
}: {
  label: string
  value: string | number
  compact: boolean
}) {
  return (
    <div className={compact ? 'p-2' : 'p-3'} >
      <p className="text-xs text-gray-600">{label}</p>
      <p className={`font-semibold ${compact ? 'text-base' : 'text-lg'}`}>
        {value}
      </p>
    </div>
  )
}

/**
 * Progress Bar - Display a percentage value
 */
function ProgressBar({ label, value }: { label: string; value: number }) {
  const getColor = (val: number) => {
    if (val >= 80) return 'bg-green-500'
    if (val >= 60) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  return (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span className="text-gray-700">{label}</span>
        <span className="font-semibold text-gray-900">{value}%</span>
      </div>
      <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full ${getColor(value)} transition-all duration-300`}
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  )
}

export default MetricsDisplay

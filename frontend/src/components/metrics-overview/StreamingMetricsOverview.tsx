/**
 * StreamingMetricsOverview Component
 *
 * Enhanced metrics overview using streaming SSE endpoint
 * Progressively displays TIER 1 → TIER 2 → TIER 3 metrics
 */

import React from 'react'
import { useStreamingMetrics } from '../../shared/hooks/useStreamingMetrics'
import { MetricsDisplay } from '../metrics/MetricsDisplay'
import type { MetricsOverviewProps } from './types'

export function StreamingMetricsOverview({ projectId, refreshTrigger }: MetricsOverviewProps) {
  // Enable streaming only when projectId is available
  const metricsState = useStreamingMetrics(projectId, projectId !== null)

  // Don't render if no project
  if (projectId === null) {
    return null
  }

  // Show loading state initially
  if (metricsState.loading && !metricsState.metrics.tier_1) {
    return (
      <div className="space-y-4">
        <p className="text-gray-500 text-sm">Analyzing your design system...</p>
      </div>
    )
  }

  // Show error state
  if (metricsState.error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <p className="text-sm text-red-700">
          Failed to load metrics: {metricsState.error}
        </p>
      </div>
    )
  }

  // Render metrics display
  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <MetricsDisplay metricsState={metricsState} compact={false} />
      </div>
    </div>
  )
}

export default StreamingMetricsOverview

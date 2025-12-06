import { useEffect, useState } from 'react'
import { ApiClient } from '../../api/client'
import type { OverviewMetricsData } from './types'

export function useMetricsData(projectId: number | null, refreshTrigger?: number) {
  const [metrics, setMetrics] = useState<OverviewMetricsData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!projectId) {
      setMetrics(null)
      setError(null)
      return
    }

    const loadMetrics = async () => {
      setLoading(true)
      setError(null)
      try {
        const data = await ApiClient.getOverviewMetrics(projectId)
        setMetrics(data)
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to load metrics'
        console.error('Failed to load overview metrics:', err)
        setError(errorMessage)
      } finally {
        setLoading(false)
      }
    }

    loadMetrics()
  }, [projectId, refreshTrigger])

  return { metrics, loading, error }
}

export function useDataValidation(metrics: OverviewMetricsData | null) {
  return (
    metrics?.source &&
    (metrics.source.has_extracted_colors ||
      metrics.source.has_extracted_spacing ||
      metrics.source.has_extracted_typography)
  )
}

export function getConfidenceColor(confidence?: number): string {
  if (!confidence) return 'bg-gray-100 text-gray-700'
  if (confidence >= 75) return 'bg-green-100 text-green-700'
  if (confidence >= 60) return 'bg-yellow-100 text-yellow-700'
  return 'bg-orange-100 text-orange-700'
}

export function getConfidenceLabel(confidence?: number): string {
  if (!confidence) return 'Calculating...'
  if (confidence >= 75) return 'High Confidence'
  if (confidence >= 60) return 'Likely Match'
  return 'Possible Interpretation'
}

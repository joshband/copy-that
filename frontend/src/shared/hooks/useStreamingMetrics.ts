/**
 * useStreamingMetrics Hook
 *
 * Consumes Server-Sent Events (SSE) from the metrics streaming endpoint
 * Provides progressive loading of metrics: TIER 1 → TIER 2 → TIER 3
 *
 * @example
 * ```tsx
 * function MetricsDashboard({ projectId }: { projectId: number }) {
 *   const { metrics, loading, error, isStreaming } = useStreamingMetrics(projectId)
 *
 *   if (error) return <div>Error: {error}</div>
 *   if (loading && !metrics.tier_1) return <div>Loading...</div>
 *
 *   return (
 *     <div>
 *       {metrics.tier_1 && <QuantitativeDisplay data={metrics.tier_1} />}
 *       {metrics.tier_2 && <AccessibilityDisplay data={metrics.tier_2} />}
 *       {metrics.tier_3 && <QualitativeDisplay data={metrics.tier_3} />}
 *       {isStreaming && <Spinner />}
 *     </div>
 *   )
 * }
 * ```
 */

import { useState, useEffect, useRef, useCallback } from 'react'
import type {
  MetricsState,
  MetricsStreamEvent,
  MetricsCompleteEvent,
  MetricsErrorEvent,
  QuantitativeMetrics,
  AccessibilityMetrics,
  QualitativeMetrics,
} from '../../types/metrics'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

/**
 * useStreamingMetrics Hook
 *
 * Streams metrics from backend using EventSource (SSE)
 * Updates state progressively as each tier completes
 *
 * @param projectId - Project ID to fetch metrics for
 * @param enabled - Whether to start streaming (default: true)
 * @returns Metrics state with progressive updates
 */
export function useStreamingMetrics(
  projectId: number | null,
  enabled: boolean = true
): MetricsState {
  const [state, setState] = useState<MetricsState>({
    metrics: {},
    loading: false,
    error: null,
    isStreaming: false,
    tiersCompleted: 0,
    totalTime: null,
  })

  const eventSourceRef = useRef<EventSource | null>(null)
  const startTimeRef = useRef<number | null>(null)

  /**
   * Handle incoming SSE message
   */
  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const data = JSON.parse(event.data)

      // Handle tier completion events
      if ('tier' in data && 'data' in data) {
        const streamEvent = data as MetricsStreamEvent

        setState((prev) => {
          const newMetrics = { ...prev.metrics }
          const tier = streamEvent.tier

          if (tier === 'tier_1') {
            newMetrics.tier_1 = streamEvent.data as QuantitativeMetrics
          } else if (tier === 'tier_2') {
            newMetrics.tier_2 = streamEvent.data as AccessibilityMetrics
          } else if (tier === 'tier_3') {
            newMetrics.tier_3 = streamEvent.data as QualitativeMetrics | null
          }

          return {
            ...prev,
            metrics: newMetrics,
            tiersCompleted: prev.tiersCompleted + 1,
          }
        })
      }

      // Handle completion event
      else if ('event' in data && data.event === 'complete') {
        const completeEvent = data as MetricsCompleteEvent

        setState((prev) => ({
          ...prev,
          loading: false,
          isStreaming: false,
          totalTime: completeEvent.total_time,
        }))

        // Close the EventSource
        if (eventSourceRef.current) {
          eventSourceRef.current.close()
          eventSourceRef.current = null
        }
      }

      // Handle error event
      else if ('event' in data && data.event === 'error') {
        const errorEvent = data as MetricsErrorEvent

        setState((prev) => ({
          ...prev,
          loading: false,
          isStreaming: false,
          error: errorEvent.message,
        }))

        // Close the EventSource
        if (eventSourceRef.current) {
          eventSourceRef.current.close()
          eventSourceRef.current = null
        }
      }
    } catch (err) {
      console.error('Failed to parse SSE message:', err)
      setState((prev) => ({
        ...prev,
        error: 'Failed to parse server response',
        loading: false,
        isStreaming: false,
      }))
    }
  }, [])

  /**
   * Handle SSE errors
   */
  const handleError = useCallback((event: Event) => {
    console.error('SSE Error:', event)

    setState((prev) => ({
      ...prev,
      error: 'Connection to metrics stream failed',
      loading: false,
      isStreaming: false,
    }))

    // Close the EventSource
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
    }
  }, [])

  /**
   * Start streaming metrics
   */
  useEffect(() => {
    // Don't start if disabled or no project ID
    if (!enabled || projectId === null) {
      return
    }

    // Reset state
    setState({
      metrics: {},
      loading: true,
      error: null,
      isStreaming: true,
      tiersCompleted: 0,
      totalTime: null,
    })

    startTimeRef.current = Date.now()

    // Create EventSource connection
    const url = `${API_BASE_URL}/api/metrics/projects/${projectId}/stream`
    const eventSource = new EventSource(url)
    eventSourceRef.current = eventSource

    // Attach event listeners
    eventSource.onmessage = handleMessage
    eventSource.onerror = handleError

    // Cleanup on unmount
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
        eventSourceRef.current = null
      }
    }
  }, [projectId, enabled, handleMessage, handleError])

  return state
}

/**
 * useMetricsProviders Hook
 *
 * Fetches list of registered metrics providers
 * Useful for displaying available metrics before streaming
 *
 * @example
 * ```tsx
 * function ProvidersList() {
 *   const { providers, loading, error } = useMetricsProviders()
 *
 *   return (
 *     <ul>
 *       {providers.map(p => (
 *         <li key={p.name}>{p.name} ({p.tier})</li>
 *       ))}
 *     </ul>
 *   )
 * }
 * ```
 */
export function useMetricsProviders() {
  const [providers, setProviders] = useState<Array<{
    name: string
    tier: string
    priority: number
  }>>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchProviders = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/metrics/providers`)

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }

        const data = await response.json()
        setProviders(data.providers || [])
        setError(null)
      } catch (err) {
        console.error('Failed to fetch providers:', err)
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }

    fetchProviders()
  }, [])

  return { providers, loading, error }
}

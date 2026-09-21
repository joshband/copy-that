import { useMetricsData, useDataValidation } from './hooks'
import { MetricsGrid } from './MetricsGrid'
import type { MetricsOverviewProps } from './types'

export function MetricsOverview({ projectId, refreshTrigger }: MetricsOverviewProps) {
  const { metrics, loading } = useMetricsData(projectId, refreshTrigger)
  const hasExtractedData = useDataValidation(metrics)

  // Only show loading state, not empty state (OverviewNarrative handles that)
  if (loading) {
    return (
      <div className="space-y-4">
        <p className="text-gray-500 text-sm">Analyzing your design system...</p>
      </div>
    )
  }

  // Don't render anything if no data (OverviewNarrative provides the content)
  if (!metrics || !hasExtractedData) {
    return null
  }

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <MetricsGrid metrics={metrics} />
      </div>
    </div>
  )
}

import { useMetricsData, useDataValidation } from './hooks'
import { MetricsGrid } from './MetricsGrid'
import type { MetricsOverviewProps } from './types'

export function MetricsOverview({ projectId, refreshTrigger }: MetricsOverviewProps) {
  const { metrics, loading } = useMetricsData(projectId, refreshTrigger)
  const hasExtractedData = useDataValidation(metrics)

  if (loading) {
    return (
      <div className="space-y-4">
        <p className="text-gray-500 text-sm">Analyzing your design system...</p>
      </div>
    )
  }

  if (!metrics || !hasExtractedData) {
    return (
      <div className="space-y-4">
        <p className="text-gray-500 text-sm">No data yet. Upload an image to see design system metrics.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <MetricsGrid metrics={metrics} />
      </div>
    </div>
  )
}

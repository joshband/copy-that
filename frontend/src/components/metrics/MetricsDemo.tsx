/**
 * MetricsDemo Component
 *
 * Demo page for testing the streaming metrics endpoint
 * Shows real-time updates as metrics arrive from backend
 */

import React, { useState } from 'react'
import { useStreamingMetrics, useMetricsProviders } from '../../shared/hooks/useStreamingMetrics'
import { MetricsDisplay } from './MetricsDisplay'

export function MetricsDemo() {
  const [projectId, setProjectId] = useState<number>(52)
  const [enabled, setEnabled] = useState(false)

  const metricsState = useStreamingMetrics(enabled ? projectId : null, enabled)
  const { providers, loading: providersLoading } = useMetricsProviders()

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h1 className="text-2xl font-bold mb-4">Streaming Metrics Demo</h1>

        {/* Project ID Input */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Project ID
          </label>
          <input
            type="number"
            value={projectId}
            onChange={(e) => setProjectId(parseInt(e.target.value, 10))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
            disabled={enabled}
          />
        </div>

        {/* Control Buttons */}
        <div className="flex gap-3">
          <button
            onClick={() => setEnabled(true)}
            disabled={enabled || !projectId}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            Start Streaming
          </button>
          <button
            onClick={() => setEnabled(false)}
            disabled={!enabled}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            Stop Streaming
          </button>
        </div>

        {/* Status Display */}
        <div className="mt-4 p-3 bg-gray-50 rounded-md">
          <p className="text-sm">
            <strong>Status:</strong>{' '}
            {enabled
              ? metricsState.isStreaming
                ? 'Streaming...'
                : 'Complete'
              : 'Idle'}
          </p>
          <p className="text-sm">
            <strong>Tiers Completed:</strong> {metricsState.tiersCompleted} / 3
          </p>
        </div>
      </div>

      {/* Providers List */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-lg font-semibold mb-3">Available Providers</h2>
        {providersLoading ? (
          <p className="text-sm text-gray-600">Loading providers...</p>
        ) : (
          <div className="space-y-2">
            {providers.map((provider) => (
              <div
                key={provider.name}
                className="flex items-center justify-between p-2 bg-gray-50 rounded"
              >
                <span className="text-sm font-medium">{provider.name}</span>
                <span className="text-xs text-gray-600 px-2 py-1 bg-white rounded">
                  {provider.tier}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Metrics Display */}
      {enabled && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h2 className="text-lg font-semibold mb-4">Metrics Results</h2>
          <MetricsDisplay metricsState={metricsState} />
        </div>
      )}
    </div>
  )
}

export default MetricsDemo

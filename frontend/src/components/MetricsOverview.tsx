/**
 * Dynamic Overview component showing inferred metrics
 * Displays insights about the design system based on extracted tokens
 */

import { useEffect, useState } from 'react';
import { ApiClient } from '../api/client';

interface ElaboratedMetric {
  primary: string;
  elaborations: string[];
}

interface OverviewMetricsData {
  spacing_scale_system: string | null;
  spacing_uniformity: number;
  color_palette_type: string | null;
  color_temperature: string | null;
  typography_hierarchy_depth: number;
  design_system_maturity: string;
  token_organization_quality: string;
  insights: string[];
  art_movement: ElaboratedMetric | null;
  emotional_tone: ElaboratedMetric | null;
  design_complexity: ElaboratedMetric | null;
  saturation_character: ElaboratedMetric | null;
  temperature_profile: ElaboratedMetric | null;
  design_system_insight: ElaboratedMetric | null;
  summary: {
    total_colors: number;
    total_spacing: number;
    total_typography: number;
    total_shadows: number;
  };
}

interface MetricsOverviewProps {
  projectId: number | null;
}

export function MetricsOverview({ projectId }: MetricsOverviewProps) {
  const [metrics, setMetrics] = useState<OverviewMetricsData | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!projectId) {
      setMetrics(null);
      return;
    }

    const loadMetrics = async () => {
      setLoading(true);
      try {
        const data = await ApiClient.getOverviewMetrics(projectId);
        setMetrics(data);
      } catch (err) {
        console.error('Failed to load overview metrics:', err);
      } finally {
        setLoading(false);
      }
    };

    loadMetrics();
  }, [projectId]);

  if (!metrics && !loading) {
    return (
      <div className="space-y-4">
        <p className="text-gray-500 text-sm">No data yet. Upload an image to see design system metrics.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <SummaryCard label="Colors" value={metrics?.summary.total_colors ?? 0} />
        <SummaryCard label="Spacing" value={metrics?.summary.total_spacing ?? 0} />
        <SummaryCard label="Typography" value={metrics?.summary.total_typography ?? 0} />
        <SummaryCard label="Shadows" value={metrics?.summary.total_shadows ?? 0} />
      </div>

      {/* Elaborated Metrics - Design Analysis */}
      {metrics && (
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-gray-700">Design Analysis</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {metrics.art_movement && (
              <ElaboratedMetricCard metric={metrics.art_movement} label="Art Movement" iconColor="purple" />
            )}
            {metrics.emotional_tone && (
              <ElaboratedMetricCard metric={metrics.emotional_tone} label="Emotional Tone" iconColor="rose" />
            )}
            {metrics.design_complexity && (
              <ElaboratedMetricCard metric={metrics.design_complexity} label="Design Complexity" iconColor="blue" />
            )}
            {metrics.saturation_character && (
              <ElaboratedMetricCard metric={metrics.saturation_character} label="Saturation Character" iconColor="amber" />
            )}
            {metrics.temperature_profile && (
              <ElaboratedMetricCard metric={metrics.temperature_profile} label="Temperature Profile" iconColor="orange" />
            )}
            {metrics.design_system_insight && (
              <ElaboratedMetricCard metric={metrics.design_system_insight} label="System Insight" iconColor="green" />
            )}
          </div>
        </div>
      )}

      {/* Inferred Insights as Chips */}
      {metrics?.insights && metrics.insights.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-gray-700">System Insights</h3>
          <div className="flex flex-wrap gap-2">
            {metrics.insights.map((insight, idx) => (
              <Chip key={idx} text={insight} />
            ))}
          </div>
        </div>
      )}

      {/* Key Metrics */}
      <div className="grid grid-cols-2 gap-4">
        {metrics?.spacing_scale_system && (
          <MetricBox
            label="Spacing System"
            value={metrics.spacing_scale_system}
            description={`${(metrics.spacing_uniformity * 100).toFixed(0)}% uniform`}
          />
        )}

        {metrics?.color_palette_type && (
          <MetricBox
            label="Palette Type"
            value={metrics.color_palette_type}
            description={metrics.color_temperature}
          />
        )}

        {metrics?.typography_hierarchy_depth > 0 && (
          <MetricBox
            label="Typography Levels"
            value={metrics.typography_hierarchy_depth.toString()}
            description={metrics.typography_scale_type}
          />
        )}

        {metrics?.design_system_maturity && (
          <MetricBox
            label="System Maturity"
            value={metrics.design_system_maturity}
            description={metrics.token_organization_quality}
          />
        )}
      </div>
    </div>
  );
}

function SummaryCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-3 text-center">
      <p className="text-2xl font-bold text-gray-900">{value}</p>
      <p className="text-xs text-gray-600 mt-1">{label}</p>
    </div>
  );
}

function Chip({ text }: { text: string }) {
  // Determine chip color based on content
  const getChipStyle = () => {
    if (text.includes('Spacing') || text.includes('grid')) {
      return 'bg-blue-100 text-blue-800 border-blue-300';
    } else if (text.includes('Color') || text.includes('palette')) {
      return 'bg-purple-100 text-purple-800 border-purple-300';
    } else if (text.includes('Typography') || text.includes('font')) {
      return 'bg-amber-100 text-amber-800 border-amber-300';
    } else if (text.includes('organized') || text.includes('mature')) {
      return 'bg-green-100 text-green-800 border-green-300';
    } else if (text.includes('minimal') || text.includes('emerging')) {
      return 'bg-gray-100 text-gray-800 border-gray-300';
    } else if (text.includes('warm') || text.includes('energetic')) {
      return 'bg-orange-100 text-orange-800 border-orange-300';
    } else if (text.includes('cool') || text.includes('calm')) {
      return 'bg-cyan-100 text-cyan-800 border-cyan-300';
    }
    return 'bg-gray-100 text-gray-800 border-gray-300';
  };

  return (
    <div className={`inline-flex items-center px-3 py-1 border rounded-full text-xs font-medium ${getChipStyle()}`}>
      {text}
    </div>
  );
}

function MetricBox({
  label,
  value,
  description,
}: {
  label: string;
  value: string;
  description?: string | null;
}) {
  return (
    <div className="bg-gradient-to-br from-gray-50 to-gray-100 border border-gray-200 rounded-lg p-4">
      <p className="text-xs font-semibold text-gray-600 uppercase tracking-wide">{label}</p>
      <p className="text-xl font-bold text-gray-900 mt-2 capitalize">{value}</p>
      {description && <p className="text-xs text-gray-600 mt-1 capitalize">{description}</p>}
    </div>
  );
}

function ElaboratedMetricCard({
  metric,
  label,
  iconColor,
}: {
  metric: { primary: string; elaborations: string[] };
  label: string;
  iconColor: string;
}) {
  const [expanded, setExpanded] = useState(false);

  const colorClasses = {
    purple: 'bg-purple-50 border-purple-200 text-purple-900',
    rose: 'bg-rose-50 border-rose-200 text-rose-900',
    blue: 'bg-blue-50 border-blue-200 text-blue-900',
    amber: 'bg-amber-50 border-amber-200 text-amber-900',
    orange: 'bg-orange-50 border-orange-200 text-orange-900',
    green: 'bg-green-50 border-green-200 text-green-900',
  };

  const headerClasses = {
    purple: 'bg-purple-100 text-purple-800',
    rose: 'bg-rose-100 text-rose-800',
    blue: 'bg-blue-100 text-blue-800',
    amber: 'bg-amber-100 text-amber-800',
    orange: 'bg-orange-100 text-orange-800',
    green: 'bg-green-100 text-green-800',
  };

  const elaborationClasses = {
    purple: 'bg-purple-50 text-purple-700 border-purple-200',
    rose: 'bg-rose-50 text-rose-700 border-rose-200',
    blue: 'bg-blue-50 text-blue-700 border-blue-200',
    amber: 'bg-amber-50 text-amber-700 border-amber-200',
    orange: 'bg-orange-50 text-orange-700 border-orange-200',
    green: 'bg-green-50 text-green-700 border-green-200',
  };

  return (
    <div className={`border rounded-lg p-4 transition-all ${colorClasses[iconColor as keyof typeof colorClasses]}`}>
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full text-left flex items-center justify-between group"
      >
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide opacity-75">{label}</p>
          <p className="text-lg font-bold mt-1 capitalize group-hover:underline">{metric.primary}</p>
        </div>
        <div className="text-xl opacity-50 group-hover:opacity-100 transition-opacity">
          {expanded ? '−' : '+'}
        </div>
      </button>

      {/* Elaborations - Expandable */}
      {expanded && metric.elaborations.length > 0 && (
        <div className="mt-3 pt-3 border-t border-current border-opacity-20 space-y-2">
          {metric.elaborations.map((elaboration, idx) => (
            <div
              key={idx}
              className={`text-sm p-2 rounded border ${elaborationClasses[iconColor as keyof typeof elaborationClasses]}`}
            >
              • {elaboration}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

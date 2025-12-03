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
      {/* Your Design Palette - Master Section */}
      {metrics && (
        <div className="space-y-4">
          {/* Title and Description */}
          <div>
            <h3 className="text-xl font-bold text-gray-900">Your Design Palette</h3>
            <p className="text-sm text-gray-600 mt-2">
              A system of{' '}
              <span className="font-medium">
                {metrics.summary.total_colors} colors
              </span>
              ,{' '}
              <span className="font-medium">
                {metrics.summary.total_spacing} spacing tokens
              </span>
              , and{' '}
              <span className="font-medium">
                {metrics.summary.total_typography} typography scales
              </span>{' '}
              that work together to define your visual language.
            </p>
          </div>

          {/* System Insights Chips */}
          {metrics?.insights && metrics.insights.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {metrics.insights.map((insight, idx) => (
                <Chip key={idx} text={insight} />
              ))}
            </div>
          )}

          {/* 6-Card Grid with Elaborated Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
            {metrics.art_movement && (
              <DesignInsightCard
                icon="🎨"
                label="Art Movement"
                title={metrics.art_movement.primary}
                description={metrics.art_movement.elaborations[0] || ''}
                elaborations={metrics.art_movement.elaborations}
              />
            )}
            {metrics.emotional_tone && (
              <DesignInsightCard
                icon="💭"
                label="Emotional Tone"
                title={metrics.emotional_tone.primary}
                description={metrics.emotional_tone.elaborations[0] || ''}
                elaborations={metrics.emotional_tone.elaborations}
              />
            )}
            {metrics.design_complexity && (
              <DesignInsightCard
                icon="⏱️"
                label="Design Complexity"
                title={metrics.design_complexity.primary}
                description={metrics.design_complexity.elaborations[0] || ''}
                elaborations={metrics.design_complexity.elaborations}
              />
            )}
            {metrics.temperature_profile && (
              <DesignInsightCard
                icon="🌡️"
                label="Temperature Profile"
                title={metrics.temperature_profile.primary}
                description={metrics.temperature_profile.elaborations[0] || ''}
                elaborations={metrics.temperature_profile.elaborations}
              />
            )}
            {metrics.saturation_character && (
              <DesignInsightCard
                icon="✨"
                label="Saturation Character"
                title={metrics.saturation_character.primary}
                description={metrics.saturation_character.elaborations[0] || ''}
                elaborations={metrics.saturation_character.elaborations}
              />
            )}
            {metrics.design_system_insight && (
              <DesignInsightCard
                icon="💪"
                label="System Health"
                title={`${metrics.summary.total_colors + metrics.summary.total_spacing + metrics.summary.total_typography + metrics.summary.total_shadows} total tokens across all categories`}
                description={metrics.design_system_insight.elaborations[0] || ''}
                elaborations={metrics.design_system_insight.elaborations}
              />
            )}
          </div>

          {/* Summary Stats - Part of Design Palette */}
          <div className="border-t border-gray-200 pt-4 mt-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <StatBox label="Colors" value={metrics?.summary.total_colors ?? 0} />
              <StatBox label="Spacing" value={metrics?.summary.total_spacing ?? 0} />
              <StatBox label="Typography" value={metrics?.summary.total_typography ?? 0} />
              <StatBox label="Shadows" value={metrics?.summary.total_shadows ?? 0} />
            </div>
          </div>

          {/* Key Metrics - Part of Design Palette */}
          <div className="border-t border-gray-200 pt-4 mt-4">
            <div className="grid grid-cols-2 gap-4">
              {metrics?.color_palette_type && (
                <MetricBox
                  label="Palette Type"
                  value={metrics.color_palette_type}
                  description={metrics.color_temperature}
                />
              )}

              {metrics?.design_system_maturity && (
                <MetricBox
                  label="System Maturity"
                  value={metrics.design_system_maturity}
                  description={metrics.token_organization_quality}
                />
              )}

              {metrics?.spacing_scale_system && (
                <MetricBox
                  label="Spacing System"
                  value={metrics.spacing_scale_system}
                  description={`${(metrics.spacing_uniformity * 100).toFixed(0)}% uniform`}
                />
              )}

              {metrics?.typography_hierarchy_depth > 0 && (
                <MetricBox
                  label="Typography Levels"
                  value={metrics.typography_hierarchy_depth.toString()}
                  description={metrics.typography_scale_type}
                />
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function StatBox({ label, value }: { label: string; value: number }) {
  return (
    <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-center">
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

function DesignInsightCard({
  icon,
  label,
  title,
  description,
  elaborations,
}: {
  icon: string;
  label: string;
  title: string;
  description: string;
  elaborations: string[];
}) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
      {/* Icon */}
      <div className="text-3xl mb-3">{icon}</div>

      {/* Label */}
      <p className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-2">{label}</p>

      {/* Title */}
      <h4 className="text-lg font-bold text-gray-900 mb-3 capitalize">{title}</h4>

      {/* Description - Primary elaboration */}
      {description && (
        <p className="text-sm text-gray-700 leading-relaxed">{description}</p>
      )}

      {/* Additional elaborations */}
      {elaborations.length > 1 && (
        <div className="mt-4 pt-4 border-t border-gray-100 space-y-2">
          {elaborations.slice(1).map((elaboration, idx) => (
            <div key={idx} className="text-xs text-gray-600 leading-relaxed">
              • {elaboration}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

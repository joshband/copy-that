/**
 * Dynamic Overview component showing inferred metrics
 * Displays insights about the design system based on extracted tokens
 */

import { useEffect, useState } from 'react';
import { ApiClient } from '../api/client';

interface ElaboratedMetric {
  primary: string;
  elaborations: string[];
  confidence?: number;
}

interface OverviewMetricsData {
  spacing_scale_system: string | null;
  spacing_uniformity: number;
  color_harmony_type: string | null;
  color_palette_type: string | null;
  color_temperature: string | null;
  typography_hierarchy_depth: number;
  typography_scale_type: string | null;
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
  // Source tracking
  source?: {
    has_extracted_colors: boolean;
    has_extracted_spacing: boolean;
    has_extracted_typography: boolean;
  };
}

interface MetricsOverviewProps {
  projectId: number | null;
  refreshTrigger?: number; // Trigger refetch when tokens change
}

export function MetricsOverview({ projectId, refreshTrigger }: MetricsOverviewProps) {
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
  }, [projectId, refreshTrigger]);

  // Only show metrics if we have extracted data (not just database defaults)
  const hasExtractedData = metrics?.source && (
    metrics.source.has_extracted_colors ||
    metrics.source.has_extracted_spacing ||
    metrics.source.has_extracted_typography
  );

  if (loading) {
    return (
      <div className="space-y-4">
        <p className="text-gray-500 text-sm">Analyzing your design system...</p>
      </div>
    );
  }

  if (!metrics || !hasExtractedData) {
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
          {/* Rich Insight Cards Grid - 3 column layout */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '50px', marginTop: '50px', marginBottom: '50px' }}>
            {metrics.art_movement && (
              <DesignInsightCard
                icon="🎨"
                label="Art Movement"
                title={metrics.art_movement.primary}
                description={metrics.art_movement.elaborations[0] || ''}
                elaborations={metrics.art_movement.elaborations.slice(1)}
                confidence={metrics.art_movement.confidence}
                source={metrics.source?.has_extracted_colors ? '🎨 Colors' : 'Database'}
              />
            )}
            {metrics.emotional_tone && (
              <DesignInsightCard
                icon="💭"
                label="Emotional Tone"
                title={metrics.emotional_tone.primary}
                description={metrics.emotional_tone.elaborations[0] || ''}
                elaborations={metrics.emotional_tone.elaborations.slice(1)}
                confidence={metrics.emotional_tone.confidence}
                source={metrics.source?.has_extracted_colors ? '🎨 Colors' : 'Database'}
              />
            )}
            {metrics.design_complexity && (
              <DesignInsightCard
                icon="⏱️"
                label="Design Complexity"
                title={metrics.design_complexity.primary}
                description={metrics.design_complexity.elaborations[0] || ''}
                elaborations={metrics.design_complexity.elaborations.slice(1)}
                confidence={metrics.design_complexity.confidence}
                source={
                  metrics.source?.has_extracted_colors || metrics.source?.has_extracted_spacing || metrics.source?.has_extracted_typography
                    ? '📊 All Tokens'
                    : 'Database'
                }
              />
            )}
            {metrics.temperature_profile && (
              <DesignInsightCard
                icon="🌡️"
                label="Temperature Profile"
                title={metrics.temperature_profile.primary}
                description={metrics.temperature_profile.elaborations[0] || ''}
                elaborations={metrics.temperature_profile.elaborations.slice(1)}
                confidence={metrics.temperature_profile.confidence}
                source={metrics.source?.has_extracted_colors ? '🎨 Colors' : 'Database'}
              />
            )}
            {metrics.saturation_character && (
              <DesignInsightCard
                icon="✨"
                label="Saturation Character"
                title={metrics.saturation_character.primary}
                description={metrics.saturation_character.elaborations[0] || ''}
                elaborations={metrics.saturation_character.elaborations.slice(1)}
                confidence={metrics.saturation_character.confidence}
                source={metrics.source?.has_extracted_colors ? '🎨 Colors' : 'Database'}
              />
            )}
            {metrics.design_system_insight && (
              <DesignInsightCard
                icon="💪"
                label="System Health"
                title={`${metrics.summary.total_colors + metrics.summary.total_spacing + metrics.summary.total_typography + metrics.summary.total_shadows} total tokens across all categories`}
                description={metrics.design_system_insight.elaborations[0] || ''}
                elaborations={metrics.design_system_insight.elaborations.slice(1)}
                confidence={metrics.design_system_insight.confidence}
                source={
                  metrics.source?.has_extracted_colors || metrics.source?.has_extracted_spacing || metrics.source?.has_extracted_typography
                    ? '📊 All Tokens'
                    : 'Database'
                }
              />
            )}
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
  return (
    <span className="inline-block px-3 py-1 bg-gray-100 text-gray-700 border border-gray-300 rounded text-sm">
      {text}
    </span>
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

function getConfidenceColor(confidence?: number): string {
  if (!confidence) return 'bg-gray-100 text-gray-700';
  if (confidence >= 75) return 'bg-green-100 text-green-700';
  if (confidence >= 60) return 'bg-yellow-100 text-yellow-700';
  return 'bg-orange-100 text-orange-700';
}

function getConfidenceLabel(confidence?: number): string {
  if (!confidence) return 'Calculating...';
  if (confidence >= 75) return 'High Confidence';
  if (confidence >= 60) return 'Likely Match';
  return 'Possible Interpretation';
}

function DesignInsightCard({
  icon,
  label,
  title,
  description,
  elaborations,
  confidence,
  source,
}: {
  icon: string;
  label: string;
  title: string;
  description: string;
  elaborations: string[];
  confidence?: number;
  source?: string;
}) {
  return (
    <div style={{
      border: '1px solid #e5e7eb',
      borderRadius: '8px',
      padding: '24px',
      backgroundColor: '#f9fafb',
      display: 'flex',
      flexDirection: 'column',
      height: '100%'
    }}>
      {/* Card Header - Label */}
      <h4 style={{ fontSize: '14px', fontWeight: 'bold', color: '#111827', marginBottom: '12px' }}>{label}</h4>

      {/* Title */}
      <h3 style={{
        fontSize: '18px',
        fontWeight: 'bold',
        color: '#111827',
        marginBottom: '16px',
        paddingBottom: '16px',
        borderBottom: '1px solid #e5e7eb'
      }}>{title}</h3>

      {/* Description - Primary elaboration */}
      {description && (
        <p style={{ fontSize: '14px', color: '#374151', lineHeight: '1.5', marginBottom: '12px', marginTop: '8px' }}>{description}</p>
      )}

      {/* Additional elaborations */}
      {elaborations.length > 0 && (
        <div style={{ marginBottom: '16px' }}>
          {elaborations.map((elaboration, idx) => (
            <div key={idx} style={{ fontSize: '14px', color: '#374151', lineHeight: '1.5', marginBottom: '4px' }}>
              • {elaboration}
            </div>
          ))}
        </div>
      )}

      {/* Uncertainty message for low-confidence items */}
      {confidence !== undefined && confidence < 60 && (
        <p style={{ fontSize: '12px', color: '#4b5563', marginBottom: '16px', fontStyle: 'italic' }}>
          Multiple interpretations possible
        </p>
      )}

      {/* Source Badge - Bottom centered, distinctive chip inside card */}
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        paddingTop: '16px',
        borderTop: '1px solid #e5e7eb',
        marginTop: 'auto'
      }}>
        {source && (
          <span
            style={{
              display: 'inline-block',
              padding: '4px 12px',
              backgroundColor: '#dbeafe',
              color: '#1e40af',
              fontSize: '12px',
              fontWeight: '500',
              borderRadius: '4px'
            }}
            title={`Inferred from ${source} data`}
            data-source={source}
          >
            {source}
          </span>
        )}
      </div>
    </div>
  );
}

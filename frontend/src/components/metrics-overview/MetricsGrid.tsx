import { DesignInsightCard } from './DesignInsightCard'
import type { OverviewMetricsData } from './types'

interface MetricsGridProps {
  metrics: OverviewMetricsData
}

export function MetricsGrid({ metrics }: MetricsGridProps) {
  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap: '50px',
        marginTop: '50px',
        marginBottom: '50px',
      }}
    >
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
            metrics.source?.has_extracted_colors ||
            metrics.source?.has_extracted_spacing ||
            metrics.source?.has_extracted_typography
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
            metrics.source?.has_extracted_colors ||
            metrics.source?.has_extracted_spacing ||
            metrics.source?.has_extracted_typography
              ? '📊 All Tokens'
              : 'Database'
          }
        />
      )}
    </div>
  )
}

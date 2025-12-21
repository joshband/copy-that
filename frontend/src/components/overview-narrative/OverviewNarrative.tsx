import '../OverviewNarrative.css'
import type { OverviewNarrativeProps } from './types'
import { NarrativeCards } from './NarrativeCards'
import { ColorSwatches } from './ColorSwatches'
import { MoodBoard } from './MoodBoard'
import {
  usePaletteAnalysis,
  useArtMovementClassification,
  useEmotionalTone,
  useDesignEra,
  useNarrative,
  useDesignSystemInsights
} from './hooks'

export function OverviewNarrative({
  colors,
  colorCount,
  aliasCount,
  spacingCount,
  multiplesCount,
  typographyCount,
  paletteSummary
}: OverviewNarrativeProps) {
  const { temp, sat } = usePaletteAnalysis(colors)
  const movement = useArtMovementClassification(colors)
  const emotional = useEmotionalTone(colors)
  const era = useDesignEra(colors)
  const narrative = useNarrative(colors)
  const insights = useDesignSystemInsights({
    colorCount,
    aliasCount,
    spacingCount,
    multiplesCount,
    typographyCount,
    temp,
    sat
  })
  const hasColors = colors.length > 0
  const hasAnyTokens = hasColors || spacingCount > 0 || typographyCount > 0

  if (!hasAnyTokens) {
    return (
      <div className="overview-narrative narrative-empty standin">
        <h2>Upload an image to see your system story</h2>
        <p className="intro-text">
          We generate palette insights, spacing diagnostics, and typography guidance after your first extraction.
        </p>
        <ul className="empty-list">
          <li>Drop an image in the uploader to extract colors, spacing, typography, and shadows.</li>
          <li>Progress streams live; once tokens arrive, this panel fills with narrative and diagnostics.</li>
          <li>Lighting analysis and token graph tools unlock automatically after the first run.</li>
        </ul>
      </div>
    )
  }

  return (
    <div className="overview-narrative">
      <div className="narrative-intro">
        <h2>Your Design Has a Story to Tell</h2>
        <p className="intro-text">
          Every color choice whispers something about intent. Every spacing decision reveals how you think about
          hierarchy. This is what your design system is saying to the world—whether you meant it to or not.
        </p>
      </div>

      {hasColors && (
        <NarrativeCards
          movement={movement}
          emotional={emotional}
          era={era}
          temperature={temp}
          saturation={sat}
          colorCount={colorCount}
          spacingCount={spacingCount}
          typographyCount={typographyCount}
        />
      )}

      {hasColors && (
        <div className="narrative-story">
          <h3>The Vibe Check</h3>
          <p>{paletteSummary || narrative}</p>
          <ColorSwatches colors={colors} />
        </div>
      )}

      {/* AI-Curated Mood Boards */}
      <MoodBoard colors={colors} />

      <div className="narrative-insight">
        <h3>What Makes This System Tick</h3>
        <ul>
          {insights.map((insight, index) => (
            <li key={index}>
              <strong>{insight.title}:</strong> {insight.description}
            </li>
          ))}
        </ul>
      </div>

      <div className="narrative-cta">
        <p>
          Ready to get nerdy? Each token below has its own story—click around and discover the science, psychology, and
          happy accidents that shaped your design system.
        </p>
      </div>
    </div>
  )
}

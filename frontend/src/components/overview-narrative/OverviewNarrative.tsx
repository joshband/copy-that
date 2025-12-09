import '../OverviewNarrative.css'
import type { OverviewNarrativeProps } from './types'
import { NarrativeCards } from './NarrativeCards'
import { ColorSwatches } from './ColorSwatches'
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
  typographyCount
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

  return (
    <div className="overview-narrative">
      <div className="narrative-intro">
        <h2>Your Design Has a Story to Tell</h2>
        <p className="intro-text">
          Every color choice whispers something about intent. Every spacing decision reveals how you think about
          hierarchy. This is what your design system is saying to the world—whether you meant it to or not.
        </p>
      </div>

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

      <div className="narrative-story">
        <h3>The Vibe Check</h3>
        <p>{narrative}</p>
        <ColorSwatches colors={colors} />
      </div>

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

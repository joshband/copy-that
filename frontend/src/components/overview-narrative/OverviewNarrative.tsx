import '../OverviewNarrative.css'
import type { OverviewNarrativeProps } from './types'
import { NarrativeCards } from './NarrativeCards'
import { ColorSwatches } from './ColorSwatches'
import {
  usePaletteAnalysis,
  useArtMovementClassification,
  useEmotionalTone,
  useDesignEra,
  useNarrative
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

  return (
    <div className="overview-narrative">
      <div className="narrative-intro">
        <h2>Your Design Palette</h2>
        <p className="intro-text">
          A system of <strong>{colorCount} colors</strong>, <strong>{spacingCount} spacing tokens</strong>, and{' '}
          <strong>{typographyCount} typography scales</strong> that work together to define your visual language.
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
        <h3>Your Design Story</h3>
        <p>{narrative}</p>
        <ColorSwatches colors={colors} />
      </div>

      <div className="narrative-insight">
        <h3>Design System Insight</h3>
        <ul>
          <li>
            <strong>Color Foundation:</strong> {aliasCount} color aliases provide semantic meaning and consistency across your
            application.
          </li>
          <li>
            <strong>Spacing Logic:</strong> {multiplesCount} spacing multiples create rhythm and proportional relationships in your
            layouts.
          </li>
          <li>
            <strong>Visual Hierarchy:</strong> Your system supports multiple scales of typography, from headlines to body text to
            fine print.
          </li>
          <li>
            <strong>Cohesion Strategy:</strong> Every token in this system is interconnected—colors, spacing, and type scales work
            together as a unified whole.
          </li>
        </ul>
      </div>

      <div className="narrative-cta">
        <p>Explore individual tokens in the sections below to dive deeper into each element of your design system.</p>
      </div>
    </div>
  )
}

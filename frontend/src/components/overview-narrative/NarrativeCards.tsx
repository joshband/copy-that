import type {
  ArtMovement,
  EmotionalTone,
  DesignEra,
  TemperatureType,
  SaturationType
} from './types'
import {
  useArtMovementDescription,
  useTemperatureDescription,
  useSaturationDescription
} from './hooks'

interface NarrativeCardsProps {
  movement: ArtMovement
  emotional: EmotionalTone
  era: DesignEra
  temperature: TemperatureType
  saturation: SaturationType
  colorCount: number
  spacingCount: number
  typographyCount: number
}

export function NarrativeCards({
  movement,
  emotional,
  era,
  temperature,
  saturation,
  colorCount,
  spacingCount,
  typographyCount
}: NarrativeCardsProps) {
  const movementDesc = useArtMovementDescription(movement)
  const tempDesc = useTemperatureDescription(temperature)
  const satDesc = useSaturationDescription(saturation)

  // Generate whimsical era description
  const getEraDescription = (): string => {
    if (colorCount <= 2) {
      return "You've stripped everything down to pure essence. Two colors doing the work of twenty. This is design at its most distilled—confident enough to let minimalism speak volumes."
    }
    if (colorCount <= 4) {
      return 'A lean, focused palette where every color earned its spot through rigorous editing. This is intentional restraint, not limitation—the difference between "minimal" and "incomplete."'
    }
    if (colorCount <= 8) {
      return "You've hit the sweet spot: enough variety to stay interesting, enough restraint to stay coherent. This is structured color harmony—complex enough to handle edge cases, simple enough to remember."
    }
    if (colorCount <= 12) {
      return "A rich color ecosystem where every hue has a purpose and a place. You've built depth and variety without sacrificing organization—this is systematic thinking at scale."
    }
    return "This is a comprehensive color system that doesn't mess around. You've got coverage for every scenario, every mood, every edge case—the kind of palette that makes design decisions feel inevitable rather than arbitrary."
  }

  // Generate whimsical system health description
  const getSystemHealthDescription = (): string => {
    const totalTokens = colorCount + spacingCount + typographyCount
    const hasAll = colorCount > 0 && spacingCount > 0 && typographyCount > 0
    const hasTwo = [colorCount > 0, spacingCount > 0, typographyCount > 0].filter(Boolean).length === 2

    if (hasAll && totalTokens >= 20) {
      return "You're not messing around. This is a fully-fledged design system with opinions about everything—color, space, type, the works. The kind of comprehensive toolkit that makes building new features feel like playing with really good Lego."
    }
    if (hasAll) {
      return "You've covered all three pillars of design systems: color, spacing, and typography. This is a complete visual language, not just a random collection of styles. Every interface you build with this will feel cohesive without even trying."
    }
    if (hasTwo) {
      if (colorCount === 0) {
        return "You've got spacing and typography locked down, but colors are MIA. Add some hues to complete the trinity—design systems work best when all three elements speak the same language."
      }
      if (spacingCount === 0) {
        return "Colors and typography are sorted, but spacing needs some love. Consider adding a spatial scale—consistent spacing is what makes layouts feel intentional instead of random."
      }
      return "You've nailed color and spacing, but typography is waiting in the wings. Add a type scale to complete the system—hierarchy matters as much as hue."
    }
    if (colorCount > 0) {
      return "You've got colors on lock. Now consider building out spacing and typography tokens to create a complete design language. Right now you're painting without a frame—add structure to really shine."
    }
    return 'This system is just getting started. Consider building out your color, spacing, and typography tokens to create a comprehensive visual language that makes design decisions feel systematic instead of arbitrary.'
  }

  return (
    <div className="narrative-grid">
      {/* Art Movement */}
      <div className="narrative-card movement">
        <div className="card-icon">🎨</div>
        <h3>Art Movement Vibes</h3>
        <p className="movement-name">{movement}</p>
        <p className="movement-description">{movementDesc}</p>
      </div>

      {/* Emotional Tone */}
      <div className="narrative-card emotional">
        <div className="card-icon">💭</div>
        <h3>Emotional Signature</h3>
        <p className="emotion-label">{emotional.emotion}</p>
        <p className="emotion-description">{emotional.description}</p>
      </div>

      {/* Design Era */}
      <div className="narrative-card era">
        <div className="card-icon">⏱️</div>
        <h3>Complexity Level</h3>
        <p className="era-name">{era}</p>
        <p className="era-description">{getEraDescription()}</p>
      </div>

      {/* Temperature Profile */}
      <div className="narrative-card temperature">
        <div className="card-icon">🌡️</div>
        <h3>Temperature Profile</h3>
        <p className="temp-label">{temperature.charAt(0).toUpperCase() + temperature.slice(1)}</p>
        <p className="temp-description">{tempDesc}</p>
      </div>

      {/* Saturation Profile */}
      <div className="narrative-card saturation">
        <div className="card-icon">✨</div>
        <h3>Saturation Character</h3>
        <p className="sat-label">{saturation.charAt(0).toUpperCase() + saturation.slice(1)}</p>
        <p className="sat-description">{satDesc}</p>
      </div>

      {/* System Health */}
      <div className="narrative-card health">
        <div className="card-icon">💪</div>
        <h3>System Completeness</h3>
        <p className="health-metric">
          {colorCount + spacingCount + typographyCount} tokens across all categories
        </p>
        <p className="health-description">{getSystemHealthDescription()}</p>
      </div>
    </div>
  )
}

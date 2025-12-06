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

  return (
    <div className="narrative-grid">
      {/* Art Movement */}
      <div className="narrative-card movement">
        <div className="card-icon">🎨</div>
        <h3>Art Movement</h3>
        <p className="movement-name">{movement}</p>
        <p className="movement-description">Your palette aligns with {movementDesc}</p>
      </div>

      {/* Emotional Tone */}
      <div className="narrative-card emotional">
        <div className="card-icon">💭</div>
        <h3>Emotional Tone</h3>
        <p className="emotion-label">{emotional.emotion}</p>
        <p className="emotion-description">{emotional.description}</p>
      </div>

      {/* Design Era */}
      <div className="narrative-card era">
        <div className="card-icon">⏱️</div>
        <h3>Design Complexity</h3>
        <p className="era-name">{era}</p>
        <p className="era-description">
          With {colorCount} colors working in concert, you've created a{' '}
          {colorCount <= 4 ? 'lean' : 'comprehensive'} visual system that{' '}
          {colorCount <= 4 ? 'maximizes impact through restraint' : 'handles multiple design scenarios'}.
        </p>
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
        <h3>System Health</h3>
        <p className="health-metric">{colorCount + spacingCount + typographyCount} total tokens across all categories</p>
        <p className="health-description">
          {colorCount > 0 && spacingCount > 0 && typographyCount > 0
            ? 'Your system is well-rounded, covering color, spacing, and typography comprehensively.'
            : colorCount > 0 && spacingCount > 0
              ? 'Your system has colors and spacing defined. Consider adding typography tokens for complete coverage.'
              : 'Your color palette is defined. Complement it with spacing and typography scales for a complete system.'}
        </p>
      </div>
    </div>
  )
}

import React from 'react'
import './ColorNarrative.css'

interface ColorNarrativeProps {
  hex: string
  name: string
  semanticNames?: Record<string, unknown> | null
  temperature?: string
  saturationLevel?: string
  lightnessLevel?: string
  isNeutral?: boolean
  prominencePercentage?: number
  category?: string
}

export function ColorNarrative({
  hex,
  name,
  semanticNames,
  temperature,
  saturationLevel,
  lightnessLevel,
  isNeutral,
  prominencePercentage,
  category
}: ColorNarrativeProps) {
  const getTemperatureDescription = (temp?: string): string => {
    switch (temp) {
      case 'warm':
        return 'This is a warm color, associated with energy, passion, and comfort. Warm colors advance toward viewers and grab attention.'
      case 'cool':
        return 'This is a cool color, associated with calmness, trust, and serenity. Cool colors recede and create a sense of peace.'
      case 'neutral':
        return 'This color sits between warm and cool, making it versatile for many design contexts.'
      default:
        return ''
    }
  }

  const getSaturationDescription = (sat?: string): string => {
    switch (sat) {
      case 'high':
        return 'With high saturation, this color is vivid and intense. It commands attention and conveys strong emotion or energy.'
      case 'medium':
        return 'Medium saturation makes this color balanced—vibrant enough to be interesting but subtle enough for professional contexts.'
      case 'low':
        return 'Low saturation makes this color muted and sophisticated. It works well in calming designs and pairs well with more saturated accents.'
      case 'desaturated':
        return 'This desaturated color is particularly versatile and elegant, working in both modern minimalist and traditional designs.'
      default:
        return ''
    }
  }

  const getLightnessDescription = (light?: string): string => {
    switch (light) {
      case 'very_light':
        return 'Very light and airy, this color is excellent for backgrounds and doesn\'t compete for visual attention.'
      case 'light':
        return 'Light and gentle, this color works well as a secondary background or for large areas without overwhelming.'
      case 'medium':
        return 'Medium lightness makes this color balanced for both foreground and background applications.'
      case 'dark':
        return 'Dark and rich, this color creates strong visual impact and works well for text or prominent design elements.'
      case 'very_dark':
        return 'Very dark and dramatic, this color is excellent for dark mode interfaces or creating strong contrast.'
      default:
        return ''
    }
  }

  return (
    <div className="color-narrative">
      <div className="narrative-section intro">
        <h3>Understanding This Color</h3>

        <div className="color-hero">
          <div className="hero-swatch" style={{ backgroundColor: hex }} />
          <div className="hero-info">
            <h2 className="hero-name">{name}</h2>
            <code className="hero-hex">{hex}</code>
            {category != null && category !== '' && <p className="hero-category">Category: {category}</p>}
          </div>
        </div>

        <p className="intro-narrative">
          You've extracted <strong>{name}</strong> ({hex}) from your design. This color tells a story about your palette.
          Let's explore what this color communicates and how it works in your design system.
        </p>
      </div>

      <div className="narrative-grid">
        {temperature != null && temperature !== '' && (
          <div className="narrative-section">
            <h4>Temperature: {temperature}</h4>
            <p>{getTemperatureDescription(temperature)}</p>
            <div className="implication">
              <strong>In your design:</strong> Use this {temperature} color to evoke the appropriate emotional response from
              your users.
            </div>
          </div>
        )}

        {saturationLevel != null && saturationLevel !== '' && (
          <div className="narrative-section">
            <h4>Saturation: {saturationLevel}</h4>
            <p>{getSaturationDescription(saturationLevel)}</p>
            <div className="implication">
              <strong>In your design:</strong> This saturation level works well for {saturationLevel} contrast scenarios.
            </div>
          </div>
        )}

        {lightnessLevel != null && lightnessLevel !== '' && (
          <div className="narrative-section">
            <h4>Lightness: {lightnessLevel}</h4>
            <p>{getLightnessDescription(lightnessLevel)}</p>
            <div className="implication">
              <strong>In your design:</strong> Consider this color for roles that match its visual weight.
            </div>
          </div>
        )}

        {isNeutral === true && (
          <div className="narrative-section neutral">
            <h4>🎨 Neutral Color</h4>
            <p>
              This is a neutral color—essentially a variation of gray, black, or white. Neutral colors are the foundation
              of every good design system, providing balance and context for more vibrant colors.
            </p>
            <div className="implication">
              <strong>In your design:</strong> Use this as a background, text color, or foundational element of your palette.
            </div>
          </div>
        )}

        {prominencePercentage != null && (
          <div className="narrative-section">
            <h4>Prominence: {prominencePercentage.toFixed(1)}%</h4>
            <p>
              This color occupies approximately <strong>{prominencePercentage.toFixed(1)}%</strong> of your design.{' '}
              {prominencePercentage > 30
                ? 'This is a dominant color that sets the overall tone.'
                : prominencePercentage > 10
                  ? 'This is a supporting color that balances your design.'
                  : 'This is an accent color that provides contrast and focus.'}
            </p>
            <div className="implication">
              <strong>In your system:</strong> Consider this color's role proportional to its prominence.
            </div>
          </div>
        )}

        {semanticNames != null && Object.keys(semanticNames).length > 0 && (
          <div className="narrative-section">
            <h4>Naming Styles</h4>
            <p>
              This color can be named in several ways depending on your naming convention. Here are automatically generated
              names:
            </p>
            <div className="naming-examples">
              {Object.entries(semanticNames).map(([style, name]) => (
                <div key={style} className="naming-style">
                  <span className="style-label">{style}</span>
                  <span className="style-name">{String(name)}</span>
                </div>
              ))}
            </div>
            <div className="implication">
              <strong>Pro tip:</strong> Choose a naming convention and stick with it across your entire design system.
            </div>
          </div>
        )}
      </div>

      <div className="narrative-section usage-guide">
        <h3>How to Use This Color</h3>

        <div className="usage-list">
          <div className="usage-item">
            <span className="usage-icon">✓</span>
            <div>
              <strong>When to use:</strong> This color works well in contexts where {temperature ?? 'emotional'} tones are
              appropriate.
            </div>
          </div>

          <div className="usage-item">
            <span className="usage-icon">→</span>
            <div>
              <strong>Pairing strategy:</strong> Combine with colors that are {temperature === 'warm' ? 'cool' : 'warm'} to
              create dynamic contrast.
            </div>
          </div>

          <div className="usage-item">
            <span className="usage-icon">⚠</span>
            <div>
              <strong>Watch out for:</strong> Don't overuse. If this color is prominent, let it dominate naturally rather
              than forcing it.
            </div>
          </div>

          <div className="usage-item">
            <span className="usage-icon">🔄</span>
            <div>
              <strong>Variations:</strong> Create a family of this color using tints (lighter), shades (darker), and tones
              (desaturated).
            </div>
          </div>
        </div>
      </div>

      <div className="narrative-section learning">
        <h3>Color Theory Deep Dive</h3>
        <p>
          Understanding color goes beyond picking pleasant hues. Color theory helps you create coherent, intentional
          designs:
        </p>
        <ul>
          <li>
            <strong>Color temperature</strong> affects mood: warm colors energize, cool colors calm.
          </li>
          <li>
            <strong>Saturation</strong> affects intensity: vivid vs. muted affects visual weight and emotion.
          </li>
          <li>
            <strong>Lightness</strong> affects contrast: sufficient contrast ensures readability and hierarchy.
          </li>
          <li>
            <strong>Context matters:</strong> Colors look different on different backgrounds (color relativity).
          </li>
          <li>
            <strong>Cultural significance:</strong> Colors carry different meanings in different cultures.
          </li>
        </ul>
      </div>
    </div>
  )
}

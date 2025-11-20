import React, { useMemo } from 'react'
import './HarmonyVisualizer.css'

interface HarmonyVisualizerProps {
  harmony: string
  hex: string
}

export function HarmonyVisualizer({ harmony, hex }: HarmonyVisualizerProps) {
  const explanations: Record<string, { description: string; pattern: string }> = {
    monochromatic: {
      description:
        'Monochromatic harmonies use a single hue with variations in lightness and saturation. They create cohesive, calming designs with high unity. Common in minimalist interfaces.',
      pattern: 'Single hue, different lightness/saturation'
    },
    analogous: {
      description:
        'Colors adjacent on the hue wheel (30-60° apart) create harmonious, comfortable palettes. Often seen in nature. Great for schemes that feel organized yet varied.',
      pattern: 'Hues within 60° of each other'
    },
    complementary: {
      description:
        'Opposite colors on the hue wheel create maximum contrast and vibrancy. High visual impact but can overwhelm if not balanced carefully. Use one as primary, other as accent.',
      pattern: '180° apart on hue wheel'
    },
    triadic: {
      description:
        'Three colors equally spaced around the hue wheel (120° apart). Creates vibrant, balanced designs with strong visual identity. Requires careful proportion management.',
      pattern: '120° apart on hue wheel'
    },
    tetradic: {
      description:
        'Four colors in two complementary pairs (90° apart). Creates rich, varied palettes with good balance. More complex to use than simpler harmonies.',
      pattern: 'Two pairs of complementary colors'
    },
    'split-complementary': {
      description:
        'A hue with the two colors adjacent to its complement. Creates vibrant yet harmonious effect. Less tension than pure complementary while maintaining contrast.',
      pattern: 'One color + two neighbors of its complement'
    },
    quadratic: {
      description:
        'Similar to tetradic, four colors create rich palettes. Each color is roughly 90° apart on the hue wheel.',
      pattern: 'Evenly spaced across color wheel'
    },
    compound: {
      description:
        'Combines multiple harmony types. Often analogous colors with one complementary accent. Creates sophisticated, layered palettes.',
      pattern: 'Mixed harmony relationships'
    },
    achromatic: {
      description:
        'Gray, black, and white only—no hue. Creates timeless, sophisticated designs. Often used as a neutral foundation for accent colors.',
      pattern: 'No saturation'
    },
    unknown: {
      description: 'Color harmony not classified. May be part of a custom palette.',
      pattern: 'Unclassified'
    }
  }

  const info = explanations[harmony] || explanations.unknown

  // Generate simplified hue wheel visualization
  const drawHueWheel = () => {
    const angles = {
      red: 0,
      orange: 30,
      yellow: 60,
      lime: 90,
      green: 120,
      cyan: 150,
      blue: 180,
      purple: 210,
      magenta: 240,
      pink: 270,
      rose: 300,
      coral: 330
    }

    return (
      <svg viewBox="0 0 200 200" className="hue-wheel">
        <circle cx="100" cy="100" r="90" fill="none" stroke="#ddd" strokeWidth="1" />

        {/* Position markers for color families */}
        {Object.entries(angles).map(([name, angle]) => {
          const rad = (angle * Math.PI) / 180
          const x = 100 + 80 * Math.cos(rad)
          const y = 100 + 80 * Math.sin(rad)

          return (
            <circle
              key={name}
              cx={x}
              cy={y}
              r="4"
              fill={`hsl(${angle}, 100%, 50%)`}
              stroke="white"
              strokeWidth="1"
            />
          )
        })}

        {/* Center */}
        <circle cx="100" cy="100" r="8" fill={hex} stroke="white" strokeWidth="2" />
      </svg>
    )
  }

  const harmonyAngles: Record<string, number[]> = {
    monochromatic: [0],
    analogous: [0, 30, 330],
    complementary: [0, 180],
    triadic: [0, 120, 240],
    tetradic: [0, 90, 180, 270],
    'split-complementary': [0, 150, 210],
    quadratic: [0, 90, 180, 270],
    compound: [0, 30, 150, 180],
    achromatic: [0],
    unknown: [0]
  }

  return (
    <div className="harmony-visualizer">
      <div className="harmony-header">
        <h3>Color Harmony: <span className="harmony-type">{harmony}</span></h3>
      </div>

      <div className="harmony-content">
        <div className="harmony-wheel-section">
          <p className="harmony-intro">
            This color participates in a <strong>{harmony}</strong> relationship with other colors in your palette.
          </p>
          <div className="wheel-container">{drawHueWheel()}</div>
          <p className="wheel-explanation">
            The center dot (your color) and surrounding markers show how {harmony} palettes relate on the hue wheel.
          </p>
        </div>

        <div className="harmony-explanation-section">
          <h4>What is a {harmony} harmony?</h4>
          <p className="description">{info.description}</p>

          <div className="pattern-info">
            <span className="pattern-label">Pattern:</span>
            <span className="pattern-value">{info.pattern}</span>
          </div>

          <div className="usage-tips">
            <h5>Design Tips</h5>
            <ul>
              {harmony === 'monochromatic' && (
                <>
                  <li>Use for calming, professional interfaces</li>
                  <li>Create depth with lightness variations</li>
                  <li>Add neutral accent colors for clarity</li>
                </>
              )}
              {harmony === 'analogous' && (
                <>
                  <li>Creates naturally harmonious, organized feel</li>
                  <li>Great for nature-inspired designs</li>
                  <li>Choose one dominant color, others as accents</li>
                </>
              )}
              {harmony === 'complementary' && (
                <>
                  <li>Creates high contrast and vibrancy</li>
                  <li>Use one color dominantly, other as accent</li>
                  <li>Perfect for drawing attention and energy</li>
                </>
              )}
              {harmony === 'triadic' && (
                <>
                  <li>Balanced and vibrant without being overwhelming</li>
                  <li>Give one color more weight than others</li>
                  <li>Excellent for playful, energetic designs</li>
                </>
              )}
              {harmony !== 'monochromatic' &&
                harmony !== 'analogous' &&
                harmony !== 'complementary' &&
                harmony !== 'triadic' && (
                  <>
                    <li>Consider the interaction of all colors</li>
                    <li>Balance dominant and accent colors</li>
                    <li>Test accessibility for color-blind users</li>
                  </>
                )}
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

import { copyToClipboard } from '../../../../../../utils/clipboard'
import type { TabProps } from '../types'

type NamingStyleKey = 'simple' | 'descriptive' | 'emotional' | 'technical' | 'vibrancy'
type NamingStyles = Partial<Record<NamingStyleKey, string>>

export function NamingStylesTab({ color }: TabProps) {
  // Extract naming styles from semantic_names
  const styleDescriptions: Record<
    NamingStyleKey,
    { title: string; description: string; example: string }
  > = {
    simple: {
      title: 'Simple',
      description: 'Just the color name',
      example: 'orange'
    },
    descriptive: {
      title: 'Descriptive',
      description: 'Temperature + hue + lightness',
      example: 'warm-orange-light'
    },
    emotional: {
      title: 'Emotional',
      description: 'Mood-based naming',
      example: 'vibrant-coral'
    },
    technical: {
      title: 'Technical',
      description: 'Hue + saturation + lightness',
      example: 'orange-saturated-light'
    },
    vibrancy: {
      title: 'Vibrancy',
      description: 'Vibrancy level + hue',
      example: 'vibrant-orange'
    }
  }

  let namingStyles: NamingStyles | null = null

  if (color.semantic_names) {
    if (typeof color.semantic_names === 'string') {
      try {
        const parsed = JSON.parse(color.semantic_names) as unknown
        namingStyles =
          parsed && typeof parsed === 'object'
            ? (Object.entries(parsed as Record<string, unknown>).reduce((acc, [key, value]) => {
                if (typeof value === 'string') {
                  acc[key as NamingStyleKey] = value
                }
                return acc
              }, {} as NamingStyles) as NamingStyles)
            : null
      } catch {
        // Invalid JSON, skip
      }
    } else {
      namingStyles = (Object.entries(color.semantic_names as Record<string, unknown>).reduce(
        (acc, [key, value]) => {
          if (typeof value === 'string') {
            acc[key as NamingStyleKey] = value
          }
          return acc
        },
        {} as NamingStyles
      ) as NamingStyles)
    }
  }

  const availableStyles = (Object.keys(styleDescriptions) as NamingStyleKey[]).filter(
    (style) => namingStyles && typeof namingStyles[style] === 'string'
  )

  if (!namingStyles || availableStyles.length === 0) {
    return (
      <div className="naming-styles-content">
        <div className="empty-state">
          <p>No naming styles available for this color</p>
        </div>
      </div>
    )
  }

  return (
    <div className="naming-styles-content">
      <section className="naming-styles-section">
        <p className="section-description">
          Five different semantic naming styles for this color, each highlighting different aspects:
        </p>

        <div className="naming-styles-grid">
          {availableStyles.map((style) => (
            <div key={style} className="naming-style-card">
              <div className="style-header">
                <h4>{styleDescriptions[style].title}</h4>
                <p className="style-description">{styleDescriptions[style].description}</p>
              </div>

              <div className="style-name">
                <code
                  onClick={() => void copyToClipboard(namingStyles![style])}
                  title="Click to copy"
                >
                  {namingStyles[style]}
                </code>
              </div>

              <div className="style-usage">
                <span className="usage-tag">{style}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="naming-reference">
        <h3>Reference</h3>
        <ul className="reference-list">
          <li>
            <strong>Simple:</strong> Minimal name for quick reference
          </li>
          <li>
            <strong>Descriptive:</strong> Best for design systems documentation
          </li>
          <li>
            <strong>Emotional:</strong> For marketing or brand-focused contexts
          </li>
          <li>
            <strong>Technical:</strong> For color science documentation
          </li>
          <li>
            <strong>Vibrancy:</strong> For palette analysis and sorting
          </li>
        </ul>
      </section>
    </div>
  )
}

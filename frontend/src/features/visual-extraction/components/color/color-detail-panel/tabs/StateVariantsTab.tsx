import { copyToClipboard } from '../../../../../../utils/clipboard'
import type { TabProps } from '../types'

interface StateVariant {
  name: string
  hex?: string
  description: string
  method: string
}

export function StateVariantsTab({ color }: TabProps) {
  // Build state variants from tint, shade, tone colors
  const variants: StateVariant[] = []

  if (color.tint_color) {
    variants.push({
      name: 'Tint',
      hex: color.tint_color,
      description: 'Lighter variant for hover states',
      method: 'Blend 50% with white using OKLCH space'
    })
  }

  if (color.shade_color) {
    variants.push({
      name: 'Shade',
      hex: color.shade_color,
      description: 'Darker variant for active/pressed states',
      method: 'Blend 50% with black using OKLCH space'
    })
  }

  if (color.tone_color) {
    variants.push({
      name: 'Tone',
      hex: color.tone_color,
      description: 'Neutral variant for disabled states',
      method: 'Blend 50% with gray using OKLCH space'
    })
  }

  // Generate synthetic state variants for common UI interactions
  const stateVariants: StateVariant[] = [
    {
      name: 'Default',
      hex: color.hex,
      description: 'Base state - normal button or component',
      method: 'Original extracted color'
    },
    {
      name: 'Hover',
      hex: color.tint_color || color.hex,
      description: 'Interactive feedback when user hovers',
      method: 'Use tint variant (increased lightness)'
    },
    {
      name: 'Active/Pressed',
      hex: color.shade_color || color.hex,
      description: 'Feedback when component is in active/pressed state',
      method: 'Use shade variant (decreased lightness)'
    },
    {
      name: 'Disabled',
      hex: color.tone_color || color.hex,
      description: 'Desaturated state for disabled components',
      method: 'Use tone variant (decreased saturation)'
    }
  ]

  if (variants.length === 0) {
    return (
      <div className="state-variants-content">
        <div className="empty-state">
          <p>No state variants generated for this color</p>
        </div>
      </div>
    )
  }

  return (
    <div className="state-variants-content">
      <section className="state-variants-section">
        <h3>Interactive State Variants</h3>
        <p className="section-description">
          These color variants are automatically generated for interactive UI states using OKLCH color space adjustments:
        </p>

        <div className="state-variants-grid">
          {stateVariants.map((variant) => (
            <div key={variant.name} className="state-variant-card">
              <div className="variant-label-header">
                <h4>{variant.name}</h4>
              </div>

              {variant.hex && (
                <div className="variant-swatch-container">
                  <div
                    className="variant-swatch-large"
                    style={{ backgroundColor: variant.hex }}
                    onClick={() => void copyToClipboard(variant.hex!)}
                    title="Click to copy hex value"
                  />
                  <code
                    className="variant-hex"
                    onClick={() => void copyToClipboard(variant.hex!)}
                    title="Click to copy"
                  >
                    {variant.hex}
                  </code>
                </div>
              )}

              <div className="variant-description">
                <p>{variant.description}</p>
              </div>

              <div className="variant-method">
                <span className="method-label">Generation:</span>
                <span className="method-text">{variant.method}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="state-variants-reference">
        <h3>Generation Method</h3>
        <div className="method-explanation">
          <p>
            All state variants are generated using the <strong>OKLCH color space</strong>, which provides
            perceptually uniform color adjustments:
          </p>
          <ul>
            <li>
              <strong>Tint:</strong> Increases lightness (L) by 25% while maintaining hue and chroma
            </li>
            <li>
              <strong>Shade:</strong> Decreases lightness (L) by 25% while maintaining hue and chroma
            </li>
            <li>
              <strong>Tone:</strong> Decreases chroma (C) by 40% for desaturation while maintaining lightness
            </li>
          </ul>
          <p className="note">
            Using OKLCH ensures perceptually consistent adjustments across colors, unlike HSL which can
            produce unexpected results for highly saturated or dark colors.
          </p>
        </div>
      </section>

      <section className="state-variants-usage">
        <h3>Usage Examples</h3>
        <div className="usage-examples">
          <div className="usage-example">
            <code className="usage-code">button:hover</code>
            <span className="usage-arrow">→</span>
            <span className="usage-value">Use Tint variant</span>
          </div>
          <div className="usage-example">
            <code className="usage-code">button:active</code>
            <span className="usage-arrow">→</span>
            <span className="usage-value">Use Shade variant</span>
          </div>
          <div className="usage-example">
            <code className="usage-code">button:disabled</code>
            <span className="usage-arrow">→</span>
            <span className="usage-value">Use Tone variant</span>
          </div>
        </div>
      </section>
    </div>
  )
}

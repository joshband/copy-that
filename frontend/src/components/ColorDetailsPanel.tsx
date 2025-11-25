import './ColorDetailsPanel.css'
import { formatSemanticValue } from '../utils/semanticNames'

interface ColorToken {
  hex: string
  name: string
  confidence: number
  semantic_names?: Record<string, unknown> | null
  temperature?: string
  saturation_level?: string
  lightness_level?: string
  category?: string
  tint_color?: string
  shade_color?: string
  tone_color?: string
  wcag_contrast_on_white?: number
  wcag_contrast_on_black?: number
  wcag_aa_compliant_text?: boolean
  wcag_aaa_compliant_text?: boolean
  colorblind_safe?: boolean
  usage?: string | string[]
}

interface Props {
  color: ColorToken | null
}

export function ColorDetailsPanel({ color }: Props) {
  if (!color) {
    return (
      <div className="color-details empty">
        <p>👆 Select a color to explore</p>
      </div>
    )
  }

  const usageArray = Array.isArray(color.usage) ? color.usage : (color.usage != null && color.usage !== '') ? [color.usage] : []

  return (
    <div className="color-details">
      {/* Color Swatch */}
      <div className="details-swatch" style={{ backgroundColor: color.hex }} />

      {/* Color Name */}
      <h3 className="color-name">{color.name}</h3>
      <div className="color-hex">{color.hex}</div>
      <div className="confidence-score">Confidence: {(color.confidence * 100).toFixed(1)}%</div>

      {/* Quick Tags */}
      <div className="quick-tags">
        {color.temperature != null && color.temperature !== '' && <span className="tag temp">{color.temperature}</span>}
        {color.saturation_level != null && color.saturation_level !== '' && <span className="tag sat">{color.saturation_level}</span>}
        {color.lightness_level != null && color.lightness_level !== '' && <span className="tag light">{color.lightness_level}</span>}
      </div>

      {/* Semantic Names */}
      {(() => {
        const entries =
          typeof color.semantic_names === 'string'
            ? [['label', color.semantic_names] as const]
            : color.semantic_names
              ? Object.entries(color.semantic_names)
              : []

        return entries.length > 0 ? (
          <div className="section">
            <h4>Semantic Names</h4>
            <ul className="semantic-list">
              {entries.map(([style, name]) => {
                const formatted = formatSemanticValue(name)
                return (
                  <li key={style}>
                    <span className="style-label">{style}</span>
                    <span className="style-value">{formatted}</span>
                  </li>
                )
              })}
            </ul>
          </div>
        ) : null
      })()}

      {/* WCAG Accessibility */}
      <div className="section">
        <h4>Accessibility</h4>
        <div className="wcag-info">
          {color.wcag_contrast_on_white != null && (
            <div className="contrast-row">
              <span>On White:</span>
              <span className="ratio">{color.wcag_contrast_on_white.toFixed(2)}:1</span>
              {color.wcag_aaa_compliant_text === true && <span className="badge aaa">AAA ✓</span>}
              {color.wcag_aaa_compliant_text !== true && color.wcag_aa_compliant_text === true && (
                <span className="badge aa">AA ✓</span>
              )}
            </div>
          )}
          {color.wcag_contrast_on_black != null && (
            <div className="contrast-row">
              <span>On Black:</span>
              <span className="ratio">{color.wcag_contrast_on_black.toFixed(2)}:1</span>
            </div>
          )}
          {color.colorblind_safe === true && <div className="colorblind-safe">✓ Colorblind safe</div>}
        </div>
      </div>

      {/* Variants */}
      {(color.tint_color != null || color.shade_color != null || color.tone_color != null) && (
        <div className="section">
          <h4>Variants</h4>
          <div className="variants">
            {color.tint_color != null && color.tint_color !== '' && (
              <div className="variant">
                <span className="variant-label">Tint</span>
                <div className="variant-swatch" style={{ backgroundColor: color.tint_color }} />
              </div>
            )}
            {color.shade_color != null && color.shade_color !== '' && (
              <div className="variant">
                <span className="variant-label">Shade</span>
                <div className="variant-swatch" style={{ backgroundColor: color.shade_color }} />
              </div>
            )}
            {color.tone_color != null && color.tone_color !== '' && (
              <div className="variant">
                <span className="variant-label">Tone</span>
                <div className="variant-swatch" style={{ backgroundColor: color.tone_color }} />
              </div>
            )}
          </div>
        </div>
      )}

      {/* Usage */}
      {usageArray.length > 0 && (
        <div className="section">
          <h4>Usage</h4>
          <ul className="usage-list">
            {usageArray.map((use, idx) => (
              <li key={idx}>{use}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Category */}
      {color.category != null && color.category !== '' && (
        <div className="section">
          <h4>Category</h4>
          <div className="category-badge">{color.category}</div>
        </div>
      )}
    </div>
  )
}

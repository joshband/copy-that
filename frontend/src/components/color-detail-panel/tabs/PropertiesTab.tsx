import { copyToClipboard } from '../../utils'
import type { TabProps } from '../types'

export function PropertiesTab({ color }: TabProps) {
  return (
    <div className="properties-content">
      <section className="props-section">
        <h3>Color Attributes</h3>
        <div className="properties-grid">
          {color.saturation_level != null && color.saturation_level !== '' && (
            <div className="prop-item">
              <label>Saturation</label>
              <span>{color.saturation_level}</span>
            </div>
          )}
          {color.lightness_level != null && color.lightness_level !== '' && (
            <div className="prop-item">
              <label>Lightness</label>
              <span>{color.lightness_level}</span>
            </div>
          )}
          {color.closest_web_safe != null && color.closest_web_safe !== '' && (
            <div className="prop-item">
              <label>Web Safe</label>
              <code
                onClick={() => void copyToClipboard(color.closest_web_safe ?? '')}
                title="Click to copy"
              >
                {color.closest_web_safe}
              </code>
            </div>
          )}
          {color.delta_e_to_dominant != null && (
            <div className="prop-item">
              <label>ΔE (to dominant)</label>
              <span>{color.delta_e_to_dominant?.toFixed(2)}</span>
            </div>
          )}
        </div>
      </section>

      {(color.tint_color != null || color.shade_color != null || color.tone_color != null) && (
        <section className="props-section">
          <h3>Variants</h3>
          <div className="variants-grid">
            {color.tint_color != null && color.tint_color !== '' && (
              <div className="variant-item">
                <div
                  className="variant-swatch"
                  style={{ backgroundColor: color.tint_color }}
                  onClick={() => void copyToClipboard(color.tint_color ?? '')}
                  title="Click to copy"
                />
                <code>{color.tint_color}</code>
                <span className="variant-label">Tint</span>
              </div>
            )}
            {color.shade_color != null && color.shade_color !== '' && (
              <div className="variant-item">
                <div
                  className="variant-swatch"
                  style={{ backgroundColor: color.shade_color }}
                  onClick={() => void copyToClipboard(color.shade_color ?? '')}
                  title="Click to copy"
                />
                <code>{color.shade_color}</code>
                <span className="variant-label">Shade</span>
              </div>
            )}
            {color.tone_color != null && color.tone_color !== '' && (
              <div className="variant-item">
                <div
                  className="variant-swatch"
                  style={{ backgroundColor: color.tone_color }}
                  onClick={() => void copyToClipboard(color.tone_color ?? '')}
                  title="Click to copy"
                />
                <code>{color.tone_color}</code>
                <span className="variant-label">Tone</span>
              </div>
            )}
          </div>
        </section>
      )}
    </div>
  )
}

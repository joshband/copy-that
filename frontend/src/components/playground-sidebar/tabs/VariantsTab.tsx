import type { ColorToken } from '../../../types/index'

interface Props {
  selectedColor: ColorToken
}

export function VariantsTab({ selectedColor }: Props) {
  return (
    <div className="variants-content">
      <h4>Generate Variants</h4>
      <p className="variants-info">
        Create tints, shades, and tones of this color for design systems.
      </p>

      {selectedColor.tint_color && (
        <div className="variant-group">
          <span className="variant-label">Tint (50% lighter)</span>
          <div
            className="variant-swatch"
            style={{ backgroundColor: selectedColor.tint_color }}
          />
          <code className="variant-code">{selectedColor.tint_color}</code>
        </div>
      )}

      {selectedColor.shade_color && (
        <div className="variant-group">
          <span className="variant-label">Shade (50% darker)</span>
          <div
            className="variant-swatch"
            style={{ backgroundColor: selectedColor.shade_color }}
          />
          <code className="variant-code">{selectedColor.shade_color}</code>
        </div>
      )}

      {selectedColor.tone_color && (
        <div className="variant-group">
          <span className="variant-label">Tone (50% desaturated)</span>
          <div
            className="variant-swatch"
            style={{ backgroundColor: selectedColor.tone_color }}
          />
          <code className="variant-code">{selectedColor.tone_color}</code>
        </div>
      )}

      <button className="generate-btn">🔄 Generate more variants</button>
    </div>
  )
}

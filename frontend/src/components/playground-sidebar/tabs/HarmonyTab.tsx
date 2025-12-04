import type { ColorToken } from '../types'

interface Props {
  selectedColor: ColorToken
}

export function HarmonyTab({ selectedColor }: Props) {
  return (
    <div className="harmony-content">
      <h4>Harmony Relationships</h4>
      <div className="harmony-wheel">
        <div className="color-circle" style={{ backgroundColor: selectedColor.hex }} />
      </div>
      <p className="harmony-info">
        This color can create harmonious palettes with other colors based on hue relationships.
      </p>
      <div className="harmony-types">
        <div className="harmony-item">
          <span className="harmony-label">Monochromatic</span>
          <p className="harmony-desc">Variations of this color</p>
        </div>
        <div className="harmony-item">
          <span className="harmony-label">Analogous</span>
          <p className="harmony-desc">Adjacent hues</p>
        </div>
        <div className="harmony-item">
          <span className="harmony-label">Complementary</span>
          <p className="harmony-desc">Opposite hue</p>
        </div>
      </div>
    </div>
  )
}

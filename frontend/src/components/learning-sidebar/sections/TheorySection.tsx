interface Props {
  isExpanded: boolean
}

export function TheorySection({ isExpanded }: Props) {
  if (!isExpanded) return null

  return (
    <div className="section-content">
      <div className="theory-content">
        <h4>Harmony Types (9)</h4>
        <ul className="theory-list">
          <li>
            <strong>Monochromatic</strong>
            <span className="desc">Single hue with variations</span>
          </li>
          <li>
            <strong>Analogous</strong>
            <span className="desc">Adjacent hues on wheel</span>
          </li>
          <li>
            <strong>Complementary</strong>
            <span className="desc">Opposite hues</span>
          </li>
          <li>
            <strong>Triadic</strong>
            <span className="desc">3 equally spaced hues</span>
          </li>
          <li>
            <strong>Tetradic</strong>
            <span className="desc">4 equally spaced hues</span>
          </li>
        </ul>

        <h4 style={{ marginTop: '0.75rem' }}>Properties</h4>
        <div className="properties-grid">
          <div className="property">
            <span className="prop-label">Temperature</span>
            <span className="prop-value">🔥 Warm / Cool ❄️</span>
          </div>
          <div className="property">
            <span className="prop-label">Saturation</span>
            <span className="prop-value">Vibrant ↔️ Muted</span>
          </div>
          <div className="property">
            <span className="prop-label">Lightness</span>
            <span className="prop-value">Light ↔️ Dark</span>
          </div>
        </div>
      </div>
    </div>
  )
}

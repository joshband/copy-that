import './ColorTokenDisplay.css'

interface ColorToken {
  id?: number
  hex: string
  rgb: string
  name: string
  semantic_name?: string
  confidence: number
  harmony?: string
  usage?: string[]
}

interface Props {
  colors: ColorToken[]
}

export default function ColorTokenDisplay({ colors }: Props) {
  return (
    <div className="color-tokens">
      <div className="tokens-grid">
        {colors.map((color, index) => (
          <div key={index} className="token-card">
            {/* Color Swatch */}
            <div
              className="color-swatch"
              style={{ backgroundColor: color.hex }}
              title={color.hex}
            />

            {/* Color Info */}
            <div className="color-info">
              <h3 className="color-name">{color.name}</h3>

              {/* Hex Code */}
              <div className="color-code">
                <span className="label">Hex:</span>
                <code>{color.hex}</code>
                <button
                  className="copy-btn"
                  onClick={() => navigator.clipboard.writeText(color.hex)}
                  title="Copy hex code"
                >
                  📋
                </button>
              </div>

              {/* RGB Code */}
              <div className="color-code">
                <span className="label">RGB:</span>
                <code>{color.rgb}</code>
                <button
                  className="copy-btn"
                  onClick={() => navigator.clipboard.writeText(color.rgb)}
                  title="Copy RGB code"
                >
                  📋
                </button>
              </div>

              {/* Semantic Name Badge */}
              {color.semantic_name && (
                <div className="semantic-name">
                  <span className="badge">{color.semantic_name}</span>
                </div>
              )}

              {/* Confidence Score */}
              <div className="confidence">
                <span className="label">Confidence:</span>
                <div className="confidence-bar">
                  <div
                    className="confidence-fill"
                    style={{ width: `${color.confidence * 100}%` }}
                  />
                </div>
                <span className="confidence-value">
                  {(color.confidence * 100).toFixed(0)}%
                </span>
              </div>

              {/* Harmony Info */}
              {color.harmony && (
                <div className="harmony">
                  <span className="label">Harmony:</span>
                  <span className="value">{color.harmony}</span>
                </div>
              )}

              {/* Usage Tags */}
              {color.usage && color.usage.length > 0 && (
                <div className="usage">
                  <span className="label">Usage:</span>
                  <div className="tags">
                    {color.usage.map((use, i) => (
                      <span key={i} className="tag">
                        {use}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Summary Stats */}
      <div className="summary">
        <p>
          Extracted <strong>{colors.length}</strong> color{colors.length !== 1 ? 's' : ''} •
          Average confidence:{' '}
          <strong>
            {(
              (colors.reduce((sum, c) => sum + c.confidence, 0) / colors.length) *
              100
            ).toFixed(0)}
            %
          </strong>
        </p>
      </div>
    </div>
  )
}

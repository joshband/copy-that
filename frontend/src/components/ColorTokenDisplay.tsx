import './ColorTokenDisplay.css'

interface ColorToken {
  id?: number
  project_id?: number
  extraction_job_id?: number
  hex: string
  rgb: string
  hsl?: string
  hsv?: string
  name: string
  semantic_name?: string
  category?: string
  confidence: number
  harmony?: string
  temperature?: string
  saturation_level?: string
  lightness_level?: string
  usage?: string | string[]
  count?: number
  prominence_percentage?: number
  wcag_contrast_on_white?: number
  wcag_contrast_on_black?: number
  wcag_aa_compliant_text?: boolean
  wcag_aaa_compliant_text?: boolean
  wcag_aa_compliant_normal?: boolean
  wcag_aaa_compliant_normal?: boolean
  colorblind_safe?: boolean
  tint_color?: string
  shade_color?: string
  tone_color?: string
  closest_web_safe?: string
  closest_css_named?: string
  delta_e_to_dominant?: number
  is_neutral?: boolean
  kmeans_cluster_id?: number
  sam_segmentation_mask?: string
  clip_embeddings?: number[]
  histogram_significance?: number
  created_at?: string
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
              <div className="color-header">
                <h3 className="color-name">{color.name}</h3>
                {color.count && color.count > 1 && (
                  <span
                    className="count-badge"
                    title={`Detected ${color.count} times in the design`}
                  >
                    {color.count}x
                  </span>
                )}
              </div>

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
              {color.usage && (Array.isArray(color.usage) ? color.usage.length > 0 : color.usage.length > 0) && (
                <div className="usage">
                  <span className="label">Usage:</span>
                  <div className="tags">
                    {(Array.isArray(color.usage) ? color.usage : color.usage.split(',')).map((use, i) => (
                      <span key={i} className="tag">
                        {typeof use === 'string' ? use.trim() : use}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Additional Color Formats */}
              <div className="formats-section">
                {color.hsl && <div className="format"><span className="label">HSL:</span> <code>{color.hsl}</code></div>}
                {color.hsv && <div className="format"><span className="label">HSV:</span> <code>{color.hsv}</code></div>}
              </div>

              {/* Color Properties */}
              <div className="properties-section">
                {color.category && <div className="prop"><span className="label">Category:</span> {color.category}</div>}
                {color.temperature && <div className="prop"><span className="label">Temperature:</span> {color.temperature}</div>}
                {color.saturation_level && <div className="prop"><span className="label">Saturation:</span> {color.saturation_level}</div>}
                {color.lightness_level && <div className="prop"><span className="label">Lightness:</span> {color.lightness_level}</div>}
                {color.is_neutral && <div className="prop"><span className="badge-neutral">Neutral</span></div>}
              </div>

              {/* Prominence */}
              {color.prominence_percentage && (
                <div className="prominence">
                  <span className="label">Prominence:</span>
                  <span className="value">{color.prominence_percentage.toFixed(1)}%</span>
                </div>
              )}

              {/* Accessibility Info */}
              {(color.wcag_contrast_on_white || color.wcag_contrast_on_black || color.colorblind_safe) && (
                <div className="accessibility">
                  <span className="section-title">♿ Accessibility</span>
                  {color.wcag_contrast_on_white && (
                    <div className="contrast">
                      <span className="label">White contrast:</span>
                      <span className={`value ${color.wcag_aa_compliant_text ? 'pass' : 'fail'}`}>
                        {color.wcag_contrast_on_white.toFixed(2)}:1
                      </span>
                    </div>
                  )}
                  {color.wcag_contrast_on_black && (
                    <div className="contrast">
                      <span className="label">Black contrast:</span>
                      <span className={`value ${color.wcag_aa_compliant_normal ? 'pass' : 'fail'}`}>
                        {color.wcag_contrast_on_black.toFixed(2)}:1
                      </span>
                    </div>
                  )}
                  {color.colorblind_safe && (
                    <div className="prop"><span className="badge-safe">Colorblind Safe</span></div>
                  )}
                </div>
              )}

              {/* Color Variants */}
              {(color.tint_color || color.shade_color || color.tone_color) && (
                <div className="variants">
                  <span className="section-title">Variants</span>
                  <div className="variant-swatches">
                    {color.tint_color && (
                      <div className="variant" title="Tint (50% lighter)">
                        <div className="swatch" style={{ backgroundColor: color.tint_color }} />
                        <span className="label">Tint</span>
                      </div>
                    )}
                    {color.shade_color && (
                      <div className="variant" title="Shade (50% darker)">
                        <div className="swatch" style={{ backgroundColor: color.shade_color }} />
                        <span className="label">Shade</span>
                      </div>
                    )}
                    {color.tone_color && (
                      <div className="variant" title="Tone (50% desaturated)">
                        <div className="swatch" style={{ backgroundColor: color.tone_color }} />
                        <span className="label">Tone</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Advanced Properties */}
              {(color.closest_web_safe || color.closest_css_named || color.delta_e_to_dominant) && (
                <div className="advanced">
                  <span className="section-title">Advanced</span>
                  {color.closest_web_safe && <div className="prop"><span className="label">Web-safe:</span> <code>{color.closest_web_safe}</code></div>}
                  {color.closest_css_named && <div className="prop"><span className="label">CSS named:</span> {color.closest_css_named}</div>}
                  {color.delta_e_to_dominant && <div className="prop"><span className="label">Delta E:</span> {color.delta_e_to_dominant.toFixed(2)}</div>}
                </div>
              )}

              {/* ML Properties */}
              {(color.kmeans_cluster_id || color.histogram_significance) && (
                <div className="ml-info">
                  <span className="section-title">ML Analysis</span>
                  {color.kmeans_cluster_id !== undefined && <div className="prop"><span className="label">Cluster:</span> #{color.kmeans_cluster_id}</div>}
                  {color.histogram_significance && <div className="prop"><span className="label">Significance:</span> {(color.histogram_significance * 100).toFixed(1)}%</div>}
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

import './ColorTokenDisplay.css'
import { HarmonyVisualizer } from './HarmonyVisualizer'
import { AccessibilityVisualizer } from './AccessibilityVisualizer'
import { ColorNarrative } from './ColorNarrative'
import { useState } from 'react'

interface ColorToken {
  id?: number
  project_id?: number
  extraction_job_id?: number
  hex: string
  rgb: string
  hsl?: string
  hsv?: string
  name: string
  design_intent?: string
  semantic_names?: Record<string, string> | null
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
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null)

  return (
    <div className="color-tokens">
      <div className="tokens-container">
        {colors.map((color, index) => (
          <div key={index} className={`token-card ${expandedIndex === index ? 'expanded' : 'collapsed'}`}>
            {/* Collapsed View - Quick Summary */}
            <div
              className="card-header"
              onClick={() => setExpandedIndex(expandedIndex === index ? null : index)}
            >
              <div className="header-left">
                <div
                  className="color-swatch-small"
                  style={{ backgroundColor: color.hex }}
                />
                <div className="header-info">
                  <h3 className="color-name">{color.name}</h3>
                  <code className="hex-code">{color.hex}</code>
                </div>
              </div>

              <div className="header-right">
                {color.count && color.count > 1 && (
                  <span className="count-badge">{color.count}x</span>
                )}
                <div className="confidence-indicator">
                  <div
                    className="confidence-bar-small"
                    style={{ width: `${color.confidence * 100}%` }}
                  />
                </div>
                <span className="expand-icon">{expandedIndex === index ? '▼' : '▶'}</span>
              </div>
            </div>

            {/* Expanded View - Full Educational Experience */}
            {expandedIndex === index && (
              <div className="card-expanded">
                {/* Quick Copy Section */}
                <div className="quick-access">
                  <div className="code-format">
                    <span className="label">Hex</span>
                    <code>{color.hex}</code>
                    <button
                      className="copy-btn"
                      onClick={() => navigator.clipboard.writeText(color.hex)}
                      title="Copy"
                    >
                      📋
                    </button>
                  </div>

                  <div className="code-format">
                    <span className="label">RGB</span>
                    <code>{color.rgb}</code>
                    <button
                      className="copy-btn"
                      onClick={() => navigator.clipboard.writeText(color.rgb)}
                      title="Copy"
                    >
                      📋
                    </button>
                  </div>

                  {color.hsl && (
                    <div className="code-format">
                      <span className="label">HSL</span>
                      <code>{color.hsl}</code>
                      <button
                        className="copy-btn"
                        onClick={() => navigator.clipboard.writeText(color.hsl)}
                        title="Copy"
                      >
                        📋
                      </button>
                    </div>
                  )}
                </div>

                {/* Color Narrative Widget */}
                <ColorNarrative
                  hex={color.hex}
                  name={color.name}
                  semanticNames={color.semantic_names}
                  temperature={color.temperature}
                  saturationLevel={color.saturation_level}
                  lightnessLevel={color.lightness_level}
                  isNeutral={color.is_neutral}
                  prominencePercentage={color.prominence_percentage}
                  category={color.category}
                />

                {/* Harmony Visualizer Widget */}
                {color.harmony && (
                  <HarmonyVisualizer harmony={color.harmony} hex={color.hex} />
                )}

                {/* Accessibility Visualizer Widget */}
                {(color.wcag_contrast_on_white ||
                  color.wcag_contrast_on_black ||
                  color.colorblind_safe) && (
                  <AccessibilityVisualizer
                    hex={color.hex}
                    wcagContrastWhite={color.wcag_contrast_on_white}
                    wcagContrastBlack={color.wcag_contrast_on_black}
                    wcagAACompliantText={color.wcag_aa_compliant_text}
                    wcagAAACompliantText={color.wcag_aaa_compliant_text}
                    wcagAACompliantNormal={color.wcag_aa_compliant_normal}
                    wcagAAACompliantNormal={color.wcag_aaa_compliant_normal}
                    colorblindSafe={color.colorblind_safe}
                  />
                )}

                {/* Variants Section */}
                {(color.tint_color || color.shade_color || color.tone_color) && (
                  <div className="variants-section">
                    <h3>Tint, Shade & Tone Variants</h3>
                    <p className="variants-explanation">
                      These are mathematically derived variants of your color. Tints are lighter (mixed with white), shades are
                      darker (mixed with black), and tones are desaturated (mixed with gray).
                    </p>
                    <div className="variant-swatches">
                      <div className="variant" title="Original">
                        <div
                          className="swatch"
                          style={{ backgroundColor: color.hex }}
                        />
                        <span className="label">Original</span>
                      </div>
                      {color.tint_color && (
                        <div className="variant" title="Tint (lighter)">
                          <div
                            className="swatch"
                            style={{ backgroundColor: color.tint_color }}
                          />
                          <span className="label">Tint</span>
                        </div>
                      )}
                      {color.shade_color && (
                        <div className="variant" title="Shade (darker)">
                          <div
                            className="swatch"
                            style={{ backgroundColor: color.shade_color }}
                          />
                          <span className="label">Shade</span>
                        </div>
                      )}
                      {color.tone_color && (
                        <div className="variant" title="Tone (desaturated)">
                          <div
                            className="swatch"
                            style={{ backgroundColor: color.tone_color }}
                          />
                          <span className="label">Tone</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Technical Details */}
                <div className="technical-details">
                  <h3>Technical Details</h3>
                  <div className="details-grid">
                    <div className="detail-item">
                      <span className="label">Confidence Score</span>
                      <span className="value">
                        {(color.confidence * 100).toFixed(0)}%
                      </span>
                      <p className="description">
                        How confident the AI was in detecting this color
                      </p>
                    </div>

                    {color.closest_css_named && (
                      <div className="detail-item">
                        <span className="label">Closest CSS Name</span>
                        <span className="value">{color.closest_css_named}</span>
                        <p className="description">
                          Nearest standard CSS named color
                        </p>
                      </div>
                    )}

                    {color.delta_e_to_dominant && (
                      <div className="detail-item">
                        <span className="label">Delta-E Distance</span>
                        <span className="value">
                          {color.delta_e_to_dominant.toFixed(2)}
                        </span>
                        <p className="description">
                          Perceptual distance to dominant color
                        </p>
                      </div>
                    )}

                    {color.kmeans_cluster_id !== undefined && (
                      <div className="detail-item">
                        <span className="label">Cluster ID</span>
                        <span className="value">#{color.kmeans_cluster_id}</span>
                        <p className="description">
                          K-means clustering assignment
                        </p>
                      </div>
                    )}

                    {color.histogram_significance && (
                      <div className="detail-item">
                        <span className="label">Histogram Significance</span>
                        <span className="value">
                          {(color.histogram_significance * 100).toFixed(1)}%
                        </span>
                        <p className="description">
                          Visual prominence in the design
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Summary Stats */}
      <div className="summary">
        <div className="summary-content">
          <p>
            Extracted <strong>{colors.length}</strong> color{colors.length !== 1 ? 's' : ''} from your design
          </p>
          <p>
            Average confidence:{' '}
            <strong>
              {(
                (colors.reduce((sum, c) => sum + c.confidence, 0) /
                  colors.length) *
                100
              ).toFixed(0)}
              %
            </strong>
          </p>
          <p className="summary-tips">
            💡 Click any color to explore its properties, understand the harmony, and learn about accessibility.
          </p>
        </div>
      </div>
    </div>
  )
}

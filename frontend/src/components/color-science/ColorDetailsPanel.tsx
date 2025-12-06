import React from 'react'
import { ColorToken } from './types'
import { useColorConversion, useContrastCalculation } from './hooks'
import { formatSemanticValue } from '../../utils/semanticNames'

interface ColorDetailsPanelProps {
  selectedColor: ColorToken | null
  paletteDescription?: string
}

export function ColorDetailsPanel({ selectedColor, paletteDescription }: ColorDetailsPanelProps) {
  const { getVibrancy, hexToRgb, hexToHsl, hexToHsv } = useColorConversion()
  const { getAccessibilityBadges } = useContrastCalculation()

  if (!selectedColor) {
    return (
      <section className="panel-card details-section empty">
        <p>Select a color to see detailed analysis</p>
      </section>
    )
  }

  // Use API values if available, otherwise compute from HEX
  const rgbValue = selectedColor.rgb || hexToRgb(selectedColor.hex)
  const hslValue = selectedColor.hsl || hexToHsl(selectedColor.hex)
  const hsvValue = selectedColor.hsv || hexToHsv(selectedColor.hex)

  const entries =
    typeof selectedColor.semantic_names === 'string'
      ? [['label', selectedColor.semantic_names] as const]
      : selectedColor.semantic_names
        ? Object.entries(selectedColor.semantic_names)
        : []

  return (
    <section className="panel-card details-section">
      <h2>Color Analysis</h2>

      {/* Main Swatch */}
      <div className="detail-swatch" style={{ backgroundColor: selectedColor.hex }} />

      <h3 className="detail-name">{selectedColor.name}</h3>
      <div className="detail-confidence">Confidence: {(selectedColor.confidence * 100).toFixed(1)}%</div>
      <div className="detail-confidence">Vibrancy: {getVibrancy(selectedColor)}</div>

      {/* Color Values */}
      <div className="detail-group">
        <h4>Color Values</h4>
        <div className="value-grid">
          <div className="value-item">
            <span className="value-label">HEX</span>
            <span className="value-data mono">{selectedColor.hex}</span>
          </div>
          {rgbValue && (
            <div className="value-item">
              <span className="value-label">RGB</span>
              <span className="value-data mono">{rgbValue}</span>
            </div>
          )}
          {hslValue && (
            <div className="value-item">
              <span className="value-label">HSL</span>
              <span className="value-data mono">{hslValue}</span>
            </div>
          )}
          {hsvValue && (
            <div className="value-item">
              <span className="value-label">HSV</span>
              <span className="value-data mono">{hsvValue}</span>
            </div>
          )}
        </div>
      </div>

      {/* Properties */}
      <div className="detail-group">
        <h4>Properties</h4>
        <div className="props-grid">
          {selectedColor.temperature && (
            <div className="prop-item">
              <span className="prop-label">Temperature</span>
              <span className="prop-value">{selectedColor.temperature}</span>
            </div>
          )}
          {selectedColor.saturation_level && (
            <div className="prop-item">
              <span className="prop-label">Saturation</span>
              <span className="prop-value">{selectedColor.saturation_level}</span>
            </div>
          )}
          {selectedColor.lightness_level && (
            <div className="prop-item">
              <span className="prop-label">Lightness</span>
              <span className="prop-value">{selectedColor.lightness_level}</span>
            </div>
          )}
          {selectedColor.harmony && (
            <div className="prop-item">
              <span className="prop-label">Harmony</span>
              <span className="prop-value">{selectedColor.harmony}</span>
            </div>
          )}
        </div>
      </div>

      {/* WCAG Accessibility */}
      <div className="detail-group">
        <h4>WCAG Accessibility</h4>
        <div className="wcag-details">
          {selectedColor.wcag_contrast_on_white != null && (
            <div className="wcag-row">
              <span className="wcag-label">On White</span>
              <span className={`wcag-ratio ${selectedColor.wcag_contrast_on_white >= 4.5 ? 'pass' : 'fail'}`}>
                {selectedColor.wcag_contrast_on_white.toFixed(2)}:1
              </span>
              <div className="wcag-badges">
                <span className={`badge ${selectedColor.wcag_aa_compliant_text ? 'pass' : 'fail'}`}>
                  AA {selectedColor.wcag_aa_compliant_text ? 'Pass' : 'Fail'}
                </span>
                <span className={`badge ${selectedColor.wcag_aaa_compliant_text ? 'pass' : 'fail'}`}>
                  AAA {selectedColor.wcag_aaa_compliant_text ? 'Pass' : 'Fail'}
                </span>
              </div>
            </div>
          )}
          {selectedColor.wcag_contrast_on_black != null && (
            <div className="wcag-row">
              <span className="wcag-label">On Black</span>
              <span className={`wcag-ratio ${selectedColor.wcag_contrast_on_black >= 4.5 ? 'pass' : 'fail'}`}>
                {selectedColor.wcag_contrast_on_black.toFixed(2)}:1
              </span>
            </div>
          )}
          {selectedColor.colorblind_safe && <div className="colorblind-safe">Colorblind Safe</div>}
        </div>
      </div>

      {/* Color Variants */}
      {(selectedColor.tint_color || selectedColor.shade_color || selectedColor.tone_color) && (
        <div className="detail-group">
          <h4>Color Variants</h4>
          <div className="variants-row">
            {selectedColor.tint_color && (
              <div className="variant-item">
                <div className="variant-swatch" style={{ backgroundColor: selectedColor.tint_color }} />
                <span className="variant-label">Tint</span>
              </div>
            )}
            <div className="variant-item">
              <div className="variant-swatch" style={{ backgroundColor: selectedColor.hex }} />
              <span className="variant-label">Base</span>
            </div>
            {selectedColor.shade_color && (
              <div className="variant-item">
                <div className="variant-swatch" style={{ backgroundColor: selectedColor.shade_color }} />
                <span className="variant-label">Shade</span>
              </div>
            )}
            {selectedColor.tone_color && (
              <div className="variant-item">
                <div className="variant-swatch" style={{ backgroundColor: selectedColor.tone_color }} />
                <span className="variant-label">Tone</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Semantic Names */}
      {entries.length > 0 && (
        <div className="detail-group">
          <h4>Semantic Names</h4>
          <div className="semantic-list">
            {(entries as any).map(([type, name]: [string, any]) => {
              const formatted = formatSemanticValue(name)
              return (
                <div key={type} className="semantic-item">
                  <span className="semantic-type">{type}</span>
                  <span className="semantic-name">{formatted}</span>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Design Intent */}
      {selectedColor.design_intent && (
        <div className="detail-group">
          <h4>Design Intent</h4>
          <p className="design-intent">{selectedColor.design_intent}</p>
        </div>
      )}

      {/* Web Safe & CSS Named */}
      {(selectedColor.closest_web_safe || selectedColor.closest_css_named) && (
        <div className="detail-group">
          <h4>Web Integration</h4>
          <div className="web-info">
            {selectedColor.closest_web_safe && (
              <div className="web-item">
                <span className="web-label">Web Safe</span>
                <span className="web-value">{selectedColor.closest_web_safe}</span>
              </div>
            )}
            {selectedColor.closest_css_named && (
              <div className="web-item">
                <span className="web-label">CSS Named</span>
                <span className="web-value">{selectedColor.closest_css_named}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Narrative */}
      <div className="detail-group">
        <h4>Story</h4>
        <p className="design-intent">
          {selectedColor.temperature && `${selectedColor.temperature} `}tone with {getVibrancy(selectedColor)}{' '}
          vibrancy. Use as a {(selectedColor as any).role ?? 'primary'} accent; pair with high-contrast neutrals for
          text and balance with a complementary hue for CTAs.
          {paletteDescription && ` Palette note: ${paletteDescription}`}
        </p>
      </div>

      {/* Provenance */}
      {selectedColor.provenance && Object.keys(selectedColor.provenance).length > 0 && (
        <div className="detail-group">
          <h4>Provenance</h4>
          <div className="provenance-list">
            {Object.entries(selectedColor.provenance).map(([source, conf]) => (
              <div key={source} className="provenance-item">
                <span className="prov-source">{source}</span>
                <span className="prov-confidence">{(Number(conf) * 100).toFixed(0)}%</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  )
}

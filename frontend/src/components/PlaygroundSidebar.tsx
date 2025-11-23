import { useState } from 'react'
import './PlaygroundSidebar.css'

interface ColorToken {
  hex: string
  name: string
  semantic_names?: Record<string, string> | null
  tint_color?: string
  shade_color?: string
  tone_color?: string
  wcag_contrast_on_white?: number
  wcag_aa_compliant_text?: boolean
  wcag_aaa_compliant_text?: boolean
  colorblind_safe?: boolean
}

interface PlaygroundSidebarProps {
  selectedColor: ColorToken | null
  isOpen: boolean
  onToggle: () => void
}

export function PlaygroundSidebar({ selectedColor, isOpen: _isOpen, onToggle: _onToggle }: PlaygroundSidebarProps) {
  void _isOpen; // Reserved for future use
  void _onToggle; // Reserved for future use
  const [activeTab, setActiveTab] = useState<'harmony' | 'accessibility' | 'picker' | 'variants'>('harmony')
  const [customBgColor, setCustomBgColor] = useState('#ffffff')

  if (!selectedColor) {
    return (
      <div className={`playground-sidebar empty`}>
        <div className="empty-message">
          <p>Select a color to explore</p>
        </div>
      </div>
    )
  }

  // Calculate contrast ratio for custom bg
  const hexToRgb = (hex: string) => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
    if (!result) return { r: 255, g: 255, b: 255 }
    return {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16),
    }
  }

  const getLuminance = (rgb: { r: number; g: number; b: number }) => {
    const [r, g, b] = [rgb.r / 255, rgb.g / 255, rgb.b / 255].map((val) =>
      val <= 0.03928 ? val / 12.92 : Math.pow((val + 0.055) / 1.055, 2.4)
    )
    return 0.2126 * r + 0.7152 * g + 0.0722 * b
  }

  const getContrastRatio = (color1: string, color2: string) => {
    const l1 = getLuminance(hexToRgb(color1))
    const l2 = getLuminance(hexToRgb(color2))
    const lighter = Math.max(l1, l2)
    const darker = Math.min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)
  }

  const contrastRatio = getContrastRatio(selectedColor.hex, customBgColor)
  const isAACompliant = contrastRatio >= 4.5
  const isAAACompliant = contrastRatio >= 7

  return (
    <div className={`playground-sidebar`}>
      <div className="sidebar-content">
          {/* Tabs */}
          <div className="tab-buttons">
            <button
              className={`tab-btn ${activeTab === 'harmony' ? 'active' : ''}`}
              onClick={() => setActiveTab('harmony')}
              title="Harmony relationships"
            >
              🌈
            </button>
            <button
              className={`tab-btn ${activeTab === 'accessibility' ? 'active' : ''}`}
              onClick={() => setActiveTab('accessibility')}
              title="WCAG accessibility"
            >
              ♿
            </button>
            <button
              className={`tab-btn ${activeTab === 'picker' ? 'active' : ''}`}
              onClick={() => setActiveTab('picker')}
              title="Color picker"
            >
              🎨
            </button>
            <button
              className={`tab-btn ${activeTab === 'variants' ? 'active' : ''}`}
              onClick={() => setActiveTab('variants')}
              title="Generate variants"
            >
              ✨
            </button>
          </div>

          {/* Tab Content */}
          <div className="tab-content">
            {/* Harmony Tab */}
            {activeTab === 'harmony' && (
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
            )}

            {/* Accessibility Tab */}
            {activeTab === 'accessibility' && (
              <div className="accessibility-content">
                <h4>WCAG Accessibility</h4>

                {/* Static Contrast */}
                <div className="contrast-section">
                  <div className="contrast-item">
                    <span className="label">On White:</span>
                    <div className="contrast-value">
                      {selectedColor.wcag_contrast_on_white?.toFixed(2) || 'N/A'}:1
                    </div>
                    {selectedColor.wcag_aa_compliant_text && (
                      <span className="badge aa">AA ✓</span>
                    )}
                    {selectedColor.wcag_aaa_compliant_text && (
                      <span className="badge aaa">AAA ✓</span>
                    )}
                  </div>
                </div>

                {/* Custom Background */}
                <div className="custom-bg-section">
                  <label>Test on background:</label>
                  <input
                    type="color"
                    value={customBgColor}
                    onChange={(e) => setCustomBgColor(e.target.value)}
                    className="color-input"
                  />
                  <div className="preview" style={{ backgroundColor: customBgColor }}>
                    <span style={{ color: selectedColor.hex }}>Sample Text</span>
                  </div>
                  <div className="custom-contrast">
                    <span>Contrast: {contrastRatio.toFixed(2)}:1</span>
                    {isAAACompliant && <span className="badge aaa">AAA ✓</span>}
                    {isAACompliant && !isAAACompliant && <span className="badge aa">AA ✓</span>}
                    {!isAACompliant && <span className="badge fail">⚠️ Low</span>}
                  </div>
                </div>

                {/* Info */}
                <div className="a11y-info">
                  <p>
                    <strong>AA:</strong> Normal text needs 4.5:1 contrast
                  </p>
                  <p>
                    <strong>AAA:</strong> Enhanced contrast needs 7:1
                  </p>
                </div>
              </div>
            )}

            {/* Picker Tab */}
            {activeTab === 'picker' && (
              <div className="picker-content">
                <h4>Color Sampler</h4>
                <p className="picker-info">Build custom palettes by sampling colors from your image.</p>
                <div className="picker-tools">
                  <button className="tool-btn">📌 Pin this color</button>
                  <button className="tool-btn">🎯 Find similar</button>
                  <button className="tool-btn">🔄 Get complementary</button>
                </div>
                <div className="pinned-colors">
                  <h5>Pinned</h5>
                  <div className="pinned-list">
                    <div className="pinned-item" style={{ backgroundColor: selectedColor.hex }} />
                  </div>
                </div>
              </div>
            )}

            {/* Variants Tab */}
            {activeTab === 'variants' && (
              <div className="variants-content">
                <h4>Generate Variants</h4>
                <p className="variants-info">Create tints, shades, and tones of this color for design systems.</p>

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
            )}
          </div>
      </div>
    </div>
  )
}

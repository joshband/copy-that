import React, { useState } from 'react'
import './AccessibilityVisualizer.css'

interface AccessibilityVisualizerProps {
  hex: string
  wcagContrastWhite?: number
  wcagContrastBlack?: number
  wcagAACompliantText?: boolean
  wcagAAACompliantText?: boolean
  wcagAACompliantNormal?: boolean
  wcagAAACompliantNormal?: boolean
  colorblindSafe?: boolean
}

export function AccessibilityVisualizer({
  hex,
  wcagContrastWhite,
  wcagContrastBlack,
  wcagAACompliantText,
  wcagAAACompliantText,
  wcagAACompliantNormal,
  wcagAAACompliantNormal,
  colorblindSafe
}: AccessibilityVisualizerProps) {
  const [activeTab, setActiveTab] = useState<'white' | 'black' | 'custom'>('white')
  const [customBackground, setCustomBackground] = useState('#ffffff')

  const parseHex = (hex: string): { r: number; g: number; b: number } => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
    return result
      ? {
          r: parseInt(result[1], 16),
          g: parseInt(result[2], 16),
          b: parseInt(result[3], 16)
        }
      : { r: 0, g: 0, b: 0 }
  }

  const getLuminance = (color: string): number => {
    const { r, g, b } = parseHex(color)
    const [rs, gs, bs] = [r, g, b].map((x) => {
      x = x / 255
      return x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4)
    })
    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs
  }

  const calculateContrast = (color1: string, color2: string): number => {
    const lum1 = getLuminance(color1)
    const lum2 = getLuminance(color2)
    const lighter = Math.max(lum1, lum2)
    const darker = Math.min(lum1, lum2)
    return (lighter + 0.05) / (darker + 0.05)
  }

  const customContrast = calculateContrast(hex, customBackground)

  // Helper functions kept for future use
  const _wcagLevelText = (ratio: number): string => {
    if (ratio >= 7) return 'AAA'
    if (ratio >= 4.5) return 'AA'
    return 'Fail'
  }

  const _wcagLevelNormal = (ratio: number): string => {
    if (ratio >= 4.5) return 'AAA'
    if (ratio >= 3) return 'AA'
    return 'Fail'
  }

  // Suppress unused variable warnings for helper functions
  void _wcagLevelText
  void _wcagLevelNormal

  return (
    <div className="accessibility-visualizer">
      <div className="accessibility-header">
        <h3>♿ Accessibility & Contrast</h3>
        <p className="subtitle">
          Explore how this color works across different backgrounds. WCAG guidelines ensure your design is readable for
          everyone, including people with vision impairments.
        </p>
      </div>

      <div className="contrast-tabs">
        <button
          className={`tab ${activeTab === 'white' ? 'active' : ''}`}
          onClick={() => setActiveTab('white')}
        >
          On White
        </button>
        <button
          className={`tab ${activeTab === 'black' ? 'active' : ''}`}
          onClick={() => setActiveTab('black')}
        >
          On Black
        </button>
        <button
          className={`tab ${activeTab === 'custom' ? 'active' : ''}`}
          onClick={() => setActiveTab('custom')}
        >
          Custom Background
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'white' && wcagContrastWhite != null && (
          <div className="contrast-panel">
            <div className="preview-area">
              <div style={{ backgroundColor: '#ffffff', padding: '40px', borderRadius: '8px', border: '2px solid #e2e8f0' }}>
                <p style={{ color: hex, margin: 0, fontSize: '18px', fontWeight: '500' }}>
                  This text is displayed on white
                </p>
                <p style={{ color: hex, margin: '8px 0 0 0', fontSize: '14px' }}>
                  The contrast ratio is {wcagContrastWhite.toFixed(2)}:1
                </p>
              </div>
            </div>

            <div className="wcag-info">
              <h4>White Background - Contrast Ratio: {wcagContrastWhite.toFixed(2)}:1</h4>

              <div className="wcag-standards">
                <div className={`standard ${wcagAACompliantText === true ? 'pass' : 'fail'}`}>
                  <span className="level">AA - Large Text</span>
                  <span className="ratio">{wcagAACompliantText === true ? '✓ Pass' : '✗ Fail'}</span>
                  <p className="description">For body text larger than 18pt (or 14pt bold). Recommended minimum for readability.</p>
                </div>

                <div className={`standard ${wcagAAACompliantText === true ? 'pass' : 'fail'}`}>
                  <span className="level">AAA - Large Text</span>
                  <span className="ratio">{wcagAAACompliantText === true ? '✓ Pass' : '✗ Fail'}</span>
                  <p className="description">Enhanced contrast for optimal readability. Recommended for critical content.</p>
                </div>

                <div className={`standard ${wcagAACompliantNormal === true ? 'pass' : 'fail'}`}>
                  <span className="level">AA - Normal Text</span>
                  <span className="ratio">{wcagAACompliantNormal === true ? '✓ Pass' : '✗ Fail'}</span>
                  <p className="description">For regular body text (14-18pt). The most common use case.</p>
                </div>

                <div className={`standard ${wcagAAACompliantNormal === true ? 'pass' : 'fail'}`}>
                  <span className="level">AAA - Normal Text</span>
                  <span className="ratio">{wcagAAACompliantNormal === true ? '✓ Pass' : '✗ Fail'}</span>
                  <p className="description">Enhanced contrast for normal-sized text. Ideal for accessibility.</p>
                </div>
              </div>

              <div className="wcag-explanation">
                <h5>What do these standards mean?</h5>
                <ul>
                  <li>
                    <strong>AA (4.5:1 for normal, 3:1 for large):</strong> Minimum legal requirement in many jurisdictions.
                    Meets WCAG 2.0 AA level.
                  </li>
                  <li>
                    <strong>AAA (7:1 for normal, 4.5:1 for large):</strong> Enhanced contrast. Recommended for maximum
                    accessibility.
                  </li>
                  <li>
                    <strong>Large text:</strong> 18pt+ or 14pt+ bold fonts. Less demanding requirements.
                  </li>
                </ul>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'black' && wcagContrastBlack != null && (
          <div className="contrast-panel">
            <div className="preview-area">
              <div style={{ backgroundColor: '#000000', padding: '40px', borderRadius: '8px', border: '2px solid #e2e8f0' }}>
                <p style={{ color: hex, margin: 0, fontSize: '18px', fontWeight: '500' }}>
                  This text is displayed on black
                </p>
                <p style={{ color: hex, margin: '8px 0 0 0', fontSize: '14px' }}>
                  The contrast ratio is {wcagContrastBlack.toFixed(2)}:1
                </p>
              </div>
            </div>

            <div className="wcag-info">
              <h4>Black Background - Contrast Ratio: {wcagContrastBlack.toFixed(2)}:1</h4>

              <div className="wcag-standards">
                <div className={`standard ${wcagAAACompliantNormal === true ? 'pass' : 'fail'}`}>
                  <span className="level">AA - Large Text</span>
                  <span className="ratio">{wcagAACompliantText === true ? '✓ Pass' : '✗ Fail'}</span>
                  <p className="description">Text larger than 18pt or 14pt bold.</p>
                </div>

                <div className={`standard ${wcagAAACompliantNormal === true ? 'pass' : 'fail'}`}>
                  <span className="level">AAA - Large Text</span>
                  <span className="ratio">{wcagAAACompliantText === true ? '✓ Pass' : '✗ Fail'}</span>
                  <p className="description">Enhanced accessibility for large text.</p>
                </div>

                <div className={`standard ${wcagAACompliantNormal === true ? 'pass' : 'fail'}`}>
                  <span className="level">AA - Normal Text</span>
                  <span className="ratio">{wcagAACompliantNormal === true ? '✓ Pass' : '✗ Fail'}</span>
                  <p className="description">Regular body text on dark backgrounds.</p>
                </div>

                <div className={`standard ${wcagAAACompliantNormal === true ? 'pass' : 'fail'}`}>
                  <span className="level">AAA - Normal Text</span>
                  <span className="ratio">{wcagAAACompliantNormal === true ? '✓ Pass' : '✗ Fail'}</span>
                  <p className="description">Maximum contrast on dark backgrounds.</p>
                </div>
              </div>

              <div className="wcag-explanation">
                <h5>Dark background considerations</h5>
                <ul>
                  <li>Dark backgrounds require lighter text for readability.</li>
                  <li>Light colors often achieve higher contrast on dark backgrounds.</li>
                  <li>Be mindful of eye strain—too much contrast can also be uncomfortable.</li>
                </ul>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'custom' && (
          <div className="contrast-panel">
            <div className="custom-input">
              <label htmlFor="bg-color">Choose a background color:</label>
              <input
                id="bg-color"
                type="color"
                value={customBackground}
                onChange={(e) => setCustomBackground(e.target.value)}
              />
              <span className="hex-display">{customBackground}</span>
            </div>

            <div className="preview-area">
              <div
                style={{
                  backgroundColor: customBackground,
                  padding: '40px',
                  borderRadius: '8px',
                  border: '2px solid #e2e8f0'
                }}
              >
                <p style={{ color: hex, margin: 0, fontSize: '18px', fontWeight: '500' }}>
                  Text on custom background
                </p>
                <p style={{ color: hex, margin: '8px 0 0 0', fontSize: '14px' }}>
                  Contrast ratio: {customContrast.toFixed(2)}:1
                </p>
              </div>
            </div>

            <div className="wcag-info">
              <h4>Custom Background - Contrast Ratio: {customContrast.toFixed(2)}:1</h4>

              <div className="wcag-standards">
                <div className={`standard ${customContrast >= 4.5 ? 'pass' : 'fail'}`}>
                  <span className="level">AA - Normal Text</span>
                  <span className="ratio">{customContrast >= 4.5 ? '✓ Pass' : '✗ Fail'}</span>
                  <p className="description">Minimum contrast for normal text (4.5:1)</p>
                </div>

                <div className={`standard ${customContrast >= 7 ? 'pass' : 'fail'}`}>
                  <span className="level">AAA - Normal Text</span>
                  <span className="ratio">{customContrast >= 7 ? '✓ Pass' : '✗ Fail'}</span>
                  <p className="description">Enhanced contrast for normal text (7:1)</p>
                </div>
              </div>

              <div className="wcag-explanation">
                <h5>Why contrast matters</h5>
                <ul>
                  <li>People with low vision, color blindness, and older users benefit from good contrast.</li>
                  <li>High contrast also improves readability on mobile devices and in bright environments.</li>
                  <li>A contrast ratio of 7:1 is considered excellent and is very accessible.</li>
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>

      {colorblindSafe === true && (
        <div className="colorblind-info">
          <p>
            <strong>✓ Colorblind Safe:</strong> This color can be distinguished by people with common color vision
            deficiencies (red-green or blue-yellow blindness). Good choice for accessibility.
          </p>
        </div>
      )}
    </div>
  )
}

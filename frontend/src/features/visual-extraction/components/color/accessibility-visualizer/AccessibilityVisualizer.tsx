import { useState } from 'react'
import '../AccessibilityVisualizer.css'
import { ContrastPanel } from './ContrastPanel'
import { CustomBackgroundTab } from './CustomBackgroundTab'
import type { TabType, AccessibilityVisualizerProps } from './types'

export function AccessibilityVisualizer({
  hex,
  wcagContrastWhite,
  wcagContrastBlack,
  wcagAACompliantText,
  wcagAAACompliantText,
  wcagAACompliantNormal,
  wcagAAACompliantNormal,
  colorblindSafe,
}: AccessibilityVisualizerProps) {
  const [activeTab, setActiveTab] = useState<TabType>('white')
  const [customBackground, setCustomBackground] = useState('#ffffff')

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
          <ContrastPanel
            hex={hex}
            backgroundColor="#ffffff"
            contrast={wcagContrastWhite}
            wcagLevels={{
              aaText: wcagAACompliantText === true,
              aaaText: wcagAAACompliantText === true,
              aaNormal: wcagAACompliantNormal === true,
              aaaNormal: wcagAAACompliantNormal === true,
            }}
            title="White Background"
          />
        )}

        {activeTab === 'black' && wcagContrastBlack != null && (
          <ContrastPanel
            hex={hex}
            backgroundColor="#000000"
            contrast={wcagContrastBlack}
            wcagLevels={{
              aaText: wcagAACompliantText === true,
              aaaText: wcagAAACompliantText === true,
              aaNormal: wcagAACompliantNormal === true,
              aaaNormal: wcagAAACompliantNormal === true,
            }}
            title="Black Background"
            isDarkBg
          />
        )}

        {activeTab === 'custom' && (
          <CustomBackgroundTab
            hex={hex}
            customBackground={customBackground}
            onCustomBackgroundChange={setCustomBackground}
          />
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

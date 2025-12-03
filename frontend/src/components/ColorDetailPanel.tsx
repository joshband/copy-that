import './ColorDetailPanel.css'
import { HarmonyVisualizer } from './HarmonyVisualizer'
import { AccessibilityVisualizer } from './AccessibilityVisualizer'
import { useState } from 'react'
import { ColorToken } from '../types'
import { copyToClipboard } from '../utils'
import { formatSemanticValue } from '../utils/semanticNames'

interface Props {
  color: ColorToken | null
  debugOverlay?: string
  isAlias?: boolean
  aliasTargetId?: string
}

type TabType = 'overview' | 'harmony' | 'accessibility' | 'properties' | 'diagnostics'

export function ColorDetailPanel({ color, debugOverlay, isAlias, aliasTargetId }: Props) {
  const [activeTab, setActiveTab] = useState<TabType>('overview')

  if (!color) {
    return (
      <div className="detail-panel empty">
        <div className="empty-state">
          <div className="empty-icon">🎨</div>
          <h3>Select a color to explore</h3>
          <p>Click on any color from the palette to view its properties</p>
        </div>
      </div>
    )
  }

  const featureNotes: string[] = []
  if (color.background_role) {
    featureNotes.push(`${color.background_role} background`)
  }
  if (color.contrast_category && color.contrast_category !== 'background') {
    featureNotes.push(`Contrast tagging (${color.contrast_category})`)
  }
  if (color.count != null && color.count > 1) {
    featureNotes.push(`OKLCH merged (${color.count} hits)`)
  }

  return (
    <div className="detail-panel">
      {/* Header */}
      <div className="detail-header">
        <div className="header-top">
          <div className="color-display">
            <div
              className="color-swatch-large"
              style={{ backgroundColor: color.hex }}
            />
            <div className="header-info">
              <h2 className="color-name">{color.name}</h2>
              {featureNotes.length > 0 && (
                <div className="feature-note">
                  <span className="feature-note-title">New features</span>
                  <div className="feature-note-items">
                    {featureNotes.map((item) => (
                      <span key={item} className="feature-tag">
                        {item}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              <div className="badge-row">
                {isAlias && aliasTargetId && (
                  <span className="alias-badge">
                    Alias of <code>{aliasTargetId}</code>
                  </span>
                )}
                {color.background_role && (
                  <span className={`background-badge ${color.background_role}`}>
                    {color.background_role} background
                  </span>
                )}
                {color.contrast_category && color.contrast_category !== 'background' && (
                  <span className={`contrast-badge ${color.contrast_category}`}>
                    Contrast: {color.contrast_category}
                  </span>
                )}
                {color.count != null && color.count > 1 && (
                  <span className="merge-badge">OKLCH merged</span>
                )}
              </div>
              <code
                className="hex-clickable"
                onClick={() => void copyToClipboard(color.hex)}
                title="Click to copy"
              >
                {color.hex}
              </code>
              <span className="confidence-badge">
                {Math.round(color.confidence * 100)}% confidence
              </span>
            </div>
          </div>
          {color.count != null && color.count > 1 && (
            <div className="count-info">
              <span className="count-value">{color.count}x</span>
              <span className="count-label">in image</span>
            </div>
          )}
        </div>

        {/* Quick Color Codes */}
        <div className="quick-codes">
          <div
            className="code-item"
            onClick={() => void copyToClipboard(color.rgb)}
            title="Click to copy"
          >
            <span className="code-label">RGB</span>
            <code>{color.rgb}</code>
          </div>
          {color.hsl != null && color.hsl !== '' && (
            <div
              className="code-item"
              onClick={() => void copyToClipboard(color.hsl ?? '')}
              title="Click to copy"
            >
              <span className="code-label">HSL</span>
              <code>{color.hsl}</code>
            </div>
          )}
          {color.closest_css_named != null && color.closest_css_named !== '' && (
            <div
              className="code-item"
              onClick={() => void copyToClipboard(color.closest_css_named ?? '')}
              title="Click to copy"
            >
              <span className="code-label">CSS</span>
              <code>{color.closest_css_named}</code>
            </div>
          )}
          {color.foreground_role && (
            <div className="code-item">
              <span className="code-label">Text Role</span>
              <code>{color.foreground_role}</code>
            </div>
          )}
          {color.background_role && (
            <div className="code-item">
              <span className="code-label">Background</span>
              <code>{color.background_role}</code>
            </div>
          )}
          {(color as any)?.extraction_metadata?.accent && (
            <div className="code-item">
              <span className="code-label">Accent</span>
              <code>accent</code>
            </div>
          )}
          {(color as any)?.extraction_metadata?.state_role && (
            <div className="code-item">
              <span className="code-label">State</span>
              <code>{(color as any).extraction_metadata.state_role}</code>
            </div>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs">
        <button
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        {color.harmony != null && color.harmony !== '' && (
          <button
            className={`tab ${activeTab === 'harmony' ? 'active' : ''}`}
            onClick={() => setActiveTab('harmony')}
          >
            Harmony
          </button>
        )}
        <button
          className={`tab ${activeTab === 'accessibility' ? 'active' : ''}`}
          onClick={() => setActiveTab('accessibility')}
        >
          Accessibility
        </button>
        <button
          className={`tab ${activeTab === 'properties' ? 'active' : ''}`}
          onClick={() => setActiveTab('properties')}
        >
          Properties
        </button>
        {debugOverlay && (
          <button
            className={`tab ${activeTab === 'diagnostics' ? 'active' : ''}`}
            onClick={() => setActiveTab('diagnostics')}
          >
            Diagnostics
          </button>
        )}
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'overview' && <OverviewTab color={color} />}
        {activeTab === 'harmony' && color.harmony != null && color.harmony !== '' && (
          <HarmonyTab color={color} />
        )}
        {activeTab === 'accessibility' && (
          <AccessibilityTab color={color} />
        )}
        {activeTab === 'properties' && <PropertiesTab color={color} />}
        {activeTab === 'diagnostics' && debugOverlay && (
          <DiagnosticsTab overlay={debugOverlay} />
        )}
      </div>
    </div>
  )
}

function OverviewTab({ color }: { color: ColorToken }) {
  return (
    <div className="overview-content">
      <section className="overview-section">
        <h3>Color Identity</h3>
        <div className="info-grid">
          {color.design_intent != null && color.design_intent !== '' && (
            <div className="info-item">
              <label>Design Intent</label>
              <span>{color.design_intent}</span>
            </div>
          )}
          {color.category != null && color.category !== '' && (
            <div className="info-item">
              <label>Category</label>
              <span>{color.category}</span>
            </div>
          )}
          {color.temperature != null && color.temperature !== '' && (
            <div className="info-item">
              <label>Temperature</label>
              <span className="temp-badge" data-temp={color.temperature}>
                {color.temperature}
              </span>
            </div>
          )}
          {color.is_neutral === true && (
            <div className="info-item">
              <label>Neutral</label>
              <span>✓ Yes</span>
            </div>
          )}
        </div>
      </section>

      {(() => {
        const entries =
          typeof color.semantic_names === 'string'
            ? [['label', color.semantic_names] as const]
            : color.semantic_names
              ? Object.entries(color.semantic_names)
              : []

        return entries.length > 0 ? (
          <section className="overview-section">
            <h3>Semantic Names</h3>
            <div className="semantic-grid">
              {(entries as any).map(([key, value]: [string, any]) => {
                const formatted = formatSemanticValue(value)
                return (
                  <div key={key} className="semantic-item">
                    <span className="semantic-key">{key}</span>
                    <span className="semantic-value">{formatted}</span>
                  </div>
                )
              })}
            </div>
          </section>
        ) : null
      })()}

      {color.prominence_percentage != null && (
        <section className="overview-section">
          <h3>Prominence</h3>
          <div className="prominence-bar">
            <div
              className="prominence-fill"
              style={{ width: `${color.prominence_percentage}%` }}
            />
          </div>
          <span className="prominence-value">
            {color.prominence_percentage?.toFixed(1)}% of image
          </span>
        </section>
      )}
      {color.extraction_metadata && (
        <section className="overview-section">
          <h3>Source & Model</h3>
          <div className="info-grid">
            {color.extraction_metadata.model && (
              <div className="info-item">
                <label>Model</label>
                <span>{String(color.extraction_metadata.model)}</span>
              </div>
            )}
            {color.extraction_metadata.extractor && (
              <div className="info-item">
                <label>Extractor</label>
                <span>{String(color.extraction_metadata.extractor)}</span>
              </div>
            )}
            {color.extraction_metadata.source && (
              <div className="info-item">
                <label>Source</label>
                <span>{String(color.extraction_metadata.source)}</span>
              </div>
            )}
            {color.histogram_significance != null && (
              <div className="info-item">
                <label>Histogram Significance</label>
                <span>{(color.histogram_significance * 100).toFixed(2)}%</span>
              </div>
            )}
          </div>
        </section>
      )}
    </div>
  )
}

function HarmonyTab({ color }: { color: ColorToken }) {
  return (
    <div className="harmony-content">
      <HarmonyVisualizer harmony={color.harmony ?? ''} hex={color.hex} />
    </div>
  )
}

function AccessibilityTab({ color }: { color: ColorToken }) {
  return (
    <div className="accessibility-content">
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
    </div>
  )
}

function PropertiesTab({ color }: { color: ColorToken }) {
  return (
    <div className="properties-content">
      <section className="props-section">
        <h3>Color Attributes</h3>
        <div className="properties-grid">
          {color.saturation_level != null && color.saturation_level !== '' && (
            <div className="prop-item">
              <label>Saturation</label>
              <span>{color.saturation_level}</span>
            </div>
          )}
          {color.lightness_level != null && color.lightness_level !== '' && (
            <div className="prop-item">
              <label>Lightness</label>
              <span>{color.lightness_level}</span>
            </div>
          )}
          {color.closest_web_safe != null && color.closest_web_safe !== '' && (
            <div className="prop-item">
              <label>Web Safe</label>
              <code
                onClick={() => void copyToClipboard(color.closest_web_safe ?? '')}
                title="Click to copy"
              >
                {color.closest_web_safe}
              </code>
            </div>
          )}
          {color.delta_e_to_dominant != null && (
            <div className="prop-item">
              <label>ΔE (to dominant)</label>
              <span>{color.delta_e_to_dominant?.toFixed(2)}</span>
            </div>
          )}
        </div>
      </section>

      {(color.tint_color != null || color.shade_color != null || color.tone_color != null) && (
        <section className="props-section">
          <h3>Variants</h3>
          <div className="variants-grid">
            {color.tint_color != null && color.tint_color !== '' && (
              <div className="variant-item">
                <div
                  className="variant-swatch"
                  style={{ backgroundColor: color.tint_color }}
                  onClick={() => void copyToClipboard(color.tint_color ?? '')}
                  title="Click to copy"
                />
                <code>{color.tint_color}</code>
                <span className="variant-label">Tint</span>
              </div>
            )}
            {color.shade_color != null && color.shade_color !== '' && (
              <div className="variant-item">
                <div
                  className="variant-swatch"
                  style={{ backgroundColor: color.shade_color }}
                  onClick={() => void copyToClipboard(color.shade_color ?? '')}
                  title="Click to copy"
                />
                <code>{color.shade_color}</code>
                <span className="variant-label">Shade</span>
              </div>
            )}
            {color.tone_color != null && color.tone_color !== '' && (
              <div className="variant-item">
                <div
                  className="variant-swatch"
                  style={{ backgroundColor: color.tone_color }}
                  onClick={() => void copyToClipboard(color.tone_color ?? '')}
                  title="Click to copy"
                />
                <code>{color.tone_color}</code>
                <span className="variant-label">Tone</span>
              </div>
            )}
          </div>
        </section>
      )}
    </div>
  )
}

function DiagnosticsTab({ overlay }: { overlay: string }) {
  return (
    <div className="diagnostics-content">
      <p className="diagnostics-hint">
        Superpixel boundaries plus background/text picks for quick QA.
      </p>
      <div className="diagnostics-frame">
        <img
          src={`data:image/png;base64,${overlay}`}
          alt="Color extraction diagnostics overlay"
          className="diagnostics-image"
        />
      </div>
    </div>
  )
}

/**
 * ShadowAnalysisPanel Component
 * Phase 4: Advanced Analysis
 *
 * Main panel displaying comprehensive shadow analysis for the token viewer/playground
 */

import { useState, useCallback } from 'react'
import { LightingDirectionIndicator } from './LightingDirectionIndicator'
import { ShadowQualityMetrics } from './ShadowQualityMetrics'
import type {
  LightingAnalysisResponse,
  LightDirection,
  CSSBoxShadowSuggestions,
} from '../../types/shadowAnalysis'
import './ShadowAnalysisPanel.css'

export interface ShadowAnalysisPanelProps {
  /** Analysis data from API */
  analysis?: LightingAnalysisResponse | null
  /** Image being analyzed (for re-analysis) */
  imageBase64?: string
  /** Loading state */
  isLoading?: boolean
  /** Error message */
  error?: string | null
  /** Callback to request new analysis */
  onAnalyze?: (imageBase64: string) => Promise<void>
  /** Show CSS suggestions panel */
  showCSSSuggestions?: boolean
  /** Compact mode */
  compact?: boolean
}

interface CSSSuggestionCardProps {
  name: string
  value: string
  onCopy: () => void
}

function CSSSuggestionCard({ name, value, onCopy }: CSSSuggestionCardProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(`box-shadow: ${value};`)
    setCopied(true)
    onCopy()
    setTimeout(() => setCopied(false), 2000)
  }, [value, onCopy])

  return (
    <div className="css-suggestion-card">
      <div className="css-card-header">
        <span className="css-card-name">{name}</span>
        <button className="css-copy-btn" onClick={handleCopy} title="Copy CSS">
          {copied ? '&#10003;' : '&#128203;'}
        </button>
      </div>
      <div className="css-preview-box" style={{ boxShadow: value }}>
        <span>Preview</span>
      </div>
      <code className="css-code">box-shadow: {value};</code>
    </div>
  )
}

export function ShadowAnalysisPanel({
  analysis,
  imageBase64,
  isLoading = false,
  error = null,
  onAnalyze,
  showCSSSuggestions = true,
  compact = false,
}: ShadowAnalysisPanelProps) {
  const [activeTab, setActiveTab] = useState<'metrics' | 'css' | 'raw'>('metrics')
  const [copiedCSS, setCopiedCSS] = useState<string | null>(null)

  const handleReanalyze = useCallback(async () => {
    if (imageBase64 && onAnalyze) {
      await onAnalyze(imageBase64)
    }
  }, [imageBase64, onAnalyze])

  const handleCopyCSSNotification = useCallback(() => {
    setCopiedCSS('Copied!')
    setTimeout(() => setCopiedCSS(null), 2000)
  }, [])

  // Build light direction from analysis
  const lightDirection: LightDirection | null = analysis?.light_direction || null

  // Empty state
  if (!analysis && !isLoading && !error) {
    return (
      <div className={`shadow-analysis-panel empty ${compact ? 'compact' : ''}`}>
        <div className="empty-state">
          <div className="empty-icon">&#9728;</div>
          <h3>No Analysis Available</h3>
          <p>Upload an image to analyze shadow characteristics and lighting direction.</p>
          {imageBase64 && onAnalyze && (
            <button className="analyze-btn" onClick={handleReanalyze}>
              Analyze Image
            </button>
          )}
        </div>
      </div>
    )
  }

  // Loading state
  if (isLoading) {
    return (
      <div className={`shadow-analysis-panel loading ${compact ? 'compact' : ''}`}>
        <div className="loading-state">
          <div className="loading-spinner" />
          <p>Analyzing shadow characteristics...</p>
        </div>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className={`shadow-analysis-panel error ${compact ? 'compact' : ''}`}>
        <div className="error-state">
          <div className="error-icon">&#9888;</div>
          <h3>Analysis Failed</h3>
          <p>{error}</p>
          {imageBase64 && onAnalyze && (
            <button className="retry-btn" onClick={handleReanalyze}>
              Retry Analysis
            </button>
          )}
        </div>
      </div>
    )
  }

  if (!analysis) return null

  // Compact mode for sidebar/inline use
  if (compact) {
    return (
      <div className="shadow-analysis-panel compact">
        <div className="compact-header">
          <LightingDirectionIndicator
            direction={lightDirection}
            directionToken={analysis.style_key_direction}
            lightingStyle={analysis.lighting_style}
            confidence={analysis.light_direction_confidence}
            size="sm"
            showDetails={false}
          />
          <ShadowQualityMetrics
            shadowAreaFraction={analysis.shadow_area_fraction}
            shadowContrast={analysis.shadow_contrast}
            edgeSoftness={analysis.edge_softness_mean}
            confidence={analysis.extraction_confidence}
            compact={true}
          />
        </div>
      </div>
    )
  }

  return (
    <div className="shadow-analysis-panel">
      {/* Header */}
      <div className="panel-header">
        <h2>Shadow Analysis</h2>
        <div className="header-actions">
          {imageBase64 && onAnalyze && (
            <button className="reanalyze-btn" onClick={handleReanalyze} disabled={isLoading}>
              Re-analyze
            </button>
          )}
          {copiedCSS && <span className="copy-notification">{copiedCSS}</span>}
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="panel-tabs">
        <button
          className={`tab-btn ${activeTab === 'metrics' ? 'active' : ''}`}
          onClick={() => setActiveTab('metrics')}
        >
          Metrics
        </button>
        {showCSSSuggestions && (
          <button
            className={`tab-btn ${activeTab === 'css' ? 'active' : ''}`}
            onClick={() => setActiveTab('css')}
          >
            CSS Suggestions
          </button>
        )}
        <button
          className={`tab-btn ${activeTab === 'raw' ? 'active' : ''}`}
          onClick={() => setActiveTab('raw')}
        >
          Raw Data
        </button>
      </div>

      {/* Tab Content */}
      <div className="panel-content">
        {activeTab === 'metrics' && (
          <div className="metrics-tab">
            <div className="metrics-grid">
              {/* Lighting Direction */}
              <div className="metrics-section lighting">
                <h3>Lighting Direction</h3>
                <LightingDirectionIndicator
                  direction={lightDirection}
                  directionToken={analysis.style_key_direction}
                  lightingStyle={analysis.lighting_style}
                  confidence={analysis.light_direction_confidence}
                  size="lg"
                  showDetails={true}
                />
              </div>

              {/* Quality Metrics */}
              <div className="metrics-section quality">
                <h3>Quality Metrics</h3>
                <ShadowQualityMetrics
                  shadowAreaFraction={analysis.shadow_area_fraction}
                  meanShadowIntensity={analysis.mean_shadow_intensity}
                  meanLitIntensity={analysis.mean_lit_intensity}
                  shadowContrast={analysis.shadow_contrast}
                  edgeSoftness={analysis.edge_softness_mean}
                  shadowCount={analysis.shadow_count_major}
                  confidence={analysis.extraction_confidence}
                  tokens={{
                    softness: analysis.style_softness,
                    contrast: analysis.style_contrast,
                    density: analysis.style_density,
                    intensityShadow: analysis.intensity_shadow,
                    intensityLit: analysis.intensity_lit,
                  }}
                />
              </div>
            </div>
          </div>
        )}

        {activeTab === 'css' && showCSSSuggestions && analysis.css_box_shadow && (
          <div className="css-tab">
            <p className="css-intro">
              Based on the analyzed shadow characteristics, here are recommended CSS box-shadow
              values:
            </p>
            <div className="css-suggestions-grid">
              {Object.entries(analysis.css_box_shadow as CSSBoxShadowSuggestions).map(
                ([name, value]) => (
                  <CSSSuggestionCard
                    key={name}
                    name={name}
                    value={value}
                    onCopy={handleCopyCSSNotification}
                  />
                )
              )}
            </div>
          </div>
        )}

        {activeTab === 'raw' && (
          <div className="raw-tab">
            <pre className="raw-json">{JSON.stringify(analysis, null, 2)}</pre>
          </div>
        )}
      </div>

      {/* Footer with source info */}
      <div className="panel-footer">
        <span className="source-badge">Source: {analysis.analysis_source}</span>
        {analysis.image_id && <span className="image-id">Image: {analysis.image_id}</span>}
      </div>
    </div>
  )
}

export default ShadowAnalysisPanel

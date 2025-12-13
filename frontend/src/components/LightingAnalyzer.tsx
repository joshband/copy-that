/**
 * Lighting Analysis Component
 * Analyzes image lighting, shadow characteristics, and geometric properties
 */

import { useState, useEffect, useCallback } from 'react'
import { API_BASE } from '../api/client'
import './LightingAnalyzer.css'

interface LightingAnalysis {
  style_key_direction: string
  style_softness: string
  style_contrast: string
  style_density: string
  intensity_shadow: string
  intensity_lit: string
  lighting_style: string
  shadow_area_fraction: number
  mean_shadow_intensity: number
  mean_lit_intensity: number
  shadow_contrast: number
  edge_softness_mean: number
  light_direction_confidence: number
  extraction_confidence: number
  shadow_count_major: number
  css_box_shadow: Record<string, string>
  image_id?: string
}

interface LightingAnalyzerProps {
  imageBase64?: string
  imageUrl?: string
  onAnalysisComplete?: (analysis: LightingAnalysis) => void
}

export default function LightingAnalyzer({
  imageBase64,
  imageUrl,
  onAnalysisComplete
}: LightingAnalyzerProps) {
  const [analysis, setAnalysis] = useState<LightingAnalysis | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const analyzeImage = useCallback(async () => {
    if (!imageBase64 && !imageUrl) {
      setError('No image provided')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`${API_BASE}/lighting/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          image_base64: imageBase64,
          image_url: imageUrl,
          use_geometry: true,
          device: 'cpu'
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Analysis failed')
      }

      const result = await response.json()
      setAnalysis(result)
      onAnalysisComplete?.(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }, [imageBase64, imageUrl])

  // Auto-analyze when image is provided
  useEffect(() => {
    if ((imageBase64 || imageUrl) && !analysis && !loading) {
      analyzeImage()
    }
  }, [imageBase64, imageUrl, analysis, loading, analyzeImage])

  if (!analysis) {
    return (
      <div className="lighting-analyzer">
        <button
          onClick={() => void analyzeImage()}
          disabled={loading || (!imageBase64 && !imageUrl)}
          className="analyze-button"
        >
          {loading ? 'Analyzing...' : 'Analyze Lighting'}
        </button>
        {error && <div className="error-message">{error}</div>}
      </div>
    )
  }

  return (
    <div className="lighting-analysis">
      <div className="analysis-grid">
        {/* Style Cards */}
        <div className="token-card">
          <div className="token-label">Light Direction</div>
          <div className="token-value">{analysis.style_key_direction}</div>
          <div className="confidence">Confidence: {Math.round(analysis.light_direction_confidence * 100)}%</div>
        </div>

        <div className="token-card">
          <div className="token-label">Edge Softness</div>
          <div className="token-value">{analysis.style_softness}</div>
          <div className="numeric-value">{(analysis.edge_softness_mean * 100).toFixed(0)}%</div>
        </div>

        <div className="token-card">
          <div className="token-label">Shadow Contrast</div>
          <div className="token-value">{analysis.style_contrast}</div>
          <div className="numeric-value">{(analysis.shadow_contrast * 100).toFixed(0)}%</div>
        </div>

        <div className="token-card">
          <div className="token-label">Shadow Density</div>
          <div className="token-value">{analysis.style_density}</div>
          <div className="numeric-value">{(analysis.shadow_area_fraction * 100).toFixed(1)}% coverage</div>
        </div>

        <div className="token-card">
          <div className="token-label">Shadow Intensity</div>
          <div className="token-value">{analysis.intensity_shadow}</div>
          <div className="numeric-value">{(analysis.mean_shadow_intensity * 100).toFixed(0)}% brightness</div>
        </div>

        <div className="token-card">
          <div className="token-label">Lit Intensity</div>
          <div className="token-value">{analysis.intensity_lit}</div>
          <div className="numeric-value">{(analysis.mean_lit_intensity * 100).toFixed(0)}% brightness</div>
        </div>

        <div className="token-card">
          <div className="token-label">Lighting Style</div>
          <div className="token-value">{analysis.lighting_style}</div>
          <div className="confidence">Overall: {Math.round(analysis.extraction_confidence * 100)}%</div>
        </div>

        <div className="token-card">
          <div className="token-label">Shadow Regions</div>
          <div className="token-value">{analysis.shadow_count_major}</div>
          <div className="numeric-value">major regions detected</div>
        </div>
      </div>

      {/* CSS Suggestions */}
      <div className="css-suggestions">
        <h3>CSS Box-Shadow Suggestions</h3>
        <div className="css-preview">
          <div className="preview-box" style={{ boxShadow: analysis.css_box_shadow.subtle }}>
            <div className="preview-label">Subtle</div>
          </div>
          <div className="preview-box" style={{ boxShadow: analysis.css_box_shadow.medium }}>
            <div className="preview-label">Medium</div>
          </div>
          <div className="preview-box" style={{ boxShadow: analysis.css_box_shadow.strong }}>
            <div className="preview-label">Strong</div>
          </div>
        </div>
        <div className="css-code">
          <code>box-shadow: {analysis.css_box_shadow.medium};</code>
        </div>
      </div>

      {/* Metrics */}
      <div className="metrics">
        <h3>Numeric Metrics</h3>
        <div className="metrics-grid">
          <div className="metric">
            <span className="metric-name">Shadow Area</span>
            <span className="metric-value">{(analysis.shadow_area_fraction * 100).toFixed(1)}%</span>
          </div>
          <div className="metric">
            <span className="metric-name">Mean Shadow</span>
            <span className="metric-value">{(analysis.mean_shadow_intensity * 100).toFixed(0)}%</span>
          </div>
          <div className="metric">
            <span className="metric-name">Mean Lit</span>
            <span className="metric-value">{(analysis.mean_lit_intensity * 100).toFixed(0)}%</span>
          </div>
          <div className="metric">
            <span className="metric-name">Edge Softness</span>
            <span className="metric-value">{(analysis.edge_softness_mean * 100).toFixed(0)}%</span>
          </div>
        </div>
      </div>

      <button
        onClick={() => void analyzeImage()}
        className="re-analyze-button"
      >
        Re-analyze
      </button>
    </div>
  )
}

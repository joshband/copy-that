import React from 'react'
import { useTokenGraphStore } from '../store/tokenGraphStore'

interface TypographyTokenDetail {
  id: string
  fontFamily?: string
  fontSize?: string
  fontWeight?: number | string
  lineHeight?: number | string
  letterSpacing?: string
  textTransform?: string
  category?: string
  semanticRole?: string
  confidence?: number
  readabilityScore?: number
  isReadable?: boolean
  prominence?: number
  colorTemp?: string
  visualWeight?: string
  contrastLevel?: string
  primaryStyle?: string
  vlmMood?: string
  vlmComplexity?: string
  usage?: string[]
  extractionMetadata?: Record<string, any>
  raw?: any
}

/**
 * Enhanced Typography Detail Cards
 * Displays all typography metrics organized by category
 */
export default function TypographyDetailCard() {
  const typography = useTokenGraphStore((s: any) => s.typography)
  const recommendation = useTokenGraphStore((s: any) => s.typographyRecommendation)

  const tokens: TypographyTokenDetail[] = typography
    .map((t: any) => {
      const val = t.raw?.$value || {}
      const fontFamily = Array.isArray(val.fontFamily) ? val.fontFamily[0] : val.fontFamily
      const fontSize =
        val.fontSize && typeof val.fontSize === 'object' && 'value' in val.fontSize
          ? `${val.fontSize.value}${val.fontSize.unit || 'px'}`
          : val.fontSize
      const lineHeight =
        val.lineHeight && typeof val.lineHeight === 'object' && 'value' in val.lineHeight
          ? `${val.lineHeight.value}${val.lineHeight.unit || ''}`
          : val.lineHeight
      const letterSpacing =
        val.letterSpacing && typeof val.letterSpacing === 'object' && 'value' in val.letterSpacing
          ? `${val.letterSpacing.value}${val.letterSpacing.unit || 'px'}`
          : val.letterSpacing

      return {
        id: t.id,
        fontFamily: typeof fontFamily === 'string' ? fontFamily : undefined,
        fontSize: typeof fontSize === 'string' ? fontSize : undefined,
        fontWeight: val.fontWeight,
        lineHeight: typeof lineHeight === 'string' ? lineHeight : undefined,
        letterSpacing: typeof letterSpacing === 'string' ? letterSpacing : undefined,
        textTransform: val.casing,
        category: t.category,
        semanticRole: t.semantic_role,
        confidence: t.confidence,
        readabilityScore: t.readability_score,
        isReadable: t.is_readable,
        prominence: t.prominence_percentage,
        colorTemp: recommendation?.styleAttributes?.color_temperature,
        visualWeight: recommendation?.styleAttributes?.visual_weight,
        contrastLevel: recommendation?.styleAttributes?.contrast_level,
        primaryStyle: recommendation?.styleAttributes?.primary_style,
        vlmMood: recommendation?.styleAttributes?.vlm_mood,
        vlmComplexity: recommendation?.styleAttributes?.vlm_complexity,
        usage: t.usage ? (typeof t.usage === 'string' ? JSON.parse(t.usage) : t.usage) : [],
        extractionMetadata: t.extraction_metadata,
        raw: t,
      }
    })

  if (!tokens.length) {
    return null
  }

  return (
    <div className="typo-detail-cards">
      <div className="typo-detail-title">Typography Details & Metrics</div>
      <div className="typo-detail-grid">
        {tokens.map((token) => (
          <div key={token.id} className="typo-detail-card">
            {/* Header */}
            <div className="typo-detail-header">
              <div className="typo-detail-name">{token.id}</div>
              {token.semanticRole && <div className="typo-detail-role">{token.semanticRole}</div>}
            </div>

            {/* Core Typography Properties */}
            <div className="typo-section">
              <div className="typo-section-title">Typography</div>
              <div className="typo-section-content">
                {token.fontFamily && (
                  <div className="typo-row">
                    <span className="label">Font</span>
                    <span className="value mono">{token.fontFamily}</span>
                  </div>
                )}
                {token.fontSize && (
                  <div className="typo-row">
                    <span className="label">Size</span>
                    <span className="value mono">{token.fontSize}</span>
                  </div>
                )}
                {token.fontWeight && (
                  <div className="typo-row">
                    <span className="label">Weight</span>
                    <span className="value mono">{token.fontWeight}</span>
                  </div>
                )}
                {token.lineHeight && (
                  <div className="typo-row">
                    <span className="label">Line Height</span>
                    <span className="value mono">{token.lineHeight}</span>
                  </div>
                )}
                {token.letterSpacing && (
                  <div className="typo-row">
                    <span className="label">Letter Spacing</span>
                    <span className="value mono">{token.letterSpacing}</span>
                  </div>
                )}
                {token.textTransform && (
                  <div className="typo-row">
                    <span className="label">Transform</span>
                    <span className="badge badge-typo-property">{token.textTransform}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Quality & Readability */}
            {(token.confidence != null ||
              token.readabilityScore != null ||
              token.isReadable != null ||
              token.prominence != null) && (
              <div className="typo-section">
                <div className="typo-section-title">Quality</div>
                <div className="typo-section-content">
                  {token.confidence != null && (
                    <div className="typo-row">
                      <span className="label">Confidence</span>
                      <div className="typo-confidence-badge" style={{ '--typo-confidence': token.confidence } as React.CSSProperties}>
                        {Math.round(token.confidence * 100)}%
                      </div>
                    </div>
                  )}
                  {token.readabilityScore != null && (
                    <div className="typo-row">
                      <span className="label">Readability</span>
                      <div className="typo-readability-badge" style={{ '--typo-readability': token.readabilityScore } as React.CSSProperties}>
                        {Math.round(token.readabilityScore * 100)}%
                      </div>
                    </div>
                  )}
                  {token.isReadable != null && (
                    <div className="typo-row">
                      <span className="label">Legible</span>
                      <span className={`badge ${token.isReadable ? 'badge-success' : 'badge-warning'}`}>
                        {token.isReadable ? '✓ Yes' : '⚠ Poor'}
                      </span>
                    </div>
                  )}
                  {token.prominence != null && (
                    <div className="typo-row">
                      <span className="label">Prominence</span>
                      <span className="value">{token.prominence.toFixed(1)}%</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Style Attributes */}
            {(token.primaryStyle || token.colorTemp || token.visualWeight || token.contrastLevel || token.vlmMood) && (
              <div className="typo-section">
                <div className="typo-section-title">Style</div>
                <div className="typo-section-content">
                  {token.primaryStyle && (
                    <div className="typo-row">
                      <span className="label">Primary</span>
                      <span className="badge badge-style">{token.primaryStyle}</span>
                    </div>
                  )}
                  {token.colorTemp && (
                    <div className="typo-row">
                      <span className="label">Temperature</span>
                      <span className="badge badge-temp">{token.colorTemp}</span>
                    </div>
                  )}
                  {token.visualWeight && (
                    <div className="typo-row">
                      <span className="label">Weight</span>
                      <span className="badge badge-weight">{token.visualWeight}</span>
                    </div>
                  )}
                  {token.contrastLevel && (
                    <div className="typo-row">
                      <span className="label">Contrast</span>
                      <span className="badge badge-contrast">{token.contrastLevel}</span>
                    </div>
                  )}
                  {token.vlmMood && (
                    <div className="typo-row">
                      <span className="label">Mood</span>
                      <span className="badge badge-mood">{token.vlmMood}</span>
                    </div>
                  )}
                  {token.vlmComplexity && (
                    <div className="typo-row">
                      <span className="label">Complexity</span>
                      <span className="badge badge-complexity">{token.vlmComplexity}</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Usage Contexts */}
            {token.usage && token.usage.length > 0 && (
              <div className="typo-section">
                <div className="typo-section-title">Usage</div>
                <div className="typo-usage-tags">
                  {token.usage.slice(0, 4).map((u, i) => (
                    <span key={i} className="typo-tag">
                      {u}
                    </span>
                  ))}
                  {token.usage.length > 4 && <span className="typo-tag">+{token.usage.length - 4}</span>}
                </div>
              </div>
            )}

            {/* Category */}
            {token.category && (
              <div className="typo-section">
                <div className="typo-section-title">Category</div>
                <div className="typo-section-content">
                  <span className="badge badge-category">{token.category}</span>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

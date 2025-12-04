import React from 'react'
import { useTokenGraphStore } from '../store/tokenGraphStore'

interface SpacingTokenDetail {
  id: string
  px: number
  rem: number
  confidence?: number
  semantic_role?: string
  spacing_type?: string
  grid_aligned?: boolean
  tailwind_class?: string
  prominence_percentage?: number
  scale_position?: number
  related_tokens?: string[]
  usage?: string[]
  raw?: any
}

/**
 * Comprehensive Spacing Detail Cards
 * Organized display of all spacing data in semantic groupings
 */
export default function SpacingDetailCard({ fallback }: { fallback?: any[] }) {
  const spacing = useTokenGraphStore((s: any) => s.spacing)

  const tokens: SpacingTokenDetail[] = (spacing.length ? spacing : fallback || [])
    .map((s: any, idx: number) => {
      const val = s.raw?.$value || { value: s.value_px }
      const px = typeof val === 'object' && val ? val.value : s.value_px
      const rem = typeof px === 'number' ? px / 16 : 0
      return {
        id: s.id || s.name || `spacing-${px}`,
        px,
        rem,
        confidence: s.confidence,
        semantic_role: s.semantic_role,
        spacing_type: s.spacing_type,
        grid_aligned: s.grid_aligned,
        tailwind_class: s.tailwind_class,
        prominence_percentage: s.prominence_percentage,
        scale_position: s.scale_position,
        related_tokens: s.related_tokens,
        usage: s.usage,
        raw: s,
      }
    })
    .sort((a: SpacingTokenDetail, b: SpacingTokenDetail) => a.px - b.px)
    .map((token, idx) => ({ ...token, id: `${token.id}-${idx}` }))

  if (!tokens.length) {
    return null
  }

  return (
    <div className="spacing-detail-cards">
      <div className="spacing-detail-title">Token Details & Metadata</div>
      <div className="spacing-detail-grid">
        {tokens.map((token) => (
          <div key={token.id} className="spacing-detail-card">
            {/* Header with name and value */}
            <div className="detail-header">
              <div className="detail-name">{token.id}</div>
              <div className="detail-value">{token.px}px</div>
            </div>

            {/* Core Section: Value & Conversion */}
            <div className="detail-section">
              <div className="section-title">Value</div>
              <div className="section-content">
                <div className="detail-row">
                  <span className="label">Pixels</span>
                  <span className="value mono">{token.px}px</span>
                </div>
                <div className="detail-row">
                  <span className="label">Rem</span>
                  <span className="value mono">{token.rem.toFixed(2)}rem</span>
                </div>
                <div className="detail-row">
                  <span className="label">Confidence</span>
                  <div className="confidence-badge" style={{ '--confidence': token.confidence ?? 0 } as React.CSSProperties}>
                    {Math.round((token.confidence ?? 0) * 100)}%
                  </div>
                </div>
              </div>
            </div>

            {/* Semantic Section */}
            {(token.semantic_role || token.spacing_type || token.usage?.length) && (
              <div className="detail-section">
                <div className="section-title">Semantic</div>
                <div className="section-content">
                  {token.semantic_role && (
                    <div className="detail-row">
                      <span className="label">Role</span>
                      <span className="badge badge-semantic">{token.semantic_role}</span>
                    </div>
                  )}
                  {token.spacing_type && (
                    <div className="detail-row">
                      <span className="label">Type</span>
                      <span className="badge badge-type">{token.spacing_type}</span>
                    </div>
                  )}
                  {token.prominence_percentage != null && (
                    <div className="detail-row">
                      <span className="label">Prominence</span>
                      <span className="value">{token.prominence_percentage.toFixed(1)}%</span>
                    </div>
                  )}
                  {token.usage && token.usage.length > 0 && (
                    <div className="detail-row">
                      <span className="label">Uses</span>
                      <div className="usage-tags">
                        {token.usage.slice(0, 3).map((u, i) => (
                          <span key={i} className="tag">
                            {u}
                          </span>
                        ))}
                        {token.usage.length > 3 && <span className="tag">+{token.usage.length - 3}</span>}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Scale & Grid Section */}
            {(token.scale_position != null || token.grid_aligned != null) && (
              <div className="detail-section">
                <div className="section-title">Scale & Grid</div>
                <div className="section-content">
                  {token.scale_position != null && (
                    <div className="detail-row">
                      <span className="label">Position</span>
                      <span className="value">#{token.scale_position}</span>
                    </div>
                  )}
                  {token.grid_aligned != null && (
                    <div className="detail-row">
                      <span className="label">Grid Aligned</span>
                      <span className={`badge ${token.grid_aligned ? 'badge-success' : 'badge-warning'}`}>
                        {token.grid_aligned ? '✓ Yes' : '⚠ Off-Grid'}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Developer Section */}
            {(token.tailwind_class || token.related_tokens?.length) && (
              <div className="detail-section">
                <div className="section-title">Developer</div>
                <div className="section-content">
                  {token.tailwind_class && (
                    <div className="detail-row">
                      <span className="label">Tailwind</span>
                      <span className="badge badge-code">{token.tailwind_class}</span>
                    </div>
                  )}
                  {token.related_tokens && token.related_tokens.length > 0 && (
                    <div className="detail-row">
                      <span className="label">Related</span>
                      <div className="related-tags">
                        {token.related_tokens.slice(0, 2).map((t, i) => (
                          <span key={i} className="tag tag-related">
                            {t}
                          </span>
                        ))}
                        {token.related_tokens.length > 2 && <span className="tag">+{token.related_tokens.length - 2}</span>}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

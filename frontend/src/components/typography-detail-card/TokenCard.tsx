import React from 'react'
import type { TypographyTokenDetail } from './types'
import { useHasQualityMetrics, useHasStyleAttributes } from './hooks'

interface TokenCardProps {
  token: TypographyTokenDetail
}

export function TokenCard({ token }: TokenCardProps) {
  const hasQuality = useHasQualityMetrics(token)
  const hasStyle = useHasStyleAttributes(token)

  return (
    <div className="typo-detail-card">
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
      {hasQuality && (
        <div className="typo-section">
          <div className="typo-section-title">Quality</div>
          <div className="typo-section-content">
            {token.confidence != null && (
              <div className="typo-row">
                <span className="label">Confidence</span>
                <div
                  className="typo-confidence-badge"
                  style={{ '--typo-confidence': token.confidence } as React.CSSProperties}
                >
                  {Math.round(token.confidence * 100)}%
                </div>
              </div>
            )}
            {token.readabilityScore != null && (
              <div className="typo-row">
                <span className="label">Readability</span>
                <div
                  className="typo-readability-badge"
                  style={{ '--typo-readability': token.readabilityScore } as React.CSSProperties}
                >
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
      {hasStyle && (
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
  )
}

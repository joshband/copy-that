import React from 'react'
import { useTokenGraphStore } from '../store/tokenGraphStore'

const chip = (label: string) => <span className="chip chip-neutral">{label}</span>

export default function TypographyCards() {
  const typography = useTokenGraphStore((s) => s.typography)
  const recommendation = useTokenGraphStore((s) => s.typographyRecommendation)
  if (!typography.length) {
    return (
      <div className="empty-subpanel">
        <div className="empty-icon">🔤</div>
        <p className="empty-title">No typography tokens yet</p>
        <p className="empty-subtitle">Wire up typography extraction to see styles.</p>
      </div>
    )
  }

  const styleChips = recommendation?.styleAttributes
    ? Object.entries(recommendation.styleAttributes).map(([k, v]) => `${k}:${String(v)}`)
    : []

  return (
    <div className="typo-grid">
      {recommendation && (
        <div className="typo-meta">
          <span className="chip chip-info">
            Confidence {recommendation.confidence != null ? recommendation.confidence.toFixed(2) : '—'}
          </span>
          {styleChips.map((label) => (
            <span key={label} className="chip chip-neutral">{label}</span>
          ))}
        </div>
      )}
      {typography.map((t) => {
        const val = (t.raw as any)?.$value as any
        const fontFamilyRaw = Array.isArray(val?.fontFamily) ? val.fontFamily[0] : val?.fontFamily
        const fontFamily =
          typeof fontFamilyRaw === 'string' ? fontFamilyRaw.replace(/^{|}$/g, '') : undefined
        const fontSize = val?.fontSize
        const fontSizeText =
          fontSize && typeof fontSize === 'object' && 'value' in fontSize
            ? `${(fontSize as any).value}${(fontSize as any).unit ?? 'px'}`
            : typeof fontSize === 'string'
              ? fontSize.replace(/^{|}$/g, '')
              : undefined
        const weight = val?.fontWeight ?? '—'
        const colorRef = val?.color
        const casing = val?.casing
        return (
          <div key={t.id} className="typo-card">
            <div className="typo-header">
              <div>
                <div className="mono">{t.id}</div>
                <div className="muted">{fontFamily ?? '—'}</div>
              </div>
              <div className="chip-row">
                {fontSizeText ? chip(fontSizeText) : null}
                {weight ? chip(String(weight)) : null}
                {casing ? chip(casing) : null}
              </div>
            </div>
            <div
              className="typo-preview"
              style={{
                fontFamily,
                fontSize: fontSizeText,
                fontWeight: weight as any,
                color: typeof colorRef === 'string' ? 'inherit' : undefined,
              }}
            >
              The quick brown fox jumps over the lazy dog.
            </div>
            <div className="typo-meta-row">
              {colorRef ? <span className="muted">Color: {String(colorRef).replace(/^{|}$/g, '')}</span> : null}
            </div>
          </div>
        )
      })}
    </div>
  )
}

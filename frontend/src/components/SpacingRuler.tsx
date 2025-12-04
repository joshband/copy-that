import React from 'react'
import { useTokenGraphStore } from '../store/tokenGraphStore'

interface SpacingToken {
  id: string
  px: number
  rem: number
}

/**
 * Step Bar / Ruler Visualization
 * Shows spacing tokens as horizontal bars proportional to their size.
 * Creates a visual rhythm that makes hierarchy obvious without reading numbers.
 */
export default function SpacingRuler({ fallback }: { fallback?: any[] }) {
  const spacing = useTokenGraphStore((s: any) => s.spacing)

  const tokens: SpacingToken[] = (spacing.length ? spacing : fallback || [])
    .map((s: any, idx: number) => {
      const val = s.raw?.$value || { value: s.value_px }
      const px = typeof val === 'object' && val ? val.value : s.value_px
      const rem = typeof px === 'number' ? px / 16 : 0
      return {
        id: s.id || s.name || `spacing-${px}`,
        px,
        rem,
      }
    })
    .sort((a: SpacingToken, b: SpacingToken) => a.px - b.px)
    .map((token, idx) => ({ ...token, id: `${token.id}-${idx}` }))

  if (!tokens.length) {
    return (
      <div className="empty-subpanel">
        <div className="empty-icon">📏</div>
        <p className="empty-title">No spacing tokens yet</p>
        <p className="empty-subtitle">Run spacing extraction to populate this tab.</p>
      </div>
    )
  }

  // Find max for scaling
  const maxPx = Math.max(...tokens.map(t => t.px), 1)
  const scale = 100 / maxPx // normalize to 100px max bar width

  return (
    <div className="spacing-ruler">
      <div className="spacing-ruler-title">Spacing Scale</div>
      <div className="spacing-ruler-list">
        {tokens.map((token) => (
          <div key={token.id} className="spacing-ruler-row">
            <div className="spacing-ruler-label">{token.id}</div>

            <div className="spacing-ruler-bar-container">
              <div
                className="spacing-ruler-bar"
                style={{
                  '--bar-width': `${Math.max(token.px * scale, 2)}px`,
                } as React.CSSProperties}
              />
            </div>

            <div className="spacing-ruler-values">
              <span className="spacing-ruler-value">{token.px}px</span>
              <span className="spacing-ruler-rem">{token.rem.toFixed(2)}rem</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

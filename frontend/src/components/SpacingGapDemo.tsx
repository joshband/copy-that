import React, { useState } from 'react'
import { useTokenGraphStore } from '../store/tokenGraphStore'

interface SpacingToken {
  id: string
  px: number
  rem: number
}

/**
 * Gap Demo / Real-World Usage Component
 * Shows spacing in action as actual gaps between elements.
 * Helps developers immediately understand "this is the gap between items".
 */
export default function SpacingGapDemo({ fallback }: { fallback?: any[] }) {
  const spacing = useTokenGraphStore((s: any) => s.spacing)
  const [activeTokenId, setActiveTokenId] = useState<string | null>(null)

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
    return null
  }

  // Default to smallest token if none selected
  const selectedToken = tokens.find(t => t.id === activeTokenId) || tokens[0]

  return (
    <div className="spacing-gap-demo">
      <div className="spacing-gap-title">Gap Preview</div>
      <p className="spacing-gap-subtitle">See spacing in action between elements</p>

      {/* Token selector chips */}
      <div className="spacing-gap-chips">
        {tokens.map((token) => (
          <button
            key={token.id}
            className={`spacing-gap-chip ${activeTokenId === token.id || (activeTokenId === null && token === tokens[0]) ? 'active' : ''}`}
            onClick={() => setActiveTokenId(token.id)}
          >
            {token.id}
          </button>
        ))}
      </div>

      {/* Demo stack with active spacing */}
      <div
        className="spacing-demo-stack"
        style={{ '--space-token': `${selectedToken.px}px` } as React.CSSProperties}
      >
        <div className="spacing-demo-item">Item</div>
        <div className="spacing-demo-item">Item</div>
        <div className="spacing-demo-item">Item</div>
      </div>

      {/* Value display */}
      <div className="spacing-gap-value">
        <span className="spacing-gap-value-label">Active spacing:</span>
        <span className="spacing-gap-value-text">
          {selectedToken.px}px ({selectedToken.rem.toFixed(2)}rem)
        </span>
      </div>
    </div>
  )
}

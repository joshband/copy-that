import React, { useState } from 'react'
import { useTokenGraphStore } from '../store/tokenGraphStore'
import type { UiSpacingToken } from '../store/tokenGraphStore'

interface SpacingToken {
  id: string
  px: number
  rem: number
}

interface SpacingFallback {
  id?: string
  name?: string
  value_px: number
  value_rem?: number
  multiplier?: number
}

// Type guard
function isUiSpacingToken(token: UiSpacingToken | SpacingFallback): token is UiSpacingToken {
  return 'raw' in token && 'category' in token
}

/**
 * Gap Demo / Real-World Usage Component
 * Shows spacing in action as actual gaps between elements.
 * Helps developers immediately understand "this is the gap between items".
 */
export default function SpacingGapDemo({ fallback }: { fallback?: SpacingFallback[] }) {
  const spacing = useTokenGraphStore((s) => s.spacing)
  const [activeTokenId, setActiveTokenId] = useState<string | null>(null)

  const tokens: SpacingToken[] = (spacing.length ? spacing : fallback || [])
    .map((s: UiSpacingToken | SpacingFallback, idx: number) => {
      if (isUiSpacingToken(s)) {
        const val = s.raw?.$value
        const px = typeof val === 'object' && val && 'value' in val ? val.value : 0
        const rem = px / 16
        return { id: s.id, px, rem }
      } else {
        const px = s.value_px
        const rem = s.value_rem ?? px / 16
        return { id: s.id || s.name || `spacing-${px}`, px, rem }
      }
    })
    .sort((a: SpacingToken, b: SpacingToken) => a.px - b.px)
    .map((token: SpacingToken, idx: number) => ({ ...token, id: `${token.id}-${idx}` }))

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

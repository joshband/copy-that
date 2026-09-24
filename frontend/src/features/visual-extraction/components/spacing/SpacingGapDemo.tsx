import React, { useState } from 'react'
import { useTokenGraphStore } from '../../../../store/tokenGraphStore'
import type { UiSpacingToken } from '../../../../store/tokenGraphStore'

interface SpacingToken {
  id: string
  label: string
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

function shortLabel(id: string, index: number): string {
  const tail = id.split('/').filter(Boolean).pop()
  if (tail && /^\d+$/.test(tail)) return String(tail).padStart(2, '0')
  if (tail && tail.length <= 12 && !tail.includes('token')) return tail
  return `${index + 1}`
}

/**
 * Gap Demo / Real-World Usage Component
 * Shows spacing in action as actual gaps between elements.
 * Helps developers immediately understand "this is the gap between items".
 */
export default function SpacingGapDemo({ fallback, selectedId, onSelect }: { fallback?: SpacingFallback[]; selectedId?: string | null; onSelect?: (id: string) => void }) {
  const spacing = useTokenGraphStore((s) => s.spacing)
  const [localSelection, setLocalSelection] = useState<string | null>(null)
  const activeTokenId = selectedId === undefined ? localSelection : selectedId
  const setActiveTokenId = onSelect ?? setLocalSelection

  const tokens: SpacingToken[] = (spacing.length ? spacing : fallback || [])
    .map((s: UiSpacingToken | SpacingFallback, idx: number) => {
      if (isUiSpacingToken(s)) {
        const val = s.raw?.$value
        const px = typeof val === 'object' && val && 'value' in val ? val.value * (val.unit === 'rem' ? 16 : 1) : 0
        const rem = px / 16
        return { id: `${s.id}-${idx}`, label: shortLabel(s.id, idx), px, rem }
      } else {
        const px = s.value_px
        const rem = s.value_rem ?? px / 16
        const rawId = s.id || s.name || `spacing-${px}`
        return { id: `${rawId}-${idx}`, label: shortLabel(rawId, idx), px, rem }
      }
    })
    .sort((a: SpacingToken, b: SpacingToken) => a.px - b.px)

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
            type="button"
            className={`spacing-gap-chip ${activeTokenId === token.id || (activeTokenId === null && token === tokens[0]) ? 'active' : ''}`}
            onClick={() => setActiveTokenId(token.id)}
            title={token.id}
          >
            {token.label}
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

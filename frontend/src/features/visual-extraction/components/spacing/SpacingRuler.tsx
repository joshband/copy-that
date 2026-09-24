import React, { useMemo } from 'react'
import { useTokenGraphStore } from '../../../../store/tokenGraphStore'
import type { UiSpacingToken } from '../../../../store/tokenGraphStore'
import { TokenSourceChip } from '../../../../components/TokenSourceChip'
import type { SpacingExtractionResponse } from '../../../../types'

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
 * Step Bar / Ruler Visualization
 * Shows spacing tokens as horizontal bars proportional to their size.
 */
export default function SpacingRuler({
  fallback,
  selectedId, onSelect,
  extraction = null,
}: {
  fallback?: SpacingFallback[]
  selectedId?: string | null
  onSelect?: (id: string) => void
  extraction?: SpacingExtractionResponse | null
}) {
  const spacing = useTokenGraphStore((s) => s.spacing)

  const tokens: SpacingToken[] = (spacing.length ? spacing : fallback || [])
    .map((s: UiSpacingToken | SpacingFallback, idx: number) => {
      if (isUiSpacingToken(s)) {
        const val = s.raw?.$value
        const px = typeof val === 'object' && val && 'value' in val ? val.value * (val.unit === 'rem' ? 16 : 1) : 0
        const rem = px / 16
        return {
          id: `${s.id}-${idx}`,
          label: shortLabel(s.id, idx),
          px,
          rem,
        }
      }
      const px = s.value_px
      const rem = s.value_rem ?? px / 16
      const rawId = s.id || s.name || `spacing-${px}`
      return {
        id: `${rawId}-${idx}`,
        label: shortLabel(rawId, idx),
        px,
        rem,
      }
    })
    .sort((a: SpacingToken, b: SpacingToken) => a.px - b.px)

  const isFallback = useMemo(() => {
    const breakdown = extraction?.spacing_confidence_breakdown
    if (breakdown && typeof breakdown.fallback === 'number' && breakdown.fallback >= 1) {
      return true
    }
    return (extraction?.warnings ?? []).some((w) => /fallback/i.test(w))
  }, [extraction])

  const confidencePct = useMemo(() => {
    const conf = extraction?.extraction_confidence
    if (typeof conf !== 'number' || Number.isNaN(conf)) return null
    return Math.round(conf * 100)
  }, [extraction])

  if (!tokens.length) {
    return (
      <div className="empty-subpanel">
        <p className="empty-title standin">No spacing tokens yet</p>
        <p className="empty-subtitle standin">Extract an image to populate spacing scale and gap previews.</p>
      </div>
    )
  }

  const maxPx = Math.max(...tokens.map((t) => t.px), 1)
  const scale = 100 / maxPx

  return (
    <div className="spacing-ruler" data-testid="spacing-visual">
      <div className="spacing-ruler-header">
        <div className="spacing-ruler-title">Spacing scale</div>
        {(isFallback || confidencePct != null) && (
          <p className="spacing-confidence-line" data-testid="spacing-confidence">
            {isFallback ? (
              <>
                <TokenSourceChip source="fallback" />
                <span>Unmeasured 4pt preset · {confidencePct ?? 15}% confidence</span>
              </>
            ) : (
              <span>Measured scale · {confidencePct}%</span>
            )}
          </p>
        )}
      </div>
      <div className="spacing-ruler-list">
        {tokens.map((token) => (
          <button type="button" key={token.id} className="spacing-ruler-row" aria-pressed={selectedId === token.id || (!selectedId && token === tokens[0])} onClick={() => onSelect?.(token.id)}>
            <div className="spacing-ruler-label" title={token.id}>
              {token.label}
            </div>

            <div className="spacing-ruler-bar-container">
              <div
                className="spacing-ruler-bar"
                style={
                  {
                    '--bar-width': `${Math.max(token.px * scale, 2)}%`,
                  } as React.CSSProperties
                }
              />
            </div>

            <div className="spacing-ruler-values">
              <span className="spacing-ruler-value">{token.px}px</span>
              <span className="spacing-ruler-rem">{token.rem.toFixed(2)}rem</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}

import React, { useMemo } from 'react'
import { useTokenGraphStore } from '../../../../store/tokenGraphStore'
import { TokenSourceChip } from '../../../../components/TokenSourceChip'
import type { SpacingExtractionResponse } from '../../../../types'

const spacingValue = (token: any): number | undefined => {
  const val = token?.$value
  if (val && typeof val === 'object' && 'value' in val) {
    return (val).value as number
  }
  return undefined
}

type Props = {
  extraction?: SpacingExtractionResponse | null
}

export default function SpacingScalePanel({ extraction = null }: Props) {
  const { spacing, loaded } = useTokenGraphStore()

  const base = useMemo(() => {
    return (
      spacing.find((t) => t.id.toLowerCase().includes('base')) ??
      spacing.find((t) => t.multiplier == null)
    )
  }, [spacing])

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

  if (!loaded || spacing.length === 0) return null

  return (
    <div className="spacing-scale-panel">
      <h2>Spacing scale (graph)</h2>
      <p className="panel-subtitle">Base spacing and multiples derived from the token graph.</p>
      {(isFallback || confidencePct != null) && (
        <p className="spacing-confidence-line" data-testid="spacing-confidence">
          {isFallback ? (
            <>
              <TokenSourceChip source="fallback" />
              <span>Unmeasured 4pt preset · {confidencePct ?? 15}% confidence</span>
            </>
          ) : (
            <span>Measured scale · {confidencePct}% confidence</span>
          )}
        </p>
      )}
      <ul className="token-list">
        {spacing.map((tok) => {
          const px = spacingValue(tok.raw)
          const raw = tok.raw as Record<string, unknown>
          return (
            <li key={tok.id}>
              <code>{tok.id}</code>
              {px != null && (
                <>
                  {' '}
                  = {px}
                  {(tok.raw)?.$value?.unit ?? 'px'}
                </>
              )}
              {base && tok.multiplier != null && (
                <span className="spacing-token-chip">
                  {tok.multiplier}× {base.id}
                </span>
              )}{' '}
              <TokenSourceChip
                raw={
                  isFallback
                    ? { ...raw, source: 'cv_fallback', extraction_metadata: { measured: false } }
                    : raw
                }
              />
            </li>
          )
        })}
      </ul>
    </div>
  )
}

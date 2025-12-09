import React, { useMemo } from 'react'
import { useTokenGraphStore } from '../../../../store/tokenGraphStore'

const spacingValue = (token: any): number | undefined => {
  const val = token?.$value
  if (val && typeof val === 'object' && 'value' in val) {
    return (val).value as number
  }
  return undefined
}

export default function SpacingScalePanel() {
  const { spacing, loaded } = useTokenGraphStore()

  const base = useMemo(() => {
    return (
      spacing.find((t) => t.id.toLowerCase().includes('base')) ??
      spacing.find((t) => t.multiplier == null)
    )
  }, [spacing])

  if (!loaded || spacing.length === 0) return null

  return (
    <section className="panel spacing-panel">
      <h2>Spacing scale (graph)</h2>
      <p className="panel-subtitle">Base spacing and multiples derived from the token graph.</p>
      <ul className="token-list">
        {spacing.map((tok) => {
          const px = spacingValue(tok.raw)
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
              )}
            </li>
          )
        })}
      </ul>
    </section>
  )
}

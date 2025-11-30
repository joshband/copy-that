import React from 'react'
import { useTokenGraphStore } from '../store/tokenGraphStore'

export default function SpacingGraphList() {
  const spacing = useTokenGraphStore((s) => s.spacing)
  if (!spacing.length) return null

  const valuePx = (tok: any): number | undefined => {
    const val = tok?.$value as any
    return val && typeof val === 'object' && 'value' in val ? val.value : undefined
  }

  return (
    <div className="spacing-graph-list">
      <h3>Spacing (graph)</h3>
      <ul className="token-list">
        {spacing.map((t) => (
          <li key={t.id}>
            <code>{t.id}</code> {valuePx(t.raw) != null ? `= ${valuePx(t.raw)}px` : ''}
            {t.multiplier != null && <span className="spacing-token-chip">{t.multiplier}×</span>}
          </li>
        ))}
      </ul>
    </div>
  )
}

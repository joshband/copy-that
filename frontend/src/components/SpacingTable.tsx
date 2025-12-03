import React from 'react'
import { useTokenGraphStore } from '../store/tokenGraphStore'

type FallbackSpacing = { id?: string; name?: string; value_px: number; value_rem?: number; multiplier?: number }

export default function SpacingTable({ fallback }: { fallback?: FallbackSpacing[] }) {
  const spacing = useTokenGraphStore((s: any) => s.spacing)
  const rows = spacing.length ? spacing : []
  const fallbackRows = !rows.length && fallback ? fallback : []

  if (!rows.length && !fallbackRows.length) {
    return (
      <div className="empty-subpanel">
        <div className="empty-icon">📏</div>
        <p className="empty-title">No spacing tokens yet</p>
        <p className="empty-subtitle">Run spacing extraction to populate this tab.</p>
      </div>
    )
  }

  return (
    <div className="table-card">
      <div className="table-head">
        <div>Name</div>
        <div>Px</div>
        <div>Rem</div>
        <div>Base/Multiplier</div>
      </div>
      <div className="table-body">
        {rows.map((s: any) => {
          const val = (s.raw)?.$value
          const px = typeof val === 'object' && val ? val.value : undefined
          const rem = val?.unit === 'px' && typeof px === 'number' ? px / 16 : undefined
          return (
            <div key={s.id} className="table-row">
              <div className="cell-id mono">{s.id}</div>
              <div className="mono">{px ?? '—'}</div>
              <div className="muted">{rem != null ? rem.toFixed(2) : '—'}</div>
              <div>
                {s.multiplier != null ? (
                  <span className="chip chip-multiple">{s.multiplier}× {s.baseId ?? ''}</span>
                ) : (
                  <span className="chip chip-neutral">base</span>
                )}
              </div>
            </div>
          )
        })}
        {fallbackRows.map((s: any, idx: number) => (
          <div key={s.id ?? idx} className="table-row">
            <div className="cell-id mono">{s.id ?? s.name ?? `spacing-${idx + 1}`}</div>
            <div className="mono">{s.value_px}</div>
            <div className="muted">{s.value_rem != null ? s.value_rem.toFixed(2) : '—'}</div>
            <div>
              {s.multiplier != null ? (
                <span className="chip chip-multiple">{s.multiplier}×</span>
              ) : (
                <span className="chip chip-neutral">legacy</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

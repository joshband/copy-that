import React from 'react'
import { useTokenGraphStore } from '../store/tokenGraphStore'

export default function SpacingTable() {
  const spacing = useTokenGraphStore((s) => s.spacing)
  if (!spacing.length) {
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
        {spacing.map((s) => {
          const val = (s.raw as any)?.$value as any
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
      </div>
    </div>
  )
}

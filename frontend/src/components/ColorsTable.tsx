import React from 'react'
import { useTokenGraphStore } from '../store/tokenGraphStore'

const badge = (label: string, tone: 'neutral' | 'alias' = 'neutral') => (
  <span className={`chip chip-${tone}`}>{label}</span>
)

export default function ColorsTable() {
  const colors = useTokenGraphStore((s) => s.colors)
  if (!colors.length) {
    return (
      <div className="empty-subpanel">
        <div className="empty-icon">🎨</div>
        <p className="empty-title">No color tokens yet</p>
        <p className="empty-subtitle">Upload an image to see extracted colors.</p>
      </div>
    )
  }

  return (
    <div className="table-card">
      <div className="table-head">
        <div>Token</div>
        <div>Hex</div>
        <div>Role</div>
        <div>Alias</div>
      </div>
      <div className="table-body">
        {colors.map((c) => {
          const val = (c.raw as any)?.$value as any
          const hex =
            (typeof val === 'object' && val?.hex) ||
            (c.raw as any)?.hex ||
            (c.raw as any)?.attributes?.hex ||
            '#cccccc'
          const role = (c.raw as any)?.attributes?.role || (c.raw as any)?.role || ''
          return (
            <div key={c.id} className="table-row">
              <div className="cell-id">
                <span className="swatch" style={{ background: hex }} />
                <span className="mono">{c.id}</span>
              </div>
              <div className="mono">{hex}</div>
              <div className="muted">{role || '—'}</div>
              <div>
                {c.isAlias && c.aliasTargetId ? (
                  <>
                    {badge('alias', 'alias')} <span className="mono">{c.aliasTargetId}</span>
                  </>
                ) : (
                  badge('base')
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

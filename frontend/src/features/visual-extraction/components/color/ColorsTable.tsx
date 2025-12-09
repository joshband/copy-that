import React from 'react'
import { useTokenGraphStore } from '../../../../store/tokenGraphStore'

const badge = (label: string, tone: 'neutral' | 'alias' = 'neutral') => (
  <span className={`chip chip-${tone}`}>{label}</span>
)

type FallbackColor = { id: string; hex: string; name?: string; role?: string }

export default function ColorsTable({ fallback }: { fallback?: FallbackColor[] }) {
  const colors = useTokenGraphStore((s: any) => s.colors)
  const rows = colors.length ? colors : []
  const fallbackRows = !rows.length && fallback ? fallback : []

  if (!rows.length && !fallbackRows.length) {
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
        {rows.map((c: any) => {
          const val = (c.raw)?.$value
          const hex =
            (typeof val === 'object' && val?.hex) ||
            (c.raw)?.hex ||
            (c.raw)?.attributes?.hex ||
            '#cccccc'
          const role = (c.raw)?.attributes?.role || (c.raw)?.role || ''
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
        {fallbackRows.map((c) => (
          <div key={c.id} className="table-row">
            <div className="cell-id">
              <span className="swatch" style={{ background: c.hex }} />
              <span className="mono">{c.id}</span>
            </div>
            <div className="mono">{c.hex}</div>
            <div className="muted">{c.role || '—'}</div>
            <div>{badge('legacy')}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

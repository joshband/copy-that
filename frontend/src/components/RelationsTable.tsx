import React, { useMemo, useState } from 'react'
import { useTokenGraphStore } from '../store/tokenGraphStore'

type Relation = { source: string; type: string; target: string; meta?: string }

export default function RelationsTable() {
  const colors = useTokenGraphStore((s) => s.colors)
  const spacing = useTokenGraphStore((s) => s.spacing)
  const shadows = useTokenGraphStore((s) => s.shadows)
  const typography = useTokenGraphStore((s) => s.typography)
  const [filter, setFilter] = useState<string>('all')

  const relations: Relation[] = useMemo(() => {
    const rows: Relation[] = []
    colors.forEach((c) => {
      if (c.isAlias && c.aliasTargetId) {
        rows.push({ source: c.id, type: 'aliasOf', target: c.aliasTargetId })
      }
    })
    spacing.forEach((s) => {
      if (s.baseId) {
        rows.push({
          source: s.id,
          type: 'multipleOf',
          target: s.baseId,
          meta: s.multiplier != null ? `${s.multiplier}×` : undefined,
        })
      }
    })
    shadows.forEach((s) => {
      s.referencedColorIds.forEach((tgt) => rows.push({ source: s.id, type: 'composes', target: tgt }))
    })
    typography.forEach((t) => {
      if (t.fontFamilyTokenId) rows.push({ source: t.id, type: 'composes', target: t.fontFamilyTokenId, meta: 'font-family' })
      if (t.fontSizeTokenId) rows.push({ source: t.id, type: 'composes', target: t.fontSizeTokenId, meta: 'font-size' })
      if (t.referencedColorId) rows.push({ source: t.id, type: 'composes', target: t.referencedColorId, meta: 'color' })
    })
    return rows
  }, [colors, spacing, shadows, typography])

  const filtered = relations.filter((r) => filter === 'all' || r.type === filter)

  if (!relations.length) {
    return (
      <div className="empty-subpanel">
        <div className="empty-icon">🕸️</div>
        <p className="empty-title">No relations detected</p>
        <p className="empty-subtitle">Aliases, multiples, and composites will show here.</p>
      </div>
    )
  }

  return (
    <div className="table-card">
      <div className="filter-row">
        <label>
          Filter:{' '}
          <select value={filter} onChange={(e) => setFilter(e.target.value)}>
            <option value="all">All</option>
            <option value="aliasOf">Alias</option>
            <option value="multipleOf">Multiple Of</option>
            <option value="composes">Composes</option>
          </select>
        </label>
        <span className="muted">{filtered.length} of {relations.length}</span>
      </div>
      <div className="table-head">
        <div>Source</div>
        <div>Type</div>
        <div>Target</div>
        <div>Meta</div>
      </div>
      <div className="table-body">
        {filtered.map((r, idx) => (
          <div key={`${r.source}-${r.target}-${idx}`} className="table-row">
            <div className="mono">{r.source}</div>
            <div><span className="chip chip-neutral">{r.type}</span></div>
            <div className="mono">{r.target}</div>
            <div className="muted">{r.meta || '—'}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

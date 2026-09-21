import React from 'react'
import { useTokenGraphStore } from '../store/tokenGraphStore'

export default function RelationsDebugPanel() {
  const { colors, spacing, shadows, typography, layout } = useTokenGraphStore()
  const all = [...colors, ...spacing, ...shadows, ...typography, ...layout]

  const relationsFor = (raw: any) =>
    (raw && (raw).relations && Array.isArray((raw).relations)
      ? ((raw).relations as Array<{ type: string; target: string; meta?: any }>)
      : []) as Array<{ type: string; target: string; meta?: any }>

  if (!all.some((t) => relationsFor(t.raw).length)) return null

  return (
    <section className="panel">
      <h2>Token graph relations (debug)</h2>
      <ul className="token-list">
        {all.map((tok) => {
          const rels = relationsFor(tok.raw)
          if (!rels.length) return null
          return (
            <li key={tok.id}>
              <strong>{tok.id}</strong>
              <ul>
                {rels.map((rel, idx) => (
                  <li key={idx}>
                    {rel.type} → <code>{rel.target}</code>
                    {rel.meta?.multiplier != null && <span> ({rel.meta.multiplier}×)</span>}
                    {rel.meta?.role && <span> [{rel.meta.role}]</span>}
                  </li>
                ))}
              </ul>
            </li>
          )
        })}
      </ul>
    </section>
  )
}

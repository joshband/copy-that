import React from 'react'
import { useTokenGraphStore } from '../store/tokenGraphStore'

export default function ColorGraphPanel() {
  const { colors, loaded } = useTokenGraphStore()

  if (!loaded || colors.length === 0) return null

  const baseColors = colors.filter((c: any) => !c.isAlias)
  const aliasColors = colors.filter((c: any) => c.isAlias)

  return (
    <section className="panel">
      <h2>Color graph</h2>
      <p className="panel-subtitle">Base palette and alias roles from the token graph.</p>
      <div className="color-graph-grid">
        <div>
          <h3>Base colors</h3>
          <ul className="token-list">
            {baseColors.map((tok: any) => (
              <li key={tok.id}>
                <code>{tok.id}</code>
              </li>
            ))}
          </ul>
        </div>
        {aliasColors.length > 0 && (
          <div>
            <h3>Aliases</h3>
            <ul className="token-list">
              {aliasColors.map((tok: any) => (
                <li key={tok.id}>
                  <code>{tok.id}</code> → <code>{tok.aliasTargetId ?? 'unknown'}</code>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </section>
  )
}

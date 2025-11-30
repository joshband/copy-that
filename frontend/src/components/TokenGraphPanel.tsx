import React, { useMemo } from 'react'
import './TokenGraphPanel.css'
import type { SpacingExtractionResponse } from '../types'

type Props = {
  spacingResult?: SpacingExtractionResponse | null
}

type TreeNode = {
  id: string
  children: string[]
  parent_id?: string | null
  meta?: Record<string, unknown>
}

export default function TokenGraphPanel({ spacingResult }: Props) {
  const nodes = (spacingResult?.token_graph as TreeNode[] | undefined) ?? []
  const fastsamCount = spacingResult?.fastsam_tokens?.length ?? 0
  const textCount = spacingResult?.text_tokens?.length ?? 0
  const uiedCount = spacingResult?.uied_tokens?.length ?? 0

  const tree = useMemo(() => {
    if (!nodes.length) return []
    const lookup = new Map<string, TreeNode>()
    nodes.forEach((n) => lookup.set(n.id, n))
    const roots = nodes.filter((n) => !n.parent_id || !lookup.has(String(n.parent_id)))
    const build = (node: TreeNode, depth = 0): Array<{ node: TreeNode; depth: number }> => {
      const row = [{ node, depth }]
      node.children?.forEach((cid) => {
        const child = lookup.get(String(cid))
        if (child) {
          row.push(...build(child, depth + 1))
        }
      })
      return row
    }
    return roots.flatMap((r) => build(r))
  }, [nodes])

  if (!spacingResult) return null

  return (
    <div className="token-graph-panel">
      <div className="tgp-header">
        <div>
          <p className="eyebrow">Token Graph</p>
          <h3>Structure & Sources</h3>
          <p className="tgp-subtitle">
            View containment/alignment graph plus CV/FastSAM/Text token counts. Useful for verifying every token type is present.
          </p>
        </div>
        <div className="tgp-stats">
          <span className="pill">graph nodes: {nodes.length}</span>
          <span className="pill">segments: {fastsamCount}</span>
          <span className="pill">text: {textCount}</span>
          <span className="pill">uied: {uiedCount}</span>
        </div>
      </div>

      {!nodes.length ? (
        <p className="muted">No token graph available yet.</p>
      ) : (
        <>
          <div className="tgp-table" role="table" aria-label="Token graph">
            <div className="tgp-row head" role="row">
              <div>ID</div>
              <div>Depth</div>
              <div>Children</div>
              <div>Meta</div>
            </div>
            <div className="tgp-body">
              {tree.map(({ node, depth }) => (
                <div key={node.id} className="tgp-row" role="row">
                  <div className="tgp-id">
                    <span style={{ paddingLeft: `${depth * 12}px` }}>#{node.id}</span>
                  </div>
                  <div>{depth}</div>
                  <div>{node.children?.length ?? 0}</div>
                  <div className="tgp-meta">
                    {node.meta ? (
                      <code>{JSON.stringify(node.meta)}</code>
                    ) : (
                      <span className="muted">—</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="tgp-tree">
            <svg width="100%" height={Math.max(200, tree.length * 28)} className="tgp-svg">
              {tree.map(({ node, depth }, idx) => {
                const y = 20 + idx * 26
                const x = 24 + depth * 32
                return (
                  <g key={`node-${node.id}`}>
                    {node.children?.map((cid) => {
                      const childIdx = tree.findIndex((n) => n.node.id === cid)
                      if (childIdx === -1) return null
                      const cy = 20 + childIdx * 26
                      const cx2 = 24 + (depth + 1) * 32
                      return (
                        <line
                          key={`edge-${node.id}-${cid}`}
                          x1={x}
                          y1={y}
                          x2={cx2}
                          y2={cy}
                          className="tgp-edge"
                        />
                      )
                    })}
                    <circle cx={x} cy={y} r={7} className="tgp-node" />
                    <text x={x + 12} y={y + 4} className="tgp-text">
                      {node.id}
                    </text>
                  </g>
                )
              })}
            </svg>
          </div>
        </>
      )}
    </div>
  )
}

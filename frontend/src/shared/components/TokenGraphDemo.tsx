/**
 * Token Graph Demo Component
 *
 * Educational demonstration of token graph relationships
 * Shows how to use useTokenGraph() hook
 *
 * ARCHITECTURE: Uses adapter pattern for token-specific rendering
 * - Generic graph logic (this file)
 * - Domain-specific rendering (adapters)
 * - Scales to multimodal tokens (audio, video, etc.)
 */

import React, { useState } from 'react'
import { useTokenGraph, isColorToken, isSpacingToken, isShadowToken, isTypographyToken } from '../hooks/useTokenGraph'
import { getAdapter, hasAdapter } from '../adapters'
import './TokenGraphDemo.css'

// Import ALL visual adapters to trigger auto-registration
import '../../features/visual-extraction/adapters/ColorVisualAdapter'
import '../../features/visual-extraction/adapters/SpacingVisualAdapter'
import '../../features/visual-extraction/adapters/TypographyVisualAdapter'
import '../../features/visual-extraction/adapters/ShadowVisualAdapter'

export function TokenGraphDemo() {
  const graph = useTokenGraph()
  const [selectedTokenId, setSelectedTokenId] = useState<string | null>(null)

  const allTokens = graph.getAllNodes()
  const selectedToken = selectedTokenId ? graph.getNode(selectedTokenId) : null

  // Get relationships for selected token
  const dependencies = selectedToken ? graph.getDependencies(selectedToken.id) : []
  const dependents = selectedToken ? graph.getDependents(selectedToken.id) : []
  const aliases = selectedToken && isColorToken(selectedToken) ? graph.getAliases(selectedToken.id) : []
  const resolved = selectedToken && isColorToken(selectedToken) && selectedToken.isAlias
    ? graph.resolveAlias(selectedToken.id)
    : null

  if (allTokens.length === 0) {
    return (
      <div className="token-graph-demo token-graph-demo--empty">
        <h3>Token Graph</h3>
        <p className="token-graph-demo__muted">Upload an image to see token relationships</p>
      </div>
    )
  }

  return (
    <div className="token-graph-demo">
      <div className="token-graph-demo__intro">
        <h3>Token Graph Explorer</h3>
        <p className="token-graph-demo__muted">
          Explore token relationships: aliases, dependencies, and composition
        </p>
      </div>

      {/* Token List */}
      <div className="token-graph-demo__section">
        <h4>All Tokens ({allTokens.length})</h4>
        <div className="token-graph-demo__grid">
          {allTokens.slice(0, 20).map((token) => {
            // Use adapter for rendering if available
            const adapter = hasAdapter(token.category) ? getAdapter(token.category) : null
            const isSelected = selectedTokenId === token.id

            return (
              <button
                key={token.id}
                onClick={() => setSelectedTokenId(token.id)}
                className={`token-graph-demo__token ${isSelected ? 'token-graph-demo__token--selected' : ''}`}
              >
                <div className="token-graph-demo__token-row">
                  {/* Adapter-based swatch rendering */}
                  {adapter && <div className="token-graph-demo__token-swatch">{adapter.renderSwatch(token)}</div>}
                  <div className="token-graph-demo__token-meta">
                    <div className="token-graph-demo__token-category">{token.category}</div>
                    <div className="token-graph-demo__token-name">
                      {adapter ? adapter.getDisplayName(token) : token.id}
                    </div>
                    {adapter && (
                      <div className="token-graph-demo__token-value">
                        {adapter.getDisplayValue(token)}
                      </div>
                    )}
                    {isColorToken(token) && token.isAlias && (
                      <div className="token-graph-demo__token-alias">Alias</div>
                    )}
                  </div>
                </div>
              </button>
            )
          })}
        </div>
        {allTokens.length > 20 && (
          <p className="token-graph-demo__muted token-graph-demo__muted--small">
            Showing first 20 of {allTokens.length} tokens
          </p>
        )}
      </div>

      {/* Selected Token Details */}
      {selectedToken && (
        <div className="token-graph-demo__details">
          <h4>Token Details</h4>

          {/* Adapter-based rendering */}
          {hasAdapter(selectedToken.category) && (
            <div className="token-graph-demo__detail-card">
              <div>{getAdapter(selectedToken.category).renderSwatch(selectedToken)}</div>
              <div className="token-graph-demo__detail-meta">
                {getAdapter(selectedToken.category).renderMetadata(selectedToken)}
              </div>
            </div>
          )}

          <div className="token-graph-demo__detail-grid">
            <strong>ID:</strong>
            <span>{selectedToken.id}</span>

            <strong>Category:</strong>
            <span>{selectedToken.category}</span>

            {isColorToken(selectedToken) && (
              <>
                <strong>Is Alias:</strong>
                <span>{selectedToken.isAlias ? 'Yes' : 'No'}</span>

                {selectedToken.isAlias && selectedToken.aliasTargetId && (
                  <>
                    <strong>Alias Target:</strong>
                    <span>{selectedToken.aliasTargetId}</span>
                  </>
                )}
              </>
            )}

            {isSpacingToken(selectedToken) && selectedToken.baseId && (
              <>
                <strong>Base Token:</strong>
                <span>{selectedToken.baseId}</span>

                {selectedToken.multiplier && (
                  <>
                    <strong>Multiplier:</strong>
                    <span>{selectedToken.multiplier}×</span>
                  </>
                )}
              </>
            )}

            {isShadowToken(selectedToken) && selectedToken.referencedColorIds.length > 0 && (
              <>
                <strong>Color Refs:</strong>
                <span>{selectedToken.referencedColorIds.join(', ')}</span>
              </>
            )}

            {isTypographyToken(selectedToken) && (
              <>
                {selectedToken.referencedColorId && (
                  <>
                    <strong>Color Ref:</strong>
                    <span>{selectedToken.referencedColorId}</span>
                  </>
                )}
                {selectedToken.fontFamilyTokenId && (
                  <>
                    <strong>Font Family:</strong>
                    <span>{selectedToken.fontFamilyTokenId}</span>
                  </>
                )}
                {selectedToken.fontSizeTokenId && (
                  <>
                    <strong>Font Size:</strong>
                    <span>{selectedToken.fontSizeTokenId}</span>
                  </>
                )}
              </>
            )}
          </div>

          {/* Dependencies */}
          {dependencies.length > 0 && (
            <div className="token-graph-demo__group">
              <strong>Dependencies ({dependencies.length}):</strong>
              <div className="token-graph-demo__chip-row">
                {dependencies.map((dep) => (
                  <button
                    key={dep.id}
                    onClick={() => setSelectedTokenId(dep.id)}
                    className="token-graph-demo__chip"
                  >
                    {dep.id}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Dependents */}
          {dependents.length > 0 && (
            <div className="token-graph-demo__group">
              <strong>Used By ({dependents.length}):</strong>
              <div className="token-graph-demo__chip-row">
                {dependents.map((dep) => (
                  <button
                    key={dep.id}
                    onClick={() => setSelectedTokenId(dep.id)}
                    className="token-graph-demo__chip"
                  >
                    {dep.id}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Aliases */}
          {aliases.length > 0 && (
            <div className="token-graph-demo__group">
              <strong>Aliases ({aliases.length}):</strong>
              <div className="token-graph-demo__chip-row">
                {aliases.map((alias) => (
                  <button
                    key={alias.id}
                    onClick={() => setSelectedTokenId(alias.id)}
                    className="token-graph-demo__chip"
                  >
                    {alias.id}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Resolved Alias */}
          {resolved && resolved.id !== selectedToken.id && (
            <div className="token-graph-demo__resolve">
              <strong>Resolves To:</strong>
              <button
                onClick={() => setSelectedTokenId(resolved.id)}
                className="token-graph-demo__chip token-graph-demo__chip--accent"
              >
                {resolved.id}
              </button>
            </div>
          )}
        </div>
      )}

      {/* Graph Statistics */}
      <div className="token-graph-demo__stats">
        <h4>Graph Statistics</h4>
        <div className="token-graph-demo__stats-grid">
          <div className="token-graph-demo__stat">
            <div className="token-graph-demo__stat-label">Total Tokens</div>
            <div className="token-graph-demo__stat-value">{allTokens.length}</div>
          </div>
          <div className="token-graph-demo__stat">
            <div className="token-graph-demo__stat-label">Colors</div>
            <div className="token-graph-demo__stat-value">{graph.getNodes('color').length}</div>
          </div>
          <div className="token-graph-demo__stat">
            <div className="token-graph-demo__stat-label">Spacing</div>
            <div className="token-graph-demo__stat-value">{graph.getNodes('spacing').length}</div>
          </div>
          <div className="token-graph-demo__stat">
            <div className="token-graph-demo__stat-label">Shadows</div>
            <div className="token-graph-demo__stat-value">{graph.getNodes('shadow').length}</div>
          </div>
          <div className="token-graph-demo__stat">
            <div className="token-graph-demo__stat-label">Typography</div>
            <div className="token-graph-demo__stat-value">{graph.getNodes('typography').length}</div>
          </div>
          <div className="token-graph-demo__stat">
            <div className="token-graph-demo__stat-label">Root Tokens</div>
            <div className="token-graph-demo__stat-value">{graph.getRootTokens().length}</div>
          </div>
        </div>
      </div>
    </div>
  )
}

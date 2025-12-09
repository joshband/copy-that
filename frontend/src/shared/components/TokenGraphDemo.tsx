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

// Import adapters to trigger auto-registration
import '../../features/visual-extraction/adapters/ColorVisualAdapter'

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
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <h3>Token Graph Demo</h3>
        <p>Upload an image to see token relationships</p>
      </div>
    )
  }

  return (
    <div style={{ padding: '1rem', border: '1px solid #ddd', borderRadius: '8px', margin: '1rem' }}>
      <h3>🕸️ Token Graph Explorer</h3>
      <p style={{ color: '#666', fontSize: '0.9rem' }}>
        Explore token relationships: aliases, dependencies, and composition
      </p>

      {/* Token List */}
      <div style={{ marginTop: '1rem' }}>
        <h4>All Tokens ({allTokens.length})</h4>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '0.5rem' }}>
          {allTokens.slice(0, 20).map((token) => {
            // Use adapter for rendering if available
            const adapter = hasAdapter(token.category) ? getAdapter(token.category) : null

            return (
              <button
                key={token.id}
                onClick={() => setSelectedTokenId(token.id)}
                style={{
                  padding: '0.5rem',
                  border: selectedTokenId === token.id ? '2px solid #0066FF' : '1px solid #ddd',
                  borderRadius: '4px',
                  background: selectedTokenId === token.id ? '#E6F0FF' : 'white',
                  cursor: 'pointer',
                  textAlign: 'left',
                }}
              >
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                  {/* Adapter-based swatch rendering */}
                  {adapter && <div>{adapter.renderSwatch(token)}</div>}
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: '0.75rem', color: '#666' }}>{token.category}</div>
                    <div style={{ fontWeight: 500 }}>{adapter ? adapter.getDisplayName(token) : token.id}</div>
                    {adapter && (
                      <div style={{ fontSize: '0.75rem', fontFamily: 'monospace', color: '#888' }}>
                        {adapter.getDisplayValue(token)}
                      </div>
                    )}
                    {isColorToken(token) && token.isAlias && (
                      <div style={{ fontSize: '0.7rem', color: '#0066FF' }}>→ alias</div>
                    )}
                  </div>
                </div>
              </button>
            )
          })}
        </div>
        {allTokens.length > 20 && (
          <p style={{ color: '#666', fontSize: '0.8rem', marginTop: '0.5rem' }}>
            Showing first 20 of {allTokens.length} tokens
          </p>
        )}
      </div>

      {/* Selected Token Details */}
      {selectedToken && (
        <div style={{ marginTop: '2rem', padding: '1rem', background: '#F5F5F5', borderRadius: '6px' }}>
          <h4>Token Details</h4>

          {/* Adapter-based rendering */}
          {hasAdapter(selectedToken.category) && (
            <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start', marginBottom: '1rem', padding: '1rem', background: 'white', borderRadius: '4px' }}>
              <div>{getAdapter(selectedToken.category).renderSwatch(selectedToken)}</div>
              <div style={{ flex: 1 }}>
                {getAdapter(selectedToken.category).renderMetadata(selectedToken)}
              </div>
            </div>
          )}

          <div style={{ display: 'grid', gridTemplateColumns: '120px 1fr', gap: '0.5rem', fontSize: '0.9rem' }}>
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
            <div style={{ marginTop: '1rem' }}>
              <strong>Dependencies ({dependencies.length}):</strong>
              <div style={{ marginTop: '0.5rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                {dependencies.map((dep) => (
                  <button
                    key={dep.id}
                    onClick={() => setSelectedTokenId(dep.id)}
                    style={{
                      padding: '0.25rem 0.5rem',
                      background: '#E3F2FD',
                      border: '1px solid #2196F3',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '0.8rem',
                    }}
                  >
                    {dep.id}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Dependents */}
          {dependents.length > 0 && (
            <div style={{ marginTop: '1rem' }}>
              <strong>Used By ({dependents.length}):</strong>
              <div style={{ marginTop: '0.5rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                {dependents.map((dep) => (
                  <button
                    key={dep.id}
                    onClick={() => setSelectedTokenId(dep.id)}
                    style={{
                      padding: '0.25rem 0.5rem',
                      background: '#FFF3E0',
                      border: '1px solid #FF9800',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '0.8rem',
                    }}
                  >
                    {dep.id}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Aliases */}
          {aliases.length > 0 && (
            <div style={{ marginTop: '1rem' }}>
              <strong>Aliases ({aliases.length}):</strong>
              <div style={{ marginTop: '0.5rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                {aliases.map((alias) => (
                  <button
                    key={alias.id}
                    onClick={() => setSelectedTokenId(alias.id)}
                    style={{
                      padding: '0.25rem 0.5rem',
                      background: '#F3E5F5',
                      border: '1px solid #9C27B0',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '0.8rem',
                    }}
                  >
                    {alias.id}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Resolved Alias */}
          {resolved && resolved.id !== selectedToken.id && (
            <div style={{ marginTop: '1rem' }}>
              <strong>Resolves To:</strong>
              <button
                onClick={() => setSelectedTokenId(resolved.id)}
                style={{
                  padding: '0.5rem',
                  background: '#E8F5E9',
                  border: '2px solid #4CAF50',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  marginLeft: '0.5rem',
                }}
              >
                {resolved.id}
              </button>
            </div>
          )}
        </div>
      )}

      {/* Graph Statistics */}
      <div style={{ marginTop: '2rem', padding: '1rem', background: '#FAFAFA', borderRadius: '6px' }}>
        <h4>Graph Statistics</h4>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem' }}>
          <div>
            <div style={{ fontSize: '0.75rem', color: '#666' }}>Total Tokens</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{allTokens.length}</div>
          </div>
          <div>
            <div style={{ fontSize: '0.75rem', color: '#666' }}>Colors</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{graph.getNodes('color').length}</div>
          </div>
          <div>
            <div style={{ fontSize: '0.75rem', color: '#666' }}>Spacing</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{graph.getNodes('spacing').length}</div>
          </div>
          <div>
            <div style={{ fontSize: '0.75rem', color: '#666' }}>Shadows</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{graph.getNodes('shadow').length}</div>
          </div>
          <div>
            <div style={{ fontSize: '0.75rem', color: '#666' }}>Typography</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{graph.getNodes('typography').length}</div>
          </div>
          <div>
            <div style={{ fontSize: '0.75rem', color: '#666' }}>Root Tokens</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{graph.getRootTokens().length}</div>
          </div>
        </div>
      </div>
    </div>
  )
}

/**
 * TokenInspectorSidebar
 *
 * Displays detailed information for selected token
 * Shows metadata, related tokens, and token history
 * Integrates with Zustand store for selection state
 */

import React, { useMemo } from 'react';
import { useTokenStore } from '../store/tokenStore';
import { ColorToken } from '../../types';
import './TokenInspectorSidebar.css';

export const TokenInspectorSidebar: React.FC = () => {
  const { tokens, selectedTokenId, sidebarOpen, toggleSidebar } = useTokenStore();

  const selectedToken = useMemo(() => {
    return tokens.find(t => t.id === selectedTokenId);
  }, [tokens, selectedTokenId]);

  if (!selectedToken) {
    return (
      <aside className={`inspector-sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="inspector-sidebar__header">
          <h2 className="inspector-sidebar__title">Inspector</h2>
          <button
            className="inspector-sidebar__toggle"
            onClick={toggleSidebar}
            title={sidebarOpen ? 'Close' : 'Open'}
          >
            {sidebarOpen ? '✕' : '▶'}
          </button>
        </div>
        <div className="inspector-sidebar__empty">
          <p>Select a token to inspect</p>
        </div>
      </aside>
    );
  }

  return (
    <aside className={`inspector-sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
      {/* Header */}
      <div className="inspector-sidebar__header">
        <h2 className="inspector-sidebar__title">Inspector</h2>
        <button
          className="inspector-sidebar__toggle"
          onClick={toggleSidebar}
          title={sidebarOpen ? 'Close' : 'Open'}
        >
          {sidebarOpen ? '✕' : '▶'}
        </button>
      </div>

      {/* Token Display */}
      <div className="inspector-sidebar__content">
        {/* Token Name & Visual */}
        <div className="inspector-section">
          <div className="inspector-header">
            {selectedToken.hex && (
              <div
                className="inspector-swatch"
                style={{ backgroundColor: selectedToken.hex }}
              />
            )}
            <div>
              <h3 className="inspector-name">{selectedToken.name}</h3>
              {selectedToken.hex && (
                <code className="inspector-hex">{selectedToken.hex}</code>
              )}
            </div>
          </div>
        </div>

        {/* Metadata */}
        <div className="inspector-section">
          <h4 className="inspector-section-title">Metadata</h4>
          <div className="inspector-grid">
            {selectedToken.confidence && (
              <div className="inspector-item">
                <span className="inspector-label">Confidence</span>
                <span className="inspector-value">
                  {Math.round(selectedToken.confidence * 100)}%
                </span>
              </div>
            )}
            {selectedToken.rgb && (
              <div className="inspector-item">
                <span className="inspector-label">RGB</span>
                <code className="inspector-value">{selectedToken.rgb}</code>
              </div>
            )}
            {(selectedToken as any).hue !== undefined && (
              <div className="inspector-item">
                <span className="inspector-label">Hue</span>
                <span className="inspector-value">
                  {Math.round((selectedToken as any).hue)}°
                </span>
              </div>
            )}
            {(selectedToken as any).saturation !== undefined && (
              <div className="inspector-item">
                <span className="inspector-label">Saturation</span>
                <span className="inspector-value">
                  {Math.round((selectedToken as any).saturation)}%
                </span>
              </div>
            )}
            {(selectedToken as any).lightness !== undefined && (
              <div className="inspector-item">
                <span className="inspector-label">Lightness</span>
                <span className="inspector-value">
                  {Math.round((selectedToken as any).lightness)}%
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Color Properties */}
        {(selectedToken as any).temperature && (
          <div className="inspector-section">
            <h4 className="inspector-section-title">Properties</h4>
            <div className="inspector-grid">
              <div className="inspector-item">
                <span className="inspector-label">Temperature</span>
                <span className="inspector-value">
                  {(selectedToken as any).temperature}
                </span>
              </div>
              {(selectedToken as any).harmony && (
                <div className="inspector-item">
                  <span className="inspector-label">Harmony</span>
                  <span className="inspector-value">
                    {(selectedToken as any).harmony}
                  </span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Semantic Name */}
        {(selectedToken as any).semantic_name && (
          <div className="inspector-section">
            <h4 className="inspector-section-title">Semantic Name</h4>
            <p className="inspector-text">
              {(selectedToken as any).semantic_name}
            </p>
          </div>
        )}

        {/* Related Tokens (Similar Colors) */}
        <div className="inspector-section">
          <h4 className="inspector-section-title">Similar Colors</h4>
          <RelatedTokensList
            currentToken={selectedToken}
            allTokens={tokens}
            maxCount={3}
          />
        </div>

        {/* Token ID & Timestamps */}
        <div className="inspector-section inspector-section--muted">
          <h4 className="inspector-section-title">Details</h4>
          <div className="inspector-grid inspector-grid--small">
            <div className="inspector-item">
              <span className="inspector-label">ID</span>
              <code className="inspector-value inspector-value--small">
                {selectedToken.id}
              </code>
            </div>
            {(selectedToken as any).created_at && (
              <div className="inspector-item">
                <span className="inspector-label">Created</span>
                <span className="inspector-value inspector-value--small">
                  {new Date((selectedToken as any).created_at).toLocaleDateString()}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    </aside>
  );
};

/**
 * Related Tokens List
 * Shows similar tokens based on color distance
 */
interface RelatedTokensListProps {
  currentToken: ColorToken;
  allTokens: ColorToken[];
  maxCount: number;
}

const RelatedTokensList: React.FC<RelatedTokensListProps> = ({
  currentToken,
  allTokens,
  maxCount,
}) => {
  const relatedTokens = useMemo(() => {
    // Simple similarity: find tokens with similar hex values (first 3 chars = hue range)
    if (!currentToken.hex) return [];

    return allTokens
      .filter(t => t.id !== currentToken.id && t.hex)
      .slice(0, maxCount);
  }, [currentToken, allTokens, maxCount]);

  if (relatedTokens.length === 0) {
    return <p className="inspector-text inspector-text--muted">No similar colors found</p>;
  }

  return (
    <div className="related-tokens">
      {relatedTokens.map(token => (
        <div key={token.id} className="related-token-item">
          <div
            className="related-token-swatch"
            style={{ backgroundColor: token.hex }}
          />
          <div className="related-token-info">
            <div className="related-token-name">{token.name}</div>
            <code className="related-token-hex">{token.hex}</code>
          </div>
        </div>
      ))}
    </div>
  );
};

export default TokenInspectorSidebar;

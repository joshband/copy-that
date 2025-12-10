/**
 * TokenGrid
 *
 * Generic grid view for tokens
 * Renders TokenCard for each token, applies filters/sorting from store
 * Supports grid, list, and table view modes
 */

import React, { useMemo } from 'react';
import { useTokenStore } from '../store/tokenStore';
import { tokenTypeRegistry } from '../config/tokenTypeRegistry';
import TokenCard from '../card/TokenCard';
import './TokenGrid.css';

export const TokenGrid: React.FC = () => {
  const {
    tokens,
    tokenType,
    filters,
    sortBy,
    viewMode,
  } = useTokenStore();

  const schema = tokenTypeRegistry[tokenType];

  // Apply filters and sorting
  const filteredAndSortedTokens = useMemo(() => {
    let result = [...tokens];

    // Apply filters
    Object.entries(filters).forEach(([key, value]) => {
      if (!value) return;
      result = result.filter((token: any) => {
        const tokenValue = token[key];
        return tokenValue === value;
      });
    });

    // Apply sorting
    if (sortBy === 'name') {
      result.sort((a, b) => (a.name || '').localeCompare(b.name || ''));
    } else if (sortBy === 'hue' && tokenType === 'color') {
      result.sort((a, b) => {
        const aHue = (a as any).hue || 0;
        const bHue = (b as any).hue || 0;
        return aHue - bHue;
      });
    } else if (sortBy === 'confidence') {
      result.sort((a, b) => (b.confidence || 0) - (a.confidence || 0));
    }

    return result;
  }, [tokens, filters, sortBy, tokenType]);

  if (!schema) {
    return <div className="token-grid empty">Token type not supported</div>;
  }

  if (filteredAndSortedTokens.length === 0) {
    return (
      <div className="token-grid empty">
        <div className="token-grid__empty-message">
          No tokens found
          {Object.keys(filters).length > 0 && ' (try clearing filters)'}
        </div>
      </div>
    );
  }

  return (
    <div className={`token-grid token-grid--${viewMode}`}>
      {filteredAndSortedTokens.map((token) => (
        <TokenCard
          key={token.id}
          token={token}
          tokenType={tokenType}
        />
      ))}
    </div>
  );
};

export default TokenGrid;

/**
 * TokenCard
 *
 * Generic token card component that works with any token type via registry schema
 * Displays token visual representation, metadata, and format tabs
 * Integrated with Zustand store for selection, editing, and deletion
 */

import React, { useState } from 'react';
import { ColorToken } from '../types';
import { useTokenStore, TokenType } from '../store/tokenStore';
import { tokenTypeRegistry } from '../config/tokenTypeRegistry';
import './TokenCard.css';

export interface TokenCardProps {
  token: Partial<ColorToken>;
  tokenType: TokenType;
}

export const TokenCard: React.FC<TokenCardProps> = ({ token, tokenType }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [activeTab, setActiveTab] = useState(0);

  const {
    selectedTokenId,
    selectToken,
    startEditing,
    deleteToken,
  } = useTokenStore();

  const schema = tokenTypeRegistry[tokenType];
  if (!schema) return null;

  const isSelected = selectedTokenId === token.id;

  const handleSelect = () => {
    if (isSelected) {
      selectToken(null);
    } else {
      selectToken(token.id as string | number);
    }
  };

  const handleEdit = () => {
    startEditing(token as ColorToken);
  };

  const handleDelete = () => {
    if (token.id) {
      deleteToken(token.id);
    }
  };

  const handleDuplicate = () => {
    // Generate new ID for duplicate
    const newToken = {
      ...token,
      id: `${token.id}-duplicate-${Date.now()}`,
    };
    // Store will handle insertion
  };

  const PrimaryVisual = schema.primaryVisual;
  const formatTabs = schema.formatTabs;

  return (
    <div
      data-testid="token-card"
      className={`token-card ${isSelected ? 'selected' : ''}`}
      onClick={handleSelect}
    >
      {/* Header */}
      <div className="token-card__header">
        <div className="token-card__visual">
          {tokenType === 'color' && token.hex && (
            <div
              data-testid="color-swatch"
              className="token-card__swatch"
              style={{ backgroundColor: token.hex as string }}
            />
          )}
        </div>

        <div className="token-card__metadata">
          <div className="token-card__name">{token.name}</div>
          {token.hex && (
            <code className="token-card__hex">{token.hex}</code>
          )}
          {token.confidence && (
            <div className="token-card__confidence">
              {Math.round(token.confidence * 100)}%
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="token-card__actions">
          <button
            data-testid="edit-button"
            className="token-card__action-btn"
            onClick={(e) => {
              e.stopPropagation();
              handleEdit();
            }}
            title="Edit"
          >
            ✎
          </button>
          <button
            data-testid="duplicate-button"
            className="token-card__action-btn"
            onClick={(e) => {
              e.stopPropagation();
              handleDuplicate();
            }}
            title="Duplicate"
          >
            ⧉
          </button>
          <button
            data-testid="delete-button"
            className="token-card__action-btn token-card__action-btn--danger"
            onClick={(e) => {
              e.stopPropagation();
              handleDelete();
            }}
            title="Delete"
          >
            ✕
          </button>
          <button
            data-testid="expand-button"
            className={`token-card__expand-btn ${isExpanded ? 'expanded' : ''}`}
            onClick={(e) => {
              e.stopPropagation();
              setIsExpanded(!isExpanded);
            }}
            title={isExpanded ? 'Collapse' : 'Expand'}
          >
            ▼
          </button>
        </div>
      </div>

      {/* Primary Visual */}
      <div className="token-card__primary">
        <PrimaryVisual token={token} />
      </div>

      {/* Expanded Details */}
      {isExpanded && (
        <div className="token-card__details">
          {/* Format Tabs */}
          {formatTabs.length > 0 && (
            <div className="token-card__tabs">
              <div className="token-card__tab-list">
                {formatTabs.map((tab, idx) => (
                  <button
                    key={idx}
                    className={`token-card__tab ${
                      activeTab === idx ? 'active' : ''
                    }`}
                    onClick={() => setActiveTab(idx)}
                  >
                    {tab.name}
                  </button>
                ))}
              </div>

              <div className="token-card__tab-content">
                {formatTabs[activeTab] && (() => {
                  const TabComponent = formatTabs[activeTab].component;
                  return (
                    <div data-testid={`${formatTabs[activeTab].name.toLowerCase()}-tab`}>
                      <TabComponent token={token} />
                    </div>
                  );
                })()}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TokenCard;

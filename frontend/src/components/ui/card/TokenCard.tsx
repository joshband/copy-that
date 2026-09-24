/**
 * TokenCard
 *
 * Generic token card component that works with any token type via registry schema
 * Displays token visual representation, metadata, and format tabs
 * Integrated with Zustand store for selection, editing, and deletion
 */

import React, { useCallback, useMemo, useState } from 'react';
import { Tabs, TabList, TabPanel, TabPanels, TabTrigger } from '../tabs/Tabs';
import type { ColorToken } from '../../../types';
import { TokenType } from '../../../store/uiStore';
import { useTokenViewState } from '../../../store/tokenView';
import { tokenTypeRegistry } from '../../../config/tokenTypeRegistry';
import './TokenCard.css';

export interface TokenCardProps {
  token: Partial<ColorToken>;
  tokenType: TokenType;
}

export const TokenCard: React.FC<TokenCardProps> = React.memo(({ token, tokenType }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [activeTab, setActiveTab] = useState('0');

  const {
    selectedTokenId,
    selectToken,
    startEditing,
    deleteToken,
    duplicateToken,
  } = useTokenViewState();

  const schema = useMemo(() => tokenTypeRegistry[tokenType], [tokenType]);
  if (!schema) return null;

  const isSelected = selectedTokenId === token.id;
  const semanticName = (token as any)?.semantic_names || token.name;
  const designIntent = (token as any)?.design_intent;
  const extractor = (token as any)?.extractor || (token as any)?.extraction_metadata?.extractor;

  const handleSelect = useCallback(() => {
    if (isSelected) {
      selectToken(null);
    } else {
      selectToken(token.id as string | number);
    }
  }, [isSelected, selectToken, token.id]);

  const handleEdit = useCallback(() => {
    startEditing(token as ColorToken);
  }, [startEditing, token]);

  const handleDelete = useCallback(() => {
    if (token.id) {
      void deleteToken(token.id);
    }
  }, [deleteToken, token.id]);

  const handleDuplicate = useCallback(() => {
    if (token.id) {
      void duplicateToken(token.id);
    }
  }, [duplicateToken, token.id]);

  const PrimaryVisual = schema.primaryVisual;
  const formatTabs = schema.formatTabs ?? [];

  const handleToggleExpand = useCallback((e: React.MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation();
    setIsExpanded((prev) => !prev);
  }, []);

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
              style={{ backgroundColor: token.hex }}
            />
          )}
        </div>

        <div className="token-card__metadata">
          <div className="token-card__name">{semanticName || token.name}</div>
          {designIntent && <div className="token-card__intent">{designIntent}</div>}
          {token.hex && <code className="token-card__hex">{token.hex}</code>}
          {token.confidence && (
            <div className="token-card__confidence">
              {Math.round(token.confidence * 100)}%
            </div>
          )}
          {extractor && (
            <div className="token-card__attribution" title="Extractor attribution">
              Extracted by {extractor}
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
            onClick={handleToggleExpand}
            title={isExpanded ? 'Collapse' : 'Expand'}
          >
            ▼
          </button>
        </div>
      </div>

      {/* Primary Visual */}
      {typeof PrimaryVisual === 'function' ? (
        <div className="token-card__primary">
          <PrimaryVisual token={token} />
        </div>
      ) : null}

      {/* Expanded Details */}
      {isExpanded && (
        <div className="token-card__details">
          {/* Format Tabs */}
          {formatTabs.length > 0 && (
            <Tabs value={activeTab} onValueChange={setActiveTab} className="token-card__tabs">
              <TabList className="token-card__tab-list">
                {formatTabs.map((tab: any, idx: number) => (
                  <TabTrigger
                    key={idx}
                    value={String(idx)}
                    className="token-card__tab"
                    activeClassName="active"
                  >
                    {tab.name}
                  </TabTrigger>
                ))}
              </TabList>
              <TabPanels className="token-card__tab-content">
                {formatTabs.map((tab: any, idx: number) => {
                  const TabComponent = tab.component;
                  return (
                    <TabPanel key={tab.name} value={String(idx)}>
                      <div data-testid={`${tab.name.toLowerCase()}-tab`}>
                        <TabComponent token={token} />
                      </div>
                    </TabPanel>
                  );
                })}
              </TabPanels>
            </Tabs>
          )}
        </div>
      )}
    </div>
  );
});

export default TokenCard;

/**
 * TokenPlaygroundDrawer
 *
 * Interactive editor for token mutations with live preview
 * Renders playground tabs from registry schema
 * Integrates with Zustand store for editing workflow
 */

import React, { useMemo } from 'react';
import { Tabs, TabList, TabTrigger, TabPanels, TabPanel } from './ui/tabs/Tabs';
import { useTokenStore } from '../store/tokenStore';
import { tokenTypeRegistry } from '../config/tokenTypeRegistry';
import type { ColorToken as _ColorToken } from '../types/index';
import './TokenPlaygroundDrawer.css';

// Type kept for future component extensions
type _Unused = _ColorToken;
void (0 as unknown as _Unused);

export const TokenPlaygroundDrawer: React.FC = () => {
  const {
    tokenType,
    playgroundOpen,
    playgroundToken,
    playgroundActiveTab,
    togglePlayground,
    setPlaygroundTab,
    setPlaygroundToken,
    applyPlaygroundChanges,
    resetPlayground,
    selectedTokenId,
    tokens,
  } = useTokenStore();

  const schema = tokenTypeRegistry[tokenType];
  const playgroundTabs = schema?.playgroundTabs || [];

  const selectedToken = useMemo(() => {
    return tokens.find((t: any) => t.id === selectedTokenId);
  }, [tokens, selectedTokenId]);

  // Initialize playground with selected token when playground opens
  // Intentionally not including playgroundToken/setPlaygroundToken to avoid re-initialization
  React.useEffect(() => {
    if (playgroundOpen && selectedToken && !playgroundToken) {
      setPlaygroundToken({ ...selectedToken });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [playgroundOpen, selectedToken]);

  return (
    <div className={`playground-drawer ${playgroundOpen ? 'open' : 'closed'}`}>
      {/* Header */}
      <div className="playground-drawer__header">
        <h2 className="playground-drawer__title">Playground</h2>
        <button
          className="playground-drawer__toggle"
          onClick={togglePlayground}
          title={playgroundOpen ? 'Close' : 'Open'}
        >
          {playgroundOpen ? '✕' : '◀'}
        </button>
      </div>

      {playgroundOpen && (
        <>
          {/* Content */}
          <div className="playground-drawer__content">
            {playgroundToken ? (
              <>
                <Tabs value={playgroundActiveTab} onValueChange={setPlaygroundTab}>
                  <TabList className="playground-drawer__tab-list">
                    {playgroundTabs.map((tab, idx) => (
                      <TabTrigger
                        key={idx}
                        value={idx.toString()}
                        className="playground-drawer__tab"
                        activeClassName="active"
                      >
                        {tab.name}
                      </TabTrigger>
                    ))}
                  </TabList>

                  <TabPanels className="playground-drawer__panel">
                    {playgroundTabs.map((tab, idx) => (
                      <TabPanel key={tab.name} value={idx.toString()}>
                        <tab.component token={playgroundToken} />
                      </TabPanel>
                    ))}
                  </TabPanels>
                </Tabs>

                {/* Preview */}
                <div className="playground-drawer__preview">
                  <h4 className="playground-drawer__preview-title">Preview</h4>
                  <div className="playground-drawer__preview-content">
                    {playgroundToken.hex && (
                      <div
                        className="playground-preview-swatch"
                        style={{ backgroundColor: playgroundToken.hex }}
                      />
                    )}
                    <div className="playground-preview-info">
                      <div className="playground-preview-name">
                        {playgroundToken.name || 'Unnamed'}
                      </div>
                      {playgroundToken.hex && (
                        <code className="playground-preview-hex">
                          {playgroundToken.hex}
                        </code>
                      )}
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="playground-drawer__actions">
                  <button
                    className="playground-drawer__btn playground-drawer__btn--apply"
                    onClick={applyPlaygroundChanges}
                  >
                    Apply Changes
                  </button>
                  <button
                    className="playground-drawer__btn playground-drawer__btn--reset"
                    onClick={resetPlayground}
                  >
                    Reset
                  </button>
                </div>
              </>
            ) : (
              <div className="playground-drawer__empty">
                <p>Select a token to start editing</p>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default TokenPlaygroundDrawer;

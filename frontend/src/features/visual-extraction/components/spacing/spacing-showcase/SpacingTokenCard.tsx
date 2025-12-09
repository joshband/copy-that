/**
 * SpacingTokenCard sub-component
 * Displays a single spacing token with visual and metadata
 */

import React from 'react';
import { SpacingToken } from './types';
import { styles } from './styles';

interface SpacingTokenCardProps {
  token: SpacingToken;
  copiedValue: string | null;
  showCopyButtons?: boolean;
  showMetadata?: boolean;
  onTokenClick?: (token: SpacingToken) => void;
  onCopyClick: (e: React.MouseEvent<HTMLButtonElement>, text: string, label: string) => void;
}

export const SpacingTokenCard: React.FC<SpacingTokenCardProps> = ({
  token,
  copiedValue,
  showCopyButtons = true,
  showMetadata = true,
  onTokenClick,
  onCopyClick,
}) => {
  const boxSize = Math.min(token.value_px, 80);

  return (
    <div
      style={styles.tokenCard}
      onClick={() => onTokenClick?.(token)}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-2px)';
        e.currentTarget.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.15)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'none';
        e.currentTarget.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.1)';
      }}
    >
      <div style={styles.tokenVisual}>
        <div
          style={{
            ...styles.spacingBox,
            width: `${boxSize}px`,
            height: `${boxSize}px`,
          }}
        >
          {token.value_px}px
        </div>
      </div>
      <div style={styles.tokenInfo}>
        <div style={styles.tokenName}>{token.name}</div>
        <div style={styles.tokenValues}>
          {token.value_px}px | {token.value_rem}rem
        </div>
        {token.prominence_percentage != null && (
          <div style={{ color: '#6b7280', fontSize: '0.85rem', marginTop: '0.1rem' }}>
            Prominence: {token.prominence_percentage.toFixed(1)}%
          </div>
        )}
        {token.role && (
          <span style={{ ...styles.badge, ...styles.roleBadge }}>{token.role}</span>
        )}
        {token.grid_aligned !== undefined && (
          <span
            style={{
              ...styles.badge,
              ...(token.grid_aligned ? styles.gridAlignedBadge : styles.gridMisalignedBadge),
            }}
          >
            {token.grid_aligned ? 'Grid Aligned' : 'Off Grid'}
          </span>
        )}
        {showMetadata && (
          <div style={styles.metadata}>
            Confidence: {(token.confidence * 100).toFixed(0)}%
            {token.provenance && ` | Sources: ${Object.keys(token.provenance).length}`}
          </div>
        )}
        {showCopyButtons && (
          <div style={styles.copyButtons}>
            <button
              style={styles.copyButton}
              onClick={(e) => onCopyClick(e, `${token.value_px}px`, 'px')}
            >
              {copiedValue === 'px' ? 'Copied!' : 'Copy px'}
            </button>
            <button
              style={styles.copyButton}
              onClick={(e) => onCopyClick(e, `${token.value_rem}rem`, 'rem')}
            >
              {copiedValue === 'rem' ? 'Copied!' : 'Copy rem'}
            </button>
            <button
              style={styles.copyButton}
              onClick={(e) => onCopyClick(e, `--${token.name}`, 'var')}
            >
              {copiedValue === 'var' ? 'Copied!' : 'Copy var'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default SpacingTokenCard;

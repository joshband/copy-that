/**
 * TokensSection sub-component
 * Displays filter controls and token grid
 */

import React from 'react';
import { SpacingToken, FilterType, SortType } from './types';
import { styles } from './styles';
import { FilterControls } from './FilterControls';
import { SpacingTokenCard } from './SpacingTokenCard';

interface TokensSectionProps {
  displayTokens: SpacingToken[];
  filter: FilterType;
  sortBy: SortType;
  copiedValue: string | null;
  showCopyButtons?: boolean;
  showMetadata?: boolean;
  onFilterChange: (filter: FilterType) => void;
  onSortChange: (sort: SortType) => void;
  onTokenClick?: (token: SpacingToken) => void;
  onCopyClick: (e: React.MouseEvent<HTMLButtonElement>, text: string, label: string) => void;
}

export const TokensSection: React.FC<TokensSectionProps> = ({
  displayTokens,
  filter,
  sortBy,
  copiedValue,
  showCopyButtons = true,
  showMetadata = true,
  onFilterChange,
  onSortChange,
  onTokenClick,
  onCopyClick,
}) => {
  return (
    <div style={styles.scaleSection}>
      <h2 style={styles.sectionTitle}>Spacing Tokens</h2>
      <FilterControls
        filter={filter}
        sortBy={sortBy}
        onFilterChange={onFilterChange}
        onSortChange={onSortChange}
      />
      <div style={styles.tokensGrid}>
        {displayTokens.map((token) => (
          <SpacingTokenCard
            key={token.name}
            token={token}
            copiedValue={copiedValue}
            showCopyButtons={showCopyButtons}
            showMetadata={showMetadata}
            onTokenClick={onTokenClick}
            onCopyClick={onCopyClick}
          />
        ))}
      </div>
    </div>
  );
};

export default TokensSection;

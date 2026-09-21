/**
 * SpacingTokenShowcase - Main Orchestrator Component
 *
 * Refactored monolithic component (512 LOC) into modular architecture:
 * - Main orchestrator (this file): ~100 LOC
 * - Custom hooks (hooks.ts): 150+ LOC
 * - Sub-components: 50-100 LOC each
 * - Shared types and styles
 *
 * Architecture inspired by Issue #9B ImageUploader refactoring pattern
 */

import React from 'react';
import { SpacingTokenShowcaseProps } from './types';
import { styles } from './styles';
import { useSpacingFiltering, useClipboard, useFileSelection, useScaleDerivation, useScaleVisualization } from './hooks';
import SpacingHeader from './SpacingHeader';
import { StatsGrid } from './StatsGrid';
import { ScaleVisualization } from './ScaleVisualization';
import { TokensSection } from './TokensSection';

export const SpacingTokenShowcase: React.FC<SpacingTokenShowcaseProps> = ({
  library,
  onTokenClick,
  showCopyButtons = true,
  showMetadata = true,
  onFileSelected,
  isLoading = false,
  error = null,
}) => {
  const { tokens, statistics } = library;

  // Hooks for state management
  const { filter, setFilter, sortBy, setSortBy, displayTokens } = useSpacingFiltering(tokens);
  const { copiedValue, copyToClipboard } = useClipboard();
  const { handleFileChange } = useFileSelection(onFileSelected);
  const { derivedBase, derivedScale } = useScaleDerivation(
    tokens,
    statistics.base_unit,
    statistics.scale_system
  );
  const { maxValue, getBarHeight } = useScaleVisualization(tokens);

  const handleCopyClick = (e: React.MouseEvent<HTMLButtonElement>, text: string, label: string) => {
    e.stopPropagation();
    void copyToClipboard(text, label);
  };

  return (
    <div style={styles.container}>
      <SpacingHeader
        library={library}
        onFileChange={handleFileChange}
        onFileSelected={onFileSelected}
        isLoading={isLoading}
        error={error}
      />

      <StatsGrid library={library} derivedBase={derivedBase} derivedScale={derivedScale} />

      <ScaleVisualization
        tokens={tokens}
        maxValue={maxValue}
        getBarHeight={getBarHeight}
        onTokenClick={onTokenClick}
      />

      <TokensSection
        displayTokens={displayTokens}
        filter={filter}
        sortBy={sortBy}
        copiedValue={copiedValue}
        showCopyButtons={showCopyButtons}
        showMetadata={showMetadata}
        onFilterChange={setFilter}
        onSortChange={setSortBy}
        onTokenClick={onTokenClick}
        onCopyClick={handleCopyClick}
      />
    </div>
  );
};

export default SpacingTokenShowcase;

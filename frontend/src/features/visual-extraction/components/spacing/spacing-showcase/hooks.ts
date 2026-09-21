/**
 * Custom hooks for SpacingTokenShowcase component
 */

import { useState, useMemo } from 'react';
import { SpacingToken, FilterType, SortType } from './types';

/**
 * Hook for managing spacing token filtering and sorting
 */
export const useSpacingFiltering = (tokens: SpacingToken[]) => {
  const [filter, setFilter] = useState<FilterType>('all');
  const [sortBy, setSortBy] = useState<SortType>('value');

  const displayTokens = useMemo(() => {
    let filtered = [...tokens];

    // Apply filter
    if (filter === 'aligned') {
      filtered = filtered.filter((t) => t.grid_aligned);
    } else if (filter === 'misaligned') {
      filtered = filtered.filter((t) => !t.grid_aligned);
    } else if (filter === 'multi-source') {
      filtered = filtered.filter((t) => t.provenance && Object.keys(t.provenance).length > 1);
    }

    // Apply sort
    filtered.sort((a, b) => {
      if (sortBy === 'value') return a.value_px - b.value_px;
      if (sortBy === 'confidence') return b.confidence - a.confidence;
      return a.name.localeCompare(b.name);
    });

    return filtered;
  }, [tokens, filter, sortBy]);

  return {
    filter,
    setFilter,
    sortBy,
    setSortBy,
    displayTokens,
  };
};

/**
 * Hook for managing clipboard copy functionality
 */
export const useClipboard = () => {
  const [copiedValue, setCopiedValue] = useState<string | null>(null);

  const copyToClipboard = async (text: string, label: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedValue(label);
      setTimeout(() => setCopiedValue(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return {
    copiedValue,
    copyToClipboard,
  };
};

/**
 * Hook for managing file selection
 */
export const useFileSelection = (onFileSelected?: (file: File) => void) => {
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && onFileSelected) {
      onFileSelected(file);
    }
  };

  return {
    handleFileChange,
  };
};

/**
 * Hook for deriving scale and base unit from tokens
 */
export const useScaleDerivation = (tokens: SpacingToken[], baseUnit: number, scale: string) => {
  const derivedBase = useMemo(
    () => tokens.find((t) => t.base_unit !== undefined)?.base_unit ?? baseUnit,
    [tokens, baseUnit]
  );

  const derivedScale = useMemo(
    () => tokens.find((t) => t.scale_system)?.scale_system ?? scale,
    [tokens, scale]
  );

  return { derivedBase, derivedScale };
};

/**
 * Hook for calculating max value for scale visualization
 */
export const useScaleVisualization = (tokens: SpacingToken[]) => {
  const maxValue = useMemo(
    () => Math.max(...tokens.map((t) => t.value_px), 0),
    [tokens]
  );

  const getBarHeight = (value: number, maxHeight = 150) => {
    return maxValue > 0 ? Math.min(maxHeight, (value / maxValue) * maxHeight) : 0;
  };

  return {
    maxValue,
    getBarHeight,
  };
};

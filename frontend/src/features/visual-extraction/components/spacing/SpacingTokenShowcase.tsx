/**
 * Spacing Token Showcase Component - DEPRECATED
 *
 * This file is kept for backward compatibility.
 * The component has been refactored into a modular architecture.
 *
 * New location: ./spacing-showcase/
 * Migration: Update imports to use the new modular version
 */

// Re-export the new modular component for backward compatibility
export { SpacingTokenShowcase, default } from './spacing-showcase/SpacingTokenShowcase';

// Also re-export types and hooks for consumers
export type {
  SpacingToken,
  SpacingLibrary,
  SpacingTokenShowcaseProps,
  FilterType,
  SortType,
} from './spacing-showcase/types';

export {
  useSpacingFiltering,
  useClipboard,
  useFileSelection,
  useScaleDerivation,
  useScaleVisualization,
} from './spacing-showcase/hooks';

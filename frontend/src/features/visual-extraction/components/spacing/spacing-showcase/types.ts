/**
 * Shared types for SpacingTokenShowcase component
 */

export interface SpacingToken {
  value_px: number;
  value_rem: number;
  name: string;
  confidence: number;
  semantic_role?: string;
  spacing_type?: string;
  role?: string;
  grid_aligned?: boolean;
  tailwind_class?: string;
  provenance?: Record<string, number>;
  prominence_percentage?: number;
  base_unit?: number;
  scale_system?: string;
}

export interface SpacingLibrary {
  tokens: SpacingToken[];
  statistics: {
    spacing_count: number;
    image_count: number;
    scale_system: string;
    base_unit: number;
    grid_compliance: number;
    avg_confidence: number;
    value_range: { min: number; max: number };
    common_values: number[];
    multi_image_spacings: number;
  };
}

export interface SpacingTokenShowcaseProps {
  library: SpacingLibrary;
  onTokenClick?: (token: SpacingToken) => void;
  showCopyButtons?: boolean;
  showMetadata?: boolean;
  onFileSelected?: (file: File) => void;
  isLoading?: boolean;
  error?: string | null;
}

export type FilterType = 'all' | 'aligned' | 'misaligned' | 'multi-source';
export type SortType = 'value' | 'confidence' | 'name';

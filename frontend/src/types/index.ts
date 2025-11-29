/**
 * Copy That - Shared Types
 *
 * Single source of truth for all TypeScript interfaces
 * Used across frontend components and API integration
 */

/**
 * ColorToken - Complete color data from extraction pipeline
 *
 * This interface represents a color extracted from an image,
 * with all metadata, harmony information, and accessibility data.
 * Matches backend ColorToken model exactly.
 */
export interface ColorToken {
  // Core identifiers
  id?: number | string;
  project_id?: number;
  extraction_job_id?: number;

  // Core display properties
  hex: string;
  rgb: string;
  hsl?: string;
  hsv?: string;
  name: string;

  // Design token properties
  design_intent?: string;
  semantic_names?: string | Record<string, unknown>;
  category?: string;

  // Color analysis properties
  confidence: number;
  harmony?: string;
  temperature?: string;
  extraction_metadata?: Record<string, string>;
  saturation_level?: string;
  lightness_level?: string;
  usage?: string[];

  // Count & prominence
  count?: number;
  prominence_percentage?: number;

  // Accessibility properties
  wcag_contrast_on_white?: number;
  wcag_contrast_on_black?: number;
  wcag_aa_compliant_text?: boolean;
  wcag_aaa_compliant_text?: boolean;
  wcag_aa_compliant_normal?: boolean;
  wcag_aaa_compliant_normal?: boolean;
  colorblind_safe?: boolean;

  // Color variants
  tint_color?: string;
  shade_color?: string;
  tone_color?: string;

  // Advanced properties
  closest_web_safe?: string;
  closest_css_named?: string;
  delta_e_to_dominant?: number;
  is_neutral?: boolean;

  // ML/CV model properties (optional, for advanced use)
  kmeans_cluster_id?: number;
  sam_segmentation_mask?: string;
  clip_embeddings?: number[];
  histogram_significance?: number;

  // Timestamps
  created_at?: string;

  // Token library & curation
  library_id?: number;
  role?: string;  // 'primary', 'secondary', 'accent', 'neutral', etc.
  provenance?: Record<string, number>;  // {"image_1": 0.95, "image_2": 0.88}
  background_role?: string; // primary/secondary background indicator
  contrast_category?: string; // high/medium/low contrast vs background
  foreground_role?: string; // text role assignment
}

export interface ColorRampEntry {
  $type?: string
  $value: {
    l?: number
    c?: number
    h?: number
    alpha?: number
    space?: string
    hex?: string
    [key: string]: unknown
  }
  [key: string]: unknown
}

export type ColorRampMap = Record<string, ColorRampEntry>

export interface SegmentedColor {
  hex: string
  coverage: number
}

export interface SpacingTokenResponse {
  value_px: number
  value_rem: number
  name: string
  confidence: number
  semantic_role?: string | null
  spacing_type?: string | null
  role?: string | null
  grid_aligned?: boolean | null
  tailwind_class?: string | null
}

export interface SpacingExtractionResponse {
  tokens: SpacingTokenResponse[]
  scale_system: string
  base_unit: number
  grid_compliance: number
  extraction_confidence: number
  unique_values: number[]
  min_spacing: number
  max_spacing: number
  cv_gap_diagnostics?: Record<string, unknown> | null
  base_alignment?: Record<string, unknown> | null
  cv_gaps_sample?: number[] | null
  baseline_spacing?: {
    value_px: number
    confidence: number
  } | null
  component_spacing_metrics?: Array<{
    index?: number
    box?: [number, number, number, number]
    padding?: Record<string, number>
    padding_confidence?: number
    margin?: Record<string, number>
    neighbor_gap?: number
  }> | null
  grid_detection?: {
    columns?: number
    gutter_px?: number
    margin_left?: number
    margin_right?: number
    confidence?: number
  } | null
  design_tokens?: Record<string, unknown> | null
}

/**
 * Project - User project context
 *
 * Groups extracted colors and settings for a specific design project
 */
export interface Project {
  id: number;
  name: string;
  description?: string;
  max_colors?: number;
  created_at: string;
  updated_at: string;
}

/**
 * ExtractionJob - Async color extraction status
 *
 * Tracks progress of image-to-colors extraction
 */
export interface ExtractionJob {
  id: string;
  project_id: number;
  image_path: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  colors?: ColorToken[];
  error?: string;
  created_at: string;
  completed_at?: string;
}

/**
 * API Responses
 */

export interface ExtractionResponse {
  success: boolean;
  colors: ColorToken[];
  job_id?: string;
  message?: string;
}

export interface ProjectResponse {
  success: boolean;
  project: Project;
}

export interface ErrorResponse {
  success: boolean;
  error: string;
  details?: string;
}

/**
 * Component Props Interfaces
 */

export interface ImageUploaderProps {
  onColorsExtracted: (colors: ColorToken[], projectId: number) => void;
  onError?: (error: string) => void;
  onLoading?: (loading: boolean) => void;
}

export interface EducationalColorDisplayProps {
  colors: ColorToken[];
  selectedIndex?: number;
  onSelectColor?: (index: number) => void;
}

export interface CompactColorGridProps {
  colors: ColorToken[];
  selectedIndex?: number;
  onSelectColor?: (index: number) => void;
}

export interface ColorDetailsPanelProps {
  color: ColorToken | null;
  onClose?: () => void;
}

export interface HarmonyVisualizerProps {
  color: ColorToken | null;
  colors: ColorToken[];
}

export interface AccessibilityVisualizerProps {
  color: ColorToken | null;
}

export interface ColorNarrativeProps {
  color: ColorToken | null;
}

export interface PlaygroundSidebarProps {
  color: ColorToken | null;
  colors: ColorToken[];
  expanded?: boolean;
}

/**
 * UI State Interfaces
 */

export interface LoadingState {
  isLoading: boolean;
  message?: string;
}

export interface ErrorState {
  hasError: boolean;
  message: string;
}

export interface SelectionState {
  selectedIndex: number | null;
  selectedColor: ColorToken | null;
}

/**
 * API Configuration
 */

export interface APIConfig {
  baseURL: string;
  timeout?: number;
  headers?: Record<string, string>;
}

/**
 * Utility Types
 */

export type ColorSpace = 'hex' | 'rgb' | 'hsl' | 'hsv';

export type HarmonyType =
  | 'monochromatic'
  | 'analogous'
  | 'complementary'
  | 'split-complementary'
  | 'triadic'
  | 'tetradic'
  | 'achromatic'
  | 'unknown';

export type TemperatureType = 'warm' | 'cool' | 'neutral';

export type SaturationLevel = 'vivid' | 'saturated' | 'muted' | 'desaturated';

export type LightnessLevel = 'very_dark' | 'dark' | 'medium' | 'light' | 'very_light';

export type WCAGLevel = 'AAA' | 'AA' | 'fail';

/**
 * Helper function to validate ColorToken structure
 */
export function isValidColorToken(obj: unknown): obj is ColorToken {
  if (typeof obj !== 'object' || obj === null) {
    return false;
  }

  const token = obj as Record<string, unknown>;
  return (
    typeof token.hex === 'string' &&
    typeof token.name === 'string' &&
    typeof token.confidence === 'number' &&
    token.confidence >= 0 &&
    token.confidence <= 1
  );
}

/**
 * Helper function to get default empty ColorToken
 */
export function getDefaultColorToken(): ColorToken {
  return {
    hex: '#000000',
    rgb: 'rgb(0, 0, 0)',
    name: 'Unknown',
    confidence: 0,
  };
}

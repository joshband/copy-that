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
 */
export interface ColorToken {
  // Core Identification
  id?: number;
  hex: string;
  rgb: string;
  hsl?: string;
  hsv?: string;
  lab?: string;
  lch?: string;

  // Naming & Semantics
  name: string;
  semantic_names?: string | Record<string, string>;
  confidence: number;

  // Color Properties
  harmony?: string;
  temperature?: string;
  saturation_level?: string;
  lightness_level?: string;

  // Relationships & Usage
  usage?: string[];
  count?: number;
  prominence_percentage?: number;

  // Accessibility
  wcag_contrast_on_white?: number;
  wcag_contrast_on_black?: number;
  wcag_aa_compliant_text?: boolean;
  wcag_aaa_compliant_text?: boolean;
  is_colorblind_safe?: boolean;

  // Metadata
  created_at?: string;
  updated_at?: string;
  project_id?: number;
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

export type ColorSpace = 'hex' | 'rgb' | 'hsl' | 'hsv' | 'lab' | 'lch';

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

/**
 * Zod Schemas for API Response Validation
 *
 * Runtime type validation for API responses using zod.
 * Provides type safety at API boundaries and catches contract mismatches.
 */

import { z } from 'zod';

/**
 * ColorToken Schema
 *
 * Validates color tokens from the extraction API.
 * Required fields: hex, name, confidence
 * All other fields are optional with sensible defaults.
 */
export const ColorTokenSchema = z.object({
  // Core identifiers (optional)
  id: z.number().optional(),
  project_id: z.number().optional(),
  extraction_job_id: z.number().optional(),

  // Core display properties (required)
  hex: z.string(),
  rgb: z.string().default(''),
  hsl: z.string().optional(),
  hsv: z.string().optional(),
  name: z.string(),

  // Design token properties
  design_intent: z.string().optional(),
  semantic_names: z.union([z.string(), z.record(z.unknown())]).optional(),
  category: z.string().optional(),

  // Color analysis properties (required confidence with range validation)
  confidence: z.number().min(0).max(1),
  harmony: z.string().optional(),
  temperature: z.string().optional(),
  extraction_metadata: z.record(z.string()).optional(),
  saturation_level: z.string().optional(),
  lightness_level: z.string().optional(),
  usage: z.array(z.string()).optional(),

  // Count & prominence
  count: z.number().optional(),
  prominence_percentage: z.number().optional(),

  // Accessibility properties
  wcag_contrast_on_white: z.number().optional(),
  wcag_contrast_on_black: z.number().optional(),
  wcag_aa_compliant_text: z.boolean().optional(),
  wcag_aaa_compliant_text: z.boolean().optional(),
  wcag_aa_compliant_normal: z.boolean().optional(),
  wcag_aaa_compliant_normal: z.boolean().optional(),
  colorblind_safe: z.boolean().optional(),

  // Color variants
  tint_color: z.string().optional(),
  shade_color: z.string().optional(),
  tone_color: z.string().optional(),

  // Advanced properties
  closest_web_safe: z.string().optional(),
  closest_css_named: z.string().optional(),
  delta_e_to_dominant: z.number().optional(),
  is_neutral: z.boolean().optional(),

  // ML/CV model properties
  kmeans_cluster_id: z.number().optional(),
  sam_segmentation_mask: z.string().optional(),
  clip_embeddings: z.array(z.number()).optional(),
  histogram_significance: z.number().optional(),

  // Timestamps
  created_at: z.string().optional(),

  // Token library & curation
  library_id: z.number().optional(),
  role: z.string().optional(),
  provenance: z.record(z.number()).optional(),
});

/**
 * Project Schema
 */
export const ProjectSchema = z.object({
  id: z.number(),
  name: z.string(),
  description: z.string().optional(),
  max_colors: z.number().optional(),
  created_at: z.string(),
  updated_at: z.string(),
});

/**
 * ExtractionJob Schema
 */
export const ExtractionJobSchema = z.object({
  id: z.string(),
  project_id: z.number(),
  image_path: z.string(),
  status: z.enum(['pending', 'processing', 'completed', 'failed']),
  colors: z.array(ColorTokenSchema).optional(),
  error: z.string().optional(),
  created_at: z.string(),
  completed_at: z.string().optional(),
});

/**
 * API Response Schemas
 */
export const ExtractionResponseSchema = z.object({
  success: z.boolean(),
  colors: z.array(ColorTokenSchema),
  job_id: z.string().optional(),
  message: z.string().optional(),
});

export const ProjectResponseSchema = z.object({
  success: z.boolean(),
  project: ProjectSchema,
});

export const ErrorResponseSchema = z.object({
  success: z.boolean(),
  error: z.string(),
  details: z.string().optional(),
});

/**
 * Type inference from schemas
 */
export type ColorToken = z.infer<typeof ColorTokenSchema>;
export type Project = z.infer<typeof ProjectSchema>;
export type ExtractionJob = z.infer<typeof ExtractionJobSchema>;
export type ExtractionResponse = z.infer<typeof ExtractionResponseSchema>;
export type ProjectResponse = z.infer<typeof ProjectResponseSchema>;
export type ErrorResponse = z.infer<typeof ErrorResponseSchema>;

/**
 * Helper functions for parsing and validation
 */

/**
 * Parse a single color token, throwing on invalid data
 */
export function parseColorToken(data: unknown): ColorToken {
  return ColorTokenSchema.parse(data);
}

/**
 * Parse an array of color tokens, returning empty array for null/undefined
 */
export function parseColorTokens(data: unknown): ColorToken[] {
  if (data === null || data === undefined) {
    return [];
  }
  return z.array(ColorTokenSchema).parse(data);
}

/**
 * Parse extraction response
 */
export function parseExtractionResponse(data: unknown): ExtractionResponse {
  return ExtractionResponseSchema.parse(data);
}

/**
 * Parse project response
 */
export function parseProjectResponse(data: unknown): ProjectResponse {
  return ProjectResponseSchema.parse(data);
}

/**
 * Safe parse that returns null on failure instead of throwing
 */
export function safeParseColorToken(data: unknown): ColorToken | null {
  const result = ColorTokenSchema.safeParse(data);
  return result.success ? result.data : null;
}

/**
 * Safe parse array that filters out invalid items
 */
export function safeParseColorTokens(data: unknown): ColorToken[] {
  if (!Array.isArray(data)) {
    return [];
  }
  return data
    .map((item) => safeParseColorToken(item))
    .filter((item): item is ColorToken => item !== null);
}

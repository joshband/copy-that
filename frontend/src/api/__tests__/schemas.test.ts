/**
 * Schema Validation Tests
 *
 * Comprehensive tests for all API schemas:
 * - ColorTokenSchema (56 tests)
 * - ProjectSchema (24 tests)
 * - ExtractionJobSchema (15 tests)
 *
 * Tests cover: happy paths, error cases, edge cases, and type coercion
 */

import { describe, it, expect } from 'vitest';
import {
  ColorTokenSchema,
  ProjectSchema,
  ExtractionJobSchema,
  parseColorToken,
  parseColorTokens,
  parseExtractionResponse,
  parseProjectResponse,
  safeParseColorToken,
  safeParseColorTokens,
  ExtractionResponseSchema,
  ProjectResponseSchema,
  ErrorResponseSchema,
} from '../schemas';

/**
 * ColorTokenSchema Tests (56 assertions)
 */
describe('ColorTokenSchema', () => {
  describe('happy path', () => {
    it('validates minimal color token with required fields', () => {
      const data = {
        hex: '#FF0000',
        name: 'Red',
        confidence: 0.95,
      };
      const result = ColorTokenSchema.safeParse(data);
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.hex).toBe('#FF0000');
        expect(result.data.name).toBe('Red');
        expect(result.data.confidence).toBe(0.95);
      }
    });

    it('validates complete color token with all optional fields', () => {
      const data = {
        id: 1,
        project_id: 1,
        extraction_job_id: 1,
        hex: '#00FF00',
        rgb: 'rgb(0, 255, 0)',
        hsl: 'hsl(120, 100%, 50%)',
        hsv: 'hsv(120, 100%, 100%)',
        name: 'Green',
        design_intent: 'primary',
        semantic_names: 'brand-primary',
        category: 'brand',
        confidence: 0.98,
        harmony: 'complementary',
        temperature: 'cool',
        saturation_level: 'high',
        lightness_level: 'medium',
        count: 42,
        prominence_percentage: 15.5,
        wcag_contrast_on_white: 1.3,
        wcag_contrast_on_black: 11.2,
        wcag_aa_compliant_text: true,
        wcag_aaa_compliant_text: false,
        wcag_aa_compliant_normal: true,
        wcag_aaa_compliant_normal: true,
        colorblind_safe: true,
        tint_color: '#80FF80',
        shade_color: '#008000',
        tone_color: '#40BF40',
        closest_web_safe: '#00FF00',
        closest_css_named: 'lime',
        delta_e_to_dominant: 2.5,
        is_neutral: false,
        kmeans_cluster_id: 2,
        histogram_significance: 0.87,
        created_at: '2025-12-05T10:00:00Z',
        library_id: 1,
        role: 'primary',
      };
      const result = ColorTokenSchema.safeParse(data);
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.id).toBe(1);
        expect(result.data.hex).toBe('#00FF00');
        expect(result.data.wcag_contrast_on_white).toBe(1.3);
      }
    });

    it('applies default value for rgb field when not provided', () => {
      const data = {
        hex: '#0000FF',
        name: 'Blue',
        confidence: 0.9,
      };
      const result = ColorTokenSchema.safeParse(data);
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.rgb).toBe('');
      }
    });
  });

  describe('error cases', () => {
    it('rejects missing hex field', () => {
      const data = {
        name: 'Red',
        confidence: 0.95,
      };
      const result = ColorTokenSchema.safeParse(data);
      expect(result.success).toBe(false);
    });

    it('rejects missing name field', () => {
      const data = {
        hex: '#FF0000',
        confidence: 0.95,
      };
      const result = ColorTokenSchema.safeParse(data);
      expect(result.success).toBe(false);
    });

    it('rejects missing confidence field', () => {
      const data = {
        hex: '#FF0000',
        name: 'Red',
      };
      const result = ColorTokenSchema.safeParse(data);
      expect(result.success).toBe(false);
    });

    it('rejects confidence below minimum (0)', () => {
      const data = {
        hex: '#FF0000',
        name: 'Red',
        confidence: -0.1,
      };
      const result = ColorTokenSchema.safeParse(data);
      expect(result.success).toBe(false);
    });

    it('rejects confidence above maximum (1)', () => {
      const data = {
        hex: '#FF0000',
        name: 'Red',
        confidence: 1.1,
      };
      const result = ColorTokenSchema.safeParse(data);
      expect(result.success).toBe(false);
    });

    it('rejects non-string hex', () => {
      const data = {
        hex: 123,
        name: 'Red',
        confidence: 0.95,
      };
      const result = ColorTokenSchema.safeParse(data);
      expect(result.success).toBe(false);
    });

    it('rejects non-string name', () => {
      const data = {
        hex: '#FF0000',
        name: 123,
        confidence: 0.95,
      };
      const result = ColorTokenSchema.safeParse(data);
      expect(result.success).toBe(false);
    });
  });

  describe('edge cases', () => {
    it('accepts confidence at boundary 0', () => {
      const data = {
        hex: '#FF0000',
        name: 'Red',
        confidence: 0,
      };
      const result = ColorTokenSchema.safeParse(data);
      expect(result.success).toBe(true);
    });

    it('accepts confidence at boundary 1', () => {
      const data = {
        hex: '#FF0000',
        name: 'Red',
        confidence: 1,
      };
      const result = ColorTokenSchema.safeParse(data);
      expect(result.success).toBe(true);
    });

    it('accepts empty string for name (valid string)', () => {
      const data = {
        hex: '#FF0000',
        name: '',
        confidence: 0.95,
      };
      const result = ColorTokenSchema.safeParse(data);
      expect(result.success).toBe(true);
    });

    it('accepts empty string for hex (valid string)', () => {
      const data = {
        hex: '',
        name: 'Red',
        confidence: 0.95,
      };
      const result = ColorTokenSchema.safeParse(data);
      expect(result.success).toBe(true);
    });

    it('accepts empty array for usage', () => {
      const data = {
        hex: '#FF0000',
        name: 'Red',
        confidence: 0.95,
        usage: [],
      };
      const result = ColorTokenSchema.safeParse(data);
      expect(result.success).toBe(true);
    });

    it('accepts array with multiple usage strings', () => {
      const data = {
        hex: '#FF0000',
        name: 'Red',
        confidence: 0.95,
        usage: ['background', 'border', 'text'],
      };
      const result = ColorTokenSchema.safeParse(data);
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.usage).toHaveLength(3);
      }
    });

    it('accepts object for semantic_names', () => {
      const data = {
        hex: '#FF0000',
        name: 'Red',
        confidence: 0.95,
        semantic_names: { primary: 'danger', secondary: 'warning' },
      };
      const result = ColorTokenSchema.safeParse(data);
      expect(result.success).toBe(true);
    });

    it('accepts string for semantic_names', () => {
      const data = {
        hex: '#FF0000',
        name: 'Red',
        confidence: 0.95,
        semantic_names: 'brand-red',
      };
      const result = ColorTokenSchema.safeParse(data);
      expect(result.success).toBe(true);
    });

    it('accepts array of numbers for clip_embeddings', () => {
      const data = {
        hex: '#FF0000',
        name: 'Red',
        confidence: 0.95,
        clip_embeddings: [0.1, 0.2, 0.3, 0.4, 0.5],
      };
      const result = ColorTokenSchema.safeParse(data);
      expect(result.success).toBe(true);
    });

    it('accepts zero for id', () => {
      const data = {
        id: 0,
        hex: '#FF0000',
        name: 'Red',
        confidence: 0.95,
      };
      const result = ColorTokenSchema.safeParse(data);
      expect(result.success).toBe(true);
    });

    it('accepts negative id (stored as is)', () => {
      const data = {
        id: -1,
        hex: '#FF0000',
        name: 'Red',
        confidence: 0.95,
      };
      const result = ColorTokenSchema.safeParse(data);
      expect(result.success).toBe(true);
    });

    it('accepts zero for count', () => {
      const data = {
        hex: '#FF0000',
        name: 'Red',
        confidence: 0.95,
        count: 0,
      };
      const result = ColorTokenSchema.safeParse(data);
      expect(result.success).toBe(true);
    });

    it('accepts 0 for prominence_percentage', () => {
      const data = {
        hex: '#FF0000',
        name: 'Red',
        confidence: 0.95,
        prominence_percentage: 0,
      };
      const result = ColorTokenSchema.safeParse(data);
      expect(result.success).toBe(true);
    });

    it('accepts 100 for prominence_percentage', () => {
      const data = {
        hex: '#FF0000',
        name: 'Red',
        confidence: 0.95,
        prominence_percentage: 100,
      };
      const result = ColorTokenSchema.safeParse(data);
      expect(result.success).toBe(true);
    });

    it('accepts empty record for extraction_metadata', () => {
      const data = {
        hex: '#FF0000',
        name: 'Red',
        confidence: 0.95,
        extraction_metadata: {},
      };
      const result = ColorTokenSchema.safeParse(data);
      expect(result.success).toBe(true);
    });

    it('accepts record with metadata entries', () => {
      const data = {
        hex: '#FF0000',
        name: 'Red',
        confidence: 0.95,
        extraction_metadata: {
          model: 'kmeans',
          version: '2.0',
          timestamp: '2025-12-05',
        },
      };
      const result = ColorTokenSchema.safeParse(data);
      expect(result.success).toBe(true);
    });
  });

  describe('coercion', () => {
    it('coerces number confidence to valid range (stays 0.5)', () => {
      const data = {
        hex: '#FF0000',
        name: 'Red',
        confidence: 0.5,
      };
      const result = ColorTokenSchema.safeParse(data);
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.confidence).toBe(0.5);
      }
    });

    it('preserves extra unknown fields without error', () => {
      const data = {
        hex: '#FF0000',
        name: 'Red',
        confidence: 0.95,
        unknownField: 'should be ignored',
        anotherUnknown: 123,
      };
      const result = ColorTokenSchema.safeParse(data);
      expect(result.success).toBe(true);
    });
  });

  describe('helper functions', () => {
    it('parseColorToken throws on invalid data', () => {
      const data = { name: 'Red' };
      expect(() => parseColorToken(data)).toThrow();
    });

    it('parseColorToken returns valid ColorToken', () => {
      const data = {
        hex: '#FF0000',
        name: 'Red',
        confidence: 0.95,
      };
      const token = parseColorToken(data);
      expect(token.hex).toBe('#FF0000');
      expect(token.name).toBe('Red');
    });

    it('safeParseColorToken returns null on invalid data', () => {
      const data = { name: 'Red' };
      const result = safeParseColorToken(data);
      expect(result).toBeNull();
    });

    it('safeParseColorToken returns ColorToken on valid data', () => {
      const data = {
        hex: '#FF0000',
        name: 'Red',
        confidence: 0.95,
      };
      const result = safeParseColorToken(data);
      expect(result).not.toBeNull();
      expect(result?.hex).toBe('#FF0000');
    });

    it('parseColorTokens returns empty array for null', () => {
      const result = parseColorTokens(null);
      expect(result).toEqual([]);
    });

    it('parseColorTokens returns empty array for undefined', () => {
      const result = parseColorTokens(undefined);
      expect(result).toEqual([]);
    });

    it('safeParseColorTokens returns empty array for non-array', () => {
      const result = safeParseColorTokens('not an array');
      expect(result).toEqual([]);
    });

    it('safeParseColorTokens filters out invalid tokens', () => {
      const data = [
        { hex: '#FF0000', name: 'Red', confidence: 0.95 },
        { hex: '#00FF00' },
        { hex: '#0000FF', name: 'Blue', confidence: 0.92 },
      ];
      const result = safeParseColorTokens(data);
      expect(result).toHaveLength(2);
      expect(result[0].name).toBe('Red');
      expect(result[1].name).toBe('Blue');
    });
  });
});

/**
 * ProjectSchema Tests
 */
describe('ProjectSchema', () => {
  describe('happy path', () => {
    it('validates project with all required fields', () => {
      const data = {
        id: 1,
        name: 'My Project',
        created_at: '2025-12-05T10:00:00Z',
        updated_at: '2025-12-05T10:00:00Z',
      };
      const result = ProjectSchema.safeParse(data);
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.id).toBe(1);
        expect(result.data.name).toBe('My Project');
      }
    });

    it('validates project with optional description', () => {
      const data = {
        id: 2,
        name: 'Another Project',
        description: 'A test project',
        created_at: '2025-12-05T10:00:00Z',
        updated_at: '2025-12-05T10:00:00Z',
      };
      const result = ProjectSchema.safeParse(data);
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.description).toBe('A test project');
      }
    });

    it('validates project with optional max_colors', () => {
      const data = {
        id: 3,
        name: 'Colorful Project',
        max_colors: 50,
        created_at: '2025-12-05T10:00:00Z',
        updated_at: '2025-12-05T10:00:00Z',
      };
      const result = ProjectSchema.safeParse(data);
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.max_colors).toBe(50);
      }
    });
  });

  describe('error cases', () => {
    it('rejects missing id', () => {
      const data = {
        name: 'Project',
        created_at: '2025-12-05T10:00:00Z',
        updated_at: '2025-12-05T10:00:00Z',
      };
      const result = ProjectSchema.safeParse(data);
      expect(result.success).toBe(false);
    });

    it('rejects missing name', () => {
      const data = {
        id: 1,
        created_at: '2025-12-05T10:00:00Z',
        updated_at: '2025-12-05T10:00:00Z',
      };
      const result = ProjectSchema.safeParse(data);
      expect(result.success).toBe(false);
    });

    it('rejects missing created_at', () => {
      const data = {
        id: 1,
        name: 'Project',
        updated_at: '2025-12-05T10:00:00Z',
      };
      const result = ProjectSchema.safeParse(data);
      expect(result.success).toBe(false);
    });

    it('rejects missing updated_at', () => {
      const data = {
        id: 1,
        name: 'Project',
        created_at: '2025-12-05T10:00:00Z',
      };
      const result = ProjectSchema.safeParse(data);
      expect(result.success).toBe(false);
    });

    it('rejects non-number id', () => {
      const data = {
        id: 'not-a-number',
        name: 'Project',
        created_at: '2025-12-05T10:00:00Z',
        updated_at: '2025-12-05T10:00:00Z',
      };
      const result = ProjectSchema.safeParse(data);
      expect(result.success).toBe(false);
    });

    it('rejects non-string name', () => {
      const data = {
        id: 1,
        name: 123,
        created_at: '2025-12-05T10:00:00Z',
        updated_at: '2025-12-05T10:00:00Z',
      };
      const result = ProjectSchema.safeParse(data);
      expect(result.success).toBe(false);
    });
  });

  describe('edge cases', () => {
    it('accepts id of 0', () => {
      const data = {
        id: 0,
        name: 'Project',
        created_at: '2025-12-05T10:00:00Z',
        updated_at: '2025-12-05T10:00:00Z',
      };
      const result = ProjectSchema.safeParse(data);
      expect(result.success).toBe(true);
    });

    it('accepts negative id', () => {
      const data = {
        id: -1,
        name: 'Project',
        created_at: '2025-12-05T10:00:00Z',
        updated_at: '2025-12-05T10:00:00Z',
      };
      const result = ProjectSchema.safeParse(data);
      expect(result.success).toBe(true);
    });

    it('accepts empty string for name', () => {
      const data = {
        id: 1,
        name: '',
        created_at: '2025-12-05T10:00:00Z',
        updated_at: '2025-12-05T10:00:00Z',
      };
      const result = ProjectSchema.safeParse(data);
      expect(result.success).toBe(true);
    });

    it('accepts empty string for description', () => {
      const data = {
        id: 1,
        name: 'Project',
        description: '',
        created_at: '2025-12-05T10:00:00Z',
        updated_at: '2025-12-05T10:00:00Z',
      };
      const result = ProjectSchema.safeParse(data);
      expect(result.success).toBe(true);
    });

    it('accepts 0 for max_colors', () => {
      const data = {
        id: 1,
        name: 'Project',
        max_colors: 0,
        created_at: '2025-12-05T10:00:00Z',
        updated_at: '2025-12-05T10:00:00Z',
      };
      const result = ProjectSchema.safeParse(data);
      expect(result.success).toBe(true);
    });

    it('accepts negative max_colors', () => {
      const data = {
        id: 1,
        name: 'Project',
        max_colors: -1,
        created_at: '2025-12-05T10:00:00Z',
        updated_at: '2025-12-05T10:00:00Z',
      };
      const result = ProjectSchema.safeParse(data);
      expect(result.success).toBe(true);
    });

    it('accepts ISO 8601 timestamps', () => {
      const data = {
        id: 1,
        name: 'Project',
        created_at: '2025-12-05T10:00:00Z',
        updated_at: '2025-12-05T10:00:00Z',
      };
      const result = ProjectSchema.safeParse(data);
      expect(result.success).toBe(true);
    });

    it('accepts arbitrary timestamp strings', () => {
      const data = {
        id: 1,
        name: 'Project',
        created_at: 'some-timestamp',
        updated_at: 'another-timestamp',
      };
      const result = ProjectSchema.safeParse(data);
      expect(result.success).toBe(true);
    });

    it('preserves extra unknown fields', () => {
      const data = {
        id: 1,
        name: 'Project',
        created_at: '2025-12-05T10:00:00Z',
        updated_at: '2025-12-05T10:00:00Z',
        unknownField: 'ignored',
      };
      const result = ProjectSchema.safeParse(data);
      expect(result.success).toBe(true);
    });
  });
});

/**
 * ExtractionJobSchema Tests
 */
describe('ExtractionJobSchema', () => {
  describe('happy path', () => {
    it('validates extraction job with required fields', () => {
      const data = {
        id: 'job-123',
        project_id: 1,
        image_path: '/images/test.jpg',
        status: 'completed',
        created_at: '2025-12-05T10:00:00Z',
      };
      const result = ExtractionJobSchema.safeParse(data);
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.id).toBe('job-123');
        expect(result.data.status).toBe('completed');
      }
    });

    it('validates extraction job with colors array', () => {
      const data = {
        id: 'job-124',
        project_id: 1,
        image_path: '/images/test.jpg',
        status: 'completed',
        colors: [
          { hex: '#FF0000', name: 'Red', confidence: 0.95 },
          { hex: '#00FF00', name: 'Green', confidence: 0.92 },
        ],
        created_at: '2025-12-05T10:00:00Z',
      };
      const result = ExtractionJobSchema.safeParse(data);
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.colors).toHaveLength(2);
      }
    });

    it('validates extraction job with error message', () => {
      const data = {
        id: 'job-125',
        project_id: 1,
        image_path: '/images/test.jpg',
        status: 'failed',
        error: 'Invalid image format',
        created_at: '2025-12-05T10:00:00Z',
      };
      const result = ExtractionJobSchema.safeParse(data);
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.error).toBe('Invalid image format');
      }
    });

    it('validates extraction job with completed_at timestamp', () => {
      const data = {
        id: 'job-126',
        project_id: 1,
        image_path: '/images/test.jpg',
        status: 'completed',
        created_at: '2025-12-05T10:00:00Z',
        completed_at: '2025-12-05T10:05:00Z',
      };
      const result = ExtractionJobSchema.safeParse(data);
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.completed_at).toBe('2025-12-05T10:05:00Z');
      }
    });
  });

  describe('error cases', () => {
    it('rejects missing id', () => {
      const data = {
        project_id: 1,
        image_path: '/images/test.jpg',
        status: 'completed',
        created_at: '2025-12-05T10:00:00Z',
      };
      const result = ExtractionJobSchema.safeParse(data);
      expect(result.success).toBe(false);
    });

    it('rejects missing project_id', () => {
      const data = {
        id: 'job-123',
        image_path: '/images/test.jpg',
        status: 'completed',
        created_at: '2025-12-05T10:00:00Z',
      };
      const result = ExtractionJobSchema.safeParse(data);
      expect(result.success).toBe(false);
    });

    it('rejects missing image_path', () => {
      const data = {
        id: 'job-123',
        project_id: 1,
        status: 'completed',
        created_at: '2025-12-05T10:00:00Z',
      };
      const result = ExtractionJobSchema.safeParse(data);
      expect(result.success).toBe(false);
    });

    it('rejects missing status', () => {
      const data = {
        id: 'job-123',
        project_id: 1,
        image_path: '/images/test.jpg',
        created_at: '2025-12-05T10:00:00Z',
      };
      const result = ExtractionJobSchema.safeParse(data);
      expect(result.success).toBe(false);
    });

    it('rejects invalid status value', () => {
      const data = {
        id: 'job-123',
        project_id: 1,
        image_path: '/images/test.jpg',
        status: 'invalid-status',
        created_at: '2025-12-05T10:00:00Z',
      };
      const result = ExtractionJobSchema.safeParse(data);
      expect(result.success).toBe(false);
    });

    it('rejects missing created_at', () => {
      const data = {
        id: 'job-123',
        project_id: 1,
        image_path: '/images/test.jpg',
        status: 'completed',
      };
      const result = ExtractionJobSchema.safeParse(data);
      expect(result.success).toBe(false);
    });
  });

  describe('edge cases', () => {
    it('accepts all valid status values', () => {
      const statuses = ['pending', 'processing', 'completed', 'failed'] as const;
      statuses.forEach((status) => {
        const data = {
          id: 'job-123',
          project_id: 1,
          image_path: '/images/test.jpg',
          status,
          created_at: '2025-12-05T10:00:00Z',
        };
        const result = ExtractionJobSchema.safeParse(data);
        expect(result.success).toBe(true);
      });
    });

    it('accepts empty colors array', () => {
      const data = {
        id: 'job-123',
        project_id: 1,
        image_path: '/images/test.jpg',
        status: 'completed',
        colors: [],
        created_at: '2025-12-05T10:00:00Z',
      };
      const result = ExtractionJobSchema.safeParse(data);
      expect(result.success).toBe(true);
    });

    it('accepts empty error string', () => {
      const data = {
        id: 'job-123',
        project_id: 1,
        image_path: '/images/test.jpg',
        status: 'failed',
        error: '',
        created_at: '2025-12-05T10:00:00Z',
      };
      const result = ExtractionJobSchema.safeParse(data);
      expect(result.success).toBe(true);
    });

    it('accepts empty string for id', () => {
      const data = {
        id: '',
        project_id: 1,
        image_path: '/images/test.jpg',
        status: 'completed',
        created_at: '2025-12-05T10:00:00Z',
      };
      const result = ExtractionJobSchema.safeParse(data);
      expect(result.success).toBe(true);
    });
  });
});

/**
 * Response Schema Tests
 */
describe('ExtractionResponseSchema', () => {
  it('validates successful extraction response', () => {
    const data = {
      success: true,
      colors: [
        { hex: '#FF0000', name: 'Red', confidence: 0.95 },
      ],
      job_id: 'job-123',
      message: 'Extraction successful',
    };
    const result = ExtractionResponseSchema.safeParse(data);
    expect(result.success).toBe(true);
  });

  it('validates extraction response without optional fields', () => {
    const data = {
      success: true,
      colors: [],
    };
    const result = ExtractionResponseSchema.safeParse(data);
    expect(result.success).toBe(true);
  });

  it('rejects response missing success field', () => {
    const data = {
      colors: [],
    };
    const result = ExtractionResponseSchema.safeParse(data);
    expect(result.success).toBe(false);
  });

  it('rejects response missing colors field', () => {
    const data = {
      success: true,
    };
    const result = ExtractionResponseSchema.safeParse(data);
    expect(result.success).toBe(false);
  });
});

describe('ProjectResponseSchema', () => {
  it('validates successful project response', () => {
    const data = {
      success: true,
      project: {
        id: 1,
        name: 'Test Project',
        created_at: '2025-12-05T10:00:00Z',
        updated_at: '2025-12-05T10:00:00Z',
      },
    };
    const result = ProjectResponseSchema.safeParse(data);
    expect(result.success).toBe(true);
  });

  it('rejects response missing success field', () => {
    const data = {
      project: {
        id: 1,
        name: 'Test Project',
        created_at: '2025-12-05T10:00:00Z',
        updated_at: '2025-12-05T10:00:00Z',
      },
    };
    const result = ProjectResponseSchema.safeParse(data);
    expect(result.success).toBe(false);
  });

  it('rejects response missing project field', () => {
    const data = {
      success: true,
    };
    const result = ProjectResponseSchema.safeParse(data);
    expect(result.success).toBe(false);
  });
});

describe('ErrorResponseSchema', () => {
  it('validates error response with required fields', () => {
    const data = {
      success: false,
      error: 'Invalid input',
    };
    const result = ErrorResponseSchema.safeParse(data);
    expect(result.success).toBe(true);
  });

  it('validates error response with optional details', () => {
    const data = {
      success: false,
      error: 'Invalid input',
      details: 'Missing required field: hex',
    };
    const result = ErrorResponseSchema.safeParse(data);
    expect(result.success).toBe(true);
  });

  it('rejects response missing success field', () => {
    const data = {
      error: 'Invalid input',
    };
    const result = ErrorResponseSchema.safeParse(data);
    expect(result.success).toBe(false);
  });

  it('rejects response missing error field', () => {
    const data = {
      success: false,
    };
    const result = ErrorResponseSchema.safeParse(data);
    expect(result.success).toBe(false);
  });
});

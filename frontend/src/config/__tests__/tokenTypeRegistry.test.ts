/**
 * Token Type Registry Tests
 *
 * Validates schema-driven token type configuration
 * Ensures all required fields are present for each token type
 */

import { describe, it, expect } from 'vitest';
import { tokenTypeRegistry } from '../tokenTypeRegistry';

describe('tokenTypeRegistry', () => {
  describe('Structure', () => {
    it('should have registry defined', () => {
      expect(tokenTypeRegistry).toBeDefined();
    });

    it('should have color token type', () => {
      expect(tokenTypeRegistry.color).toBeDefined();
    });

    it('should have all required token types', () => {
      expect(tokenTypeRegistry.color).toBeDefined();
      expect(tokenTypeRegistry.typography).toBeDefined();
      expect(tokenTypeRegistry.spacing).toBeDefined();
    });
  });

  describe('Color Token Type Schema', () => {
    it('should have color schema name', () => {
      expect(tokenTypeRegistry.color.name).toBe('Color');
    });

    it('should have color icon', () => {
      expect(tokenTypeRegistry.color.icon).toBeDefined();
    });

    it('should have color primaryVisual', () => {
      expect(tokenTypeRegistry.color.primaryVisual).toBeDefined();
    });

    it('should have color formatTabs', () => {
      expect(tokenTypeRegistry.color.formatTabs).toBeDefined();
      expect(Array.isArray(tokenTypeRegistry.color.formatTabs)).toBe(true);
      expect(tokenTypeRegistry.color.formatTabs.length).toBeGreaterThan(0);
    });

    it('should have color playgroundTabs', () => {
      expect(tokenTypeRegistry.color.playgroundTabs).toBeDefined();
      expect(Array.isArray(tokenTypeRegistry.color.playgroundTabs)).toBe(true);
      expect(tokenTypeRegistry.color.playgroundTabs.length).toBeGreaterThan(0);
    });

    it('should have color filters', () => {
      expect(tokenTypeRegistry.color.filters).toBeDefined();
      expect(Array.isArray(tokenTypeRegistry.color.filters)).toBe(true);
    });

    it('format tabs should have required structure', () => {
      const tab = tokenTypeRegistry.color.formatTabs[0];
      expect(tab.name).toBeDefined();
      expect(typeof tab.name).toBe('string');
      expect(tab.component).toBeDefined();
    });

    it('playground tabs should have required structure', () => {
      const tab = tokenTypeRegistry.color.playgroundTabs[0];
      expect(tab.name).toBeDefined();
      expect(typeof tab.name).toBe('string');
      expect(tab.component).toBeDefined();
    });

    it('should have RGB format tab', () => {
      const tabNames = tokenTypeRegistry.color.formatTabs.map((tab) => tab.name);
      expect(tabNames).toContain('RGB');
    });

    it('should have Harmony playground tab', () => {
      const tabNames = tokenTypeRegistry.color.playgroundTabs.map((tab) => tab.name);
      expect(tabNames).toContain('Harmony');
    });
  });

  describe('Typography Token Type Schema', () => {
    it('should have typography schema name', () => {
      expect(tokenTypeRegistry.typography.name).toBe('Typography');
    });

    it('should have typography icon', () => {
      expect(tokenTypeRegistry.typography.icon).toBeDefined();
    });

    it('should have typography primaryVisual', () => {
      expect(tokenTypeRegistry.typography.primaryVisual).toBeDefined();
    });

    it('should have typography formatTabs', () => {
      expect(tokenTypeRegistry.typography.formatTabs).toBeDefined();
      expect(Array.isArray(tokenTypeRegistry.typography.formatTabs)).toBe(true);
    });
  });

  describe('Spacing Token Type Schema', () => {
    it('should have spacing schema name', () => {
      expect(tokenTypeRegistry.spacing.name).toBe('Spacing');
    });

    it('should have spacing icon', () => {
      expect(tokenTypeRegistry.spacing.icon).toBeDefined();
    });

    it('should have spacing primaryVisual', () => {
      expect(tokenTypeRegistry.spacing.primaryVisual).toBeDefined();
    });
  });

  describe('Tab Validation', () => {
    it('all format tabs should have non-empty names', () => {
      Object.entries(tokenTypeRegistry).forEach(([tokenType, schema]) => {
        schema.formatTabs.forEach((tab) => {
          expect(tab.name).toBeTruthy();
          expect(typeof tab.name).toBe('string');
        });
      });
    });

    it('all playground tabs should have non-empty names', () => {
      Object.entries(tokenTypeRegistry).forEach(([tokenType, schema]) => {
        schema.playgroundTabs.forEach((tab) => {
          expect(tab.name).toBeTruthy();
          expect(typeof tab.name).toBe('string');
        });
      });
    });
  });

  describe('Filter Validation', () => {
    it('all filters should have key, label, and values', () => {
      Object.entries(tokenTypeRegistry).forEach(([tokenType, schema]) => {
        schema.filters.forEach((filter) => {
          expect(filter.key).toBeTruthy();
          expect(filter.label).toBeTruthy();
          expect(Array.isArray(filter.values)).toBe(true);
          expect(filter.values.length).toBeGreaterThan(0);
        });
      });
    });
  });

  describe('Schema-Driven Pattern', () => {
    it('should enable generic component usage without hardcoding', () => {
      const colorSchema = tokenTypeRegistry.color;
      const typographySchema = tokenTypeRegistry.typography;

      // Both should have the same structure
      expect(colorSchema.name).toBeDefined();
      expect(typographySchema.name).toBeDefined();
      expect(colorSchema.formatTabs.length).toBeGreaterThan(0);
      expect(typographySchema.formatTabs.length).toBeGreaterThan(0);
    });
  });
});

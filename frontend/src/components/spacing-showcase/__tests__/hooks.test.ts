/**
 * Tests for SpacingTokenShowcase custom hooks
 */

import { renderHook, act } from '@testing-library/react';
import { vi } from 'vitest';
import {
  useSpacingFiltering,
  useClipboard,
  useFileSelection,
  useScaleDerivation,
  useScaleVisualization,
} from '../hooks';
import type { SpacingToken } from '../types';

const mockTokens: SpacingToken[] = [
  {
    name: 'xs',
    value_px: 8,
    value_rem: 0.5,
    confidence: 0.95,
    grid_aligned: true,
    role: 'small',
    provenance: { image1: 1 },
    prominence_percentage: 10,
  },
  {
    name: 'md',
    value_px: 16,
    value_rem: 1,
    confidence: 0.85,
    grid_aligned: true,
    role: 'medium',
    provenance: { image1: 1, image2: 1 },
    prominence_percentage: 25,
  },
  {
    name: 'lg',
    value_px: 32,
    value_rem: 2,
    confidence: 0.75,
    grid_aligned: false,
    role: 'large',
    provenance: { image1: 1 },
    prominence_percentage: 15,
  },
];

describe('SpacingTokenShowcase Hooks', () => {
  describe('useSpacingFiltering', () => {
    it('should initialize with default filter and sort', () => {
      const { result } = renderHook(() => useSpacingFiltering(mockTokens));

      expect(result.current.filter).toBe('all');
      expect(result.current.sortBy).toBe('value');
      expect(result.current.displayTokens).toHaveLength(3);
    });

    it('should filter tokens by alignment', () => {
      const { result } = renderHook(() => useSpacingFiltering(mockTokens));

      act(() => {
        result.current.setFilter('aligned');
      });

      expect(result.current.displayTokens).toHaveLength(2);
      expect(result.current.displayTokens[0].grid_aligned).toBe(true);
    });

    it('should filter tokens by misalignment', () => {
      const { result } = renderHook(() => useSpacingFiltering(mockTokens));

      act(() => {
        result.current.setFilter('misaligned');
      });

      expect(result.current.displayTokens).toHaveLength(1);
      expect(result.current.displayTokens[0].name).toBe('lg');
    });

    it('should filter multi-source tokens', () => {
      const { result } = renderHook(() => useSpacingFiltering(mockTokens));

      act(() => {
        result.current.setFilter('multi-source');
      });

      expect(result.current.displayTokens).toHaveLength(1);
      expect(result.current.displayTokens[0].name).toBe('md');
    });

    it('should sort tokens by value', () => {
      const { result } = renderHook(() => useSpacingFiltering(mockTokens));

      act(() => {
        result.current.setSortBy('value');
      });

      expect(result.current.displayTokens[0].value_px).toBe(8);
      expect(result.current.displayTokens[2].value_px).toBe(32);
    });

    it('should sort tokens by confidence', () => {
      const { result } = renderHook(() => useSpacingFiltering(mockTokens));

      act(() => {
        result.current.setSortBy('confidence');
      });

      expect(result.current.displayTokens[0].confidence).toBe(0.95);
      expect(result.current.displayTokens[2].confidence).toBe(0.75);
    });

    it('should sort tokens by name', () => {
      const { result } = renderHook(() => useSpacingFiltering(mockTokens));

      act(() => {
        result.current.setSortBy('name');
      });

      expect(result.current.displayTokens[0].name).toBe('lg');
      expect(result.current.displayTokens[1].name).toBe('md');
      expect(result.current.displayTokens[2].name).toBe('xs');
    });

    it('should handle combined filter and sort', () => {
      const { result } = renderHook(() => useSpacingFiltering(mockTokens));

      act(() => {
        result.current.setFilter('aligned');
        result.current.setSortBy('name');
      });

      expect(result.current.displayTokens).toHaveLength(2);
      expect(result.current.displayTokens[0].name).toBe('md');
      expect(result.current.displayTokens[1].name).toBe('xs');
    });
  });

  describe('useClipboard', () => {
    beforeEach(() => {
      Object.assign(navigator, {
        clipboard: {
          writeText: vi.fn(),
        },
      });
    });

    it('should initialize with null copiedValue', () => {
      const { result } = renderHook(() => useClipboard());

      expect(result.current.copiedValue).toBe(null);
    });

    it('should copy text to clipboard', async () => {
      const { result } = renderHook(() => useClipboard());

      await act(async () => {
        await result.current.copyToClipboard('16px', 'px');
      });

      expect(navigator.clipboard.writeText).toHaveBeenCalledWith('16px');
      expect(result.current.copiedValue).toBe('px');
    });

    it('should clear copiedValue after timeout', async () => {
      const { result } = renderHook(() => useClipboard());

      await act(async () => {
        await result.current.copyToClipboard('16px', 'px');
      });

      expect(result.current.copiedValue).toBe('px');

      // Fast-forward time
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 2100));
      });

      expect(result.current.copiedValue).toBe(null);
    });

    it('should handle clipboard write errors', async () => {
      (navigator.clipboard.writeText as any).mockRejectedValue(new Error('Copy failed'));
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      const { result } = renderHook(() => useClipboard());

      await act(async () => {
        await result.current.copyToClipboard('16px', 'px');
      });

      expect(consoleSpy).toHaveBeenCalledWith('Failed to copy:', expect.any(Error));
      consoleSpy.mockRestore();
    });
  });

  describe('useFileSelection', () => {
    it('should call onFileSelected callback', () => {
      const mockCallback = vi.fn();
      const { result } = renderHook(() => useFileSelection(mockCallback));

      const mockFile = new File(['content'], 'test.jpg', { type: 'image/jpeg' });
      const event = new Event('change');
      Object.defineProperty(event, 'target', {
        value: { files: [mockFile] },
        enumerable: true,
      });

      act(() => {
        result.current.handleFileChange(event as any);
      });

      expect(mockCallback).toHaveBeenCalledWith(mockFile);
    });

    it('should handle missing file', () => {
      const mockCallback = vi.fn();
      const { result } = renderHook(() => useFileSelection(mockCallback));

      const event = new Event('change');
      Object.defineProperty(event, 'target', {
        value: { files: [] },
        enumerable: true,
      });

      act(() => {
        result.current.handleFileChange(event as any);
      });

      expect(mockCallback).not.toHaveBeenCalled();
    });

    it('should handle undefined onFileSelected', () => {
      const { result } = renderHook(() => useFileSelection(undefined));

      const mockFile = new File(['content'], 'test.jpg', { type: 'image/jpeg' });
      const event = new Event('change');
      Object.defineProperty(event, 'target', {
        value: { files: [mockFile] },
        enumerable: true,
      });

      expect(() => {
        act(() => {
          result.current.handleFileChange(event as any);
        });
      }).not.toThrow();
    });
  });

  describe('useScaleDerivation', () => {
    it('should derive base unit from tokens', () => {
      const tokensWithBase = [
        ...mockTokens,
        { ...mockTokens[0], base_unit: 4 },
      ];

      const { result } = renderHook(() =>
        useScaleDerivation(tokensWithBase, 8, '4-8-16-32')
      );

      expect(result.current.derivedBase).toBe(4);
    });

    it('should use provided base unit when no tokens have it', () => {
      const { result } = renderHook(() =>
        useScaleDerivation(mockTokens, 8, '4-8-16-32')
      );

      expect(result.current.derivedBase).toBe(8);
    });

    it('should derive scale from tokens', () => {
      const tokensWithScale = [
        ...mockTokens,
        { ...mockTokens[0], scale_system: 'fibonacci' },
      ];

      const { result } = renderHook(() =>
        useScaleDerivation(tokensWithScale, 8, 'linear')
      );

      expect(result.current.derivedScale).toBe('fibonacci');
    });

    it('should use provided scale when no tokens have it', () => {
      const { result } = renderHook(() =>
        useScaleDerivation(mockTokens, 8, 'linear')
      );

      expect(result.current.derivedScale).toBe('linear');
    });
  });

  describe('useScaleVisualization', () => {
    it('should calculate max value', () => {
      const { result } = renderHook(() => useScaleVisualization(mockTokens));

      expect(result.current.maxValue).toBe(32);
    });

    it('should calculate bar height correctly', () => {
      const { result } = renderHook(() => useScaleVisualization(mockTokens));

      const height = result.current.getBarHeight(16);
      expect(height).toBeCloseTo((16 / 32) * 150);
    });

    it('should handle max height constraint', () => {
      const { result } = renderHook(() => useScaleVisualization(mockTokens));

      const height = result.current.getBarHeight(32);
      expect(height).toBe(150);
    });

    it('should handle empty token list', () => {
      const { result } = renderHook(() => useScaleVisualization([]));

      expect(result.current.maxValue).toBe(0);
      expect(result.current.getBarHeight(16)).toBe(0);
    });

    it('should allow custom max height', () => {
      const { result } = renderHook(() => useScaleVisualization(mockTokens));

      const height = result.current.getBarHeight(16, 200);
      expect(height).toBeCloseTo((16 / 32) * 200);
    });
  });
});

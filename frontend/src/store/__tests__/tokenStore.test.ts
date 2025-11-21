/**
 * Token Store Tests
 *
 * Comprehensive test suite for Zustand tokenState store
 * Tests initialization, state updates, and all action methods
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useTokenStore } from '../tokenStore';
import { ColorToken } from '../../types';

describe('useTokenStore', () => {
  beforeEach(() => {
    // Reset store to initial state before each test
    useTokenStore.setState({
      tokens: [],
      tokenType: 'color',
      projectId: '',
      selectedTokenId: null,
      editingToken: null,
      playgroundToken: null,
      filters: {},
      sortBy: 'hue',
      viewMode: 'grid',
      sidebarOpen: false,
      playgroundOpen: false,
      playgroundActiveTab: 'adjuster',
      isExtracting: false,
      extractionProgress: 0,
      extractionStage: 'uploading',
      extractionTokenCount: 0,
    });
  });

  describe('Initial State', () => {
    it('should have correct initial state values', () => {
      const { result } = renderHook(() => useTokenStore());

      expect(result.current.tokens).toEqual([]);
      expect(result.current.tokenType).toBe('color');
      expect(result.current.projectId).toBe('');
      expect(result.current.selectedTokenId).toBeNull();
      expect(result.current.editingToken).toBeNull();
      expect(result.current.viewMode).toBe('grid');
      expect(result.current.sidebarOpen).toBe(false);
      expect(result.current.isExtracting).toBe(false);
    });
  });

  describe('Token Management', () => {
    it('should set tokens', () => {
      const { result } = renderHook(() => useTokenStore());
      const mockToken: ColorToken = {
        id: 1,
        hex: '#FF0000',
        rgb: 'rgb(255, 0, 0)',
        name: 'Red',
        confidence: 0.95,
      };

      act(() => {
        result.current.setTokens([mockToken]);
      });

      expect(result.current.tokens).toEqual([mockToken]);
    });

    it('should set multiple tokens', () => {
      const { result } = renderHook(() => useTokenStore());
      const mockTokens: ColorToken[] = [
        { id: 1, hex: '#FF0000', rgb: 'rgb(255, 0, 0)', name: 'Red', confidence: 0.95 },
        { id: 2, hex: '#00FF00', rgb: 'rgb(0, 255, 0)', name: 'Green', confidence: 0.9 },
        { id: 3, hex: '#0000FF', rgb: 'rgb(0, 0, 255)', name: 'Blue', confidence: 0.88 },
      ];

      act(() => {
        result.current.setTokens(mockTokens);
      });

      expect(result.current.tokens).toHaveLength(3);
      expect(result.current.tokens).toEqual(mockTokens);
    });

    it('should set project ID', () => {
      const { result } = renderHook(() => useTokenStore());

      act(() => {
        result.current.setProjectId('project-123');
      });

      expect(result.current.projectId).toBe('project-123');
    });

    it('should set token type', () => {
      const { result } = renderHook(() => useTokenStore());

      act(() => {
        result.current.setTokenType('typography');
      });

      expect(result.current.tokenType).toBe('typography');
    });
  });

  describe('Token Selection', () => {
    it('should select a token by ID', () => {
      const { result } = renderHook(() => useTokenStore());

      act(() => {
        result.current.selectToken('token-123');
      });

      expect(result.current.selectedTokenId).toBe('token-123');
    });

    it('should clear selected token when passing null', () => {
      const { result } = renderHook(() => useTokenStore());

      act(() => {
        result.current.selectToken('token-123');
        result.current.selectToken(null);
      });

      expect(result.current.selectedTokenId).toBeNull();
    });
  });

  describe('Token Editing', () => {
    it('should start editing a token', () => {
      const { result } = renderHook(() => useTokenStore());
      const mockToken: ColorToken = {
        id: 1,
        hex: '#FF0000',
        rgb: 'rgb(255, 0, 0)',
        name: 'Red',
        confidence: 0.95,
      };

      act(() => {
        result.current.startEditing(mockToken);
      });

      expect(result.current.editingToken).toEqual(mockToken);
    });

    it('should update editing field', () => {
      const { result } = renderHook(() => useTokenStore());
      const mockToken: ColorToken = {
        id: 1,
        hex: '#FF0000',
        rgb: 'rgb(255, 0, 0)',
        name: 'Red',
        confidence: 0.95,
      };

      act(() => {
        result.current.startEditing(mockToken);
        result.current.updateEditingField('name', 'Crimson Red');
      });

      expect(result.current.editingToken?.name).toBe('Crimson Red');
      expect(result.current.editingToken?.hex).toBe('#FF0000');
    });

    it('should update multiple editing fields', () => {
      const { result } = renderHook(() => useTokenStore());
      const mockToken: ColorToken = {
        id: 1,
        hex: '#FF0000',
        rgb: 'rgb(255, 0, 0)',
        name: 'Red',
        confidence: 0.95,
      };

      act(() => {
        result.current.startEditing(mockToken);
        result.current.updateEditingField('name', 'Crimson');
        result.current.updateEditingField('confidence', 0.99);
      });

      expect(result.current.editingToken?.name).toBe('Crimson');
      expect(result.current.editingToken?.confidence).toBe(0.99);
    });

    it('should cancel editing', () => {
      const { result } = renderHook(() => useTokenStore());
      const mockToken: ColorToken = {
        id: 1,
        hex: '#FF0000',
        rgb: 'rgb(255, 0, 0)',
        name: 'Red',
        confidence: 0.95,
      };

      act(() => {
        result.current.startEditing(mockToken);
        result.current.cancelEdit();
      });

      expect(result.current.editingToken).toBeNull();
    });
  });

  describe('Playground Mode', () => {
    it('should set playground token', () => {
      const { result } = renderHook(() => useTokenStore());
      const mockToken: Partial<ColorToken> = {
        hex: '#FF0000',
        name: 'Red',
      };

      act(() => {
        result.current.setPlaygroundToken(mockToken);
      });

      expect(result.current.playgroundToken).toEqual(mockToken);
    });

    it('should reset playground', () => {
      const { result } = renderHook(() => useTokenStore());
      const mockToken: Partial<ColorToken> = {
        hex: '#FF0000',
        name: 'Red',
      };

      act(() => {
        result.current.setPlaygroundToken(mockToken);
        result.current.resetPlayground();
      });

      expect(result.current.playgroundToken).toBeNull();
    });

    it('should toggle playground open state', () => {
      const { result } = renderHook(() => useTokenStore());

      expect(result.current.playgroundOpen).toBe(false);

      act(() => {
        result.current.togglePlayground();
      });

      expect(result.current.playgroundOpen).toBe(true);

      act(() => {
        result.current.togglePlayground();
      });

      expect(result.current.playgroundOpen).toBe(false);
    });

    it('should set playground active tab', () => {
      const { result } = renderHook(() => useTokenStore());

      act(() => {
        result.current.setPlaygroundTab('harmony');
      });

      expect(result.current.playgroundActiveTab).toBe('harmony');
    });
  });

  describe('Filtering', () => {
    it('should set filter', () => {
      const { result } = renderHook(() => useTokenStore());

      act(() => {
        result.current.setFilter('temperature', 'warm');
      });

      expect(result.current.filters.temperature).toBe('warm');
    });

    it('should set multiple filters', () => {
      const { result } = renderHook(() => useTokenStore());

      act(() => {
        result.current.setFilter('temperature', 'warm');
        result.current.setFilter('saturation', 'vivid');
      });

      expect(result.current.filters.temperature).toBe('warm');
      expect(result.current.filters.saturation).toBe('vivid');
    });

    it('should clear all filters', () => {
      const { result } = renderHook(() => useTokenStore());

      act(() => {
        result.current.setFilter('temperature', 'warm');
        result.current.setFilter('saturation', 'vivid');
        result.current.clearFilters();
      });

      expect(result.current.filters).toEqual({});
    });
  });

  describe('Sorting', () => {
    it('should set sort option', () => {
      const { result } = renderHook(() => useTokenStore());

      act(() => {
        result.current.setSortBy('name');
      });

      expect(result.current.sortBy).toBe('name');
    });

    it('should change sort option', () => {
      const { result } = renderHook(() => useTokenStore());

      act(() => {
        result.current.setSortBy('hue');
      });

      expect(result.current.sortBy).toBe('hue');

      act(() => {
        result.current.setSortBy('confidence');
      });

      expect(result.current.sortBy).toBe('confidence');
    });
  });

  describe('View Mode', () => {
    it('should set view mode to list', () => {
      const { result } = renderHook(() => useTokenStore());

      act(() => {
        result.current.setViewMode('list');
      });

      expect(result.current.viewMode).toBe('list');
    });

    it('should set view mode to table', () => {
      const { result } = renderHook(() => useTokenStore());

      act(() => {
        result.current.setViewMode('table');
      });

      expect(result.current.viewMode).toBe('table');
    });

    it('should change view mode', () => {
      const { result } = renderHook(() => useTokenStore());

      act(() => {
        result.current.setViewMode('grid');
        result.current.setViewMode('list');
        result.current.setViewMode('table');
      });

      expect(result.current.viewMode).toBe('table');
    });
  });

  describe('Sidebar', () => {
    it('should toggle sidebar open state', () => {
      const { result } = renderHook(() => useTokenStore());

      expect(result.current.sidebarOpen).toBe(false);

      act(() => {
        result.current.toggleSidebar();
      });

      expect(result.current.sidebarOpen).toBe(true);

      act(() => {
        result.current.toggleSidebar();
      });

      expect(result.current.sidebarOpen).toBe(false);
    });
  });

  describe('Extraction Progress', () => {
    it('should update extraction progress', () => {
      const { result } = renderHook(() => useTokenStore());

      act(() => {
        result.current.updateExtractionProgress(50, 'processing', 15);
      });

      expect(result.current.extractionProgress).toBe(50);
      expect(result.current.extractionStage).toBe('processing');
      expect(result.current.extractionTokenCount).toBe(15);
    });

    it('should mark extraction as complete', () => {
      const { result } = renderHook(() => useTokenStore());

      act(() => {
        result.current.updateExtractionProgress(100, 'completed', 25);
        result.current.completeExtraction();
      });

      expect(result.current.isExtracting).toBe(false);
      expect(result.current.extractionProgress).toBe(0);
    });

    it('should handle extraction progress from start to finish', () => {
      const { result } = renderHook(() => useTokenStore());

      act(() => {
        result.current.updateExtractionProgress(0, 'uploading', 0);
      });
      expect(result.current.extractionProgress).toBe(0);
      expect(result.current.extractionStage).toBe('uploading');

      act(() => {
        result.current.updateExtractionProgress(33, 'analyzing', 5);
      });
      expect(result.current.extractionProgress).toBe(33);
      expect(result.current.extractionStage).toBe('analyzing');

      act(() => {
        result.current.updateExtractionProgress(66, 'extracting', 15);
      });
      expect(result.current.extractionProgress).toBe(66);
      expect(result.current.extractionTokenCount).toBe(15);

      act(() => {
        result.current.updateExtractionProgress(100, 'completed', 25);
      });
      expect(result.current.extractionProgress).toBe(100);

      act(() => {
        result.current.completeExtraction();
      });
      expect(result.current.isExtracting).toBe(false);
    });
  });
});

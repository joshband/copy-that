/**
 * Token State Store
 *
 * Single source of truth for all token-related state
 * Managed with Zustand for simplicity and performance
 *
 * Schema-driven approach: All token types share this store structure
 */

import { create } from 'zustand';
import { ColorToken } from '../types';

export type TokenType = 'color' | 'typography' | 'spacing' | 'shadow' | 'animation';
export type SortOption = 'hue' | 'name' | 'confidence' | 'temperature' | 'saturation';
export type ViewMode = 'grid' | 'list' | 'table';
export type ExtractionStage = 'uploading' | 'analyzing' | 'extracting' | 'completed' | 'failed';

/**
 * Core Token State Interface
 *
 * All state related to tokens, their selection, editing, and display
 */
export interface TokenState {
  // Data
  tokens: ColorToken[];
  tokenType: TokenType;
  projectId: string;

  // Selection & Editing
  selectedTokenId: string | number | null;
  editingToken: Partial<ColorToken> | null;
  playgroundToken: Partial<ColorToken> | null;

  // View State
  filters: Record<string, string>;
  sortBy: SortOption;
  viewMode: ViewMode;
  sidebarOpen: boolean;
  playgroundOpen: boolean;
  playgroundActiveTab: string;

  // Extraction State
  isExtracting: boolean;
  extractionProgress: number;
  extractionStage: ExtractionStage;
  extractionTokenCount: number;

  // Actions
  setTokens: (tokens: ColorToken[]) => void;
  setProjectId: (projectId: string) => void;
  setTokenType: (tokenType: TokenType) => void;
  selectToken: (id: string | number | null) => void;
  startEditing: (token: ColorToken) => void;
  updateEditingField: (field: string, value: unknown) => void;
  saveEdit: () => Promise<void>;
  cancelEdit: () => void;
  deleteToken: (id: string | number) => Promise<void>;
  duplicateToken: (id: string | number) => Promise<void>;
  setPlaygroundToken: (token: Partial<ColorToken> | null) => void;
  applyPlaygroundChanges: () => void;
  resetPlayground: () => void;
  setFilter: (key: string, value: string) => void;
  clearFilters: () => void;
  setSortBy: (option: SortOption) => void;
  setViewMode: (mode: ViewMode) => void;
  toggleSidebar: () => void;
  togglePlayground: () => void;
  setPlaygroundTab: (tab: string) => void;
  updateExtractionProgress: (progress: number, stage: ExtractionStage, count: number) => void;
  completeExtraction: () => void;
}

/**
 * Zustand store for token state management
 *
 * Provides centralized state with zero prop drilling
 * All actions are type-safe and testable
 */
export const useTokenStore = create<TokenState>((set) => ({
  // Initial state
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

  // Token data actions
  setTokens: (tokens) => set({ tokens }),
  setProjectId: (projectId) => set({ projectId }),
  setTokenType: (tokenType) => set({ tokenType }),

  // Selection
  selectToken: (id) => set({ selectedTokenId: id }),

  // Editing
  startEditing: (token) => set({ editingToken: { ...token } }),
  updateEditingField: (field, value) =>
    set((state) => ({
      editingToken: state.editingToken ? { ...state.editingToken, [field]: value } : null,
    })),
  cancelEdit: () => set({ editingToken: null }),
  saveEdit: async () => {
    // Local-only operation - applies edits to in-memory state
    // Re-extract to persist changes to backend
    set((state) => {
      if (!state.editingToken || !state.editingToken.id) return { editingToken: null };
      return {
        tokens: state.tokens.map((t) =>
          t.id === state.editingToken!.id ? { ...t, ...state.editingToken } as ColorToken : t
        ),
        editingToken: null,
      };
    });
  },
  deleteToken: async (id) => {
    // Local-only operation - removes from in-memory state
    set((state) => ({
      tokens: state.tokens.filter((t) => t.id !== id),
      selectedTokenId: state.selectedTokenId === id ? null : state.selectedTokenId,
    }));
  },
  duplicateToken: async (id) => {
    // Local-only operation - duplicates in in-memory state
    set((state) => {
      const token = state.tokens.find((t) => t.id === id);
      if (!token) return state;
      const newToken = {
        ...token,
        id: `${token.id}-copy-${Date.now()}`,
        name: `${token.name} (copy)`,
      };
      return { tokens: [...state.tokens, newToken] };
    });
  },

  // Playground
  setPlaygroundToken: (token) => set({ playgroundToken: token }),
  applyPlaygroundChanges: () => {
    // Merges playground adjustments into selected token (local-only)
    set((state) => {
      if (!state.playgroundToken || !state.selectedTokenId) return { playgroundToken: null };
      return {
        tokens: state.tokens.map((t) =>
          t.id === state.selectedTokenId ? { ...t, ...state.playgroundToken } as ColorToken : t
        ),
        playgroundToken: null,
      };
    });
  },
  resetPlayground: () => set({ playgroundToken: null }),
  setPlaygroundTab: (tab) => set({ playgroundActiveTab: tab }),
  togglePlayground: () =>
    set((state) => ({
      playgroundOpen: !state.playgroundOpen,
    })),

  // Filtering & Sorting
  setFilter: (key, value) =>
    set((state) => ({
      filters: { ...state.filters, [key]: value },
    })),
  clearFilters: () => set({ filters: {} }),
  setSortBy: (option) => set({ sortBy: option }),

  // View
  setViewMode: (mode) => set({ viewMode: mode }),
  toggleSidebar: () =>
    set((state) => ({
      sidebarOpen: !state.sidebarOpen,
    })),

  // Extraction
  updateExtractionProgress: (progress, stage, count) =>
    set({
      isExtracting: true,
      extractionProgress: progress,
      extractionStage: stage,
      extractionTokenCount: count,
    }),
  completeExtraction: () =>
    set({
      isExtracting: false,
      extractionProgress: 0,
      extractionStage: 'uploading',
      extractionTokenCount: 0,
    }),
}));

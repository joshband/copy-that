/**
 * UI Store
 *
 * Ephemeral UI state (selections, filters, view toggles, extraction progress).
 * Token data lives exclusively in tokenGraphStore; this store must not hold canonical token records.
 */
import { create } from 'zustand'

export type TokenType = 'color' | 'spacing' | 'shadow' | 'typography'
export type ViewMode = 'grid' | 'list' | 'table'
export type SortOption = 'hue' | 'name' | 'confidence' | 'temperature' | 'saturation'

export type ExtractionStage =
  | 'idle'
  | 'uploading'
  | 'streaming'
  | 'extracting'
  | 'processing'
  | 'analyzing'
  | 'completed'
  | 'complete'

export interface TokenUIState {
  overrideTokens: any[] | null
  tokenType: TokenType
  projectId: string | number | null
  selectedTokenId: string | number | null
  editingToken: any | null
  playgroundToken: any | null
  filters: Record<string, string>
  searchTerm: string
  sortBy: SortOption
  viewMode: ViewMode
  sidebarOpen: boolean
  playgroundOpen: boolean
  playgroundActiveTab: string
  isExtracting: boolean
  extractionProgress: number
  extractionStage: ExtractionStage
  extractionTokenCount: number
  setTokens: (tokens: any[]) => void
  setProjectId: (id: string | number | null) => void
  setTokenType: (type: TokenType) => void
  selectToken: (id: string | number | null) => void
  startEditing: (token: any) => void
  updateEditingField: (field: string, value: any) => void
  cancelEdit: () => void
  deleteToken: (id: string | number) => Promise<void>
  duplicateToken: (id: string | number) => Promise<void>
  toggleSidebar: () => void
  togglePlayground: () => void
  setPlaygroundToken: (token: any) => void
  resetPlayground: () => void
  setPlaygroundTab: (tab: string) => void
  applyPlaygroundChanges: () => void
  setFilter: (key: string, value: string) => void
  setSearchTerm: (value: string) => void
  clearFilters: () => void
  setSortBy: (sortBy: SortOption) => void
  setViewMode: (mode: ViewMode) => void
  updateExtractionProgress: (progress: number, stage?: ExtractionStage, count?: number) => void
  completeExtraction: () => void
}

export const useTokenUIStore = create<TokenUIState>((set, get) => ({
  overrideTokens: null,
  tokenType: 'color',
  projectId: '',
  selectedTokenId: null,
  editingToken: null,
  playgroundToken: null,
  filters: {},
  searchTerm: '',
  sortBy: 'hue',
  viewMode: 'grid',
  sidebarOpen: false,
  playgroundOpen: false,
  playgroundActiveTab: 'adjuster',
  isExtracting: false,
  extractionProgress: 0,
  extractionStage: 'idle',
  extractionTokenCount: 0,

  setTokens: (tokens) => set({ overrideTokens: tokens }),
  setProjectId: (id) => set({ projectId: id }),
  setTokenType: (type) => set({ tokenType: type }),
  selectToken: (id) => set({ selectedTokenId: id }),
  startEditing: (token) => set({ editingToken: token }),
  updateEditingField: (field, value) =>
    set((state) => ({
      editingToken: state.editingToken ? { ...state.editingToken, [field]: value } : state.editingToken,
    })),
  cancelEdit: () => set({ editingToken: null }),
  deleteToken: async (id) => {
    set((state) => ({
      overrideTokens: (state.overrideTokens ?? []).filter((t) => t.id !== id),
    }))
  },
  duplicateToken: async (id) => {
    set((state) => {
      const list = state.overrideTokens ?? []
      const found = list.find((t) => t.id === id)
      if (!found) return {}
      const cloneId = typeof id === 'string' ? `${id}-copy` : `${String(id)}-copy`
      return { overrideTokens: [...list, { ...found, id: cloneId }] }
    })
  },
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  togglePlayground: () => set((state) => ({ playgroundOpen: !state.playgroundOpen })),
  setPlaygroundToken: (token) => set({ playgroundToken: token }),
  resetPlayground: () => set({ playgroundToken: null }),
  setPlaygroundTab: (tab) => set({ playgroundActiveTab: tab }),
  applyPlaygroundChanges: () => {},
  setFilter: (key, value) => set((state) => ({ filters: { ...state.filters, [key]: value } })),
  setSearchTerm: (value) => set({ searchTerm: value }),
  clearFilters: () => set({ filters: {} }),
  setSortBy: (sortBy) => set({ sortBy }),
  setViewMode: (mode) => set({ viewMode: mode }),
  updateExtractionProgress: (progress, stage = 'streaming', count) =>
    set({
      extractionProgress: progress,
      extractionStage: stage,
      extractionTokenCount: count ?? get().extractionTokenCount,
      isExtracting: progress < 100,
    }),
  completeExtraction: () =>
    set({
      isExtracting: false,
      extractionProgress: 0,
      extractionStage: 'complete',
    }),
}))

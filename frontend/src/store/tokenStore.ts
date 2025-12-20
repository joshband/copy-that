export type TokenType = 'color' | 'spacing' | 'shadow' | 'typography'
export type ViewMode = 'grid' | 'list' | 'table'
export type SortOption = 'hue' | 'name' | 'confidence' | 'temperature' | 'saturation'

const factory = () => ({
  tokenType: 'color' as TokenType,
  viewMode: 'grid' as ViewMode,
  sortBy: 'hue' as SortOption,
  filters: {} as Record<string, string>,
  tokens: [],
  projectId: null as number | null,
  selectedTokenId: null as string | number | null,
  editingToken: null as any,
  sidebarOpen: false,
  playgroundOpen: false,
  playgroundToken: null as any,
  playgroundActiveTab: 'info',
  extractionProgress: 0,
  extractionStage: 'idle',
  extractionTokenCount: 0,
  isExtracting: false,
  setViewMode: (_mode: ViewMode) => {},
  setSortBy: (_sort: SortOption) => {},
  setFilter: (_key: string, _val: string) => {},
  clearFilters: () => {},
  setTokens: (_tokens: any) => {},
  setProjectId: (_id: number | null) => {},
  selectToken: (_id: string | number | null) => {},
  startEditing: (_token: any) => {},
  updateEditingField: (_field: string, _value: any) => {},
  cancelEdit: () => {},
  toggleSidebar: () => {},
  togglePlayground: () => {},
  setPlaygroundToken: (_token: any) => {},
  resetPlayground: () => {},
  setPlaygroundTab: (_tab: string) => {},
  applyPlaygroundChanges: () => {},
  updateExtractionProgress: (_progress: number, _stage?: string, _count?: number) => {},
  completeExtraction: () => {},
})

export const useTokenStore: any = Object.assign(factory, { setState: (_fn: any) => {} })

export default useTokenStore

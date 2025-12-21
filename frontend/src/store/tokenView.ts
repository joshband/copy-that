import { useMemo } from 'react'
import { shallow } from 'zustand/shallow'
import {
  useTokenGraphStore,
  selectLegacyColors,
  selectLegacySpacing,
  selectLegacyShadows,
  selectTypography,
} from './tokenGraphStore'
import { useTokenUIStore, type TokenUIState, type TokenType } from './uiStore'

/**
 * Hook that combines canonical token data (tokenGraphStore) with UI-only state (uiStore).
 * Consumers should treat the returned tokens as read-only.
 */
export const useTokenViewState = () => {
  const ui = useTokenUIStore(
    (s) => ({
      tokensOverride: s.overrideTokens,
      tokenType: s.tokenType,
      filters: s.filters,
      searchTerm: s.searchTerm,
      sortBy: s.sortBy,
      viewMode: s.viewMode,
      selectedTokenId: s.selectedTokenId,
      selectToken: s.selectToken,
      startEditing: s.startEditing,
      deleteToken: s.deleteToken,
      duplicateToken: s.duplicateToken,
      setSearchTerm: s.setSearchTerm,
      clearFilters: s.clearFilters,
      setFilter: s.setFilter,
      setSortBy: s.setSortBy,
      setViewMode: s.setViewMode,
    }),
    shallow,
  )
  const colors = useTokenGraphStore(selectLegacyColors)
  const spacing = useTokenGraphStore(selectLegacySpacing)
  const shadows = useTokenGraphStore(selectLegacyShadows)
  const typography = useTokenGraphStore(selectTypography)

  const tokens = useMemo(() => {
    const tokensFromGraph = mapTokens(ui.tokenType, { colors, spacing, shadows, typography })
    return ui.tokensOverride ?? tokensFromGraph
  }, [ui.tokensOverride, ui.tokenType, colors, spacing, shadows, typography])

  return { ...ui, tokens }
}

export const mapTokens = (
  tokenType: TokenType,
  graph: {
    colors: any[]
    spacing: any[]
    shadows: any[]
    typography: any[]
  },
) => {
  switch (tokenType) {
    case 'color':
      return (graph.colors as any[]).map((c) => {
        const value = (c?.raw as any)?.$value ?? (c as any)?.raw
        const hex = typeof value === 'string' ? value : value?.hex ?? '#cccccc'
        const semantic = (c?.raw as any)?.name ?? (c as any)?.semantic_names
        const designIntent = (c?.raw as any)?.design_intent ?? (c as any)?.design_intent
        const extractor =
          (c as any)?.extraction_metadata?.extractor ||
          (c as any)?.raw?.extraction_metadata?.extractor
        return {
          id: c.id,
          hex,
          name: (c?.raw as any)?.name ?? c?.name ?? c.id,
          confidence: (c?.raw as any)?.confidence ?? 0.5,
          semantic_names: semantic,
          design_intent: designIntent,
          extractor,
          usage: (c as any)?.raw?.usage ?? (c as any)?.usage,
        }
      })
    case 'spacing':
      return (graph.spacing as any[]).map((t) => {
        const rawValue = (t?.raw as any)?.$value?.value ?? (t?.raw as any)?.value ?? 0
        return {
          id: t.id,
          name: t.id,
          value_px: rawValue ?? 0,
          value_rem: (rawValue ?? 0) / 16,
          multiplier: (t as any)?.multiplier,
        }
      })
    case 'shadow':
      return graph.shadows
    case 'typography':
      return graph.typography
    default:
      return []
  }
}

export type TokenViewState = ReturnType<typeof useTokenViewState>
export type { TokenType, TokenUIState }

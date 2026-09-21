/**
 * @deprecated Canonical token data now lives in tokenGraphStore (W3C format).
 * Use tokenGraphStore selectors for data and uiStore for UI-only state.
 * This wrapper remains for legacy components during migration.
 */
import { useTokenGraphStore } from './tokenGraphStore'
import { useTokenUIStore, type TokenUIState, type TokenType, type ViewMode, type SortOption } from './uiStore'

export type { TokenType, ViewMode, SortOption } from './uiStore'

export const useTokenStore: any = (selector?: (state: ReturnType<typeof combineState>) => any) => {
  const ui = useTokenUIStore()
  const colors = useTokenGraphStore((s) => s.legacyColors())
  const spacing = useTokenGraphStore((s) => s.legacySpacing())
  const shadows = useTokenGraphStore((s) => s.shadows)
  const typography = useTokenGraphStore((s) => s.typography)

  const combined = combineState(ui, { colors, spacing, shadows, typography })
  return selector ? selector(combined) : (combined as any)
}

const combineState = (
  ui: TokenUIState,
  graph: {
    colors: any[]
    spacing: any[]
    shadows: any[]
    typography: any[]
  },
) => {
  const tokensFromGraph: any[] = (() => {
    switch (ui.tokenType) {
      case 'color':
        return (graph.colors as any[]).map((c) => {
          const value = (c?.raw as any)?.$value ?? (c as any)?.raw
          const hex = typeof value === 'string' ? value : value?.hex ?? '#cccccc'
          return {
            id: c.id,
            hex,
            name: (c?.raw as any)?.name ?? c?.name ?? c.id,
            confidence: (c?.raw as any)?.confidence ?? 0.5,
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
          }
        })
      case 'shadow':
        return graph.shadows
      case 'typography':
        return graph.typography
      default:
        return []
    }
  })()

  const tokens = ui.overrideTokens ?? tokensFromGraph

  return {
    ...ui,
    tokens: tokens as any[],
  }
}

// expose zustand helpers for tests
(useTokenStore as any).setState = (partial: any) => {
  if (typeof partial === 'function') {
    return useTokenUIStore.setState((state) => {
      const current = { ...state, tokens: state.overrideTokens ?? [] }
      const next = partial(current)
      if (!next) return state
      const { tokens, ...rest } = next as any
      return { ...state, ...rest, ...(tokens !== undefined ? { overrideTokens: tokens } : {}) }
    })
  }
  const { tokens, ...rest } = (partial ?? {}) as any
  return useTokenUIStore.setState({
    ...rest,
    ...(tokens !== undefined ? { overrideTokens: tokens } : {}),
  })
}
(useTokenStore as any).getState = () => {
  const ui = useTokenUIStore.getState()
  return { ...ui, tokens: ui.overrideTokens ?? [] }
}

export default useTokenStore

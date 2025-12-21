/**
 * Shadow Token Store
 *
 * @deprecated Token data should be sourced from tokenGraphStore (W3C format).
 * This store is UI-only for legacy components while migration completes.
 * Manages shadow token UI state with color linking capabilities.
 */

import { create } from 'zustand'
import { useTokenGraphStore } from './tokenGraphStore'
import type { W3CShadowToken, W3CShadowLayer } from '../types/tokens'

export interface ShadowTokenWithMeta {
  id: string
  raw: W3CShadowToken
  name?: string
  shadowType?: string
  semanticRole?: string
  confidence?: number
  /** Layer-by-layer linked color token IDs */
  linkedColorIds: string[]
  /** Original hex values (fallback when no token linked) */
  originalColors: string[]
}

export interface ColorTokenOption {
  id: string
  hex: string
  name?: string
}

export interface ShadowStoreState {
  // Data
  shadows: ShadowTokenWithMeta[]
  availableColors: ColorTokenOption[]

  // Selection
  selectedShadowId: string | null
  editingShadowId: string | null

  // Actions
  setShadows: (shadows: ShadowTokenWithMeta[]) => void
  setAvailableColors: (colors: ColorTokenOption[]) => void
  selectShadow: (id: string | null) => void
  startEditing: (id: string) => void
  cancelEditing: () => void

  // Color Linking Actions
  linkColorToShadow: (shadowId: string, layerIndex: number, colorTokenId: string) => void
  unlinkColorFromShadow: (shadowId: string, layerIndex: number) => void
  updateShadowColor: (shadowId: string, layerIndex: number, hexOrTokenRef: string) => void

  // Helpers
  getShadowById: (id: string) => ShadowTokenWithMeta | undefined
  getLinkedColor: (shadowId: string, layerIndex: number) => ColorTokenOption | undefined
  getShadowsUsingColor: (colorTokenId: string) => ShadowTokenWithMeta[]
}

/**
 * Extract color from a shadow layer value
 */
const extractLayerColor = (layer: W3CShadowLayer | any): string => {
  if (layer && typeof layer === 'object' && 'color' in layer) {
    const color = layer.color
    if (typeof color === 'string') {
      // Check if it's a token reference like {color.primary}
      if (color.startsWith('{') && color.endsWith('}')) {
        return color
      }
      return color
    }
  }
  return '#000000'
}

/**
 * Strip braces from token reference
 */
const stripBraces = (val: string): string =>
  (val.startsWith('{') && val.endsWith('}')) ? val.slice(1, -1) : val

/**
 * Check if value is a token reference
 */
const isTokenRef = (val: string): boolean =>
  val.startsWith('{') && val.endsWith('}')

/**
 * Zustand store for shadow token management
 */
export const useShadowStore = create<ShadowStoreState>((set, get) => {
  const graph = useTokenGraphStore.getState ? useTokenGraphStore.getState() : null
  const initialShadows = graph?.legacyShadows ? graph.legacyShadows() : []
  const initialColors =
    graph?.legacyColors
      ? graph.legacyColors().map((c) => ({ id: c.id, hex: c.hex, name: c.name }))
      : []

  return {
    // Initial state (derived from canonical tokenGraphStore)
    shadows: initialShadows,
    availableColors: initialColors,
    selectedShadowId: null,
    editingShadowId: null,

    // Data setters
    setShadows: (shadows) => set({ shadows }),
    setAvailableColors: (colors) => set({ availableColors: colors }),

    // Selection
    selectShadow: (id) => set({ selectedShadowId: id }),
    startEditing: (id) => set({ editingShadowId: id }),
    cancelEditing: () => set({ editingShadowId: null }),

    // Color Linking
    linkColorToShadow: (shadowId, layerIndex, colorTokenId) => {
      set((state) => ({
        shadows: state.shadows.map((shadow) => {
          if (shadow.id !== shadowId) return shadow

          const newLinkedColorIds = [...shadow.linkedColorIds]
          newLinkedColorIds[layerIndex] = colorTokenId

          // Update the raw token value with token reference
          const rawValue = shadow.raw.$value
          const layers = Array.isArray(rawValue) ? [...rawValue] : [{ ...rawValue }]
          if (layers[layerIndex]) {
            layers[layerIndex] = {
              ...layers[layerIndex],
              color: `{${colorTokenId}}`,
            }
          }

          return {
            ...shadow,
            linkedColorIds: newLinkedColorIds,
            raw: {
              ...shadow.raw,
              $value: Array.isArray(rawValue) ? layers : layers[0],
            },
          }
        }),
      }))
    },

    unlinkColorFromShadow: (shadowId, layerIndex) => {
      set((state) => ({
        shadows: state.shadows.map((shadow) => {
          if (shadow.id !== shadowId) return shadow

          const newLinkedColorIds = [...shadow.linkedColorIds]
          const originalColor = shadow.originalColors[layerIndex] || '#000000'
          newLinkedColorIds[layerIndex] = ''

          // Revert to original hex color
          const rawValue = shadow.raw.$value
          const layers = Array.isArray(rawValue) ? [...rawValue] : [{ ...rawValue }]
          if (layers[layerIndex]) {
            layers[layerIndex] = {
              ...layers[layerIndex],
              color: originalColor,
            }
          }

          return {
            ...shadow,
            linkedColorIds: newLinkedColorIds,
            raw: {
              ...shadow.raw,
              $value: Array.isArray(rawValue) ? layers : layers[0],
            },
          }
        }),
      }))
    },

    updateShadowColor: (shadowId, layerIndex, hexOrTokenRef) => {
      set((state) => ({
        shadows: state.shadows.map((shadow) => {
          if (shadow.id !== shadowId) return shadow

          const newLinkedColorIds = [...shadow.linkedColorIds]
          if (isTokenRef(hexOrTokenRef)) {
            newLinkedColorIds[layerIndex] = stripBraces(hexOrTokenRef)
          } else {
            newLinkedColorIds[layerIndex] = ''
          }

          const rawValue = shadow.raw.$value
          const layers = Array.isArray(rawValue) ? [...rawValue] : [{ ...rawValue }]
          if (layers[layerIndex]) {
            layers[layerIndex] = {
              ...layers[layerIndex],
              color: hexOrTokenRef,
            }
          }

          return {
            ...shadow,
            linkedColorIds: newLinkedColorIds,
            raw: {
              ...shadow.raw,
              $value: Array.isArray(rawValue) ? layers : layers[0],
            },
          }
        }),
      }))
    },

    // Helpers
    getShadowById: (id) => {
      return get().shadows.find((s) => s.id === id)
    },

    getLinkedColor: (shadowId, layerIndex) => {
      const shadow = get().shadows.find((s) => s.id === shadowId)
      if (!shadow) return undefined

      const colorId = shadow.linkedColorIds[layerIndex]
      if (!colorId) return undefined

      return get().availableColors.find((c) => c.id === colorId)
    },

    getShadowsUsingColor: (colorTokenId) => {
      return get().shadows.filter((shadow) =>
        shadow.linkedColorIds.includes(colorTokenId)
      )
    },
  }
})

/**
 * Convert API shadow tokens to store format
 */
export function apiShadowsToStore(
  shadows: Record<string, W3CShadowToken> | W3CShadowToken[] | any[],
  availableColors: ColorTokenOption[] = []
): ShadowTokenWithMeta[] {
  const resolveShadowMeta = (token: Record<string, unknown>) => {
    const attributes =
      token.attributes && typeof token.attributes === 'object'
        ? (token.attributes as Record<string, unknown>)
        : undefined
    const extensions =
      token.$extensions && typeof token.$extensions === 'object'
        ? (token.$extensions as Record<string, unknown>)
        : undefined
    const getMeta = (key: string) => token[key] ?? attributes?.[key] ?? extensions?.[key]

    const nameRaw = getMeta('name')
    const shadowTypeRaw = getMeta('shadowType') ?? getMeta('shadow_type')
    const semanticRoleRaw = getMeta('semanticRole') ?? getMeta('semantic_role') ?? getMeta('role')
    const confidenceRaw = getMeta('confidence')

    return {
      name: typeof nameRaw === 'string' ? nameRaw : undefined,
      shadowType: typeof shadowTypeRaw === 'string' ? shadowTypeRaw : undefined,
      semanticRole: typeof semanticRoleRaw === 'string' ? semanticRoleRaw : undefined,
      confidence: typeof confidenceRaw === 'number' ? confidenceRaw : undefined,
    }
  }

  const buildFromW3C = (id: string, token: W3CShadowToken): ShadowTokenWithMeta => {
    const value = token.$value
    const layers = Array.isArray(value) ? value : [value]

    const linkedColorIds: string[] = []
    const originalColors: string[] = []

    for (const layer of layers) {
      const color = extractLayerColor(layer)
      if (isTokenRef(color)) {
        linkedColorIds.push(stripBraces(color))
        // For token refs, find the hex from available colors
        const colorToken = availableColors.find((c) => c.id === stripBraces(color))
        originalColors.push(colorToken?.hex || '#000000')
      } else {
        linkedColorIds.push('')
        originalColors.push(color)
      }
    }

    const meta = resolveShadowMeta(token as Record<string, unknown>)
    return {
      id,
      raw: token,
      linkedColorIds,
      originalColors,
      ...(meta.name ? { name: meta.name } : {}),
      ...(meta.shadowType ? { shadowType: meta.shadowType } : {}),
      ...(meta.semanticRole ? { semanticRole: meta.semanticRole } : {}),
      ...(meta.confidence !== undefined ? { confidence: meta.confidence } : {}),
    }
  }

  // Handle array format (from extraction API)
  if (Array.isArray(shadows)) {
    const first = shadows[0]
    if (first && typeof first === 'object' && '$value' in first) {
      return shadows.map((shadow, idx) => {
        const token = shadow as W3CShadowToken
        const id = (shadow as any).id || (shadow as any).name || `shadow.${idx + 1}`
        return buildFromW3C(id, token)
      })
    }
    return shadows.map((shadow, idx) => {
      const name = shadow.name || `shadow.${idx + 1}`
      const colorHex = shadow.color_hex || '#000000'

      // Try to find a matching color token
      const matchingColor = availableColors.find(
        (c) => c.hex.toLowerCase() === colorHex.toLowerCase()
      )

      return {
        id: name,
        raw: {
          $type: 'shadow' as const,
          $value: {
            x: { value: shadow.x_offset || 0, unit: 'px' },
            y: { value: shadow.y_offset || 0, unit: 'px' },
            blur: { value: shadow.blur_radius || 0, unit: 'px' },
            spread: { value: shadow.spread_radius || 0, unit: 'px' },
            color: matchingColor ? `{${matchingColor.id}}` : colorHex,
          },
        },
        name,
        shadowType: shadow.shadow_type || 'drop',
        semanticRole: shadow.semantic_role || 'medium',
        confidence: shadow.confidence,
        linkedColorIds: [matchingColor?.id || ''],
        originalColors: [colorHex],
      }
    })
  }

  // Handle W3C format (from design tokens API)
  return Object.entries(shadows).map(([id, token]) => buildFromW3C(id, token))
}

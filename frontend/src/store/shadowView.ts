import { useCallback, useEffect, useMemo, useState } from 'react'
import { useTokenGraphStore } from './tokenGraphStore'

export interface ShadowViewState {
  shadows: any[]
  availableColors: Array<{ id: string; hex: string; name?: string }>
  selectedShadowId: string | null
  selectShadow: (id: string | null) => void
  setShadows: (shadows: any[]) => void
  setAvailableColors: (colors: Array<{ id: string; hex: string; name?: string }>) => void
  linkColorToShadow: (shadowId: string, layerIndex: number, colorTokenId: string) => void
  unlinkColorFromShadow: (shadowId: string, layerIndex: number) => void
  updateShadowColor: (shadowId: string, layerIndex: number, hexOrTokenRef: string) => void
}

const stripBraces = (val: string) => (val.startsWith('{') && val.endsWith('}')) ? val.slice(1, -1) : val
const isTokenRef = (val: string) => typeof val === 'string' && val.startsWith('{') && val.endsWith('}')

export function useShadowViewState(): ShadowViewState {
  const graphShadowTokens = useTokenGraphStore((state) => state.shadows)
  const graphColorTokens = useTokenGraphStore((state) => state.colors)

  const graphShadows = useMemo(() => {
    return graphShadowTokens.map((tok) => {
      const rawVal = tok.raw.$value
      const layers = Array.isArray(rawVal) ? rawVal : [rawVal]
      const linkedColorIds: string[] = []
      const originalColors: string[] = []

      layers.forEach((layer) => {
        const color = (layer as any)?.color
        if (typeof color === 'string' && color.startsWith('{') && color.endsWith('}')) {
          linkedColorIds.push(stripBraces(color))
          originalColors.push('#000000')
        } else if (typeof color === 'string') {
          linkedColorIds.push('')
          originalColors.push(color)
        } else {
          linkedColorIds.push('')
          originalColors.push('#000000')
        }
      })

      const meta = tok.raw as any
      return {
        id: tok.id,
        name: meta?.name ?? tok.id,
        raw: tok.raw,
        shadowType: meta?.shadowType ?? meta?.semantic_role ?? meta?.role,
        semanticRole: meta?.semanticRole ?? meta?.semantic_role ?? meta?.role,
        confidence: meta?.confidence,
        linkedColorIds,
        originalColors,
      }
    })
  }, [graphShadowTokens])

  const graphColors = useMemo(
    () =>
      graphColorTokens.map((tok) => {
        const raw = tok.raw as any
        const val = raw?.$value
        const hex =
          (typeof val === 'object' && val?.hex) ||
          raw?.hex ||
          raw?.attributes?.hex ||
          '#cccccc'
        const name = raw?.name ?? raw?.attributes?.name
        return {
          id: tok.id,
          hex,
          name,
        }
      }),
    [graphColorTokens],
  )

  const [shadows, setShadows] = useState<any[]>(graphShadows)
  const [availableColors, setAvailableColors] = useState(graphColors)
  const [selectedShadowId, setSelectedShadowId] = useState<string | null>(null)

  const linkColorToShadow = useCallback((shadowId: string, layerIndex: number, colorTokenId: string) => {
    setShadows((current) =>
      current.map((shadow) => {
        if (shadow.id !== shadowId) return shadow
        const newLinkedColorIds = [...(shadow.linkedColorIds ?? [])]
        newLinkedColorIds[layerIndex] = colorTokenId

        const rawValue = shadow.raw.$value
        const layers = Array.isArray(rawValue) ? [...rawValue] : [{ ...rawValue }]
        if (layers[layerIndex]) {
          layers[layerIndex] = { ...layers[layerIndex], color: `{${colorTokenId}}` }
        }

        return {
          ...shadow,
          linkedColorIds: newLinkedColorIds,
          raw: { ...shadow.raw, $value: Array.isArray(rawValue) ? layers : layers[0] },
        }
      }),
    )
  }, [])

  const unlinkColorFromShadow = useCallback((shadowId: string, layerIndex: number) => {
    setShadows((current) =>
      current.map((shadow) => {
        if (shadow.id !== shadowId) return shadow
        const newLinkedColorIds = [...(shadow.linkedColorIds ?? [])]
        const originalColor = shadow.originalColors?.[layerIndex] || '#000000'
        newLinkedColorIds[layerIndex] = ''

        const rawValue = shadow.raw.$value
        const layers = Array.isArray(rawValue) ? [...rawValue] : [{ ...rawValue }]
        if (layers[layerIndex]) {
          layers[layerIndex] = { ...layers[layerIndex], color: originalColor }
        }

        return {
          ...shadow,
          linkedColorIds: newLinkedColorIds,
          raw: { ...shadow.raw, $value: Array.isArray(rawValue) ? layers : layers[0] },
        }
      }),
    )
  }, [])

  const updateShadowColor = useCallback((shadowId: string, layerIndex: number, hexOrTokenRef: string) => {
    setShadows((current) =>
      current.map((shadow) => {
        if (shadow.id !== shadowId) return shadow
        const newLinkedColorIds = [...(shadow.linkedColorIds ?? [])]
        if (isTokenRef(hexOrTokenRef)) {
          newLinkedColorIds[layerIndex] = stripBraces(hexOrTokenRef)
        } else {
          newLinkedColorIds[layerIndex] = ''
        }

        const rawValue = shadow.raw.$value
        const layers = Array.isArray(rawValue) ? [...rawValue] : [{ ...rawValue }]
        if (layers[layerIndex]) {
          layers[layerIndex] = { ...layers[layerIndex], color: hexOrTokenRef }
        }

        return {
          ...shadow,
          linkedColorIds: newLinkedColorIds,
          raw: { ...shadow.raw, $value: Array.isArray(rawValue) ? layers : layers[0] },
        }
      }),
    )
  }, [])

  const selectShadow = useCallback((id: string | null) => setSelectedShadowId(id), [])

  // Keep local colors/shadows in sync when canonical state changes
  useEffect(() => {
    setShadows(graphShadows)
  }, [graphShadows])

  useEffect(() => {
    setAvailableColors(graphColors)
  }, [graphColors])

  return {
    shadows,
    availableColors,
    selectedShadowId,
    selectShadow,
    setShadows,
    setAvailableColors,
    linkColorToShadow,
    unlinkColorFromShadow,
    updateShadowColor,
  }
}

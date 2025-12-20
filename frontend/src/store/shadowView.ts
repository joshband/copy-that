import { useCallback, useEffect, useState } from 'react'
import { useTokenGraphStore, selectLegacyShadows, selectLegacyColors } from './tokenGraphStore'

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
  const graphShadows = useTokenGraphStore(selectLegacyShadows)
  const graphColors = useTokenGraphStore(selectLegacyColors).map((c) => ({
    id: c.id,
    hex: c.hex,
    name: c.name,
  }))

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

import { create } from 'zustand'
import { ApiClient } from '../api/client'
import type {
  W3CDesignTokenResponse,
  W3CColorToken,
  W3CSpacingToken,
  W3CShadowToken,
  WCTypographyToken,
} from '../types'

type TokenCategory = 'color' | 'spacing' | 'shadow' | 'typography' | 'layout'

export interface UiTokenBase<T> {
  id: string
  category: TokenCategory
  raw: T
}

export interface UiColorToken extends UiTokenBase<W3CColorToken> {
  category: 'color'
  isAlias: boolean
  aliasTargetId?: string
}

export interface UiSpacingToken extends UiTokenBase<W3CSpacingToken> {
  category: 'spacing'
  baseId?: string
  multiplier?: number
}

export interface UiShadowToken extends UiTokenBase<W3CShadowToken> {
  category: 'shadow'
  referencedColorIds: string[]
}

export interface UiTypographyToken extends UiTokenBase<WCTypographyToken> {
  category: 'typography'
  referencedColorId?: string
  fontFamilyTokenId?: string
  fontSizeTokenId?: string
}

export interface TokenGraphState {
  loaded: boolean
  colors: UiColorToken[]
  spacing: UiSpacingToken[]
  shadows: UiShadowToken[]
  typography: UiTypographyToken[]
  layout: UiTokenBase<unknown>[]
  load: (projectId: number) => Promise<void>
  legacyColors: () => Array<{
    id: string
    hex: string
    name?: string
    confidence?: number
    isAlias: boolean
    aliasTargetId?: string
  }>
  legacySpacing: () => Array<{
    name: string
    value_px: number
    value_rem?: number
    multiplier?: number
  }>
  legacyColorExtras: () => Record<string, { isAlias: boolean; aliasTargetId?: string }>
}

const stripBraces = (val: string) => (val.startsWith('{') && val.endsWith('}')) ? val.slice(1, -1) : val

export const useTokenGraphStore = create<TokenGraphState>((set) => ({
  loaded: false,
  colors: [],
  spacing: [],
  shadows: [],
  typography: [],
  layout: [],

  async load(projectId: number) {
    const resp: W3CDesignTokenResponse = await ApiClient.getDesignTokens(projectId)

    const colors: UiColorToken[] = Object.entries(resp.color ?? {}).map(([id, token]) => {
      const val = token.$value
      let isAlias = false
      let aliasTargetId: string | undefined
      if (typeof val === 'string' && val.startsWith('{') && val.endsWith('}')) {
        isAlias = true
        aliasTargetId = stripBraces(val)
      } else if (typeof token['aliasOf'] === 'string') {
        isAlias = true
        aliasTargetId = token['aliasOf'] as string
      }
      return { id, category: 'color', raw: token, isAlias, aliasTargetId }
    })

    const spacing: UiSpacingToken[] = Object.entries(resp.spacing ?? {}).map(([id, token]) => {
      const baseId = typeof token['multipleOf'] === 'string' ? token['multipleOf'] as string : undefined
      const multiplier = typeof token['multiplier'] === 'number' ? token['multiplier'] as number : undefined
      return { id, category: 'spacing', raw: token, baseId, multiplier }
    })

    const shadows: UiShadowToken[] = Object.entries(resp.shadow ?? {}).map(([id, token]) => {
      const value = token.$value
      const layers = Array.isArray(value) ? value : [value]
      const referencedColorIds: string[] = []
      for (const layer of layers) {
        if (layer && typeof layer === 'object' && 'color' in layer && typeof (layer as any).color === 'string') {
          referencedColorIds.push(stripBraces((layer as any).color as string))
        }
      }
      return { id, category: 'shadow', raw: token, referencedColorIds }
    })

    const typography: UiTypographyToken[] = Object.entries(resp.typography ?? {}).map(([id, token]) => {
      const val = token.$value as any
      let referencedColorId: string | undefined
      let fontFamilyTokenId: string | undefined
      let fontSizeTokenId: string | undefined

      if (val?.color && typeof val.color === 'string') {
        referencedColorId = stripBraces(val.color)
      }
      if (val?.fontFamily && typeof val.fontFamily === 'string' && val.fontFamily.startsWith('{')) {
        fontFamilyTokenId = stripBraces(val.fontFamily)
      }
      const fontSizeVal = val?.fontSize
      if (fontSizeVal && typeof fontSizeVal === 'object' && 'token' in fontSizeVal) {
        fontSizeTokenId = stripBraces(String(fontSizeVal.token))
      } else if (typeof fontSizeVal === 'string' && fontSizeVal.startsWith('{')) {
        fontSizeTokenId = stripBraces(fontSizeVal)
      }

      return {
        id,
        category: 'typography',
        raw: token,
        referencedColorId,
        fontFamilyTokenId,
        fontSizeTokenId,
      }
    })

    const layout: UiTokenBase<unknown>[] = Object.entries(resp.layout ?? {}).map(([id, token]) => ({
      id,
      category: 'layout',
      raw: token,
    }))

    set({ loaded: true, colors, spacing, shadows, typography, layout })
  },
  legacyColors() {
    const state = (useTokenGraphStore.getState && useTokenGraphStore.getState()) ?? null
    const src = state?.colors ?? []
    return src.map((tok) => {
      const raw = tok.raw
      const val = (raw as any)?.$value as any
      const hex =
        (typeof val === 'object' && val?.hex) ||
        (raw as any)?.hex ||
        (raw as any)?.attributes?.hex ||
        '#cccccc'
      const confidence = (raw as any)?.confidence ?? (raw as any)?.attributes?.confidence
      const name = (raw as any)?.name ?? (raw as any)?.attributes?.name
      return {
        id: tok.id,
        hex,
        name,
        confidence,
        isAlias: tok.isAlias,
        aliasTargetId: tok.aliasTargetId,
      }
    })
  },
  legacyColorExtras() {
    const state = (useTokenGraphStore.getState && useTokenGraphStore.getState()) ?? null
    const src = state?.colors ?? []
    return src.reduce((acc, tok) => {
      acc[tok.id] = { isAlias: tok.isAlias, aliasTargetId: tok.aliasTargetId }
      return acc
    }, {} as Record<string, { isAlias: boolean; aliasTargetId?: string }>)
  },
  legacySpacing() {
    const state = (useTokenGraphStore.getState && useTokenGraphStore.getState()) ?? null
    const src = state?.spacing ?? []
    return src
      .map((tok) => {
        const val = (tok.raw as any)?.$value as any
        const px = typeof val === 'object' && val ? val.value : undefined
        if (px == null) return null
        const unit = val.unit ?? 'px'
        const value_px = typeof px === 'number' ? px : Number(px)
        const value_rem = unit === 'px' ? value_px / 16 : undefined
        return {
          name: tok.id,
          value_px,
          value_rem,
          multiplier: tok.multiplier,
        }
      })
      .filter(Boolean) as Array<{ name: string; value_px: number; value_rem?: number; multiplier?: number }>
  },
}))

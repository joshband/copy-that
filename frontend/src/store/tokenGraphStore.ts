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
}))

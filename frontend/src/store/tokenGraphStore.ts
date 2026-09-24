import { createWithEqualityFn } from 'zustand/traditional'
import { ApiClient } from '../api/client'
import type {
  W3CDesignTokenResponse,
  W3CColorToken,
  W3CSpacingToken,
  W3CShadowToken,
  WCTypographyToken,
  W3CLayoutToken,
  W3COpacityToken,
  W3CGradientToken,
  W3CDurationToken,
  W3CCubicBezierToken,
  W3CFontFamilyToken,
  W3CFontWeightToken,
  W3CStrokeStyleToken,
  W3CBorderToken,
  W3CTransitionToken,
  W3CNumberToken,
  W3CDimensionToken,
} from '../types'

type TokenCategory =
  | 'color'
  | 'spacing'
  | 'shadow'
  | 'typography'
  | 'layout'
  | 'opacity'
  | 'gradient'
  | 'duration'
  | 'cubicBezier'
  | 'fontFamily'
  | 'fontWeight'
  | 'strokeStyle'
  | 'border'
  | 'transition'
  | 'number'
  | 'dimension'

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

export interface UiLayoutToken extends UiTokenBase<W3CLayoutToken> {
  category: 'layout'
}

export interface UiOpacityToken extends UiTokenBase<W3COpacityToken> {
  category: 'opacity'
  value: number
}

export interface UiGradientToken extends UiTokenBase<W3CGradientToken> {
  category: 'gradient'
}

export interface UiDurationToken extends UiTokenBase<W3CDurationToken> {
  category: 'duration'
}

export interface UiCubicBezierToken extends UiTokenBase<W3CCubicBezierToken> {
  category: 'cubicBezier'
}

export interface UiFontFamilyToken extends UiTokenBase<W3CFontFamilyToken> {
  category: 'fontFamily'
}

export interface UiFontWeightToken extends UiTokenBase<W3CFontWeightToken> {
  category: 'fontWeight'
}

export interface UiStrokeStyleToken extends UiTokenBase<W3CStrokeStyleToken> {
  category: 'strokeStyle'
}

export interface UiBorderToken extends UiTokenBase<W3CBorderToken> {
  category: 'border'
}

export interface UiTransitionToken extends UiTokenBase<W3CTransitionToken> {
  category: 'transition'
}

export interface UiNumberToken extends UiTokenBase<W3CNumberToken> {
  category: 'number'
}

export interface UiDimensionToken extends UiTokenBase<W3CDimensionToken> {
  category: 'dimension'
}

export interface TokenGraphState {
  reset: () => void
  loaded: boolean
  colors: UiColorToken[]
  spacing: UiSpacingToken[]
  shadows: UiShadowToken[]
  typography: UiTypographyToken[]
  layout: UiLayoutToken[]
  opacity: UiOpacityToken[]
  gradient: UiGradientToken[]
  duration: UiDurationToken[]
  cubicBezier: UiCubicBezierToken[]
  fontFamily: UiFontFamilyToken[]
  fontWeight: UiFontWeightToken[]
  strokeStyle: UiStrokeStyleToken[]
  border: UiBorderToken[]
  transition: UiTransitionToken[]
  number: UiNumberToken[]
  dimension: UiDimensionToken[]
  /**
   * Optional typography recommendation returned from the API.
   * Confidence is null when the recommendation is absent or not numeric.
   * styleAttributes contains primitive keys and string/number values.
   */
  typographyRecommendation?: {
    styleAttributes?: Record<string, string | number>
    confidence?: number | null
  }
  load: (projectId: number) => Promise<void>
  legacyColors: () => Array<{
    id: string
    hex: string
    rgb?: string
    name?: string
    confidence?: number
    temperature?: string
    saturation_level?: string
    lightness_level?: string
    harmony?: string
    semantic_names?: string | Record<string, unknown>
    design_intent?: string
    usage?: string[]
    background_role?: string
    is_accent?: boolean
    prominence_percentage?: number
    isAlias: boolean
    aliasTargetId?: string
  }>
  legacySpacing: () => Array<{
    name: string
    value_px: number
    value_rem?: number
    multiplier?: number
    confidence?: number
    semantic_role?: string
    spacing_type?: string
    grid_aligned?: boolean
    tailwind_class?: string
    prominence_percentage?: number
    scale_position?: number
    related_tokens?: string[]
    usage?: string[]
    responsive_scales?: Record<string, number>
  }>
  legacyColorExtras: () => Record<string, { isAlias: boolean; aliasTargetId?: string }>
  legacyShadows: () => Array<{
    id: string
    name?: string
    raw: W3CShadowToken
    shadowType?: string
    semanticRole?: string
    confidence?: number
    linkedColorIds: string[]
    originalColors: string[]
  }>
}

const stripBraces = (val: string) => (val.startsWith('{') && val.endsWith('}')) ? val.slice(1, -1) : val

let loadRevision = 0

export const useTokenGraphStore = createWithEqualityFn<TokenGraphState>((set): TokenGraphState => ({
  loaded: false,
  colors: [],
  spacing: [],
  shadows: [],
  typography: [],
  layout: [],
  opacity: [],
  gradient: [],
  duration: [],
  cubicBezier: [],
  fontFamily: [],
  fontWeight: [],
  strokeStyle: [],
  border: [],
  transition: [],
  number: [],
  dimension: [],
  typographyRecommendation: undefined,

  reset() {
    ++loadRevision
    set({ loaded: false, colors: [], spacing: [], shadows: [], typography: [], layout: [], opacity: [], gradient: [], duration: [], cubicBezier: [], fontFamily: [], fontWeight: [], strokeStyle: [], border: [], transition: [], number: [], dimension: [], typographyRecommendation: undefined })
  },
  async load(projectId: number) {
    const revision = ++loadRevision
    const resp: W3CDesignTokenResponse = await ApiClient.getDesignTokens(projectId)
    if (revision !== loadRevision) return

    console.log('🔍 Token Graph Load - Raw Response:', resp)
    console.log('🔍 Response type:', typeof resp, 'Is Object:', resp instanceof Object)
    console.log('🔍 resp.color:', resp.color)
    console.log('🔍 resp.spacing:', resp.spacing)
    console.log('🔍 resp.typography:', resp.typography)
    console.log('🔍 Color keys:', Object.keys(resp.color ?? {}))
    console.log('🔍 Spacing keys:', Object.keys(resp.spacing ?? {}))

    const colors: UiColorToken[] = Object.entries(resp.color ?? {}).map(([id, token]) => {
      const val = token.$value
      let isAlias = false
      let aliasTargetId: string | undefined
      if (typeof val === 'string' && val.startsWith('{') && val.endsWith('}')) {
        isAlias = true
        aliasTargetId = stripBraces(val)
      } else if (typeof (token as any)['aliasOf'] === 'string') {
        isAlias = true
        aliasTargetId = (token as any)['aliasOf'] as string
      }
      return { id, category: 'color', raw: token, isAlias, aliasTargetId }
    })
    console.log('✅ Parsed colors:', colors.length, 'tokens')

    const spacing: UiSpacingToken[] = Object.entries(resp.spacing ?? {}).map(([id, token]) => {
      const baseId = typeof (token as any)['multipleOf'] === 'string' ? (token as any)['multipleOf'] as string : undefined
      const multiplier = typeof (token as any)['multiplier'] === 'number' ? (token as any)['multiplier'] as number : undefined
      return { id, category: 'spacing', raw: token, baseId, multiplier }
    })
    console.log('✅ Parsed spacing:', spacing.length, 'tokens')

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
      const fontFamilyVal = val?.fontFamily
      if (Array.isArray(fontFamilyVal) && fontFamilyVal.length && typeof fontFamilyVal[0] === 'string') {
        fontFamilyTokenId = fontFamilyVal[0].startsWith('{') ? stripBraces(fontFamilyVal[0]) : fontFamilyVal[0]
      } else if (typeof fontFamilyVal === 'string' && fontFamilyVal.startsWith('{')) {
        fontFamilyTokenId = stripBraces(fontFamilyVal)
      }
      const fontSizeVal = val?.fontSize
      if (val?.fontSizeToken && typeof val.fontSizeToken === 'string') {
        fontSizeTokenId = stripBraces(val.fontSizeToken)
      } else if (fontSizeVal && typeof fontSizeVal === 'object' && 'token' in fontSizeVal) {
        fontSizeTokenId = stripBraces(String((fontSizeVal).token))
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

    const layout: UiLayoutToken[] = Object.entries(resp.layout ?? {}).map(([id, token]) => ({
      id,
      category: 'layout',
      raw: token as W3CLayoutToken,
    }))

    const opacity: UiOpacityToken[] = Object.entries(resp.opacity ?? {}).map(([id, token]) => {
      const rawVal = (token as W3COpacityToken).$value ?? (token as { value?: number }).value
      const value = typeof rawVal === 'number' ? rawVal : Number(rawVal) || 0
      return {
        id,
        category: 'opacity' as const,
        raw: { ...token, $type: token.$type ?? 'number', $value: value } as W3COpacityToken,
        value,
      }
    })

    const gradient: UiGradientToken[] = Object.entries(resp.gradient ?? {}).map(([id, token]) => ({
      id,
      category: 'gradient',
      raw: token as W3CGradientToken,
    }))

    const duration: UiDurationToken[] = Object.entries(resp.duration ?? {}).map(([id, token]) => ({
      id,
      category: 'duration',
      raw: token as W3CDurationToken,
    }))

    const cubicBezier: UiCubicBezierToken[] = Object.entries(resp.cubicBezier ?? {}).map(
      ([id, token]) => ({
        id,
        category: 'cubicBezier',
        raw: token as W3CCubicBezierToken,
      }),
    )

    const mapSection = <T, C extends TokenCategory>(
      section: Record<string, T> | undefined,
      category: C,
    ) =>
      Object.entries(section ?? {}).map(([id, token]) => ({
        id,
        category,
        raw: token,
      }))

    const fontFamily = mapSection(resp.fontFamily as Record<string, W3CFontFamilyToken> | undefined, 'fontFamily') as UiFontFamilyToken[]
    const fontWeight = mapSection(resp.fontWeight as Record<string, W3CFontWeightToken> | undefined, 'fontWeight') as UiFontWeightToken[]
    const strokeStyle = mapSection(resp.strokeStyle as Record<string, W3CStrokeStyleToken> | undefined, 'strokeStyle') as UiStrokeStyleToken[]
    const border = mapSection(resp.border as Record<string, W3CBorderToken> | undefined, 'border') as UiBorderToken[]
    const transition = mapSection(resp.transition as Record<string, W3CTransitionToken> | undefined, 'transition') as UiTransitionToken[]
    const number = mapSection(resp.number as Record<string, W3CNumberToken> | undefined, 'number') as UiNumberToken[]
    const dimension = mapSection(resp.dimension as Record<string, W3CDimensionToken> | undefined, 'dimension') as UiDimensionToken[]

    // Extract and sanitize typography recommendation from the API response.
    const recRaw = resp.meta?.typography_recommendation
    const typographyRecommendation =
      recRaw && typeof recRaw === 'object'
        ? {
            styleAttributes:
              recRaw.style_attributes && typeof recRaw.style_attributes === 'object'
                ? (recRaw.style_attributes)
                : undefined,
            confidence:
              typeof recRaw.confidence === 'number' && !Number.isNaN(recRaw.confidence)
                ? recRaw.confidence
                : null,
          }
        : undefined

    console.log('📦 Setting store state:', {
      colorsCount: colors.length,
      spacingCount: spacing.length,
      shadowsCount: shadows.length,
      typographyCount: typography.length,
      layoutCount: layout.length,
      opacityCount: opacity.length,
      gradientCount: gradient.length,
      durationCount: duration.length,
    })

    set({
      loaded: true,
      colors,
      spacing,
      shadows,
      typography,
      layout,
      opacity,
      gradient,
      duration,
      cubicBezier,
      fontFamily,
      fontWeight,
      strokeStyle,
      border,
      transition,
      number,
      dimension,
      typographyRecommendation,
    })

    console.log('✅ Store updated! New state:', {
      loaded: true,
      colorsInStore: colors.length,
      spacingInStore: spacing.length,
      typographyInStore: typography.length,
    })
  },
  legacyColors(): Array<{
    id: string
    hex: string
    rgb?: string
    name?: string
    confidence?: number
    temperature?: string
    saturation_level?: string
    lightness_level?: string
    harmony?: string
    semantic_names?: string | Record<string, unknown>
    design_intent?: string
    usage?: string[]
    background_role?: string
    is_accent?: boolean
    prominence_percentage?: number
    isAlias: boolean
    aliasTargetId?: string
  }> {
    const state = useTokenGraphStore.getState ? useTokenGraphStore.getState() : null
    const src = state?.colors ?? []
    return src.map((tok: UiColorToken) => {
      const raw = tok.raw as any
      const val = raw?.$value
      const attributes = raw?.attributes && typeof raw.attributes === 'object' ? (raw.attributes as any) : undefined
      const extensions = raw?.$extensions && typeof raw.$extensions === 'object' ? (raw.$extensions as any) : undefined
      const readAttr = (key: string) => raw?.[key] ?? attributes?.[key] ?? extensions?.[key]
      const hexFromValue =
        (typeof val === 'object' && val?.hex) ||
        (typeof val === 'string' && val.startsWith('#') ? val : undefined)
      const hex = hexFromValue || readAttr('hex') || '#cccccc'
      const confidence = readAttr('confidence')
      const name = readAttr('name')
      const semanticRaw = readAttr('semantic_names')
      let semantic_names = semanticRaw
      if (typeof semanticRaw === 'string') {
        const trimmed = semanticRaw.trim()
        if (trimmed.startsWith('{') || trimmed.startsWith('[')) {
          try {
            semantic_names = JSON.parse(semanticRaw) as Record<string, unknown>
          } catch {
            semantic_names = semanticRaw
          }
        }
      }
      const designIntent = readAttr('design_intent')
      const usage = readAttr('usage')
      const backgroundRole = readAttr('background_role')
      const isAccent = readAttr('is_accent')
      const prominence = readAttr('prominence_percentage')
      return {
        id: tok.id,
        hex,
        rgb: readAttr('rgb'),
        name,
        confidence,
        temperature: readAttr('temperature'),
        saturation_level: readAttr('saturation_level'),
        lightness_level: readAttr('lightness_level'),
        harmony: readAttr('harmony'),
        semantic_names,
        design_intent: typeof designIntent === 'string' ? designIntent : undefined,
        usage: Array.isArray(usage) ? usage.filter((item) => typeof item === 'string') : undefined,
        background_role: typeof backgroundRole === 'string' ? backgroundRole : undefined,
        is_accent: typeof isAccent === 'boolean' ? isAccent : undefined,
        prominence_percentage: typeof prominence === 'number' ? prominence : undefined,
        isAlias: tok.isAlias,
        aliasTargetId: tok.aliasTargetId,
      }
    })
  },
  legacyColorExtras(): Record<string, { isAlias: boolean; aliasTargetId?: string }> {
    const state = useTokenGraphStore.getState ? useTokenGraphStore.getState() : null
    const src = state?.colors ?? []
    return src.reduce((acc: Record<string, { isAlias: boolean; aliasTargetId?: string }>, tok: UiColorToken) => {
      acc[tok.id] = { isAlias: tok.isAlias, aliasTargetId: tok.aliasTargetId }
      return acc
    }, {} as Record<string, { isAlias: boolean; aliasTargetId?: string }>)
  },
  legacySpacing(): Array<{
    name: string
    value_px: number
    value_rem?: number
    multiplier?: number
    confidence?: number
    semantic_role?: string
    spacing_type?: string
    grid_aligned?: boolean
    tailwind_class?: string
    prominence_percentage?: number
    scale_position?: number
    related_tokens?: string[]
    usage?: string[]
    responsive_scales?: Record<string, number>
  }> {
    const state = useTokenGraphStore.getState ? useTokenGraphStore.getState() : null
    const src = state?.spacing ?? []
    return src
      .map((tok: UiSpacingToken) => {
        const rawRecord = tok.raw && typeof tok.raw === 'object' ? (tok.raw as Record<string, unknown>) : {}
        const attributes =
          rawRecord.attributes && typeof rawRecord.attributes === 'object'
            ? (rawRecord.attributes as Record<string, unknown>)
            : undefined
        const extensions =
          rawRecord.$extensions && typeof rawRecord.$extensions === 'object'
            ? (rawRecord.$extensions as Record<string, unknown>)
            : undefined
        const getMeta = (key: string) => rawRecord[key] ?? attributes?.[key] ?? extensions?.[key]

        const val = (tok.raw)?.$value as { value?: number; unit?: string } | undefined
        const px = typeof val === 'object' && val ? val.value : undefined
        if (px == null) return null
        const unit = val?.unit ?? 'px'
        const value_px = typeof px === 'number' ? px : Number(px)
        const value_rem = unit === 'px' ? value_px / 16 : undefined
        return {
          name: tok.id,
          value_px,
          value_rem,
          multiplier: tok.multiplier,
          confidence: typeof getMeta('confidence') === 'number' ? (getMeta('confidence') as number) : undefined,
          semantic_role: typeof getMeta('semantic_role') === 'string' ? (getMeta('semantic_role') as string) : undefined,
          spacing_type: typeof getMeta('spacing_type') === 'string' ? (getMeta('spacing_type') as string) : undefined,
          grid_aligned: typeof getMeta('grid_aligned') === 'boolean' ? (getMeta('grid_aligned') as boolean) : undefined,
          tailwind_class: typeof getMeta('tailwind_class') === 'string' ? (getMeta('tailwind_class') as string) : undefined,
          prominence_percentage:
            typeof getMeta('prominence_percentage') === 'number' ? (getMeta('prominence_percentage') as number) : undefined,
          scale_position: typeof getMeta('scale_position') === 'number' ? (getMeta('scale_position') as number) : undefined,
          related_tokens: Array.isArray(getMeta('related_tokens'))
            ? (getMeta('related_tokens') as string[])
            : undefined,
          usage: Array.isArray(getMeta('usage')) ? (getMeta('usage') as string[]) : undefined,
          responsive_scales:
            getMeta('responsive_scales') && typeof getMeta('responsive_scales') === 'object'
              ? (getMeta('responsive_scales') as Record<string, number>)
              : undefined,
        }
      })
      .filter(Boolean) as Array<{
        name: string
        value_px: number
        value_rem?: number
        multiplier?: number
        confidence?: number
        semantic_role?: string
        spacing_type?: string
        grid_aligned?: boolean
        tailwind_class?: string
        prominence_percentage?: number
        scale_position?: number
        related_tokens?: string[]
        usage?: string[]
        responsive_scales?: Record<string, number>
      }>
  },
  legacyShadows(): Array<{
    id: string
    name?: string
    raw: W3CShadowToken
    shadowType?: string
    semanticRole?: string
    confidence?: number
    linkedColorIds: string[]
    originalColors: string[]
  }> {
    const state = useTokenGraphStore.getState ? useTokenGraphStore.getState() : null
    const src = state?.shadows ?? []
    return src.map((tok: UiShadowToken) => {
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
  },
}))

export const selectColors = (state: TokenGraphState) => state.colors
export const selectSpacing = (state: TokenGraphState) => state.spacing
export const selectShadows = (state: TokenGraphState) => state.shadows
export const selectTypography = (state: TokenGraphState) => state.typography
export const selectLegacyColors = (state: TokenGraphState) => state.legacyColors()
export const selectLegacySpacing = (state: TokenGraphState) => state.legacySpacing()
export const selectLegacyShadows = (state: TokenGraphState) => state.legacyShadows()

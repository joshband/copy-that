import { useMemo } from 'react'
import { useTokenGraphStore } from '../../../../../store/tokenGraphStore'
import type { TypographyTokenDetail } from './types'

function extractDimensionValue(
  value: any
): string | undefined {
  if (!value) return undefined
  if (typeof value === 'string') return value
  if (typeof value === 'object' && 'value' in value) {
    return `${value.value}${value.unit || 'px'}`
  }
  return undefined
}

export function useTypographyTokens(): TypographyTokenDetail[] {
  const typography = useTokenGraphStore((s: any) => s.typography)
  const recommendation = useTokenGraphStore((s: any) => s.typographyRecommendation)

  return useMemo(() => {
    return typography
      .map((t: any) => {
        const val = t.raw?.$value || {}
        const fontFamily = Array.isArray(val.fontFamily) ? val.fontFamily[0] : val.fontFamily
        const fontSize = extractDimensionValue(val.fontSize)
        const lineHeight = extractDimensionValue(val.lineHeight)
        const letterSpacing = extractDimensionValue(val.letterSpacing)

        return {
          id: t.id,
          fontFamily: typeof fontFamily === 'string' ? fontFamily : undefined,
          fontSize,
          fontWeight: val.fontWeight,
          lineHeight,
          letterSpacing,
          textTransform: val.casing,
          category: t.category,
          semanticRole: t.semantic_role,
          confidence: t.confidence,
          readabilityScore: t.readability_score,
          isReadable: t.is_readable,
          prominence: t.prominence_percentage,
          colorTemp: recommendation?.styleAttributes?.color_temperature,
          visualWeight: recommendation?.styleAttributes?.visual_weight,
          contrastLevel: recommendation?.styleAttributes?.contrast_level,
          primaryStyle: recommendation?.styleAttributes?.primary_style,
          vlmMood: recommendation?.styleAttributes?.vlm_mood,
          vlmComplexity: recommendation?.styleAttributes?.vlm_complexity,
          usage: t.usage
            ? typeof t.usage === 'string'
              ? JSON.parse(t.usage)
              : t.usage
            : [],
          extractionMetadata: t.extraction_metadata,
          raw: t
        }
      })
  }, [typography, recommendation])
}

export function useHasQualityMetrics(token: TypographyTokenDetail): boolean {
  return useMemo(() => {
    return (
      token.confidence != null ||
      token.readabilityScore != null ||
      token.isReadable != null ||
      token.prominence != null
    )
  }, [token.confidence, token.readabilityScore, token.isReadable, token.prominence])
}

export function useHasStyleAttributes(token: TypographyTokenDetail): boolean {
  return useMemo(() => {
    return !!(
      token.primaryStyle ||
      token.colorTemp ||
      token.visualWeight ||
      token.contrastLevel ||
      token.vlmMood
    )
  }, [
    token.primaryStyle,
    token.colorTemp,
    token.visualWeight,
    token.contrastLevel,
    token.vlmMood
  ])
}

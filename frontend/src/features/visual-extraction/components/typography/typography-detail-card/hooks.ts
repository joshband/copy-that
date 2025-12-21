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
        const rawRecord = t.raw && typeof t.raw === 'object' ? (t.raw as Record<string, unknown>) : {}
        const attributes =
          rawRecord.attributes && typeof rawRecord.attributes === 'object'
            ? (rawRecord.attributes as Record<string, unknown>)
            : undefined
        const extensions =
          rawRecord.$extensions && typeof rawRecord.$extensions === 'object'
            ? (rawRecord.$extensions as Record<string, unknown>)
            : undefined
        const getMeta = (key: string) => t?.[key] ?? rawRecord[key] ?? attributes?.[key] ?? extensions?.[key]
        const val = (t.raw?.$value as Record<string, unknown>) || {}
        const fontFamily = Array.isArray(val.fontFamily) ? val.fontFamily[0] : val.fontFamily
        const fontSize = extractDimensionValue(val.fontSize)
        const lineHeight = extractDimensionValue(val.lineHeight)
        const letterSpacing = extractDimensionValue(val.letterSpacing)
        const usageRaw = getMeta('usage')
        let usage: string[] = []
        if (Array.isArray(usageRaw)) {
          usage = usageRaw.filter((item) => typeof item === 'string') as string[]
        } else if (typeof usageRaw === 'string') {
          try {
            const parsed = JSON.parse(usageRaw)
            usage = Array.isArray(parsed) ? parsed.filter((item) => typeof item === 'string') : [usageRaw]
          } catch {
            usage = [usageRaw]
          }
        }

        return {
          id: t.id,
          fontFamily: typeof fontFamily === 'string' ? fontFamily : undefined,
          fontSize,
          fontWeight: val.fontWeight,
          lineHeight,
          letterSpacing,
          textTransform: val.casing,
          category: t.category,
          semanticRole: typeof getMeta('semantic_role') === 'string' ? (getMeta('semantic_role') as string) : undefined,
          confidence: typeof getMeta('confidence') === 'number' ? (getMeta('confidence') as number) : undefined,
          readabilityScore:
            typeof getMeta('readability_score') === 'number' ? (getMeta('readability_score') as number) : undefined,
          isReadable: typeof getMeta('is_readable') === 'boolean' ? (getMeta('is_readable') as boolean) : undefined,
          prominence:
            typeof getMeta('prominence_percentage') === 'number'
              ? (getMeta('prominence_percentage') as number)
              : undefined,
          colorTemp: recommendation?.styleAttributes?.color_temperature,
          visualWeight: recommendation?.styleAttributes?.visual_weight,
          contrastLevel: recommendation?.styleAttributes?.contrast_level,
          primaryStyle: recommendation?.styleAttributes?.primary_style,
          vlmMood: recommendation?.styleAttributes?.vlm_mood,
          vlmComplexity: recommendation?.styleAttributes?.vlm_complexity,
          usage,
          extractionMetadata:
            getMeta('extraction_metadata') && typeof getMeta('extraction_metadata') === 'object'
              ? (getMeta('extraction_metadata') as Record<string, unknown>)
              : undefined,
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

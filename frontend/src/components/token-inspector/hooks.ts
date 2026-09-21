import { useEffect, useMemo, useRef, useState } from 'react'
import type { SpacingExtractionResponse, ColorToken, SegmentedColor } from '../../types'
import type { TokenRow, ColorMap } from './types'

const deriveType = (metric: NonNullable<SpacingExtractionResponse['component_spacing_metrics']>[number]) => {
  if (metric.padding && Object.values(metric.padding).some((v) => (v ?? 0) > 8)) {
    return 'container'
  }
  if (metric.neighbor_gap && metric.neighbor_gap > 0) {
    return 'element'
  }
  return 'node'
}

export const useTokens = (spacingResult: SpacingExtractionResponse | undefined | null): TokenRow[] => {
  return useMemo(() => {
    const metrics = spacingResult?.component_spacing_metrics ?? []
    const metricTokens = metrics
      .map((m, idx) => ({ metric: m, idx }))
      .filter(({ metric }) => Array.isArray(metric.box) && metric.box.length === 4)
      .map(({ metric, idx }) => ({
        id: metric.index ?? idx,
        type: metric.element_type ?? deriveType(metric),
        box: metric.box as [number, number, number, number],
        polygon: undefined,
        text: metric.text,
        elementType: metric.element_type,
        source: 'cv',
      }))

    const fastsam = spacingResult?.fastsam_tokens ?? []
    const segmentTokens = fastsam
      .filter((seg) => Array.isArray(seg.bbox) && seg.bbox.length === 4)
      .map((seg, idx) => ({
        id: seg.id ?? `seg-${idx}`,
        type: seg.type ?? (seg as any).element_type ?? 'segment',
        box: seg.bbox,
        polygon: seg.polygon,
        text: undefined,
        elementType: (seg as any).element_type,
        source: seg.source ?? 'fastsam',
      }))

    const textTokens = (spacingResult?.text_tokens ?? []).map((t, idx) => ({
      id: t.id ?? `text-${idx}`,
      type: t.type ?? (t as any).element_type ?? 'text',
      box: t.bbox,
      polygon: undefined,
      text: t.text,
      elementType: t.type ?? 'text',
      source: t.source ?? 'layoutparser',
    }))

    const uiedTokens = (spacingResult?.uied_tokens ?? []).map((t, idx) => ({
      id: t.id ?? `uied-${idx}`,
      type: (t as any).element_type ?? t.type ?? 'component',
      box: t.bbox,
      polygon: undefined,
      text: t.text,
      elementType: (t as any).element_type ?? t.uied_label ?? t.type,
      source: t.source ?? 'uied',
    }))

    return [...metricTokens, ...segmentTokens, ...textTokens, ...uiedTokens]
  }, [spacingResult?.component_spacing_metrics, spacingResult?.fastsam_tokens, spacingResult?.text_tokens, spacingResult?.uied_tokens])
}

export const useMetricById = (spacingResult: SpacingExtractionResponse | undefined | null) => {
  return useMemo(() => {
    const metrics = spacingResult?.component_spacing_metrics ?? []
    const map = new Map<number, (typeof metrics)[number]>()
    metrics.forEach((m, idx) => {
      map.set(m.index ?? idx, m)
    })
    return map
  }, [spacingResult?.component_spacing_metrics])
}

export const useFallbackColors = (
  colors: ColorToken[],
  segmentedPalette: SegmentedColor[] | undefined | null,
): string[] => {
  return useMemo(() => {
    if (segmentedPalette?.length) {
      return segmentedPalette.map((s) => s.hex)
    }
    return colors.map((c) => c.hex)
  }, [colors, segmentedPalette])
}

export const useCanvasColorSampling = (
  overlaySrc: string | null,
  tokens: TokenRow[],
) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const [colorMap, setColorMap] = useState<ColorMap>({})

  useEffect(() => {
    if (!overlaySrc || !tokens.length) {
      setColorMap({})
      return
    }
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.src = overlaySrc
    img.onload = () => {
      const canvas = canvasRef.current
      if (!canvas) return
      canvas.width = img.naturalWidth
      canvas.height = img.naturalHeight
      const ctx = canvas.getContext('2d')
      if (!ctx) return
      ctx.drawImage(img, 0, 0)
      const next: ColorMap = {}
      tokens.forEach((token) => {
        const [x, y, w, h] = token.box
        const cx = Math.min(Math.max(Math.round(x + w / 2), 0), img.naturalWidth - 1)
        const cy = Math.min(Math.max(Math.round(y + h / 2), 0), img.naturalHeight - 1)
        const data = ctx.getImageData(cx, cy, 1, 1).data
        const hex = `#${[data[0], data[1], data[2]].map((v) => v.toString(16).padStart(2, '0')).join('')}`
        next[token.id] = hex
      })
      setColorMap(next)
    }
  }, [overlaySrc, tokens])

  return { canvasRef, colorMap }
}

export const useFilteredTokens = (tokens: TokenRow[], filter: string): TokenRow[] => {
  return useMemo(() => {
    const term = filter.trim().toLowerCase()
    if (!term) return tokens
    return tokens.filter(
      (token) =>
        String(token.id).toLowerCase().includes(term) ||
        token.type.toLowerCase().includes(term) ||
        token.text?.toLowerCase().includes(term) ||
        token.source?.toLowerCase().includes(term),
    )
  }, [tokens, filter])
}

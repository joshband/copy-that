import { useEffect, useMemo, useRef, useState } from 'react'
import type { SpacingExtractionResponse } from '../types'
import { FALLBACK_TOLERANCE, type PaletteEntry, type SpacingEntry } from './types'

const computeFallbackSpacings = (componentMetrics: SpacingExtractionResponse['component_spacing_metrics']) => {
  if (!componentMetrics?.length) return []
  const counts = new Map<number, number>()
  componentMetrics.forEach((metric) => {
    if (metric.neighbor_gap != null) {
      const rounded = Math.round(metric.neighbor_gap)
      counts.set(rounded, (counts.get(rounded) ?? 0) + 1)
    }
    if (metric.padding) {
      Object.values(metric.padding).forEach((val) => {
        const rounded = Math.round(val)
        counts.set(rounded, (counts.get(rounded) ?? 0) + 1)
      })
    }
  })
  return [...counts.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 6)
    .map<SpacingEntry>(([value_px, count]) => ({
      value_px,
      count,
      orientation: 'mixed',
    }))
}

export const useCommonSpacings = (
  componentMetrics: SpacingExtractionResponse['component_spacing_metrics'] | undefined,
  commonSpacings: SpacingExtractionResponse['common_spacings'] | undefined,
): SpacingEntry[] => {
  return useMemo(() => {
    if (commonSpacings?.length) {
      return commonSpacings
    }
    return computeFallbackSpacings(componentMetrics)
  }, [componentMetrics, commonSpacings])
}

export const useOverlayDimensions = (overlaySrc: string | null) => {
  const imgRef = useRef<HTMLImageElement | null>(null)
  const [dimensions, setDimensions] = useState({
    naturalWidth: 0,
    naturalHeight: 0,
    clientWidth: 0,
    clientHeight: 0,
  })

  useEffect(() => {
    const img = imgRef.current
    if (!img) return undefined
    const update = () =>
      setDimensions({
        naturalWidth: img.naturalWidth || 1,
        naturalHeight: img.naturalHeight || 1,
        clientWidth: img.clientWidth || 1,
        clientHeight: img.clientHeight || 1,
      })
    update()
    window.addEventListener('resize', update)
    return () => window.removeEventListener('resize', update)
  }, [overlaySrc])

  return { imgRef, dimensions }
}

export const useMatchingBoxes = (
  componentMetrics: SpacingExtractionResponse['component_spacing_metrics'] | undefined,
  selectedComponent: number | null,
  selectedSpacing: number | null,
) => {
  return useMemo(() => {
    if (!componentMetrics?.length) return []
    const byGap = selectedSpacing != null
      ? componentMetrics
          .map((metric, idx) => ({ metric, idx }))
          .filter(
            ({ metric }) =>
              metric.neighbor_gap != null &&
              Math.abs(Math.round(metric.neighbor_gap) - (selectedSpacing ?? 0)) <= FALLBACK_TOLERANCE,
          )
      : []
    const bySelection =
      selectedComponent != null
        ? componentMetrics
            .map((metric, idx) => ({ metric, idx }))
            .filter(({ idx }) => idx === selectedComponent)
        : []
    const combined = [...byGap, ...bySelection]
    const unique = new Map<number, { metric: (typeof componentMetrics)[number]; idx: number }>()
    combined.forEach((entry) => {
      if (!unique.has(entry.idx)) unique.set(entry.idx, entry)
    })
    return [...unique.values()]
  }, [componentMetrics, selectedComponent, selectedSpacing])
}

export const useAlignmentLines = (
  spacingResult: SpacingExtractionResponse | undefined | null,
  dimensions: { naturalWidth: number; naturalHeight: number; clientWidth: number; clientHeight: number },
) => {
  return useMemo(() => {
    if (!spacingResult?.alignment || !dimensions.naturalWidth || !dimensions.naturalHeight) return []
    const sx = dimensions.clientWidth / dimensions.naturalWidth
    const sy = dimensions.clientHeight / dimensions.naturalHeight
    const lines: Array<{ orientation: 'vertical' | 'horizontal'; pos: number }> = []
    const addLines = (vals: number[] | undefined, orientation: 'vertical' | 'horizontal') => {
      if (!vals) return
      vals.forEach((v) => lines.push({ orientation, pos: v }))
    }
    addLines(spacingResult.alignment.left, 'vertical')
    addLines(spacingResult.alignment.center_x, 'vertical')
    addLines(spacingResult.alignment.right, 'vertical')
    addLines(spacingResult.alignment.top, 'horizontal')
    addLines(spacingResult.alignment.center_y, 'horizontal')
    addLines(spacingResult.alignment.bottom, 'horizontal')
    return lines.map((line) => {
      if (line.orientation === 'vertical') {
        return {
          orientation: 'vertical' as const,
          style: { left: line.pos * sx },
        }
      }
      return {
        orientation: 'horizontal' as const,
        style: { top: line.pos * sy },
      }
    })
  }, [dimensions.clientHeight, dimensions.clientWidth, dimensions.naturalHeight, dimensions.naturalWidth, spacingResult?.alignment])
}

export const usePayloadInfo = (
  componentMetrics: SpacingExtractionResponse['component_spacing_metrics'] | undefined,
  commonSpacings: SpacingEntry[],
  spacingResult: SpacingExtractionResponse | undefined | null,
  fastsamTokens: SpacingExtractionResponse['fastsam_tokens'] | undefined,
) => {
  return useMemo(() => {
    const items: Array<{ label: string; value: string }> = []
    items.push({ label: 'components', value: String(componentMetrics?.length || 0) })
    items.push({ label: 'common spacings', value: String(commonSpacings.length || 0) })
    if (spacingResult?.alignment) {
      const totalLines = Object.values(spacingResult.alignment).reduce(
        (sum, vals) => sum + ((vals as number[] | undefined)?.length ?? 0),
        0,
      )
      items.push({ label: 'alignment lines', value: `${totalLines} lines` })
    }
    if (spacingResult?.gap_clusters) {
      const gx = spacingResult.gap_clusters.x?.join(', ') || '—'
      const gy = spacingResult.gap_clusters.y?.join(', ') || '—'
      items.push({ label: 'gap clusters', value: `x: ${gx} | y: ${gy}` })
    }
    items.push({
      label: 'debug overlay',
      value: spacingResult?.debug_overlay ? 'yes' : 'no',
    })
    items.push({
      label: 'warnings',
      value: spacingResult?.warnings?.length ? spacingResult.warnings.join(' | ') : 'none',
    })
    items.push({
      label: 'fastsam segments',
      value: `${fastsamTokens?.length || 0}`,
    })
    return items
  }, [commonSpacings.length, componentMetrics?.length, spacingResult?.alignment, spacingResult?.debug_overlay, spacingResult?.gap_clusters, spacingResult?.warnings, fastsamTokens?.length])
}

export const useScalePolygon = (
  dimensions: { naturalWidth: number; naturalHeight: number; clientWidth: number; clientHeight: number },
) => {
  return (poly?: Array<[number, number]>) => {
    if (!poly?.length || !dimensions.naturalWidth || !dimensions.naturalHeight) return null
    const sx = dimensions.clientWidth / dimensions.naturalWidth
    const sy = dimensions.clientHeight / dimensions.naturalHeight
    return poly.map(([x, y]) => [x * sx, y * sy] as [number, number])
  }
}

export const useRenderBox = (
  dimensions: { naturalWidth: number; naturalHeight: number; clientWidth: number; clientHeight: number },
) => {
  return (box: [number, number, number, number]) => {
    if (!dimensions.naturalWidth || !dimensions.naturalHeight) return null
    const [x, y, w, h] = box
    const scaleX = dimensions.clientWidth / dimensions.naturalWidth
    const scaleY = dimensions.clientHeight / dimensions.naturalHeight
    return {
      left: x * scaleX,
      top: y * scaleY,
      width: Math.max(w * scaleX, 2),
      height: Math.max(h * scaleY, 2),
    }
  }
}

import { useMemo, useState } from 'react'
import type { ColorToken, SegmentedColor, SpacingExtractionResponse } from '../../types'
import { SpacingDiagnostics } from './SpacingDiagnostics'
import { ColorPalettePicker } from './ColorPalettePicker'
import { OverlayPreview } from './OverlayPreview'
import {
  useAlignmentLines,
  useCommonSpacings,
  useMatchingBoxes,
  useOverlayDimensions,
  usePayloadInfo,
  useRenderBox,
  useScalePolygon,
} from './hooks'
import type { PaletteEntry, Props } from './types'

const toDataUrl = (base64?: string | null) =>
  base64 ? `data:image/png;base64,${base64}` : null

export default function DiagnosticsPanel({
  colors,
  spacingResult,
  spacingOverlay,
  colorOverlay,
  segmentedPalette,
  showAlignment = true,
  showPayload = false,
}: Props) {
  const [selectedSpacing, setSelectedSpacing] = useState<number | null>(null)
  const [selectedComponent, setSelectedComponent] = useState<number | null>(null)
  const [selectedColor, setSelectedColor] = useState<string | null>(null)
  const [showAlignmentLines, setShowAlignmentLines] = useState(false)
  const [showSegments, setShowSegments] = useState(false)

  const componentMetrics = spacingResult?.component_spacing_metrics ?? []
  const fastsamTokens = spacingResult?.fastsam_tokens ?? []

  const commonSpacings = useCommonSpacings(componentMetrics, spacingResult?.common_spacings)
  const { imgRef, dimensions } = useOverlayDimensions(toDataUrl(spacingOverlay ?? spacingResult?.debug_overlay) ?? toDataUrl(colorOverlay))
  const matchingBoxes = useMatchingBoxes(componentMetrics, selectedComponent, selectedSpacing)
  const alignmentLines = useAlignmentLines(spacingResult, dimensions)
  const payloadInfo = usePayloadInfo(componentMetrics, commonSpacings, spacingResult, fastsamTokens)
  const scalePolygon = useScalePolygon(dimensions)
  const renderBox = useRenderBox(dimensions)

  const palette: PaletteEntry[] = useMemo(() => {
    if (segmentedPalette?.length) {
      return segmentedPalette
        .slice(0, 10)
        .map((seg, idx) => ({ hex: seg.hex, coverage: seg.coverage, label: `Segment ${idx + 1}` }))
    }
    return colors.slice(0, 10).map((c, idx) => ({
      hex: c.hex,
      coverage: c.prominence_percentage ?? 0,
      label: c.name ?? `Color ${idx + 1}`,
    }))
  }, [colors, segmentedPalette])

  const overlaySrc = toDataUrl(spacingOverlay ?? spacingResult?.debug_overlay) ?? toDataUrl(colorOverlay)

  return (
    <div className="diagnostics">
      <div className="diagnostics-header">
        <div>
          <p className="eyebrow">Diagnostics</p>
          <h3>Spacing & color QA</h3>
          <p className="diagnostics-subtitle">
            Inspect common gaps and the extracted palette. Click a spacing value to highlight
            matching regions; click a component or swatch to focus details.
          </p>
        </div>
      </div>

      <div className="diagnostics-grid">
        <SpacingDiagnostics
          commonSpacings={commonSpacings}
          componentMetrics={componentMetrics}
          spacingResult={spacingResult}
          selectedSpacing={selectedSpacing}
          selectedComponent={selectedComponent}
          showPayload={showPayload}
          payloadInfo={payloadInfo}
          onSpacingSelect={setSelectedSpacing}
          onComponentSelect={setSelectedComponent}
        />

        <ColorPalettePicker
          palette={palette}
          selectedColor={selectedColor}
          onColorSelect={setSelectedColor}
        />

        {showAlignment && (
          <div style={{ display: 'contents' }}>
            <button
              onClick={() => setShowAlignmentLines((s) => !s)}
              style={{ gridColumn: '1 / -1', display: 'none' }}
            >
              {showAlignmentLines ? 'Hide alignment overlay' : 'Show alignment overlay'}
            </button>
          </div>
        )}

        <OverlayPreview
          overlaySrc={overlaySrc}
          fastsamTokens={fastsamTokens}
          matchingBoxes={matchingBoxes}
          alignmentLines={alignmentLines}
          dimensions={dimensions}
          showSegments={showSegments}
          showAlignmentLines={showAlignmentLines}
          selectedSpacing={selectedSpacing}
          selectedComponent={selectedComponent}
          onSegmentsToggle={() => setShowSegments((s) => !s)}
          scalePolygon={scalePolygon}
          renderBox={renderBox}
        />
      </div>
    </div>
  )
}

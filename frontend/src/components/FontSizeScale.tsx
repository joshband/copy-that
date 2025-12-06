import React from 'react'
import { useTokenGraphStore } from '../store/tokenGraphStore'

interface FontSize {
  label: string
  size: number
  unit: string
  sizeString: string
  fontFamily?: string
  fontWeight?: number | string
  usage: number
  confidence: number
}

/**
 * Font Size Scale
 * Shows typography sizes as a visual hierarchy scale
 */
export default function FontSizeScale() {
  const typography = useTokenGraphStore((s: any) => s.typography)

  // Extract unique font sizes and build scale
  const fontSizes = new Map<string, FontSize>()

  typography.forEach((t: any) => {
    const val = t.raw?.$value || {}
    const fontSize = val.fontSize
    let sizeNum = 0
    let unit = 'px'

    if (fontSize && typeof fontSize === 'object' && 'value' in fontSize) {
      sizeNum = fontSize.value
      unit = fontSize.unit || 'px'
    } else if (typeof fontSize === 'string') {
      const match = fontSize.match(/(\d+(?:\.\d+)?)(.*?)$/)
      if (match) {
        sizeNum = parseFloat(match[1])
        unit = match[2] || 'px'
      }
    } else if (typeof fontSize === 'number') {
      sizeNum = fontSize
    }

    if (sizeNum === 0) return

    const sizeKey = `${sizeNum}${unit}`
    if (!fontSizes.has(sizeKey)) {
      fontSizes.set(sizeKey, {
        label: t.id || `size-${sizeNum}`,
        size: sizeNum,
        unit,
        sizeString: sizeKey,
        fontFamily: Array.isArray(val.fontFamily) ? val.fontFamily[0] : val.fontFamily,
        fontWeight: val.fontWeight,
        usage: 0,
        confidence: t.confidence || 0.8,
      })
    }

    const font = fontSizes.get(sizeKey)!
    font.usage += 1
  })

  if (fontSizes.size === 0) {
    return null
  }

  const sortedSizes = Array.from(fontSizes.values()).sort((a, b) => a.size - b.size)
  const maxSize = Math.max(...sortedSizes.map(s => s.size))
  const minSize = Math.min(...sortedSizes.map(s => s.size))

  return (
    <div className="font-size-scale">
      <div className="size-scale-title">Font Size Hierarchy</div>
      <p className="size-scale-subtitle">Visual scale of typography sizes</p>

      <div className="size-scale-container">
        {sortedSizes.map((fontSize, idx) => {
          const scaledPercent = ((fontSize.size - minSize) / (maxSize - minSize)) * 100
          const displaySize = fontSize.size + fontSize.unit

          return (
            <div key={fontSize.sizeString} className="size-scale-row">
              <div className="size-scale-label">{fontSize.label}</div>

              <div className="size-scale-bar-container">
                <div
                  className="size-scale-bar"
                  style={{
                    '--size-percent': scaledPercent,
                  } as React.CSSProperties}
                />
              </div>

              <div className="size-scale-values">
                <span className="size-value mono">{displaySize}</span>
                <span className="size-preview"
                  style={{
                    fontSize: displaySize,
                    fontFamily: fontSize.fontFamily,
                    fontWeight: fontSize.fontWeight,
                  }}
                >
                  Aa
                </span>
              </div>

              <div className="size-scale-meta">
                <span className="meta-usage">{fontSize.usage}x</span>
                <div className="meta-confidence" style={{ '--confidence': fontSize.confidence } as React.CSSProperties}>
                  {Math.round(fontSize.confidence * 100)}%
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Legend */}
      <div className="size-scale-legend">
        <div className="legend-item">
          <span className="legend-label">Usage</span>
          <span className="legend-value">Times used in design</span>
        </div>
        <div className="legend-item">
          <span className="legend-label">Confidence</span>
          <span className="legend-value">Extraction quality</span>
        </div>
      </div>
    </div>
  )
}

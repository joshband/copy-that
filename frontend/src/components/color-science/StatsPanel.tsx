import React from 'react'
import { ColorToken } from './types'

interface StatsPanelProps {
  colors: ColorToken[]
  extractorUsed: string
  paletteDescription: string
}

export function StatsPanel({ colors, extractorUsed, paletteDescription }: StatsPanelProps) {
  const avgConfidence = colors.length > 0 ? (colors.reduce((a, c) => a + c.confidence, 0) / colors.length * 100).toFixed(0) : '0'
  const wcagAACount = colors.filter(c => c.wcag_aa_compliant_text).length

  return (
    <section className="panel-card stats-section">
      <div className="stats-grid">
        <div className="stat-item">
          <div className="stat-value">{colors.length}</div>
          <div className="stat-label">Colors</div>
        </div>
        <div className="stat-item">
          <div className="stat-value">{avgConfidence}%</div>
          <div className="stat-label">Avg Confidence</div>
        </div>
        <div className="stat-item">
          <div className="stat-value">{wcagAACount}</div>
          <div className="stat-label">WCAG AA</div>
        </div>
        <div className="stat-item">
          <div className="stat-value">{extractorUsed}</div>
          <div className="stat-label">Extractor</div>
        </div>
      </div>
      {paletteDescription && <p className="palette-description">{paletteDescription}</p>}
    </section>
  )
}

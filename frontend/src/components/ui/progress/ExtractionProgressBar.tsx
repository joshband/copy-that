import React, { useMemo } from 'react'
import './ExtractionProgressBar.css'

interface Stage {
  id: string
  label: string
  status: 'pending' | 'running' | 'complete' | 'error'
}

interface Props {
  /**
   * Overall progress 0-100 for streaming phase
   */
  streamProgress?: number
  /**
   * Pipeline stages
   */
  stages?: Stage[]
  /**
   * Current active stage
   */
  activeStage?: string
  /**
   * Colors extracted so far
   */
  colorsExtracted?: number
  /**
   * Target color count
   */
  targetColors?: number
  /**
   * Show detailed timing info
   */
  showTiming?: boolean
  /**
   * Extraction start time for timing calculations
   */
  startTime?: number
}

export const ExtractionProgressBar: React.FC<Props> = ({
  streamProgress = 0,
  stages = [],
  activeStage,
  colorsExtracted = 0,
  targetColors,
  showTiming = false,
  startTime,
}) => {
  const elapsedSeconds = useMemo(() => {
    if (!startTime) return 0
    return Math.round((Date.now() - startTime) / 1000)
  }, [startTime])

  const colorsPercentage = useMemo(() => {
    if (!targetColors || targetColors === 0) return 0
    return Math.round((colorsExtracted / targetColors) * 100)
  }, [colorsExtracted, targetColors])

  return (
    <div className="extraction-progress">
      {/* Stream Progress Bar */}
      {streamProgress > 0 && streamProgress < 100 && (
        <div className="progress-section">
          <div className="progress-header">
            <span className="progress-label">Extracting colors...</span>
            <span className="progress-percentage">{Math.round(streamProgress)}%</span>
          </div>
          <div className="progress-bar-container">
            <div
              className="progress-bar-fill"
              style={{ width: `${streamProgress}%` }}
            />
          </div>
        </div>
      )}

      {/* Color Count */}
      {colorsExtracted > 0 && (
        <div className="colors-info">
          <span className="colors-label">
            Extracted {colorsExtracted}{targetColors ? ` of ${targetColors}` : ''} colors
          </span>
          {targetColors && colorsPercentage > 0 && (
            <span className="colors-percentage">{colorsPercentage}%</span>
          )}
        </div>
      )}

      {/* Pipeline Stages */}
      {stages.length > 0 && (
        <div className="pipeline-stages">
          {stages.map((stage, index) => (
            <div key={stage.id} className="stage-row">
              <div className={`stage-indicator ${stage.status}`}>
                {stage.status === 'complete' && <span className="check-mark">✓</span>}
                {stage.status === 'running' && <span className="spinner">⟳</span>}
                {stage.status === 'pending' && <span className="dot">•</span>}
                {stage.status === 'error' && <span className="error-mark">✕</span>}
              </div>
              <span className={`stage-label ${stage.status === 'running' ? 'active' : ''}`}>
                {stage.label}
              </span>
              {stage.id === activeStage && stage.status === 'running' && (
                <span className="stage-status">Running...</span>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Timing Info */}
      {showTiming && startTime && elapsedSeconds > 0 && (
        <div className="timing-info">
          <span className="timing-label">Elapsed: {elapsedSeconds}s</span>
        </div>
      )}
    </div>
  )
}

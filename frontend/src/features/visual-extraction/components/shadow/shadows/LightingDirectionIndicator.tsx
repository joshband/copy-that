/**
 * LightingDirectionIndicator Component
 * Phase 4: Advanced Analysis
 *
 * Visual compass-style indicator showing light direction and elevation
 */

import { useMemo } from 'react'
import type {
  LightDirection,
  LightDirectionToken,
  LightingStyleToken,
} from '../../types/shadowAnalysis'
import {
  getLightDirectionLabel,
  getLightingStyleLabel,
  azimuthToCompassDirection,
} from '../../types/shadowAnalysis'
import './LightingDirectionIndicator.css'

export interface LightingDirectionIndicatorProps {
  /** Light direction in radians */
  direction?: LightDirection | null
  /** Categorical direction token */
  directionToken?: LightDirectionToken
  /** Lighting style */
  lightingStyle?: LightingStyleToken
  /** Confidence in direction detection (0-1) */
  confidence?: number
  /** Size of the indicator */
  size?: 'sm' | 'md' | 'lg'
  /** Show detailed info */
  showDetails?: boolean
}

const DIRECTION_TOKEN_TO_DEGREES: Record<LightDirectionToken, number> = {
  upper_left: 315,
  upper_right: 45,
  left: 270,
  right: 90,
  overhead: 0,
  front: 180,
  back: 0,
  unknown: 0,
}

export function LightingDirectionIndicator({
  direction,
  directionToken = 'unknown',
  lightingStyle = 'diffuse',
  confidence = 0,
  size = 'md',
  showDetails = true,
}: LightingDirectionIndicatorProps) {
  // Calculate rotation angle
  const rotationAngle = useMemo(() => {
    if (direction) {
      // Convert azimuth (radians) to degrees, adjusted for CSS rotation
      return (direction.azimuth * 180) / Math.PI - 90
    }
    return DIRECTION_TOKEN_TO_DEGREES[directionToken] - 90
  }, [direction, directionToken])

  // Calculate elevation indicator position
  const elevationPercent = useMemo(() => {
    if (direction) {
      // Elevation 0 = horizon, PI/2 = zenith
      return (direction.elevation / (Math.PI / 2)) * 100
    }
    // Estimate from token
    if (directionToken === 'overhead') return 90
    if (directionToken.includes('upper')) return 60
    return 30
  }, [direction, directionToken])

  // Confidence affects opacity and styling
  const confidenceClass = useMemo(() => {
    if (confidence >= 0.8) return 'high'
    if (confidence >= 0.5) return 'medium'
    return 'low'
  }, [confidence])

  const compassDir = useMemo(() => {
    if (direction) {
      return azimuthToCompassDirection(direction.azimuth)
    }
    return directionToken.replace('_', ' ').replace('upper ', '').toUpperCase().charAt(0)
  }, [direction, directionToken])

  const isUnknown = directionToken === 'unknown' && !direction

  return (
    <div className={`lighting-direction-indicator ${size}`}>
      {/* Compass Circle */}
      <div className={`compass-container confidence-${confidenceClass}`}>
        <div className="compass-ring">
          {/* Cardinal directions */}
          <span className="cardinal n">N</span>
          <span className="cardinal e">E</span>
          <span className="cardinal s">S</span>
          <span className="cardinal w">W</span>

          {/* Center point */}
          <div className="compass-center">
            {isUnknown ? (
              <span className="unknown-indicator">?</span>
            ) : (
              <>
                {/* Light direction arrow */}
                <div
                  className="direction-arrow"
                  style={{ transform: `rotate(${rotationAngle}deg)` }}
                >
                  <div className="arrow-head" />
                  <div className="arrow-tail" />
                </div>

                {/* Elevation indicator (dot size) */}
                <div
                  className="elevation-dot"
                  style={{
                    width: `${8 + elevationPercent * 0.12}px`,
                    height: `${8 + elevationPercent * 0.12}px`,
                  }}
                />
              </>
            )}
          </div>
        </div>

        {/* Confidence ring */}
        <svg className="confidence-ring" viewBox="0 0 100 100">
          <circle className="confidence-bg" cx="50" cy="50" r="46" />
          <circle
            className="confidence-fill"
            cx="50"
            cy="50"
            r="46"
            strokeDasharray={`${confidence * 289} 289`}
          />
        </svg>
      </div>

      {/* Details */}
      {showDetails && (
        <div className="direction-details">
          <div className="detail-row primary">
            <span className="direction-label">{getLightDirectionLabel(directionToken)}</span>
            {direction && <span className="compass-badge">{compassDir}</span>}
          </div>

          <div className="detail-row secondary">
            <span className="style-label">{getLightingStyleLabel(lightingStyle)}</span>
          </div>

          <div className="detail-row metrics">
            <div className="metric">
              <span className="metric-label">Confidence</span>
              <span className={`metric-value confidence-${confidenceClass}`}>
                {Math.round(confidence * 100)}%
              </span>
            </div>
            {direction && (
              <div className="metric">
                <span className="metric-label">Elevation</span>
                <span className="metric-value">{Math.round(elevationPercent)}%</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default LightingDirectionIndicator

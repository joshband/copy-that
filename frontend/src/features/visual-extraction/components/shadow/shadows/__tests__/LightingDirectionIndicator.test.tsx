/**
 * Tests for LightingDirectionIndicator Component
 * Phase 4: Advanced Analysis
 */

import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { LightingDirectionIndicator } from '../LightingDirectionIndicator'

describe('LightingDirectionIndicator', () => {
  describe('Basic Rendering', () => {
    it('should render the compass container', () => {
      render(<LightingDirectionIndicator />)
      expect(document.querySelector('.compass-container')).toBeInTheDocument()
    })

    it('should render cardinal directions', () => {
      render(<LightingDirectionIndicator />)
      expect(screen.getByText('N')).toBeInTheDocument()
      expect(screen.getByText('E')).toBeInTheDocument()
      expect(screen.getByText('S')).toBeInTheDocument()
      expect(screen.getByText('W')).toBeInTheDocument()
    })

    it('should render with default size md', () => {
      render(<LightingDirectionIndicator />)
      expect(document.querySelector('.lighting-direction-indicator.md')).toBeInTheDocument()
    })
  })

  describe('Size Variants', () => {
    it('should render small size', () => {
      render(<LightingDirectionIndicator size="sm" />)
      expect(document.querySelector('.lighting-direction-indicator.sm')).toBeInTheDocument()
    })

    it('should render large size', () => {
      render(<LightingDirectionIndicator size="lg" />)
      expect(document.querySelector('.lighting-direction-indicator.lg')).toBeInTheDocument()
    })
  })

  describe('Direction Token Display', () => {
    it('should display Upper Left direction', () => {
      render(<LightingDirectionIndicator directionToken="upper_left" showDetails={true} />)
      expect(screen.getByText('Upper Left')).toBeInTheDocument()
    })

    it('should display Right direction', () => {
      render(<LightingDirectionIndicator directionToken="right" showDetails={true} />)
      expect(screen.getByText('Right')).toBeInTheDocument()
    })

    it('should display Overhead direction', () => {
      render(<LightingDirectionIndicator directionToken="overhead" showDetails={true} />)
      expect(screen.getByText('Overhead')).toBeInTheDocument()
    })

    it('should display Unknown for unknown direction', () => {
      render(<LightingDirectionIndicator directionToken="unknown" showDetails={true} />)
      expect(screen.getByText('Unknown')).toBeInTheDocument()
    })
  })

  describe('Lighting Style Display', () => {
    it('should display Directional style', () => {
      render(<LightingDirectionIndicator lightingStyle="directional" showDetails={true} />)
      expect(screen.getByText('Directional')).toBeInTheDocument()
    })

    it('should display Diffuse / Ambient style', () => {
      render(<LightingDirectionIndicator lightingStyle="diffuse" showDetails={true} />)
      expect(screen.getByText('Diffuse / Ambient')).toBeInTheDocument()
    })

    it('should display Rim Light style', () => {
      render(<LightingDirectionIndicator lightingStyle="rim" showDetails={true} />)
      expect(screen.getByText('Rim Light')).toBeInTheDocument()
    })
  })

  describe('Confidence Display', () => {
    it('should display confidence percentage', () => {
      render(<LightingDirectionIndicator confidence={0.85} showDetails={true} />)
      expect(screen.getByText('85%')).toBeInTheDocument()
    })

    it('should have high confidence class for >= 0.8', () => {
      render(<LightingDirectionIndicator confidence={0.9} />)
      expect(document.querySelector('.confidence-high')).toBeInTheDocument()
    })

    it('should have medium confidence class for >= 0.5', () => {
      render(<LightingDirectionIndicator confidence={0.6} />)
      expect(document.querySelector('.confidence-medium')).toBeInTheDocument()
    })

    it('should have low confidence class for < 0.5', () => {
      render(<LightingDirectionIndicator confidence={0.3} />)
      expect(document.querySelector('.confidence-low')).toBeInTheDocument()
    })
  })

  describe('Light Direction (Radians)', () => {
    it('should render direction arrow when direction provided', () => {
      render(
        <LightingDirectionIndicator
          direction={{ azimuth: Math.PI / 4, elevation: Math.PI / 4 }}
        />
      )
      expect(document.querySelector('.direction-arrow')).toBeInTheDocument()
    })

    it('should render elevation dot when direction provided', () => {
      render(
        <LightingDirectionIndicator
          direction={{ azimuth: 0, elevation: Math.PI / 3 }}
        />
      )
      expect(document.querySelector('.elevation-dot')).toBeInTheDocument()
    })

    it('should display compass badge when direction provided', () => {
      render(
        <LightingDirectionIndicator
          direction={{ azimuth: 0, elevation: 0 }}
          showDetails={true}
        />
      )
      expect(document.querySelector('.compass-badge')).toBeInTheDocument()
    })
  })

  describe('Unknown State', () => {
    it('should show unknown indicator when direction is unknown and no radians', () => {
      render(<LightingDirectionIndicator directionToken="unknown" direction={null} />)
      expect(document.querySelector('.unknown-indicator')).toBeInTheDocument()
    })

    it('should show question mark for unknown state', () => {
      render(<LightingDirectionIndicator directionToken="unknown" />)
      expect(screen.getByText('?')).toBeInTheDocument()
    })
  })

  describe('Show Details Toggle', () => {
    it('should show details section by default', () => {
      render(<LightingDirectionIndicator />)
      expect(document.querySelector('.direction-details')).toBeInTheDocument()
    })

    it('should hide details when showDetails is false', () => {
      render(<LightingDirectionIndicator showDetails={false} />)
      expect(document.querySelector('.direction-details')).not.toBeInTheDocument()
    })
  })

  describe('Confidence Ring', () => {
    it('should render confidence ring SVG', () => {
      render(<LightingDirectionIndicator confidence={0.7} />)
      expect(document.querySelector('.confidence-ring')).toBeInTheDocument()
    })

    it('should have confidence fill circle', () => {
      render(<LightingDirectionIndicator confidence={0.5} />)
      expect(document.querySelector('.confidence-fill')).toBeInTheDocument()
    })
  })
})

/**
 * Tests for ShadowQualityMetrics Component
 * Phase 4: Advanced Analysis
 */

import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ShadowQualityMetrics } from '../ShadowQualityMetrics'

describe('ShadowQualityMetrics', () => {
  const defaultProps = {
    shadowAreaFraction: 0.25,
    meanShadowIntensity: 0.3,
    meanLitIntensity: 0.8,
    shadowContrast: 0.6,
    edgeSoftness: 0.4,
    shadowCount: 3,
    confidence: 0.85,
  }

  describe('Basic Rendering', () => {
    it('should render the metrics container', () => {
      render(<ShadowQualityMetrics {...defaultProps} />)
      expect(document.querySelector('.shadow-quality-metrics')).toBeInTheDocument()
    })

    it('should render with grid layout by default', () => {
      render(<ShadowQualityMetrics {...defaultProps} />)
      expect(document.querySelector('.layout-grid')).toBeInTheDocument()
    })
  })

  describe('Layout Variants', () => {
    it('should render horizontal layout', () => {
      render(<ShadowQualityMetrics {...defaultProps} layout="horizontal" />)
      expect(document.querySelector('.layout-horizontal')).toBeInTheDocument()
    })

    it('should render vertical layout', () => {
      render(<ShadowQualityMetrics {...defaultProps} layout="vertical" />)
      expect(document.querySelector('.layout-vertical')).toBeInTheDocument()
    })
  })

  describe('Summary Cards', () => {
    it('should render quality score card', () => {
      render(<ShadowQualityMetrics {...defaultProps} />)
      expect(screen.getByText('Quality Score')).toBeInTheDocument()
    })

    it('should render shadow count card', () => {
      render(<ShadowQualityMetrics {...defaultProps} />)
      expect(screen.getByText('Shadows Found')).toBeInTheDocument()
      expect(screen.getByText('3')).toBeInTheDocument()
    })

    it('should render contrast ratio card', () => {
      render(<ShadowQualityMetrics {...defaultProps} />)
      expect(screen.getByText('Contrast Ratio')).toBeInTheDocument()
    })

    it('should render confidence card', () => {
      render(<ShadowQualityMetrics {...defaultProps} />)
      expect(screen.getByText('Confidence')).toBeInTheDocument()
      expect(screen.getByText('85%')).toBeInTheDocument()
    })
  })

  describe('Metric Bars', () => {
    it('should render shadow coverage bar', () => {
      render(<ShadowQualityMetrics {...defaultProps} />)
      expect(screen.getByText('Shadow Coverage')).toBeInTheDocument()
    })

    it('should render shadow contrast bar', () => {
      render(<ShadowQualityMetrics {...defaultProps} />)
      expect(screen.getByText('Shadow Contrast')).toBeInTheDocument()
    })

    it('should render edge softness bar', () => {
      render(<ShadowQualityMetrics {...defaultProps} />)
      expect(screen.getByText('Edge Softness')).toBeInTheDocument()
    })

    it('should render shadow intensity bar', () => {
      render(<ShadowQualityMetrics {...defaultProps} />)
      expect(screen.getByText('Shadow Intensity')).toBeInTheDocument()
    })

    it('should render lit region intensity bar', () => {
      render(<ShadowQualityMetrics {...defaultProps} />)
      expect(screen.getByText('Lit Region Intensity')).toBeInTheDocument()
    })

    it('should display percentage values', () => {
      render(<ShadowQualityMetrics shadowAreaFraction={0.25} />)
      expect(screen.getByText('25%')).toBeInTheDocument()
    })
  })

  describe('Token Display', () => {
    it('should display softness token when provided', () => {
      render(
        <ShadowQualityMetrics
          {...defaultProps}
          tokens={{ softness: 'medium' }}
        />
      )
      expect(screen.getByText('medium')).toBeInTheDocument()
    })

    it('should display contrast token when provided', () => {
      render(
        <ShadowQualityMetrics
          {...defaultProps}
          tokens={{ contrast: 'high' }}
        />
      )
      expect(screen.getByText('high')).toBeInTheDocument()
    })

    it('should display density token when provided', () => {
      render(
        <ShadowQualityMetrics
          {...defaultProps}
          tokens={{ density: 'moderate' }}
        />
      )
      expect(screen.getByText('moderate')).toBeInTheDocument()
    })

    it('should render token pills section when tokens provided', () => {
      render(
        <ShadowQualityMetrics
          {...defaultProps}
          tokens={{ softness: 'soft', contrast: 'high', density: 'sparse' }}
        />
      )
      expect(screen.getByText('Detected Characteristics:')).toBeInTheDocument()
    })
  })

  describe('Confidence Variants', () => {
    it('should show success variant for high confidence', () => {
      render(<ShadowQualityMetrics {...defaultProps} confidence={0.9} />)
      expect(document.querySelector('.variant-success')).toBeInTheDocument()
    })

    it('should show warning variant for medium confidence', () => {
      render(<ShadowQualityMetrics {...defaultProps} confidence={0.6} />)
      expect(document.querySelector('.variant-warning')).toBeInTheDocument()
    })

    it('should show error variant for low confidence', () => {
      render(<ShadowQualityMetrics {...defaultProps} confidence={0.3} />)
      expect(document.querySelector('.variant-error')).toBeInTheDocument()
    })
  })

  describe('Compact Mode', () => {
    it('should render compact mode when enabled', () => {
      render(<ShadowQualityMetrics {...defaultProps} compact={true} />)
      expect(document.querySelector('.shadow-quality-metrics.compact')).toBeInTheDocument()
    })

    it('should show compact metrics in compact mode', () => {
      render(<ShadowQualityMetrics {...defaultProps} compact={true} />)
      expect(document.querySelector('.compact-metrics')).toBeInTheDocument()
    })

    it('should show coverage in compact mode', () => {
      render(<ShadowQualityMetrics shadowAreaFraction={0.25} compact={true} />)
      expect(screen.getByText('Coverage')).toBeInTheDocument()
      expect(screen.getByText('25%')).toBeInTheDocument()
    })

    it('should show contrast in compact mode', () => {
      render(<ShadowQualityMetrics shadowContrast={0.6} compact={true} />)
      expect(screen.getByText('Contrast')).toBeInTheDocument()
      expect(screen.getByText('60%')).toBeInTheDocument()
    })

    it('should show quality score in compact mode', () => {
      render(<ShadowQualityMetrics {...defaultProps} compact={true} />)
      expect(screen.getByText('Quality')).toBeInTheDocument()
    })
  })

  describe('Edge Cases', () => {
    it('should handle zero values', () => {
      render(
        <ShadowQualityMetrics
          shadowAreaFraction={0}
          meanShadowIntensity={0}
          meanLitIntensity={0}
          shadowContrast={0}
          edgeSoftness={0}
          shadowCount={0}
          confidence={0}
        />
      )
      expect(document.querySelector('.shadow-quality-metrics')).toBeInTheDocument()
    })

    it('should handle high contrast ratio', () => {
      render(
        <ShadowQualityMetrics
          meanShadowIntensity={0}
          meanLitIntensity={0.9}
        />
      )
      expect(screen.getByText('High')).toBeInTheDocument()
    })

    it('should handle undefined tokens', () => {
      render(<ShadowQualityMetrics {...defaultProps} tokens={undefined} />)
      expect(document.querySelector('.metrics-tokens')).not.toBeInTheDocument()
    })
  })

  describe('Quality Score Calculation', () => {
    it('should display calculated quality score', () => {
      render(<ShadowQualityMetrics {...defaultProps} />)
      // Quality score should be displayed as percentage
      expect(screen.getByText('Quality Score')).toBeInTheDocument()
    })

    it('should reflect high confidence in quality score', () => {
      render(<ShadowQualityMetrics {...defaultProps} confidence={0.95} />)
      expect(document.querySelector('.variant-success')).toBeInTheDocument()
    })
  })
})

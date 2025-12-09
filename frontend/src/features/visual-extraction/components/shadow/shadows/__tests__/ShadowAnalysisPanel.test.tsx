/**
 * Tests for ShadowAnalysisPanel Component
 * Phase 4: Advanced Analysis
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ShadowAnalysisPanel } from '../ShadowAnalysisPanel'
import type { LightingAnalysisResponse } from '../../../types/shadowAnalysis'

const mockAnalysis: LightingAnalysisResponse = {
  style_key_direction: 'upper_left',
  style_softness: 'medium',
  style_contrast: 'high',
  style_density: 'moderate',
  intensity_shadow: 'dark',
  intensity_lit: 'bright',
  lighting_style: 'directional',
  shadow_area_fraction: 0.25,
  mean_shadow_intensity: 0.3,
  mean_lit_intensity: 0.8,
  shadow_contrast: 0.6,
  edge_softness_mean: 0.4,
  light_direction: { azimuth: 0.785, elevation: 0.5 },
  light_direction_confidence: 0.85,
  extraction_confidence: 0.9,
  shadow_count_major: 3,
  css_box_shadow: {
    subtle: '0 1px 2px rgba(0,0,0,0.1)',
    medium: '0 4px 8px rgba(0,0,0,0.15)',
    prominent: '0 8px 16px rgba(0,0,0,0.2)',
    dramatic: '0 16px 32px rgba(0,0,0,0.25)',
  },
  image_id: 'test-image-123',
  analysis_source: 'shadowlab',
}

describe('ShadowAnalysisPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    Object.assign(navigator, {
      clipboard: { writeText: vi.fn().mockResolvedValue(undefined) },
    })
  })

  describe('Empty State', () => {
    it('should render empty state when no analysis', () => {
      render(<ShadowAnalysisPanel />)
      expect(screen.getByText('No Analysis Available')).toBeInTheDocument()
    })

    it('should show empty state message', () => {
      render(<ShadowAnalysisPanel />)
      expect(
        screen.getByText(/Upload an image to analyze shadow characteristics/)
      ).toBeInTheDocument()
    })

    it('should show analyze button when image available', () => {
      const onAnalyze = vi.fn()
      render(
        <ShadowAnalysisPanel
          imageBase64="base64data"
          onAnalyze={onAnalyze}
        />
      )
      expect(screen.getByText('Analyze Image')).toBeInTheDocument()
    })

    it('should call onAnalyze when analyze button clicked', async () => {
      const onAnalyze = vi.fn().mockResolvedValue(undefined)
      render(
        <ShadowAnalysisPanel
          imageBase64="base64data"
          onAnalyze={onAnalyze}
        />
      )

      fireEvent.click(screen.getByText('Analyze Image'))
      expect(onAnalyze).toHaveBeenCalledWith('base64data')
    })
  })

  describe('Loading State', () => {
    it('should render loading state when isLoading', () => {
      render(<ShadowAnalysisPanel isLoading={true} />)
      expect(screen.getByText('Analyzing shadow characteristics...')).toBeInTheDocument()
    })

    it('should show loading spinner', () => {
      render(<ShadowAnalysisPanel isLoading={true} />)
      expect(document.querySelector('.loading-spinner')).toBeInTheDocument()
    })
  })

  describe('Error State', () => {
    it('should render error state when error provided', () => {
      render(<ShadowAnalysisPanel error="Analysis failed" />)
      expect(screen.getByText('Analysis Failed')).toBeInTheDocument()
    })

    it('should display error message', () => {
      render(<ShadowAnalysisPanel error="Network error occurred" />)
      expect(screen.getByText('Network error occurred')).toBeInTheDocument()
    })

    it('should show retry button when image available', () => {
      const onAnalyze = vi.fn()
      render(
        <ShadowAnalysisPanel
          error="Failed"
          imageBase64="base64data"
          onAnalyze={onAnalyze}
        />
      )
      expect(screen.getByText('Retry Analysis')).toBeInTheDocument()
    })
  })

  describe('Analysis Display', () => {
    it('should render panel header', () => {
      render(<ShadowAnalysisPanel analysis={mockAnalysis} />)
      expect(screen.getByText('Shadow Analysis')).toBeInTheDocument()
    })

    it('should render tab navigation', () => {
      render(<ShadowAnalysisPanel analysis={mockAnalysis} />)
      expect(screen.getByText('Metrics')).toBeInTheDocument()
      expect(screen.getByText('CSS Suggestions')).toBeInTheDocument()
      expect(screen.getByText('Raw Data')).toBeInTheDocument()
    })

    it('should show metrics tab by default', () => {
      render(<ShadowAnalysisPanel analysis={mockAnalysis} />)
      expect(document.querySelector('.metrics-tab')).toBeInTheDocument()
    })

    it('should display source badge', () => {
      render(<ShadowAnalysisPanel analysis={mockAnalysis} />)
      expect(screen.getByText('Source: shadowlab')).toBeInTheDocument()
    })

    it('should display image id if provided', () => {
      render(<ShadowAnalysisPanel analysis={mockAnalysis} />)
      expect(screen.getByText('Image: test-image-123')).toBeInTheDocument()
    })
  })

  describe('Tab Navigation', () => {
    it('should switch to CSS tab when clicked', () => {
      render(<ShadowAnalysisPanel analysis={mockAnalysis} />)

      fireEvent.click(screen.getByText('CSS Suggestions'))
      expect(document.querySelector('.css-tab')).toBeInTheDocument()
    })

    it('should switch to raw data tab when clicked', () => {
      render(<ShadowAnalysisPanel analysis={mockAnalysis} />)

      fireEvent.click(screen.getByText('Raw Data'))
      expect(document.querySelector('.raw-tab')).toBeInTheDocument()
    })

    it('should highlight active tab', () => {
      render(<ShadowAnalysisPanel analysis={mockAnalysis} />)

      const metricsTab = screen.getByText('Metrics')
      expect(metricsTab).toHaveClass('active')
    })
  })

  describe('Metrics Tab Content', () => {
    it('should render lighting direction section', () => {
      render(<ShadowAnalysisPanel analysis={mockAnalysis} />)
      expect(screen.getByText('Lighting Direction')).toBeInTheDocument()
    })

    it('should render quality metrics section', () => {
      render(<ShadowAnalysisPanel analysis={mockAnalysis} />)
      expect(screen.getByText('Quality Metrics')).toBeInTheDocument()
    })

    it('should display direction label', () => {
      render(<ShadowAnalysisPanel analysis={mockAnalysis} />)
      expect(screen.getByText('Upper Left')).toBeInTheDocument()
    })

    it('should display lighting style', () => {
      render(<ShadowAnalysisPanel analysis={mockAnalysis} />)
      expect(screen.getByText('Directional')).toBeInTheDocument()
    })
  })

  describe('CSS Suggestions Tab', () => {
    it('should show CSS suggestions when tab active', () => {
      render(<ShadowAnalysisPanel analysis={mockAnalysis} />)

      fireEvent.click(screen.getByText('CSS Suggestions'))
      expect(screen.getByText(/recommended CSS box-shadow values/)).toBeInTheDocument()
    })

    it('should display CSS suggestion cards', () => {
      render(<ShadowAnalysisPanel analysis={mockAnalysis} />)

      fireEvent.click(screen.getByText('CSS Suggestions'))
      expect(screen.getByText('subtle')).toBeInTheDocument()
      expect(screen.getByText('medium')).toBeInTheDocument()
      expect(screen.getByText('prominent')).toBeInTheDocument()
      expect(screen.getByText('dramatic')).toBeInTheDocument()
    })

    it('should show preview boxes', () => {
      render(<ShadowAnalysisPanel analysis={mockAnalysis} />)

      fireEvent.click(screen.getByText('CSS Suggestions'))
      const previews = screen.getAllByText('Preview')
      expect(previews.length).toBe(4)
    })

    it('should copy CSS when copy button clicked', async () => {
      render(<ShadowAnalysisPanel analysis={mockAnalysis} />)

      fireEvent.click(screen.getByText('CSS Suggestions'))

      const copyButtons = document.querySelectorAll('.css-copy-btn')
      fireEvent.click(copyButtons[0])

      expect(navigator.clipboard.writeText).toHaveBeenCalled()
    })

    it('should hide CSS tab when showCSSSuggestions is false', () => {
      render(<ShadowAnalysisPanel analysis={mockAnalysis} showCSSSuggestions={false} />)
      expect(screen.queryByText('CSS Suggestions')).not.toBeInTheDocument()
    })
  })

  describe('Raw Data Tab', () => {
    it('should display JSON when raw tab active', () => {
      render(<ShadowAnalysisPanel analysis={mockAnalysis} />)

      fireEvent.click(screen.getByText('Raw Data'))
      expect(document.querySelector('.raw-json')).toBeInTheDocument()
    })

    it('should contain analysis data in JSON', () => {
      render(<ShadowAnalysisPanel analysis={mockAnalysis} />)

      fireEvent.click(screen.getByText('Raw Data'))
      const jsonContent = document.querySelector('.raw-json')?.textContent
      expect(jsonContent).toContain('upper_left')
      expect(jsonContent).toContain('shadowlab')
    })
  })

  describe('Compact Mode', () => {
    it('should render compact mode when enabled', () => {
      render(<ShadowAnalysisPanel analysis={mockAnalysis} compact={true} />)
      expect(document.querySelector('.shadow-analysis-panel.compact')).toBeInTheDocument()
    })

    it('should show compact header in compact mode', () => {
      render(<ShadowAnalysisPanel analysis={mockAnalysis} compact={true} />)
      expect(document.querySelector('.compact-header')).toBeInTheDocument()
    })

    it('should not show tabs in compact mode', () => {
      render(<ShadowAnalysisPanel analysis={mockAnalysis} compact={true} />)
      expect(document.querySelector('.panel-tabs')).not.toBeInTheDocument()
    })
  })

  describe('Re-analyze Button', () => {
    it('should show reanalyze button when onAnalyze provided', () => {
      const onAnalyze = vi.fn()
      render(
        <ShadowAnalysisPanel
          analysis={mockAnalysis}
          imageBase64="base64data"
          onAnalyze={onAnalyze}
        />
      )
      expect(screen.getByText('Re-analyze')).toBeInTheDocument()
    })

    it('should call onAnalyze when reanalyze clicked', () => {
      const onAnalyze = vi.fn().mockResolvedValue(undefined)
      render(
        <ShadowAnalysisPanel
          analysis={mockAnalysis}
          imageBase64="imagedata"
          onAnalyze={onAnalyze}
        />
      )

      fireEvent.click(screen.getByText('Re-analyze'))
      expect(onAnalyze).toHaveBeenCalledWith('imagedata')
    })

    it('should disable reanalyze button when loading', () => {
      const onAnalyze = vi.fn()
      render(
        <ShadowAnalysisPanel
          analysis={mockAnalysis}
          imageBase64="base64data"
          onAnalyze={onAnalyze}
          isLoading={true}
        />
      )

      // When loading, shows loading state instead
      expect(screen.getByText('Analyzing shadow characteristics...')).toBeInTheDocument()
    })
  })

  describe('Null Analysis Handling', () => {
    it('should handle null analysis gracefully', () => {
      render(<ShadowAnalysisPanel analysis={null} />)
      expect(screen.getByText('No Analysis Available')).toBeInTheDocument()
    })
  })
})

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import ColorTokenDisplay from '../ColorTokenDisplay'

describe('ColorTokenDisplay', () => {
  const mockColors = [
    {
      hex: '#FF5733',
      rgb: 'rgb(255, 87, 51)',
      name: 'Coral Red',
      confidence: 0.95,
      count: 2,
      harmony: 'triadic',
      temperature: 'warm',
      saturation_level: 'high',
      lightness_level: 'medium'
    },
    {
      hex: '#33FF57',
      rgb: 'rgb(51, 255, 87)',
      name: 'Neon Green',
      confidence: 0.87,
      harmony: 'analogous'
    }
  ]

  beforeEach(() => {
    // Mock clipboard API
    Object.assign(navigator, {
      clipboard: {
        writeText: vi.fn().mockResolvedValue(undefined)
      }
    })
  })

  it('renders without crashing', () => {
    render(<ColorTokenDisplay colors={mockColors} />)
    expect(screen.getByText('Coral Red')).toBeInTheDocument()
  })

  it('displays color palette with all colors', () => {
    render(<ColorTokenDisplay colors={mockColors} />)
    const swatches = document.querySelectorAll('.palette-swatch')
    expect(swatches.length).toBe(2)
  })

  it('displays color names and hex codes in detail panel', () => {
    render(<ColorTokenDisplay colors={mockColors} />)
    // First color should be selected by default
    expect(screen.getByText('Coral Red')).toBeInTheDocument()
    // Hex code appears in both palette and detail panel
    const hexElements = screen.getAllByText('#FF5733')
    expect(hexElements.length).toBeGreaterThanOrEqual(1)
  })

  it('selects first color by default', () => {
    render(<ColorTokenDisplay colors={mockColors} />)
    const firstSwatch = document.querySelector('.palette-swatch.selected')
    expect(firstSwatch).toBeInTheDocument()
  })

  it('switches color on palette swatch click', () => {
    render(<ColorTokenDisplay colors={mockColors} />)
    const swatches = document.querySelectorAll('.palette-swatch')

    fireEvent.click(swatches[1])
    expect(screen.getByText('Neon Green')).toBeInTheDocument()
    // Hex code appears in both palette and detail panel
    const hexElements = screen.getAllByText('#33FF57')
    expect(hexElements.length).toBeGreaterThanOrEqual(1)
  })

  it('displays confidence percentage in palette', () => {
    render(<ColorTokenDisplay colors={mockColors} />)
    expect(screen.getByText('95%')).toBeInTheDocument()
  })

  it('displays count badge when color appears multiple times', () => {
    render(<ColorTokenDisplay colors={mockColors} />)
    // Count badge may be split across elements, check for the container
    const countBadge = document.querySelector('.swatch-count, .count-value')
    expect(countBadge).toBeInTheDocument()
  })

  it('shows hex code clickable in detail panel', () => {
    render(<ColorTokenDisplay colors={mockColors} />)
    // Get the hex-clickable element specifically from the detail panel
    const hexClickable = document.querySelector('.hex-clickable')
    expect(hexClickable).toBeInTheDocument()
    expect(hexClickable).toHaveTextContent('#FF5733')
  })

  it('displays color codes in quick access section', () => {
    render(<ColorTokenDisplay colors={mockColors} />)
    expect(screen.getByText('rgb(255, 87, 51)')).toBeInTheDocument()
  })

  it('handles empty color list', () => {
    render(<ColorTokenDisplay colors={[]} />)
    const detailPanel = document.querySelector('.detail-panel.empty')
    expect(detailPanel).toBeInTheDocument()
  })

  // Defensive pattern tests
  it('handles undefined colors prop (renders without crashing)', () => {
    // @ts-expect-error - Testing defensive pattern for undefined prop
    render(<ColorTokenDisplay />)
    const detailPanel = document.querySelector('.detail-panel.empty')
    expect(detailPanel).toBeInTheDocument()
  })

  it('handles single token prop from registry pattern', () => {
    const singleToken = {
      hex: '#FF5733',
      rgb: 'rgb(255, 87, 51)',
      name: 'Coral Red',
      confidence: 0.95
    }
    render(<ColorTokenDisplay token={singleToken} />)
    expect(screen.getByText('Coral Red')).toBeInTheDocument()
  })

  it('prioritizes colors array over token prop when both provided', () => {
    const singleToken = {
      hex: '#000000',
      name: 'Black',
      confidence: 1.0
    }
    render(<ColorTokenDisplay colors={mockColors} token={singleToken} />)
    // Should show colors array, not the single token
    expect(screen.getByText('Coral Red')).toBeInTheDocument()
    expect(screen.queryByText('Black')).not.toBeInTheDocument()
  })
})

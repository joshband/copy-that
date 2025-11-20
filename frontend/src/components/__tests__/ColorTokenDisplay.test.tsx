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

  it('displays color names and hex codes', () => {
    render(<ColorTokenDisplay colors={mockColors} />)
    expect(screen.getByText('Coral Red')).toBeInTheDocument()
    expect(screen.getByText('#FF5733')).toBeInTheDocument()
    expect(screen.getByText('Neon Green')).toBeInTheDocument()
    expect(screen.getByText('#33FF57')).toBeInTheDocument()
  })

  it('displays confidence indicators', () => {
    render(<ColorTokenDisplay colors={mockColors} />)
    const confidenceBars = document.querySelectorAll('.confidence-bar-small')
    expect(confidenceBars.length).toBe(2)
  })

  it('displays count badge when color appears multiple times', () => {
    render(<ColorTokenDisplay colors={mockColors} />)
    expect(screen.getByText('2x')).toBeInTheDocument()
  })

  it('expands and collapses card on header click', () => {
    render(<ColorTokenDisplay colors={mockColors} />)
    const firstCard = document.querySelector('.token-card')
    const header = firstCard?.querySelector('.card-header')

    expect(firstCard).toHaveClass('collapsed')
    fireEvent.click(header as Element)
    expect(firstCard).toHaveClass('expanded')
  })

  it('displays copy button for hex code', () => {
    render(<ColorTokenDisplay colors={mockColors} />)
    const firstCard = document.querySelector('.token-card')
    const header = firstCard?.querySelector('.card-header')
    fireEvent.click(header as Element)

    const copyButtons = screen.getAllByRole('button')
    expect(copyButtons.length).toBeGreaterThan(0)
  })

  it('renders multiple color cards for multiple colors', () => {
    render(<ColorTokenDisplay colors={mockColors} />)
    const cards = document.querySelectorAll('.token-card')
    expect(cards.length).toBe(2)
  })

  it('handles empty color list', () => {
    render(<ColorTokenDisplay colors={[]} />)
    const container = document.querySelector('.color-tokens')
    expect(container).toBeInTheDocument()
  })
})

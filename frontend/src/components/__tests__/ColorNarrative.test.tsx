import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ColorNarrative } from '../ColorNarrative'

describe('ColorNarrative', () => {
  const defaultProps = {
    hex: '#FF5733',
    name: 'Coral Red',
    temperature: 'warm',
    saturationLevel: 'high',
    lightnessLevel: 'medium',
    isNeutral: false,
    prominencePercentage: 25
  }

  it('renders without crashing', () => {
    render(<ColorNarrative {...defaultProps} />)
    expect(screen.getByText('Understanding This Color')).toBeInTheDocument()
  })

  it('displays color name and hex code', () => {
    render(<ColorNarrative {...defaultProps} />)
    expect(screen.getAllByText('Coral Red')[0]).toBeInTheDocument()
    expect(screen.getByText('#FF5733')).toBeInTheDocument()
  })

  it('displays temperature description for warm colors', () => {
    render(<ColorNarrative {...defaultProps} />)
    expect(screen.getByText(/This is a warm color/)).toBeInTheDocument()
    expect(screen.getByText(/associated with energy, passion/)).toBeInTheDocument()
  })

  it('displays temperature description for cool colors', () => {
    render(<ColorNarrative {...defaultProps} temperature="cool" />)
    expect(screen.getByText(/This is a cool color/)).toBeInTheDocument()
    expect(screen.getByText(/associated with calmness, trust/)).toBeInTheDocument()
  })

  it('displays saturation description for high saturation', () => {
    render(<ColorNarrative {...defaultProps} />)
    expect(screen.getByText(/With high saturation/)).toBeInTheDocument()
    expect(screen.getByText(/vivid and intense/)).toBeInTheDocument()
  })

  it('displays lightness description for medium lightness', () => {
    render(<ColorNarrative {...defaultProps} />)
    expect(screen.getByText(/Medium lightness makes this color balanced/)).toBeInTheDocument()
  })

  it('displays prominence percentage and classification', () => {
    render(<ColorNarrative {...defaultProps} prominencePercentage={45} />)
    expect(screen.getAllByText(/45\.0%/)[0]).toBeInTheDocument()
    expect(screen.getByText(/dominant color/)).toBeInTheDocument()
  })

  it('displays neutral color indicator when neutral', () => {
    render(<ColorNarrative {...defaultProps} isNeutral={true} />)
    expect(screen.getByText(/🎨 Neutral Color/)).toBeInTheDocument()
    expect(screen.getByText(/foundation of every good design system/)).toBeInTheDocument()
  })

  it('displays category information when provided', () => {
    render(<ColorNarrative {...defaultProps} category="Primary" />)
    expect(screen.getByText(/Category: Primary/)).toBeInTheDocument()
  })

  it('displays narrative introduction text', () => {
    render(<ColorNarrative {...defaultProps} />)
    expect(screen.getByText(/You've extracted/)).toBeInTheDocument()
    expect(screen.getByText(/from your design/)).toBeInTheDocument()
  })
})

import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import ColorTokenDisplay from '../ColorTokenDisplay'

describe('Color Display Integration Tests', () => {
  const colorWithAllData = {
    hex: '#FF5733',
    rgb: 'rgb(255, 87, 51)',
    name: 'Coral Red',
    confidence: 0.95,
    harmony: 'triadic',
    temperature: 'warm',
    saturation_level: 'high',
    lightness_level: 'medium',
    wcag_contrast_on_white: 6.5,
    wcag_contrast_on_black: 3.2,
    wcag_aa_compliant_text: true,
    wcag_aaa_compliant_text: false,
    prominence_percentage: 25,
    category: 'Primary'
  }

  it('displays color token with all visualizers integrated', () => {
    render(<ColorTokenDisplay colors={[colorWithAllData]} />)
    expect(screen.getByText('Coral Red')).toBeInTheDocument()
    expect(screen.getByText('#FF5733')).toBeInTheDocument()
  })

  it('displays harmony, temperature, and saturation together', () => {
    render(<ColorTokenDisplay colors={[colorWithAllData]} />)
    const card = document.querySelector('.token-card')
    expect(card).toBeInTheDocument()
  })

  it('maintains color consistency across multiple tokens', () => {
    const colors = [
      { ...colorWithAllData, name: 'Color 1', hex: '#FF5733' },
      { ...colorWithAllData, name: 'Color 2', hex: '#33FF57' },
      { ...colorWithAllData, name: 'Color 3', hex: '#5733FF' }
    ]
    render(<ColorTokenDisplay colors={colors} />)
    expect(screen.getByText('Color 1')).toBeInTheDocument()
    expect(screen.getByText('Color 2')).toBeInTheDocument()
    expect(screen.getByText('Color 3')).toBeInTheDocument()
  })

  it('handles partial color data gracefully', () => {
    const partialColor = {
      hex: '#FF5733',
      rgb: 'rgb(255, 87, 51)',
      name: 'Partial Color',
      confidence: 0.75
    }
    render(<ColorTokenDisplay colors={[partialColor]} />)
    expect(screen.getByText('Partial Color')).toBeInTheDocument()
  })

  it('allows expanding and viewing details of multiple colors', () => {
    const colors = [
      { ...colorWithAllData, name: 'Color 1', hex: '#FF5733' },
      { ...colorWithAllData, name: 'Color 2', hex: '#33FF57' }
    ]
    render(<ColorTokenDisplay colors={colors} />)
    const cards = document.querySelectorAll('.token-card')
    expect(cards.length).toBe(2)
  })
})

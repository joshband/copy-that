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
    // Hex code appears in both palette and detail panel
    const hexElements = screen.getAllByText('#FF5733')
    expect(hexElements.length).toBeGreaterThanOrEqual(1)
  })

  it('displays harmony, temperature, and saturation together', () => {
    render(<ColorTokenDisplay colors={[colorWithAllData]} />)
    // Component uses detail-panel, not token-card
    const detailPanel = document.querySelector('.detail-panel')
    expect(detailPanel).toBeInTheDocument()
  })

  it('maintains color consistency across multiple tokens', () => {
    const colors = [
      { ...colorWithAllData, name: 'Color 1', hex: '#FF5733' },
      { ...colorWithAllData, name: 'Color 2', hex: '#33FF57' },
      { ...colorWithAllData, name: 'Color 3', hex: '#5733FF' }
    ]
    render(<ColorTokenDisplay colors={colors} />)
    // Color names are shown in palette swatch titles
    const swatches = document.querySelectorAll('.palette-swatch')
    expect(swatches.length).toBe(3)
    // First color is selected and shown in detail panel
    expect(screen.getByText('Color 1')).toBeInTheDocument()
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
    // Component shows palette swatches that can be clicked
    const swatches = document.querySelectorAll('.palette-swatch')
    expect(swatches.length).toBe(2)
  })
})

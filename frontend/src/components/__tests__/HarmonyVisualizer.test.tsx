import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { HarmonyVisualizer } from '../HarmonyVisualizer'

describe('HarmonyVisualizer', () => {
  const defaultProps = {
    harmony: 'triadic',
    hex: '#FF5733'
  }

  it('renders without crashing', () => {
    render(<HarmonyVisualizer {...defaultProps} />)
    expect(screen.getByText('Color Harmony:')).toBeInTheDocument()
  })

  it('displays the harmony type', () => {
    render(<HarmonyVisualizer {...defaultProps} />)
    const headings = screen.getAllByRole('heading')
    expect(headings.some(h => h.textContent?.includes('triadic'))).toBe(true)
  })

  it('displays correct description for monochromatic harmony', () => {
    render(<HarmonyVisualizer harmony="monochromatic" hex="#FF5733" />)
    expect(screen.getByText(/Monochromatic harmonies use a single hue/)).toBeInTheDocument()
  })

  it('displays correct description for analogous harmony', () => {
    render(<HarmonyVisualizer harmony="analogous" hex="#FF5733" />)
    expect(screen.getByText(/Colors adjacent on the hue wheel/)).toBeInTheDocument()
  })

  it('displays correct description for complementary harmony', () => {
    render(<HarmonyVisualizer harmony="complementary" hex="#FF5733" />)
    expect(screen.getByText(/Opposite colors on the hue wheel/)).toBeInTheDocument()
  })

  it('displays correct description for triadic harmony', () => {
    render(<HarmonyVisualizer harmony="triadic" hex="#FF5733" />)
    expect(screen.getByText(/Three colors equally spaced around/)).toBeInTheDocument()
  })

  it('displays correct description for tetradic harmony', () => {
    render(<HarmonyVisualizer harmony="tetradic" hex="#FF5733" />)
    expect(screen.getByText(/Four colors in two complementary pairs/)).toBeInTheDocument()
  })

  it('displays pattern information', () => {
    render(<HarmonyVisualizer harmony="complementary" hex="#FF5733" />)
    expect(screen.getByText('Pattern:')).toBeInTheDocument()
    expect(screen.getByText('180° apart on hue wheel')).toBeInTheDocument()
  })

  it('displays design tips section', () => {
    render(<HarmonyVisualizer harmony="monochromatic" hex="#FF5733" />)
    expect(screen.getByText('Design Tips')).toBeInTheDocument()
    expect(screen.getByText(/Use for calming, professional interfaces/)).toBeInTheDocument()
  })

  it('renders SVG hue wheel', () => {
    render(<HarmonyVisualizer {...defaultProps} />)
    const svg = document.querySelector('.hue-wheel')
    expect(svg).toBeInTheDocument()
  })

  it('displays wheel explanation text', () => {
    render(<HarmonyVisualizer harmony="triadic" hex="#FF5733" />)
    expect(screen.getByText(/The center dot/)).toBeInTheDocument()
    expect(screen.getByText(/surrounding markers/)).toBeInTheDocument()
  })

  it('handles unknown harmony type', () => {
    render(<HarmonyVisualizer harmony="unknown" hex="#FF5733" />)
    const unknownElements = screen.getAllByText('unknown')
    expect(unknownElements.length).toBeGreaterThan(0)
    const description = document.querySelector('p.description')
    expect(description).toBeInTheDocument()
    expect(description?.textContent).toContain('Color harmony not classified')
  })
})

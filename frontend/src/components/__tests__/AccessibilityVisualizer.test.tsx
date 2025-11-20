import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { AccessibilityVisualizer } from '../AccessibilityVisualizer'

describe('AccessibilityVisualizer', () => {
  const defaultProps = {
    hex: '#FF5733',
    wcagContrastWhite: 6.5,
    wcagContrastBlack: 3.2,
    wcagAACompliantText: true,
    wcagAAACompliantText: false,
    wcagAACompliantNormal: true,
    wcagAAACompliantNormal: false,
    colorblindSafe: true
  }

  beforeEach(() => {
    // Mock navigator.clipboard
    Object.assign(navigator, {
      clipboard: {
        writeText: async () => {}
      }
    })
  })

  it('renders without crashing', () => {
    render(<AccessibilityVisualizer {...defaultProps} />)
    expect(screen.getByText(/Accessibility & Contrast/)).toBeInTheDocument()
  })

  it('displays accessibility header with WCAG information', () => {
    render(<AccessibilityVisualizer {...defaultProps} />)
    expect(screen.getByText(/WCAG guidelines/)).toBeInTheDocument()
  })

  it('renders three tabs: White, Black, and Custom Background', () => {
    render(<AccessibilityVisualizer {...defaultProps} />)
    expect(screen.getByRole('button', { name: /On White/ })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /On Black/ })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Custom Background/ })).toBeInTheDocument()
  })

  it('displays white background contrast by default', () => {
    render(<AccessibilityVisualizer {...defaultProps} />)
    const buttons = screen.getAllByRole('button')
    expect(buttons[0]).toHaveClass('active')
  })

  it('displays contrast ratio on white background', () => {
    render(<AccessibilityVisualizer {...defaultProps} />)
    const contrastElements = screen.getAllByText(/6\.50:1/)
    expect(contrastElements.length).toBeGreaterThan(0)
  })

  it('switches to black background tab when clicked', () => {
    render(<AccessibilityVisualizer {...defaultProps} />)
    const blackTab = screen.getByRole('button', { name: /On Black/ })
    fireEvent.click(blackTab)
    expect(blackTab).toHaveClass('active')
  })

  it('displays WCAG AA compliance badge for text', () => {
    render(<AccessibilityVisualizer {...defaultProps} />)
    const aaElements = screen.getAllByText(/AA - Large Text/)
    expect(aaElements.length).toBeGreaterThan(0)
  })

  it('displays WCAG AAA compliance badge for text', () => {
    render(<AccessibilityVisualizer {...defaultProps} />)
    expect(screen.getByText(/AAA - Large Text/)).toBeInTheDocument()
  })

  it('shows Pass badge for compliant levels', () => {
    render(<AccessibilityVisualizer {...defaultProps} />)
    const passElements = screen.getAllByText(/✓ Pass/)
    expect(passElements.length).toBeGreaterThan(0)
  })

  it('shows Fail badge for non-compliant levels', () => {
    render(<AccessibilityVisualizer {...defaultProps} />)
    const failElements = screen.getAllByText(/✗ Fail/)
    expect(failElements.length).toBeGreaterThan(0)
  })

  it('displays WCAG explanation text', () => {
    render(<AccessibilityVisualizer {...defaultProps} />)
    expect(screen.getByText(/What do these standards mean/)).toBeInTheDocument()
  })

  it('displays contrast description for normal text', () => {
    render(<AccessibilityVisualizer {...defaultProps} />)
    expect(screen.getByText(/For regular body text/)).toBeInTheDocument()
  })

  it('handles missing contrast values gracefully', () => {
    render(<AccessibilityVisualizer hex="#FF5733" />)
    expect(screen.getByText(/Accessibility & Contrast/)).toBeInTheDocument()
  })

  it('displays preview area with text on white background', () => {
    render(<AccessibilityVisualizer {...defaultProps} />)
    expect(screen.getByText(/This text is displayed on white/)).toBeInTheDocument()
  })
})

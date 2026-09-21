import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import ColorTokenDisplay from '../ColorTokenDisplay'
import { HarmonyVisualizer } from '../HarmonyVisualizer'
import { AccessibilityVisualizer } from '../AccessibilityVisualizer'

describe('Accessibility (a11y) Tests', () => {
  const testColor = {
    hex: '#FF5733',
    rgb: 'rgb(255, 87, 51)',
    name: 'Test Color',
    confidence: 0.95
  }

  it('ColorTokenDisplay has semantic heading structure', () => {
    render(<ColorTokenDisplay colors={[testColor]} />)
    const headings = screen.getAllByRole('heading')
    expect(headings.length).toBeGreaterThan(0)
  })

  it('HarmonyVisualizer uses heading tags correctly', () => {
    render(<HarmonyVisualizer harmony="triadic" hex="#FF5733" />)
    expect(screen.getByRole('heading', { level: 3, name: /Color Harmony/ })).toBeInTheDocument()
  })

  it('AccessibilityVisualizer has accessible tab buttons', () => {
    render(
      <AccessibilityVisualizer
        hex="#FF5733"
        wcagContrastWhite={6.5}
        wcagAACompliantText={true}
      />
    )
    const buttons = screen.getAllByRole('button')
    expect(buttons.length).toBeGreaterThan(0)
  })

  it('Color text has sufficient contrast information displayed', () => {
    render(
      <AccessibilityVisualizer
        hex="#FF5733"
        wcagContrastWhite={6.5}
        wcagContrastBlack={3.2}
        wcagAACompliantText={true}
      />
    )
    const subtitle = document.querySelector('.subtitle')
    expect(subtitle?.textContent).toContain('WCAG')
  })

  it('Components display text alternatives for visual elements', () => {
    render(<HarmonyVisualizer harmony="complementary" hex="#FF5733" />)
    const harmonyType = document.querySelector('.harmony-type')
    expect(harmonyType).toBeInTheDocument()
    expect(harmonyType?.textContent).toContain('complementary')
    expect(screen.getByText(/180° apart/)).toBeInTheDocument()
  })

  it('Color cards have proper labeling and semantic structure', () => {
    render(<ColorTokenDisplay colors={[testColor]} />)
    // Component uses detail-panel, not token-card
    const detailPanel = document.querySelector('.detail-panel')
    expect(detailPanel).toBeInTheDocument()
    const colorName = screen.getByText('Test Color')
    expect(colorName).toBeInTheDocument()
  })
})

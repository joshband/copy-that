import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { TokenInspector, ComponentMeta } from './TokenInspector'

const demoMeta: ComponentMeta = {
  component: 'Button',
  variant: 'primary',
  description: 'Read-only component anatomy for primary buttons',
  accessibility: {
    intent: 'Communicates button role + press state; focus ring comes from tokens.',
    role: 'button',
    notes: ['Expose aria-pressed when toggleable'],
  },
  slots: [
    {
      name: 'Root',
      description: 'Clickable surface of the button',
      tokens: [
        { property: 'background', token: 'color.background.primary', intent: 'Default fill' },
        { property: 'text', token: 'color.text.onPrimary', intent: 'High contrast text' },
      ],
      accessibility: {
        role: 'button',
        intent: 'Provides interaction state + focus ring',
        aria: { 'aria-pressed': 'Toggle buttons surface pressed state' },
        notes: ['Keeps label readable on hover/focus'],
      },
    },
    {
      name: 'Icon',
      description: 'Optional leading or trailing icon',
      tokens: [{ property: 'color', token: 'color.icon.default', intent: 'Align icon color with text' }],
      accessibility: {
        notes: ['Decorative icons should be aria-hidden'],
      },
    },
  ],
}

describe('TokenInspector', () => {
  it('renders component header and description', () => {
    render(<TokenInspector componentMeta={demoMeta} />)
    expect(screen.getByRole('heading', { level: 3, name: /Button \(primary\)/i })).toBeInTheDocument()
    expect(screen.getByText(/primary buttons/i)).toBeInTheDocument()
    expect(screen.getByText(/Accessibility/)).toBeInTheDocument()
    expect(screen.getByText(/Communicates button role/i)).toBeInTheDocument()
  })

  it('shows token bindings for the first slot by default', () => {
    render(<TokenInspector componentMeta={demoMeta} />)
    expect(screen.getAllByTestId('token-binding').length).toBeGreaterThan(0)
    expect(screen.getByText('color.background.primary')).toBeInTheDocument()
  })

  it('switches slots via tabs without mutation', () => {
    render(<TokenInspector componentMeta={demoMeta} />)
    const iconTab = screen.getByRole('button', { name: 'Icon' })
    fireEvent.click(iconTab)
    expect(screen.getByText('color.icon.default')).toBeInTheDocument()
    expect(screen.queryByText('color.text.onPrimary')).not.toBeInTheDocument()
  })

  it('renders empty state when no slots provided', () => {
    const metaWithoutSlots: ComponentMeta = { component: 'Card', slots: [] }
    render(<TokenInspector componentMeta={metaWithoutSlots} />)
    expect(screen.getByTestId('token-inspector-empty')).toBeInTheDocument()
  })
})

/**
 * Tests for ShadowTokenList Component
 * Phase 2: Color Linking
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import ShadowTokenList from '../ShadowTokenList'

// Mock the stores
vi.mock('../../../store/shadowStore', () => ({
  useShadowStore: vi.fn(() => ({
    shadows: [],
    availableColors: [],
    setShadows: vi.fn(),
    setAvailableColors: vi.fn(),
    linkColorToShadow: vi.fn(),
    unlinkColorFromShadow: vi.fn(),
  })),
  apiShadowsToStore: vi.fn(() => []),
}))

vi.mock('../../../store/tokenGraphStore', () => ({
  useTokenGraphStore: vi.fn(() => ({
    colors: [],
  })),
}))

describe('ShadowTokenList', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Empty State', () => {
    it('should render empty state when no shadows provided', () => {
      render(<ShadowTokenList shadows={null} />)
      expect(screen.getByText('No shadows extracted yet.')).toBeInTheDocument()
    })

    it('should render empty state for empty array', () => {
      render(<ShadowTokenList shadows={[]} />)
      expect(screen.getByText('No shadows extracted yet.')).toBeInTheDocument()
    })

    it('should render empty state for undefined', () => {
      render(<ShadowTokenList shadows={undefined} />)
      expect(screen.getByText('No shadows extracted yet.')).toBeInTheDocument()
    })
  })

  describe('API Format Shadows', () => {
    const apiShadows = [
      {
        name: 'shadow.sm',
        x_offset: 0,
        y_offset: 2,
        blur_radius: 4,
        spread_radius: 0,
        color_hex: '#000000',
        opacity: 0.1,
        shadow_type: 'drop',
        semantic_role: 'subtle',
        confidence: 0.9,
      },
      {
        name: 'shadow.md',
        x_offset: 0,
        y_offset: 4,
        blur_radius: 8,
        spread_radius: 0,
        color_hex: '#1a1a1a',
        opacity: 0.15,
        shadow_type: 'drop',
        semantic_role: 'medium',
        confidence: 0.85,
      },
    ]

    it('should render shadow cards for API format', () => {
      render(<ShadowTokenList shadows={apiShadows} enableColorLinking={false} />)

      expect(screen.getByText('shadow.sm')).toBeInTheDocument()
      expect(screen.getByText('shadow.md')).toBeInTheDocument()
    })

    it('should display shadow properties', () => {
      render(<ShadowTokenList shadows={[apiShadows[0]]} enableColorLinking={false} />)

      expect(screen.getByText('drop')).toBeInTheDocument()
      expect(screen.getByText('0px, 2px')).toBeInTheDocument()
      expect(screen.getByText('4px')).toBeInTheDocument()
    })

    it('should display confidence percentage', () => {
      render(<ShadowTokenList shadows={[apiShadows[0]]} enableColorLinking={false} />)

      expect(screen.getByText('90%')).toBeInTheDocument()
    })

    it('should display color hex value', () => {
      render(<ShadowTokenList shadows={[apiShadows[0]]} enableColorLinking={false} />)

      expect(screen.getByText(/#000000/)).toBeInTheDocument()
    })
  })

  describe('W3C Format Shadows', () => {
    const w3cShadows = {
      'shadow.card': {
        $type: 'shadow',
        $value: {
          x: { value: 0, unit: 'px' },
          y: { value: 4, unit: 'px' },
          blur: { value: 8, unit: 'px' },
          spread: { value: 0, unit: 'px' },
          color: '#000000',
        },
      },
    }

    it('should handle W3C format as object', () => {
      render(<ShadowTokenList shadows={w3cShadows as any} enableColorLinking={false} />)
      // Component should not crash
      expect(document.querySelector('.shadow-list')).toBeInTheDocument()
    })
  })

  describe('Visual Preview', () => {
    const shadow = [
      {
        name: 'test-shadow',
        x_offset: 2,
        y_offset: 4,
        blur_radius: 8,
        spread_radius: 1,
        color_hex: '#333333',
        opacity: 0.5,
      },
    ]

    it('should render preview box with box-shadow style', () => {
      render(<ShadowTokenList shadows={shadow} enableColorLinking={false} />)

      const previewBox = document.querySelector('.shadow-preview-box')
      expect(previewBox).toBeInTheDocument()
      expect(previewBox).toHaveStyle({ boxShadow: expect.stringContaining('px') })
    })
  })

  describe('Props', () => {
    it('should accept enableColorLinking prop', () => {
      const shadow = [{ name: 'test', x_offset: 0, y_offset: 4, blur_radius: 8, color_hex: '#000' }]

      // Should not throw
      expect(() => {
        render(<ShadowTokenList shadows={shadow} enableColorLinking={true} />)
      }).not.toThrow()
    })

    it('should accept readOnly prop', () => {
      const shadow = [{ name: 'test', x_offset: 0, y_offset: 4, blur_radius: 8, color_hex: '#000' }]

      expect(() => {
        render(<ShadowTokenList shadows={shadow} readOnly={true} />)
      }).not.toThrow()
    })

    it('should accept colorTokens prop', () => {
      const shadow = [{ name: 'test', x_offset: 0, y_offset: 4, blur_radius: 8, color_hex: '#000' }]
      const colors = [{ id: 'color.primary', hex: '#3b82f6', name: 'Primary' }]

      expect(() => {
        render(<ShadowTokenList shadows={shadow} colorTokens={colors} />)
      }).not.toThrow()
    })
  })

  describe('Spread Radius', () => {
    it('should show spread when non-zero', () => {
      const shadow = [
        {
          name: 'with-spread',
          x_offset: 0,
          y_offset: 4,
          blur_radius: 8,
          spread_radius: 2,
          color_hex: '#000',
        },
      ]

      render(<ShadowTokenList shadows={shadow} enableColorLinking={false} />)

      expect(screen.getByText('Spread:')).toBeInTheDocument()
      expect(screen.getByText('2px')).toBeInTheDocument()
    })

    it('should hide spread when zero', () => {
      const shadow = [
        {
          name: 'no-spread',
          x_offset: 0,
          y_offset: 4,
          blur_radius: 8,
          spread_radius: 0,
          color_hex: '#000',
        },
      ]

      render(<ShadowTokenList shadows={shadow} enableColorLinking={false} />)

      expect(screen.queryByText('Spread:')).not.toBeInTheDocument()
    })
  })
})

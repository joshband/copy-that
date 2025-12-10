/**
 * Tests for ShadowColorLink Component
 * Phase 2: Color Linking
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ShadowColorLink } from '../ShadowColorLink'
import type { ColorTokenOption } from '../../../../../../store/shadowStore'

const mockColors: ColorTokenOption[] = [
  { id: 'color.primary', hex: '#3b82f6', name: 'Primary Blue' },
  { id: 'color.neutral.900', hex: '#0f172a', name: 'Neutral 900' },
]

describe('ShadowColorLink', () => {
  const defaultProps = {
    layerIndex: 0,
    linkedColorId: '',
    currentHex: '#000000',
    opacity: 1,
    availableColors: mockColors,
    onLinkColor: vi.fn(),
    onUnlinkColor: vi.fn(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Compact Mode', () => {
    it('should render in compact mode', () => {
      render(<ShadowColorLink {...defaultProps} compact={true} />)
      expect(document.querySelector('.shadow-color-link.compact')).toBeInTheDocument()
    })

    it('should display hex in compact mode when not linked', () => {
      render(<ShadowColorLink {...defaultProps} compact={true} currentHex="#ff0000" />)
      expect(screen.getByText('#ff0000')).toBeInTheDocument()
    })

    it('should display linked token name in compact mode', () => {
      render(
        <ShadowColorLink {...defaultProps} compact={true} linkedColorId="color.primary" />
      )
      expect(screen.getByText('Primary Blue')).toBeInTheDocument()
    })

    it('should show link badge when linked', () => {
      render(
        <ShadowColorLink {...defaultProps} compact={true} linkedColorId="color.primary" />
      )
      expect(document.querySelector('.link-badge')).toBeInTheDocument()
    })

    it('should show opacity indicator when opacity < 1', () => {
      render(<ShadowColorLink {...defaultProps} compact={true} opacity={0.5} />)
      expect(screen.getByText(/50%/)).toBeInTheDocument()
    })
  })

  describe('Full Mode - Header', () => {
    it('should display color swatch', () => {
      render(<ShadowColorLink {...defaultProps} currentHex="#ff0000" />)
      const swatch = document.querySelector('.color-swatch')
      expect(swatch).toHaveStyle({ backgroundColor: '#ff0000' })
    })

    it('should display raw hex when not linked', () => {
      render(<ShadowColorLink {...defaultProps} currentHex="#ff0000" />)
      expect(screen.getByText('#ff0000')).toBeInTheDocument()
    })

    it('should display "Not linked to token" hint when not linked', () => {
      render(<ShadowColorLink {...defaultProps} />)
      expect(screen.getByText('Not linked to token')).toBeInTheDocument()
    })

    it('should display linked token name when linked', () => {
      render(<ShadowColorLink {...defaultProps} linkedColorId="color.primary" />)
      expect(screen.getByText('Primary Blue')).toBeInTheDocument()
    })

    it('should display token reference when linked', () => {
      render(<ShadowColorLink {...defaultProps} linkedColorId="color.primary" />)
      expect(screen.getByText('{color.primary}')).toBeInTheDocument()
    })
  })

  describe('Status Badge', () => {
    it('should show "Linked" status when linked', () => {
      render(<ShadowColorLink {...defaultProps} linkedColorId="color.primary" />)
      expect(screen.getByText(/Linked/)).toBeInTheDocument()
      expect(document.querySelector('.status-badge.linked')).toBeInTheDocument()
    })

    it('should show "Raw Hex" status when not linked', () => {
      render(<ShadowColorLink {...defaultProps} />)
      expect(screen.getByText('Raw Hex')).toBeInTheDocument()
      expect(document.querySelector('.status-badge.unlinked')).toBeInTheDocument()
    })
  })

  describe('Opacity Display', () => {
    it('should show opacity when less than 1', () => {
      render(<ShadowColorLink {...defaultProps} opacity={0.75} />)
      expect(screen.getByText('Opacity:')).toBeInTheDocument()
      expect(screen.getByText('75%')).toBeInTheDocument()
    })

    it('should not show opacity when 1', () => {
      render(<ShadowColorLink {...defaultProps} opacity={1} />)
      expect(screen.queryByText('Opacity:')).not.toBeInTheDocument()
    })
  })

  describe('Edit Button', () => {
    it('should show edit button when not readOnly', () => {
      render(<ShadowColorLink {...defaultProps} />)
      expect(screen.getByTitle(/Edit/)).toBeInTheDocument()
    })

    it('should not show edit button when readOnly', () => {
      render(<ShadowColorLink {...defaultProps} readOnly={true} />)
      expect(screen.queryByTitle(/Edit/)).not.toBeInTheDocument()
    })

    it('should expand editor when edit clicked', () => {
      render(<ShadowColorLink {...defaultProps} />)
      fireEvent.click(screen.getByTitle(/Edit/))
      expect(document.querySelector('.color-link-editor')).toBeInTheDocument()
    })

    it('should collapse editor when edit clicked again', () => {
      render(<ShadowColorLink {...defaultProps} />)

      const editBtn = screen.getByTitle(/Edit/)
      fireEvent.click(editBtn)
      fireEvent.click(screen.getByTitle(/Close/))

      expect(document.querySelector('.color-link-editor')).not.toBeInTheDocument()
    })

    it('should have expanded class when editor open', () => {
      render(<ShadowColorLink {...defaultProps} />)
      fireEvent.click(screen.getByTitle(/Edit/))
      expect(document.querySelector('.shadow-color-link.expanded')).toBeInTheDocument()
    })
  })

  describe('Editor', () => {
    it('should show label with layer index', () => {
      render(<ShadowColorLink {...defaultProps} layerIndex={1} />)
      fireEvent.click(screen.getByTitle(/Edit/))
      expect(screen.getByText('Layer 2 Color')).toBeInTheDocument()
    })

    it('should show "Shadow Color" label for first layer', () => {
      render(<ShadowColorLink {...defaultProps} layerIndex={0} />)
      fireEvent.click(screen.getByTitle(/Edit/))
      expect(screen.getByText('Shadow Color')).toBeInTheDocument()
    })

    it('should render ColorTokenPicker in editor', () => {
      render(<ShadowColorLink {...defaultProps} />)
      fireEvent.click(screen.getByTitle(/Edit/))
      expect(document.querySelector('.color-token-picker')).toBeInTheDocument()
    })

    it('should show tips section', () => {
      render(<ShadowColorLink {...defaultProps} />)
      fireEvent.click(screen.getByTitle(/Edit/))
      expect(screen.getByText(/Tip:/)).toBeInTheDocument()
    })
  })

  describe('Color Comparison', () => {
    it('should show comparison when linked color differs from original', () => {
      render(
        <ShadowColorLink
          {...defaultProps}
          linkedColorId="color.primary"
          currentHex="#000000"
        />
      )
      fireEvent.click(screen.getByTitle(/Edit/))

      expect(screen.getByText('Original:')).toBeInTheDocument()
      expect(screen.getByText('Linked:')).toBeInTheDocument()
    })

    it('should not show comparison when colors match', () => {
      render(
        <ShadowColorLink
          {...defaultProps}
          linkedColorId="color.primary"
          currentHex="#3b82f6" // Same as primary color
        />
      )
      fireEvent.click(screen.getByTitle(/Edit/))

      expect(screen.queryByText('Original:')).not.toBeInTheDocument()
    })

    it('should not show comparison when not linked', () => {
      render(<ShadowColorLink {...defaultProps} />)
      fireEvent.click(screen.getByTitle(/Edit/))

      expect(screen.queryByText('Original:')).not.toBeInTheDocument()
    })
  })

  describe('Callbacks', () => {
    it('should call onLinkColor when color selected', () => {
      const onLinkColor = vi.fn()
      render(<ShadowColorLink {...defaultProps} onLinkColor={onLinkColor} />)

      fireEvent.click(screen.getByTitle(/Edit/))

      // Open the color picker
      fireEvent.click(document.querySelector('.color-picker-trigger')!)

      // Select a color
      const option = screen.getByText('Primary Blue').closest('.color-option')!
      fireEvent.click(option)

      expect(onLinkColor).toHaveBeenCalledWith('color.primary')
    })

    it('should call onUnlinkColor when unlink clicked', () => {
      const onUnlinkColor = vi.fn()
      render(
        <ShadowColorLink
          {...defaultProps}
          linkedColorId="color.primary"
          onUnlinkColor={onUnlinkColor}
        />
      )

      fireEvent.click(screen.getByTitle(/Edit/))
      fireEvent.click(document.querySelector('.color-picker-trigger')!)

      const unlinkOption = screen.getByText(/Unlink/).closest('.color-option')!
      fireEvent.click(unlinkOption)

      expect(onUnlinkColor).toHaveBeenCalled()
    })
  })

  describe('Linked Color Display', () => {
    it('should show linked color hex in swatch', () => {
      render(<ShadowColorLink {...defaultProps} linkedColorId="color.primary" />)
      const swatch = document.querySelector('.color-swatch')
      expect(swatch).toHaveStyle({ backgroundColor: '#3b82f6' })
    })

    it('should use original hex when linked color not found', () => {
      render(
        <ShadowColorLink {...defaultProps} linkedColorId="nonexistent" currentHex="#ff0000" />
      )
      const swatch = document.querySelector('.color-swatch')
      expect(swatch).toHaveStyle({ backgroundColor: '#ff0000' })
    })
  })
})

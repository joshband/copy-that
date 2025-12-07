/**
 * Tests for ColorTokenPicker Component
 * Phase 2: Color Linking
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ColorTokenPicker } from '../ColorTokenPicker'
import type { ColorTokenOption } from '../../../store/shadowStore'

const mockColors: ColorTokenOption[] = [
  { id: 'color.primary', hex: '#3b82f6', name: 'Primary Blue' },
  { id: 'color.secondary', hex: '#10b981', name: 'Secondary Green' },
  { id: 'color.neutral.900', hex: '#0f172a', name: 'Neutral 900' },
  { id: 'color.accent', hex: '#f59e0b', name: 'Accent Orange' },
]

describe('ColorTokenPicker', () => {
  const defaultProps = {
    selectedColorId: '',
    availableColors: mockColors,
    currentHex: '#000000',
    onSelectColor: vi.fn(),
    onUnlink: vi.fn(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Trigger Button', () => {
    it('should render trigger button', () => {
      render(<ColorTokenPicker {...defaultProps} />)
      expect(document.querySelector('.color-picker-trigger')).toBeInTheDocument()
    })

    it('should display current hex when not linked', () => {
      render(<ColorTokenPicker {...defaultProps} currentHex="#ff0000" />)
      expect(screen.getByText('#ff0000')).toBeInTheDocument()
    })

    it('should display "Link to token" hint when not linked', () => {
      render(<ColorTokenPicker {...defaultProps} />)
      expect(screen.getByText('Link to token')).toBeInTheDocument()
    })

    it('should display linked token name when linked', () => {
      render(<ColorTokenPicker {...defaultProps} selectedColorId="color.primary" />)
      expect(screen.getByText('Primary Blue')).toBeInTheDocument()
    })

    it('should display token reference when linked', () => {
      render(<ColorTokenPicker {...defaultProps} selectedColorId="color.primary" />)
      expect(screen.getByText('{color.primary}')).toBeInTheDocument()
    })

    it('should show color preview swatch', () => {
      render(<ColorTokenPicker {...defaultProps} currentHex="#ff0000" />)
      const swatch = document.querySelector('.color-preview-swatch')
      expect(swatch).toHaveStyle({ backgroundColor: '#ff0000' })
    })

    it('should show linked color swatch when linked', () => {
      render(<ColorTokenPicker {...defaultProps} selectedColorId="color.primary" />)
      const swatch = document.querySelector('.color-preview-swatch')
      expect(swatch).toHaveStyle({ backgroundColor: '#3b82f6' })
    })

    it('should have linked class when color is linked', () => {
      render(<ColorTokenPicker {...defaultProps} selectedColorId="color.primary" />)
      expect(document.querySelector('.color-picker-trigger.linked')).toBeInTheDocument()
    })
  })

  describe('Dropdown', () => {
    it('should not show dropdown initially', () => {
      render(<ColorTokenPicker {...defaultProps} />)
      expect(document.querySelector('.color-picker-dropdown')).not.toBeInTheDocument()
    })

    it('should show dropdown when trigger clicked', () => {
      render(<ColorTokenPicker {...defaultProps} />)

      fireEvent.click(document.querySelector('.color-picker-trigger')!)
      expect(document.querySelector('.color-picker-dropdown')).toBeInTheDocument()
    })

    it('should close dropdown when trigger clicked again', () => {
      render(<ColorTokenPicker {...defaultProps} />)

      const trigger = document.querySelector('.color-picker-trigger')!
      fireEvent.click(trigger)
      fireEvent.click(trigger)

      expect(document.querySelector('.color-picker-dropdown')).not.toBeInTheDocument()
    })

    it('should render all color options', () => {
      render(<ColorTokenPicker {...defaultProps} />)
      fireEvent.click(document.querySelector('.color-picker-trigger')!)

      mockColors.forEach((color) => {
        expect(screen.getByText(color.name!)).toBeInTheDocument()
      })
    })

    it('should show color hex in options', () => {
      render(<ColorTokenPicker {...defaultProps} />)
      fireEvent.click(document.querySelector('.color-picker-trigger')!)

      expect(screen.getByText('#3b82f6')).toBeInTheDocument()
    })
  })

  describe('Search', () => {
    it('should render search input', () => {
      render(<ColorTokenPicker {...defaultProps} />)
      fireEvent.click(document.querySelector('.color-picker-trigger')!)

      expect(screen.getByPlaceholderText('Search colors...')).toBeInTheDocument()
    })

    it('should filter colors by name', () => {
      render(<ColorTokenPicker {...defaultProps} />)
      fireEvent.click(document.querySelector('.color-picker-trigger')!)

      const input = screen.getByPlaceholderText('Search colors...')
      fireEvent.change(input, { target: { value: 'Primary' } })

      expect(screen.getByText('Primary Blue')).toBeInTheDocument()
      expect(screen.queryByText('Secondary Green')).not.toBeInTheDocument()
    })

    it('should filter colors by hex', () => {
      render(<ColorTokenPicker {...defaultProps} />)
      fireEvent.click(document.querySelector('.color-picker-trigger')!)

      const input = screen.getByPlaceholderText('Search colors...')
      fireEvent.change(input, { target: { value: '3b82f6' } })

      expect(screen.getByText('Primary Blue')).toBeInTheDocument()
      expect(screen.queryByText('Secondary Green')).not.toBeInTheDocument()
    })

    it('should filter colors by ID', () => {
      render(<ColorTokenPicker {...defaultProps} />)
      fireEvent.click(document.querySelector('.color-picker-trigger')!)

      const input = screen.getByPlaceholderText('Search colors...')
      fireEvent.change(input, { target: { value: 'neutral' } })

      expect(screen.getByText('Neutral 900')).toBeInTheDocument()
      expect(screen.queryByText('Primary Blue')).not.toBeInTheDocument()
    })

    it('should show no results message', () => {
      render(<ColorTokenPicker {...defaultProps} />)
      fireEvent.click(document.querySelector('.color-picker-trigger')!)

      const input = screen.getByPlaceholderText('Search colors...')
      fireEvent.change(input, { target: { value: 'nonexistent' } })

      expect(screen.getByText('No matching colors found')).toBeInTheDocument()
    })
  })

  describe('Selection', () => {
    it('should call onSelectColor when color clicked', () => {
      const onSelectColor = vi.fn()
      render(<ColorTokenPicker {...defaultProps} onSelectColor={onSelectColor} />)
      fireEvent.click(document.querySelector('.color-picker-trigger')!)

      const option = screen.getByText('Primary Blue').closest('.color-option')!
      fireEvent.click(option)

      expect(onSelectColor).toHaveBeenCalledWith('color.primary')
    })

    it('should close dropdown after selection', () => {
      render(<ColorTokenPicker {...defaultProps} />)
      fireEvent.click(document.querySelector('.color-picker-trigger')!)

      const option = screen.getByText('Primary Blue').closest('.color-option')!
      fireEvent.click(option)

      expect(document.querySelector('.color-picker-dropdown')).not.toBeInTheDocument()
    })

    it('should show check mark on selected option', () => {
      render(<ColorTokenPicker {...defaultProps} selectedColorId="color.primary" />)
      fireEvent.click(document.querySelector('.color-picker-trigger')!)

      const option = screen.getByText('Primary Blue').closest('.color-option')!
      expect(option).toHaveClass('selected')
      expect(option.querySelector('.check-mark')).toBeInTheDocument()
    })
  })

  describe('Unlink', () => {
    it('should show unlink option when color is linked', () => {
      render(<ColorTokenPicker {...defaultProps} selectedColorId="color.primary" />)
      fireEvent.click(document.querySelector('.color-picker-trigger')!)

      expect(screen.getByText(/Unlink/)).toBeInTheDocument()
    })

    it('should not show unlink option when not linked', () => {
      render(<ColorTokenPicker {...defaultProps} />)
      fireEvent.click(document.querySelector('.color-picker-trigger')!)

      expect(screen.queryByText(/Unlink/)).not.toBeInTheDocument()
    })

    it('should call onUnlink when unlink clicked', () => {
      const onUnlink = vi.fn()
      render(<ColorTokenPicker {...defaultProps} selectedColorId="color.primary" onUnlink={onUnlink} />)
      fireEvent.click(document.querySelector('.color-picker-trigger')!)

      const unlinkOption = screen.getByText(/Unlink/).closest('.color-option')!
      fireEvent.click(unlinkOption)

      expect(onUnlink).toHaveBeenCalled()
    })
  })

  describe('Disabled State', () => {
    it('should not open dropdown when disabled', () => {
      render(<ColorTokenPicker {...defaultProps} disabled={true} />)
      fireEvent.click(document.querySelector('.color-picker-trigger')!)

      expect(document.querySelector('.color-picker-dropdown')).not.toBeInTheDocument()
    })

    it('should have disabled class', () => {
      render(<ColorTokenPicker {...defaultProps} disabled={true} />)
      expect(document.querySelector('.color-token-picker.disabled')).toBeInTheDocument()
    })
  })

  describe('Keyboard Navigation', () => {
    it('should close dropdown on Escape', () => {
      render(<ColorTokenPicker {...defaultProps} />)

      const trigger = document.querySelector('.color-picker-trigger')!
      fireEvent.click(trigger)

      fireEvent.keyDown(document.querySelector('.color-token-picker')!, { key: 'Escape' })

      expect(document.querySelector('.color-picker-dropdown')).not.toBeInTheDocument()
    })
  })

  describe('Empty Colors', () => {
    it('should show message when no colors available', () => {
      render(<ColorTokenPicker {...defaultProps} availableColors={[]} />)
      fireEvent.click(document.querySelector('.color-picker-trigger')!)

      expect(screen.getByText('No color tokens available')).toBeInTheDocument()
    })
  })
})

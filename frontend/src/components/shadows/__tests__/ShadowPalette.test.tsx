/**
 * Tests for ShadowPalette Component
 * Phase 3: Shadow Palette
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import ShadowPalette from '../ShadowPalette'
import type { ShadowTokenWithMeta } from '../../../store/shadowStore'

// Mock the stores
const mockLinkColorToShadow = vi.fn()
const mockUnlinkColorFromShadow = vi.fn()
const mockSelectShadow = vi.fn()

vi.mock('../../../store/shadowStore', () => ({
  useShadowStore: vi.fn(() => ({
    shadows: [],
    availableColors: [
      { id: 'color.primary', hex: '#3b82f6', name: 'Primary' },
      { id: 'color.neutral.900', hex: '#0f172a', name: 'Neutral 900' },
    ],
    selectedShadowId: null,
    selectShadow: mockSelectShadow,
    linkColorToShadow: mockLinkColorToShadow,
    unlinkColorFromShadow: mockUnlinkColorFromShadow,
  })),
}))

const createMockShadow = (overrides: Partial<ShadowTokenWithMeta> = {}): ShadowTokenWithMeta => ({
  id: 'shadow.test',
  raw: {
    $type: 'shadow',
    $value: {
      x: { value: 0, unit: 'px' },
      y: { value: 4, unit: 'px' },
      blur: { value: 8, unit: 'px' },
      spread: { value: 0, unit: 'px' },
      color: '#000000',
    },
  },
  name: 'Test Shadow',
  shadowType: 'drop',
  semanticRole: 'medium',
  confidence: 0.9,
  linkedColorIds: [''],
  originalColors: ['#000000'],
  ...overrides,
})

describe('ShadowPalette', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    Object.assign(navigator, {
      clipboard: { writeText: vi.fn().mockResolvedValue(undefined) },
    })
  })

  describe('Empty State', () => {
    it('should render empty state when no shadows', () => {
      render(<ShadowPalette shadows={[]} />)
      expect(screen.getByText('No Shadows Yet')).toBeInTheDocument()
    })
  })

  describe('Header', () => {
    it('should display shadow count', () => {
      const shadows = [createMockShadow({ id: 'shadow.1' }), createMockShadow({ id: 'shadow.2' })]

      render(<ShadowPalette shadows={shadows} />)

      expect(screen.getByText(/2 of 2 shadows/)).toBeInTheDocument()
    })

    it('should display linked count when shadows are linked', () => {
      const shadows = [
        createMockShadow({ id: 'shadow.1', linkedColorIds: ['color.primary'] }),
        createMockShadow({ id: 'shadow.2', linkedColorIds: [''] }),
      ]

      render(<ShadowPalette shadows={shadows} />)

      expect(screen.getByText(/1 linked/)).toBeInTheDocument()
    })
  })

  describe('View Mode Toggle', () => {
    it('should render view mode toggle buttons', () => {
      render(<ShadowPalette shadows={[createMockShadow()]} />)

      const buttons = document.querySelectorAll('.view-btn')
      expect(buttons.length).toBe(2)
    })

    it('should default to grid view', () => {
      render(<ShadowPalette shadows={[createMockShadow()]} />)

      const gridBtn = document.querySelector('.view-btn.active')
      expect(gridBtn).toBeInTheDocument()
    })

    it('should switch to list view when clicked', () => {
      render(<ShadowPalette shadows={[createMockShadow()]} />)

      const listBtn = document.querySelectorAll('.view-btn')[1]
      fireEvent.click(listBtn)

      expect(document.querySelector('.shadow-container.list')).toBeInTheDocument()
    })
  })

  describe('Search', () => {
    const shadows = [
      createMockShadow({ id: 'shadow.card', name: 'Card Shadow' }),
      createMockShadow({ id: 'shadow.button', name: 'Button Shadow' }),
    ]

    it('should render search input', () => {
      render(<ShadowPalette shadows={shadows} />)

      expect(screen.getByPlaceholderText('Search shadows...')).toBeInTheDocument()
    })

    it('should filter shadows by name', () => {
      render(<ShadowPalette shadows={shadows} />)

      const input = screen.getByPlaceholderText('Search shadows...')
      fireEvent.change(input, { target: { value: 'Card' } })

      expect(screen.getByText('Card Shadow')).toBeInTheDocument()
      expect(screen.queryByText('Button Shadow')).not.toBeInTheDocument()
    })

    it('should show clear button when search has value', () => {
      render(<ShadowPalette shadows={shadows} />)

      const input = screen.getByPlaceholderText('Search shadows...')
      fireEvent.change(input, { target: { value: 'test' } })

      expect(document.querySelector('.clear-search')).toBeInTheDocument()
    })

    it('should clear search when clear button clicked', () => {
      render(<ShadowPalette shadows={shadows} />)

      const input = screen.getByPlaceholderText('Search shadows...')
      fireEvent.change(input, { target: { value: 'test' } })

      const clearBtn = document.querySelector('.clear-search')!
      fireEvent.click(clearBtn)

      expect((input as HTMLInputElement).value).toBe('')
    })
  })

  describe('Filters', () => {
    const shadows = [
      createMockShadow({
        id: 'shadow.subtle',
        name: 'Subtle',
        semanticRole: 'subtle',
        raw: {
          $type: 'shadow',
          $value: { x: 0, y: 1, blur: { value: 2, unit: 'px' }, spread: 0, color: '#000' },
        },
      }),
      createMockShadow({
        id: 'shadow.prominent',
        name: 'Prominent',
        semanticRole: 'prominent',
        raw: {
          $type: 'shadow',
          $value: { x: 0, y: 8, blur: { value: 24, unit: 'px' }, spread: 0, color: '#000' },
        },
      }),
    ]

    it('should render elevation filter', () => {
      render(<ShadowPalette shadows={shadows} />)

      expect(screen.getByText('Elevation:')).toBeInTheDocument()
    })

    it('should render type filter', () => {
      render(<ShadowPalette shadows={shadows} />)

      expect(screen.getByText('Type:')).toBeInTheDocument()
    })

    it('should filter by elevation', () => {
      render(<ShadowPalette shadows={shadows} />)

      const elevationSelect = document.querySelectorAll('.filter-select')[0]
      fireEvent.change(elevationSelect, { target: { value: 'subtle' } })

      expect(screen.getByText('Subtle')).toBeInTheDocument()
      expect(screen.queryByText('Prominent')).not.toBeInTheDocument()
    })
  })

  describe('Shadow Items', () => {
    it('should render shadow preview', () => {
      render(<ShadowPalette shadows={[createMockShadow()]} />)

      expect(document.querySelector('.preview-box')).toBeInTheDocument()
    })

    it('should render shadow name', () => {
      render(<ShadowPalette shadows={[createMockShadow({ name: 'Card Shadow' })]} />)

      expect(screen.getByText('Card Shadow')).toBeInTheDocument()
    })

    it('should render elevation badge', () => {
      render(<ShadowPalette shadows={[createMockShadow({ semanticRole: 'medium' })]} />)

      expect(screen.getByText('medium')).toBeInTheDocument()
    })

    it('should render shadow type badge', () => {
      render(<ShadowPalette shadows={[createMockShadow({ shadowType: 'drop' })]} />)

      expect(screen.getByText('drop')).toBeInTheDocument()
    })

    it('should render linked badge when color is linked', () => {
      render(<ShadowPalette shadows={[createMockShadow({ linkedColorIds: ['color.primary'] })]} />)

      expect(screen.getByText(/Linked/)).toBeInTheDocument()
    })
  })

  describe('Selection', () => {
    it('should highlight selected shadow', () => {
      const shadows = [createMockShadow({ id: 'shadow.1' })]
      render(<ShadowPalette shadows={shadows} />)

      const item = document.querySelector('.shadow-item')!
      fireEvent.click(item)

      expect(item).toHaveClass('selected')
    })

    it('should call onSelectShadow callback', () => {
      const onSelect = vi.fn()
      const shadow = createMockShadow()

      render(<ShadowPalette shadows={[shadow]} onSelectShadow={onSelect} />)

      const item = document.querySelector('.shadow-item')!
      fireEvent.click(item)

      expect(onSelect).toHaveBeenCalledWith(shadow)
    })
  })

  describe('Multi-Select', () => {
    const shadows = [
      createMockShadow({ id: 'shadow.1', name: 'Shadow 1' }),
      createMockShadow({ id: 'shadow.2', name: 'Shadow 2' }),
      createMockShadow({ id: 'shadow.3', name: 'Shadow 3' }),
    ]

    it('should show batch actions when items selected', () => {
      render(<ShadowPalette shadows={shadows} enableMultiSelect={true} />)

      const item = document.querySelector('.shadow-item')!
      fireEvent.click(item)

      expect(screen.getByText(/1 selected/)).toBeInTheDocument()
    })

    it('should show Select All button', () => {
      render(<ShadowPalette shadows={shadows} enableMultiSelect={true} />)

      const item = document.querySelector('.shadow-item')!
      fireEvent.click(item)

      expect(screen.getByText(/Select All/)).toBeInTheDocument()
    })

    it('should show Clear Selection button', () => {
      render(<ShadowPalette shadows={shadows} enableMultiSelect={true} />)

      const item = document.querySelector('.shadow-item')!
      fireEvent.click(item)

      expect(screen.getByText('Clear Selection')).toBeInTheDocument()
    })
  })

  describe('Copy CSS', () => {
    it('should show copy button on hover', () => {
      render(<ShadowPalette shadows={[createMockShadow()]} />)

      const copyBtn = document.querySelector('.copy-btn')
      expect(copyBtn).toBeInTheDocument()
    })

    it('should copy CSS to clipboard when clicked', async () => {
      render(<ShadowPalette shadows={[createMockShadow()]} />)

      const copyBtn = document.querySelector('.copy-btn')!
      fireEvent.click(copyBtn)

      expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
        expect.stringContaining('box-shadow:')
      )
    })
  })

  describe('No Results', () => {
    it('should show no results message when filters exclude all', () => {
      const shadows = [createMockShadow({ semanticRole: 'medium' })]
      render(<ShadowPalette shadows={shadows} />)

      const input = screen.getByPlaceholderText('Search shadows...')
      fireEvent.change(input, { target: { value: 'nonexistent' } })

      expect(screen.getByText('No shadows match your filters.')).toBeInTheDocument()
    })

    it('should show reset filters button', () => {
      const shadows = [createMockShadow()]
      render(<ShadowPalette shadows={shadows} />)

      const input = screen.getByPlaceholderText('Search shadows...')
      fireEvent.change(input, { target: { value: 'nonexistent' } })

      expect(screen.getByText('Reset Filters')).toBeInTheDocument()
    })
  })
})

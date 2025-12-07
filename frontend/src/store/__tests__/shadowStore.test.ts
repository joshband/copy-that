/**
 * Tests for shadowStore - Shadow Token State Management
 * Phase 2: Color Linking
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { act } from '@testing-library/react'
import { useShadowStore, apiShadowsToStore, type ShadowTokenWithMeta, type ColorTokenOption } from '../shadowStore'

// Reset store before each test
beforeEach(() => {
  useShadowStore.setState({
    shadows: [],
    availableColors: [],
    selectedShadowId: null,
    editingShadowId: null,
  })
})

const mockColors: ColorTokenOption[] = [
  { id: 'color.primary', hex: '#3b82f6', name: 'Primary Blue' },
  { id: 'color.secondary', hex: '#10b981', name: 'Secondary Green' },
  { id: 'color.neutral.900', hex: '#0f172a', name: 'Neutral 900' },
]

const mockShadow: ShadowTokenWithMeta = {
  id: 'shadow.card',
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
  name: 'Card Shadow',
  shadowType: 'drop',
  semanticRole: 'medium',
  confidence: 0.95,
  linkedColorIds: [''],
  originalColors: ['#000000'],
}

const mockShadowWithLink: ShadowTokenWithMeta = {
  ...mockShadow,
  id: 'shadow.linked',
  linkedColorIds: ['color.neutral.900'],
  raw: {
    ...mockShadow.raw,
    $value: {
      ...mockShadow.raw.$value as any,
      color: '{color.neutral.900}',
    },
  },
}

describe('shadowStore', () => {
  describe('Initial State', () => {
    it('should initialize with empty shadows', () => {
      const state = useShadowStore.getState()
      expect(state.shadows).toEqual([])
      expect(state.availableColors).toEqual([])
      expect(state.selectedShadowId).toBeNull()
      expect(state.editingShadowId).toBeNull()
    })
  })

  describe('setShadows', () => {
    it('should set shadows in store', () => {
      act(() => {
        useShadowStore.getState().setShadows([mockShadow])
      })

      const state = useShadowStore.getState()
      expect(state.shadows).toHaveLength(1)
      expect(state.shadows[0].id).toBe('shadow.card')
    })

    it('should replace existing shadows', () => {
      act(() => {
        useShadowStore.getState().setShadows([mockShadow])
        useShadowStore.getState().setShadows([mockShadowWithLink])
      })

      const state = useShadowStore.getState()
      expect(state.shadows).toHaveLength(1)
      expect(state.shadows[0].id).toBe('shadow.linked')
    })
  })

  describe('setAvailableColors', () => {
    it('should set available colors', () => {
      act(() => {
        useShadowStore.getState().setAvailableColors(mockColors)
      })

      const state = useShadowStore.getState()
      expect(state.availableColors).toHaveLength(3)
      expect(state.availableColors[0].id).toBe('color.primary')
    })
  })

  describe('Selection', () => {
    it('should select a shadow', () => {
      act(() => {
        useShadowStore.getState().setShadows([mockShadow])
        useShadowStore.getState().selectShadow('shadow.card')
      })

      expect(useShadowStore.getState().selectedShadowId).toBe('shadow.card')
    })

    it('should clear selection with null', () => {
      act(() => {
        useShadowStore.getState().selectShadow('shadow.card')
        useShadowStore.getState().selectShadow(null)
      })

      expect(useShadowStore.getState().selectedShadowId).toBeNull()
    })

    it('should start editing a shadow', () => {
      act(() => {
        useShadowStore.getState().startEditing('shadow.card')
      })

      expect(useShadowStore.getState().editingShadowId).toBe('shadow.card')
    })

    it('should cancel editing', () => {
      act(() => {
        useShadowStore.getState().startEditing('shadow.card')
        useShadowStore.getState().cancelEditing()
      })

      expect(useShadowStore.getState().editingShadowId).toBeNull()
    })
  })

  describe('Color Linking', () => {
    beforeEach(() => {
      act(() => {
        useShadowStore.getState().setShadows([mockShadow])
        useShadowStore.getState().setAvailableColors(mockColors)
      })
    })

    it('should link a color to a shadow', () => {
      act(() => {
        useShadowStore.getState().linkColorToShadow('shadow.card', 0, 'color.primary')
      })

      const state = useShadowStore.getState()
      const shadow = state.shadows[0]

      expect(shadow.linkedColorIds[0]).toBe('color.primary')
      expect((shadow.raw.$value as any).color).toBe('{color.primary}')
    })

    it('should unlink a color from a shadow', () => {
      // First link
      act(() => {
        useShadowStore.getState().linkColorToShadow('shadow.card', 0, 'color.primary')
      })

      // Then unlink
      act(() => {
        useShadowStore.getState().unlinkColorFromShadow('shadow.card', 0)
      })

      const state = useShadowStore.getState()
      const shadow = state.shadows[0]

      expect(shadow.linkedColorIds[0]).toBe('')
      expect((shadow.raw.$value as any).color).toBe('#000000') // Original color
    })

    it('should update shadow color with hex value', () => {
      act(() => {
        useShadowStore.getState().updateShadowColor('shadow.card', 0, '#ff0000')
      })

      const state = useShadowStore.getState()
      const shadow = state.shadows[0]

      expect(shadow.linkedColorIds[0]).toBe('')
      expect((shadow.raw.$value as any).color).toBe('#ff0000')
    })

    it('should update shadow color with token reference', () => {
      act(() => {
        useShadowStore.getState().updateShadowColor('shadow.card', 0, '{color.secondary}')
      })

      const state = useShadowStore.getState()
      const shadow = state.shadows[0]

      expect(shadow.linkedColorIds[0]).toBe('color.secondary')
      expect((shadow.raw.$value as any).color).toBe('{color.secondary}')
    })
  })

  describe('Helper Methods', () => {
    beforeEach(() => {
      act(() => {
        useShadowStore.getState().setShadows([mockShadow, mockShadowWithLink])
        useShadowStore.getState().setAvailableColors(mockColors)
      })
    })

    it('should get shadow by ID', () => {
      const shadow = useShadowStore.getState().getShadowById('shadow.card')
      expect(shadow).toBeDefined()
      expect(shadow?.id).toBe('shadow.card')
    })

    it('should return undefined for non-existent shadow', () => {
      const shadow = useShadowStore.getState().getShadowById('non.existent')
      expect(shadow).toBeUndefined()
    })

    it('should get linked color for shadow', () => {
      const color = useShadowStore.getState().getLinkedColor('shadow.linked', 0)
      expect(color).toBeDefined()
      expect(color?.id).toBe('color.neutral.900')
    })

    it('should return undefined for unlinked shadow', () => {
      const color = useShadowStore.getState().getLinkedColor('shadow.card', 0)
      expect(color).toBeUndefined()
    })

    it('should get shadows using a specific color', () => {
      const shadows = useShadowStore.getState().getShadowsUsingColor('color.neutral.900')
      expect(shadows).toHaveLength(1)
      expect(shadows[0].id).toBe('shadow.linked')
    })

    it('should return empty array when no shadows use color', () => {
      const shadows = useShadowStore.getState().getShadowsUsingColor('color.unused')
      expect(shadows).toHaveLength(0)
    })
  })
})

describe('apiShadowsToStore', () => {
  describe('API Format Conversion', () => {
    it('should convert API format shadows to store format', () => {
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
      ]

      const result = apiShadowsToStore(apiShadows as any, mockColors)

      expect(result).toHaveLength(1)
      expect(result[0].id).toBe('shadow.sm')
      expect(result[0].shadowType).toBe('drop')
      expect(result[0].semanticRole).toBe('subtle')
      expect(result[0].confidence).toBe(0.9)
      expect(result[0].originalColors[0]).toBe('#000000')
    })

    it('should auto-link colors when hex matches available token', () => {
      const apiShadows = [
        {
          name: 'shadow.matched',
          x_offset: 0,
          y_offset: 4,
          blur_radius: 8,
          spread_radius: 0,
          color_hex: '#3b82f6', // Matches color.primary
        },
      ]

      const result = apiShadowsToStore(apiShadows as any, mockColors)

      expect(result[0].linkedColorIds[0]).toBe('color.primary')
    })

    it('should handle shadows without matching colors', () => {
      const apiShadows = [
        {
          name: 'shadow.unmatched',
          color_hex: '#ff00ff', // No matching token
        },
      ]

      const result = apiShadowsToStore(apiShadows as any, mockColors)

      expect(result[0].linkedColorIds[0]).toBe('')
      expect(result[0].originalColors[0]).toBe('#ff00ff')
    })
  })

  describe('W3C Format Conversion', () => {
    it('should convert W3C format shadows to store format', () => {
      const w3cShadows = {
        'shadow.w3c': {
          $type: 'shadow',
          $value: {
            x: { value: 0, unit: 'px' },
            y: { value: 4, unit: 'px' },
            blur: { value: 8, unit: 'px' },
            spread: { value: 0, unit: 'px' },
            color: '#334155',
          },
        },
      }

      const result = apiShadowsToStore(w3cShadows as any, mockColors)

      expect(result).toHaveLength(1)
      expect(result[0].id).toBe('shadow.w3c')
      expect(result[0].originalColors[0]).toBe('#334155')
    })

    it('should handle token references in W3C format', () => {
      const w3cShadows = {
        'shadow.linked': {
          $type: 'shadow',
          $value: {
            x: { value: 0, unit: 'px' },
            y: { value: 4, unit: 'px' },
            blur: { value: 8, unit: 'px' },
            spread: { value: 0, unit: 'px' },
            color: '{color.neutral.900}',
          },
        },
      }

      const result = apiShadowsToStore(w3cShadows as any, mockColors)

      expect(result[0].linkedColorIds[0]).toBe('color.neutral.900')
    })
  })

  describe('Edge Cases', () => {
    it('should handle empty arrays', () => {
      const result = apiShadowsToStore([], mockColors)
      expect(result).toHaveLength(0)
    })

    it('should handle empty objects', () => {
      const result = apiShadowsToStore({} as any, mockColors)
      expect(result).toHaveLength(0)
    })

    it('should generate default names for unnamed shadows', () => {
      const apiShadows = [
        { x_offset: 0, y_offset: 4, blur_radius: 8, color_hex: '#000000' },
      ]

      const result = apiShadowsToStore(apiShadows as any, [])

      expect(result[0].id).toBe('shadow.1')
    })
  })
})

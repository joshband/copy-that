/**
 * Overview Narrative Hooks - Tier 1 Critical Tests
 *
 * Tests for palette analysis and art movement classification hooks
 * These are critical for narrative generation and design classification.
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { renderHook } from '@testing-library/react'
import { usePaletteAnalysis, useArtMovementClassification } from '../hooks'
import { ColorToken } from '../../../types'

// Mock color token factory
const createMockColor = (overrides: Partial<ColorToken> = {}): ColorToken => ({
  hex: '#FF0000',
  confidence: 0.95,
  semantic_name: 'red',
  temperature: 'warm',
  saturation_level: 'high',
  token_type: 'color',
  created_at: new Date().toISOString(),
  ...overrides,
})

describe('usePaletteAnalysis', () => {
  describe('temperature classification', () => {
    it('should classify warm palette', () => {
      const { result } = renderHook(() =>
        usePaletteAnalysis([
          createMockColor({ temperature: 'warm' }),
          createMockColor({ temperature: 'warm' }),
          createMockColor({ temperature: 'cool' }),
        ])
      )

      expect(result.current.temp).toBe('warm')
    })

    it('should classify cool palette', () => {
      const { result } = renderHook(() =>
        usePaletteAnalysis([
          createMockColor({ temperature: 'cool' }),
          createMockColor({ temperature: 'cool' }),
          createMockColor({ temperature: 'warm' }),
        ])
      )

      expect(result.current.temp).toBe('cool')
    })

    it('should classify balanced palette', () => {
      const { result } = renderHook(() =>
        usePaletteAnalysis([
          createMockColor({ temperature: 'warm' }),
          createMockColor({ temperature: 'cool' }),
        ])
      )

      expect(result.current.temp).toBe('balanced')
    })

    it('should handle empty color array', () => {
      const { result } = renderHook(() => usePaletteAnalysis([]))
      expect(result.current.temp).toBe('balanced')
    })

    it('should handle all warm colors', () => {
      const { result } = renderHook(() =>
        usePaletteAnalysis([
          createMockColor({ temperature: 'warm' }),
          createMockColor({ temperature: 'warm' }),
        ])
      )

      expect(result.current.temp).toBe('warm')
    })

    it('should handle all cool colors', () => {
      const { result } = renderHook(() =>
        usePaletteAnalysis([
          createMockColor({ temperature: 'cool' }),
          createMockColor({ temperature: 'cool' }),
        ])
      )

      expect(result.current.temp).toBe('cool')
    })
  })

  describe('saturation classification', () => {
    it('should classify vivid palette', () => {
      const { result } = renderHook(() =>
        usePaletteAnalysis([
          createMockColor({ saturation_level: 'high' }),
          createMockColor({ saturation_level: 'high' }),
          createMockColor({ saturation_level: 'low' }),
        ])
      )

      expect(result.current.sat).toBe('vivid')
    })

    it('should classify muted palette', () => {
      const { result } = renderHook(() =>
        usePaletteAnalysis([
          createMockColor({ saturation_level: 'low' }),
          createMockColor({ saturation_level: 'desaturated' }),
          createMockColor({ saturation_level: 'high' }),
        ])
      )

      expect(result.current.sat).toBe('muted')
    })

    it('should classify balanced saturation', () => {
      const { result } = renderHook(() =>
        usePaletteAnalysis([
          createMockColor({ saturation_level: 'high' }),
          createMockColor({ saturation_level: 'low' }),
        ])
      )

      expect(result.current.sat).toBe('balanced')
    })

    it('should handle empty palette', () => {
      const { result } = renderHook(() => usePaletteAnalysis([]))
      expect(result.current.sat).toBe('medium')
    })
  })

  describe('memoization', () => {
    it('should memoize results with same colors', () => {
      const colors = [
        createMockColor({ temperature: 'warm', saturation_level: 'high' }),
      ]

      const { result: result1 } = renderHook(() => usePaletteAnalysis(colors))
      const { result: result2 } = renderHook(() => usePaletteAnalysis(colors))

      // Same analysis
      expect(result1.current.temp).toBe(result2.current.temp)
      expect(result1.current.sat).toBe(result2.current.sat)
    })

    it.skip('should update results when colors change', () => {
      const { result, rerender } = renderHook(
        ({ colors }) => usePaletteAnalysis(colors),
        {
          initialProps: {
            colors: [createMockColor({ temperature: 'warm' })],
          },
        }
      )

      expect(result.current.temp).toBe('warm')

      rerender({
        colors: [
          createMockColor({ temperature: 'cool' }),
          createMockColor({ temperature: 'cool' }),
        ],
      })

      expect(result.current.temp).toBe('cool')
    })
  })
})

describe('useArtMovementClassification', () => {
  describe('art movement classification', () => {
    it('should classify Expressionism', () => {
      const { result } = renderHook(() =>
        useArtMovementClassification(
          Array(8).fill(null).map(() =>
            createMockColor({
              saturation_level: 'high',
              temperature: 'warm',
            })
          )
        )
      )

      expect(result.current).toBe('Expressionism')
    })

    it('should classify Fauvism', () => {
      const { result } = renderHook(() =>
        useArtMovementClassification(
          Array(8).fill(null).map(() =>
            createMockColor({
              saturation_level: 'high',
              temperature: 'cool',
            })
          )
        )
      )

      expect(result.current).toBe('Fauvism')
    })

    it('should classify Minimalism', () => {
      const { result } = renderHook(() =>
        useArtMovementClassification(
          Array(3).fill(null).map(() =>
            createMockColor({ saturation_level: 'low' })
          )
        )
      )

      expect(result.current).toBe('Minimalism')
    })

    it('should classify Swiss Modernism', () => {
      const { result } = renderHook(() =>
        useArtMovementClassification(
          Array(5).fill(null).map(() =>
            createMockColor({
              saturation_level: 'low',
              temperature: 'cool',
            })
          )
        )
      )

      expect(result.current).toBe('Swiss Modernism')
    })

    it.skip('should classify Art Deco', () => {
      const colors = [
        ...Array(6).fill(null).map(() => createMockColor({ saturation_level: 'high', temperature: 'warm' })),
        ...Array(6).fill(null).map(() => createMockColor({ saturation_level: 'high', temperature: 'cool' })),
      ]
      const { result } = renderHook(() => useArtMovementClassification(colors))

      expect(result.current).toBe('Art Deco')
    })

    it('should classify Brutalism', () => {
      const { result } = renderHook(() =>
        useArtMovementClassification(
          Array(5).fill(null).map(() =>
            createMockColor({
              saturation_level: 'low',
              temperature: 'warm',
            })
          )
        )
      )

      expect(result.current).toBe('Brutalism')
    })

    it.skip('should classify Postmodernism (balanced saturation, vivid colors)', () => {
      const colors = [
        ...Array(3).fill(null).map(() => createMockColor({ saturation_level: 'high', temperature: 'warm' })),
        ...Array(3).fill(null).map(() => createMockColor({ saturation_level: 'high', temperature: 'cool' })),
      ]
      const { result } = renderHook(() => useArtMovementClassification(colors))

      expect(result.current).toBe('Postmodernism')
    })

    it('should classify Neo-Minimalism', () => {
      const { result } = renderHook(() =>
        useArtMovementClassification(
          Array(2).fill(null).map(() =>
            createMockColor({
              saturation_level: 'high',
              temperature: 'warm',
            })
          )
        )
      )

      expect(result.current).toBe('Neo-Minimalism')
    })

    it.skip('should classify Postmodernism', () => {
      const colors = [
        ...Array(4).fill(null).map(() => createMockColor({ saturation_level: 'high', temperature: 'warm' })),
        ...Array(4).fill(null).map(() => createMockColor({ saturation_level: 'high', temperature: 'cool' })),
      ]
      const { result } = renderHook(() => useArtMovementClassification(colors))

      expect(result.current).toBe('Postmodernism')
    })

    it.skip('should default to Modern Design', () => {
      const colors = [
        ...Array(2).fill(null).map(() => createMockColor({ saturation_level: 'high', temperature: 'warm' })),
        ...Array(2).fill(null).map(() => createMockColor({ saturation_level: 'low', temperature: 'cool' })),
      ]
      const { result } = renderHook(() => useArtMovementClassification(colors))

      expect(result.current).toBe('Modern Design')
    })

    it('should handle empty palette', () => {
      const { result } = renderHook(() => useArtMovementClassification([]))
      expect(result.current).toBe('Neo-Minimalism')
    })
  })

  describe('boundary conditions', () => {
    it('should handle single color', () => {
      const { result } = renderHook(() =>
        useArtMovementClassification([
          createMockColor({
            saturation_level: 'high',
            temperature: 'warm',
          }),
        ])
      )

      expect(result.current).toBeDefined()
      expect(typeof result.current).toBe('string')
    })

    it('should handle many colors', () => {
      const { result } = renderHook(() =>
        useArtMovementClassification(
          Array(20).fill(null).map(() =>
            createMockColor({
              saturation_level: 'high',
              temperature: 'cool',
            })
          )
        )
      )

      expect(result.current).toBe('Fauvism')
    })

    it('should handle mixed saturation levels', () => {
      const colors = [
        ...Array(5).fill(null).map(() =>
          createMockColor({
            saturation_level: 'high',
            temperature: 'warm',
          })
        ),
        ...Array(5).fill(null).map(() =>
          createMockColor({
            saturation_level: 'low',
            temperature: 'warm',
          })
        ),
      ]

      const { result } = renderHook(() => useArtMovementClassification(colors))
      expect(result.current).toBeDefined()
    })
  })

  describe('memoization', () => {
    it('should memoize classification result', () => {
      const colors = Array(8).fill(null).map(() =>
        createMockColor({
          saturation_level: 'high',
          temperature: 'warm',
        })
      )

      const { result, rerender } = renderHook(
        ({ colors: c }) => useArtMovementClassification(c),
        { initialProps: { colors } }
      )

      const firstResult = result.current

      // Rerender with same colors
      rerender({ colors })

      // Result should be memoized (same reference)
      expect(result.current).toBe(firstResult)
    })

    it('should update classification when colors change significantly', () => {
      const { result, rerender } = renderHook(
        ({ colors }) => useArtMovementClassification(colors),
        {
          initialProps: {
            colors: [
              createMockColor({
                saturation_level: 'high',
                temperature: 'warm',
              }),
            ],
          },
        }
      )

      const firstResult = result.current

      // Change to Art Deco palette (6 warm + 6 cool, high saturation)
      rerender({
        colors: [
          ...Array(6).fill(null).map(() => createMockColor({ saturation_level: 'high', temperature: 'warm' })),
          ...Array(6).fill(null).map(() => createMockColor({ saturation_level: 'high', temperature: 'cool' })),
        ],
      })

      expect(result.current).not.toBe(firstResult)
      expect(result.current).toBe('Art Deco')
    })
  })
})

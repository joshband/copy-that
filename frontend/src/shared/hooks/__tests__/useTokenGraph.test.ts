/**
 * Tests for useTokenGraph hook
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { renderHook } from '@testing-library/react'
import { useTokenGraph } from '../useTokenGraph'
import { useTokenGraphStore } from '../../../store/tokenGraphStore'

describe('useTokenGraph', () => {
  beforeEach(() => {
    // Reset store before each test
    useTokenGraphStore.setState({
      loaded: false,
      colors: [],
      spacing: [],
      shadows: [],
      typography: [],
      layout: [],
    })
  })

  describe('getNode', () => {
    it('should return token by id', () => {
      useTokenGraphStore.setState({
        colors: [
          {
            id: 'color.primary',
            category: 'color',
            isAlias: false,
            raw: { $type: 'color', $value: { hex: '#FF0000' } },
          },
        ],
      })

      const { result } = renderHook(() => useTokenGraph())
      const node = result.current.getNode('color.primary')

      expect(node).toBeDefined()
      expect(node?.id).toBe('color.primary')
    })

    it('should return null for non-existent token', () => {
      const { result } = renderHook(() => useTokenGraph())
      const node = result.current.getNode('does.not.exist')

      expect(node).toBeNull()
    })
  })

  describe('getNodes', () => {
    it('should return all color tokens', () => {
      useTokenGraphStore.setState({
        colors: [
          {
            id: 'color.primary',
            category: 'color',
            isAlias: false,
            raw: { $type: 'color', $value: { hex: '#FF0000' } },
          },
          {
            id: 'color.secondary',
            category: 'color',
            isAlias: false,
            raw: { $type: 'color', $value: { hex: '#00FF00' } },
          },
        ],
      })

      const { result } = renderHook(() => useTokenGraph())
      const colors = result.current.getNodes('color')

      expect(colors).toHaveLength(2)
      expect(colors[0].id).toBe('color.primary')
      expect(colors[1].id).toBe('color.secondary')
    })

    it('should return empty array for category with no tokens', () => {
      const { result } = renderHook(() => useTokenGraph())
      const shadows = result.current.getNodes('shadow')

      expect(shadows).toEqual([])
    })
  })

  describe('getAliases', () => {
    it('should return all tokens that alias the given token', () => {
      useTokenGraphStore.setState({
        colors: [
          {
            id: 'color.primary',
            category: 'color',
            isAlias: false,
            raw: { $type: 'color', $value: { hex: '#FF0000' } },
          },
          {
            id: 'color.button',
            category: 'color',
            isAlias: true,
            aliasTargetId: 'color.primary',
            raw: { $type: 'color', $value: '{color.primary}' },
          },
          {
            id: 'color.link',
            category: 'color',
            isAlias: true,
            aliasTargetId: 'color.primary',
            raw: { $type: 'color', $value: '{color.primary}' },
          },
        ],
      })

      const { result } = renderHook(() => useTokenGraph())
      const aliases = result.current.getAliases('color.primary')

      expect(aliases).toHaveLength(2)
      expect(aliases[0].id).toBe('color.button')
      expect(aliases[1].id).toBe('color.link')
    })

    it('should return empty array if no aliases', () => {
      useTokenGraphStore.setState({
        colors: [
          {
            id: 'color.primary',
            category: 'color',
            isAlias: false,
            raw: { $type: 'color', $value: { hex: '#FF0000' } },
          },
        ],
      })

      const { result } = renderHook(() => useTokenGraph())
      const aliases = result.current.getAliases('color.primary')

      expect(aliases).toEqual([])
    })
  })

  describe('getDependencies', () => {
    it('should return color dependency for alias', () => {
      useTokenGraphStore.setState({
        colors: [
          {
            id: 'color.primary',
            category: 'color',
            isAlias: false,
            raw: { $type: 'color', $value: { hex: '#FF0000' } },
          },
          {
            id: 'color.button',
            category: 'color',
            isAlias: true,
            aliasTargetId: 'color.primary',
            raw: { $type: 'color', $value: '{color.primary}' },
          },
        ],
      })

      const { result } = renderHook(() => useTokenGraph())
      const deps = result.current.getDependencies('color.button')

      expect(deps).toHaveLength(1)
      expect(deps[0].id).toBe('color.primary')
    })

    it('should return spacing base dependency', () => {
      useTokenGraphStore.setState({
        spacing: [
          {
            id: 'spacing.base',
            category: 'spacing',
            raw: { $type: 'dimension', $value: { value: 8, unit: 'px' } },
          },
          {
            id: 'spacing.md',
            category: 'spacing',
            baseId: 'spacing.base',
            multiplier: 2,
            raw: { $type: 'dimension', $value: { value: 16, unit: 'px' } },
          },
        ],
      })

      const { result } = renderHook(() => useTokenGraph())
      const deps = result.current.getDependencies('spacing.md')

      expect(deps).toHaveLength(1)
      expect(deps[0].id).toBe('spacing.base')
    })

    it('should return shadow color dependencies', () => {
      useTokenGraphStore.setState({
        colors: [
          {
            id: 'color.shadow',
            category: 'color',
            isAlias: false,
            raw: { $type: 'color', $value: { hex: '#000000' } },
          },
        ],
        shadows: [
          {
            id: 'shadow.card',
            category: 'shadow',
            referencedColorIds: ['color.shadow'],
            raw: { $type: 'shadow', $value: { color: '{color.shadow}', x: 4, y: 4, blur: 8, spread: 0 } },
          },
        ],
      })

      const { result } = renderHook(() => useTokenGraph())
      const deps = result.current.getDependencies('shadow.card')

      expect(deps).toHaveLength(1)
      expect(deps[0].id).toBe('color.shadow')
    })
  })

  describe('getDependents', () => {
    it('should return tokens that depend on the given token', () => {
      useTokenGraphStore.setState({
        colors: [
          {
            id: 'color.primary',
            category: 'color',
            isAlias: false,
            raw: { $type: 'color', $value: { hex: '#FF0000' } },
          },
          {
            id: 'color.button',
            category: 'color',
            isAlias: true,
            aliasTargetId: 'color.primary',
            raw: { $type: 'color', $value: '{color.primary}' },
          },
        ],
        shadows: [
          {
            id: 'shadow.card',
            category: 'shadow',
            referencedColorIds: ['color.primary'],
            raw: { $type: 'shadow', $value: { color: '{color.primary}', x: 4, y: 4, blur: 8, spread: 0 } },
          },
        ],
      })

      const { result } = renderHook(() => useTokenGraph())
      const dependents = result.current.getDependents('color.primary')

      expect(dependents).toHaveLength(2)
      expect(dependents.some((d) => d.id === 'color.button')).toBe(true)
      expect(dependents.some((d) => d.id === 'shadow.card')).toBe(true)
    })
  })

  describe('resolveAlias', () => {
    it('should resolve alias to target token', () => {
      useTokenGraphStore.setState({
        colors: [
          {
            id: 'color.primary',
            category: 'color',
            isAlias: false,
            raw: { $type: 'color', $value: { hex: '#FF0000' } },
          },
          {
            id: 'color.button',
            category: 'color',
            isAlias: true,
            aliasTargetId: 'color.primary',
            raw: { $type: 'color', $value: '{color.primary}' },
          },
        ],
      })

      const { result } = renderHook(() => useTokenGraph())
      const resolved = result.current.resolveAlias('color.button')

      expect(resolved).toBeDefined()
      expect(resolved?.id).toBe('color.primary')
    })

    it('should handle alias chains', () => {
      useTokenGraphStore.setState({
        colors: [
          {
            id: 'color.primary',
            category: 'color',
            isAlias: false,
            raw: { $type: 'color', $value: { hex: '#FF0000' } },
          },
          {
            id: 'color.button',
            category: 'color',
            isAlias: true,
            aliasTargetId: 'color.primary',
            raw: { $type: 'color', $value: '{color.primary}' },
          },
          {
            id: 'color.cta',
            category: 'color',
            isAlias: true,
            aliasTargetId: 'color.button',
            raw: { $type: 'color', $value: '{color.button}' },
          },
        ],
      })

      const { result } = renderHook(() => useTokenGraph())
      const resolved = result.current.resolveAlias('color.cta')

      // Should follow chain: color.cta → color.button → color.primary
      expect(resolved?.id).toBe('color.primary')
    })
  })

  describe('getRootTokens', () => {
    it('should return tokens with no dependencies', () => {
      useTokenGraphStore.setState({
        colors: [
          {
            id: 'color.primary',
            category: 'color',
            isAlias: false,
            raw: { $type: 'color', $value: { hex: '#FF0000' } },
          },
          {
            id: 'color.button',
            category: 'color',
            isAlias: true,
            aliasTargetId: 'color.primary',
            raw: { $type: 'color', $value: '{color.primary}' },
          },
        ],
      })

      const { result } = renderHook(() => useTokenGraph())
      const roots = result.current.getRootTokens()

      expect(roots).toHaveLength(1)
      expect(roots[0].id).toBe('color.primary')
    })
  })

  describe('getLeafTokens', () => {
    it('should return tokens with no dependents', () => {
      useTokenGraphStore.setState({
        colors: [
          {
            id: 'color.primary',
            category: 'color',
            isAlias: false,
            raw: { $type: 'color', $value: { hex: '#FF0000' } },
          },
          {
            id: 'color.button',
            category: 'color',
            isAlias: true,
            aliasTargetId: 'color.primary',
            raw: { $type: 'color', $value: '{color.primary}' },
          },
        ],
      })

      const { result } = renderHook(() => useTokenGraph())
      const leaves = result.current.getLeafTokens()

      expect(leaves).toHaveLength(1)
      expect(leaves[0].id).toBe('color.button')
    })
  })

  describe('hasToken', () => {
    it('should return true if token exists', () => {
      useTokenGraphStore.setState({
        colors: [
          {
            id: 'color.primary',
            category: 'color',
            isAlias: false,
            raw: { $type: 'color', $value: { hex: '#FF0000' } },
          },
        ],
      })

      const { result } = renderHook(() => useTokenGraph())
      expect(result.current.hasToken('color.primary')).toBe(true)
      expect(result.current.hasToken('color.missing')).toBe(false)
    })
  })

  describe('getTokensByIds', () => {
    it('should return multiple tokens by IDs', () => {
      useTokenGraphStore.setState({
        colors: [
          {
            id: 'color.primary',
            category: 'color',
            isAlias: false,
            raw: { $type: 'color', $value: { hex: '#FF0000' } },
          },
          {
            id: 'color.secondary',
            category: 'color',
            isAlias: false,
            raw: { $type: 'color', $value: { hex: '#00FF00' } },
          },
        ],
      })

      const { result } = renderHook(() => useTokenGraph())
      const tokens = result.current.getTokensByIds(['color.primary', 'color.secondary'])

      expect(tokens).toHaveLength(2)
      expect(tokens[0].id).toBe('color.primary')
      expect(tokens[1].id).toBe('color.secondary')
    })

    it('should filter out non-existent IDs', () => {
      useTokenGraphStore.setState({
        colors: [
          {
            id: 'color.primary',
            category: 'color',
            isAlias: false,
            raw: { $type: 'color', $value: { hex: '#FF0000' } },
          },
        ],
      })

      const { result } = renderHook(() => useTokenGraph())
      const tokens = result.current.getTokensByIds(['color.primary', 'color.missing'])

      expect(tokens).toHaveLength(1)
      expect(tokens[0].id).toBe('color.primary')
    })
  })
})

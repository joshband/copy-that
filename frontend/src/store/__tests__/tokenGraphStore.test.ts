import { describe, it, expect, beforeEach } from 'vitest'
import {
  useTokenGraphStore,
  selectColors,
  selectLegacyColors,
  selectLegacySpacing,
  selectLegacyShadows,
} from '../tokenGraphStore'
import type { W3CColorToken, W3CSpacingToken, W3CShadowToken } from '../../types'

const resetStore = () => useTokenGraphStore.setState({
  loaded: false,
  colors: [],
  spacing: [],
  shadows: [],
  typography: [],
  layout: [],
  opacity: [],
  gradient: [],
  duration: [],
  cubicBezier: [],
  fontFamily: [],
  fontWeight: [],
  strokeStyle: [],
  border: [],
  transition: [],
  number: [],
  dimension: [],
  typographyRecommendation: undefined,
})

describe('tokenGraphStore selectors & adapters', () => {
  beforeEach(() => {
    resetStore()
  })

  it('maps legacy colors with alias detection', () => {
    const colorToken: W3CColorToken = { $type: 'color', $value: { hex: '#ff0000' }, name: 'Primary', confidence: 0.9 }
    const aliasToken: W3CColorToken = { $type: 'color', $value: '{color.primary}' }

    useTokenGraphStore.setState({
      loaded: true,
      colors: [
        { id: 'color.primary', category: 'color', raw: colorToken, isAlias: false, aliasTargetId: undefined },
        { id: 'color.alias', category: 'color', raw: aliasToken, isAlias: true, aliasTargetId: 'color.primary' },
      ],
      spacing: [],
      shadows: [],
      typography: [],
      layout: [],
      opacity: [],
      gradient: [],
      duration: [],
      cubicBezier: [],
      fontFamily: [],
      fontWeight: [],
      strokeStyle: [],
      border: [],
      transition: [],
      number: [],
      dimension: [],
      typographyRecommendation: undefined,
    })

    const legacy = selectLegacyColors(useTokenGraphStore.getState())
    expect(legacy).toHaveLength(2)
    expect(legacy[0]).toMatchObject({ id: 'color.primary', hex: '#ff0000', isAlias: false })
    expect(legacy[1]).toMatchObject({ id: 'color.alias', isAlias: true, aliasTargetId: 'color.primary' })
  })

  it('maps legacy spacing with px/rem values', () => {
    const spacingToken: W3CSpacingToken = { $type: 'dimension', $value: { value: 16, unit: 'px' } }
    useTokenGraphStore.setState((state) => ({
      ...state,
      loaded: true,
      spacing: [{ id: 'spacing.sm', category: 'spacing', raw: spacingToken }],
    }))

    const spacing = selectLegacySpacing(useTokenGraphStore.getState())
    expect(spacing[0]).toMatchObject({ name: 'spacing.sm', value_px: 16, value_rem: 1 })
  })

  it('maps legacy shadows with linkedColorIds + originals', () => {
    const shadowToken: W3CShadowToken = {
      $type: 'shadow',
      $value: [
        { x: 0, y: 2, blur: 4, spread: 0, color: '{color.primary}' },
        { x: 0, y: 4, blur: 12, spread: 0, color: '#222222' },
      ],
    }
    useTokenGraphStore.setState((state) => ({
      ...state,
      loaded: true,
      shadows: [{ id: 'shadow.card', category: 'shadow', raw: shadowToken, referencedColorIds: ['color.primary'] }],
    }))

    const shadows = selectLegacyShadows(useTokenGraphStore.getState())
    expect(shadows).toHaveLength(1)
    expect(shadows[0].linkedColorIds).toEqual(['color.primary', ''])
    expect(shadows[0].originalColors).toEqual(['#000000', '#222222'])
  })

  it('supports selectors for direct access', () => {
    useTokenGraphStore.setState((state) => ({
      ...state,
      colors: [{ id: 'color.primary', category: 'color', raw: { $type: 'color', $value: '#fff' } as W3CColorToken, isAlias: false }],
    }))
    const colors = selectColors(useTokenGraphStore.getState())
    expect(colors[0].id).toBe('color.primary')
  })
})

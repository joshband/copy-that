/**
 * Token Graph Hook
 *
 * Provides graph-based query API for token relationships
 * Single source of truth for all token data access
 */

import { useMemo } from 'react'
import { useTokenGraphStore } from '../../store/tokenGraphStore'
import type {
  UiColorToken,
  UiSpacingToken,
  UiShadowToken,
  UiTypographyToken,
  UiTokenBase,
} from '../../store/tokenGraphStore'

type TokenCategory = 'color' | 'spacing' | 'shadow' | 'typography' | 'layout'
type TokenNode = UiColorToken | UiSpacingToken | UiShadowToken | UiTypographyToken | UiTokenBase<unknown>

/**
 * Type guard to check if token is a color token
 */
export function isColorToken(token: TokenNode): token is UiColorToken {
  return token.category === 'color'
}

/**
 * Type guard to check if token is a spacing token
 */
export function isSpacingToken(token: TokenNode): token is UiSpacingToken {
  return token.category === 'spacing'
}

/**
 * Type guard to check if token is a shadow token
 */
export function isShadowToken(token: TokenNode): token is UiShadowToken {
  return token.category === 'shadow'
}

/**
 * Type guard to check if token is a typography token
 */
export function isTypographyToken(token: TokenNode): token is UiTypographyToken {
  return token.category === 'typography'
}

export interface TokenGraphAPI {
  // Node access
  getNode(id: string): TokenNode | null
  getNodes(category: TokenCategory): TokenNode[]
  getAllNodes(): TokenNode[]

  // Edge traversal
  getAliases(tokenId: string): UiColorToken[]
  getDependencies(tokenId: string): TokenNode[]
  getDependents(tokenId: string): TokenNode[]

  // Reference resolution
  resolveAlias(tokenId: string): TokenNode | null
  resolveReferences(token: TokenNode): TokenNode

  // Graph queries
  getRootTokens(): TokenNode[]
  getLeafTokens(): TokenNode[]

  // Utilities
  hasToken(id: string): boolean
  getTokensByIds(ids: string[]): TokenNode[]
}

/**
 * useTokenGraph Hook
 *
 * Provides graph-based access to token data with relationship queries
 *
 * @example
 * ```tsx
 * function ColorPalette() {
 *   const graph = useTokenGraph()
 *   const colors = graph.getNodes('color')
 *   const aliases = graph.getAliases('color.primary')
 *
 *   return <div>{colors.map(c => <ColorCard color={c} />)}</div>
 * }
 * ```
 */
export function useTokenGraph(): TokenGraphAPI {
  const colors = useTokenGraphStore((s) => s.colors)
  const spacing = useTokenGraphStore((s) => s.spacing)
  const shadows = useTokenGraphStore((s) => s.shadows)
  const typography = useTokenGraphStore((s) => s.typography)
  const layout = useTokenGraphStore((s) => s.layout)

  const allTokens = useMemo(
    () => [...colors, ...spacing, ...shadows, ...typography, ...layout],
    [colors, spacing, shadows, typography, layout]
  )

  const api: TokenGraphAPI = useMemo(
    () => ({
      // Get single token by ID
      getNode(id: string): TokenNode | null {
        return allTokens.find((t) => t.id === id) ?? null
      },

      // Get all tokens of a category
      getNodes(category: TokenCategory): TokenNode[] {
        switch (category) {
          case 'color':
            return colors
          case 'spacing':
            return spacing
          case 'shadow':
            return shadows
          case 'typography':
            return typography
          case 'layout':
            return layout
          default:
            return []
        }
      },

      // Get all tokens (all categories)
      getAllNodes(): TokenNode[] {
        return allTokens
      },

      // Get all tokens that alias the given token
      getAliases(tokenId: string): UiColorToken[] {
        return colors.filter((c) => c.isAlias && c.aliasTargetId === tokenId)
      },

      // Get all tokens that this token depends on
      getDependencies(tokenId: string): TokenNode[] {
        const token = allTokens.find((t) => t.id === tokenId)
        if (!token) return []

        const deps: TokenNode[] = []

        // Color aliases - use type guard
        if (isColorToken(token) && token.isAlias && token.aliasTargetId) {
          const target = allTokens.find((t) => t.id === token.aliasTargetId)
          if (target) deps.push(target)
        }

        // Spacing base references - use type guard
        if (isSpacingToken(token) && token.baseId) {
          const base = allTokens.find((t) => t.id === token.baseId)
          if (base) deps.push(base)
        }

        // Shadow color references - use type guard
        if (isShadowToken(token) && token.referencedColorIds) {
          token.referencedColorIds.forEach((colorId: string) => {
            const color = allTokens.find((t) => t.id === colorId)
            if (color) deps.push(color)
          })
        }

        // Typography references - use type guard
        if (isTypographyToken(token)) {
          if (token.referencedColorId) {
            const color = allTokens.find((t) => t.id === token.referencedColorId)
            if (color) deps.push(color)
          }
          if (token.fontFamilyTokenId) {
            const fontFamily = allTokens.find((t) => t.id === token.fontFamilyTokenId)
            if (fontFamily) deps.push(fontFamily)
          }
          if (token.fontSizeTokenId) {
            const fontSize = allTokens.find((t) => t.id === token.fontSizeTokenId)
            if (fontSize) deps.push(fontSize)
          }
        }

        return deps
      },

      // Get all tokens that depend on this token
      getDependents(tokenId: string): TokenNode[] {
        const dependents: TokenNode[] = []

        allTokens.forEach((token) => {
          // Check if this token depends on tokenId
          const deps = api.getDependencies(token.id)
          if (deps.some((d) => d.id === tokenId)) {
            dependents.push(token)
          }
        })

        return dependents
      },

      // Resolve alias to final token (follow alias chain)
      resolveAlias(tokenId: string): TokenNode | null {
        const token = allTokens.find((t) => t.id === tokenId)
        if (!token) return null

        // Only color tokens can be aliases - use type guard
        if (isColorToken(token) && token.isAlias && token.aliasTargetId) {
          // Recursively resolve (handle alias chains)
          return api.resolveAlias(token.aliasTargetId) ?? token
        }

        return token
      },

      // Resolve all references in a token (returns token with resolved values)
      resolveReferences(token: TokenNode): TokenNode {
        // For now, just return the token as-is
        // Future: resolve {color.primary} strings to actual values
        return token
      },

      // Get tokens with no dependencies (root nodes)
      getRootTokens(): TokenNode[] {
        return allTokens.filter((token) => {
          const deps = api.getDependencies(token.id)
          return deps.length === 0
        })
      },

      // Get tokens with no dependents (leaf nodes)
      getLeafTokens(): TokenNode[] {
        return allTokens.filter((token) => {
          const dependents = api.getDependents(token.id)
          return dependents.length === 0
        })
      },

      // Check if token exists
      hasToken(id: string): boolean {
        return allTokens.some((t) => t.id === id)
      },

      // Get multiple tokens by IDs
      getTokensByIds(ids: string[]): TokenNode[] {
        return ids.map((id) => api.getNode(id)).filter((t): t is TokenNode => t !== null)
      },
    }),
    [allTokens, colors, spacing, shadows, typography, layout]
  )

  return api
}

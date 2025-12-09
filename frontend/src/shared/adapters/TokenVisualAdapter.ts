/**
 * Token Visual Adapter
 *
 * Adapter pattern for rendering token-specific UI elements.
 * Enables generic components to work with any token type (color, spacing, audio, video, etc.)
 * without hardcoding domain-specific logic.
 *
 * Key Innovation: Separates presentation logic from component structure.
 * - Generic components (TokenCard, TokenGrid) use adapters for rendering
 * - Domain-specific adapters (ColorVisualAdapter, SpacingVisualAdapter) handle visualization
 * - Adding new token types requires only creating new adapters (no changes to shared components)
 *
 * Architecture Benefits:
 * - ✅ Scales to multimodal (visual, audio, video tokens)
 * - ✅ Zero cross-domain dependencies
 * - ✅ Easy to add new token types
 * - ✅ Type-safe with generics
 */

import type { ReactNode } from 'react'

/**
 * Token Category
 * Re-exported from tokenGraphStore for convenience
 */
export type TokenCategory = 'color' | 'spacing' | 'shadow' | 'typography' | 'layout' | 'audio' | 'video' | 'motion'

/**
 * Tab Definition
 * Describes a detail tab in token inspector
 */
export interface TabDefinition {
  name: string
  label: string
  component: React.ComponentType<any>
  icon?: React.ComponentType<any>
}

/**
 * Token Visual Adapter Interface
 *
 * Contract for all token adapters (visual, audio, video, etc.)
 *
 * @template T - The token type (UiColorToken, UiSpacingToken, etc.)
 *
 * @example
 * ```typescript
 * const ColorVisualAdapter: TokenVisualAdapter<UiColorToken> = {
 *   category: 'color',
 *   renderSwatch: (token) => <div style={{ background: token.raw.$value }} />,
 *   renderMetadata: (token) => <div>Hex: {token.raw.$value}</div>,
 *   getDetailTabs: (token) => [
 *     { name: 'harmony', label: 'Harmony', component: HarmonyTab },
 *     { name: 'accessibility', label: 'Accessibility', component: AccessibilityTab }
 *   ],
 *   getDisplayName: (token) => token.id,
 *   getDisplayValue: (token) => token.raw.$value,
 *   canEdit: (token) => true
 * }
 * ```
 */
export interface TokenVisualAdapter<T> {
  /**
   * Token category this adapter handles
   */
  category: TokenCategory

  /**
   * Render the token's visual swatch/preview
   * - Colors: color swatch
   * - Spacing: ruler/scale visualization
   * - Audio: waveform
   * - Video: thumbnail/preview
   */
  renderSwatch: (token: T) => ReactNode

  /**
   * Render token metadata (confidence, properties, etc.)
   * Shown in hover cards, inspector panels, etc.
   */
  renderMetadata: (token: T) => ReactNode

  /**
   * Get detail tabs for token inspector
   * Each tab provides deep-dive into specific aspects
   * - Colors: Harmony, Accessibility, Properties, Diagnostics
   * - Spacing: Scale, Relationships, Grid
   * - Audio: Waveform, Spectrum, MIDI
   */
  getDetailTabs: (token: T) => TabDefinition[]

  /**
   * Get human-readable display name
   * Examples: "Primary Blue", "spacing-md", "440Hz A4"
   */
  getDisplayName: (token: T) => string

  /**
   * Get primary display value
   * Examples: "#2563eb", "16px", "440Hz"
   */
  getDisplayValue: (token: T) => string

  /**
   * Check if token can be edited in UI
   */
  canEdit?: (token: T) => boolean

  /**
   * Get icon component for token type
   * Optional: used in lists, toolbars, etc.
   */
  getIcon?: () => React.ComponentType<any>
}

/**
 * Adapter Registry
 * Maps token categories to their adapters
 */
export interface AdapterRegistry {
  [category: string]: TokenVisualAdapter<any>
}

/**
 * Global adapter registry
 * Populated by each feature module (visual-extraction, audio-extraction, etc.)
 */
const registry: AdapterRegistry = {}

/**
 * Register an adapter for a token category
 *
 * @example
 * ```typescript
 * registerAdapter(ColorVisualAdapter)
 * registerAdapter(AudioVisualAdapter)
 * ```
 */
export function registerAdapter<T>(adapter: TokenVisualAdapter<T>): void {
  registry[adapter.category] = adapter
}

/**
 * Get adapter for a token category
 *
 * @throws Error if no adapter registered for category
 *
 * @example
 * ```typescript
 * const adapter = getAdapter('color')
 * const swatch = adapter.renderSwatch(colorToken)
 * ```
 */
export function getAdapter<T>(category: TokenCategory): TokenVisualAdapter<T> {
  const adapter = registry[category]
  if (!adapter) {
    throw new Error(`No adapter registered for category: ${category}`)
  }
  return adapter
}

/**
 * Check if adapter is registered for category
 */
export function hasAdapter(category: TokenCategory): boolean {
  return category in registry
}

/**
 * Get all registered adapters
 */
export function getRegisteredAdapters(): AdapterRegistry {
  return { ...registry }
}

/**
 * Phase 0 / MVP feature flags.
 * Parked features stay in the codebase but off the default App path.
 * Flip to true only when promoting a P4+ feature.
 *
 * Park decision (keep flags, do not hard-unmount API routers):
 * - Frontend: these flags gate tabs/widgets in AppShell / TokenExplorer.
 * - Backend: parked routers remain mounted in app_factory.py for clients/tests;
 *   see comments there. Do not delete routers until a P4/P5 promotion plan.
 *
 * See docs/planning/MVP_EXPANSION_ROADMAP.md
 */

export const featureFlags = {
  /** Default explorer tabs: overview | colors | spacing | typography | shadows | shape | mood | export */
  /**
   * P4 lighting tab — production default OFF (G3/G4 policy).
   * Local/dev only: set true temporarily; do not commit. See P4_GEOMETRY_GATES.md
   * § Production flag policy.
   */
  showLightingTab: false,
  showRelationsTab: false,
  showRawTab: false,
  /**
   * Mood tab — AI mood boards (unparked 2026-09-22; promoted off Overview Labs).
   * When true: Mood appears in AppShell nav. Generation still requires an explicit
   * Generate click (never auto-runs). Kill switch: set false to hide the tab.
   * Lighting remains default-off. See MOOD_BOARD_SPECIFICATION.md.
   */
  showMoodBoard: true,
  /**
   * Overview: auto /lighting/analyze on image upload — P4.
   * Production default OFF after G1–G4: geometry must not sit on upload happy path.
   * Local/dev: set true here (rebuild frontend). Pair with showLightingTab
   * for the explorer Lighting tab. See docs/planning/P4_GEOMETRY_GATES.md
   * § G4 product acceptance + Production flag policy.
   */
  showLightingAnalyzer: false,
  /** Overview: TokenGraphDemo widget — demo / parked */
  showTokenGraphDemo: false,
} as const

export type MvpTab =
  | 'overview'
  | 'mood'
  | 'colors'
  | 'spacing'
  | 'typography'
  | 'shadows'
  | 'shape'
  | 'export'

export type ParkedTab = 'lighting' | 'relations' | 'raw'

export type AppTab = MvpTab | ParkedTab

export const MVP_TABS: readonly MvpTab[] = [
  'overview',
  'colors',
  'spacing',
  'typography',
  'shadows',
  'shape',
  'mood',
  'export',
] as const

/** Tabs visible in the App shell nav, based on flags. */
export function visibleAppTabs(): AppTab[] {
  const tabs: AppTab[] = ['overview']
  tabs.push('colors', 'spacing', 'typography', 'shadows', 'shape')
  if (featureFlags.showMoodBoard) tabs.push('mood')
  if (featureFlags.showLightingTab) tabs.push('lighting')
  tabs.push('export')
  if (featureFlags.showRelationsTab) tabs.push('relations')
  if (featureFlags.showRawTab) tabs.push('raw')
  return tabs
}

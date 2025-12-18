/**
 * Static semantic metadata for the shared Tabs primitive.
 * This file is intentionally not imported at runtime; it documents structure only.
 */

export const tabsSemantics = {
  component: 'Tabs',
  description: 'Controlled tab primitive used across panels/playground without altering visuals.',
  parts: [
    { name: 'Tabs', role: 'container', notes: 'Provides context + value for triggers/panels.' },
    { name: 'TabList', role: 'presentation', notes: 'Wraps TabTrigger elements; no semantics enforced.' },
    { name: 'TabTrigger', role: 'button', notes: 'Uses aria-pressed and data-active for styling; controlled externally.' },
    { name: 'TabPanels', role: 'container', notes: 'Grouping element for panels (optional).' },
    { name: 'TabPanel', role: 'tabpanel', notes: 'Renders only when matching the active value; consumer supplies IDs/headings.' },
  ],
} as const

export type TabsSemantics = typeof tabsSemantics

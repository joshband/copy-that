---
name: token-review-ui-improvements
description: Improve token review UI layout, metadata visibility, and scanability.
---

# Review Findings

- High: Primary layout defines a two-column grid but only renders the upload panel, leaving a large empty column and pushing token content below the fold; this dominates the overview and colors screens. Evidence in extraction-flow-exposes-token-data-points-and-captures-screens-01-main.png and extraction-flow-exposes-token-data-points-and-captures-screens-04-colors-overview.png; layout in App.tsx (line 53) and App.css (line 118) (also amplified by App.css (line 134)).
- High: Color detail header metadata and count info are explicitly hidden, so key data points are not visible during review. ColorDetailPanel.css (line 119) and ColorDetailPanel.css (line 170); visible in extraction-flow-exposes-token-data-points-and-captures-screens-05-colors-accessibility.png.
- Medium: Spacing tab stacks six full sections with no navigation or collapses, creating a long vertical scroll and low scanability. TokenExplorer.tsx (line 241) and TokenExplorer.tsx (line 248); extraction-flow-exposes-token-data-points-and-captures-screens-10-spacing.png.
- Medium: Typography inspector renders style attributes as one long inline string, which is dense and hard to parse. TypographyInspector.tsx (line 31); extraction-flow-exposes-token-data-points-and-captures-screens-11-typography.png.
- Low: State variant cards rely on swatch differences without deltas or contrast markers, so variants can look identical for dark colors and reduce the value of the tab. StateVariantsTab.tsx (line 89); extraction-flow-exposes-token-data-points-and-captures-screens-08-colors-states.png.

## Open Questions

- Should the right-hand column in the primary row host TokenExplorer content, or should it be a new summary/preview panel?
- Do you want the typography and spacing tabs optimized for scanning (condensed cards/accordions) or for teaching (long-form narrative)?
- No code changes made.

# Plan

Improve token review usability by reclaiming unused layout space, surfacing key metadata, and reorganizing dense tabs to reduce scrolling while keeping the extraction flow and data unchanged.

## Requirements
- Use the primary viewport area efficiently without large empty regions.
- Make core token metadata visible by default (counts, confidence, semantic roles, accessibility).
- Improve scanability in spacing, typography, and shadows tabs.
- Keep Playwright screenshot flow intact and update baselines as needed.

## Scope
- In: App layout, token tab layouts, color detail visibility, typography inspector formatting, spacing organization, screenshot updates.
- Out: Backend extraction logic, token schema changes, or new token types.

## Files and entry points
- frontend/src/App.tsx
- frontend/src/App.css
- frontend/src/features/explorer/TokenExplorer.tsx
- frontend/src/features/visual-extraction/components/color/color-detail-panel/ColorDetailPanel.css
- frontend/src/features/visual-extraction/components/typography/TypographyInspector.tsx
- frontend/src/features/visual-extraction/components/spacing/SpacingDetailCard.tsx
- frontend/tests/playwright/token-data-points.spec.ts

## Data model / API changes
- None.

## Action items
[ ] Decide primary-row layout: move TokenExplorer into the right column or add a summary/preview panel; remove unused grid space and revisit min-height settings.
[ ] Re-enable color header metadata and count badges; confirm which fields should always show for data review.
[ ] Reorganize spacing tab into grouped sections (sub-tabs or accordions) to reduce scroll and improve navigation.
[ ] Convert typography style attributes into a structured list or grid with wrapping and optional expand/collapse.
[ ] Add clearer differentiation for color state variants (delta metrics, labels, or contrast indicators).
[ ] Update Playwright screenshots after layout changes and validate all tabs still render expected data.

## Testing and validation
- pnpm exec playwright test -c frontend/playwright.config.ts frontend/tests/playwright/token-data-points.spec.ts
- Manual visual scan of colors, spacing, typography, shadows tabs.

## Risks and edge cases
- Layout changes could break responsive behavior or introduce new overflow issues.
- Surfacing hidden metadata might create visual clutter without careful styling.
- Collapsing sections could hide data from first-time users if defaults are not clear.

## Open questions
- Do you want any sections pinned (sticky) for faster comparison while scrolling?
- Should the overview tab prioritize diagnostics or token graph content?

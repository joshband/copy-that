feat/advanced-spacing-extraction branch | 12/20/2025

# Findings

- High: Diagnostics tab is always empty in this flow because the overlay never reaches the color detail panel; TokenExplorer.tsx (line 273), UploadPanel.tsx (line 159), DiagnosticsTab.tsx (line 3). Seen in extraction-flow-exposes-token-data-points-and-captures-screens-10-colors-diagnostics.png.
- High: Overview tools are disconnected from extracted data, so Lighting Analyzer, Token Graph Demo, and diagnostics stay in empty states after extraction; TokenExplorer.tsx (line 360). Seen in extraction-flow-exposes-token-data-points-and-captures-screens-03-extract-clicked.png.
- Medium: Upload panel remains tall and sits above token review content, forcing repeated scroll to reach colors/spacing/typography after extraction; App.css (line 138), App.tsx (line 53). Seen in extraction-flow-exposes-token-data-points-and-captures-screens-04-colors-overview.png.
- Medium: Spacing tab shows duplicate token listings (scale panel + graph list) in the same card, pushing metadata and responsive sections lower; TokenExplorer.tsx (line 298), SpacingScalePanel.tsx (line 12), SpacingGraphList.tsx (line 4). Seen in extraction-flow-exposes-token-data-points-and-captures-screens-11-spacing.png.
- Low: Typography style attribute chips lack a clear label/section title, which makes the metadata block feel detached from the inspector; TypographyInspector.tsx (line 31), App.css (line 398). Seen in extraction-flow-exposes-token-data-points-and-captures-screens-12-typography.png.


## Open Questions

- Should upload collapse automatically after extraction, or only on user toggle?
- Where do you want the overlay/image data to live long-term (tokenGraphStore vs. local UploadPanel state)?


# Plan

Improve functional completeness and scanability by wiring diagnostics/overview data, reducing repeated scroll, and decluttering spacing/typography metadata without changing extraction logic.

## Requirements

- Diagnostics and overview panels show real extraction data (or actionable CTAs).
- Upload workflow does not block token review once extraction completes.
- Spacing and typography views remain comprehensive but faster to scan.
- Updated Playwright flow captures new states and remains stable.

## Scope

In: Upload panel behavior, overview data wiring, diagnostics overlay wiring, spacing layout refinement, typography metadata labeling, Playwright updates.

Out: Backend extraction changes, token schema changes.

Files and entry points
- UploadPanel.tsx
- TokenExplorer.tsx
- App.tsx
- App.css
- ColorDetailPanel.tsx
- DiagnosticsTab.tsx
- LightingAnalyzer.tsx
- DiagnosticsPanel.tsx
- TokenGraphDemo.tsx
- SpacingScalePanel.tsx
- SpacingGraphList.tsx
- TypographyInspector.tsx
- token-data-points.spec.ts

## Data model / API changes

None (wire existing in-memory data to UI).

## Action items

- [ ] Pass debug overlay, segmented palette, spacing results, and image data from UploadPanel to TokenExplorer (or store) and feed them into DiagnosticsPanel, TokenGraphDemo, and ColorTokenDisplay diagnostics.
- [ ] Add a compact/collapsible upload header after extraction (summary + “Change image”), leaving a toggle to expand full upload controls.
- [ ] Replace the duplicate spacing list by merging SpacingGraphList into SpacingScalePanel or converting it into a compact summary row.
- [ ] Add a “Style attributes” label/section header for typography chips and optionally group them into 2–3 categories for scanability.
- [ ] Add contextual CTAs in empty diagnostics/overview states (e.g., “Enable debug overlay” or “Run analysis”).
- [ ] Update Playwright assertions/screens to cover the populated overview/diagnostics states and new compact upload layout.

## Testing and validation

- token-data-points.spec.ts
- Manual check of overview tab post-extraction (lighting/graph/diagnostics now populated).

## Risks and edge cases

- Wiring more data through UploadPanel may complicate state and re-renders.
- Collapsing the upload panel could hide needed controls if not discoverable.
- Diagnostics overlays may be large; ensure rendering is performant and opt-in.

## Open questions
- Should diagnostics be visible only when “Debug on” is enabled, or always show with a CTA?
- Do you want the overview tab to become the default landing after extraction?

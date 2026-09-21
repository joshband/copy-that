import type { ReactNode } from 'react'
import type { Props } from './types'
import { ColorHeader } from './ColorHeader'
import { OverviewTab } from './tabs/OverviewTab'
import { HarmonyTab } from './tabs/HarmonyTab'
import { AccessibilityTab } from './tabs/AccessibilityTab'
import { PropertiesTab } from './tabs/PropertiesTab'
import { NamingStylesTab } from './tabs/NamingStylesTab'
import { StateVariantsTab } from './tabs/StateVariantsTab'
import { DiagnosticsTab } from './tabs/DiagnosticsTab'
import './ColorDetailPanel.css'

function DetailCard({
  title,
  children,
  note,
}: {
  title: string
  children: ReactNode
  note?: string
}) {
  return (
    <article className="detail-panel color-detail-card">
      <h3 className="color-detail-card__title">{title}</h3>
      {note ? <p className="color-detail-card__note">{note}</p> : null}
      <div className="tab-content">{children}</div>
    </article>
  )
}

export function ColorDetailPanel({
  color,
  debugOverlay,
  isAlias,
  aliasTargetId,
  showDebug = false,
}: Props) {
  if (!color) {
    return (
      <div className="detail-panel empty">
        <div className="empty-state">
          <h3 className="standin">Select a color to explore</h3>
          <p className="standin">Click any swatch in the palette to view its properties</p>
        </div>
      </div>
    )
  }

  return (
    <div className="color-detail-stack">
      <article className="detail-panel color-detail-card color-detail-card--identity">
        <ColorHeader color={color} isAlias={isAlias} aliasTargetId={aliasTargetId} />
      </article>
      <DetailCard title="Overview">
        <OverviewTab color={color} />
      </DetailCard>
      <DetailCard title="Accessibility">
        <AccessibilityTab color={color} />
      </DetailCard>

      <details className="color-detail-more">
        <summary>More analysis</summary>
        <div className="color-detail-more__body">
          <DetailCard title="Harmony">
            <HarmonyTab color={color} />
          </DetailCard>
          <DetailCard title="Properties">
            <PropertiesTab color={color} />
          </DetailCard>
          <DetailCard title="Names" note="Generated naming suggestions — not extracted labels">
            <NamingStylesTab color={color} />
          </DetailCard>
          <DetailCard title="States" note="Generated variants — not observed UI states">
            <StateVariantsTab color={color} />
          </DetailCard>
        </div>
      </details>

      {showDebug && debugOverlay ? (
        <DetailCard title="Diagnostics">
          <DiagnosticsTab overlay={debugOverlay} />
        </DetailCard>
      ) : null}
    </div>
  )
}

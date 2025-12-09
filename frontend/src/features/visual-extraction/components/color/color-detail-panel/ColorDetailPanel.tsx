import { useState } from 'react'
import type { Props, TabType } from './types'
import { ColorHeader } from './ColorHeader'
import { OverviewTab } from './tabs/OverviewTab'
import { HarmonyTab } from './tabs/HarmonyTab'
import { AccessibilityTab } from './tabs/AccessibilityTab'
import { PropertiesTab } from './tabs/PropertiesTab'
import { DiagnosticsTab } from './tabs/DiagnosticsTab'

export function ColorDetailPanel({ color, debugOverlay, isAlias, aliasTargetId }: Props) {
  const [activeTab, setActiveTab] = useState<TabType>('overview')

  if (!color) {
    return (
      <div className="detail-panel empty">
        <div className="empty-state">
          <div className="empty-icon">🎨</div>
          <h3>Select a color to explore</h3>
          <p>Click on any color from the palette to view its properties</p>
        </div>
      </div>
    )
  }

  return (
    <div className="detail-panel">
      <ColorHeader color={color} isAlias={isAlias} aliasTargetId={aliasTargetId} />

      {/* Tabs */}
      <div className="tabs">
        <button
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        {color.harmony != null && color.harmony !== '' && (
          <button
            className={`tab ${activeTab === 'harmony' ? 'active' : ''}`}
            onClick={() => setActiveTab('harmony')}
          >
            Harmony
          </button>
        )}
        <button
          className={`tab ${activeTab === 'accessibility' ? 'active' : ''}`}
          onClick={() => setActiveTab('accessibility')}
        >
          Accessibility
        </button>
        <button
          className={`tab ${activeTab === 'properties' ? 'active' : ''}`}
          onClick={() => setActiveTab('properties')}
        >
          Properties
        </button>
        {debugOverlay && (
          <button
            className={`tab ${activeTab === 'diagnostics' ? 'active' : ''}`}
            onClick={() => setActiveTab('diagnostics')}
          >
            Diagnostics
          </button>
        )}
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'overview' && <OverviewTab color={color} />}
        {activeTab === 'harmony' && color.harmony != null && color.harmony !== '' && (
          <HarmonyTab color={color} />
        )}
        {activeTab === 'accessibility' && (
          <AccessibilityTab color={color} />
        )}
        {activeTab === 'properties' && <PropertiesTab color={color} />}
        {activeTab === 'diagnostics' && debugOverlay && (
          <DiagnosticsTab overlay={debugOverlay} />
        )}
      </div>
    </div>
  )
}

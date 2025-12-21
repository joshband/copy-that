import { useState } from 'react'
import type { Props, TabType } from './types'
import { ColorHeader } from './ColorHeader'
import { OverviewTab } from './tabs/OverviewTab'
import { HarmonyTab } from './tabs/HarmonyTab'
import { AccessibilityTab } from './tabs/AccessibilityTab'
import { PropertiesTab } from './tabs/PropertiesTab'
import { NamingStylesTab } from './tabs/NamingStylesTab'
import { StateVariantsTab } from './tabs/StateVariantsTab'
import { DiagnosticsTab } from './tabs/DiagnosticsTab'
import './ColorDetailPanel.css'

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
        <button
          className={`tab ${activeTab === 'harmony' ? 'active' : ''}`}
          onClick={() => setActiveTab('harmony')}
        >
          Harmony
        </button>
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
        <button
          className={`tab ${activeTab === 'naming_styles' ? 'active' : ''}`}
          onClick={() => setActiveTab('naming_styles')}
        >
          Names
        </button>
        <button
          className={`tab ${activeTab === 'state_variants' ? 'active' : ''}`}
          onClick={() => setActiveTab('state_variants')}
        >
          States
        </button>
        <button
          className={`tab ${activeTab === 'diagnostics' ? 'active' : ''}`}
          onClick={() => setActiveTab('diagnostics')}
        >
          Diagnostics
        </button>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'overview' && <OverviewTab color={color} />}
        {activeTab === 'harmony' && <HarmonyTab color={color} />}
        {activeTab === 'accessibility' && (
          <AccessibilityTab color={color} />
        )}
        {activeTab === 'properties' && <PropertiesTab color={color} />}
        {activeTab === 'naming_styles' && <NamingStylesTab color={color} />}
        {activeTab === 'state_variants' && <StateVariantsTab color={color} />}
        {activeTab === 'diagnostics' && <DiagnosticsTab overlay={debugOverlay} />}
      </div>
    </div>
  )
}

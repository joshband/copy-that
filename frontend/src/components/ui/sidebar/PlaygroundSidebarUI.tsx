import { useActiveTab, useCustomBackground } from './hooks'
import { HarmonyTab } from './tabs/HarmonyTab'
import { AccessibilityTab } from './tabs/AccessibilityTab'
import { PickerTab } from './tabs/PickerTab'
import { VariantsTab } from './tabs/VariantsTab'
import type { PlaygroundSidebarProps } from './types'

interface UIProps extends PlaygroundSidebarProps {}

export function PlaygroundSidebarUI({ selectedColor, isOpen: _isOpen, onToggle: _onToggle }: UIProps) {
  void _isOpen
  void _onToggle
  const { activeTab, switchTab } = useActiveTab('harmony')
  const { customBgColor, updateBackground } = useCustomBackground('#ffffff')

  if (!selectedColor) {
    return (
      <div className={`playground-sidebar empty`}>
        <div className="empty-message">
          <p>Select a color to explore</p>
        </div>
      </div>
    )
  }

  return (
    <div className={`playground-sidebar`}>
      <div className="sidebar-content">
        {/* Tabs */}
        <div className="tab-buttons">
          <button
            className={`tab-btn ${activeTab === 'harmony' ? 'active' : ''}`}
            onClick={() => switchTab('harmony')}
            title="Harmony relationships"
          >
            🌈
          </button>
          <button
            className={`tab-btn ${activeTab === 'accessibility' ? 'active' : ''}`}
            onClick={() => switchTab('accessibility')}
            title="WCAG accessibility"
          >
            ♿
          </button>
          <button
            className={`tab-btn ${activeTab === 'picker' ? 'active' : ''}`}
            onClick={() => switchTab('picker')}
            title="Color picker"
          >
            🎨
          </button>
          <button
            className={`tab-btn ${activeTab === 'variants' ? 'active' : ''}`}
            onClick={() => switchTab('variants')}
            title="Generate variants"
          >
            ✨
          </button>
        </div>

        {/* Tab Content */}
        <div className="tab-content">
          {activeTab === 'harmony' && <HarmonyTab selectedColor={selectedColor} />}

          {activeTab === 'accessibility' && (
            <AccessibilityTab
              selectedColor={selectedColor}
              customBgColor={customBgColor}
              onBackgroundChange={updateBackground}
            />
          )}

          {activeTab === 'picker' && <PickerTab selectedColor={selectedColor} />}

          {activeTab === 'variants' && <VariantsTab selectedColor={selectedColor} />}
        </div>
      </div>
    </div>
  )
}

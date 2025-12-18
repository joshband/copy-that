import { useActiveTab, useCustomBackground } from './hooks'
import { HarmonyTab } from './tabs/HarmonyTab'
import { AccessibilityTab } from './tabs/AccessibilityTab'
import { PickerTab } from './tabs/PickerTab'
import { VariantsTab } from './tabs/VariantsTab'
import type { PlaygroundSidebarProps } from './types'
import { Tabs, TabList, TabTrigger, TabPanels, TabPanel } from '../tabs/Tabs'

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
        <Tabs value={activeTab} onValueChange={switchTab}>
          <TabList className="tab-buttons">
            <TabTrigger
              value="harmony"
              className="tab-btn"
              activeClassName="active"
              aria-label="Harmony relationships"
            >
              🌈
            </TabTrigger>
            <TabTrigger
              value="accessibility"
              className="tab-btn"
              activeClassName="active"
              aria-label="WCAG accessibility"
            >
              ♿
            </TabTrigger>
            <TabTrigger
              value="picker"
              className="tab-btn"
              activeClassName="active"
              aria-label="Color picker"
            >
              🎨
            </TabTrigger>
            <TabTrigger
              value="variants"
              className="tab-btn"
              activeClassName="active"
              aria-label="Generate variants"
            >
              ✨
            </TabTrigger>
          </TabList>

          <TabPanels className="tab-content">
            <TabPanel value="harmony">
              <HarmonyTab selectedColor={selectedColor} />
            </TabPanel>
            <TabPanel value="accessibility">
              <AccessibilityTab
                selectedColor={selectedColor}
                customBgColor={customBgColor}
                onBackgroundChange={updateBackground}
              />
            </TabPanel>
            <TabPanel value="picker">
              <PickerTab selectedColor={selectedColor} />
            </TabPanel>
            <TabPanel value="variants">
              <VariantsTab selectedColor={selectedColor} />
            </TabPanel>
          </TabPanels>
        </Tabs>
      </div>
    </div>
  )
}

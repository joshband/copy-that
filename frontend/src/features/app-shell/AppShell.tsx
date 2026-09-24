import { ReactNode, useMemo, useEffect, useRef, useState } from 'react'
import { useExtractionState, phaseLabel } from '../extraction/state'
import { type AppTab, visibleAppTabs } from '../../config/featureFlags'

const TAB_LABELS: Record<AppTab, string> = {
  overview: 'Overview',
  mood: 'Mood',
  colors: 'Colors',
  spacing: 'Spacing',
  typography: 'Typography',
  shadows: 'Shadows',
  shape: 'Shape',
  export: 'Export',
  lighting: 'Lighting',
  relations: 'Relations',
  raw: 'Raw',
}

interface AppShellProps {
  projectId: number | null
  activeTab: AppTab
  onTabChange: (tab: AppTab) => void
  isLoading: boolean
  showDebug: boolean
  onToggleDebug: () => void
  warnings: string[]
  error?: string
  headerActions?: ReactNode
  /** Sticky session chrome (upload / source strip) below tabs */
  sessionChrome?: ReactNode
  children: ReactNode
}

export function AppShell({
  projectId,
  activeTab,
  onTabChange,
  showDebug,
  onToggleDebug,
  warnings,
  error,
  headerActions,
  sessionChrome,
  children,
}: AppShellProps) {
  const phase = useExtractionState(s => s.phase)
  const [focusedTab, setFocusedTab] = useState(activeTab)
  const tabList = useRef<HTMLElement>(null)
  useEffect(() => {
    setFocusedTab(activeTab)
    tabList.current?.querySelector<HTMLElement>(`#tab-${activeTab}`)?.scrollIntoView({ block: 'nearest', inline: 'nearest' })
  }, [activeTab])
  const tabs = useMemo(() => visibleAppTabs(), [])

  const warningBanner = useMemo(() => {
    if (error) return null
    if (!warnings.length) return null
    return (
      <div className="warning-banner" role="status" aria-live="polite">
        <strong>Heads up:</strong> {warnings.join(' ')}
      </div>
    )
  }, [error, warnings])

  return (
    <div className="app-shell">
      <div className="sticky-chrome">
        <header className="app-header">
          <div className="header-content">
            <div className="header-title">
              <h1>Copy That</h1>
              {projectId != null && <span className="project-id">Project #{projectId}</span>}
            </div>
            <div className="header-actions">
              <span className="source-status" role="status">{phaseLabel[phase]}</span>
              {projectId != null && <button type="button" onClick={() => onTabChange('export')}>Export</button>}
              <details className="settings-disclosure">
                <summary>Settings</summary>
                <label><input type="checkbox" checked={showDebug} onChange={onToggleDebug} /> Show debug details</label>
              </details>
              {headerActions}
            </div>
          </div>
        </header>

        <nav ref={tabList} className="tabs tab-row" role="tablist" aria-label="Token explorer" onBlur={(event) => { if (!event.currentTarget.contains(event.relatedTarget as Node)) setFocusedTab(activeTab) }}>
          {tabs.map((tab) => (
            <button
              key={tab}
              id={`tab-${tab}`}
              role="tab"
              aria-selected={activeTab === tab}
              aria-controls={`panel-${tab}`}
              tabIndex={focusedTab === tab ? 0 : -1}
              onFocus={() => setFocusedTab(tab)}
              onKeyDown={(event) => {
                const index = tabs.indexOf(tab)
                const next = event.key === 'ArrowRight' ? (index + 1) % tabs.length : event.key === 'ArrowLeft' ? (index - 1 + tabs.length) % tabs.length : event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1 : null
                if (next != null) {
                  event.preventDefault()
                  tabList.current?.querySelector<HTMLElement>(`#tab-${tabs[next]}`)?.focus()
                }
              }}
              className={`tab-button ${activeTab === tab ? 'active' : ''}`}
              onClick={() => onTabChange(tab)}
              type="button"
            >
              {TAB_LABELS[tab] ?? tab}
            </button>
          ))}
        </nav>

      </div>
      {error && <div className="error-banner" role="alert">{error}</div>}
      {warningBanner}
      <main className="app-main workspace">
        {sessionChrome ? <aside className="source-column" aria-label="Source image">{sessionChrome}</aside> : null}
        <div className="inspection-column" role="tabpanel" id={`panel-${activeTab}`} aria-labelledby={`tab-${activeTab}`} tabIndex={0}>{children}</div>
      </main>
    </div>
  )
}

import { ReactNode, useMemo } from 'react'
import { type AppTab, visibleAppTabs } from '../../config/featureFlags'

const TAB_LABELS: Record<AppTab, string> = {
  overview: 'Overview',
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
  isLoading,
  showDebug,
  onToggleDebug,
  warnings,
  error,
  headerActions,
  sessionChrome,
  children,
}: AppShellProps) {
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
              {isLoading && (
                <div className="loading-chip small" aria-live="polite">
                  Processing image…
                </div>
              )}
              <span className="overlay-label">{showDebug ? 'Debug on' : 'Debug off'}</span>
              <label className="switch" title="Show validation and advanced panels">
                <input type="checkbox" checked={showDebug} onChange={onToggleDebug} />
                <span className="slider" />
              </label>
              {headerActions}
            </div>
          </div>
          {error && <div className="error-banner">{error}</div>}
          {warningBanner}
        </header>

        <nav className="tabs tab-row" aria-label="Token explorer">
          {tabs.map((tab) => (
            <button
              key={tab}
              className={`tab-button ${activeTab === tab ? 'active' : ''}`}
              onClick={() => onTabChange(tab)}
              type="button"
            >
              {TAB_LABELS[tab] ?? tab}
            </button>
          ))}
        </nav>

        {sessionChrome ? <div className="sticky-chrome__session">{sessionChrome}</div> : null}
      </div>

      <main className="app-main">{children}</main>
    </div>
  )
}

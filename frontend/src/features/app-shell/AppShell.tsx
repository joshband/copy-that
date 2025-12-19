import { ReactNode, useMemo } from 'react'

type Tab =
  | 'overview'
  | 'colors'
  | 'spacing'
  | 'typography'
  | 'shadows'
  | 'lighting'
  | 'export'
  | 'relations'
  | 'raw'

interface AppShellProps {
  projectId: number | null
  activeTab: Tab
  onTabChange: (tab: Tab) => void
  isLoading: boolean
  showDebug: boolean
  onToggleDebug: () => void
  warnings: string[]
  error?: string
  headerActions?: ReactNode
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
  children,
}: AppShellProps) {
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
      <header className="app-header">
        <div className="header-left">
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
          <label className="switch">
            <input type="checkbox" checked={showDebug} onChange={onToggleDebug} />
            <span className="slider" />
          </label>
          {headerActions}
        </div>
        {error && <div className="error-banner">{error}</div>}
        {warningBanner}
      </header>

      <nav className="tabs">
        {(
          [
            'overview',
            'colors',
            'spacing',
            'typography',
            'shadows',
            'lighting',
            'export',
            'relations',
            'raw',
          ] as Tab[]
        ).map((tab) => (
          <button
            key={tab}
            className={`tab ${activeTab === tab ? 'active' : ''}`}
            onClick={() => onTabChange(tab)}
            type="button"
          >
            {tab}
          </button>
        ))}
      </nav>

      <main className="app-main">{children}</main>
    </div>
  )
}

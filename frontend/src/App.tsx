import { useState } from 'react'
import ImageUploader from './components/ImageUploader'
import TokenToolbar from './components/TokenToolbar'
import TokenGrid from './components/TokenGrid'
import TokenInspectorSidebar from './components/TokenInspectorSidebar'
import TokenPlaygroundDrawer from './components/TokenPlaygroundDrawer'
import { useTokenStore } from './store/tokenStore'
import { ColorToken } from './types'
import './App.css'

export default function App() {
  const [projectId, setProjectId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  // Store hooks
  const { setTokens, setProjectId: setStoreProjectId, tokens, isExtracting } = useTokenStore()

  // Create or manage project
  const handleProjectCreated = (id: number) => {
    const projectIdStr = String(id)
    setProjectId(projectIdStr)
    setStoreProjectId(projectIdStr)
    setError(null)
  }

  // Handle color extraction
  const handleColorExtracted = (extractedColors: ColorToken[]) => {
    setTokens(extractedColors)
    setLoading(false)
    setError(null)
  }

  const handleError = (errorMsg: string) => {
    setError(errorMsg)
    setLoading(false)
  }

  const handleLoadingChange = (isLoading: boolean) => {
    setLoading(isLoading)
  }

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="header-title">
            <h1>Copy That</h1>
            {projectId != null && projectId !== '' && <span className="project-id">Project: {projectId}</span>}
          </div>
          <div className="header-upload">
            <ImageUploader
              projectId={projectId != null && projectId !== '' ? parseInt(projectId) : null}
              onProjectCreated={handleProjectCreated}
              onColorExtracted={handleColorExtracted}
              onError={handleError}
              onLoadingChange={handleLoadingChange}
            />
          </div>
        </div>
        {error != null && error !== '' && (
          <div className="error-banner">
            <span>⚠️ {error}</span>
          </div>
        )}
      </header>

      {/* Main Layout */}
      <div className="app-layout">
        {/* Playground Drawer (Left) */}
        <TokenPlaygroundDrawer />

        {/* Main Content Area */}
        <main className="app-main">
          {/* Loading State */}
          {(loading || isExtracting) && (
            <div className="loading-state">
              <div className="spinner"></div>
              <p>Extracting colors...</p>
            </div>
          )}

          {/* Token Grid View */}
          {!loading && !isExtracting && tokens.length > 0 && (
            <>
              <TokenToolbar />
              <TokenGrid />
            </>
          )}

          {/* Empty State */}
          {!loading && !isExtracting && tokens.length === 0 && (error == null || error === '') && (
            <div className="empty-state">
              <div className="empty-content">
                <p className="empty-icon">🎨</p>
                <p className="empty-title">Upload an image to begin</p>
                <p className="empty-subtitle">Extract colors and explore their properties</p>
              </div>
            </div>
          )}
        </main>

        {/* Inspector Sidebar (Right) */}
        <TokenInspectorSidebar />
      </div>
    </div>
  )
}

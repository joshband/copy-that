import { useEffect, useState } from 'react'
import './App.css'
import ImageUploader from './components/ImageUploader'
import ColorTokenDisplay from './components/ColorTokenDisplay'
import type { ColorToken } from './types'

export default function App() {
  // Ensure global scroll isn’t disabled by other styles
  useEffect(() => {
    const originalBodyOverflow = document.body.style.overflowY
    const originalHtmlOverflow = document.documentElement.style.overflowY
    document.body.style.overflowY = 'auto'
    document.documentElement.style.overflowY = 'auto'
    return () => {
      document.body.style.overflowY = originalBodyOverflow
      document.documentElement.style.overflowY = originalHtmlOverflow
    }
  }, [])

  const [projectId, setProjectId] = useState<number | null>(null)
  const [colors, setColors] = useState<ColorToken[]>([])
  const [error, setError] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)
  const [hasUpload, setHasUpload] = useState(false)

  const handleColorsExtracted = (extracted: ColorToken[]) => {
    setColors(extracted)
    setHasUpload(true)
  }

  const handleProjectCreated = (id: number) => {
    setProjectId(id)
  }

  const handleError = (message: string) => {
    setError(message)
  }

  const handleLoadingChange = (loading: boolean) => {
    setIsLoading(loading)
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="header-title">
            <h1>Copy That Playground</h1>
            {projectId != null && <span className="project-id">Project #{projectId}</span>}
          </div>
          {isLoading && (
            <div className="loading-chip" aria-live="polite">
              Processing image…
            </div>
          )}
        </div>
        {error && <div className="error-banner">{error}</div>}
      </header>

      <main className="app-main">
        <div className="app-grid">
          <section className="panel">
            <h2>Upload an image</h2>
            <p className="panel-subtitle">
              We’ll send it to the backend, stream the extraction, and render tokens below.
            </p>
            <ImageUploader
              projectId={projectId}
              onProjectCreated={handleProjectCreated}
              onColorExtracted={handleColorsExtracted}
              onError={handleError}
              onLoadingChange={handleLoadingChange}
            />
          </section>

          <section className="panel">
            <h2>Extracted tokens</h2>
            <p className="panel-subtitle">
              Browse the palette and details as soon as extraction completes.
            </p>
            {hasUpload && colors.length === 0 && !isLoading && (
              <div className="empty-state">
                <div className="empty-content">
                  <div className="empty-icon">⌛</div>
                  <p className="empty-title">No tokens yet</p>
                  <p className="empty-subtitle">Upload an image to see extracted colors</p>
                </div>
              </div>
            )}
            {colors.length > 0 && <ColorTokenDisplay colors={colors} />}
            {!hasUpload && colors.length === 0 && (
              <div className="empty-state">
                <div className="empty-content">
                  <div className="empty-icon">🖼️</div>
                  <p className="empty-title">Drop an image to begin</p>
                  <p className="empty-subtitle">We’ll stream results from the backend</p>
                </div>
              </div>
            )}
          </section>
        </div>
      </main>
    </div>
  )
}

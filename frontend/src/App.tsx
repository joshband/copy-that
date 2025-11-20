import { useState } from 'react'
import ImageUploader from './components/ImageUploader'
import ColorTokenDisplay from './components/ColorTokenDisplay'
import './App.css'

interface ColorToken {
  id?: number
  hex: string
  rgb: string
  name: string
  semantic_name?: string
  confidence: number
  harmony?: string
  usage?: string[]
  count?: number
  created_at?: string
}

export default function App() {
  const [projectId, setProjectId] = useState<number | null>(null)
  const [colors, setColors] = useState<ColorToken[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Create or manage project
  const handleProjectCreated = (id: number) => {
    setProjectId(id)
    setError(null)
  }

  // Handle color extraction
  const handleColorExtracted = (extractedColors: ColorToken[]) => {
    setColors(extractedColors)
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
      <header className="header">
        <h1>🎨 Copy That</h1>
        <p>AI-Powered Color Extraction Platform</p>
      </header>

      <main className="main">
        {/* Image Upload Section */}
        <section className="section">
          <h2>Upload Image</h2>
          <ImageUploader
            projectId={projectId}
            onProjectCreated={handleProjectCreated}
            onColorExtracted={handleColorExtracted}
            onError={handleError}
            onLoadingChange={handleLoadingChange}
          />
        </section>

        {/* Error Display */}
        {error && (
          <section className="error-section">
            <div className="error-message">⚠️ {error}</div>
          </section>
        )}

        {/* Loading Indicator */}
        {loading && (
          <section className="loading-section">
            <div className="spinner"></div>
            <p>Extracting colors...</p>
          </section>
        )}

        {/* Color Display Section */}
        {colors.length > 0 && (
          <section className="section">
            <h2>Extracted Colors ({colors.length})</h2>
            <ColorTokenDisplay colors={colors} />
          </section>
        )}

        {!loading && colors.length === 0 && !error && (
          <section className="section empty">
            <p>👆 Upload an image to extract colors</p>
          </section>
        )}
      </main>

      <footer className="footer">
        <p>Copy That v1.0.0 — Multi-Modal Token Platform</p>
      </footer>
    </div>
  )
}

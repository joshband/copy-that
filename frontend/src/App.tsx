import { useEffect, useState } from 'react'
import './App.css'
import { AppShell } from './features/app-shell/AppShell'
import type { ColorRampMap, LightingAnalysis, SegmentedColor, SpacingExtractionResponse } from './types'

import UploadPanel from './features/upload/UploadPanel'
import TokenExplorer from './features/explorer/TokenExplorer'

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

export default function App() {
  const [projectId, setProjectId] = useState<number | null>(null)
  const [error, setError] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)
  const [showDebug, setShowDebug] = useState(false)
  const [activeTab, setActiveTab] = useState<Tab>('overview')
  const [warnings, setWarnings] = useState<string[]>([])
  const [lightingAnalysis, setLightingAnalysis] = useState<LightingAnalysis | null>(null)
  const [imageBase64, setImageBase64] = useState<string | null>(null)
  const [colorRamps, setColorRamps] = useState<ColorRampMap>({})
  const [segmentedPalette, setSegmentedPalette] = useState<SegmentedColor[] | null>(null)
  const [paletteSummary, setPaletteSummary] = useState<string | null>(null)
  const [spacingResult, setSpacingResult] = useState<SpacingExtractionResponse | null>(null)
  const [debugOverlay, setDebugOverlay] = useState<string | null>(null)

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

  useEffect(() => {
    if (!isLoading) return
    setActiveTab('overview')
    setImageBase64(null)
    setColorRamps({})
    setSegmentedPalette(null)
    setPaletteSummary(null)
    setSpacingResult(null)
    setDebugOverlay(null)
  }, [isLoading])

  return (
    <div className="app">
      <AppShell
        projectId={projectId}
        activeTab={activeTab}
        onTabChange={setActiveTab}
        isLoading={isLoading}
        showDebug={showDebug}
        onToggleDebug={() => setShowDebug((s) => !s)}
        warnings={warnings}
        error={error}
      >
        <div className="primary-row">
          <UploadPanel
            projectId={projectId}
            onProjectCreated={setProjectId}
            onError={setError}
            onLoadingChange={setIsLoading}
            showDebug={showDebug}
            onWarningsChange={setWarnings}
            onImageBase64Change={setImageBase64}
            onRampsChange={setColorRamps}
            onSegmentedPaletteChange={setSegmentedPalette}
            onPaletteSummaryChange={setPaletteSummary}
            onSpacingResultChange={setSpacingResult}
            onDebugOverlayChange={setDebugOverlay}
          />
        </div>
        <div className="secondary-row">
          <TokenExplorer
            activeTab={activeTab}
            showDebug={showDebug}
            lighting={lightingAnalysis}
            onLightingAnalysis={setLightingAnalysis}
            imageBase64={imageBase64}
            ramps={colorRamps}
            segmentedPalette={segmentedPalette}
            paletteSummary={paletteSummary}
            spacingResult={spacingResult}
            debugOverlay={debugOverlay}
          />
        </div>
      </AppShell>
    </div>
  )
}

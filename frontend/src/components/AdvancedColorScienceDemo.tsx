import { useState, useCallback } from 'react'
import './AdvancedColorScienceDemo.css'
import {
  ColorToken,
  PipelineStage,
  SpacingToken,
  ColorDetailsPanel,
  ColorGrid,
  SpacingGrid,
  StatsPanel,
  PipelineVisualization,
  EducationPanel,
  UploadSection,
  ProjectControls,
  useColorConversion,
} from './color-science'

export default function AdvancedColorScienceDemo() {
  // State management
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [isExtracting, setIsExtracting] = useState(false)
  const [colors, setColors] = useState<ColorToken[]>([])
  const [selectedColorIndex, setSelectedColorIndex] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [paletteDescription, setPaletteDescription] = useState<string>('')
  const [extractorUsed, setExtractorUsed] = useState<string>('')
  const [expandedEducation, setExpandedEducation] = useState<string | null>('pipeline')
  const [projectId, setProjectId] = useState<number>(1)
  const [projectName, setProjectName] = useState<string>('Color Science Demo')
  const [loadProjectId, setLoadProjectId] = useState<string>('1')
  const [imageBase64, setImageBase64] = useState<string | null>(null)
  const [imageMediaType, setImageMediaType] = useState<string>('image/png')
  const [spacingTokens, setSpacingTokens] = useState<SpacingToken[]>([])
  const [spacingSummary, setSpacingSummary] = useState<string>('')
  const [stages, setStages] = useState<PipelineStage[]>([
    { id: 'preprocess', name: 'Preprocess', description: 'Validate, resize, enhance image', status: 'pending' },
    { id: 'extract', name: 'Extract', description: 'AI-powered color detection', status: 'pending' },
    { id: 'aggregate', name: 'Aggregate', description: 'Delta-E deduplication', status: 'pending' },
    { id: 'validate', name: 'Validate', description: 'WCAG accessibility checks', status: 'pending' },
    { id: 'generate', name: 'Generate', description: 'W3C Design Tokens output', status: 'pending' },
  ])

  const tokenTypes = ['color', 'spacing'] as const
  const { copyToClipboard } = useColorConversion()

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      const reader = new FileReader()
      reader.onload = (e) => {
        const dataUrl = e.target?.result as string
        setPreview(dataUrl)
        const [meta, payload] = (dataUrl || '').split(',', 2)
        if (payload) {
          setImageBase64(payload)
          const mtMatch = meta.match(/data:(.*);base64/)
          setImageMediaType(mtMatch?.[1] || 'image/png')
        }
      }
      reader.readAsDataURL(file)
      setError(null)
      resetStages()
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    const file = e.dataTransfer.files[0]
    if (file && file.type.startsWith('image/')) {
      setSelectedFile(file)
      const reader = new FileReader()
      reader.onload = (e) => {
        const dataUrl = e.target?.result as string
        setPreview(dataUrl)
        const [meta, payload] = (dataUrl || '').split(',', 2)
        if (payload) {
          setImageBase64(payload)
          const mtMatch = meta.match(/data:(.*);base64/)
          setImageMediaType(mtMatch?.[1] || 'image/png')
        }
      }
      reader.readAsDataURL(file)
      setError(null)
      resetStages()
    }
  }, [])

  const resetStages = () => {
    setStages(prev => prev.map(s => ({ ...s, status: 'pending', duration: undefined })))
  }

  const updateStage = (id: string, status: PipelineStage['status'], duration?: number) => {
    setStages(prev => prev.map(s =>
      s.id === id ? { ...s, status, duration } : s
    ))
  }

  const extractColors = async () => {
    if (!selectedFile || !preview) return

    setIsExtracting(true)
    setError(null)
    setColors([])
    setSelectedColorIndex(null)
    resetStages()

    try {
      // Ensure project exists
      let workingProjectId = projectId
      try {
        const projectRes = await fetch(`/api/v1/projects/${workingProjectId}/colors`)
        if (projectRes.status === 404) {
          const createRes = await fetch('/api/v1/projects', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: projectName || 'Color Science Demo', description: 'Advanced pipeline demo' })
          })
          if (createRes.ok) {
            const project = await createRes.json()
            workingProjectId = project.id
            setProjectId(project.id)
            setLoadProjectId(String(project.id))
          }
        }
      } catch {
        // Use default project
      }

      // Stage 1: Preprocess
      const preprocessStart = performance.now()
      updateStage('preprocess', 'running')
      await delay(300)
      updateStage('preprocess', 'done', performance.now() - preprocessStart)

      // Stage 2: Extract (SSE CV-first, AI-second)
      const extractStart = performance.now()
      updateStage('extract', 'running')

      const controller = new AbortController()
      const body = JSON.stringify({
        image_base64: preview,
        image_media_type: imageMediaType || 'image/png',
        project_id: workingProjectId,
        token_types: tokenTypes,
        max_colors: 12,
        max_spacing_tokens: 20,
      })

      const response = await fetch('/api/v1/extract/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body,
        signal: controller.signal,
      })

      if (!response.ok || !response.body) {
        throw new Error(`Extraction failed (status ${response.status})`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder('utf-8')
      let buffer = ''
      const applyTokens = (type: string, source: string, payload: any[], metadata?: Record<string, any>) => {
        if (type === 'color') {
          setColors((prev) => (source === 'ai' ? payload : prev.length ? prev : payload))
          if (payload.length > 0) setSelectedColorIndex(0)
        } else if (type === 'spacing') {
          setSpacingTokens((prev) => (source === 'ai' ? payload : prev.length ? prev : payload))
          if (payload.length > 0) {
            const uniq = payload.map((p) => p.value_px)
            const base = metadata?.base_unit ?? payload[0].base_unit ?? payload[0].value_px ?? 0
            const confidenceLabel =
              metadata?.base_unit_confidence != null
                ? ` · confidence ${Math.round(metadata.base_unit_confidence * 100)}%`
                : ''
            const valuesLabel = uniq.slice(0, 6).join(', ')
            setSpacingSummary(
              `${payload.length} spacing · base ${base}px${confidenceLabel}${
                valuesLabel ? ` · values ${valuesLabel}` : ''
              }`
            )
          }
        }
      }

      while (true) {
        const { value, done } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const events = buffer.split('\n\n')
        buffer = events.pop() || ''
        for (const evt of events) {
          const lines = evt.split('\n')
          const eventLine = lines.find((l) => l.startsWith('event:'))
          const dataLine = lines.find((l) => l.startsWith('data:'))
          if (!eventLine || !dataLine) continue
          const event = eventLine.replace('event:', '').trim()
          const data = JSON.parse(dataLine.replace('data:', '').trim() || '{}')
          // Verbose logging for debugging stream events
          console.log('SSE event', event, data)
          if (event === 'token') {
            const { type, source, tokens, metadata } = data
            if (type && tokens) applyTokens(type, source || 'cv', tokens, metadata)
          } else if (event === 'complete') {
            updateStage('extract', 'done', performance.now() - extractStart)
          } else if (event === 'error') {
            throw new Error(data.error || 'Extraction failed')
          }
        }
      }

      updateStage('extract', 'done', performance.now() - extractStart)

      // Stage 3: Aggregate
      const aggStart = performance.now()
      updateStage('aggregate', 'running')
      await delay(200)
      updateStage('aggregate', 'done', performance.now() - aggStart)

      // Stage 4: Validate
      const valStart = performance.now()
      updateStage('validate', 'running')
      await delay(200)
      updateStage('validate', 'done', performance.now() - valStart)

      // Stage 5: Generate
      const genStart = performance.now()
      updateStage('generate', 'running')
      await delay(150)
      updateStage('generate', 'done', performance.now() - genStart)

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
      const currentRunning = stages.find(s => s.status === 'running')
      if (currentRunning) {
        updateStage(currentRunning.id, 'error')
      }
    } finally {
      setIsExtracting(false)
    }
  }

  // Utility functions
  const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))
  const selectedColor = selectedColorIndex !== null ? colors[selectedColorIndex] : null

  // Handlers for child components
  const handleSaveProject = async () => {
    try {
      const res = await fetch('/api/v1/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: projectName || 'My Colors',
          description: 'Saved session',
          image_base64: imageBase64,
          image_media_type: imageMediaType,
          spacing_tokens: spacingTokens,
        }),
      })
      if (res.ok) {
        const proj = await res.json()
        setProjectId(proj.id)
        setLoadProjectId(String(proj.id))
        setError(null)
      } else {
        const err = await res.json()
        setError(err.detail || 'Failed to save project')
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to save project')
    }
  }

  const handleLoadProject = async () => {
    try {
      const pid = Number(loadProjectId || projectId)
      try {
        const projRes = await fetch(`/api/v1/projects/${pid}`)
        if (projRes.ok) {
          const proj = await projRes.json()
          if (proj.image_base64) {
            setImageBase64(proj.image_base64)
            setImageMediaType(proj.image_media_type || 'image/png')
            setPreview(`data:${proj.image_media_type || 'image/png'};base64,${proj.image_base64}`)
          }
          if (proj.spacing_tokens) {
            setSpacingTokens(proj.spacing_tokens)
            setSpacingSummary(proj.spacing_tokens.length ? `${proj.spacing_tokens.length} spacing tokens (loaded)` : '')
          }
          if (proj.name) setProjectName(proj.name)
        }
      } catch (_) {
        // ignore
      }
      const res = await fetch(`/api/v1/projects/${pid}/colors`)
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Load failed')
      }
      const data = await res.json()
      setColors(data || [])
      setPaletteDescription('')
      setProjectId(pid)
      setError(null)
      setSelectedColorIndex(data?.length ? 0 : null)
      try {
        const spacRes = await fetch(`/api/v1/spacing/projects/${pid}/spacing`)
        if (spacRes.ok) {
          const spac = await spacRes.json()
          setSpacingTokens(spac || [])
          setSpacingSummary(spac?.length ? `${spac.length} spacing tokens loaded` : spacingSummary)
        }
      } catch (_) {
        // ignore
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load project')
    }
  }

  const handleLoadSnapshot = async () => {
    try {
      const pid = Number(loadProjectId || projectId)
      const listRes = await fetch(`/api/v1/projects/${pid}/snapshots`)
      if (!listRes.ok) throw new Error('No snapshots found')
      const snaps = await listRes.json()
      if (!snaps.length) throw new Error('No snapshots available')
      const snapId = snaps[0].id
      const snapRes = await fetch(`/api/v1/projects/${pid}/snapshots/${snapId}`)
      if (!snapRes.ok) throw new Error('Failed to load snapshot')
      const snap = await snapRes.json()
      const data = snap.data || {}
      if (data.colors) setColors(data.colors)
      if (data.spacing) {
        setSpacingTokens(data.spacing)
        setSpacingSummary(data.spacing.length ? `${data.spacing.length} spacing (snapshot)` : '')
      }
      setProjectId(pid)
      setSelectedColorIndex(data.colors?.length ? 0 : null)
      setError(null)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load snapshot')
    }
  }

  return (
    <div className="advanced-color-science-demo">
      {/* Header */}
      <header className="demo-header">
        <h1>Advanced Color Science Demo</h1>
        <p>Full 5-stage pipeline visualization with color science education</p>
      </header>

      <div className="demo-layout">
        {/* Left Panel - Upload & Pipeline */}
        <aside className="left-panel">
          <UploadSection
            preview={preview}
            isExtracting={isExtracting}
            onFileChange={handleFileChange}
            onDrop={handleDrop}
            onExtract={() => void extractColors()}
            selectedFile={selectedFile}
          />
          <ProjectControls
            projectName={projectName}
            projectId={projectId}
            loadProjectId={loadProjectId}
            colors={colors}
            spacingTokens={spacingTokens}
            imageBase64={imageBase64}
            imageMediaType={imageMediaType}
            onProjectNameChange={setProjectName}
            onSaveProject={() => void handleSaveProject()}
            onLoadProjectIdChange={setLoadProjectId}
            onLoadProject={() => void handleLoadProject()}
            onLoadSnapshot={() => void handleLoadSnapshot()}
          />
          <PipelineVisualization stages={stages} />
          <EducationPanel
            expandedEducation={expandedEducation}
            onExpandTopic={setExpandedEducation}
            paletteDescription={paletteDescription}
          />
        </aside>

        {/* Center Panel - Results */}
        <main className="center-panel">
          {error && <div className="error-message">{error}</div>}

          {colors.length === 0 && !isExtracting && (
            <div className="empty-state">
              <p>Upload an image to extract and analyze colors</p>
            </div>
          )}

          {isExtracting && (
            <div className="loading-state">
              <div className="spinner" />
              <p>Processing through pipeline...</p>
            </div>
          )}

          {colors.length > 0 && (
            <>
              <StatsPanel colors={colors} extractorUsed={extractorUsed} paletteDescription={paletteDescription} />
              <ColorGrid
                colors={colors}
                selectedColorIndex={selectedColorIndex}
                onSelectColor={setSelectedColorIndex}
                onCopyHex={copyToClipboard}
              />
              <SpacingGrid spacingTokens={spacingTokens} spacingSummary={spacingSummary} />
            </>
          )}
        </main>

        {/* Right Panel - Selected Color Details */}
        <aside className="right-panel">
          <ColorDetailsPanel selectedColor={selectedColor} paletteDescription={paletteDescription} />
        </aside>
      </div>
    </div>
  )
}

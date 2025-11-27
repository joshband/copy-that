import { useState, useCallback } from 'react'
import './AdvancedColorScienceDemo.css'
import { formatSemanticValue } from '../utils/semanticNames'

interface ColorToken {
  id?: number
  hex: string
  rgb?: string
  hsl?: string
  hsv?: string
  name: string
  design_intent?: string
  semantic_names?: Record<string, unknown> | null
  confidence: number
  harmony?: string
  temperature?: string
  saturation_level?: string
  lightness_level?: string
  category?: string
  usage?: string | string[]
  wcag_contrast_on_white?: number
  wcag_contrast_on_black?: number
  wcag_aa_compliant_text?: boolean
  wcag_aaa_compliant_text?: boolean
  wcag_aa_compliant_normal?: boolean
  wcag_aaa_compliant_normal?: boolean
  colorblind_safe?: boolean
  tint_color?: string
  shade_color?: string
  tone_color?: string
  closest_web_safe?: string
  closest_css_named?: string
  is_neutral?: boolean
  provenance?: Record<string, number>
  extraction_metadata?: Record<string, unknown>
}

interface PipelineStage {
  id: string
  name: string
  description: string
  status: 'pending' | 'running' | 'done' | 'error'
  duration?: number
}

interface ExtractionResult {
  colors: ColorToken[]
  extractor_used: string
  color_palette?: string
}

interface SpacingToken {
  value_px: number
  value_rem: number
  name: string
  confidence: number
  semantic_role?: string
  spacing_type?: string
  role?: string
  grid_aligned?: boolean
  tailwind_class?: string
}

export default function AdvancedColorScienceDemo() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [isExtracting, setIsExtracting] = useState(false)
  const [colors, setColors] = useState<ColorToken[]>([])
  const [selectedColorIndex, setSelectedColorIndex] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)
  const tokenTypes = ['color', 'spacing'] as const
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
    { id: 'generate', name: 'Generate', description: 'W3C Design Tokens output', status: 'pending' }
  ])

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

  const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

  const selectedColor = selectedColorIndex !== null ? colors[selectedColorIndex] : null

  const copyToClipboard = (text: string) => {
    void navigator.clipboard.writeText(text)
  }

  const getVibrancy = (color: ColorToken | null) => {
    if (!color?.hsl) return 'balanced'
    const match = color.hsl.match(/hsl\\(([^,]+),\\s*([^%]+)%?,\\s*([^%]+)%?\\)/i)
    if (!match) return 'balanced'
    const saturation = parseFloat(match[2]) / 100
    const lightness = parseFloat(match[3]) / 100
    if (saturation >= 0.65 && lightness >= 0.45 && lightness <= 0.75) return 'vibrant'
    if (saturation <= 0.25) return 'muted'
    return 'balanced'
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
          {/* Upload Section */}
          <section className="panel-card upload-section">
            <h2>Upload Image</h2>
            <div
              className={`upload-area ${preview ? 'has-preview' : ''}`}
              onDrop={handleDrop}
              onDragOver={(e) => e.preventDefault()}
              onClick={() => document.getElementById('file-input')?.click()}
            >
              {preview ? (
                <img src={preview} alt="Preview" className="preview-image" />
              ) : (
                <>
                  <span className="upload-icon">+</span>
                  <p>Drop image or click to browse</p>
                </>
              )}
              <input
                id="file-input"
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                style={{ display: 'none' }}
              />
            </div>
            <button
              className="extract-btn"
              onClick={() => void extractColors()}
              disabled={isExtracting || !selectedFile}
            >
              {isExtracting ? 'Extracting...' : 'Extract Color Tokens'}
            </button>
          </section>

          {/* Project/Session */}
          <section className="panel-card">
            <h2>Project / Session</h2>
            <div className="project-controls">
              <label className="field">
                <span>Project Name</span>
                <input
                  type="text"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  placeholder="My Colors"
                />
              </label>
              <div className="project-actions">
                <button
                  className="small-btn"
                  onClick={() => {
                    void (async () => {
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
                          })
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
                    })()
                  }}
                  disabled={!colors.length && !spacingTokens.length}
                  title={!colors.length && !spacingTokens.length ? 'Extract tokens first' : undefined}
                >
                  Save Project
                </button>
                <div className="load-row">
                  <input
                    type="number"
                    value={loadProjectId}
                    onChange={(e) => setLoadProjectId(e.target.value)}
                    className="load-input"
                    placeholder="Project ID"
                  />
                  <button
                    className="small-btn"
                    onClick={() => {
                      void (async () => {
                        try {
                          const pid = Number(loadProjectId || projectId)
                          // Load project metadata first (for image)
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
                                setSpacingSummary(
                                  proj.spacing_tokens.length
                                    ? `${proj.spacing_tokens.length} spacing tokens (loaded)`
                                    : ''
                                )
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
                          setExtractorUsed(extractorUsed)
                          setProjectId(pid)
                          setError(null)
                          setSelectedColorIndex(data?.length ? 0 : null)

                          // Load spacing tokens from DB
                          try {
                            const spacRes = await fetch(`/api/v1/spacing/projects/${pid}/spacing`)
                            if (spacRes.ok) {
                              const spac = await spacRes.json()
                              setSpacingTokens(spac || [])
                              setSpacingSummary(
                                spac?.length
                                  ? `${spac.length} spacing tokens loaded`
                                  : spacingSummary
                              )
                            }
                          } catch (_) {
                            // ignore
                          }
                        } catch (e) {
                          setError(e instanceof Error ? e.message : 'Failed to load project')
                        }
                      })()
                    }}
                  >
                    Load Project
                  </button>
                </div>
                <div className="load-row">
                  <button
                    className="small-btn"
                    onClick={() => {
                      void (async () => {
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
                            setSpacingSummary(
                              data.spacing.length ? `${data.spacing.length} spacing (snapshot)` : ''
                            )
                          }
                          setProjectId(pid)
                          setSelectedColorIndex(data.colors?.length ? 0 : null)
                          setError(null)
                        } catch (e) {
                          setError(e instanceof Error ? e.message : 'Failed to load snapshot')
                        }
                      })()
                    }}
                    title="Load most recent snapshot"
                  >
                    Load Latest Snapshot
                  </button>
                </div>
                <div className="project-meta">Current Project ID: {projectId}</div>
              </div>
            </div>
          </section>

          {/* Pipeline Visualization */}
          <section className="panel-card pipeline-section">
            <h2>Pipeline Stages</h2>
            <div className="pipeline-stages">
              {stages.map((stage, index) => (
                <div key={stage.id} className={`pipeline-stage ${stage.status}`}>
                  <div className="stage-number">{index + 1}</div>
                  <div className="stage-info">
                    <div className="stage-name">{stage.name}</div>
                    <div className="stage-desc">{stage.description}</div>
                  </div>
                  <div className="stage-status">
                    {stage.status === 'pending' && 'Pending'}
                    {stage.status === 'running' && <span className="spinner-small" />}
                    {stage.status === 'done' && (
                      <span className="done-check">
                        {stage.duration ? `${stage.duration.toFixed(0)}ms` : 'Done'}
                      </span>
                    )}
                    {stage.status === 'error' && 'Error'}
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Education Panel */}
          <section className="panel-card education-section">
            <h2>Color Science Education</h2>

            {/* Pipeline Education */}
            <div className="edu-topic">
              <button
                className="edu-header"
                onClick={() => setExpandedEducation(expandedEducation === 'pipeline' ? null : 'pipeline')}
              >
                <span>Algorithm Pipeline</span>
                <span className="expand-icon">{expandedEducation === 'pipeline' ? '-' : '+'}</span>
              </button>
              {expandedEducation === 'pipeline' && (
                <div className="edu-content">
                  <p><strong>Preprocess:</strong> SSRF protection, image validation, resize to 1920x1080, CLAHE enhancement</p>
                  <p><strong>Extract:</strong> Claude Sonnet 4.5 with Tool Use API for structured extraction</p>
                  <p><strong>Aggregate:</strong> Delta-E 2000 deduplication (JND = 2.0), provenance tracking</p>
                  <p><strong>Validate:</strong> WCAG contrast ratios, colorblind safety, quality scoring</p>
                  <p><strong>Generate:</strong> W3C Design Tokens, CSS, React, Tailwind output</p>
                </div>
              )}
            </div>

            {/* Delta-E Education */}
            <div className="edu-topic">
              <button
                className="edu-header"
                onClick={() => setExpandedEducation(expandedEducation === 'deltae' ? null : 'deltae')}
              >
                <span>Delta-E (CIEDE2000)</span>
                <span className="expand-icon">{expandedEducation === 'deltae' ? '-' : '+'}</span>
              </button>
              {expandedEducation === 'deltae' && (
                <div className="edu-content">
                  <p>Perceptual color difference metric based on human vision.</p>
                  <ul>
                    <li><strong>0-1:</strong> Not perceptible by human eyes</li>
                    <li><strong>1-2:</strong> Perceptible through close observation</li>
                    <li><strong>2-10:</strong> Perceptible at a glance</li>
                    <li><strong>11-49:</strong> More similar than opposite</li>
                    <li><strong>100:</strong> Exact opposite colors</li>
                  </ul>
                  <p className="highlight">JND threshold: 2.0 (Just Noticeable Difference)</p>
                </div>
              )}
            </div>

            {/* WCAG Education */}
            <div className="edu-topic">
              <button
                className="edu-header"
                onClick={() => setExpandedEducation(expandedEducation === 'wcag' ? null : 'wcag')}
              >
                <span>WCAG Accessibility</span>
                <span className="expand-icon">{expandedEducation === 'wcag' ? '-' : '+'}</span>
              </button>
              {expandedEducation === 'wcag' && (
                <div className="edu-content">
                  <p><strong>Level AA (Minimum):</strong></p>
                  <ul>
                    <li>Normal text: 4.5:1 ratio</li>
                    <li>Large text (18pt+): 3:1 ratio</li>
                  </ul>
                  <p><strong>Level AAA (Enhanced):</strong></p>
                  <ul>
                    <li>Normal text: 7:1 ratio</li>
                    <li>Large text: 4.5:1 ratio</li>
                  </ul>
                  <p className="highlight">Formula: (L1 + 0.05) / (L2 + 0.05)</p>
                </div>
              )}
            </div>

            {/* Color Spaces Education */}
            <div className="edu-topic">
              <button
                className="edu-header"
                onClick={() => setExpandedEducation(expandedEducation === 'spaces' ? null : 'spaces')}
              >
                <span>Color Spaces</span>
                <span className="expand-icon">{expandedEducation === 'spaces' ? '-' : '+'}</span>
              </button>
              {expandedEducation === 'spaces' && (
                <div className="edu-content">
                  <p><strong>RGB:</strong> Additive color for displays (Red, Green, Blue)</p>
                  <p><strong>HSL:</strong> Human-readable (Hue, Saturation, Lightness)</p>
                  <p><strong>HSV:</strong> Design-friendly (Hue, Saturation, Value)</p>
                  <p><strong>LAB:</strong> Perceptually uniform (Lightness, A, B)</p>
                  <p><strong>Oklch:</strong> Modern perceptual space for CSS</p>
                </div>
              )}
            </div>

            {/* Semantic Naming */}
            <div className="edu-topic">
              <button
                className="edu-header"
                onClick={() => setExpandedEducation(expandedEducation === 'semantic' ? null : 'semantic')}
              >
                <span>Semantic Naming</span>
                <span className="expand-icon">{expandedEducation === 'semantic' ? '-' : '+'}</span>
              </button>
              {expandedEducation === 'semantic' && (
                <div className="edu-content">
                  <p>5-dimension naming system:</p>
                  <ul>
                    <li><strong>Simple:</strong> red, blue, green</li>
                    <li><strong>Descriptive:</strong> warm red, ocean blue</li>
                    <li><strong>Emotional:</strong> passionate, calm, energetic</li>
                    <li><strong>Technical:</strong> #FF5733, rgb(255, 87, 51)</li>
                    <li><strong>Vibrancy:</strong> vivid, muted, desaturated, balanced</li>
                  </ul>
                  {paletteDescription && (
                    <p className="highlight">Palette Story: {paletteDescription}</p>
                  )}
                </div>
              )}
            </div>

            {/* Narrative */}
            <div className="edu-topic">
              <button
                className="edu-header"
                onClick={() => setExpandedEducation(expandedEducation === 'narrative' ? null : 'narrative')}
              >
                <span>Palette Narrative</span>
                <span className="expand-icon">{expandedEducation === 'narrative' ? '-' : '+'}</span>
              </button>
              {expandedEducation === 'narrative' && (
                <div className="edu-content">
                  <p>
                    This palette blends technical rigor with creative tone. Use dominant hues for backgrounds,
                    pair high-confidence accents for calls-to-action, and reserve muted tones for surfaces and dividers.
                  </p>
                  <p>
                    Accessibility: prioritize the highest contrast pairings for primary text, and validate secondary accents
                    against both light and dark surfaces.
                  </p>
                </div>
              )}
            </div>
          </section>
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
              {/* Stats */}
              <section className="panel-card stats-section">
                <div className="stats-grid">
                  <div className="stat-item">
                    <div className="stat-value">{colors.length}</div>
                    <div className="stat-label">Colors</div>
                  </div>
                  <div className="stat-item">
                    <div className="stat-value">
                      {(colors.reduce((a, c) => a + c.confidence, 0) / colors.length * 100).toFixed(0)}%
                    </div>
                    <div className="stat-label">Avg Confidence</div>
                  </div>
                  <div className="stat-item">
                    <div className="stat-value">
                      {colors.filter(c => c.wcag_aa_compliant_text).length}
                    </div>
                    <div className="stat-label">WCAG AA</div>
                  </div>
                  <div className="stat-item">
                    <div className="stat-value">{extractorUsed}</div>
                    <div className="stat-label">Extractor</div>
                  </div>
                </div>
                {paletteDescription && (
                  <p className="palette-description">{paletteDescription}</p>
                )}
              </section>

              {/* Color Grid */}
              <section className="panel-card colors-section">
                <h2>Extracted Colors</h2>
                <div className="colors-grid">
                  {colors.map((color, index) => (
                    <div
                      key={index}
                      className={`color-card ${selectedColorIndex === index ? 'selected' : ''}`}
                      onClick={() => setSelectedColorIndex(index)}
                    >
                      <div
                        className="color-swatch"
                        style={{ backgroundColor: color.hex }}
                        onClick={(e) => {
                          e.stopPropagation()
                          copyToClipboard(color.hex)
                        }}
                        title={`Click to copy ${color.hex}`}
                      />
                      <div className="color-info">
                        <div className="color-name">{color.name}</div>
                        <div className="color-hex mono">{color.hex}</div>
                        <div className="color-tags">
                          <span className="tag confidence">{Math.round(color.confidence * 100)}%</span>
                          {color.harmony && <span className="tag harmony">{color.harmony}</span>}
                          {color.temperature && <span className="tag temp">{color.temperature}</span>}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </section>

              {spacingTokens.length > 0 && (
                <section className="panel-card colors-section">
                  <h2>Extracted Spacing Tokens</h2>
                  <p className="palette-description">{spacingSummary}</p>
                  <div className="colors-grid">
                    {spacingTokens.map((t, idx) => (
                      <div key={idx} className="color-card">
                        <div className="color-info">
                          <div className="color-name">{t.name}</div>
                          <div className="color-hex mono">
                            {t.value_px}px ({t.value_rem}rem)
                          </div>
                          <div className="color-tags">
                            <span className="tag confidence">{Math.round(t.confidence * 100)}%</span>
                            {t.semantic_role && <span className="tag temp">{t.semantic_role}</span>}
                            {t.grid_aligned != null && (
                              <span className="tag {t.grid_aligned ? 'wcag-pass' : 'temp'}">
                                {t.grid_aligned ? 'Grid' : 'Off-grid'}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </section>
              )}
            </>
          )}
        </main>

        {/* Right Panel - Selected Color Details */}
        <aside className="right-panel">
          {selectedColor ? (
            <section className="panel-card details-section">
              <h2>Color Analysis</h2>

              {/* Main Swatch */}
              <div
                className="detail-swatch"
                style={{ backgroundColor: selectedColor.hex }}
              />

              <h3 className="detail-name">{selectedColor.name}</h3>
              <div className="detail-confidence">
                Confidence: {(selectedColor.confidence * 100).toFixed(1)}%
              </div>
              <div className="detail-confidence">
                Vibrancy: {getVibrancy(selectedColor)}
              </div>

              {/* Color Values */}
              <div className="detail-group">
                <h4>Color Values</h4>
                <div className="value-grid">
                  <div className="value-item">
                    <span className="value-label">HEX</span>
                    <span className="value-data mono">{selectedColor.hex}</span>
                  </div>
                  {selectedColor.rgb && (
                    <div className="value-item">
                      <span className="value-label">RGB</span>
                      <span className="value-data mono">{selectedColor.rgb}</span>
                    </div>
                  )}
                  {selectedColor.hsl && (
                    <div className="value-item">
                      <span className="value-label">HSL</span>
                      <span className="value-data mono">{selectedColor.hsl}</span>
                    </div>
                  )}
                  {selectedColor.hsv && (
                    <div className="value-item">
                      <span className="value-label">HSV</span>
                      <span className="value-data mono">{selectedColor.hsv}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Properties */}
              <div className="detail-group">
                <h4>Properties</h4>
                <div className="props-grid">
                  {selectedColor.temperature && (
                    <div className="prop-item">
                      <span className="prop-label">Temperature</span>
                      <span className="prop-value">{selectedColor.temperature}</span>
                    </div>
                  )}
                  {selectedColor.saturation_level && (
                    <div className="prop-item">
                      <span className="prop-label">Saturation</span>
                      <span className="prop-value">{selectedColor.saturation_level}</span>
                    </div>
                  )}
                  {selectedColor.lightness_level && (
                    <div className="prop-item">
                      <span className="prop-label">Lightness</span>
                      <span className="prop-value">{selectedColor.lightness_level}</span>
                    </div>
                  )}
                  {selectedColor.harmony && (
                    <div className="prop-item">
                      <span className="prop-label">Harmony</span>
                      <span className="prop-value">{selectedColor.harmony}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* WCAG Accessibility */}
              <div className="detail-group">
                <h4>WCAG Accessibility</h4>
                <div className="wcag-details">
                  {selectedColor.wcag_contrast_on_white != null && (
                    <div className="wcag-row">
                      <span className="wcag-label">On White</span>
                      <span className={`wcag-ratio ${selectedColor.wcag_contrast_on_white >= 4.5 ? 'pass' : 'fail'}`}>
                        {selectedColor.wcag_contrast_on_white.toFixed(2)}:1
                      </span>
                      <div className="wcag-badges">
                        <span className={`badge ${selectedColor.wcag_aa_compliant_text ? 'pass' : 'fail'}`}>
                          AA {selectedColor.wcag_aa_compliant_text ? 'Pass' : 'Fail'}
                        </span>
                        <span className={`badge ${selectedColor.wcag_aaa_compliant_text ? 'pass' : 'fail'}`}>
                          AAA {selectedColor.wcag_aaa_compliant_text ? 'Pass' : 'Fail'}
                        </span>
                      </div>
                    </div>
                  )}
                  {selectedColor.wcag_contrast_on_black != null && (
                    <div className="wcag-row">
                      <span className="wcag-label">On Black</span>
                      <span className={`wcag-ratio ${selectedColor.wcag_contrast_on_black >= 4.5 ? 'pass' : 'fail'}`}>
                        {selectedColor.wcag_contrast_on_black.toFixed(2)}:1
                      </span>
                    </div>
                  )}
                  {selectedColor.colorblind_safe && (
                    <div className="colorblind-safe">Colorblind Safe</div>
                  )}
                </div>
              </div>

              {/* Color Variants */}
              {(selectedColor.tint_color || selectedColor.shade_color || selectedColor.tone_color) && (
                <div className="detail-group">
                  <h4>Color Variants</h4>
                  <div className="variants-row">
                    {selectedColor.tint_color && (
                      <div className="variant-item">
                        <div
                          className="variant-swatch"
                          style={{ backgroundColor: selectedColor.tint_color }}
                        />
                        <span className="variant-label">Tint</span>
                      </div>
                    )}
                    <div className="variant-item">
                      <div
                        className="variant-swatch"
                        style={{ backgroundColor: selectedColor.hex }}
                      />
                      <span className="variant-label">Base</span>
                    </div>
                    {selectedColor.shade_color && (
                      <div className="variant-item">
                        <div
                          className="variant-swatch"
                          style={{ backgroundColor: selectedColor.shade_color }}
                        />
                        <span className="variant-label">Shade</span>
                      </div>
                    )}
                    {selectedColor.tone_color && (
                      <div className="variant-item">
                        <div
                          className="variant-swatch"
                          style={{ backgroundColor: selectedColor.tone_color }}
                        />
                        <span className="variant-label">Tone</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Semantic Names */}
              {(() => {
                const entries =
                  typeof selectedColor.semantic_names === 'string'
                    ? [['label', selectedColor.semantic_names] as const]
                    : selectedColor.semantic_names
                      ? Object.entries(selectedColor.semantic_names)
                      : []

                return entries.length > 0 ? (
                  <div className="detail-group">
                    <h4>Semantic Names</h4>
                    <div className="semantic-list">
                      {entries.map(([type, name]) => {
                        const formatted = formatSemanticValue(name)
                        return (
                          <div key={type} className="semantic-item">
                            <span className="semantic-type">{type}</span>
                            <span className="semantic-name">{formatted}</span>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                ) : null
              })()}

              {/* Design Intent */}
              {selectedColor.design_intent && (
                <div className="detail-group">
                  <h4>Design Intent</h4>
                  <p className="design-intent">{selectedColor.design_intent}</p>
                </div>
              )}

              {/* Web Safe & CSS Named */}
              {(selectedColor.closest_web_safe || selectedColor.closest_css_named) && (
                <div className="detail-group">
                  <h4>Web Integration</h4>
                  <div className="web-info">
                    {selectedColor.closest_web_safe && (
                      <div className="web-item">
                        <span className="web-label">Web Safe</span>
                        <span className="web-value">{selectedColor.closest_web_safe}</span>
                      </div>
                    )}
                    {selectedColor.closest_css_named && (
                      <div className="web-item">
                        <span className="web-label">CSS Named</span>
                        <span className="web-value">{selectedColor.closest_css_named}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Narrative */}
              <div className="detail-group">
                <h4>Story</h4>
                <p className="design-intent">
                  {selectedColor.temperature && `${selectedColor.temperature} `}tone with {getVibrancy(selectedColor)} vibrancy.
                  Use as a {selectedColor.role ?? 'primary'} accent; pair with high-contrast neutrals for text and balance with a complementary hue for CTAs.
                  {paletteDescription && ` Palette note: ${paletteDescription}`}
                </p>
              </div>

              {/* Provenance */}
              {selectedColor.provenance && Object.keys(selectedColor.provenance).length > 0 && (
                <div className="detail-group">
                  <h4>Provenance</h4>
                  <div className="provenance-list">
                    {Object.entries(selectedColor.provenance).map(([source, conf]) => (
                      <div key={source} className="provenance-item">
                        <span className="prov-source">{source}</span>
                        <span className="prov-confidence">{(Number(conf) * 100).toFixed(0)}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </section>
          ) : (
            <section className="panel-card details-section empty">
              <p>Select a color to see detailed analysis</p>
            </section>
          )}
        </aside>
      </div>
    </div>
  )
}

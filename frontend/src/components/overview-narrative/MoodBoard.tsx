import { useEffect, useRef, useState } from 'react'
import type { ColorToken } from '../../types'
import {
  fetchMoodBoardHealth,
  generateMoodBoard,
  MoodBoardUnavailableError,
  MOOD_BOARD_POLL_MAX_WAIT_MS,
  type MoodBoardHealth,
  type MoodBoardImageSlot,
} from '../../api/moodBoard'
import { JobPollTimeoutError, type JobStatusResponse } from '../../api/jobs'
import type { GeneratedImage, MoodBoardVariant } from './moodBoardTypes'

interface MoodBoardProps {
  sourceIdentity?: string
  colors: ColorToken[]
  /** Session upload preview — shown as the middle board slot (display-only). */
  sourceImageBase64?: string | null
}

/** Default AI slots: Materials → UI elements → (source in UI) → Typography & grid. */
export const DEFAULT_IMAGE_SLOTS: MoodBoardImageSlot[] = [
  { focus_type: 'material' },
  { focus_type: 'ui' },
  { focus_type: 'typography' },
]

/**
 * Cost / latency hint — cloud defaults; local LM Studio + mflux are free aside from compute.
 * Themes-only is the default path; imagery is opt-in (2 boards × 3 AI images).
 * See docs/features/MOOD_BOARD_SPECIFICATION.md.
 */
export const MOOD_BOARD_COST_HINT =
  'Themes take seconds to minutes. Optional imagery takes longer and may incur provider charges. A token collage is labelled when generated imagery is unavailable.'

type RoutingPolicy = 'balanced' | 'fast' | 'cheap' | 'private' | 'quality'

function readCachedVariants(key: string): MoodBoardVariant[] | null {
  try {
    const raw = localStorage.getItem(key)
    const value = raw ? JSON.parse(raw) : null
    return Array.isArray(value) ? value : null
  } catch { return null }
}

type Stage = 'idle' | 'queueing' | 'generating' | 'rendering' | 'complete' | 'error'

function stageFromJob(job: JobStatusResponse, includeImages: boolean): Stage {
  if (job.status === 'failed') return 'error'
  if (job.status === 'completed') return 'complete'
  const msg = (job.message || '').toLowerCase()
  if (includeImages && (msg.includes('render') || msg.includes('image') || job.progress >= 0.45)) {
    return 'rendering'
  }
  if (
    msg.includes('generat') ||
    msg.includes('theme') ||
    msg.includes('enqueued') ||
    job.progress >= 0.15
  ) {
    return 'generating'
  }
  return 'queueing'
}

function humanizeJobMessage(
  message: string | null | undefined,
  stage: Stage,
  includeImages: boolean
): string {
  const msg = (message || '').toLowerCase()
  if (includeImages && (msg.includes('render') || msg.includes('image'))) {
    return 'Creating imagery; a labelled collage may be used if imagery is unavailable…'
  }
  if (msg.includes('theme') || msg.includes('generat')) {
    return 'Generating theme prompts…'
  }
  if (msg.includes('enqueued') || msg.includes('queued') || msg.includes('worker')) {
    return 'Waiting for generation to start…'
  }
  if (stage === 'rendering') {
    return 'Rendering imagery (local image gen can take 5+ minutes per image)…'
  }
  if (stage === 'generating') {
    return includeImages ? 'Generating theme prompts…' : 'Generating themes (no imagery)…'
  }
  if (stage === 'queueing') {
    return 'Queueing mood board job…'
  }
  return 'Working…'
}

function formatElapsed(ms: number): string {
  const totalSec = Math.floor(ms / 1000)
  const min = Math.floor(totalSec / 60)
  const sec = totalSec % 60
  if (min <= 0) return `${sec}s`
  return `${min}m ${sec.toString().padStart(2, '0')}s`
}

function mapSaturation(level: string | undefined): string | undefined {
  if (!level) return undefined
  const normalized = level.toLowerCase()
  if (normalized === 'high' || normalized === 'vibrant' || normalized === 'vivid') return 'vibrant'
  if (normalized === 'muted') return 'muted'
  if (normalized === 'desaturated' || normalized === 'low') return 'desaturated'
  if (normalized === 'grayscale' || normalized === 'grey' || normalized === 'gray') return 'grayscale'
  return undefined
}

function providerHint(health: MoodBoardHealth | null): string | null {
  if (!health) return null
  const text = health.text_configured
    ? `${health.text_provider ?? 'text'}${health.text_model ? ` · ${health.text_model}` : ''}`
    : 'themes provider not configured'
  const backends = health.backends ?? []
  const available = backends.filter((b) => b.available).map((b) => b.id)
  const onlyCollage =
    available.length > 0 && available.every((id) => id === 'token_collage')
  const onlyLocal =
    available.length > 0 &&
    available.every((id) => id === 'token_collage' || id === 'local_mflux') &&
    available.includes('local_mflux')
  let images: string
  if (available.length === 0) {
    images = 'no image backends'
  } else if (onlyCollage) {
    images = 'collage only (no cloud/local gen)'
  } else if (onlyLocal) {
    images = `local mflux (slow) · policy ${health.recommended_policy ?? 'private'}`
  } else {
    images = `${available.join(', ')} · policy ${health.default_policy ?? health.recommended_policy ?? 'balanced'}`
  }
  return `Providers: ${text} · ${images}`
}

function sourcePreviewSrc(sourceImageBase64: string | null | undefined): string | null {
  if (!sourceImageBase64) return null
  if (sourceImageBase64.startsWith('data:')) return sourceImageBase64
  return `data:image/png;base64,${sourceImageBase64}`
}

export function MoodBoard({ colors, sourceIdentity = "", sourceImageBase64 = null }: MoodBoardProps) {
  const [moodBoards, setMoodBoards] = useState<MoodBoardVariant[] | null>(null)
  const [modelsUsed, setModelsUsed] = useState<Record<string, string> | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  /** Themes-only focus; ignored when imagery uses mixed composition. */
  const [themesFocus, setThemesFocus] = useState<'material' | 'typography'>('material')
  /** Themes-first default — imagery is an explicit cost/latency choice. */
  const [includeImages, setIncludeImages] = useState(false)
  const [policy, setPolicy] = useState<RoutingPolicy>('balanced')
  const [stage, setStage] = useState<Stage>('idle')
  const [jobMessage, setJobMessage] = useState<string | null>(null)
  const [jobProgress, setJobProgress] = useState(0)
  const [elapsedMs, setElapsedMs] = useState(0)
  const [retryToken, setRetryToken] = useState(0)
  /** Explicit user opt-in — never auto-generate on mount. */
  const [optedIn, setOptedIn] = useState(false)
  const [health, setHealth] = useState<MoodBoardHealth | null>(null)
  const abortRef = useRef<AbortController | null>(null)
  const startedAtRef = useRef<number | null>(null)

  const [submitted, setSubmitted] = useState<{ includeImages: boolean; themesFocus: 'material' | 'typography'; policy: RoutingPolicy } | null>(null)
  const inputIdentity = JSON.stringify([sourceIdentity || sourceImageBase64, colors])
  const submit = () => {
    setSubmitted({ includeImages, themesFocus, policy })
    setOptedIn(true)
    setRetryToken(v => v + 1)
  }
  useEffect(() => {
    abortRef.current?.abort()
    setSubmitted(null)
    setOptedIn(false)
    setMoodBoards(null)
    setLoading(false)
    setStage('idle')
    setError(null)
  }, [inputIdentity])

  useEffect(() => {
    const controller = new AbortController()
    void fetchMoodBoardHealth(controller.signal)
      .then((h) => {
        if (!controller.signal.aborted) {
          setHealth(h)
          const rec = h.recommended_policy
          if (
            rec === 'balanced' ||
            rec === 'fast' ||
            rec === 'cheap' ||
            rec === 'private' ||
            rec === 'quality'
          ) {
            setPolicy(rec)
          }
        }
      })
      .catch(() => {
        if (!controller.signal.aborted) setHealth(null)
      })
    return () => controller.abort()
  }, [])

  useEffect(() => {
    if (!submitted || colors.length === 0) return
    const { includeImages, themesFocus, policy } = submitted
    const key = `moodboard::v2::${JSON.stringify([inputIdentity, submitted, DEFAULT_IMAGE_SLOTS])}`

    const cached = readCachedVariants(key)
    if (cached && cached.length > 0) {
      setMoodBoards(cached)
      setStage('complete')
      setError(null)
      setLoading(false)
      setJobMessage(null)
      setJobProgress(1)
      return
    }

    const controller = new AbortController()
    abortRef.current = controller
    startedAtRef.current = Date.now()
    setElapsedMs(0)

    const elapsedTimer = window.setInterval(() => {
      if (startedAtRef.current != null) {
        setElapsedMs(Date.now() - startedAtRef.current)
      }
    }, 1000)

    const run = async () => {
      setLoading(true)
      setError(null)
      setStage('queueing')
      setJobMessage('enqueued')
      setJobProgress(0)
      setModelsUsed(null)

      try {
        const colorInput = colors.slice(0, 20).map((c) => ({
          hex: c.hex,
          name: c.name,
          temperature: c.temperature,
          saturation_level: mapSaturation(c.saturation_level),
          lightness_level: c.lightness_level,
          hue_family: c.hue_family,
          design_intent: c.design_intent,
          usage: c.usage,
          background_role: c.background_role,
          is_accent: c.is_accent,
          prominence_percentage: c.prominence_percentage,
        }))

        const result = await generateMoodBoard(
          includeImages
            ? {
                colors: colorInput,
                num_variants: 2,
                include_images: true,
                num_images_per_variant: DEFAULT_IMAGE_SLOTS.length,
                focus_type: 'mixed',
                image_slots: DEFAULT_IMAGE_SLOTS,
                policy,
                allow_cloud: policy !== 'private',
                source_image_base64: sourceImageBase64,
              }
            : {
                colors: colorInput,
                num_variants: 2,
                include_images: false,
                num_images_per_variant: 1,
                source_image_base64: sourceImageBase64,
                focus_type: themesFocus,
                policy,
                allow_cloud: policy !== 'private',
              },
          {
            signal: controller.signal,
            intervalMs: 1500,
            maxWaitMs: includeImages ? MOOD_BOARD_POLL_MAX_WAIT_MS : 10 * 60 * 1000,
            onUpdate: (job) => {
              if (!controller.signal.aborted) {
                setStage(stageFromJob(job, includeImages))
                setJobMessage(job.message ?? null)
                setJobProgress(typeof job.progress === 'number' ? job.progress : 0)
              }
            },
          }
        )

        if (controller.signal.aborted) return
        setMoodBoards(result.variants)
        setModelsUsed(result.models_used ?? null)
        setStage('complete')
        setJobProgress(1)
        setJobMessage('completed')
        try {
          localStorage.setItem(
            key,
            JSON.stringify(result.variants)
          )
        } catch {
          // ignore storage errors
        }
      } catch (err) {
        if (controller.signal.aborted) return
        if (err instanceof DOMException && err.name === 'AbortError') return
        console.error('Error fetching mood boards:', err)
        const message =
          err instanceof JobPollTimeoutError
            ? err.message
            : err instanceof MoodBoardUnavailableError
              ? err.message
              : err instanceof Error
                ? err.message
                : 'Failed to load mood boards'
        setError(message)
        setStage('error')
      } finally {
        window.clearInterval(elapsedTimer)
        if (!controller.signal.aborted) setLoading(false)
        if (abortRef.current === controller) abortRef.current = null
      }
    }

    void run()
    return () => {
      controller.abort()
      window.clearInterval(elapsedTimer)
    }
  }, [inputIdentity, submitted, retryToken])

  const cancelGeneration = () => {
    abortRef.current?.abort()
    setLoading(false)
    setError('Stopped waiting. Server generation may continue.')
    setStage('error')
  }

  if (colors.length === 0) return null

  const hint = providerHint(health)
  const waitMinutes = includeImages
    ? Math.round(MOOD_BOARD_POLL_MAX_WAIT_MS / 60000)
    : 10
  const sourceSrc = sourcePreviewSrc(sourceImageBase64)

  return (
    <div className="mood-board-section" data-testid="mood-board-section">
      <header className="mood-board-section__header">
        <h3>Mood boards</h3>
        <p className="mood-board-section__lede">
          Generated inspiration, separate from extracted evidence. Your source stays labelled.
        </p>
      </header>

      <div
        className="mood-board-cost-banner warning-banner"
        role="status"
        data-testid="mood-board-cost-banner"
      >
        {MOOD_BOARD_COST_HINT}
        {hint && <details><summary>Generation service details</summary><span data-testid="mood-board-provider-hint">{hint}</span></details>}
      </div>

      {!optedIn ? (
        <div className="mood-board-opt-in" data-testid="mood-board-opt-in">
          <p className="mood-board-intro">
            Optional boards from your extracted palette. Nothing is generated until you confirm.
          </p>
          <div className="mood-board-opt-in__controls">
            <label className="mood-board-image-toggle">
              <input
                type="checkbox"
                checked={includeImages}
                onChange={(e) => setIncludeImages(e.target.checked)}
                data-testid="mood-board-include-images"
              />
              <span>Include imagery (2 boards × 3 AI images)</span>
            </label>
            {includeImages ? (
              <label className="mood-board-policy">
                <span>Generation preference</span>
                <select
                  value={policy}
                  onChange={(e) => setPolicy(e.target.value as RoutingPolicy)}
                  data-testid="mood-board-policy"
                >
                  <option value="balanced">Balanced</option>
                  <option value="fast">Fast</option>
                  <option value="cheap">Cheap</option>
                  <option value="quality">Quality</option>
                  <option value="private">Private (local/collage)</option>
                </select>
              </label>
            ) : null}
            <button
              type="button"
              className="mood-board-opt-in-button"
              data-testid="mood-board-opt-in-button"
              onClick={submit}
            >
              {includeImages ? 'Generate boards with imagery' : 'Generate themes'}
            </button>
          </div>
        </div>
      ) : (
        <>
          <div className="mood-board-toolbar">
            <button type="button" disabled={loading} onClick={submit}>Generate with these options</button>
            {!includeImages ? (
              <div className="mood-board-focus-selector">
                <label>Themes focus</label>
                <div className="focus-buttons" role="group" aria-label="Themes focus">
                  <button
                    type="button"
                    className={`focus-button ${themesFocus === 'material' ? 'active' : ''}`}
                    onClick={() => setThemesFocus('material')}
                    disabled={loading}
                  >
                    Material &amp; texture
                  </button>
                  <button
                    type="button"
                    className={`focus-button ${themesFocus === 'typography' ? 'active' : ''}`}
                    onClick={() => setThemesFocus('typography')}
                    disabled={loading}
                  >
                    Typography &amp; grid
                  </button>
                </div>
              </div>
            ) : (
              <p className="mood-board-composition-note" data-testid="mood-board-composition-note">
                Composition: Materials &amp; finishes → UI elements → Source → Typography &amp; grid
              </p>
            )}
            <label className="mood-board-image-toggle">
              <input
                type="checkbox"
                checked={includeImages}
                onChange={(e) => {
                  setIncludeImages(e.target.checked)
                }}
                disabled={loading}
                data-testid="mood-board-include-images"
              />
              <span>Include imagery</span>
            </label>
            {includeImages ? (
              <label className="mood-board-policy">
                <span>Generation preference</span>
                <select
                  value={policy}
                  onChange={(e) => {
                    setPolicy(e.target.value as RoutingPolicy)
                  }}
                  disabled={loading}
                  data-testid="mood-board-policy"
                >
                  <option value="balanced">Balanced</option>
                  <option value="fast">Fast</option>
                  <option value="cheap">Cheap</option>
                  <option value="quality">Quality</option>
                  <option value="private">Private</option>
                </select>
              </label>
            ) : null}
          </div>

          <p className="mood-board-intro">
            {includeImages
              ? 'A materials board, a UI-elements board, your source photo, then a typography board.'
              : themesFocus === 'material'
                ? 'Physical materials, textures, and tactile qualities that embody your palette.'
                : 'Typographic systems, grid structures, and graphic language inspired by your colors.'}
          </p>

          <ProgressStages stage={stage} includeImages={submitted?.includeImages ?? false} />

          {loading && (
            <div className="mood-board-loading" data-testid="mood-board-loading">
              <div className="mood-board-progress-track" aria-hidden>
                <div
                  className="mood-board-progress-fill"
                  style={{ width: `${Math.max(4, Math.round(jobProgress * 100))}%` }}
                />
              </div>
              <p data-testid="mood-board-progress-copy">
                {humanizeJobMessage(jobMessage, stage, includeImages)}
              </p>
              <p className="mood-board-progress-meta" data-testid="mood-board-progress-meta">
                Elapsed {formatElapsed(elapsedMs)}
                {jobProgress > 0 ? ` · ${Math.round(jobProgress * 100)}%` : ''}
                {' · '}
                waits up to {waitMinutes} min
                {includeImages ? ' for local image gen' : ' for themes'}
              </p>
              <button
                type="button"
                className="retry-button"
                data-testid="mood-board-cancel-button"
                onClick={cancelGeneration}
              >
                Stop waiting
              </button>
            </div>
          )}

          {error && (
            <div className="mood-board-error" data-testid="mood-board-error">
              <p>{error}</p>
              <p className="error-note">
                Generation is unavailable. You can retry, or continue inspecting and exporting your extracted tokens.
              </p>
              <button
                type="button"
                className="retry-button"
                data-testid="mood-board-retry-button"
                onClick={() => {
                  setStage('queueing')
                  setError(null)
                  setRetryToken((v) => v + 1)
                }}
              >
                Retry generation
              </button>
              {moodBoards && (
                <p className="error-note">Showing last saved boards below while we retry.</p>
              )}
            </div>
          )}

          {!loading && !error && (!moodBoards || moodBoards.length === 0) && (
            <div className="mood-board-empty" data-testid="mood-board-empty">
              <p>No boards yet.</p>
              <p className="error-note">Retry, or toggle imagery and generate again.</p>
            </div>
          )}

          {moodBoards && moodBoards.length > 0 && (
            <>
              {modelsUsed && Object.keys(modelsUsed).length > 0 && (
                <p className="mood-board-models" data-testid="mood-board-models">
                  Models:{' '}
                  {Object.entries(modelsUsed)
                    .map(([k, v]) => `${k.replace(/_/g, ' ')} · ${v}`)
                    .join(' · ')}
                </p>
              )}
              <div className="mood-board-variants" data-testid="mood-board-variants">
                {moodBoards.map((variant, index) => (
                  <MoodBoardVariantCard
                    key={variant.id}
                    variant={variant}
                    index={index}
                    sourceSrc={sourceSrc}
                    showComposition={includeImages}
                  />
                ))}
              </div>
            </>
          )}
        </>
      )}
    </div>
  )
}

interface ProgressProps {
  stage: Stage
  includeImages: boolean
}

function ProgressStages({ stage, includeImages }: ProgressProps) {
  const stages = includeImages
    ? ([
        { id: 'queueing', label: 'Queueing' },
        { id: 'generating', label: 'Themes' },
        { id: 'rendering', label: 'Imagery' },
        { id: 'complete', label: 'Done' },
      ] as const)
    : ([
        { id: 'queueing', label: 'Queueing' },
        { id: 'generating', label: 'Themes' },
        { id: 'complete', label: 'Done' },
      ] as const)

  return (
    <div className="mood-board-stages" aria-label="Generation progress">
      {stages.map((s) => {
        const isActive = stage === s.id
        const activeIndex = stages.findIndex((st) => st.id === stage)
        const currentIndex = stages.findIndex((st) => st.id === s.id)
        const isDone = activeIndex > currentIndex || stage === 'complete'
        return (
          <div key={s.id} className={`stage ${isDone ? 'done' : ''} ${isActive ? 'active' : ''}`}>
            <span className="stage-dot" />
            <span className="stage-label">{s.label}</span>
          </div>
        )
      })}
      {stage === 'error' && (
        <div className="stage error">
          <span className="stage-dot" />
          <span className="stage-label">Error</span>
        </div>
      )}
    </div>
  )
}

interface MoodBoardVariantProps {
  variant: MoodBoardVariant
  index: number
  sourceSrc: string | null
  showComposition: boolean
}

function pickAiImages(images: GeneratedImage[]): {
  material: GeneratedImage | null
  ui: GeneratedImage | null
  typography: GeneratedImage | null
} {
  const material =
    images.find((img) => (img.role || img.focus_type) === 'material') ?? null
  const ui = images.find((img) => (img.role || img.focus_type) === 'ui') ?? null
  const typography =
    images.find((img) => (img.role || img.focus_type) === 'typography') ?? null
  return { material, ui, typography }
}

function AiImageFigure({
  image,
  title,
  label,
}: {
  image: GeneratedImage
  title: string
  label: string
}) {
  return (
    <figure className="mood-board-image-figure" data-slot={label}>
      <div className="mood-board-image">
        <img src={image.url} alt={`${title} — ${label}`} loading="lazy" />
      </div>
      <figcaption className="mood-board-slot-label">{label}</figcaption>
      {(image.provider || image.selection?.provider) && (
        <figcaption className="mood-board-image-meta" data-testid="mood-board-image-selection">
          {String(image.selection?.provider || image.provider)}
          {image.selection?.fallback_from
            ? ` · fallback from ${String(image.selection.fallback_from)}`
            : ''}
          {image.selection?.policy ? ` · ${String(image.selection.policy)}` : ''}
        </figcaption>
      )}
    </figure>
  )
}

function MoodBoardVariantCard({
  variant,
  index,
  sourceSrc,
  showComposition,
}: MoodBoardVariantProps) {
  const images = variant.theme.generated_images ?? []
  const hasImages = images.length > 0
  const { material, ui, typography } = pickAiImages(images)

  return (
    <article className="mood-board-variant" data-testid="mood-board-variant">
      <div className="mood-board-header">
        <span className="mood-board-label">Board {index + 1}</span>
        <h4 className="mood-board-title">{variant.title}</h4>
        <p className="mood-board-subtitle">{variant.subtitle}</p>
        <span className="mood-board-vibe">{variant.vibe}</span>
      </div>

      <div className="mood-board-colors" aria-label="Dominant colors">
        {variant.dominant_colors.map((color, i) => (
          <div
            key={i}
            className="mood-board-color-swatch"
            style={{ backgroundColor: color }}
            title={color}
          />
        ))}
      </div>

      <div className="mood-board-tags">
        {variant.theme.tags.map((tag, i) => (
          <span key={i} className="mood-board-tag">
            {tag}
          </span>
        ))}
      </div>

      {showComposition ? (
        <div
          className="mood-board-visual-grid mood-board-visual-grid--composition"
          data-testid="mood-board-composition-grid"
        >
          {material ? (
            <AiImageFigure
              image={material}
              title={variant.title}
              label="Materials & finishes"
            />
          ) : (
            <figure className="mood-board-image-figure" data-slot="Materials & finishes">
              <div className="mood-board-image mood-board-image--empty" />
              <figcaption className="mood-board-slot-label">Materials &amp; finishes</figcaption>
            </figure>
          )}

          {ui ? (
            <AiImageFigure image={ui} title={variant.title} label="UI elements" />
          ) : (
            <figure className="mood-board-image-figure" data-slot="UI elements">
              <div className="mood-board-image mood-board-image--empty" />
              <figcaption className="mood-board-slot-label">UI elements</figcaption>
            </figure>
          )}

          <figure className="mood-board-image-figure" data-slot="Source" data-testid="mood-board-source-slot">
            <div className="mood-board-image mood-board-image--source">
              {sourceSrc ? (
                <img src={sourceSrc} alt="Source upload" loading="lazy" />
              ) : (
                <div className="mood-board-source-placeholder">Upload a source image</div>
              )}
            </div>
            <figcaption className="mood-board-slot-label">Source</figcaption>
          </figure>

          {typography ? (
            <AiImageFigure
              image={typography}
              title={variant.title}
              label="Typography & grid"
            />
          ) : (
            <figure className="mood-board-image-figure" data-slot="Typography & grid">
              <div className="mood-board-image mood-board-image--empty" />
              <figcaption className="mood-board-slot-label">Typography &amp; grid</figcaption>
            </figure>
          )}
        </div>
      ) : hasImages ? (
        <div className="mood-board-visual-grid">
          {images.map((image, i) => (
            <figure key={i} className="mood-board-image-figure">
              <div className="mood-board-image">
                <img src={image.url} alt={`${variant.title} inspiration ${i + 1}`} loading="lazy" />
              </div>
              {(image.provider || image.selection?.provider) && (
                <figcaption className="mood-board-image-meta" data-testid="mood-board-image-selection">
                  {String(image.selection?.provider || image.provider)}
                  {image.selection?.fallback_from
                    ? ` · fallback from ${String(image.selection.fallback_from)}`
                    : ''}
                  {image.selection?.policy ? ` · ${String(image.selection.policy)}` : ''}
                </figcaption>
              )}
            </figure>
          ))}
        </div>
      ) : (
        <p className="mood-board-themes-only" data-testid="mood-board-themes-only">
          Themes only — no imagery for this run.
        </p>
      )}

      <div className="mood-board-elements">
        <h5>Visual language</h5>
        <ul>
          {(variant.theme.visual_elements ?? []).slice(0, 4).map((element, i) => (
            <li key={i} className={`element-${element.prominence}`}>
              <strong>{element.type}:</strong> {element.description}
            </li>
          ))}
        </ul>
      </div>

      <div className="mood-board-references">
        <h5>References</h5>
        {(variant.theme.references ?? []).map((ref, i) => (
          <div key={i} className="mood-board-reference">
            <strong>{ref.movement}</strong>
            {ref.artist && <span className="reference-artist"> — {ref.artist}</span>}
            {ref.period && <span className="reference-period"> ({ref.period})</span>}
            <div className="reference-characteristics">
              {(ref.characteristics ?? []).slice(0, 3).map((char, j) => (
                <span key={j} className="characteristic-tag">
                  {char}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </article>
  )
}

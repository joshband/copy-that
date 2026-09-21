import { useEffect, useRef, useState } from 'react'
import type { ColorToken } from '../../types'
import {
  generateMoodBoard,
  MoodBoardUnavailableError,
  MOOD_BOARD_POLL_MAX_WAIT_MS,
} from '../../api/moodBoard'
import { JobPollTimeoutError, type JobStatusResponse } from '../../api/jobs'
import type { MoodBoardVariant } from './moodBoardTypes'

interface MoodBoardProps {
  colors: ColorToken[]
}

/**
 * Cost / latency hint — cloud defaults; local LM Studio + mflux are free aside from compute.
 * Local image gens routinely take several minutes per image (solo Celery + mflux).
 * See docs/features/MOOD_BOARD_SPECIFICATION.md.
 */
export const MOOD_BOARD_COST_HINT =
  '~$0.10–0.20 and ~30–60s per cloud run (Claude + DALL·E; 2 variants). Local LM Studio + mflux: no API fees, but expect ~5+ min per image.'

function readCachedVariants(focusType: string): MoodBoardVariant[] | null {
  const raw = localStorage.getItem(`moodboard::${focusType}`)
  if (!raw) return null
  try {
    return JSON.parse(raw) as MoodBoardVariant[]
  } catch {
    return null
  }
}

type Stage = 'idle' | 'queueing' | 'generating' | 'rendering' | 'complete' | 'error'

function stageFromJob(job: JobStatusResponse): Stage {
  if (job.status === 'failed') return 'error'
  if (job.status === 'completed') return 'complete'
  const msg = (job.message || '').toLowerCase()
  if (msg.includes('render') || msg.includes('image') || job.progress >= 0.45) return 'rendering'
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

function humanizeJobMessage(message: string | null | undefined, stage: Stage): string {
  const msg = (message || '').toLowerCase()
  if (msg.includes('render') || msg.includes('image')) {
    return 'Rendering imagery via local mflux (several minutes per image is normal)…'
  }
  if (msg.includes('theme') || msg.includes('generat')) {
    return 'Generating theme prompts via LM Studio…'
  }
  if (msg.includes('enqueued') || msg.includes('queued') || msg.includes('worker')) {
    return 'Job queued — waiting for the mood-board Celery worker…'
  }
  if (stage === 'rendering') {
    return 'Rendering imagery (local image gen can take 5+ minutes per image)…'
  }
  if (stage === 'generating') {
    return 'Generating theme prompts…'
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

export function MoodBoard({ colors }: MoodBoardProps) {
  const [moodBoards, setMoodBoards] = useState<MoodBoardVariant[] | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [focusType, setFocusType] = useState<'material' | 'typography'>('material')
  const [stage, setStage] = useState<Stage>('idle')
  const [jobMessage, setJobMessage] = useState<string | null>(null)
  const [jobProgress, setJobProgress] = useState(0)
  const [elapsedMs, setElapsedMs] = useState(0)
  const [retryToken, setRetryToken] = useState(0)
  /** Explicit user opt-in — never auto-generate on mount. */
  const [optedIn, setOptedIn] = useState(false)
  const abortRef = useRef<AbortController | null>(null)
  const startedAtRef = useRef<number | null>(null)

  useEffect(() => {
    if (!optedIn || colors.length === 0) return

    const cached = retryToken === 0 ? readCachedVariants(focusType) : null
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

      try {
        const colorInput = colors.slice(0, 10).map(c => ({
          hex: c.hex,
          name: c.name,
          temperature: c.temperature,
          saturation_level: mapSaturation(c.saturation_level),
          hue_family: c.hue_family,
        }))

        // 1 image/variant keeps local dogfood practical (~5+ min each). Cloud can raise later.
        const result = await generateMoodBoard(
          {
            colors: colorInput,
            num_variants: 2,
            include_images: true,
            num_images_per_variant: 1,
            focus_type: focusType,
          },
          {
            signal: controller.signal,
            intervalMs: 1500,
            maxWaitMs: MOOD_BOARD_POLL_MAX_WAIT_MS,
            onUpdate: job => {
              if (!controller.signal.aborted) {
                setStage(stageFromJob(job))
                setJobMessage(job.message ?? null)
                setJobProgress(typeof job.progress === 'number' ? job.progress : 0)
              }
            },
          }
        )

        if (controller.signal.aborted) return
        setMoodBoards(result.variants)
        setStage('complete')
        setJobProgress(1)
        setJobMessage('completed')
        try {
          localStorage.setItem(`moodboard::${focusType}`, JSON.stringify(result.variants))
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
  }, [colors, focusType, retryToken, optedIn])

  const cancelGeneration = () => {
    abortRef.current?.abort()
    setLoading(false)
    setError('Generation cancelled.')
    setStage('error')
  }

  if (colors.length === 0) return null

  return (
    <div className="mood-board-section" data-testid="mood-board-section">
      <h3>AI-Curated Mood Boards</h3>

      <div
        className="mood-board-cost-banner warning-banner"
        role="status"
        data-testid="mood-board-cost-banner"
      >
        Paid AI call: {MOOD_BOARD_COST_HINT}. Requires providers (or local LM Studio + mflux) and a
        running mood-board Celery worker. Generation stays off until you opt in.
      </div>

      {!optedIn ? (
        <div className="mood-board-opt-in" data-testid="mood-board-opt-in">
          <p className="mood-board-intro">
            Optional inspiration boards from your palette. Nothing is generated until you confirm.
          </p>
          <button
            type="button"
            className="mood-board-opt-in-button"
            data-testid="mood-board-opt-in-button"
            onClick={() => setOptedIn(true)}
          >
            Generate mood boards
          </button>
        </div>
      ) : (
        <>
          <div className="mood-board-focus-selector">
            <label>Board Focus:</label>
            <div className="focus-buttons">
              <button
                type="button"
                className={`focus-button ${focusType === 'material' ? 'active' : ''}`}
                onClick={() => setFocusType('material')}
                disabled={loading}
              >
                Material & Texture
              </button>
              <button
                type="button"
                className={`focus-button ${focusType === 'typography' ? 'active' : ''}`}
                onClick={() => setFocusType('typography')}
                disabled={loading}
              >
                Typography & Grid
              </button>
            </div>
          </div>

          <p className="mood-board-intro">
            {focusType === 'material'
              ? 'Explore physical materials, textures, and tactile qualities that embody your palette.'
              : 'Discover typographic systems, grid structures, and graphic language inspired by your colors.'}
          </p>

          <ProgressStages stage={stage} />

          {loading && (
            <div className="mood-board-loading" data-testid="mood-board-loading">
              <div className="loading-spinner"></div>
              <p data-testid="mood-board-progress-copy">
                {humanizeJobMessage(jobMessage, stage)}
              </p>
              <p className="mood-board-progress-meta" data-testid="mood-board-progress-meta">
                Elapsed {formatElapsed(elapsedMs)}
                {jobProgress > 0 ? ` · ${Math.round(jobProgress * 100)}%` : ''}
                {' · '}
                waits up to {Math.round(MOOD_BOARD_POLL_MAX_WAIT_MS / 60000)} min for local image
                gen
              </p>
              <button
                type="button"
                className="retry-button"
                data-testid="mood-board-cancel-button"
                onClick={cancelGeneration}
              >
                Cancel
              </button>
            </div>
          )}

          {error && (
            <div className="mood-board-error" data-testid="mood-board-error">
              <p>{error}</p>
              <p className="error-note">
                Needs Celery + mood-board worker (`make celery-mood-board`). Themes: ANTHROPIC_API_KEY
                or MOOD_BOARD_TEXT_*; images: OPENAI_API_KEY or MOOD_BOARD_IMAGE_* (optional — themes
                render without images). Local image gen often exceeds several minutes per image.
              </p>
              <button
                type="button"
                className="retry-button"
                data-testid="mood-board-retry-button"
                onClick={() => {
                  setStage('queueing')
                  setError(null)
                  setRetryToken(v => v + 1)
                }}
              >
                Retry generation
              </button>
              {moodBoards && (
                <p className="error-note">Showing last saved boards below while we retry.</p>
              )}
            </div>
          )}

          {moodBoards && moodBoards.length > 0 && (
            <div className="mood-board-variants" data-testid="mood-board-variants">
              {moodBoards.map((variant, index) => (
                <MoodBoardVariantCard key={variant.id} variant={variant} index={index} />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  )
}

interface ProgressProps {
  stage: Stage
}

function ProgressStages({ stage }: ProgressProps) {
  const stages = [
    { id: 'queueing', label: 'Queueing job' },
    { id: 'generating', label: 'Generating themes' },
    { id: 'rendering', label: 'Rendering imagery' },
    { id: 'complete', label: 'Complete' },
  ] as const

  return (
    <div className="mood-board-stages">
      {stages.map(s => {
        const isActive = stage === s.id
        const activeIndex = stages.findIndex(st => st.id === stage)
        const currentIndex = stages.findIndex(st => st.id === s.id)
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
}

function MoodBoardVariantCard({ variant, index }: MoodBoardVariantProps) {
  const images = variant.theme.generated_images ?? []
  const hasImages = images.length > 0

  return (
    <div className="mood-board-variant" data-testid="mood-board-variant">
      <div className="mood-board-header">
        <span className="mood-board-label">Board {index + 1}</span>
        <h4 className="mood-board-title">{variant.title}</h4>
        <p className="mood-board-subtitle">{variant.subtitle}</p>
        <span className="mood-board-vibe">Vibe: {variant.vibe}</span>
      </div>

      <div className="mood-board-colors">
        {variant.dominant_colors.map((color, i) => (
          <div key={i} className="mood-board-color-swatch" style={{ backgroundColor: color }} title={color} />
        ))}
      </div>

      <div className="mood-board-tags">
        {variant.theme.tags.map((tag, i) => (
          <span key={i} className="mood-board-tag">
            {tag}
          </span>
        ))}
      </div>

      {hasImages ? (
        <div className="mood-board-visual-grid">
          {images.map((image, i) => (
            <div key={i} className="mood-board-image">
              <img src={image.url} alt={`${variant.title} inspiration ${i + 1}`} loading="lazy" />
            </div>
          ))}
        </div>
      ) : (
        <p className="mood-board-themes-only" data-testid="mood-board-themes-only">
          Themes only — images unavailable for this run.
        </p>
      )}

      <div className="mood-board-elements">
        <h5>Visual Language</h5>
        <ul>
          {(variant.theme.visual_elements ?? []).slice(0, 4).map((element, i) => (
            <li key={i} className={`element-${element.prominence}`}>
              <strong>{element.type}:</strong> {element.description}
            </li>
          ))}
        </ul>
      </div>

      <div className="mood-board-references">
        <h5>Cultural References</h5>
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
    </div>
  )
}

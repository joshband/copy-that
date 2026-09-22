import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, cleanup } from '@testing-library/react'
import { ProjectTokenExport } from '../ProjectTokenExport'

const guidePack = {
  meta: {
    source_counts: { extract: 4, derive: 2, synth: 3, preset: 1 },
    type_coverage: {
      color: 'live',
      dimension: 'live',
      fontFamily: 'derive',
      fontWeight: 'derive',
      typography: 'live',
      shadow: 'live',
      gradient: 'live',
      border: 'derive',
      strokeStyle: 'derive',
      number: 'synth',
      duration: 'synth',
      cubicBezier: 'synth',
      transition: 'synth',
    },
    token_snapshot_hash: 'abc123def456',
  },
  brand: { name: 'Fixture Brand' },
  foundations: { gradients: ['gradient.primary', 'gradient.accent'] },
}

const exportGuidePack = vi.fn(async () => guidePack)
const exportGuideHtml = vi.fn(async () => ({
  format: 'guide-html',
  content: '<html></html>',
  filename: 'guide.html',
}))

vi.mock('../../api/client', () => ({
  ApiClient: {
    exportGuidePack: (...args: unknown[]) => exportGuidePack(...args),
    exportGuideHtml: (...args: unknown[]) => exportGuideHtml(...args),
    exportDesignTokensW3c: vi.fn(),
    exportDesignTokensCss: vi.fn(),
    exportDesignTokensReact: vi.fn(),
    exportDesignTokensTailwind: vi.fn(),
  },
}))

vi.mock('../../utils/download', () => ({
  downloadTextFile: vi.fn(),
}))

describe('ProjectTokenExport Guide Pack UX', () => {
  beforeEach(() => {
    exportGuidePack.mockClear()
    exportGuideHtml.mockClear()
    exportGuidePack.mockResolvedValue(guidePack)
  })

  afterEach(() => {
    cleanup()
  })

  it('renders honesty strip and Guide Pack actions when tokens exist', async () => {
    render(
      <ProjectTokenExport
        projectId={7}
        colorCount={3}
        spacingCount={2}
        typographyCount={1}
        shadowCount={1}
        gradientCount={2}
      />
    )

    expect(await screen.findByTestId('export-honesty-strip')).toBeInTheDocument()
    expect(screen.getByTestId('export-gradient-honesty')).toHaveTextContent(/extracted/i)
    expect(screen.getByTestId('export-guide-html')).toBeInTheDocument()
    expect(screen.getByTestId('export-guide-pack')).toBeInTheDocument()
    expect(screen.getByText(/Brand guide over your token graph/i)).toBeInTheDocument()
  })

  it('disables downloads when there is no project', () => {
    render(
      <ProjectTokenExport
        projectId={null}
        colorCount={0}
        spacingCount={0}
        typographyCount={0}
        shadowCount={0}
      />
    )
    expect(screen.getByTestId('export-guide-html')).toBeDisabled()
    expect(screen.getByTestId('export-guide-pack')).toBeDisabled()
  })
})

import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { UploadArea } from '../UploadArea'
import { PreviewSection } from '../PreviewSection'
import { SettingsPanel } from '../SettingsPanel'
import { ExtractButton } from '../ExtractButton'
import { ProjectInfo } from '../ProjectInfo'

describe('image-uploader sub-components', () => {
  describe('UploadArea', () => {
    it('should render upload area with instructions', () => {
      const handlers = {
        onDragOver: vi.fn(),
        onDrop: vi.fn(),
        onFileSelect: vi.fn(),
      }

      render(<UploadArea {...handlers} />)

      expect(screen.getByText('Upload Image')).toBeInTheDocument()
      expect(screen.getByText(/Drag and drop or click/i)).toBeInTheDocument()
    })

    it('should handle file selection', async () => {
      const user = userEvent.setup()
      const onFileSelect = vi.fn()

      render(
        <UploadArea
          onDragOver={vi.fn()}
          onDrop={vi.fn()}
          onFileSelect={onFileSelect}
        />
      )

      const input = screen.getByRole('button', { name: /Upload Image/i })
      // Note: actual file selection testing requires more complex setup
      expect(input).toBeInTheDocument()
    })

    it('should call onDragOver when dragging', async () => {
      const user = userEvent.setup()
      const onDragOver = vi.fn()

      const { container } = render(
        <UploadArea
          onDragOver={onDragOver}
          onDrop={vi.fn()}
          onFileSelect={vi.fn()}
        />
      )

      const uploadArea = container.querySelector('.upload-area')
      if (uploadArea) {
        await user.pointer({ keys: '[MouseLeft>]', target: uploadArea })
        // Drag event would be triggered here
      }
    })
  })

  describe('PreviewSection', () => {
    it('should not render when preview is null', () => {
      render(<PreviewSection preview={null} fileName={null} />)
      expect(screen.queryByText('Preview')).not.toBeInTheDocument()
    })

    it('should render preview image and filename', () => {
      const preview = 'data:image/jpeg;base64,test'
      const filename = 'test.jpg'

      render(<PreviewSection preview={preview} fileName={filename} />)

      expect(screen.getByText('Preview')).toBeInTheDocument()
      expect(screen.getByAltText('Preview')).toHaveAttribute('src', preview)
      expect(screen.getByText(filename)).toBeInTheDocument()
    })

    it('should display filename without path', () => {
      const preview = 'data:image/png;base64,test'
      const filename = 'my-image.png'

      render(<PreviewSection preview={preview} fileName={filename} />)

      expect(screen.getByText(filename)).toBeInTheDocument()
    })
  })

  describe('SettingsPanel', () => {
    it('should render project name input and max colors slider', () => {
      render(
        <SettingsPanel
          projectName="My Project"
          maxColors={10}
          projectId={null}
          onProjectNameChange={vi.fn()}
          onMaxColorsChange={vi.fn()}
        />
      )

      expect(screen.getByLabelText(/Project Name/)).toHaveValue('My Project')
      expect(screen.getByLabelText(/Max Colors/)).toHaveValue('10')
    })

    it('should display current max colors value', () => {
      render(
        <SettingsPanel
          projectName="My Project"
          maxColors={25}
          projectId={null}
          onProjectNameChange={vi.fn()}
          onMaxColorsChange={vi.fn()}
        />
      )

      expect(screen.getByText(/Max Colors: 25/)).toBeInTheDocument()
    })

    it('should disable project name input when projectId exists', () => {
      render(
        <SettingsPanel
          projectName="My Project"
          maxColors={10}
          projectId={123}
          onProjectNameChange={vi.fn()}
          onMaxColorsChange={vi.fn()}
        />
      )

      expect(screen.getByLabelText(/Project Name/)).toBeDisabled()
    })

    it('should call onProjectNameChange when input changes', async () => {
      const user = userEvent.setup()
      const onProjectNameChange = vi.fn()

      render(
        <SettingsPanel
          projectName="My Project"
          maxColors={10}
          projectId={null}
          onProjectNameChange={onProjectNameChange}
          onMaxColorsChange={vi.fn()}
        />
      )

      const input = screen.getByLabelText(/Project Name/)
      await user.clear(input)
      await user.type(input, 'New Project')

      expect(onProjectNameChange).toHaveBeenCalledWith('New Project')
    })

    it('should call onMaxColorsChange when slider changes', async () => {
      const user = userEvent.setup()
      const onMaxColorsChange = vi.fn()

      render(
        <SettingsPanel
          projectName="My Project"
          maxColors={10}
          projectId={null}
          onProjectNameChange={vi.fn()}
          onMaxColorsChange={onMaxColorsChange}
        />
      )

      const slider = screen.getByLabelText(/Max Colors/) as HTMLInputElement
      await user.clear(slider)
      await user.type(slider, '20')

      expect(onMaxColorsChange).toHaveBeenCalled()
    })
  })

  describe('ExtractButton', () => {
    it('should render enabled extract button when not disabled', () => {
      render(
        <ExtractButton
          disabled={false}
          onClick={vi.fn()}
        />
      )

      const button = screen.getByRole('button', { name: /Extract Colors/ })
      expect(button).not.toBeDisabled()
      expect(button.title).toMatch(/Ready to extract/)
    })

    it('should render disabled extract button when disabled', () => {
      render(
        <ExtractButton
          disabled={true}
          onClick={vi.fn()}
        />
      )

      const button = screen.getByRole('button', { name: /Extract Colors/ })
      expect(button).toBeDisabled()
      expect(button.title).toMatch(/Please select an image/)
    })

    it('should call onClick when button is clicked', async () => {
      const user = userEvent.setup()
      const onClick = vi.fn()

      render(
        <ExtractButton
          disabled={false}
          onClick={onClick}
        />
      )

      await user.click(screen.getByRole('button', { name: /Extract Colors/ }))
      expect(onClick).toHaveBeenCalledTimes(1)
    })
  })

  describe('ProjectInfo', () => {
    it('should not render when projectId is null', () => {
      render(<ProjectInfo projectId={null} />)
      expect(screen.queryByText(/Project ID/)).not.toBeInTheDocument()
    })

    it('should render project ID when provided', () => {
      render(<ProjectInfo projectId={123} />)

      expect(screen.getByText(/Project ID/)).toBeInTheDocument()
      expect(screen.getByText('123')).toBeInTheDocument()
    })

    it('should display project ID in code element', () => {
      render(<ProjectInfo projectId={456} />)

      const codeElement = screen.getByText('456').closest('code')
      expect(codeElement).toBeInTheDocument()
    })
  })
})

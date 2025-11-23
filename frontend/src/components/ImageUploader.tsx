import { useState, useEffect } from 'react'
import './ImageUploader.css'
import { ColorToken } from '../types'
import { ApiClient } from '../api/client'
import { fileToBase64 as convertFileToBase64, isValidImageFile, isFileSizeValid } from '../utils'

interface Props {
  projectId: number | null
  onProjectCreated: (id: number) => void
  onColorExtracted: (colors: ColorToken[]) => void
  onError: (error: string) => void
  onLoadingChange: (loading: boolean) => void
}

// API base URL from environment or default
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1'

export default function ImageUploader({
  projectId,
  onProjectCreated,
  onColorExtracted,
  onError,
  onLoadingChange,
}: Props) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [projectName, setProjectName] = useState('My Colors')
  const [maxColors, setMaxColors] = useState(10)
  const [preview, setPreview] = useState<string | null>(null)

  // Log component mount
  useEffect(() => {
    console.log('ImageUploader component mounted')
    console.log('API_BASE_URL:', API_BASE_URL)
  }, [])

  // Create project if needed
  const ensureProject = async (): Promise<number> => {
    if (projectId) return projectId

    try {
      const response = await ApiClient.post<{ id: number }>('/projects', {
        name: projectName,
        description: 'Color extraction project',
      })
      const newProjectId = response.id
      onProjectCreated(newProjectId)
      return newProjectId
    } catch (err) {
      throw new Error('Failed to create project')
    }
  }

  // Handle file selection
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    console.log('File selected:', e.target.files)
    const file = e.target.files?.[0]
    if (!file) {
      console.log('No file selected')
      return
    }

    console.log('File details:', { name: file.name, size: file.size, type: file.type })

    // Validate file type using shared utility
    if (!isValidImageFile(file)) {
      onError('Please select a valid image file')
      return
    }

    // Validate file size (max 5MB) using shared utility
    const MAX_FILE_SIZE = 5 * 1024 * 1024
    if (!isFileSizeValid(file, MAX_FILE_SIZE)) {
      onError('Image size must be less than 5MB')
      return
    }

    setSelectedFile(file)
    console.log('File set successfully')

    // Generate preview using shared utility
    convertFileToBase64(file)
      .then((dataUrl) => {
        setPreview(dataUrl)
        console.log('Preview generated')
      })
      .catch((err) => {
        console.error('Failed to generate preview:', err)
      })

    onError('')
  }

  // Convert file to base64 (extract raw base64 without data URL prefix)
  const fileToBase64 = async (file: File): Promise<string> => {
    console.log('Starting FileReader.readAsDataURL...')
    const dataUrl = await convertFileToBase64(file)
    // Extract base64 part (remove data:image/...;base64, prefix)
    const base64 = dataUrl.split(',')[1]
    console.log('File converted to base64, length:', base64.length)
    return base64
  }

  // Handle extraction
  const handleExtract = async () => {
    if (!selectedFile) {
      onError('Please select an image first')
      return
    }

    try {
      console.log('Starting color extraction...')
      onLoadingChange(true)
      onError('')

      // Ensure project exists
      console.log('Ensuring project exists...')
      const pId = await ensureProject()
      console.log('Project ID:', pId)

      // Convert image to base64
      console.log('Converting image to base64...')
      const base64 = await fileToBase64(selectedFile)
      console.log('Base64 length:', base64.length)

      // Call streaming extraction API
      console.log('Calling streaming extraction API at:', `${API_BASE_URL}/colors/extract-streaming`)
      const streamResponse = await fetch(`${API_BASE_URL}/colors/extract-streaming`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: pId,
          image_base64: base64,
          max_colors: maxColors,
        })
      })

      if (!streamResponse.ok) {
        throw new Error(`API error: ${streamResponse.statusText}`)
      }

      // Parse streaming response
      const reader = streamResponse.body?.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let extractedColors: any[] = []

      while (reader) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const event = JSON.parse(line.slice(6))
              console.log('Stream event:', event)

              if (event.error) {
                throw new Error(event.error)
              }

              if (event.phase === 1 && event.status === 'colors_extracted') {
                console.log(`Extracted ${event.color_count} colors`)
              } else if (event.phase === 1 && event.status === 'colors_streaming') {
                console.log(`Progress: ${(event.progress * 100).toFixed(0)}%`)
              } else if (event.phase === 2 && event.status === 'extraction_complete') {
                console.log('Extraction complete! Got full color data from stream')
                extractedColors = event.colors || []
              }
            } catch (e) {
              console.error('Error parsing stream event:', e)
            }
          }
        }
      }

      console.log('Extracted colors:', extractedColors)
      onColorExtracted(extractedColors)
    } catch (err: any) {
      console.error('Extraction error:', err)
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to extract colors'
      onError(errorMsg)
    } finally {
      onLoadingChange(false)
    }
  }

  // Handle drag and drop
  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()

    const file = e.dataTransfer.files?.[0]
    if (file) {
      const event = {
        target: { files: [file] },
      } as any
      handleFileSelect(event)
    }
  }

  return (
    <div className="uploader">
      {/* Upload Area */}
      <div
        className="upload-area"
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="file-input"
          className="file-input"
          accept="image/*"
          onChange={handleFileSelect}
        />
        <label htmlFor="file-input" className="upload-label">
          <div className="upload-icon">📸</div>
          <h3>Upload Image</h3>
          <p>Drag and drop or click to select</p>
          <p className="upload-hint">JPEG, PNG, WebP (max 5MB)</p>
        </label>
      </div>

      {/* Preview */}
      {preview && (
        <div className="preview-section">
          <h4>Preview</h4>
          <img src={preview} alt="Preview" className="preview-image" />
          <p className="preview-name">{selectedFile?.name}</p>
        </div>
      )}

      {/* Settings */}
      <div className="settings">
        <div className="setting-group">
          <label htmlFor="project-name">Project Name:</label>
          <input
            id="project-name"
            type="text"
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
            placeholder="My Colors"
            disabled={projectId !== null}
          />
        </div>

        <div className="setting-group">
          <label htmlFor="max-colors">
            Max Colors: <span className="value">{maxColors}</span>
          </label>
          <input
            id="max-colors"
            type="range"
            min="1"
            max="50"
            value={maxColors}
            onChange={(e) => setMaxColors(parseInt(e.target.value))}
            className="slider"
          />
        </div>
      </div>

      {/* Extract Button */}
      <button
        className="extract-btn"
        onClick={() => {
          console.log('Extract button clicked! selectedFile:', selectedFile)
          handleExtract()
        }}
        disabled={!selectedFile}
        title={selectedFile ? 'Ready to extract colors' : 'Please select an image first'}
      >
        ✨ Extract Colors {selectedFile ? `(${selectedFile.name})` : ''}
      </button>

      {/* Project Info */}
      {projectId && (
        <div className="project-info">
          <p>Project ID: <code>{projectId}</code></p>
        </div>
      )}
    </div>
  )
}

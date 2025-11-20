import { useState } from 'react'
import axios from 'axios'
import './ImageUploader.css'

interface ColorToken {
  id?: number
  hex: string
  rgb: string
  name: string
  semantic_name?: string
  confidence: number
  harmony?: string
  usage?: string[]
}

interface Props {
  projectId: number | null
  onProjectCreated: (id: number) => void
  onColorExtracted: (colors: ColorToken[]) => void
  onError: (error: string) => void
  onLoadingChange: (loading: boolean) => void
}

const API_BASE_URL = '/api/v1'

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

  // Create project if needed
  const ensureProject = async (): Promise<number> => {
    if (projectId) return projectId

    try {
      const response = await axios.post(`${API_BASE_URL}/projects`, {
        name: projectName,
        description: 'Color extraction project',
      })
      const newProjectId = response.data.id
      onProjectCreated(newProjectId)
      return newProjectId
    } catch (err) {
      throw new Error('Failed to create project')
    }
  }

  // Handle file selection
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validate file type
    if (!file.type.startsWith('image/')) {
      onError('Please select a valid image file')
      return
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      onError('Image size must be less than 5MB')
      return
    }

    setSelectedFile(file)

    // Generate preview
    const reader = new FileReader()
    reader.onload = (event) => {
      setPreview(event.target?.result as string)
    }
    reader.readAsDataURL(file)

    onError('')
  }

  // Convert file to base64
  const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => {
        const result = reader.result as string
        // Extract base64 part (remove data:image/...;base64, prefix)
        const base64 = result.split(',')[1]
        resolve(base64)
      }
      reader.onerror = reject
    })
  }

  // Handle extraction
  const handleExtract = async () => {
    if (!selectedFile) {
      onError('Please select an image first')
      return
    }

    try {
      onLoadingChange(true)
      onError('')

      // Ensure project exists
      const pId = await ensureProject()

      // Convert image to base64
      const base64 = await fileToBase64(selectedFile)

      // Call extraction API
      const response = await axios.post(`${API_BASE_URL}/colors/extract`, {
        project_id: pId,
        image_base64: base64,
        max_colors: maxColors,
      })

      // Process response
      const extractedColors = response.data.colors
      onColorExtracted(extractedColors)
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Failed to extract colors'
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
        onClick={handleExtract}
        disabled={!selectedFile}
      >
        ✨ Extract Colors
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

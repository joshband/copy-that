import React, { useState } from 'react';
import { useBatchExtract } from '../api/hooks';
import './BatchImageUploader.css';

interface BatchImageUploaderProps {
  sessionId: number;
  projectId: number;
  onExtractionComplete: (libraryId: number, statistics: any) => void;
}

export function BatchImageUploader({
  sessionId,
  projectId,
  onExtractionComplete,
}: BatchImageUploaderProps) {
  const [imageUrls, setImageUrls] = useState<string[]>([]);
  const [maxColors, setMaxColors] = useState(10);
  const [progress, setProgress] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [currentImageInput, setCurrentImageInput] = useState('');

  const batchExtractMutation = useBatchExtract();

  const handleAddUrl = () => {
    if (!currentImageInput.trim()) {
      setError('Please enter a URL');
      return;
    }

    if (imageUrls.includes(currentImageInput)) {
      setError('URL already added');
      return;
    }

    if (imageUrls.length >= 50) {
      setError('Maximum 50 images per session');
      return;
    }

    setImageUrls([...imageUrls, currentImageInput.trim()]);
    setCurrentImageInput('');
    setError(null);
  };

  const handleRemoveUrl = (index: number) => {
    setImageUrls(imageUrls.filter((_, i) => i !== index));
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    // Handle dropped text (URLs)
    const text = e.dataTransfer.getData('text/plain');
    if (text) {
      const urls = text
        .split('\n')
        .map((url) => url.trim())
        .filter((url) => url.length > 0 && url.startsWith('http'))
        .filter((url) => !imageUrls.includes(url));

      const newUrls = [...imageUrls, ...urls].slice(0, 50);
      setImageUrls(newUrls);
    }
  };

  const handleExtractColors = async () => {
    if (imageUrls.length === 0) {
      setError('Please add at least one image URL');
      return;
    }

    setError(null);
    setProgress('Starting extraction...');

    try {
      const result = await batchExtractMutation.mutateAsync({
        sessionId,
        request: {
          image_urls: imageUrls,
          max_colors: maxColors,
        },
      });

      setProgress(`Extraction complete! ${result.extracted_tokens} colors extracted and aggregated.`);

      setTimeout(() => {
        onExtractionComplete(result.library_id, result.statistics);
      }, 1500);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Extraction failed';
      setError(message);
      setProgress('');
    }
  };

  return (
    <div className="batch-uploader">
      <div className="uploader-card">
        <h2>Upload Images for Batch Extraction</h2>

        {error && <div className="error-message">{error}</div>}
        {progress && <div className="success-message">{progress}</div>}

        <div className="input-section">
          <label>Image URLs</label>
          <div className="url-input-group">
            <input
              type="url"
              value={currentImageInput}
              onChange={(e) => setCurrentImageInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddUrl()}
              placeholder="https://example.com/image.jpg"
              disabled={batchExtractMutation.isPending}
            />
            <button
              onClick={handleAddUrl}
              disabled={batchExtractMutation.isPending || !currentImageInput.trim()}
              className="primary"
            >
              Add URL
            </button>
          </div>
          <p className="help-text">
            Paste URLs one at a time, or drag and drop multiple URLs at once. Maximum 50 images.
          </p>
        </div>

        <div className="drop-zone" onDragEnter={handleDrag} onDragLeave={handleDrag} onDragOver={handleDrag} onDrop={handleDrop}>
          <div className={`drop-content ${dragActive ? 'active' : ''}`}>
            <p>📎 Drop multiple image URLs here</p>
            <p className="small">or continue adding URLs above</p>
          </div>
        </div>

        {imageUrls.length > 0 && (
          <div className="urls-list">
            <h3>Images to Extract ({imageUrls.length})</h3>
            <div className="urls-grid">
              {imageUrls.map((url, index) => (
                <div key={index} className="url-item">
                  <div className="url-text" title={url}>
                    {index + 1}. {new URL(url).hostname}
                  </div>
                  <button
                    onClick={() => handleRemoveUrl(index)}
                    disabled={batchExtractMutation.isPending}
                    className="remove"
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="form-group">
          <label>Max Colors per Image</label>
          <input
            type="number"
            value={maxColors}
            onChange={(e) => setMaxColors(Math.max(1, Math.min(50, parseInt(e.target.value) || 10)))}
            min={1}
            max={50}
            disabled={batchExtractMutation.isPending}
          />
          <p className="help-text">Higher = more colors extracted (more detail, larger library)</p>
        </div>

        <button
          onClick={handleExtractColors}
          disabled={batchExtractMutation.isPending || imageUrls.length === 0}
          className="primary large"
        >
          {batchExtractMutation.isPending ? (
            <>
              <span className="spinner"></span>
              Extracting...
            </>
          ) : (
            `Extract & Aggregate Colors from ${imageUrls.length} Image${imageUrls.length === 1 ? '' : 's'}`
          )}
        </button>
      </div>

      <div className="info-panel">
        <h3>How It Works</h3>
        <ol>
          <li><strong>Extract:</strong> AI analyzes each image for dominant colors</li>
          <li><strong>Aggregate:</strong> Colors from all images are deduplicated using Delta-E</li>
          <li><strong>Organize:</strong> Similar colors are grouped and statistics calculated</li>
          <li><strong>Curate:</strong> You assign semantic roles (primary, secondary, etc.)</li>
        </ol>

        <h3>Pro Tips</h3>
        <ul>
          <li>Include 2-5 images for best results</li>
          <li>Higher resolution images = better color detection</li>
          <li>Mix different brand usage contexts (primary buttons, backgrounds, accents)</li>
        </ul>
      </div>
    </div>
  );
}

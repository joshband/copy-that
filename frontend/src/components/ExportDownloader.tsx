import React, { useState } from 'react';
import { useExportLibrary } from '../api/hooks';
import './ExportDownloader.css';

interface LibraryStatistics {
  color_count?: number;
  image_count?: number;
  avg_confidence?: number;
  multi_image_colors?: number;
  [key: string]: unknown;
}

interface ExportDownloaderProps {
  sessionId: number;
  libraryId: number;
  statistics: LibraryStatistics;
  onReset: () => void;
}

export function ExportDownloader({
  sessionId,
  libraryId: _libraryId,
  statistics,
  onReset,
}: ExportDownloaderProps) {
  void _libraryId; // Reserved for future use
  const [selectedFormat, setSelectedFormat] = useState<string>('w3c');
  const [error, setError] = useState<string | null>(null);

  const exportMutation = useExportLibrary();

  const formats = [
    {
      id: 'w3c',
      name: 'W3C Design Tokens',
      description: 'Industry standard JSON format for design tokens',
      icon: '📋',
    },
    {
      id: 'css',
      name: 'CSS Variables',
      description: 'CSS custom properties for web projects',
      icon: '🎨',
    },
    {
      id: 'react',
      name: 'React/TypeScript',
      description: 'Typed exports for React applications',
      icon: '⚛️',
    },
    {
      id: 'html',
      name: 'HTML Demo',
      description: 'Interactive demo page to preview colors',
      icon: '🌐',
    },
  ];

  const handleDownload = async () => {
    setError(null);

    try {
      const data = await exportMutation.mutateAsync({
        sessionId,
        format: selectedFormat,
      });

      // Create download link
      const element = document.createElement('a');
      const file = new Blob([data.content], { type: 'text/plain' });
      element.href = URL.createObjectURL(file);

      const fileExtensions: Record<string, string> = {
        w3c: 'json',
        css: 'css',
        react: 'ts',
        html: 'html',
      };

      element.download = `tokens.${fileExtensions[selectedFormat]}`;
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Download failed';
      setError(message);
    }
  };

  return (
    <div className="export-downloader">
      <div className="export-header">
        <h2>✨ Export Your Token Library</h2>
        <p>Download in your preferred format</p>
      </div>

      {error != null && error !== '' && <div className="error-message">{error}</div>}

      <div className="summary-card">
        <h3>Library Summary</h3>
        <div className="summary-stats">
          <div>
            <strong>{statistics.color_count ?? 0}</strong> unique colors
          </div>
          <div>
            <strong>{statistics.image_count ?? 0}</strong> source images
          </div>
          <div>
            <strong>{((statistics.avg_confidence ?? 0) * 100).toFixed(0)}%</strong> avg confidence
          </div>
          <div>
            <strong>{statistics.multi_image_colors ?? 0}</strong> multi-source colors
          </div>
        </div>
      </div>

      <div className="format-selector">
        <h3>Select Export Format</h3>
        <div className="formats-grid">
          {formats.map((format) => (
            <div
              key={format.id}
              className={`format-card ${selectedFormat === format.id ? 'selected' : ''}`}
              onClick={() => setSelectedFormat(format.id)}
            >
              <div className="format-icon">{format.icon}</div>
              <div className="format-name">{format.name}</div>
              <div className="format-description">{format.description}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="format-details">
        {selectedFormat === 'w3c' && (
          <div className="detail-panel">
            <h4>W3C Design Tokens (JSON)</h4>
            <p>Standard format used by design tools and frameworks</p>
            <ul>
              <li>Compatible with Figma Tokens, Style Dictionary, etc.</li>
              <li>Includes metadata and statistics</li>
              <li>Role-based organization</li>
            </ul>
          </div>
        )}
        {selectedFormat === 'css' && (
          <div className="detail-panel">
            <h4>CSS Custom Properties</h4>
            <p>CSS :root variables for web projects</p>
            <ul>
              <li>Ready to drop into your CSS</li>
              <li>Semantic naming (--color-primary, etc.)</li>
              <li>Confidence metadata in comments</li>
            </ul>
          </div>
        )}
        {selectedFormat === 'react' && (
          <div className="detail-panel">
            <h4>React/TypeScript</h4>
            <p>Typed exports for React applications</p>
            <ul>
              <li>Full type definitions</li>
              <li>Tree-shakeable exports</li>
              <li>Helper utility functions</li>
            </ul>
          </div>
        )}
        {selectedFormat === 'html' && (
          <div className="detail-panel">
            <h4>Interactive Demo Page</h4>
            <p>Beautiful HTML page to preview and share</p>
            <ul>
              <li>Copy-to-clipboard for hex values</li>
              <li>Statistics dashboard</li>
              <li>Responsive design</li>
            </ul>
          </div>
        )}
      </div>

      <div className="action-buttons">
        <button
          onClick={() => void handleDownload()}
          disabled={exportMutation.isPending}
          className="primary large"
        >
          {exportMutation.isPending ? 'Downloading...' : `Download as ${formats.find(f => f.id === selectedFormat)?.name}`}
        </button>

        <button
          onClick={onReset}
          disabled={exportMutation.isPending}
          className="secondary"
        >
          Start New Session
        </button>
      </div>

      <div className="export-tips">
        <h3>Next Steps</h3>
        <ol>
          <li>Download your tokens in the format you need</li>
          <li>Import into your design tool or development environment</li>
          <li>Use tokens consistently across your project</li>
          <li>Share with your team for alignment</li>
        </ol>
      </div>
    </div>
  );
}

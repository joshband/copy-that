/**
 * SpacingHeader sub-component
 * Displays the title, subtitle, and file upload controls
 */

import React from 'react';
import { SpacingLibrary } from './types';
import { styles } from './styles';

interface SpacingHeaderProps {
  library: SpacingLibrary;
  onFileChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onFileSelected?: (file: File) => void;
  isLoading?: boolean;
  error?: string | null;
}

export const SpacingHeader: React.FC<SpacingHeaderProps> = ({
  library,
  onFileChange,
  onFileSelected,
  isLoading = false,
  error = null,
}) => {
  const { spacing_count, image_count } = library.statistics;

  return (
    <header style={styles.header}>
      <h1 style={styles.title}>Spacing Token Library</h1>
      <p style={styles.subtitle}>
        {spacing_count} tokens extracted from {image_count} image(s)
      </p>
      {onFileSelected && (
        <div style={{ marginTop: '0.75rem', display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
          <input type="file" accept="image/*" onChange={onFileChange} />
          {isLoading && <span style={{ color: '#666' }}>Extracting spacings…</span>}
          {error && <span style={{ color: '#b91c1c' }}>{error}</span>}
        </div>
      )}
    </header>
  );
};

export default SpacingHeader;

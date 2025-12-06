/**
 * ScaleVisualization sub-component
 * Displays a bar chart visualization of spacing scale
 */

import React from 'react';
import { SpacingToken } from './types';
import { styles } from './styles';

interface ScaleVisualizationProps {
  tokens: SpacingToken[];
  maxValue: number;
  getBarHeight: (value: number) => number;
  onTokenClick?: (token: SpacingToken) => void;
}

export const ScaleVisualization: React.FC<ScaleVisualizationProps> = ({
  tokens,
  maxValue,
  getBarHeight,
  onTokenClick,
}) => {
  if (tokens.length === 0) {
    return (
      <div style={styles.scaleSection}>
        <h2 style={styles.sectionTitle}>Spacing Scale</h2>
        <p style={{ color: '#999' }}>No spacing tokens to display</p>
      </div>
    );
  }

  return (
    <div style={styles.scaleSection}>
      <h2 style={styles.sectionTitle}>Spacing Scale</h2>
      <div style={styles.scaleVisual}>
        {tokens.map((token) => {
          const barHeight = getBarHeight(token.value_px);
          return (
            <div
              key={token.name}
              style={styles.scaleBar}
              onClick={() => onTokenClick?.(token)}
            >
              <div
                style={{
                  ...styles.scaleBarFill,
                  height: `${barHeight}px`,
                }}
              />
              <span style={{ fontWeight: 600, fontSize: '0.8rem', color: '#333' }}>
                {token.value_px}px
              </span>
              <span style={{ fontSize: '0.7rem', color: '#666' }}>
                {token.role || token.name}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ScaleVisualization;

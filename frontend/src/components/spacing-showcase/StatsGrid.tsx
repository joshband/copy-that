/**
 * StatsGrid sub-component
 * Displays key statistics about the spacing library
 */

import React from 'react';
import { SpacingLibrary } from './types';
import { styles } from './styles';

interface StatsGridProps {
  library: SpacingLibrary;
  derivedBase: number;
  derivedScale: string;
}

export const StatsGrid: React.FC<StatsGridProps> = ({
  library,
  derivedBase,
  derivedScale,
}) => {
  const { statistics } = library;

  return (
    <div style={styles.statsGrid}>
      <div style={styles.stat}>
        <div style={styles.statValue}>{statistics.spacing_count}</div>
        <div style={styles.statLabel}>Tokens</div>
      </div>
      <div style={styles.stat}>
        <div style={styles.statValue}>{derivedScale || statistics.scale_system}</div>
        <div style={styles.statLabel}>Scale</div>
      </div>
      <div style={styles.stat}>
        <div style={styles.statValue}>{derivedBase || statistics.base_unit}px</div>
        <div style={styles.statLabel}>Base Unit</div>
      </div>
      <div style={styles.stat}>
        <div style={styles.statValue}>{(statistics.grid_compliance * 100).toFixed(0)}%</div>
        <div style={styles.statLabel}>Grid Aligned</div>
      </div>
      <div style={styles.stat}>
        <div style={styles.statValue}>{(statistics.avg_confidence * 100).toFixed(0)}%</div>
        <div style={styles.statLabel}>Confidence</div>
      </div>
      <div style={styles.stat}>
        <div style={styles.statValue}>{statistics.multi_image_spacings}</div>
        <div style={styles.statLabel}>Multi-Source</div>
      </div>
    </div>
  );
};

export default StatsGrid;

/**
 * Spacing Token Showcase Component
 *
 * Interactive React component for displaying and exploring spacing tokens.
 * Similar to color token showcase but optimized for spacing visualization.
 */

import React, { useState, useMemo } from 'react';

// Types
interface SpacingToken {
  value_px: number;
  value_rem: number;
  name: string;
  confidence: number;
  semantic_role?: string;
  spacing_type?: string;
  role?: string;
  grid_aligned?: boolean;
  tailwind_class?: string;
  provenance?: Record<string, number>;
}

interface SpacingLibrary {
  tokens: SpacingToken[];
  statistics: {
    spacing_count: number;
    image_count: number;
    scale_system: string;
    base_unit: number;
    grid_compliance: number;
    avg_confidence: number;
    value_range: { min: number; max: number };
    common_values: number[];
    multi_image_spacings: number;
  };
}

interface SpacingTokenShowcaseProps {
  library: SpacingLibrary;
  onTokenClick?: (token: SpacingToken) => void;
  showCopyButtons?: boolean;
  showMetadata?: boolean;
}

// Styles (inline for portability)
const styles = {
  container: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    padding: '1.5rem',
    backgroundColor: '#f5f5f5',
    minHeight: '100vh',
  },
  header: {
    backgroundColor: 'white',
    padding: '1.5rem',
    borderRadius: '8px',
    marginBottom: '1.5rem',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
  },
  title: {
    fontSize: '1.75rem',
    fontWeight: 600,
    color: '#333',
    marginBottom: '0.5rem',
  },
  subtitle: {
    color: '#666',
    fontSize: '0.9rem',
  },
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
    gap: '1rem',
    backgroundColor: 'white',
    padding: '1.5rem',
    borderRadius: '8px',
    marginBottom: '1.5rem',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
  },
  stat: {
    textAlign: 'center' as const,
  },
  statValue: {
    fontSize: '1.5rem',
    fontWeight: 700,
    color: '#333',
  },
  statLabel: {
    color: '#666',
    fontSize: '0.75rem',
    marginTop: '0.25rem',
  },
  scaleSection: {
    backgroundColor: 'white',
    padding: '1.5rem',
    borderRadius: '8px',
    marginBottom: '1.5rem',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
  },
  sectionTitle: {
    fontSize: '1.25rem',
    fontWeight: 600,
    color: '#333',
    marginBottom: '1rem',
  },
  scaleVisual: {
    display: 'flex',
    alignItems: 'flex-end',
    gap: '0.75rem',
    padding: '1rem',
    backgroundColor: '#fafafa',
    borderRadius: '4px',
    overflowX: 'auto' as const,
  },
  scaleBar: {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    gap: '0.5rem',
    cursor: 'pointer',
    transition: 'transform 0.2s',
  },
  scaleBarFill: {
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    borderRadius: '4px',
    minWidth: '40px',
    transition: 'transform 0.2s',
  },
  tokensGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
    gap: '1rem',
  },
  tokenCard: {
    backgroundColor: 'white',
    borderRadius: '8px',
    overflow: 'hidden',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
    border: '1px solid #e0e0e0',
    transition: 'transform 0.2s, box-shadow 0.2s',
    cursor: 'pointer',
  },
  tokenVisual: {
    padding: '1.25rem',
    backgroundColor: '#fafafa',
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    gap: '0.75rem',
  },
  spacingBox: {
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    borderRadius: '4px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: 'white',
    fontWeight: 600,
    fontSize: '0.8rem',
  },
  tokenInfo: {
    padding: '1rem',
  },
  tokenName: {
    fontWeight: 600,
    color: '#333',
    marginBottom: '0.25rem',
  },
  tokenValues: {
    fontFamily: 'monospace',
    fontSize: '0.8rem',
    color: '#666',
    marginBottom: '0.5rem',
  },
  badge: {
    display: 'inline-block',
    padding: '0.2rem 0.5rem',
    borderRadius: '10px',
    fontSize: '0.7rem',
    marginRight: '0.5rem',
    marginBottom: '0.5rem',
  },
  roleBadge: {
    backgroundColor: '#f0f0f0',
    color: '#666',
  },
  gridAlignedBadge: {
    backgroundColor: '#d4edda',
    color: '#155724',
  },
  gridMisalignedBadge: {
    backgroundColor: '#fff3cd',
    color: '#856404',
  },
  metadata: {
    fontSize: '0.75rem',
    color: '#999',
    marginTop: '0.5rem',
  },
  copyButtons: {
    display: 'flex',
    gap: '0.5rem',
    marginTop: '0.75rem',
  },
  copyButton: {
    flex: 1,
    padding: '0.4rem',
    backgroundColor: 'transparent',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontSize: '0.7rem',
    cursor: 'pointer',
    transition: 'all 0.2s',
  },
  filterBar: {
    display: 'flex',
    gap: '0.5rem',
    marginBottom: '1rem',
    flexWrap: 'wrap' as const,
  },
  filterButton: {
    padding: '0.5rem 1rem',
    border: '1px solid #ddd',
    borderRadius: '4px',
    backgroundColor: 'white',
    cursor: 'pointer',
    fontSize: '0.8rem',
    transition: 'all 0.2s',
  },
  filterButtonActive: {
    backgroundColor: '#667eea',
    color: 'white',
    borderColor: '#667eea',
  },
};

export const SpacingTokenShowcase: React.FC<SpacingTokenShowcaseProps> = ({
  library,
  onTokenClick,
  showCopyButtons = true,
  showMetadata = true,
}) => {
  const [filter, setFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'value' | 'confidence' | 'name'>('value');
  const [copiedValue, setCopiedValue] = useState<string | null>(null);

  const { tokens, statistics } = library;

  // Filter and sort tokens
  const displayTokens = useMemo(() => {
    let filtered = [...tokens];

    // Apply filter
    if (filter === 'aligned') {
      filtered = filtered.filter((t) => t.grid_aligned);
    } else if (filter === 'misaligned') {
      filtered = filtered.filter((t) => !t.grid_aligned);
    } else if (filter === 'multi-source') {
      filtered = filtered.filter((t) => t.provenance && Object.keys(t.provenance).length > 1);
    }

    // Apply sort
    filtered.sort((a, b) => {
      if (sortBy === 'value') return a.value_px - b.value_px;
      if (sortBy === 'confidence') return b.confidence - a.confidence;
      return a.name.localeCompare(b.name);
    });

    return filtered;
  }, [tokens, filter, sortBy]);

  // Copy to clipboard
  const copyToClipboard = async (text: string, label: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedValue(label);
      setTimeout(() => setCopiedValue(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  // Get max value for scale visualization
  const maxValue = Math.max(...tokens.map((t) => t.value_px));

  return (
    <div style={styles.container}>
      {/* Header */}
      <header style={styles.header}>
        <h1 style={styles.title}>Spacing Token Library</h1>
        <p style={styles.subtitle}>
          {statistics.spacing_count} tokens extracted from {statistics.image_count} image(s)
        </p>
      </header>

      {/* Statistics */}
      <div style={styles.statsGrid}>
        <div style={styles.stat}>
          <div style={styles.statValue}>{statistics.spacing_count}</div>
          <div style={styles.statLabel}>Tokens</div>
        </div>
        <div style={styles.stat}>
          <div style={styles.statValue}>{statistics.scale_system}</div>
          <div style={styles.statLabel}>Scale</div>
        </div>
        <div style={styles.stat}>
          <div style={styles.statValue}>{statistics.base_unit}px</div>
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

      {/* Scale Visualization */}
      <div style={styles.scaleSection}>
        <h2 style={styles.sectionTitle}>Spacing Scale</h2>
        <div style={styles.scaleVisual}>
          {tokens.map((token) => {
            const barHeight = maxValue > 0 ? Math.min(150, (token.value_px / maxValue) * 150) : 0;
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

      {/* Filters and Sort */}
      <div style={styles.scaleSection}>
        <h2 style={styles.sectionTitle}>Spacing Tokens</h2>
        <div style={styles.filterBar}>
          {['all', 'aligned', 'misaligned', 'multi-source'].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              style={{
                ...styles.filterButton,
                ...(filter === f ? styles.filterButtonActive : {}),
              }}
            >
              {f === 'all' ? 'All' : f === 'aligned' ? 'Grid Aligned' : f === 'misaligned' ? 'Off Grid' : 'Multi-Source'}
            </button>
          ))}
          <span style={{ marginLeft: 'auto', color: '#666', fontSize: '0.8rem' }}>
            Sort by:
          </span>
          {['value', 'confidence', 'name'].map((s) => (
            <button
              key={s}
              onClick={() => setSortBy(s as typeof sortBy)}
              style={{
                ...styles.filterButton,
                ...(sortBy === s ? styles.filterButtonActive : {}),
              }}
            >
              {s.charAt(0).toUpperCase() + s.slice(1)}
            </button>
          ))}
        </div>

        {/* Token Grid */}
        <div style={styles.tokensGrid}>
          {displayTokens.map((token) => {
            const boxSize = Math.min(token.value_px, 80);
            return (
              <div
                key={token.name}
                style={styles.tokenCard}
                onClick={() => onTokenClick?.(token)}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.15)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'none';
                  e.currentTarget.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.1)';
                }}
              >
                <div style={styles.tokenVisual}>
                  <div
                    style={{
                      ...styles.spacingBox,
                      width: `${boxSize}px`,
                      height: `${boxSize}px`,
                    }}
                  >
                    {token.value_px}px
                  </div>
                </div>
                <div style={styles.tokenInfo}>
                  <div style={styles.tokenName}>{token.name}</div>
                  <div style={styles.tokenValues}>
                    {token.value_px}px | {token.value_rem}rem
                  </div>
                  {token.role && (
                    <span style={{ ...styles.badge, ...styles.roleBadge }}>{token.role}</span>
                  )}
                  {token.grid_aligned !== undefined && (
                    <span
                      style={{
                        ...styles.badge,
                        ...(token.grid_aligned ? styles.gridAlignedBadge : styles.gridMisalignedBadge),
                      }}
                    >
                      {token.grid_aligned ? 'Grid Aligned' : 'Off Grid'}
                    </span>
                  )}
                  {showMetadata && (
                    <div style={styles.metadata}>
                      Confidence: {(token.confidence * 100).toFixed(0)}%
                      {token.provenance && ` | Sources: ${Object.keys(token.provenance).length}`}
                    </div>
                  )}
                  {showCopyButtons && (
                    <div style={styles.copyButtons}>
                      <button
                        style={styles.copyButton}
                        onClick={(e) => {
                          e.stopPropagation();
                          copyToClipboard(`${token.value_px}px`, 'px');
                        }}
                      >
                        {copiedValue === 'px' ? 'Copied!' : 'Copy px'}
                      </button>
                      <button
                        style={styles.copyButton}
                        onClick={(e) => {
                          e.stopPropagation();
                          copyToClipboard(`${token.value_rem}rem`, 'rem');
                        }}
                      >
                        {copiedValue === 'rem' ? 'Copied!' : 'Copy rem'}
                      </button>
                      <button
                        style={styles.copyButton}
                        onClick={(e) => {
                          e.stopPropagation();
                          copyToClipboard(`--${token.name}`, 'var');
                        }}
                      >
                        {copiedValue === 'var' ? 'Copied!' : 'Copy var'}
                      </button>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default SpacingTokenShowcase;

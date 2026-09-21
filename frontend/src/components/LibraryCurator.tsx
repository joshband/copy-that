import React, { useState, useEffect } from 'react';
import { useLibrary, useCurateTokens } from '../api/hooks';
import './LibraryCurator.css';

interface LibraryCuratorProps {
  sessionId: number;
  libraryId: number;
  statistics: any;
  onCurationComplete: () => void;
}

const VALID_ROLES = ['primary', 'secondary', 'accent', 'neutral', 'success', 'warning', 'danger', 'info'];
const ROLE_COLORS: Record<string, string> = {
  primary: '#FF5733',
  secondary: '#0066FF',
  accent: '#9933FF',
  neutral: '#808080',
  success: '#00AA00',
  warning: '#FFA500',
  danger: '#FF0000',
  info: '#00CCFF',
};

// ColorToken interface moved to shared types

export function LibraryCurator({
  sessionId,
  libraryId: _libraryId,
  statistics,
  onCurationComplete,
}: LibraryCuratorProps) {
  void _libraryId; // Reserved for future use
  const [roles, setRoles] = useState<Record<number, string>>({});
  const [error, setError] = useState<string | null>(null);

  const libraryQuery = useLibrary(sessionId);
  const curateTokensMutation = useCurateTokens();

  // Initialize roles when library loads
  useEffect(() => {
    if (libraryQuery.data?.tokens) {
      const initialRoles: Record<number, string> = {};
      libraryQuery.data.tokens.forEach((token) => {
        initialRoles[token.id] = token.role || '';
      });
      setRoles(initialRoles);
    }
  }, [libraryQuery.data?.tokens]);

  const handleRoleChange = (tokenId: number, role: string) => {
    setRoles({ ...roles, [tokenId]: role });
  };

  const handleCurate = async () => {
    const tokens = libraryQuery.data?.tokens || [];

    const roleAssignments = tokens
      .filter((token) => roles[token.id])
      .map((token) => ({
        token_id: token.id,
        role: roles[token.id],
      }));

    if (roleAssignments.length === 0) {
      setError('Please assign at least one role');
      return;
    }

    setError(null);

    try {
      await curateTokensMutation.mutateAsync({
        sessionId,
        request: {
          role_assignments: roleAssignments,
          notes: 'Curated from UI',
        },
      });

      onCurationComplete();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Curation failed';
      setError(message);
    }
  };

  return (
    <div className="library-curator">
      <div className="curator-header">
        <h2>Curate Token Library</h2>
        <p>Assign semantic roles to organize your color tokens</p>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="statistics-summary">
        <div className="stat">
          <div className="stat-label">Total Colors</div>
          <div className="stat-value">{statistics.color_count}</div>
        </div>
        <div className="stat">
          <div className="stat-label">Source Images</div>
          <div className="stat-value">{statistics.image_count}</div>
        </div>
        <div className="stat">
          <div className="stat-label">Avg. Confidence</div>
          <div className="stat-value">{(statistics.avg_confidence * 100).toFixed(0)}%</div>
        </div>
        <div className="stat">
          <div className="stat-label">Multi-Source</div>
          <div className="stat-value">{statistics.multi_image_colors}</div>
        </div>
      </div>

      <div className="tokens-curation">
        <div className="tokens-grid">
          {libraryQuery.isLoading ? (
            <p>Loading tokens...</p>
          ) : (libraryQuery.data?.tokens || []).length === 0 ? (
            <p>No tokens extracted yet</p>
          ) : (
            (libraryQuery.data?.tokens || []).map((token) => (
              <div key={token.id} className="token-card">
                <div
                  className="token-swatch"
                  style={{ backgroundColor: token.hex }}
                  title={token.hex}
                />
                <div className="token-info">
                  <div className="token-name">{token.name}</div>
                  <div className="token-hex">{token.hex}</div>
                  <div className="token-confidence">{(token.confidence * 100).toFixed(0)}%</div>
                </div>
                <div className="role-selector">
                  <select
                    value={roles[token.id] || ''}
                    onChange={(e) => handleRoleChange(token.id, e.target.value)}
                    disabled={curateTokensMutation.isPending}
                  >
                    <option value="">Unassigned</option>
                    {VALID_ROLES.map((role) => (
                      <option key={role} value={role}>
                        {role.charAt(0).toUpperCase() + role.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="role-guide">
        <h3>Role Guide</h3>
        <div className="role-examples">
          {VALID_ROLES.map((role) => (
            <div key={role} className="role-example">
              <div className="role-color" style={{ backgroundColor: ROLE_COLORS[role] }} />
              <div className="role-name">{role.charAt(0).toUpperCase() + role.slice(1)}</div>
              <div className="role-description">
                {getRoleDescription(role)}
              </div>
            </div>
          ))}
        </div>
      </div>

      <button
        onClick={() => void handleCurate()}
        disabled={curateTokensMutation.isPending || (libraryQuery.data?.tokens?.length ?? 0) === 0}
        className="primary large"
      >
        {curateTokensMutation.isPending ? 'Curating...' : 'Continue to Export'}
      </button>
    </div>
  );
}

function getRoleDescription(role: string): string {
  const descriptions: Record<string, string> = {
    primary: 'Main brand color',
    secondary: 'Supporting brand color',
    accent: 'Highlight/emphasis color',
    neutral: 'Grayscale/neutral color',
    success: 'Positive/success state',
    warning: 'Warning/caution state',
    danger: 'Error/danger state',
    info: 'Information state',
  };
  return descriptions[role] || '';
}

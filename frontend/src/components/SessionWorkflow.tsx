import React, { useState } from 'react';
import { SessionCreator } from './SessionCreator';
import { BatchImageUploader } from './BatchImageUploader';
import { LibraryCurator } from './LibraryCurator';
import { ExportDownloader } from './ExportDownloader';
import './SessionWorkflow.css';

interface SessionState {
  sessionId: number | null;
  projectId: number | null;
  step: 'create' | 'upload' | 'curate' | 'export';
  libraryId: number | null;
  statistics: any | null;
  loading: boolean;
}

export function SessionWorkflow() {
  const [state, setState] = useState<SessionState>({
    sessionId: null,
    projectId: null,
    step: 'create',
    libraryId: null,
    statistics: null,
    loading: false,
  });

  const handleSessionCreated = (sessionId: number, projectId: number) => {
    setState(prev => ({
      ...prev,
      sessionId,
      projectId,
      step: 'upload',
    }));
  };

  const handleExtractionComplete = (libraryId: number, statistics: any) => {
    setState(prev => ({
      ...prev,
      libraryId,
      statistics,
      step: 'curate',
    }));
  };

  const handleCurationComplete = () => {
    setState(prev => ({
      ...prev,
      step: 'export',
    }));
  };

  const handleReset = () => {
    setState({
      sessionId: null,
      projectId: null,
      step: 'create',
      libraryId: null,
      statistics: null,
      loading: false,
    });
  };

  const stepVal = state.step as string;

  return (
    <div className="session-workflow">
      <div className="workflow-header">
        <h1>🎨 Token Extraction Workflow</h1>
        <p>Extract, aggregate, and export design tokens from your images</p>
      </div>

      <div className="workflow-steps">
        <div className="step-indicator">
          <div className={`step ${stepVal === 'create' ? 'active' : stepVal !== 'create' ? 'completed' : ''}`}>
            <div className="step-number">1</div>
            <div className="step-label">Create Session</div>
          </div>

          <div className={`step ${stepVal === 'upload' ? 'active' : stepVal !== 'upload' && stepVal !== 'create' ? 'completed' : ''}`}>
            <div className="step-number">2</div>
            <div className="step-label">Extract Colors</div>
          </div>

          <div className={`step ${stepVal === 'curate' ? 'active' : stepVal === 'export' ? 'completed' : ''}`}>
            <div className="step-number">3</div>
            <div className="step-label">Curate Tokens</div>
          </div>

          <div className={`step ${stepVal === 'export' ? 'active' : ''}`}>
            <div className="step-number">4</div>
            <div className="step-label">Export</div>
          </div>
        </div>
      </div>

      <div className="workflow-content">
        {state.step === 'create' && (
          <SessionCreator onSessionCreated={handleSessionCreated} />
        )}

        {state.step === 'upload' && state.sessionId && state.projectId && (
          <BatchImageUploader
            sessionId={state.sessionId}
            projectId={state.projectId}
            onExtractionComplete={handleExtractionComplete}
          />
        )}

        {state.step === 'curate' && state.sessionId && state.libraryId && (
          <LibraryCurator
            sessionId={state.sessionId}
            libraryId={state.libraryId}
            statistics={state.statistics}
            onCurationComplete={handleCurationComplete}
          />
        )}

        {state.step === 'export' && state.sessionId && state.libraryId && (
          <ExportDownloader
            sessionId={state.sessionId}
            libraryId={state.libraryId}
            statistics={state.statistics}
            onReset={handleReset}
          />
        )}
      </div>

      {state.loading && (
        <div className="loading-overlay">
          <div className="spinner"></div>
          <p>Processing...</p>
        </div>
      )}
    </div>
  );
}

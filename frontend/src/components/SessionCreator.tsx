import React, { useState, useEffect } from 'react';
import { useCreateSession, useProjects } from '../api/hooks';
import './SessionCreator.css';

interface SessionCreatorProps {
  onSessionCreated: (sessionId: number, projectId: number) => void;
}

export function SessionCreator({ onSessionCreated }: SessionCreatorProps) {
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null);
  const [sessionName, setSessionName] = useState('');
  const [sessionDescription, setSessionDescription] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [showNewProject, setShowNewProject] = useState(false);
  const [_newProjectName, _setNewProjectName] = useState('');
  void _newProjectName; // Reserved for future use
  void _setNewProjectName;

  const createSessionMutation = useCreateSession();
  const { data: projects = [], isLoading: projectsLoading, error: projectsError } = useProjects();

  // Select first project when projects load
  useEffect(() => {
    if (projects.length > 0 && !selectedProjectId) {
      setSelectedProjectId(projects[0].id);
    }
  }, [projects, selectedProjectId]);

  const handleCreateSession = async () => {
    if (!selectedProjectId) {
      setError('Please select or create a project');
      return;
    }

    if (!sessionName.trim()) {
      setError('Session name is required');
      return;
    }

    setError(null);

    try {
      const session = await createSessionMutation.mutateAsync({
        project_id: selectedProjectId,
        session_name: sessionName,
        session_description: sessionDescription || undefined,
      });
      onSessionCreated(session.session_id, selectedProjectId);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to create session';
      setError(message);
    }
  };

  return (
    <div className="session-creator">
      <div className="creator-card">
        <h2>Create Extraction Session</h2>

        {error && <div className="error-message">{error}</div>}

        <div className="form-group">
          <label>Project</label>
          <div className="project-selector">
            <select
              value={selectedProjectId || ''}
              onChange={(e) => setSelectedProjectId(Number(e.target.value))}
              disabled={createSessionMutation.isPending || projectsLoading}
            >
              {projectsLoading ? (
                <option value="">Loading projects...</option>
              ) : projectsError ? (
                <option value="">Failed to load projects</option>
              ) : projects.length === 0 ? (
                <option value="">No projects available</option>
              ) : (
                <>
                  <option value="">Select a project...</option>
                  {projects.map((project) => (
                    <option key={project.id} value={project.id}>
                      {project.name}
                    </option>
                  ))}
                </>
              )}
            </select>
            <button
              onClick={() => setShowNewProject(!showNewProject)}
              disabled={createSessionMutation.isPending}
              className="secondary"
            >
              New Project
            </button>
          </div>
        </div>

        <div className="form-group">
          <label>Session Name</label>
          <input
            type="text"
            value={sessionName}
            onChange={(e) => setSessionName(e.target.value)}
            placeholder="e.g., Brand Colors - Q1 2025"
            disabled={createSessionMutation.isPending}
          />
        </div>

        <div className="form-group">
          <label>Description (optional)</label>
          <textarea
            value={sessionDescription}
            onChange={(e) => setSessionDescription(e.target.value)}
            placeholder="What are you extracting tokens from?"
            rows={3}
            disabled={createSessionMutation.isPending}
          />
        </div>

        <button
          onClick={() => void handleCreateSession()}
          disabled={createSessionMutation.isPending || !selectedProjectId || !sessionName.trim()}
          className="primary large"
        >
          {createSessionMutation.isPending ? 'Creating Session...' : 'Create Session & Continue'}
        </button>
      </div>

      <div className="info-panel">
        <h3>What is a Session?</h3>
        <p>
          A session is a batch of images you want to extract design tokens from together.
          Colors from multiple images are automatically aggregated and deduplicated.
        </p>
        <ul>
          <li>Upload multiple images at once</li>
          <li>Automatic color deduplication</li>
          <li>Assign semantic roles (primary, secondary, etc.)</li>
          <li>Export in multiple formats</li>
        </ul>
      </div>
    </div>
  );
}

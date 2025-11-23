/**
 * TanStack Query hooks for session workflow API
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { ApiClient } from './client';

// Types
export interface Project {
  id: number;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface Session {
  session_id: number;
  project_id: number;
  session_name: string;
  session_description?: string;
  image_count: number;
  created_at: string;
  updated_at: string;
}

export interface BatchExtractRequest {
  image_urls: string[];
  max_colors: number;
}

export interface ExtractionResult {
  status: string;
  session_id: number;
  library_id: number;
  extracted_tokens: number;
  statistics: {
    total: number;
    unique: number;
    [key: string]: unknown;
  };
}

export interface ColorToken {
  id: number;
  hex: string;
  rgb: string;
  name: string;
  confidence: number;
  harmony?: string;
  temperature?: string;
  role?: string;
  provenance?: Record<string, number>;
}

export interface Library {
  library_id: number;
  session_id: number;
  token_type: string;
  tokens: ColorToken[];
  statistics: Record<string, unknown>;
  is_curated: boolean;
}

export interface RoleAssignment {
  token_id: number;
  role: string;
}

export interface CurateRequest {
  role_assignments: RoleAssignment[];
  notes?: string;
}

export interface ExportResponse {
  format: string;
  content: string;
  filename: string;
}

// Project queries
export function useProjects() {
  return useQuery({
    queryKey: ['projects'],
    queryFn: () => ApiClient.get<Project[]>('/projects'),
    staleTime: 60000, // 1 minute
  });
}

// Session queries
export function useCreateSession() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { project_id: number; session_name?: string; session_description?: string }) =>
      ApiClient.post<Session>('/sessions', data),
    onSuccess: (session) => {
      queryClient.setQueryData(['session', session.session_id], session);
    },
  });
}

export function useSession(sessionId: number | null) {
  return useQuery({
    queryKey: ['session', sessionId],
    queryFn: () => (sessionId != null ? ApiClient.get<Session>(`/sessions/${sessionId}`) : null),
    enabled: sessionId != null,
    staleTime: 30000, // 30 seconds
  });
}

// Extraction queries
export function useBatchExtract() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ sessionId, request }: { sessionId: number; request: BatchExtractRequest }) =>
      ApiClient.post<ExtractionResult>(`/sessions/${sessionId}/extract`, request),
    onSuccess: (result) => {
      // Invalidate library query when extraction completes
      void queryClient.invalidateQueries({ queryKey: ['library', result.session_id] });
    },
  });
}

// Library queries
export function useLibrary(sessionId: number | null) {
  return useQuery({
    queryKey: ['library', sessionId],
    queryFn: () => (sessionId != null ? ApiClient.get<Library>(`/sessions/${sessionId}/library`) : null),
    enabled: sessionId != null,
  });
}

export function useCurateTokens() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ sessionId, request }: { sessionId: number; request: CurateRequest }) =>
      ApiClient.post<{ status: string }>(`/sessions/${sessionId}/library/curate`, request),
    onSuccess: (_, { sessionId }) => {
      // Invalidate library query when curation completes
      void queryClient.invalidateQueries({ queryKey: ['library', sessionId] });
    },
  });
}

// Export queries
export function useExportLibrary() {
  return useMutation({
    mutationFn: async ({ sessionId, format }: { sessionId: number; format: string }) =>
      ApiClient.get<ExportResponse>(`/sessions/${sessionId}/library/export?format=${format}`),
  });
}

// Convenience hook for full workflow
export function useSessionWorkflow() {
  const createSession = useCreateSession();
  const batchExtract = useBatchExtract();
  const curateTokens = useCurateTokens();
  const exportLibrary = useExportLibrary();

  return {
    createSession,
    batchExtract,
    curateTokens,
    exportLibrary,
    isLoading: [createSession.isPending, batchExtract.isPending, curateTokens.isPending, exportLibrary.isPending].some(Boolean),
  };
}

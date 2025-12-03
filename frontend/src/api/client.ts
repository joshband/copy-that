/**
 * API client with fetch and TanStack Query
 *
 * Uses zod for runtime validation of API responses
 */

import {
  ColorTokenSchema,
  ProjectSchema,
  ExtractionResponseSchema,
  type ColorToken,
  type Project,
  type ExtractionResponse,
} from './schemas';
import { z } from 'zod';
import type { W3CDesignTokenResponse } from '../types';

// Type-safe environment variable access
export const API_BASE = (import.meta as any).env?.VITE_API_URL ?? '/api/v1';

export interface ApiError {
  detail?: string;
  error?: string;
  message?: string;
}

export class ApiClient {
  static async request<T>(
    path: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE}${path}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error: ApiError = await (response.json() as Promise<ApiError>).catch(() => ({
        detail: `HTTP ${response.status}: ${response.statusText}`,
      }));
      throw error;
    }

    return response.json() as Promise<T>;
  }

  static get<T>(path: string): Promise<T> {
    return this.request<T>(path, { method: 'GET' });
  }

  static post<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>(path, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  static put<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>(path, {
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  static delete<T>(path: string): Promise<T> {
    return this.request<T>(path, { method: 'DELETE' });
  }

  /**
   * Validated API methods
   * These methods validate responses with zod schemas
   */

  /**
   * Get colors for a project with validation
   */
  static async getColors(projectId: number): Promise<ColorToken[]> {
    const data = await this.get<unknown>(`/projects/${projectId}/colors`);
    return z.array(ColorTokenSchema).parse(data);
  }

  /**
   * Create a new project with validation
   */
  static async createProject(name: string, description?: string): Promise<Project> {
    const data = await this.post<unknown>('/projects', { name, description });
    return ProjectSchema.parse(data);
  }

  /**
   * Extract colors from image with validation
   */
  static async extractColors(
    projectId: number,
    imageBase64: string,
    maxColors: number
  ): Promise<ExtractionResponse> {
    const data = await this.post<unknown>('/colors/extract', {
      project_id: projectId,
      image_base64: imageBase64,
      max_colors: maxColors,
    });
    return ExtractionResponseSchema.parse(data);
  }

  /**
   * Get a project by ID with validation
   */
  static async getProject(projectId: number): Promise<Project> {
    const data = await this.get<unknown>(`/projects/${projectId}`);
    return ProjectSchema.parse(data);
  }

  /**
   * Fetch W3C design tokens for a project (graph-aware)
   */
  static async getDesignTokens(projectId: number): Promise<W3CDesignTokenResponse> {
    const data = await this.get<unknown>(`/design-tokens/export/w3c?project_id=${projectId}`);
    return data as W3CDesignTokenResponse;
  }

  /**
   * Get inferred overview metrics for a project
   */
  static async getOverviewMetrics(projectId?: number): Promise<{
    spacing_scale_system: string | null;
    spacing_uniformity: number;
    color_harmony_type: string | null;
    color_palette_type: string | null;
    color_temperature: string | null;
    typography_hierarchy_depth: number;
    typography_scale_type: string | null;
    design_system_maturity: string;
    token_organization_quality: string;
    insights: string[];
    summary: {
      total_colors: number;
      total_spacing: number;
      total_typography: number;
      total_shadows: number;
    };
  }> {
    const url = projectId
      ? `/design-tokens/overview/metrics?project_id=${projectId}`
      : '/design-tokens/overview/metrics';
    const data = await this.get<unknown>(url);
    return data as any;
  }
}

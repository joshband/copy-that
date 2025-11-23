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

// Type-safe environment variable access
const API_BASE = (import.meta.env.VITE_API_URL as string | undefined) ?? '/api/v1';

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
}

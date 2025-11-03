/**
 * API Client for Copy That Backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface Project {
  id: string;
  name: string;
  created_at: string;
  status: string;
  images: Array<{
    id: string;
    filename: string;
    path: string;
    uploaded_at: string;
  }>;
  use_openai: boolean;
  analysis: any;
  design_system: any;
}

export interface VisualDNA {
  color_genome: any;
  shape_language: any;
  texture_signature: any;
  spatial_rhythm: any;
  visual_weight: any;
  elevation_model: any;
  corner_style: any;
  design_rules: any;
}

export interface ComponentLibrary {
  metadata: {
    name: string;
    version: string;
    generated_at: string;
    component_count: number;
  };
  components: Record<string, any>;
}

class APIClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  // Helper method for API requests
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;

    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        detail: response.statusText,
      }));
      throw new Error(error.detail || 'API request failed');
    }

    return response.json();
  }

  // Project Management

  async createProject(name: string, useOpenAI: boolean = true): Promise<{
    project_id: string;
    project: Project;
  }> {
    return this.request('/projects', {
      method: 'POST',
      body: JSON.stringify({ name, use_openai: useOpenAI }),
    });
  }

  async listProjects(): Promise<{ projects: Project[] }> {
    return this.request('/projects');
  }

  async getProject(projectId: string): Promise<Project> {
    return this.request(`/projects/${projectId}`);
  }

  async deleteProject(projectId: string): Promise<{ status: string }> {
    return this.request(`/projects/${projectId}`, {
      method: 'DELETE',
    });
  }

  // Image Upload

  async uploadImages(
    projectId: string,
    files: File[]
  ): Promise<{
    project_id: string;
    uploaded: number;
    images: any[];
  }> {
    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));

    const url = `${this.baseURL}/projects/${projectId}/upload`;
    const response = await fetch(url, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Upload failed');
    }

    return response.json();
  }

  // Analysis

  async analyzeProject(projectId: string): Promise<{
    project_id: string;
    status: string;
    visual_dna: VisualDNA;
    ai_analysis: any;
  }> {
    return this.request(`/projects/${projectId}/analyze`, {
      method: 'POST',
    });
  }

  // Generation

  async generateDesignSystem(
    projectId: string,
    options: {
      components?: string[];
      export_formats?: string[];
    } = {}
  ): Promise<{
    project_id: string;
    status: string;
    summary: any;
    component_library: ComponentLibrary;
  }> {
    return this.request(`/projects/${projectId}/generate`, {
      method: 'POST',
      body: JSON.stringify(options),
    });
  }

  // Components

  async listComponents(projectId: string): Promise<{
    project_id: string;
    components: Record<string, any>;
  }> {
    return this.request(`/projects/${projectId}/components`);
  }

  async getComponent(projectId: string, componentType: string): Promise<{
    project_id: string;
    component_type: string;
    component: any;
  }> {
    return this.request(`/projects/${projectId}/components/${componentType}`);
  }

  async getComponentVariant(
    projectId: string,
    componentType: string,
    variantKey: string
  ): Promise<any> {
    return this.request(
      `/projects/${projectId}/components/${componentType}/${variantKey}`
    );
  }

  // Tokens

  async getDesignTokens(
    projectId: string,
    format: 'json' | 'css' | 'tailwind' = 'json'
  ): Promise<any> {
    const response = await fetch(
      `${this.baseURL}/projects/${projectId}/tokens?format=${format}`
    );

    if (!response.ok) {
      throw new Error('Failed to fetch design tokens');
    }

    if (format === 'json') {
      return response.json();
    } else {
      return response.text();
    }
  }

  // Export

  async exportDesignSystem(
    projectId: string
  ): Promise<Blob> {
    const response = await fetch(
      `${this.baseURL}/projects/${projectId}/export?format=zip`,
      {
        method: 'POST',
      }
    );

    if (!response.ok) {
      throw new Error('Failed to export design system');
    }

    return response.blob();
  }
}

export const api = new APIClient();
export default api;

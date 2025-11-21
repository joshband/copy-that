variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "copy-that-platform"
}

variable "region" {
  description = "GCP region for resources"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "prod"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

# ============================================
# Cloud Run Configuration
# ============================================

variable "service_name" {
  description = "Cloud Run service name"
  type        = string
  default     = "copy-that-api"
}

variable "image_tag" {
  description = "Docker image tag (e.g., latest, v1.0.0)"
  type        = string
  default     = "latest"
}

variable "cloud_run_memory" {
  description = "Memory allocation (MB): 128, 256, 512, 1024, 2048, 4096"
  type        = string
  default     = "512"
}

variable "cloud_run_cpu" {
  description = "CPU allocation: 1, 2, 4 (must scale with memory)"
  type        = string
  default     = "1"
}

variable "cloud_run_timeout" {
  description = "Request timeout in seconds (max 3600)"
  type        = number
  default     = 300
}

variable "cloud_run_max_instances" {
  description = "Maximum concurrent instances"
  type        = number
  default     = 10
}

variable "cloud_run_min_instances" {
  description = "Minimum instances (0 = scale to zero)"
  type        = number
  default     = 0
}

variable "allow_unauthenticated" {
  description = "Allow unauthenticated invocations"
  type        = bool
  default     = true
}

# ============================================
# Artifact Registry
# ============================================

variable "artifact_registry_name" {
  description = "Artifact Registry repository name"
  type        = string
  default     = "copy-that"
}

# ============================================
# Environment Variables (Secrets)
# ============================================

variable "anthropic_api_key" {
  description = "Anthropic API key for Claude"
  type        = string
  sensitive   = true
}

variable "database_url" {
  description = "Neon PostgreSQL connection string"
  type        = string
  sensitive   = true
}

variable "allowed_origins" {
  description = "CORS allowed origins (comma-separated)"
  type        = string
  default     = "https://copy-that.com,https://www.copy-that.com"
}

variable "vite_api_url" {
  description = "Frontend API URL"
  type        = string
  default     = "https://api.copy-that.com/api/v1"
}

variable "log_level" {
  description = "Application log level"
  type        = string
  default     = "info"
  validation {
    condition     = contains(["debug", "info", "warning", "error"], var.log_level)
    error_message = "Log level must be debug, info, warning, or error."
  }
}

# ============================================
# Common Labels
# ============================================

variable "labels" {
  description = "Labels applied to all resources"
  type        = map(string)
  default = {
    project    = "copy-that"
    managed_by = "terraform"
  }
}

# Project Configuration
variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "copy-that-platform"
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "GCP Zone"
  type        = string
  default     = "us-central1-a"
}

variable "environment" {
  description = "Environment (staging, production)"
  type        = string
  default     = "staging"

  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "Environment must be either 'staging' or 'production'."
  }
}

# GitHub Configuration
variable "github_repository" {
  description = "GitHub repository in format owner/repo"
  type        = string
  default     = "joshband/copy-that"
}

# Networking
variable "vpc_cidr" {
  description = "CIDR range for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "private_ip_range" {
  description = "Private IP range for Cloud SQL and services"
  type        = string
  default     = "10.1.0.0/16"
}

# Cloud Run Configuration
variable "cloudrun_cpu" {
  description = "CPU units for Cloud Run service"
  type        = string
  default     = "1"
}

variable "cloudrun_memory" {
  description = "Memory for Cloud Run service"
  type        = string
  default     = "512Mi"
}

variable "cloudrun_max_instances" {
  description = "Maximum number of Cloud Run instances"
  type        = number
  default     = 10
}

variable "cloudrun_min_instances" {
  description = "Minimum number of Cloud Run instances"
  type        = number
  default     = 0
}

variable "cloudrun_concurrency" {
  description = "Requests per instance"
  type        = number
  default     = 80
}

# Database Configuration
variable "database_tier" {
  description = "Cloud SQL tier"
  type        = string
  default     = "db-f1-micro" # Use db-custom-2-7680 for production
}

variable "database_disk_size" {
  description = "Database disk size in GB"
  type        = number
  default     = 10
}

variable "database_backup_enabled" {
  description = "Enable automated backups"
  type        = bool
  default     = true
}

variable "database_ha_enabled" {
  description = "Enable high availability"
  type        = bool
  default     = false
}

# Redis Configuration
variable "redis_tier" {
  description = "Redis tier (BASIC, STANDARD_HA)"
  type        = string
  default     = "BASIC"
}

variable "redis_memory_size_gb" {
  description = "Redis memory size in GB"
  type        = number
  default     = 1
}

# Artifact Registry
variable "docker_repository_name" {
  description = "Docker repository name in Artifact Registry"
  type        = string
  default     = "copy-that"
}

# Domain Configuration
variable "domain_name" {
  description = "Custom domain name (optional)"
  type        = string
  default     = ""
}

# API Keys (stored in Secret Manager)
variable "anthropic_api_key_secret_name" {
  description = "Name of secret containing Anthropic API key"
  type        = string
  default     = "anthropic-api-key"
}

variable "openai_api_key_secret_name" {
  description = "Name of secret containing OpenAI API key"
  type        = string
  default     = "openai-api-key"
}

# Monitoring
variable "enable_monitoring" {
  description = "Enable Cloud Monitoring and Logging"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "Log retention in days"
  type        = number
  default     = 30
}

# Tags
variable "labels" {
  description = "Labels to apply to resources"
  type        = map(string)
  default = {
    project     = "copy-that"
    managed_by  = "terraform"
    environment = "staging"
  }
}

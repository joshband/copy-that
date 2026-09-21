# Minimal Cost-Optimized Infrastructure for Personal/Demo Use
# Uses: Cloud Run + External Free Services (Neon + Upstash)
# Cost: ~$0-5/month (only pay for actual Cloud Run requests)
#
# To use this instead of main.tf:
# 1. Rename main.tf to main-full.tf
# 2. Rename this file to main.tf
# 3. Run terraform init && terraform apply

terraform {
  required_version = ">= 1.5"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }

  backend "gcs" {
    bucket = "copy-that-terraform-state"
    prefix = "terraform/state-minimal"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs (minimal set)
resource "google_project_service" "apis" {
  for_each = toset([
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "secretmanager.googleapis.com",
    "iam.googleapis.com",
    "cloudbuild.googleapis.com"
  ])

  service            = each.value
  disable_on_destroy = false
}

# Service account for Cloud Run
resource "google_service_account" "cloudrun_sa" {
  account_id   = "copy-that-cloudrun-minimal"
  display_name = "Copy That Cloud Run Service Account (Minimal)"
  description  = "Service account for Cloud Run (minimal setup)"

  depends_on = [google_project_service.apis]
}

# Service account for Cloud Build
resource "google_service_account" "cloudbuild_sa" {
  account_id   = "copy-that-cloudbuild-minimal"
  display_name = "Copy That Cloud Build Service Account (Minimal)"
  description  = "Service account for Cloud Build (minimal setup)"

  depends_on = [google_project_service.apis]
}

# Grant IAM roles
resource "google_project_iam_member" "cloudrun_sa_roles" {
  for_each = toset([
    "roles/secretmanager.secretAccessor",
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter"
  ])

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.cloudrun_sa.email}"
}

resource "google_project_iam_member" "cloudbuild_sa_roles" {
  for_each = toset([
    "roles/run.admin",
    "roles/artifactregistry.writer",
    "roles/iam.serviceAccountUser"
  ])

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.cloudbuild_sa.email}"
}

# Workload Identity for GitHub Actions
resource "google_iam_workload_identity_pool" "github" {
  workload_identity_pool_id = "github-actions-pool-minimal"
  display_name              = "GitHub Actions Pool (Minimal)"
  description               = "Workload Identity Pool for GitHub Actions (minimal setup)"
  disabled                  = false

  depends_on = [google_project_service.apis]
}

resource "google_iam_workload_identity_pool_provider" "github" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-actions-provider"
  display_name                       = "GitHub Actions Provider"
  description                        = "OIDC identity pool provider for GitHub Actions"

  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.actor"      = "assertion.actor"
    "attribute.repository" = "assertion.repository"
  }

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

resource "google_service_account_iam_member" "github_actions_sa" {
  service_account_id = google_service_account.cloudbuild_sa.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.repository/${var.github_repository}"
}

# Artifact Registry for Docker images
resource "google_artifact_registry_repository" "docker_repo" {
  location      = var.region
  repository_id = var.docker_repository_name
  description   = "Docker repository for Copy That (minimal setup)"
  format        = "DOCKER"

  labels = var.labels

  depends_on = [google_project_service.apis]
}

resource "google_artifact_registry_repository_iam_member" "cloudbuild_writer" {
  project    = var.project_id
  location   = google_artifact_registry_repository.docker_repo.location
  repository = google_artifact_registry_repository.docker_repo.name
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:${google_service_account.cloudbuild_sa.email}"
}

resource "google_artifact_registry_repository_iam_member" "cloudrun_reader" {
  project    = var.project_id
  location   = google_artifact_registry_repository.docker_repo.location
  repository = google_artifact_registry_repository.docker_repo.name
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${google_service_account.cloudrun_sa.email}"
}

# Store external database URL in Secret Manager
# You'll need to manually create this secret and add your Neon.tech URL
resource "google_secret_manager_secret" "database_url" {
  secret_id = "database-url-external"

  replication {
    auto {}
  }

  labels = var.labels

  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret_iam_member" "database_url_access" {
  secret_id = google_secret_manager_secret.database_url.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloudrun_sa.email}"
}

# Store external Redis URL in Secret Manager
resource "google_secret_manager_secret" "redis_url" {
  secret_id = "redis-url-external"

  replication {
    auto {}
  }

  labels = var.labels

  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret_iam_member" "redis_url_access" {
  secret_id = google_secret_manager_secret.redis_url.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloudrun_sa.email}"
}

# Cloud Run service for API
resource "google_cloud_run_v2_service" "api" {
  name     = "copy-that-api-minimal"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.cloudrun_sa.email

    scaling {
      min_instance_count = 0  # Zero cost when idle!
      max_instance_count = 5  # Limit for personal use
    }

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}/copy-that-api:latest"

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
        cpu_idle          = true
        startup_cpu_boost = true
      }

      ports {
        name           = "http1"
        container_port = 8080
      }

      env {
        name  = "ENVIRONMENT"
        value = "demo"
      }

      env {
        name  = "LOG_LEVEL"
        value = "INFO"
      }

      env {
        name = "DATABASE_URL"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.database_url.secret_id
            version = "latest"
          }
        }
      }

      env {
        name = "REDIS_URL"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.redis_url.secret_id
            version = "latest"
          }
        }
      }

      startup_probe {
        http_get {
          path = "/health"
          port = 8080
        }
        initial_delay_seconds = 0
        timeout_seconds       = 1
        period_seconds        = 3
        failure_threshold     = 10
      }

      liveness_probe {
        http_get {
          path = "/health"
          port = 8080
        }
        initial_delay_seconds = 0
        timeout_seconds       = 1
        period_seconds        = 10
        failure_threshold     = 3
      }
    }

    timeout                          = "300s"
    max_instance_request_concurrency = 80
    execution_environment            = "EXECUTION_ENVIRONMENT_GEN2"
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  labels = var.labels

  depends_on = [
    google_artifact_registry_repository.docker_repo
  ]
}

# Allow public access (for family/friends)
resource "google_cloud_run_service_iam_member" "public_access" {
  location = google_cloud_run_v2_service.api.location
  service  = google_cloud_run_v2_service.api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Outputs
output "api_url" {
  description = "Public URL for your Copy That demo (share with family/friends!)"
  value       = google_cloud_run_v2_service.api.uri
}

output "artifact_registry_url" {
  description = "Docker repository URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}"
}

output "workload_identity_provider" {
  description = "Workload Identity Provider for GitHub Actions"
  value       = google_iam_workload_identity_pool_provider.github.name
}

output "service_account_email" {
  description = "Service Account for Cloud Build"
  value       = google_service_account.cloudbuild_sa.email
}

output "setup_instructions" {
  description = "Next steps to complete setup"
  value       = <<-EOT

  🎉 Infrastructure created successfully!

  Next steps:

  1. Create free accounts:
     - Neon.tech (Postgres): https://neon.tech
     - Upstash (Redis): https://upstash.com

  2. Add database URLs to secrets:
     echo "postgresql://user:pass@host/db" | gcloud secrets versions add database-url-external --data-file=-
     echo "redis://default:pass@host:port" | gcloud secrets versions add redis-url-external --data-file=-

  3. Build and deploy:
     gcloud builds submit --tag ${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}/copy-that-api:latest

  4. Share with friends:
     ${google_cloud_run_v2_service.api.uri}

  💰 Estimated cost: $0-5/month (only when used)
  EOT
}

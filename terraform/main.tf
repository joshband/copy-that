# ============================================
# Artifact Registry (Docker Image Storage)
# ============================================

resource "google_artifact_registry_repository" "docker_repo" {
  location      = var.region
  repository_id = var.artifact_registry_name
  description   = "Docker repository for Copy That API"
  format        = "DOCKER"
  labels        = var.labels

  depends_on = [
    google_project_service.artifact_registry
  ]
}

# ============================================
# Cloud Run Service
# ============================================

resource "google_cloud_run_service" "api" {
  name     = var.service_name
  location = var.region

  template {
    spec {
      service_account_name = google_service_account.cloud_run.email
      timeout_seconds      = var.cloud_run_timeout
      container_concurrency = 80

      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_registry_name}/copy-that-api:${var.image_tag}"

        resources {
          limits = {
            cpu    = var.cloud_run_cpu
            memory = "${var.cloud_run_memory}Mi"
          }
        }

        # Environment variables
        env {
          name  = "ENVIRONMENT"
          value = var.environment
        }

        env {
          name  = "DATABASE_URL"
          value = var.database_url
        }

        env {
          name  = "ANTHROPIC_API_KEY"
          value = var.anthropic_api_key
        }

        env {
          name  = "ALLOWED_ORIGINS"
          value = var.allowed_origins
        }

        env {
          name  = "LOG_LEVEL"
          value = var.log_level
        }

        # Health check
        liveness_probe {
          http_get {
            path = "/health"
            port = 8000
          }
          initial_delay_seconds = 5
          timeout_seconds       = 3
          period_seconds        = 30
          failure_threshold     = 3
        }

        startup_probe {
          http_get {
            path = "/health"
            port = 8000
          }
          initial_delay_seconds = 0
          timeout_seconds       = 3
          period_seconds        = 10
          failure_threshold     = 3
        }
      }
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = var.cloud_run_min_instances
        "autoscaling.knative.dev/maxScale" = var.cloud_run_max_instances
      }
      labels = var.labels
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [
    google_project_service.cloud_run,
    google_service_account_iam_binding.cloud_run_logging,
  ]
}

# ============================================
# Cloud Run IAM (Public Access)
# ============================================

resource "google_cloud_run_service_iam_binding" "public" {
  count   = var.allow_unauthenticated ? 1 : 0
  service = google_cloud_run_service.api.name
  location = var.region
  role    = "roles/run.invoker"

  members = ["allUsers"]
}

# ============================================
# Service Account
# ============================================

resource "google_service_account" "cloud_run" {
  account_id   = "${var.service_name}-sa"
  display_name = "Service account for ${var.service_name}"
}

# Grant Cloud Run logging permissions
resource "google_project_iam_member" "cloud_run_logging" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

resource "google_service_account_iam_binding" "cloud_run_logging" {
  service_account_id = google_service_account.cloud_run.name
  role               = "roles/logging.logWriter"
  members = [
    "serviceAccount:${google_service_account.cloud_run.email}"
  ]
}

# ============================================
# Enable Required APIs
# ============================================

resource "google_project_service" "cloud_run" {
  service            = "run.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "artifact_registry" {
  service            = "artifactregistry.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "container_registry" {
  service            = "containerregistry.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "cloud_build" {
  service            = "cloudbuild.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "cloud_logging" {
  service            = "logging.googleapis.com"
  disable_on_destroy = false
}

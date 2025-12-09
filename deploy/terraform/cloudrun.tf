# Cloud Run service for API
resource "google_cloud_run_v2_service" "api" {
  name     = "copy-that-api-${var.environment}"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.cloudrun_sa.email

    vpc_access {
      connector = google_vpc_access_connector.connector.id
      egress    = "PRIVATE_RANGES_ONLY"
    }

    scaling {
      min_instance_count = var.cloudrun_min_instances
      max_instance_count = var.cloudrun_max_instances
    }

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}/copy-that-api:latest"

      resources {
        limits = {
          cpu    = var.cloudrun_cpu
          memory = var.cloudrun_memory
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
        value = var.environment
      }

      env {
        name  = "LOG_LEVEL"
        value = var.environment == "production" ? "INFO" : "DEBUG"
      }

      env {
        name  = "PROJECT_ID"
        value = var.project_id
      }

      # DATABASE_URL and REDIS_URL should be set via GitHub Actions secrets
      # These come from Neon (managed separately) not Cloud SQL

      # Startup probe
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

      # Liveness probe
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

    # Timeout for requests
    timeout = "300s"

    # Max concurrent requests per instance
    max_instance_request_concurrency = var.cloudrun_concurrency

    # Execution environment
    execution_environment = "EXECUTION_ENVIRONMENT_GEN2"
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  labels = var.labels

  depends_on = [
    google_vpc_access_connector.connector,
    google_artifact_registry_repository.docker_repo
  ]
}

# IAM policy to allow public access (adjust for production)
resource "google_cloud_run_service_iam_member" "public_access" {
  count    = var.environment == "staging" ? 1 : 0
  location = google_cloud_run_v2_service.api.location
  service  = google_cloud_run_v2_service.api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Cloud Run job for database migrations
resource "google_cloud_run_v2_job" "migrations" {
  name     = "copy-that-migrations-${var.environment}"
  location = var.region

  template {
    template {
      service_account = google_service_account.cloudrun_sa.email

      vpc_access {
        connector = google_vpc_access_connector.connector.id
        egress    = "PRIVATE_RANGES_ONLY"
      }

      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}/copy-that-api:latest"

        command = ["alembic", "upgrade", "head"]

        resources {
          limits = {
            cpu    = "1"
            memory = "512Mi"
          }
        }

        env {
          name  = "ENVIRONMENT"
          value = var.environment
        }

        # DATABASE_URL should be set via GitHub Actions secrets
        # Comes from Neon (managed separately)
      }

      timeout = "600s"
    }
  }

  labels = var.labels

  depends_on = [
    google_cloud_run_v2_service.api
  ]
}

# Scheduled job for cleanup tasks (optional)
resource "google_cloud_scheduler_job" "cleanup" {
  name             = "copy-that-cleanup-${var.environment}"
  description      = "Daily cleanup of old data"
  schedule         = "0 2 * * *" # 2 AM daily
  time_zone        = "America/New_York"
  attempt_deadline = "600s"

  http_target {
    http_method = "POST"
    uri         = "${google_cloud_run_v2_service.api.uri}/api/v1/admin/cleanup"

    oidc_token {
      service_account_email = google_service_account.cloudrun_sa.email
    }
  }

  retry_config {
    retry_count = 3
  }

  depends_on = [
    google_project_service.apis,
    google_cloud_run_v2_service.api
  ]
}

# Outputs
output "cloudrun_url" {
  description = "Cloud Run service URL"
  value       = google_cloud_run_v2_service.api.uri
}

output "cloudrun_service_name" {
  description = "Cloud Run service name"
  value       = google_cloud_run_v2_service.api.name
}

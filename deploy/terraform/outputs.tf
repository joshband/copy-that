# Consolidated outputs file

# Service URLs
output "api_url" {
  description = "Copy That API URL"
  value       = google_cloud_run_v2_service.api.uri
}

# Infrastructure
output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}

output "region" {
  description = "GCP Region"
  value       = var.region
}

output "environment" {
  description = "Environment name"
  value       = var.environment
}

# Artifact Registry
output "docker_repository" {
  description = "Full Docker repository path"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}"
}

# Database - NOT USED (using Neon instead of Cloud SQL)
# output "database_connection" {
#   description = "Cloud SQL connection name (for Cloud SQL Proxy)"
#   value       = google_sql_database_instance.postgres.connection_name
# }
#
# output "database_name" {
#   description = "Database name"
#   value       = google_sql_database.database.name
# }
#
# # Redis - NOT USED
# output "redis_url_internal" {
#   description = "Internal Redis connection string"
#   value       = "redis://${google_redis_instance.redis.host}:${google_redis_instance.redis.port}/0"
#   sensitive   = true
# }

# Service Accounts
output "cloudrun_service_account" {
  description = "Cloud Run service account email"
  value       = google_service_account.cloudrun_sa.email
}

output "cloudbuild_service_account" {
  description = "Cloud Build service account email"
  value       = google_service_account.cloudbuild_sa.email
}

# GitHub Actions Integration
output "workload_identity_pool" {
  description = "Workload Identity Pool for GitHub Actions"
  value       = google_iam_workload_identity_pool.github.name
}

output "workload_identity_provider_name" {
  description = "Full Workload Identity Provider resource name"
  value       = google_iam_workload_identity_pool_provider.github.name
}

# Networking
output "vpc_network" {
  description = "VPC network name"
  value       = google_compute_network.vpc.name
}

output "vpc_connector" {
  description = "VPC Access Connector name"
  value       = google_vpc_access_connector.connector.name
}

# Secrets - NOT USED (DATABASE_URL/REDIS_URL come from GitHub Actions secrets)
# output "database_secret_name" {
#   description = "Secret Manager secret name for database URL"
#   value       = google_secret_manager_secret.database_url.secret_id
# }
#
# output "redis_secret_name" {
#   description = "Secret Manager secret name for Redis URL"
#   value       = google_secret_manager_secret.redis_url.secret_id
# }

# Jobs
output "migration_job_name" {
  description = "Cloud Run job name for migrations"
  value       = google_cloud_run_v2_job.migrations.name
}

# Monitoring (if enabled)
output "logs_url" {
  description = "Cloud Logging URL for this project"
  value       = "https://console.cloud.google.com/logs/query?project=${var.project_id}"
}

output "monitoring_url" {
  description = "Cloud Monitoring URL for this project"
  value       = "https://console.cloud.google.com/monitoring?project=${var.project_id}"
}

# Quick reference commands
output "helpful_commands" {
  description = "Helpful commands for managing the deployment"
  value = {
    deploy_cloudrun  = "gcloud run deploy ${google_cloud_run_v2_service.api.name} --region ${var.region} --image ${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}/copy-that-api:latest"
    run_migrations   = "gcloud run jobs execute ${google_cloud_run_v2_job.migrations.name} --region ${var.region} --wait"
    view_logs        = "gcloud run services logs read ${google_cloud_run_v2_service.api.name} --region ${var.region} --limit 50"
    describe_service = "gcloud run services describe ${google_cloud_run_v2_service.api.name} --region ${var.region}"
    # Database connection managed via Neon - see https://neon.tech
  }
}

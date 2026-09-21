# Neon Database Configuration
# Provider: https://registry.terraform.io/providers/kislerdm/neon/latest/docs
# Note: Neon provider is configured in main.tf required_providers block

provider "neon" {
  api_key = var.neon_api_key
}

# Main Neon Project
resource "neon_project" "copy_that" {
  name      = "copy-that-${var.environment}"
  region_id = "aws-us-east-2"  # Match your current Neon region

  # PostgreSQL version
  pg_version = 17

  # Compute settings
  compute_settings = {
    min = 0.25  # Scale to zero for cost savings
    max = 1.0   # Sufficient for staging/testing
  }

  # Branch protection
  branch_protection_limits = {
    # Prevent accidental deletion of main branch
    protected_branches = ["main"]
  }

  # Lifecycle management
  lifecycle {
    prevent_destroy = true  # Prevent accidental terraform destroy
  }
}

# Main branch (production data)
resource "neon_branch" "main" {
  project_id = neon_project.copy_that.id
  name       = "main"
}

# CI/Testing branch (ephemeral test data)
resource "neon_branch" "ci_test" {
  project_id = neon_project.copy_that.id
  parent_id  = neon_branch.main.id
  name       = "ci-testing"

  # Lifecycle - can be recreated
  lifecycle {
    prevent_destroy = false
  }
}

# Staging branch (for staging environment)
resource "neon_branch" "staging" {
  count      = var.environment == "staging" ? 1 : 0
  project_id = neon_project.copy_that.id
  parent_id  = neon_branch.main.id
  name       = "staging"
}

# Database on CI testing branch
resource "neon_database" "ci_test" {
  project_id = neon_project.copy_that.id
  branch_id  = neon_branch.ci_test.id
  name       = "copy_that_test"
  owner_name = "neondb_owner"
}

# Database role (optional - uses default neondb_owner)
resource "neon_role" "app_user" {
  project_id = neon_project.copy_that.id
  branch_id  = neon_branch.main.id
  name       = "copy_that_app"
}

# Endpoint for main branch (read-write)
resource "neon_endpoint" "main_rw" {
  project_id = neon_project.copy_that.id
  branch_id  = neon_branch.main.id
  type       = "read_write"

  # Autoscaling
  autoscaling_limit_min_cu = 0.25
  autoscaling_limit_max_cu = 1.0

  # Auto-suspend after inactivity
  suspend_timeout_seconds = 300  # 5 minutes
}

# Outputs
output "neon_project_id" {
  description = "Neon project ID"
  value       = neon_project.copy_that.id
}

output "neon_main_branch_id" {
  description = "Main branch ID"
  value       = neon_branch.main.id
}

output "neon_ci_test_branch_id" {
  description = "CI test branch ID"
  value       = neon_branch.ci_test.id
}

output "neon_database_host" {
  description = "Database host"
  value       = neon_endpoint.main_rw.host
  sensitive   = true
}

output "neon_connection_string_ci" {
  description = "Connection string for CI tests"
  value       = "postgresql+asyncpg://${neon_project.copy_that.database_user}:${neon_project.copy_that.database_password}@${neon_endpoint.main_rw.host}/${neon_database.ci_test.name}"
  sensitive   = true
}

output "neon_connection_string_main" {
  description = "Connection string for main branch"
  value       = "postgresql+asyncpg://${neon_project.copy_that.database_user}:${neon_project.copy_that.database_password}@${neon_endpoint.main_rw.host}/neondb"
  sensitive   = true
}

# Store Neon connection string in Secret Manager
resource "google_secret_manager_secret" "neon_database_url" {
  secret_id = "neon-database-url-${var.environment}"

  replication {
    auto {}
  }

  labels = var.labels

  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret_version" "neon_database_url" {
  secret = google_secret_manager_secret.neon_database_url.id

  secret_data = neon_branch.ci_test != null ? (
    "postgresql+asyncpg://${neon_project.copy_that.database_user}:${neon_project.copy_that.database_password}@${neon_endpoint.main_rw.host}/${neon_database.ci_test.name}"
  ) : (
    "postgresql+asyncpg://${neon_project.copy_that.database_user}:${neon_project.copy_that.database_password}@${neon_endpoint.main_rw.host}/neondb"
  )
}

# Grant Cloud Run access to Neon secret
resource "google_secret_manager_secret_iam_member" "cloudrun_neon_access" {
  secret_id = google_secret_manager_secret.neon_database_url.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloudrun_sa.email}"
}

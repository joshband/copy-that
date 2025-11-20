# Redis (Memorystore) instance
resource "google_redis_instance" "redis" {
  name               = "copy-that-redis-${var.environment}"
  tier               = var.redis_tier
  memory_size_gb     = var.redis_memory_size_gb
  region             = var.region
  redis_version      = "REDIS_7_0"
  display_name       = "Copy That Redis ${title(var.environment)}"
  reserved_ip_range  = "10.2.0.0/29"
  connect_mode       = "PRIVATE_SERVICE_ACCESS"
  authorized_network = google_compute_network.vpc.id

  redis_configs = {
    maxmemory-policy = "allkeys-lru"
    notify-keyspace-events = "Ex"
  }

  maintenance_policy {
    weekly_maintenance_window {
      day = "SUNDAY"
      start_time {
        hours   = 3
        minutes = 0
        seconds = 0
        nanos   = 0
      }
    }
  }

  labels = var.labels

  depends_on = [
    google_service_networking_connection.private_vpc_connection
  ]
}

# Store Redis URL in Secret Manager
resource "google_secret_manager_secret" "redis_url" {
  secret_id = "redis-url-${var.environment}"

  replication {
    auto {}
  }

  labels = var.labels

  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret_version" "redis_url" {
  secret      = google_secret_manager_secret.redis_url.id
  secret_data = "redis://${google_redis_instance.redis.host}:${google_redis_instance.redis.port}/0"
}

# Grant Cloud Run SA access to secret
resource "google_secret_manager_secret_iam_member" "redis_url_access" {
  secret_id = google_secret_manager_secret.redis_url.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloudrun_sa.email}"
}

# Outputs
output "redis_host" {
  description = "Redis host"
  value       = google_redis_instance.redis.host
}

output "redis_port" {
  description = "Redis port"
  value       = google_redis_instance.redis.port
}

output "redis_connection_string" {
  description = "Redis connection string"
  value       = "redis://${google_redis_instance.redis.host}:${google_redis_instance.redis.port}/0"
  sensitive   = true
}

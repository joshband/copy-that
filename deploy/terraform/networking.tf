# VPC Network
resource "google_compute_network" "vpc" {
  name                    = "copy-that-vpc-${var.environment}"
  auto_create_subnetworks = false
  routing_mode            = "REGIONAL"

  depends_on = [google_project_service.apis]
}

# Subnet for Cloud Run and other services
resource "google_compute_subnetwork" "subnet" {
  name          = "copy-that-subnet-${var.environment}"
  ip_cidr_range = var.vpc_cidr
  region        = var.region
  network       = google_compute_network.vpc.id

  private_ip_google_access = true

  log_config {
    aggregation_interval = "INTERVAL_10_MIN"
    flow_sampling        = 0.5
    metadata             = "INCLUDE_ALL_METADATA"
  }
}

# VPC Access Connector for Cloud Run to access VPC resources
resource "google_vpc_access_connector" "connector" {
  name          = "copy-that-connector-${var.environment}"
  region        = var.region
  network       = google_compute_network.vpc.name
  ip_cidr_range = "10.8.0.0/28"

  min_instances = 2
  max_instances = 3

  machine_type = "e2-micro"

  depends_on = [
    google_project_service.apis,
    google_compute_network.vpc
  ]
}

# Private Service Connection for Cloud SQL - NOT NEEDED (using Neon)
# Commented out to avoid unnecessary resource creation
# Uncomment if you need private GCP services in the future
#
# resource "google_compute_global_address" "private_ip_address" {
#   name          = "copy-that-private-ip-${var.environment}"
#   purpose       = "VPC_PEERING"
#   address_type  = "INTERNAL"
#   prefix_length = 16
#   network       = google_compute_network.vpc.id
#
#   depends_on = [google_compute_network.vpc]
# }
#
# resource "google_service_networking_connection" "private_vpc_connection" {
#   network                 = google_compute_network.vpc.id
#   service                 = "servicenetworking.googleapis.com"
#   reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]
#
#   depends_on = [
#     google_project_service.apis,
#     google_compute_global_address.private_ip_address
#   ]
# }

# Cloud NAT for outbound internet access
resource "google_compute_router" "router" {
  name    = "copy-that-router-${var.environment}"
  region  = var.region
  network = google_compute_network.vpc.id

  bgp {
    asn = 64514
  }
}

resource "google_compute_router_nat" "nat" {
  name                               = "copy-that-nat-${var.environment}"
  router                             = google_compute_router.router.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# Firewall rules
resource "google_compute_firewall" "allow_health_check" {
  name    = "copy-that-allow-health-check-${var.environment}"
  network = google_compute_network.vpc.name

  allow {
    protocol = "tcp"
    ports    = ["8080"]
  }

  source_ranges = ["130.211.0.0/22", "35.191.0.0/16"] # Google health check ranges
  target_tags   = ["copy-that-cloudrun"]
}

resource "google_compute_firewall" "allow_internal" {
  name    = "copy-that-allow-internal-${var.environment}"
  network = google_compute_network.vpc.name

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "icmp"
  }

  source_ranges = [var.vpc_cidr]
}

# Outputs
output "vpc_name" {
  description = "VPC network name"
  value       = google_compute_network.vpc.name
}

output "vpc_connector_name" {
  description = "VPC Access Connector name"
  value       = google_vpc_access_connector.connector.name
}

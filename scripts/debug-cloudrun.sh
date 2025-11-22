#!/bin/bash
# Cloud Run Debugging Script
# Helps diagnose issues with Cloud Run deployments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
PROJECT_ID="${GCP_PROJECT_ID:-copy-that-platform}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="${CLOUD_RUN_SERVICE:-copy-that-api}"

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"

    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI not found. Please install: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    print_success "gcloud CLI found"

    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_error "Not authenticated with gcloud. Run: gcloud auth login"
        exit 1
    fi
    print_success "gcloud authenticated"

    gcloud config set project "$PROJECT_ID" 2>/dev/null
    print_success "Project set to: $PROJECT_ID"
}

# Get service info
get_service_info() {
    print_header "Cloud Run Service Information"

    echo "Fetching service details for: $SERVICE_NAME"

    if gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="yaml" 2>/dev/null; then
        print_success "Service found"
    else
        print_error "Service not found: $SERVICE_NAME in region $REGION"
        echo "Available services:"
        gcloud run services list --region="$REGION" --format="table(SERVICE,REGION,URL,LAST_DEPLOYED)"
        return 1
    fi
}

# Check service revisions
check_revisions() {
    print_header "Service Revisions"

    echo "Recent revisions:"
    gcloud run revisions list \
        --service="$SERVICE_NAME" \
        --region="$REGION" \
        --format="table(REVISION,ACTIVE,SERVICE,DEPLOYED,STATUS)" \
        --limit=10
}

# Get service logs
get_logs() {
    local LOG_LIMIT="${1:-100}"
    local SEVERITY="${2:-DEFAULT}"

    print_header "Cloud Run Logs (Last $LOG_LIMIT entries)"

    echo "Fetching logs..."
    gcloud logging read \
        "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=$SEVERITY" \
        --limit="$LOG_LIMIT" \
        --format="table(timestamp,severity,textPayload)" \
        --project="$PROJECT_ID"
}

# Get error logs specifically
get_error_logs() {
    print_header "Error Logs (Last 50 entries)"

    gcloud logging read \
        "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" \
        --limit=50 \
        --format="json" \
        --project="$PROJECT_ID" | jq -r '.[] | "\(.timestamp) [\(.severity)] \(.textPayload // .jsonPayload)"'
}

# Check health endpoint
check_health() {
    print_header "Health Check"

    local SERVICE_URL
    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(status.url)" 2>/dev/null)

    if [ -z "$SERVICE_URL" ]; then
        print_error "Could not get service URL"
        return 1
    fi

    print_info "Service URL: $SERVICE_URL"

    echo -e "\nTesting /health endpoint..."
    if curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL/health" | grep -q "200"; then
        print_success "Health check passed (200 OK)"
        echo "Response:"
        curl -s "$SERVICE_URL/health" | jq .
    else
        print_error "Health check failed"
        echo "Response:"
        curl -s -w "\nHTTP Status: %{http_code}\n" "$SERVICE_URL/health"
    fi

    echo -e "\nTesting /api/v1/status endpoint..."
    curl -s "$SERVICE_URL/api/v1/status" | jq .
}

# Check environment variables (secrets redacted)
check_env_vars() {
    print_header "Environment Variables (Secrets Redacted)"

    gcloud run services describe "$SERVICE_NAME" \
        --region="$REGION" \
        --format="yaml(spec.template.spec.containers[0].env)" 2>/dev/null | \
        sed 's/\(.*_KEY\|.*_SECRET\|.*_PASSWORD\|.*DATABASE_URL\|.*REDIS_URL\):.*/\1: [REDACTED]/'
}

# Check IAM permissions
check_iam() {
    print_header "IAM Policy"

    gcloud run services get-iam-policy "$SERVICE_NAME" \
        --region="$REGION" \
        --format="yaml"
}

# Check container metrics
check_metrics() {
    print_header "Recent Metrics Summary"

    echo "Container instance count:"
    gcloud monitoring metrics list \
        --filter="metric.type=run.googleapis.com/container/instance_count" \
        --format="table(name,description)" 2>/dev/null || echo "Metrics API may not be enabled"
}

# Build and deploy debug image
deploy_debug_image() {
    print_header "Building and Deploying Debug Image"

    local IMAGE_TAG="debug-$(date +%Y%m%d-%H%M%S)"
    local IMAGE_URL="$REGION-docker.pkg.dev/$PROJECT_ID/copy-that/copy-that-api:$IMAGE_TAG"

    print_info "Building debug image: $IMAGE_URL"

    # Build the debug image
    docker build -f Dockerfile.debug --target cloudrun-debug -t "$IMAGE_URL" .

    # Push to Artifact Registry
    print_info "Pushing to Artifact Registry..."
    docker push "$IMAGE_URL"

    # Deploy to Cloud Run
    print_info "Deploying to Cloud Run..."
    gcloud run deploy "$SERVICE_NAME-debug" \
        --image="$IMAGE_URL" \
        --region="$REGION" \
        --platform=managed \
        --allow-unauthenticated \
        --memory=1Gi \
        --cpu=1 \
        --min-instances=0 \
        --max-instances=2 \
        --set-env-vars="LOG_LEVEL=DEBUG,DEBUG=true"

    print_success "Debug service deployed: $SERVICE_NAME-debug"
}

# Execute SQL query via Cloud Run
test_database() {
    print_header "Database Connectivity Test"

    local SERVICE_URL
    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(status.url)" 2>/dev/null)

    if [ -z "$SERVICE_URL" ]; then
        print_error "Could not get service URL"
        return 1
    fi

    echo "Testing database connection via API..."
    curl -s "$SERVICE_URL/api/v1/db-test" | jq .
}

# Stream logs in real-time
stream_logs() {
    print_header "Streaming Logs (Ctrl+C to stop)"

    gcloud logging tail \
        "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" \
        --format="table(timestamp,severity,textPayload)"
}

# Show usage
usage() {
    echo "Cloud Run Debugging Script"
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  info          Get service information"
    echo "  revisions     List service revisions"
    echo "  logs [n]      Get last n logs (default: 100)"
    echo "  errors        Get error logs"
    echo "  stream        Stream logs in real-time"
    echo "  health        Check health endpoints"
    echo "  env           Show environment variables"
    echo "  iam           Show IAM policy"
    echo "  metrics       Show metrics summary"
    echo "  db            Test database connectivity"
    echo "  deploy-debug  Build and deploy debug image"
    echo "  all           Run all diagnostic checks"
    echo ""
    echo "Environment Variables:"
    echo "  GCP_PROJECT_ID     GCP project (default: copy-that-platform)"
    echo "  GCP_REGION         GCP region (default: us-central1)"
    echo "  CLOUD_RUN_SERVICE  Service name (default: copy-that-api)"
    echo ""
    echo "Examples:"
    echo "  $0 logs 200"
    echo "  $0 health"
    echo "  CLOUD_RUN_SERVICE=copy-that-api-staging $0 info"
}

# Main execution
main() {
    local COMMAND="${1:-all}"

    check_prerequisites

    case "$COMMAND" in
        info)
            get_service_info
            ;;
        revisions)
            check_revisions
            ;;
        logs)
            get_logs "${2:-100}"
            ;;
        errors)
            get_error_logs
            ;;
        stream)
            stream_logs
            ;;
        health)
            check_health
            ;;
        env)
            check_env_vars
            ;;
        iam)
            check_iam
            ;;
        metrics)
            check_metrics
            ;;
        db)
            test_database
            ;;
        deploy-debug)
            deploy_debug_image
            ;;
        all)
            get_service_info
            check_revisions
            check_health
            check_env_vars
            get_logs 50
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            print_error "Unknown command: $COMMAND"
            usage
            exit 1
            ;;
    esac
}

main "$@"

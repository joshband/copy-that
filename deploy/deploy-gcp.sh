#!/bin/bash
# Copy That - GCP Deployment Script
# Project: copy-that-platform

set -e

PROJECT_ID="copy-that-platform"
REGION="us-central1"
STATE_BUCKET="copy-that-terraform-state"

echo "================================================"
echo "Copy That - GCP Deployment"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "================================================"
echo ""

# Check if gcloud is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n1 > /dev/null 2>&1; then
    echo "ERROR: Not authenticated with gcloud. Run: gcloud auth login"
    exit 1
fi

# Set project
echo "1. Setting GCP project..."
gcloud config set project $PROJECT_ID

# Create Terraform state bucket
echo ""
echo "2. Creating Terraform state bucket..."
if ! gsutil ls -b gs://$STATE_BUCKET > /dev/null 2>&1; then
    gsutil mb -p $PROJECT_ID -l $REGION gs://$STATE_BUCKET
    gsutil versioning set on gs://$STATE_BUCKET
    echo "   Created bucket: gs://$STATE_BUCKET"
else
    echo "   Bucket already exists: gs://$STATE_BUCKET"
fi

# Enable required APIs
echo ""
echo "3. Enabling required APIs..."
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    sqladmin.googleapis.com \
    redis.googleapis.com \
    secretmanager.googleapis.com \
    vpcaccess.googleapis.com \
    compute.googleapis.com \
    servicenetworking.googleapis.com \
    cloudresourcemanager.googleapis.com \
    iam.googleapis.com \
    cloudbuild.googleapis.com \
    --quiet

echo "   APIs enabled successfully"

# Create secrets
echo ""
echo "4. Creating secrets in Secret Manager..."
echo ""

# Anthropic API Key
if ! gcloud secrets describe anthropic-api-key > /dev/null 2>&1; then
    echo "   Creating anthropic-api-key secret..."
    read -sp "   Enter your Anthropic API key: " ANTHROPIC_KEY
    echo ""
    echo -n "$ANTHROPIC_KEY" | gcloud secrets create anthropic-api-key --data-file=- --replication-policy="automatic"
    echo "   Created anthropic-api-key"
else
    echo "   anthropic-api-key already exists"
fi

# Secret key for JWT
if ! gcloud secrets describe app-secret-key > /dev/null 2>&1; then
    echo "   Creating app-secret-key secret..."
    openssl rand -hex 32 | gcloud secrets create app-secret-key --data-file=- --replication-policy="automatic"
    echo "   Created app-secret-key"
else
    echo "   app-secret-key already exists"
fi

# Terraform deployment
echo ""
echo "5. Running Terraform..."
cd "$(dirname "$0")/terraform"

terraform init
terraform plan -out=tfplan
echo ""
read -p "   Apply this plan? (yes/no): " APPLY
if [ "$APPLY" = "yes" ]; then
    terraform apply tfplan
    echo ""
    echo "   Terraform apply complete!"
else
    echo "   Skipping Terraform apply"
fi

# Build and push Docker image
echo ""
echo "6. Building and pushing Docker image..."
cd ../..

# Get the Artifact Registry repository URL
REPO_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/copy-that/api"

# Build with Cloud Build
gcloud builds submit --tag $REPO_URL:latest .

echo ""
echo "================================================"
echo "Deployment Complete!"
echo "================================================"
echo ""
echo "Cloud Run URL will be displayed above after deployment."
echo ""
echo "Next steps:"
echo "1. Test the API health endpoint: curl <CLOUD_RUN_URL>/health"
echo "2. Test color extraction: POST <CLOUD_RUN_URL>/api/v1/colors/extract"
echo ""
echo "To view logs:"
echo "  gcloud logging read 'resource.type=cloud_run_revision' --limit 50"
echo ""
echo "To update the deployment:"
echo "  cd deploy && ./deploy-gcp.sh"
echo ""

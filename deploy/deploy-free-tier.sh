#!/bin/bash
# Copy That - Free Tier Deployment
# Uses: Neon (Postgres), Upstash (Redis), Cloud Run (free tier)
# Total cost: $0/month

set -e

PROJECT_ID="copy-that-platform"
REGION="us-central1"
SERVICE_NAME="copy-that-api"

echo "================================================"
echo "Copy That - Free Tier Deployment"
echo "================================================"
echo ""
echo "This deployment uses:"
echo "  - Neon Postgres (free tier)"
echo "  - Upstash Redis (already configured)"
echo "  - Cloud Run (2M requests/month free)"
echo ""

# Check gcloud
if ! command -v gcloud &> /dev/null; then
    echo "ERROR: gcloud CLI not installed"
    echo "Install: brew install google-cloud-sdk"
    exit 1
fi

# Set project
echo "1. Setting GCP project..."
gcloud config set project $PROJECT_ID

# Enable required APIs (just Cloud Run and Artifact Registry)
echo ""
echo "2. Enabling APIs..."
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com \
    cloudbuild.googleapis.com \
    --quiet

# Create Artifact Registry repository
echo ""
echo "3. Creating Docker repository..."
if ! gcloud artifacts repositories describe copy-that --location=$REGION > /dev/null 2>&1; then
    gcloud artifacts repositories create copy-that \
        --repository-format=docker \
        --location=$REGION \
        --description="Copy That Docker images"
fi

# Get secrets
echo ""
echo "4. Setting up secrets..."
echo ""

# Database URL (Neon) - check both possible secret names
if gcloud secrets describe database-url-external > /dev/null 2>&1; then
    echo "   database-url-external secret exists (using existing)"
    DB_SECRET_NAME="database-url-external"
elif gcloud secrets describe database-url > /dev/null 2>&1; then
    echo "   database-url secret exists"
    DB_SECRET_NAME="database-url"
else
    echo "   Enter your Neon database URL:"
    echo "   (e.g., postgresql://user:pass@ep-xxx.neon.tech/neondb?sslmode=require)"
    read -sp "   DATABASE_URL: " DATABASE_URL
    echo ""
    echo -n "$DATABASE_URL" | gcloud secrets create database-url --data-file=- --replication-policy="automatic"
    DB_SECRET_NAME="database-url"
fi

# OpenAI API Key (preferred for extraction)
if ! gcloud secrets describe openai-api-key > /dev/null 2>&1; then
    read -sp "   Enter your OpenAI API key: " OPENAI_KEY
    echo ""
    echo -n "$OPENAI_KEY" | gcloud secrets create openai-api-key --data-file=- --replication-policy="automatic"
else
    echo "   openai-api-key secret exists"
fi

# Redis URL - check for existing external secret
if gcloud secrets describe redis-url-external > /dev/null 2>&1; then
    echo "   redis-url-external secret exists (using existing)"
    REDIS_SECRET_NAME="redis-url-external"
elif gcloud secrets describe redis-url > /dev/null 2>&1; then
    echo "   redis-url secret exists"
    REDIS_SECRET_NAME="redis-url"
else
    REDIS_SECRET_NAME=""
    echo "   No Redis secret found (optional - will use in-memory caching)"
fi

# Secret key
if ! gcloud secrets describe app-secret-key > /dev/null 2>&1; then
    openssl rand -hex 32 | gcloud secrets create app-secret-key --data-file=- --replication-policy="automatic"
    echo "   Created app-secret-key"
else
    echo "   app-secret-key secret exists"
fi

# Build and deploy
echo ""
echo "5. Building Docker image..."
cd "$(dirname "$0")/.."

REPO_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/copy-that/api"
gcloud builds submit --tag $REPO_URL:latest .

echo ""
echo "6. Deploying to Cloud Run..."

# Build secrets string dynamically
SECRETS_STRING="DATABASE_URL=${DB_SECRET_NAME}:latest,OPENAI_API_KEY=openai-api-key:latest,SECRET_KEY=app-secret-key:latest"

# Add Redis if available
if [ -n "$REDIS_SECRET_NAME" ]; then
    SECRETS_STRING="${SECRETS_STRING},REDIS_URL=${REDIS_SECRET_NAME}:latest"
fi

echo "   Using secrets: $SECRETS_STRING"

gcloud run deploy $SERVICE_NAME \
    --image $REPO_URL:latest \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --set-secrets="$SECRETS_STRING" \
    --set-env-vars="ENVIRONMENT=staging,CORS_ORIGINS=*" \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 3 \
    --timeout 300

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format='value(status.url)')

echo ""
echo "================================================"
echo "Deployment Complete!"
echo "================================================"
echo ""
echo "API URL: $SERVICE_URL"
echo ""
echo "Test endpoints:"
echo "  Health: curl $SERVICE_URL/health"
echo "  Status: curl $SERVICE_URL/api/v1/status"
echo ""
echo "Cost: \$0/month (free tier)"
echo ""
echo "Note: Upstash Redis is already configured in staging config."
echo "If you need a new Upstash instance, create one at upstash.com"
echo ""

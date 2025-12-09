#!/bin/bash
# Test production Docker build locally before deploying
# Usage: ./scripts/test-production-build.sh

set -e

echo "🧪 Testing Production Build Locally"
echo "===================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Build production image
echo "📦 Step 1: Building production Docker image..."
docker build \
  --file Dockerfile \
  --target production \
  --tag copy-that:prod-test \
  --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
  --build-arg VCS_REF="$(git rev-parse --short HEAD)" \
  --build-arg VERSION="$(git describe --tags --always)" \
  .

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✅ Build successful${NC}"
else
  echo -e "${RED}❌ Build failed${NC}"
  exit 1
fi

# Step 2: Check image size
echo ""
echo "📊 Step 2: Checking image size..."
IMAGE_SIZE=$(docker images copy-that:prod-test --format "{{.Size}}")
echo "Image size: $IMAGE_SIZE"

# Step 3: Start production test environment
echo ""
echo "🚀 Step 3: Starting production test environment..."
docker-compose --profile prod-test up -d

# Wait for health check
echo ""
echo "⏳ Step 4: Waiting for health check..."
sleep 5

MAX_ATTEMPTS=10
ATTEMPT=0
while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health || echo "000")

  if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Health check passed (HTTP $HTTP_CODE)${NC}"
    break
  fi

  ATTEMPT=$((ATTEMPT + 1))
  echo "Attempt $ATTEMPT/$MAX_ATTEMPTS: HTTP $HTTP_CODE, retrying..."
  sleep 2
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
  echo -e "${RED}❌ Health check failed after $MAX_ATTEMPTS attempts${NC}"
  docker-compose --profile prod-test logs api-prod-test
  docker-compose --profile prod-test down
  exit 1
fi

# Step 5: Test API endpoints
echo ""
echo "🧪 Step 5: Testing API endpoints..."

# Test status endpoint
echo "Testing /api/v1/status..."
STATUS_RESPONSE=$(curl -s http://localhost:8080/api/v1/status)
if echo "$STATUS_RESPONSE" | jq . > /dev/null 2>&1; then
  echo -e "${GREEN}✅ Status endpoint working${NC}"
  echo "$STATUS_RESPONSE" | jq .
else
  echo -e "${RED}❌ Status endpoint failed${NC}"
fi

# Step 6: Check logs
echo ""
echo "📋 Step 6: Recent logs..."
docker-compose --profile prod-test logs --tail=20 api-prod-test

# Step 7: Summary
echo ""
echo "================================"
echo -e "${GREEN}✅ Production build test complete!${NC}"
echo "================================"
echo ""
echo "📊 Summary:"
echo "  - Image: copy-that:prod-test"
echo "  - Size: $IMAGE_SIZE"
echo "  - Port: http://localhost:8080"
echo "  - Health: ✅ Passing"
echo ""
echo "🧹 Cleanup:"
echo "  docker-compose --profile prod-test down"
echo "  docker rmi copy-that:prod-test"
echo ""
echo "🚀 Deploy when ready:"
echo "  git push origin main"
echo ""

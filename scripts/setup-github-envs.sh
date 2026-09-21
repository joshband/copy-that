#!/usr/bin/env bash
# Setup GitHub environments for Copy That
# Requires: gh CLI authenticated with repo admin access
# Usage: ./scripts/setup-github-envs.sh

set -e

echo "🔧 Setting up GitHub environments..."
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get repo info
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "")

if [[ -z "$REPO" ]]; then
    echo -e "${RED}❌ Could not determine repository. Make sure gh is authenticated.${NC}"
    echo "  Run: gh auth login"
    exit 1
fi

echo "Repository: $REPO"
echo ""

# Create staging environment
create_staging() {
    echo "📦 Creating 'staging' environment..."

    # Check if it exists
    if gh api "repos/$REPO/environments/staging" &>/dev/null; then
        echo -e "  ${YELLOW}⚠${NC} Environment 'staging' already exists"
    else
        gh api --method PUT "repos/$REPO/environments/staging" \
            -f deployment_branch_policy='{"protected_branches":false,"custom_branch_policies":true}' \
            &>/dev/null || true

        # Add branch policy for develop
        gh api --method POST "repos/$REPO/environments/staging/deployment-branch-policies" \
            -f name='develop' \
            &>/dev/null || true

        echo -e "  ${GREEN}✓${NC} Created 'staging' environment"
    fi
}

# Create production environment
create_production() {
    echo "📦 Creating 'production' environment..."

    if gh api "repos/$REPO/environments/production" &>/dev/null; then
        echo -e "  ${YELLOW}⚠${NC} Environment 'production' already exists"
    else
        gh api --method PUT "repos/$REPO/environments/production" \
            -f wait_timer=5 \
            -f deployment_branch_policy='{"protected_branches":false,"custom_branch_policies":true}' \
            &>/dev/null || true

        echo -e "  ${GREEN}✓${NC} Created 'production' environment"
    fi
}

# Setup branch protection
setup_branch_protection() {
    echo ""
    echo "🔒 Setting up branch protection..."

    # Main branch
    echo "  Configuring 'main' branch..."
    gh api --method PUT "repos/$REPO/branches/main/protection" \
        -f required_status_checks='{"strict":true,"contexts":["lint","type-check","unit-tests-fast"]}' \
        -f enforce_admins=false \
        -f required_pull_request_reviews='{"required_approving_review_count":1}' \
        -f restrictions=null \
        &>/dev/null || echo -e "    ${YELLOW}⚠${NC} Could not set protection for main (may need admin access)"

    # Develop branch
    echo "  Configuring 'develop' branch..."
    gh api --method PUT "repos/$REPO/branches/develop/protection" \
        -f required_status_checks='{"strict":true,"contexts":["lint","type-check","unit-tests-fast"]}' \
        -f enforce_admins=false \
        -f required_pull_request_reviews='{"required_approving_review_count":1}' \
        -f restrictions=null \
        &>/dev/null || echo -e "    ${YELLOW}⚠${NC} Could not set protection for develop (may need admin access)"

    echo -e "  ${GREEN}✓${NC} Branch protection configured"
}

# Print secrets needed
print_secrets_needed() {
    echo ""
    echo "=========================================="
    echo "📝 MANUAL STEPS REQUIRED"
    echo "=========================================="
    echo ""
    echo "Add these secrets to each environment:"
    echo "(Settings → Environments → [env] → Environment secrets)"
    echo ""
    echo "For 'staging':"
    echo "  GCP_PROJECT_ID     - Your GCP staging project"
    echo "  GCP_SA_KEY         - Service account JSON (base64)"
    echo "  DATABASE_URL       - Staging database URL"
    echo "  REDIS_URL          - Staging Redis URL"
    echo ""
    echo "For 'production':"
    echo "  GCP_PROJECT_ID     - Your GCP production project"
    echo "  GCP_SA_KEY         - Service account JSON (base64)"
    echo "  DATABASE_URL       - Production database URL"
    echo "  REDIS_URL          - Production Redis URL"
    echo ""
    echo "Optionally add reviewers:"
    echo "  Settings → Environments → production → Required reviewers"
    echo ""
}

# Main
main() {
    # Check gh is available
    if ! command -v gh &> /dev/null; then
        echo -e "${RED}❌ GitHub CLI (gh) not found${NC}"
        echo "  Install: https://cli.github.com/"
        exit 1
    fi

    # Check authenticated
    if ! gh auth status &>/dev/null; then
        echo -e "${RED}❌ GitHub CLI not authenticated${NC}"
        echo "  Run: gh auth login"
        exit 1
    fi

    create_staging
    create_production
    setup_branch_protection
    print_secrets_needed

    echo ""
    echo -e "${GREEN}✅ GitHub environments setup complete!${NC}"
    echo ""
    echo "View environments: https://github.com/$REPO/settings/environments"
}

main "$@"

#!/bin/bash
# Clean up merged remote branches for copy-that repository
# Run this AFTER you update your GitHub token permissions

set -e

REPO="joshband/copy-that"
MAIN_BRANCH="main"

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}GitHub Branch Cleanup Tool${NC}"
echo "Repository: $REPO"
echo ""

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI (gh) is not installed${NC}"
    echo "Install it from: https://cli.github.com"
    exit 1
fi

# Check authentication
echo -e "${YELLOW}Checking authentication...${NC}"
if ! gh auth status &> /dev/null; then
    echo -e "${RED}Error: Not authenticated with GitHub${NC}"
    echo "Run: gh auth login"
    exit 1
fi

echo -e "${GREEN}✓ Authenticated${NC}"
echo ""

# Check token permissions
echo -e "${YELLOW}Checking token permissions...${NC}"
TOKEN_SCOPES=$(gh auth status 2>&1 | grep -i "Token scopes" || echo "")
if [[ $TOKEN_SCOPES == *"repo"* ]]; then
    echo -e "${GREEN}✓ Token has 'repo' scope${NC}"
else
    echo -e "${RED}✗ Token missing 'repo' scope${NC}"
    echo ""
    echo "Your token needs write permissions. Update it at:"
    echo "  https://github.com/settings/tokens"
    echo ""
    echo "Or re-authenticate with: gh auth login"
    exit 1
fi
echo ""

# Get list of merged branches
echo -e "${YELLOW}Finding merged branches...${NC}"
git fetch origin
MERGED_BRANCHES=$(git branch -r --merged origin/$MAIN_BRANCH --list --no-column | \
    grep -v "origin/$MAIN_BRANCH\|origin/HEAD" | \
    sed 's/^  origin\///' | \
    sort)

if [ -z "$MERGED_BRANCHES" ]; then
    echo -e "${GREEN}✓ No merged branches found${NC}"
    exit 0
fi

BRANCH_COUNT=$(echo "$MERGED_BRANCHES" | wc -l)
echo -e "${YELLOW}Found $BRANCH_COUNT merged branches:${NC}"
echo ""
echo "$MERGED_BRANCHES" | nl
echo ""

# Ask for confirmation
read -p "Delete these branches? (y/N): " -r CONFIRM
if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo -e "${YELLOW}Deleting branches...${NC}"
DELETED=0
FAILED=0

while IFS= read -r BRANCH; do
    if [ -z "$BRANCH" ]; then
        continue
    fi

    echo -n "Deleting $BRANCH... "

    if gh api repos/$REPO/git/refs/heads/$BRANCH -X DELETE &> /dev/null; then
        echo -e "${GREEN}✓ Deleted${NC}"
        ((DELETED++))
    else
        echo -e "${RED}✗ Failed${NC}"
        ((FAILED++))
    fi
done <<< "$MERGED_BRANCHES"

echo ""
echo -e "${GREEN}Summary:${NC}"
echo "  Deleted: $DELETED"
if [ $FAILED -gt 0 ]; then
    echo -e "  ${RED}Failed: $FAILED${NC}"
fi

# Verify
echo ""
echo -e "${YELLOW}Verifying cleanup...${NC}"
git fetch origin
REMAINING=$(git branch -r --list | grep -v "origin/$MAIN_BRANCH\|origin/HEAD" | wc -l)
echo -e "${GREEN}Remaining remote branches: $REMAINING${NC}"

exit 0

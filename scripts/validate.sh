#!/bin/bash
# Quick validation script - run before committing
# Catches lint, type, and test errors early
# Usage: ./scripts/validate.sh

set -e

echo "🔍 Running Quick Validation"
echo "============================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track failures
FAILED=0

# Step 1: Ruff linting
echo "1️⃣  Running Ruff linter..."
if ruff check . ; then
  echo -e "${GREEN}✅ Ruff linting passed${NC}"
else
  echo -e "${RED}❌ Ruff linting failed${NC}"
  FAILED=1
fi
echo ""

# Step 2: Ruff formatting
echo "2️⃣  Checking Ruff formatting..."
if ruff format --check . ; then
  echo -e "${GREEN}✅ Code formatting is correct${NC}"
else
  echo -e "${YELLOW}⚠️  Code needs formatting - run: ruff format .${NC}"
  FAILED=1
fi
echo ""

# Step 3: Mypy type checking
echo "3️⃣  Running Mypy type checker..."
if mypy src/ ; then
  echo -e "${GREEN}✅ Type checking passed${NC}"
else
  echo -e "${RED}❌ Type checking failed${NC}"
  FAILED=1
fi
echo ""

# Step 4: Fast unit tests
echo "4️⃣  Running fast unit tests..."
if pytest tests/unit -x -q -m "not slow" --tb=line ; then
  echo -e "${GREEN}✅ Unit tests passed${NC}"
else
  echo -e "${RED}❌ Unit tests failed${NC}"
  FAILED=1
fi
echo ""

# Summary
echo "============================"
if [ $FAILED -eq 0 ]; then
  echo -e "${GREEN}✅ All validations passed!${NC}"
  echo "Safe to commit and push."
  exit 0
else
  echo -e "${RED}❌ Validation failed!${NC}"
  echo "Fix errors before committing."
  exit 1
fi

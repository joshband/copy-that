#!/bin/bash
# Validate .env file has required variables for copy-that

echo "Validating .env file..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found"
    echo "Run from project root directory"
    exit 1
fi

# Source the .env
set -a
source .env
set +a

# Required variables
errors=0

# DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL: missing"
    errors=$((errors+1))
elif [[ "$DATABASE_URL" == postgres* ]]; then
    echo "✓ DATABASE_URL: set ($(echo $DATABASE_URL | cut -d'@' -f2 | cut -d'/' -f1))"
else
    echo "⚠️  DATABASE_URL: unusual format"
fi

# OPENAI_API_KEY
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY: missing"
    errors=$((errors+1))
elif [[ "$OPENAI_API_KEY" == sk-* ]]; then
    echo "✓ OPENAI_API_KEY: set (sk-...${OPENAI_API_KEY: -4})"
else
    echo "⚠️  OPENAI_API_KEY: unusual format (should start with sk-)"
fi

# SECRET_KEY
if [ -z "$SECRET_KEY" ]; then
    echo "❌ SECRET_KEY: missing"
    errors=$((errors+1))
else
    echo "✓ SECRET_KEY: set (${#SECRET_KEY} chars)"
fi

# REDIS_URL (optional but recommended)
if [ -z "$REDIS_URL" ]; then
    echo "⚠️  REDIS_URL: missing (optional - will use in-memory cache)"
else
    echo "✓ REDIS_URL: set"
fi

# ANTHROPIC_API_KEY (optional - alternative to OpenAI)
if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "✓ ANTHROPIC_API_KEY: set (optional)"
fi

echo ""
if [ $errors -gt 0 ]; then
    echo "Found $errors error(s). Fix before running."
    exit 1
else
    echo "All required variables set!"
    echo ""
    echo "Test locally with:"
    echo "  docker build --target production -t copy-that-api ."
    echo "  docker run -p 8080:8080 --env-file .env copy-that-api"
fi

#!/bin/bash

# =============================================================================
# Spacing Token Pipeline Setup Script
# =============================================================================
#
# REFERENCE IMPLEMENTATION - This is planning/documentation code showing how the
# setup script should be structured when implemented. This script is not meant
# to be run directly but serves as a complete reference for implementing the
# actual setup process.
#
# This script:
# 1. Installs dependencies
# 2. Runs database migrations
# 3. Verifies the setup
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =============================================================================
# Helper Functions
# =============================================================================

print_header() {
    echo ""
    echo -e "${BLUE}==============================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}==============================================================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 is not installed"
        return 1
    fi
    print_success "$1 is installed"
    return 0
}

# =============================================================================
# Configuration
# =============================================================================

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../../../../.." && pwd)"
REFERENCE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Default values
PYTHON_VERSION="3.11"
VENV_NAME=".venv"
SKIP_VENV=${SKIP_VENV:-false}
SKIP_MIGRATIONS=${SKIP_MIGRATIONS:-false}

# =============================================================================
# Parse Arguments
# =============================================================================

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-venv)
            SKIP_VENV=true
            shift
            ;;
        --skip-migrations)
            SKIP_MIGRATIONS=true
            shift
            ;;
        --python)
            PYTHON_VERSION="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --skip-venv         Skip virtual environment creation"
            echo "  --skip-migrations   Skip database migrations"
            echo "  --python VERSION    Python version to use (default: 3.11)"
            echo "  --help              Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# =============================================================================
# Pre-flight Checks
# =============================================================================

print_header "Pre-flight Checks"

# Check required commands
MISSING_COMMANDS=0

if ! check_command "python3"; then
    ((MISSING_COMMANDS++))
fi

if ! check_command "pip"; then
    ((MISSING_COMMANDS++))
fi

if ! check_command "psql"; then
    print_warning "psql is not installed (needed for PostgreSQL)"
else
    print_success "psql is installed"
fi

if ! check_command "redis-cli"; then
    print_warning "redis-cli is not installed (needed for caching)"
else
    print_success "redis-cli is installed"
fi

if [ $MISSING_COMMANDS -gt 0 ]; then
    print_error "Missing required commands. Please install them and try again."
    exit 1
fi

# Check Python version
PYTHON_ACTUAL=$(python3 --version | cut -d' ' -f2)
print_info "Python version: $PYTHON_ACTUAL"

# =============================================================================
# Virtual Environment Setup
# =============================================================================

if [ "$SKIP_VENV" = false ]; then
    print_header "Virtual Environment Setup"

    cd "$PROJECT_ROOT"

    if [ -d "$VENV_NAME" ]; then
        print_warning "Virtual environment already exists at $VENV_NAME"
        read -p "Recreate it? [y/N] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$VENV_NAME"
            python3 -m venv "$VENV_NAME"
            print_success "Virtual environment recreated"
        else
            print_info "Using existing virtual environment"
        fi
    else
        python3 -m venv "$VENV_NAME"
        print_success "Virtual environment created"
    fi

    # Activate virtual environment
    source "$VENV_NAME/bin/activate"
    print_success "Virtual environment activated"
else
    print_info "Skipping virtual environment setup"
fi

# =============================================================================
# Install Dependencies
# =============================================================================

print_header "Installing Dependencies"

cd "$PROJECT_ROOT"

# Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip

# Install main dependencies
if [ -f "requirements.txt" ]; then
    print_info "Installing from requirements.txt..."
    pip install -r requirements.txt
    print_success "Main dependencies installed"
else
    print_warning "requirements.txt not found"
fi

# Install development dependencies
if [ -f "requirements-dev.txt" ]; then
    print_info "Installing from requirements-dev.txt..."
    pip install -r requirements-dev.txt
    print_success "Development dependencies installed"
fi

# Install spacing-specific dependencies if needed
print_info "Installing spacing pipeline dependencies..."

# Core dependencies for spacing pipeline
pip install anthropic openai pydantic pydantic-settings

# Test dependencies
pip install pytest pytest-asyncio pytest-cov httpx aiosqlite

print_success "All dependencies installed"

# =============================================================================
# Environment Configuration
# =============================================================================

print_header "Environment Configuration"

# Copy example env file if it doesn't exist
ENV_SPACING_FILE="$PROJECT_ROOT/.env.spacing"
ENV_EXAMPLE_FILE="$REFERENCE_DIR/config/.env.spacing.example"

if [ ! -f "$ENV_SPACING_FILE" ]; then
    if [ -f "$ENV_EXAMPLE_FILE" ]; then
        cp "$ENV_EXAMPLE_FILE" "$ENV_SPACING_FILE"
        print_success "Created .env.spacing from example"
        print_warning "Please update .env.spacing with your configuration"
    else
        print_warning ".env.spacing.example not found"
    fi
else
    print_info ".env.spacing already exists"
fi

# Check for API keys
if [ -z "$ANTHROPIC_API_KEY" ]; then
    print_warning "ANTHROPIC_API_KEY not set in environment"
else
    print_success "ANTHROPIC_API_KEY is set"
fi

if [ -z "$OPENAI_API_KEY" ]; then
    print_info "OPENAI_API_KEY not set (optional if using Anthropic)"
else
    print_success "OPENAI_API_KEY is set"
fi

# =============================================================================
# Database Migrations
# =============================================================================

if [ "$SKIP_MIGRATIONS" = false ]; then
    print_header "Database Migrations"

    # Check if alembic is installed
    if command -v alembic &> /dev/null; then
        print_info "Running database migrations..."

        cd "$PROJECT_ROOT"

        # Check current migration status
        alembic current

        # Run migrations
        alembic upgrade head

        print_success "Database migrations completed"
    else
        print_warning "Alembic not found. Please install it and run migrations manually:"
        print_info "  pip install alembic"
        print_info "  alembic upgrade head"
    fi
else
    print_info "Skipping database migrations"
fi

# =============================================================================
# Verification
# =============================================================================

print_header "Verification"

cd "$PROJECT_ROOT"

# Check if spacing modules can be imported
print_info "Checking module imports..."

python3 << 'EOF'
import sys
sys.path.insert(0, "src")

# Test basic imports
try:
    import anthropic
    print("✓ anthropic imported successfully")
except ImportError as e:
    print(f"✗ anthropic import failed: {e}")

try:
    import openai
    print("✓ openai imported successfully")
except ImportError as e:
    print(f"✗ openai import failed: {e}")

try:
    from pydantic import BaseModel
    from pydantic_settings import BaseSettings
    print("✓ pydantic imported successfully")
except ImportError as e:
    print(f"✗ pydantic import failed: {e}")

try:
    import pytest
    print("✓ pytest imported successfully")
except ImportError as e:
    print(f"✗ pytest import failed: {e}")

# When actual spacing modules are implemented, test them here:
# try:
#     from copy_that.application.spacing_extractor import AISpacingExtractor
#     print("✓ AISpacingExtractor imported successfully")
# except ImportError as e:
#     print(f"⚠ AISpacingExtractor not yet implemented: {e}")

print("\nModule verification complete!")
EOF

# Check database connection (if DATABASE_URL is set)
if [ -n "$DATABASE_URL" ]; then
    print_info "Checking database connection..."
    python3 << 'EOF'
import os
from sqlalchemy import create_engine, text

try:
    url = os.environ.get("DATABASE_URL")
    engine = create_engine(url)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✓ Database connection successful")
except Exception as e:
    print(f"✗ Database connection failed: {e}")
EOF
else
    print_warning "DATABASE_URL not set, skipping database check"
fi

# =============================================================================
# Summary
# =============================================================================

print_header "Setup Complete!"

echo "Next steps:"
echo ""
echo "1. Configure your environment:"
echo "   - Edit .env.spacing with your API keys and settings"
echo "   - Ensure DATABASE_URL is set correctly"
echo ""
echo "2. Run tests to verify setup:"
echo "   ./scripts/run_spacing_tests.sh"
echo ""
echo "3. Seed development data (optional):"
echo "   python scripts/seed_spacing_data.py"
echo ""
echo "4. Start development:"
echo "   - Implement spacing_extractor.py"
echo "   - Implement spacing_utils.py"
echo "   - Implement aggregator.py"
echo ""

print_success "Spacing pipeline setup complete!"

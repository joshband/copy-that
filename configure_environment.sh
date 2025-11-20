#!/bin/bash
set -e

# Ensure the script is run from the project root
cd "$(dirname "$0")"

# Create a virtual environment if not exists
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-cov

# Configure environment
case "$1" in
    local|staging|production)
        echo "Configuring $1 environment..."
        python3 -m src.copy_that.infrastructure.deployment_config
        ;;
    *)
        echo "Usage: $0 {local|staging|production}"
        exit 1
        ;;
esac

# Run infrastructure tests with coverage
python3 -m pytest tests/infrastructure/test_deployment_config.py

# Deactivate virtual environment
deactivate
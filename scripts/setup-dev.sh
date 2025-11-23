#!/usr/bin/env bash
# Setup development environment for Copy That
# Usage: ./scripts/setup-dev.sh

set -e

echo "🚀 Setting up Copy That development environment..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
check_prereqs() {
    echo "📋 Checking prerequisites..."

    # Python 3.12+
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 not found. Please install Python 3.12+${NC}"
        exit 1
    fi

    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    if [[ "$PYTHON_VERSION" < "3.12" ]]; then
        echo -e "${RED}❌ Python 3.12+ required (found $PYTHON_VERSION)${NC}"
        exit 1
    fi
    echo -e "  ${GREEN}✓${NC} Python $PYTHON_VERSION"

    # uv (recommended) or pip
    if command -v uv &> /dev/null; then
        INSTALLER="uv"
        echo -e "  ${GREEN}✓${NC} uv package manager"
    elif command -v pip &> /dev/null; then
        INSTALLER="pip"
        echo -e "  ${YELLOW}⚠${NC} uv not found, using pip (slower)"
    else
        echo -e "${RED}❌ No package manager found. Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh${NC}"
        exit 1
    fi

    # Git
    if ! command -v git &> /dev/null; then
        echo -e "${RED}❌ Git not found${NC}"
        exit 1
    fi
    echo -e "  ${GREEN}✓${NC} Git"

    echo ""
}

# Install dependencies
install_deps() {
    echo "📦 Installing dependencies..."

    if [[ "$INSTALLER" == "uv" ]]; then
        uv pip install -e ".[dev]"
    else
        pip install -e ".[dev]"
    fi

    echo -e "  ${GREEN}✓${NC} Dependencies installed"
    echo ""
}

# Setup pre-commit hooks
setup_precommit() {
    echo "🔧 Setting up pre-commit hooks..."

    # Install pre-commit if not available
    if ! command -v pre-commit &> /dev/null; then
        if [[ "$INSTALLER" == "uv" ]]; then
            uv pip install pre-commit
        else
            pip install pre-commit
        fi
    fi

    # Install hooks for both commit and push
    pre-commit install --hook-type pre-commit --hook-type pre-push

    echo -e "  ${GREEN}✓${NC} Pre-commit hooks installed"
    echo -e "  ${GREEN}✓${NC} Pre-push hooks installed (runs tests before push)"
    echo ""
}

# Setup environment file
setup_env() {
    echo "⚙️  Setting up environment..."

    if [[ ! -f .env ]]; then
        if [[ -f .env.example ]]; then
            cp .env.example .env
            echo -e "  ${GREEN}✓${NC} Created .env from .env.example"
            echo -e "  ${YELLOW}⚠${NC} Please update .env with your credentials"
        else
            echo -e "  ${YELLOW}⚠${NC} No .env.example found, skipping"
        fi
    else
        echo -e "  ${GREEN}✓${NC} .env already exists"
    fi
    echo ""
}

# Verify installation
verify() {
    echo "✅ Verifying installation..."

    # Check ruff
    if python -m ruff --version &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} Ruff linter"
    else
        echo -e "  ${RED}❌${NC} Ruff not working"
    fi

    # Check mypy
    if python -m mypy --version &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} MyPy type checker"
    else
        echo -e "  ${RED}❌${NC} MyPy not working"
    fi

    # Check pytest
    if python -m pytest --version &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} Pytest"
    else
        echo -e "  ${RED}❌${NC} Pytest not working"
    fi

    echo ""
}

# Print summary
summary() {
    echo "=========================================="
    echo -e "${GREEN}🎉 Development environment ready!${NC}"
    echo "=========================================="
    echo ""
    echo "Quick commands:"
    echo "  make test        Run fast tests"
    echo "  make check       Run linting + type checks"
    echo "  make test-cov    Run tests with coverage"
    echo "  make ci-light    Simulate light CI tier"
    echo ""
    echo "Git hooks active:"
    echo "  • Pre-commit: lint, format (auto-fix)"
    echo "  • Pre-push: type-check, fast tests"
    echo ""
    echo "To skip hooks temporarily:"
    echo "  git commit --no-verify"
    echo "  git push --no-verify"
    echo ""
}

# Main
main() {
    check_prereqs
    install_deps
    setup_precommit
    setup_env
    verify
    summary
}

main "$@"

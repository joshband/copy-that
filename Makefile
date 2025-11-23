.PHONY: help install lint format type-check test test-fast test-unit test-integration test-all test-cov clean

# Default target
help:
	@echo "Copy That - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install        Install dependencies and pre-commit hooks"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint           Run ruff linter"
	@echo "  make format         Format code with ruff"
	@echo "  make type-check     Run mypy type checker"
	@echo "  make check          Run all checks (lint + format + type)"
	@echo ""
	@echo "Testing (tiered):"
	@echo "  make test-fast      Run fast unit tests only (< 1 min)"
	@echo "  make test-unit      Run all unit tests"
	@echo "  make test-int       Run integration tests"
	@echo "  make test-all       Run all tests"
	@echo "  make test-cov       Run tests with coverage report"
	@echo ""
	@echo "Shortcuts:"
	@echo "  make test           Alias for test-fast"
	@echo "  make ci-light       Simulate light CI tier"
	@echo "  make ci-medium      Simulate medium CI tier"
	@echo "  make ci-heavy       Simulate heavy CI tier"

# =============================================================================
# SETUP
# =============================================================================

install:
	uv pip install -e ".[dev]"
	pre-commit install --hook-type pre-commit --hook-type pre-push
	@echo ""
	@echo "✅ Installed! Pre-commit hooks active for commit and push."

# =============================================================================
# CODE QUALITY
# =============================================================================

lint:
	ruff check .

format:
	ruff format .

format-check:
	ruff format --check .

type-check:
	mypy src/

check: lint format-check type-check
	@echo "✅ All checks passed!"

# =============================================================================
# TESTING - TIERED
# =============================================================================

# Light tier - fast feedback
test-fast:
	pytest tests/unit -x -q -m "not slow" --ignore=tests/unit/pipeline --tb=line

test: test-fast

# Medium tier - full unit + integration
test-unit:
	pytest tests/unit -v --tb=short

test-int: test-integration
test-integration:
	pytest tests/integration -v --tb=short

# Heavy tier - everything
test-all:
	pytest tests/ -v --tb=short

# With coverage
test-cov:
	pytest tests/ -v --cov=src/copy_that --cov-report=term-missing --cov-report=html
	@echo ""
	@echo "📊 Coverage report: htmlcov/index.html"

# =============================================================================
# CI SIMULATION
# =============================================================================

ci-light: lint format-check type-check test-fast
	@echo ""
	@echo "✅ Light CI tier passed!"

ci-medium: ci-light test-unit test-integration
	@echo ""
	@echo "✅ Medium CI tier passed!"

ci-heavy: ci-medium test-all
	@echo ""
	@echo "✅ Heavy CI tier passed!"

# =============================================================================
# UTILITIES
# =============================================================================

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "🧹 Cleaned!"

# Database
db-migrate:
	alembic upgrade head

db-rollback:
	alembic downgrade -1

# Docker
docker-build:
	docker build -t copy-that:dev --target development .

docker-run:
	docker compose up -d

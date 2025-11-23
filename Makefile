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
	@echo "  make dead-code      Find unused code with vulture"
	@echo ""
	@echo "Testing (tiered):"
	@echo "  make test-fast      Run fast unit tests only (< 1 min)"
	@echo "  make test-unit      Run all unit tests"
	@echo "  make test-int       Run integration tests"
	@echo "  make test-all       Run all tests"
	@echo "  make test-cov       Run tests with coverage report"
	@echo ""
	@echo "Advanced Testing:"
	@echo "  make test-e2e       Run E2E tests with Playwright"
	@echo "  make test-visual    Run visual regression tests"
	@echo "  make test-a11y      Run accessibility tests"
	@echo "  make test-api       Run API contract tests"
	@echo "  make test-load      Run load tests with Locust"
	@echo "  make test-mutation  Run mutation tests (slow)"
	@echo ""
	@echo "CI Simulation:"
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

dead-code:
	vulture src/copy_that --min-confidence 80

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
# TESTING - ADVANCED
# =============================================================================

# E2E tests with Playwright
test-e2e:
	playwright install chromium --with-deps
	pytest tests/ui -v --browser chromium

# Visual regression tests
test-visual:
	playwright install chromium --with-deps
	pytest tests/visual -v --browser chromium

# Accessibility tests
test-a11y:
	playwright install chromium --with-deps
	pytest tests/a11y -v --browser chromium

# API contract tests
test-api:
	pytest tests/api -v

# Load tests with Locust (headless, 1 minute)
test-load:
	locust -f tests/load/locustfile.py --headless -u 50 -r 5 -t 1m --host http://localhost:8000

# Load tests with web UI
test-load-ui:
	@echo "Starting Locust web UI at http://localhost:8089"
	locust -f tests/load/locustfile.py --host http://localhost:8000

# Mutation testing (slow - tests your tests)
test-mutation:
	mutmut run --paths-to-mutate=src/copy_that/pipeline/ --runner="pytest tests/unit/pipeline -x -q"
	mutmut results

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

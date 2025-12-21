# Copy That - Development Makefile
# Fast local validation + TDD workflow

.PHONY: help check quick test dev coverage tdd user-test

## ⚡ FAST VALIDATION (30 seconds)
check: ## Fast validation before commit
	@echo "🔍 Running fast validation..."
	@source .venv/bin/activate && mypy src/ && ruff check . && ruff format --check . && pnpm type-check
	@echo "✅ All checks passed!"

quick: check

ruff-fix: ## Auto-fix linting issues
	@source .venv/bin/activate && ruff check . --fix && ruff format .

## 🧪 TESTING
test-quick: ## Quick smoke tests (2-3 min)
	@source .venv/bin/activate && pytest tests/unit -x -k "test_color or test_spacing" --maxfail=5

test: ## Full test suite (10-15 min)
	@source .venv/bin/activate && pytest tests/ -v

test-watch: ## 🔥 TDD mode - auto-run tests on file changes
	@echo "👀 Starting TDD watch mode..."
	@source .venv/bin/activate && pytest-watch tests/unit -- -v --tb=short

test-failed: ## Re-run only failed tests
	@source .venv/bin/activate && pytest --lf -v

coverage: ## Generate coverage report (HTML + terminal)
	@echo "📊 Generating coverage report..."
	@source .venv/bin/activate && pytest tests/ --cov=src/copy_that --cov-report=html --cov-report=term
	@echo "✅ Coverage report: open htmlcov/index.html"

coverage-quick: ## Quick coverage (unit tests only)
	@source .venv/bin/activate && pytest tests/unit --cov=src/copy_that --cov-report=term

## 🚀 DEVELOPMENT
dev: ## Start backend + frontend (Docker Compose)
	@echo "🚀 Starting development environment..."
	@docker-compose up -d
	@sleep 3
	@echo "✅ Services started:"
	@echo "   Frontend: http://localhost:3000"
	@echo "   Backend:  http://localhost:8000"
	@echo "   API Docs: http://localhost:8000/docs"

user-test: ## 🎯 Quick standup for user testing (fast!)
	@echo "🎯 Standing up backend + frontend for user testing..."
	@docker-compose up -d
	@echo ""
	@echo "✅ Ready for user testing!"
	@echo "   👉 Frontend: http://localhost:3000"
	@echo "   👉 Backend:  http://localhost:8000"
	@echo ""
	@echo "Logs: make logs"
	@echo "Stop: make stop"

stop: ## Stop all services
	@docker-compose down

logs: ## View service logs
	@docker-compose logs -f

restart: ## Restart services
	@docker-compose restart

## 🗄️ DATABASE
db-migrate: ## Run database migrations
	@source .venv/bin/activate && alembic upgrade head

db-rollback: ## Rollback last migration
	@source .venv/bin/activate && alembic downgrade -1

## 🔧 CI/CD
ci-local: ## Run full CI locally (matches GitHub Actions)
	@make check && make test-quick
	@echo "🚀 Safe to push!"

ci-watch: ## Watch latest CI run status
	@gh run list --limit 1

## 🧹 CLEANUP
clean: ## Clean build artifacts
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf htmlcov/ coverage.xml 2>/dev/null || true

help:
	@echo "Copy That - Development Commands"
	@echo ""
	@echo "⚡ FAST (before every commit):"
	@echo "  make check        # Validation (30 sec)"
	@echo "  make test-quick   # Smoke tests (2-3 min)"
	@echo ""
	@echo "🔥 TDD MODE:"
	@echo "  make test-watch   # Auto-run tests on save"
	@echo ""
	@echo "🚀 DEVELOPMENT:"
	@echo "  make dev          # Start backend + frontend"
	@echo "  make user-test    # Quick standup for testing"
	@echo "  make stop         # Stop services"
	@echo ""
	@echo "📊 COVERAGE:"
	@echo "  make coverage     # Full coverage report"
	@echo ""
	@echo "All commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-18s %s\n", $$1, $$2}'

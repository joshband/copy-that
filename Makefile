# Copy That - Development Makefile
# Fast local validation + TDD workflow

.PHONY: help check quick test dev coverage tdd user-test celery-mood-board fal-flux-shim labs labs-check

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
dev: ## Start Docker compose stack (API/DB). UI: use `pnpm dev` → :5173 (not :3000)
	@echo "🚀 Starting Docker services (postgres/redis/api if defined)…"
	@docker compose up -d
	@sleep 3
	@echo "✅ Infra up. Canonical Vite UI (recommended):"
	@echo "   pnpm dev                 → http://127.0.0.1:5173"
	@echo "   Backend / OpenAPI:         http://127.0.0.1:8000/docs"
	@echo "   Docker frontend image:     http://127.0.0.1:3000 (often stale — rebuild to use)"

labs: ## Labs stack: postgres/redis + Fal shim + API + Vite (:5173). Optional: labs WITH_CELERY=1
	@./scripts/dev_labs.sh $(if $(WITH_CELERY),--with-celery,)

labs-check: ## Status of Labs ports / FAL_KEY / Flux URL
	@./scripts/dev_labs.sh --check

celery-mood-board: ## macOS Celery solo worker for mood-board queue (prefork often SIGSEGVs)
	@echo "🧵 Starting mood-board Celery worker (solo pool)…"
	@echo "   Requires: docker compose up -d redis postgres"
	@echo "   Tip: prefer MOOD_BOARD_TEXT_MODEL=google/gemma-2-9b for theme JSON;"
	@echo "        google/gemma-4-e4b can stall on long structured prompts."
	@set -a && . ./.env && set +a && \
		PYTHONPATH=src .venv/bin/celery -A copy_that.infrastructure.celery.app worker \
		--loglevel=info -Q mood-board,celery --pool=solo

fal-flux-shim: ## OpenAI images shim → Fal FLUX.1 schnell (:8766); needs FAL_KEY in .env
	@echo "⚡ Starting Fal→OpenAI images shim on :8766…"
	@echo "   Get a key: https://fal.ai/dashboard/keys"
	@echo "   Then set in .env: FAL_KEY=… and MOOD_BOARD_FLUX_BASE_URL=http://127.0.0.1:8766/v1"
	@set -a && . ./.env && set +a && \
		.venv/bin/python scripts/mood_board_fal_openai_shim.py

user-test: ## Stand up compose for testing; prefer Vite :5173 for latest UI
	@echo "🎯 Standing up docker compose…"
	@docker compose up -d
	@echo ""
	@echo "✅ Infra ready."
	@echo "   👉 Canonical UI:  pnpm dev → http://127.0.0.1:5173"
	@echo "   👉 Backend:       http://127.0.0.1:8000"
	@echo "   👉 Docker UI:     http://127.0.0.1:3000 (image — rebuild if Labs missing)"
	@echo ""
	@echo "Labs one-shot: make labs   (or make labs WITH_CELERY=1)"

stop: ## Stop all services
	@docker-compose down

logs: ## View service logs
	@docker-compose logs -f

restart: ## Restart services
	@docker-compose restart

## 🗄️ DATABASE
db-up: ## Start local Postgres (Docker Compose) and wait until ready
	@.venv/bin/python scripts/db_bootstrap.py --wait-only

db-down: ## Stop local Postgres
	@docker compose stop postgres

db-bootstrap: ## Bootstrap local DB (Postgres via Docker + Alembic)
	@.venv/bin/python scripts/db_bootstrap.py

db-bootstrap-sqlite: ## Bootstrap local SQLite (create_all + stamp head)
	@.venv/bin/python scripts/db_bootstrap.py --sqlite

db-migrate: ## Run Alembic upgrade head against current DATABASE_URL
	@source .venv/bin/activate && alembic upgrade head

db-rollback: ## Rollback last migration
	@source .venv/bin/activate && alembic downgrade -1

db-reset: ## Reset local Postgres volume and re-bootstrap
	@docker compose down -v --remove-orphans
	@$(MAKE) db-bootstrap

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
	@echo "  make celery-mood-board  # macOS solo Celery for mood board"
	@echo "  make stop         # Stop services"
	@echo ""
	@echo "📊 COVERAGE:"
	@echo "  make coverage     # Full coverage report"
	@echo ""
	@echo "All commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-18s %s\n", $$1, $$2}'

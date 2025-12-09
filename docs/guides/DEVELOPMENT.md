# Development Guide

Complete setup and development instructions for Copy That.

## Quick Start (5 minutes)

### Prerequisites
- **Python 3.12+** ([download](https://www.python.org/downloads/))
- **Node.js 18+** ([download](https://nodejs.org/))
- **Docker** (optional, for containerized database)

### One-Time Setup

```bash
# Clone the repository
git clone https://github.com/joshband/copy-that.git
cd copy-that

# Backend setup
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
make install

# Frontend setup
pnpm install
```

**That's it!** You're ready to develop.

---

## Running the Application

### Local Development (All Services)

Run everything locally with Docker Compose:

```bash
# Start PostgreSQL + Redis
docker compose up -d

# In one terminal - Backend
source .venv/bin/activate
pnpm dev:backend

# In another terminal - Frontend
pnpm dev
```

**URLs:**
- Frontend: http://localhost:5173 (Vite dev server)
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Backend Only

```bash
source .venv/bin/activate
pnpm dev:backend
```

### Frontend Only

```bash
pnpm dev
```

### All Services (One Command)

```bash
pnpm dev:all
```

---

## Database Setup

### Run Migrations

```bash
source .venv/bin/activate
alembic upgrade head
```

### Create New Migration

After modifying models in `src/copy_that/domain/models.py`:

```bash
source .venv/bin/activate
alembic revision --autogenerate -m "description of changes"
alembic upgrade head
```

### Reset Database (Development Only)

```bash
docker compose down
docker compose up -d
source .venv/bin/activate
alembic upgrade head
```

---

## Testing

### Tiered Testing Strategy

The test suite is organized by speed and scope:

```bash
# Fast feedback (< 1 min) - Run after every code change
make test-fast

# Full unit tests (~ 2 min)
make test-unit

# Integration tests (~ 2 min)
make test-int

# All tests with coverage report
make test-cov

# Run specific test file
pytest tests/unit/api/test_colors_api.py -v

# Run single test
pytest tests/unit/api/test_colors_api.py::TestColorExtraction::test_extract_colors_project_not_found -v
```

### Advanced Testing

```bash
# End-to-end (Playwright browser automation)
make test-e2e

# Visual regression testing
make test-visual

# Accessibility testing
make test-a11y

# API contract testing
make test-api

# Load testing (50 concurrent users, 1 minute)
make test-load

# Load testing with UI dashboard
make test-load-ui  # Visit http://localhost:8089
```

### CI Simulation

Simulate the exact CI environment locally:

```bash
# Light tier (lint + fast tests)
make ci-light

# Medium tier (light + full unit + integration)
make ci-medium

# Heavy tier (everything including security scans)
make ci-heavy
```

---

## Code Quality

### Before Committing

```bash
# Run all checks (linting, formatting, type checking)
make check

# Format code
make format

# Check format without modifying
make format-check

# Lint for issues
make lint

# Type check with mypy
make type-check

# Find dead code
make dead-code
```

**Note:** Pre-commit hooks run these automatically on `git push`, but you can run manually.

### Code Style

- **Formatter:** Ruff (configured in `pyproject.toml`)
- **Linter:** Ruff with multiple rule sets (see `pyproject.toml`)
- **Type Checker:** mypy with strict mode
- **Docstring Style:** Google-style docstrings

---

## Project Structure

```
copy-that/
├── src/copy_that/              # Main application code
│   ├── application/            # Business logic (extractors, utilities)
│   ├── domain/                 # Data models (SQLModel entities)
│   ├── infrastructure/         # Technical infrastructure (DB, cache, security)
│   ├── interfaces/             # API layer (FastAPI routers)
│   └── services/               # Service layer (orchestration)
├── frontend/                   # React + Vite frontend
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── hooks/              # Custom React hooks
│   │   ├── pages/              # Page components
│   │   ├── store/              # Zustand state management
│   │   └── types/              # TypeScript types
│   └── vite.config.ts
├── tests/                      # Test suite
│   ├── unit/                   # Fast unit tests
│   ├── integration/            # Integration tests (with DB)
│   ├── e2e/ or ui/             # End-to-end tests (Playwright)
│   ├── visual/                 # Visual regression tests
│   ├── a11y/                   # Accessibility tests
│   ├── api/                    # API contract tests
│   └── load/                   # Load tests (Locust)
├── docs/                       # Documentation
├── Makefile                    # Development commands
├── docker-compose.yml          # Local services (Postgres, Redis)
├── Dockerfile                  # Container builds
├── pyproject.toml              # Python project config
├── pnpm-workspace.yaml         # Frontend + backend workspaces
└── DEVELOPMENT.md              # This file
```

---

## Common Development Tasks

### Add a New API Endpoint

1. **Define Request/Response Models** in `src/copy_that/interfaces/api/schemas.py`
2. **Create Route Handler** in appropriate router (e.g., `src/copy_that/interfaces/api/colors.py`)
3. **Write Tests** in corresponding test file (e.g., `tests/unit/api/test_colors_api.py`)
4. **Run Tests** with `pytest tests/unit/api/test_colors_api.py -v`

### Add a New Database Model

1. **Define Model** in `src/copy_that/domain/models.py`
2. **Create Migration** with `alembic revision --autogenerate -m "add new model"`
3. **Run Migration** with `alembic upgrade head`
4. **Write Tests** for new model

### Add a New Feature

1. **Create feature branch** from `develop`: `git checkout -b feature/my-feature`
2. **Write tests first** (TDD approach)
3. **Implement feature** to make tests pass
4. **Run full checks**: `make check`
5. **Push to GitHub** and create Pull Request

### Debug Backend Issues

```bash
# Enable detailed logging
export LOG_LEVEL=DEBUG
pnpm dev:backend

# Debug with breakpoints (VS Code)
# Add "debugpy" to [tool.pytest.ini_options] in pyproject.toml:
# addopts = "--debugpyfor pdb in the terminal"

# Use pdb for debugging
import pdb; pdb.set_trace()
```

### Inspect Database During Development

```bash
# Connect to PostgreSQL
docker compose exec postgres psql -U postgres -d copy_that_test

# Common queries
\dt                  # List all tables
\d color_tokens      # Describe table schema
SELECT * FROM color_tokens LIMIT 5;
```

---

## Environment Variables

### Backend (.env or .env.local)

```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/copy_that_test

# Cache
REDIS_URL=redis://localhost:6379/0

# AI/ML APIs
ANTHROPIC_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here

# Optional Features
FASTSAM_MODEL_PATH=/path/to/FastSAM-x.pt
LOG_LEVEL=INFO

# Development
DEBUG=True
```

### Frontend (.env.local)

```bash
# API Backend URL
VITE_API_URL=http://localhost:8000/api/v1
```

---

## Docker Development

### Using Docker Compose

```bash
# Start all services (Postgres + Redis)
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down

# Clean up volumes (resets database)
docker compose down -v
```

### Build and Run Docker Images

```bash
# Build development image
make docker-build

# Build production image
docker build -t copy-that:prod --target production .

# Run in container
docker run -p 8000:8000 -e DATABASE_URL=... copy-that:dev
```

---

## CI/CD Pipeline

Your code is automatically tested when you push. The CI pipeline runs tiered tests:

### PR/Feature Branch
- ✅ Lint & Format Check
- ✅ Type Check (mypy)
- ✅ Fast Unit Tests (< 1 min)

### Develop Branch
- ✅ All above
- ✅ Full Unit Tests
- ✅ Integration Tests

### Main/Release Branch
- ✅ All above
- ✅ Security Scans (Bandit, Gitleaks, pip-audit)
- ✅ Docker Build & Scan (Trivy)
- ✅ E2E Tests (Playwright)

**Status:** Check GitHub Actions tab for detailed results.

---

## Troubleshooting

### "command not found: python3.12"

Install Python 3.12+:
```bash
# macOS (Homebrew)
brew install python@3.12

# Ubuntu/Debian
sudo apt-get install python3.12

# Windows
Download from https://www.python.org/downloads/
```

### "command not found: pnpm"

Install pnpm:
```bash
npm install -g pnpm
```

### Database connection errors

```bash
# Ensure PostgreSQL is running
docker compose ps

# Restart services
docker compose down && docker compose up -d
```

### "Port 8000 already in use"

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### Tests failing locally but passing in CI

```bash
# Simulate exact CI environment
make ci-light

# Or with verbose output
pytest tests/unit -v --tb=short
```

### Pre-commit hooks not running

```bash
# Reinstall hooks
pre-commit install --hook-type pre-commit --hook-type pre-push

# Run manually
pre-commit run --all-files
```

---

## Performance Tips

### Speed Up Local Development

1. **Use fast tests while developing:**
   ```bash
   make test-fast
   ```

2. **Skip integration tests for frontend changes:**
   ```bash
   pytest tests/unit -v -m "not slow"
   ```

3. **Run specific test file instead of whole suite:**
   ```bash
   pytest tests/unit/api/test_colors_api.py -v
   ```

4. **Keep Docker services running between sessions:**
   ```bash
   docker compose up -d  # Once, then leave running
   ```

### CI Performance

- Light tier tests run in ~2 minutes
- Medium tier tests run in ~5 minutes
- Heavy tier tests run in ~12 minutes

---

## Getting Help

- **Quick questions:** Check existing GitHub Issues
- **Bug reports:** Open a new Issue with reproduction steps
- **Feature requests:** Discuss in Issues before implementing
- **Code review:** Ensure all checks pass before PR submission

---

## Related Documentation

- **API Documentation:** http://localhost:8000/docs (when running locally)
- **Architecture:** See `docs/` directory
- **Deployment:** See `.github/workflows/` for CI/CD setup
- **Roadmap:** [ROADMAP.md](ROADMAP.md)
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)

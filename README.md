# Copy That

**Universal Multi-Modal Token Platform** - Extract design tokens from any source, transform them into structured data, and generate production-ready code.

[![CI](https://github.com/joshband/copy-that/actions/workflows/ci.yml/badge.svg)](https://github.com/joshband/copy-that/actions/workflows/ci.yml)
[![Deploy](https://github.com/joshband/copy-that/actions/workflows/deploy.yml/badge.svg)](https://github.com/joshband/copy-that/actions/workflows/deploy.yml)
[![codecov](https://codecov.io/gh/joshband/copy-that/branch/main/graph/badge.svg)](https://codecov.io/gh/joshband/copy-that)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📖 Getting Started

**New to Copy That?** Start here: **[→ START_HERE.md](docs/START_HERE.md)**

**Full Documentation:** **[→ DOCUMENTATION.md](docs/DOCUMENTATION.md)** - Complete guide to all docs, learning paths, and use cases

**Quick start covers:**
- Where to find documentation
- Quick start (5 minutes)
- Understanding the architecture
- Building features (Phase 4)
- Deployment options

---

## Overview

Copy That is a modern token extraction and generation platform built with:
- **FastAPI** - High-performance async Python backend
- **W3C Design Tokens** - Industry-standard token schema
- **Domain-Driven Design** - Clean, maintainable architecture
- **Cloud-Native** - Designed for GCP Cloud Run
- **AI-Powered** - Claude Sonnet 4.5 for intelligent extraction

## Features

### Current (v0.1.0)
- 🎨 **Color Extraction** - AI-powered color palette extraction from images
- 📐 **Spacing Analysis** - SAM-enhanced spatial relationship detection
- 🔤 **Typography Recognition** - Font identification and hierarchy
- 🏗️ **W3C Tokens** - Industry-standard design token output
- 🔄 **REST API** - FastAPI with automatic OpenAPI docs
- 🐳 **Docker Ready** - Multi-stage builds for dev and production
- ☁️ **Cloud Run** - Optimized for serverless deployment

### Roadmap
See [ROADMAP.md](ROADMAP.md) for upcoming features.

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+ (for frontend)
- Docker & Docker Compose (optional)
- GCP account (for deployment)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/joshband/copy-that.git
   cd copy-that
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Install Python dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Set up database** (Neon PostgreSQL)
   ```bash
   # Database is pre-configured with Neon in .env
   # Run migrations to create tables
   alembic upgrade head
   ```

5. **Start backend**
   ```bash
   # Option A: With uvicorn directly
   python -m uvicorn src.copy_that.interfaces.api.main:app --reload --host 0.0.0.0 --port 8000

   # Option B: With Docker Compose
   docker-compose up postgres redis
   # then run uvicorn in separate terminal
   ```

6. **Install and run frontend** (in new terminal)
   ```bash
   # Install dependencies
   npm install

   # Start dev server (Vite)
   npm run dev

   # Frontend will be at http://localhost:5173
   # Proxies API calls to http://localhost:8000
   ```

### API Endpoints

**Project Management:**
- `POST /api/v1/projects` - Create new project
- `GET /api/v1/projects` - List all projects
- `GET /api/v1/projects/{id}` - Get project details
- `PUT /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project

**Color Extraction:**
- `POST /api/v1/colors/extract` - Extract colors from image (URL or base64)
- `POST /api/v1/colors` - Create color token manually
- `GET /api/v1/projects/{id}/colors` - Get all colors for project
- `GET /api/v1/colors/{id}` - Get specific color token

**Utilities:**
- `GET /api/v1/health` - Health check
- `GET /api/v1/db-test` - Test database connection
- `GET /api/v1/docs` - API documentation (JSON)

### Running Tests

```bash
# All tests (71 total)
pytest

# Unit tests (35)
pytest tests/unit

# Integration tests (13)
pytest tests/integration

# End-to-end tests (4)
pytest tests/e2e

# With coverage report
pytest --cov=src/copy_that --cov-report=html

# Specific test file
pytest tests/e2e/test_color_extraction_e2e.py -v
```

### Linting & Type Checking

```bash
# Lint Python
ruff check .

# Format Python
ruff format .

# Type check Python
mypy src/

# Type check frontend
npm run type-check
```

## Architecture

```
┌───────────────────────────────────────────┐
│     INPUT ADAPTERS (Modular)              │
│  Image | Video | Audio | Text | Custom    │
└───────────────────────────────────────────┘
                  ↓
┌───────────────────────────────────────────┐
│     TOKEN PLATFORM (Core)                 │
│  W3C Schema | Token Graph | Ontologies    │
└───────────────────────────────────────────┘
                  ↓
┌───────────────────────────────────────────┐
│     OUTPUT GENERATORS (Modular)           │
│  React | Flutter | Material | JUCE | ...  │
└───────────────────────────────────────────┘
```

### Tech Stack

**Backend:**
- FastAPI 0.115+ (async REST API)
- Pydantic v2 (strict type validation)
- SQLAlchemy 2.0 + Alembic (async ORM & migrations)
- PostgreSQL 17 (Neon serverless)
- Redis 7 (caching, background jobs)
- Celery (async task queue)

**Frontend:**
- React 18 (modern component library)
- Vite (next-gen bundler)
- TypeScript 5.3 (strict type checking)
- Axios (HTTP client)
- CSS3 (animations, gradients, responsive design)

**AI/ML:**
- Anthropic Claude Sonnet 4.5 (color extraction)
- Meta SAM (Segment Anything - future)
- ColorAide (color science - future)

**Infrastructure:**
- Docker / Docker Compose (local dev)
- GCP Cloud Run (serverless deployment)
- Terraform (infrastructure as code)
- GitHub Actions (CI/CD)

## Project Structure

```
copy-that/
├── src/copy_that/           # Application code
│   ├── domain/              # Domain models and business logic
│   ├── application/         # Use cases and services
│   ├── infrastructure/      # External dependencies (DB, Redis, etc.)
│   └── interfaces/          # API endpoints, CLI, etc.
├── tests/                   # Test suite
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── e2e/               # End-to-end tests
├── deploy/                  # Deployment configs
│   ├── local/              # Local development
│   ├── terraform/          # Infrastructure as code
│   └── cloudrun/           # Cloud Run configs
├── docs/                    # Documentation
│   ├── api/                # API documentation
│   ├── architecture/       # Architecture docs
│   └── guides/             # User guides
├── .github/workflows/       # CI/CD pipelines
├── Dockerfile              # Multi-stage Docker build
├── Dockerfile.cloudrun     # Cloud Run optimized
└── docker-compose.yml      # Local development stack
```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Key endpoints:
- `POST /api/v1/extract/color` - Extract color tokens from image
- `POST /api/v1/extract/spacing` - Extract spacing tokens
- `POST /api/v1/extract/typography` - Extract typography tokens
- `GET /api/v1/projects/{id}` - Get project details
- `GET /api/v1/db-test` - Test database connection
- `GET /api/v1/health` - Health check

## Deployment

### Choose Your Deployment Option

**Option 1: Minimal Cloud** (~$0-5/month) - **Recommended for personal/demo**
- Perfect for: Personal projects, sharing with friends/family
- Cost: Pay only when URL is accessed
- Setup time: 30 minutes
- See: [docs/SETUP_MINIMAL.md](docs/SETUP_MINIMAL.md)

**Option 2: Full Cloud** ($30-890/month) - **For production**
- Perfect for: Production apps, compliance needs, high traffic
- Cost: Staging $30-70/month, Production $320-890/month
- Setup time: 60 minutes
- See: [docs/INFRASTRUCTURE_SETUP.md](docs/INFRASTRUCTURE_SETUP.md)

**Option 3: Local Development** (FREE)
- Perfect for: Daily development
- Cost: $0
- Setup: `docker-compose up`

Compare options: [docs/DEPLOYMENT_OPTIONS.md](docs/DEPLOYMENT_OPTIONS.md)

### Quick Deploy (Minimal)
```bash
# 1. Create free accounts
https://neon.tech      # Free Postgres
https://upstash.com    # Free Redis

# 2. Deploy infrastructure
cd deploy/terraform
mv main.tf main-full.tf && mv main-minimal.tf main.tf
terraform init && terraform apply

# 3. Get your public URL
terraform output api_url
```

### Quick Deploy (Full)
```bash
# Deploy with Terraform
cd deploy/terraform
terraform init
terraform apply

# Or via GitHub Actions (auto-deploys)
git push origin develop  # → staging
git push origin main     # → production
```

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed guides.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development Workflow

1. **Feature Branch** - Create branch from `develop`
2. **Code** - Implement feature with tests
3. **CI Checks** - All tests, linting, type checking must pass
4. **PR Review** - Submit PR to `develop`
5. **Merge** - Auto-deploy to staging
6. **Release** - Merge `develop` → `main` for production

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- **Documentation**: [docs/DOCUMENTATION.md](docs/DOCUMENTATION.md) - Complete documentation guide
- **Quick Start**: [docs/START_HERE.md](docs/START_HERE.md)
- **API Docs**: http://localhost:8000/docs (when running)
- **Issues**: [GitHub Issues](https://github.com/joshband/copy-that/issues)
- **Discussions**: [GitHub Discussions](https://github.com/joshband/copy-that/discussions)

## Acknowledgments

- Built with [Claude Code](https://claude.com/claude-code)
- Inspired by the W3C Design Tokens Community Group
- Powered by Anthropic Claude Sonnet 4.5

---

**Status**: 🚧 Active Development | **Version**: 0.1.0 | **Last Updated**: 2025-11-19

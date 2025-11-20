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
- Python 3.11+ (3.12 recommended)
- Docker & Docker Compose
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

3. **Install dependencies**
   ```bash
   # Using uv (recommended - 10-100x faster)
   pip install uv
   uv pip install -e ".[dev]"

   # Or using pip
   pip install -e ".[dev]"
   ```

4. **Set up database** (Neon PostgreSQL)
   ```bash
   # Database is pre-configured with Neon
   # Run migrations to create tables
   alembic upgrade head

   # See docs/DATABASE_SETUP.md for details
   ```

4. **Run with Docker Compose**
   ```bash
   docker-compose up
   ```

   This starts:
   - **API** - http://localhost:8000
   - **Docs** - http://localhost:8000/docs
   - **PostgreSQL** - localhost:5432
   - **Redis** - localhost:6379
   - **Prometheus** - http://localhost:9090
   - **Grafana** - http://localhost:3000

5. **Or run locally**
   ```bash
   # Start backend services
   docker-compose up postgres redis

   # Run API
   uvicorn copy_that.interfaces.api.main:app --reload
   ```

### Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit

# Integration tests
pytest tests/integration

# With coverage
pytest --cov=src/copy_that --cov-report=html
```

### Linting & Type Checking

```bash
# Lint
ruff check .

# Format
ruff format .

# Type check
mypy src/
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
- FastAPI 0.115+
- Pydantic v2
- SQLAlchemy 2.0 + Alembic
- PostgreSQL 17 (Neon)
- Redis 7
- Celery

**AI/ML:**
- Anthropic Claude Sonnet 4.5
- Meta SAM (Segment Anything)
- ColorAide (color science)

**Infrastructure:**
- Docker / Docker Compose
- GCP Cloud Run
- Terraform
- GitHub Actions

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

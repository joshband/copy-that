# 🚀 Copy That - Start Here

**Welcome to Copy That!** A fresh, modular platform for extracting design tokens from images.

**Status:** v3.5.1 (Database Foundation Complete) | Last Updated: 2025-11-19

---

## 📍 Where Am I?

**If you're:**

### 👨‍💻 A Developer Getting Started
1. Read: [Local Development Setup](#local-development)
2. Follow: [Backend: Database Integration](#backend-database-integration)
3. Try: [Running the API](#running-the-api)

### 🏗️ Understanding the Architecture
1. Read: [System Architecture](#system-architecture)
2. Explore: `/docs/architecture/` - Design patterns and patterns
3. Reference: `/docs/domain/` - Token system and domain knowledge

### 📦 Building Features (Phase 4)
1. Start: [Phase 4 Color Vertical Slice](#phase-4-implementation)
2. Follow: `/docs/workflows/phase_4_color_vertical_slice.md`
3. Reference: `/docs/domain/token_system.md`

### 🚀 Deploying to Production
1. Read: `/docs/deployment/setup/deployment_options.md` - Choose your path
2. Follow: `/docs/deployment/setup/setup_minimal.md` (recommended) or `/docs/deployment/setup/infrastructure_setup.md`
3. Monitor: Cloud console for your deployment

### 📚 Understanding Tokens
1. Read: `/docs/domain/token_system.md` - Complete token reference
2. Explore: `/docs/domain/` - Token ontology, color science, etc.

---

## 🗺️ Documentation Map

### Essential Reading (15 minutes)

| Document | Purpose | Read Time |
|----------|---------|-----------|
| **[setup/start_here.md](#)** | You are here | 5 min |
| **[setup/database_setup.md](setup/database_setup.md)** | Database configuration | 10 min |
| **[workflows/phase_4_color_vertical_slice.md](workflows/phase_4_color_vertical_slice.md)** | Week 1 implementation plan | 15 min |

### Core Documentation

**Infrastructure & Deployment:**
- `deployment/setup/deployment_options.md` - Local vs Cloud comparison
- `deployment/setup/infrastructure_setup.md` - Full GCP Terraform guide
- `deployment/setup/setup_minimal.md` - Budget-friendly cloud setup

**Architecture & Design:**
- `architecture/` - System patterns and design decisions (coming soon)
- `domain/token_system.md` - 9 token types and schema structure
- `domain/` - Token ontology, visual DNA, color science

**Implementation:**
- `workflows/phase_4_color_vertical_slice.md` - Week 1 color extraction guide
- `guides/` - Development guides (coming soon)

---

## 🎯 Quick Start

### Local Development (5 minutes)

```bash
# 1. Clone and setup
git clone https://github.com/joshband/copy-that.git
cd copy-that
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env:
#   - DATABASE_URL (required; Postgres)
#   - SECRET_KEY (required; do not use the example value)
# For staging/prod also set REDIS_URL, CELERY_BROKER_URL, CELERY_RESULT_BACKEND

# 3. Run migrations
alembic upgrade head

# 4. Start the API
uvicorn src.copy_that.interfaces.api.main:app --reload

# 5. Test
curl http://localhost:8000/api/v1/db-test
```

### Backend: Database Integration

✅ **Already Complete:**
- Neon PostgreSQL project created
- SQLAlchemy async ORM configured
- Alembic migrations set up
- Initial schema (projects, extraction_jobs)
- FastAPI dependency injection ready

📖 **See:** `docs/setup/database_setup.md` for complete reference

### Running the API

```bash
# Development (with hot reload)
uvicorn src.copy_that.interfaces.api.main:app --reload

# Production
uvicorn src.copy_that.interfaces.api.main:app --host 0.0.0.0 --port 8000

# API docs (automatic)
open http://localhost:8000/docs
```

---

## 🏛️ System Architecture

### High-Level Design

```
┌──────────────────────────────────┐
│  Frontend (React + Vite)         │
│  - Image upload UI               │
│  - Token display                 │
│  - Generator integration         │
└──────────────────────────────────┘
              ↑ HTTP/WebSocket
┌──────────────────────────────────┐
│  Backend API (FastAPI)           │
│  - Token extraction              │
│  - Database queries              │
│  - Streaming updates             │
└──────────────────────────────────┘
              ↓ SQL
┌──────────────────────────────────┐
│  Database (Neon PostgreSQL)      │
│  - Projects table                │
│  - Extraction jobs               │
│  - Extracted tokens (color, etc.)│
└──────────────────────────────────┘
```

### Core Components

**Infrastructure Layer:**
- Database: `src/copy_that/infrastructure/database.py` (async SQLAlchemy)
- Persistence: `src/copy_that/infrastructure/persistence/models.py` (ORM) + `.../repositories/`
- Migrations: `alembic/` (Alembic with auto-detection)

**Domain Layer:**
- Entities/value objects only (no ORM): `src/copy_that/domain/`
- Token/value objects: `src/copy_that/domain/*`

**Application Layer:**
- Ports + use cases + extractors: `src/copy_that/application/`
- Execution abstractions: `src/copy_that/application/execution/`

**Composition Layer:**
- Dependency wiring: `src/copy_that/composition/container.py`

**Interface Layer:**
- API: `src/copy_that/interfaces/api/main.py` (FastAPI app)
- Routes: `src/copy_that/interfaces/api/` (endpoint handlers)

---

## 📋 Phase 4 Implementation

### Week 1: Color Tokens (NOW)

**Goal:** Extract, store, and display color tokens end-to-end

| Day | Focus | Status | Time |
|-----|-------|--------|------|
| **1** | Color schema foundation | ✅ Complete | 3 hrs |
| **2** | Adapter layer + tests | ✅ Complete | 2 hrs |
| **3** | Database migration | ✅ Complete | 2 hrs |
| **4** | AI extractor (Claude Structured Outputs) | ✅ Complete | 3 hrs |
| **5** | Frontend integration + E2E tests | 🔄 In Progress | 3 hrs |

**Success Criteria:**
- ✅ Color tokens extracted via Claude API
- ✅ Core → API transformation working
- ✅ color_tokens table in database
- ✅ Frontend displays colors with confidence
- ✅ All tests passing

📖 **Full Plan:** `docs/workflows/phase_4_color_vertical_slice.md`

### Week 2-5: Additional Tokens

Once color pattern is validated:
- Copy pattern for spacing tokens (2-3 days)
- Copy pattern for shadow tokens (1-2 days)
- Add typography tokens (2 days)
- Add border-radius tokens (1 day)
- Add opacity tokens (1 day)

---

## 🧠 Understanding Design Tokens

### What Are Tokens?

Design tokens are the **building blocks** of a design system:

```
Color #FF6B35        ← Color Token
Spacing 16px         ← Spacing Token
Font "Inter" 14px    ← Typography Token
Shadow 0 4px 8px    ← Shadow Token
```

### Token Types (9 Core)

1. **Color** - Palettes, primitives, semantic roles
2. **Spacing** - Layout, padding, margins (6 scales)
3. **Typography** - Fonts, sizes, weights, line heights
4. **Shadow** - Depth, elevation (4 levels)
5. **Border** - Width, radius, styles
6. **Opacity** - Transparency scales
7. **State Layer** - Hover, focus, pressed, disabled
8. **Gradient** - Multi-stop color transitions
9. **Animation** - Timing, easing, duration

### From Image to Tokens

```
Image Upload
    ↓
AI Analysis (Claude Structured Outputs)
    ↓
Token Extraction (color, spacing, etc.)
    ↓
Semantic Enhancement (naming, confidence)
    ↓
Database Storage
    ↓
Frontend Display + Code Generation
```

📖 **Complete Reference:** `/docs/domain/token_system.md`

---

## 🔧 Development Workflow

### Adding a New Feature

1. **Create branch:** `git checkout -b feature/my-feature`
2. **Write tests:** Follow TDD discipline
3. **Implement:** Add your code
4. **Verify:** `pnpm typecheck` and test suite pass
5. **Commit:** Follow commit conventions
6. **Push & PR:** Submit for review

### Running Tests

```bash
# Backend tests
pytest tests/ -v

# Type checking
mypy src/ --strict

# All checks
pytest && mypy src/
```

### Making Migrations

```bash
# Auto-detect changes from models
alembic revision --autogenerate -m "Description of change"

# Review migration file, then apply
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

---

## 🚀 Deployment Paths

### Path 1: Local Only (FREE)
```bash
docker-compose up
# http://localhost:8000
```
**Best for:** Development, testing

### Path 2: Minimal Cloud (Recommended) ← **START HERE**
- Public URL for sharing
- Auto-scaling
- Cost: $0-5/month

📖 Follow: `/docs/deployment/setup/setup_minimal.md`

### Path 3: Full Cloud (Enterprise)
- High availability
- Private networking
- Cost: $30-890/month

📖 Follow: `/docs/deployment/setup/infrastructure_setup.md`

---

## 📚 Key Resources

### Reference Docs
- `docs/setup/database_setup.md` - Database configuration, usage, monitoring
- `docs/deployment/setup/deployment_options.md` - Comparison of deployment options
- `docs/domain/token_system.md` - Complete token system reference

### Implementation Guides
- `docs/workflows/phase_4_color_vertical_slice.md` - Week 1 color extraction
- `docs/architecture/` - System patterns and best practices

### External Resources
- **Neon Dashboard:** https://console.neon.tech/app/projects/icy-lake-85661769
- **SQLAlchemy Docs:** https://docs.sqlalchemy.org/en/20/
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **Alembic Docs:** https://alembic.sqlalchemy.org/

---

## ❓ Common Questions

### Q: Where's the database connection?
**A:** Set `DATABASE_URL` in `.env`. Neon project already created: `icy-lake-85661769`

### Q: How do I test database queries?
**A:** Use `curl http://localhost:8000/api/v1/db-test` or query directly via:
```bash
mcp__Neon__run_sql --projectId icy-lake-85661769 --sql "SELECT * FROM projects"
```

### Q: Can I use a local PostgreSQL instead of Neon?
**A:** Yes! Set `DATABASE_URL=postgresql+asyncpg://user:pass@localhost/copy_that`

### Q: How do migrations work?
**A:** Alembic auto-detects model changes and generates SQL. See `docs/setup/database_setup.md` for commands.

### Q: What if I'm stuck?
**A:** Check:
1. `/docs/setup/database_setup.md` - Troubleshooting section
2. `/docs/deployment/` - Setup guides
3. GitHub issues - Search existing problems
4. Ask in project discussions

---

## 🎯 Next Steps

### Immediate (This Session)
1. ✅ Review this document
2. ⏳ Read: `docs/workflows/phase_4_color_vertical_slice.md`
3. ⏳ Build: Color token extraction endpoints

### This Week
1. Complete Phase 4 Week 1 (color tokens)
2. Test end-to-end extraction flow
3. Deploy to minimal cloud setup

### This Month
1. Add spacing token extraction
2. Add shadow token extraction
3. Build token display UI
4. Integrate with generators

---

## 📖 Full Documentation Structure

```
docs/
├── setup/start_here.md                    ← You are here
├── setup/database_setup.md                ← Database reference
├── workflows/phase_4_color_vertical_slice.md  ← Implementation guide
│
├── deployment/                      ← Deployment guides
│   ├── setup/deployment_options.md        (Local vs Cloud)
│   ├── setup/setup_minimal.md            (Recommended)
│   └── setup/infrastructure_setup.md      (Full Cloud)
│
├── domain/                          ← Domain knowledge
│   └── token_system.md             (Token reference)
│
└── architecture/                    ← Design patterns (coming)
    └── (Pattern documentation)
```

---

## 🤝 Contributing

When you make improvements:
1. Update relevant documentation
2. Keep this setup/start_here.md current
3. Add new docs for new features
4. Link between related documents

---

**Ready to start?** → Read **[workflows/phase_4_color_vertical_slice.md](workflows/phase_4_color_vertical_slice.md)**

**Questions?** → Check **[setup/database_setup.md](setup/database_setup.md)** or GitHub issues

---

**Version:** 3.5.1 | **Last Updated:** 2025-11-19 | **Project:** Copy That

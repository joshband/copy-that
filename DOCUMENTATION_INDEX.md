# Copy That Documentation Index
**Last Updated:** 2025-12-12
**Purpose:** Single source of truth for all active documentation

---

## 🚀 Quick Start

**New Developer?** Start here:
1. [README.md](README.md) - Project overview
2. [CLAUDE.md](CLAUDE.md) - Development rules
3. [docs/architecture/CURRENT_ARCHITECTURE_STATE.md](docs/architecture/CURRENT_ARCHITECTURE_STATE.md) - Architecture overview (v1.1)

**Working on a Feature?** Check:
- [Architecture](#architecture) - System design
- [Planning](#planning) - Roadmaps and phases
- [Guides](#guides) - How-to documentation

---

## 📋 Documentation Categories

### Architecture (Primary Reference)

**START HERE:** [Current Architecture State](docs/architecture/CURRENT_ARCHITECTURE_STATE.md)
- Complete system overview (Dec 2025, v1.1)
- Technology stack (Python, React, PostgreSQL)
- Architectural patterns (Adapter, Orchestrator, Multi-Extractor)
- Technical debt analysis
- Phase roadmap (Phase 2.5 → Phase 5)
- **NEW:** AI-powered mood board generation (Section 2.6)

**Core Architecture Docs:**
- [Strategic Vision](docs/architecture/STRATEGIC_VISION_AND_ARCHITECTURE.md) - Multi-modal platform vision
- [Multimodal Components](docs/architecture/MULTIMODAL_COMPONENT_ARCHITECTURE.md) - Token-agnostic UI pattern
- [Schema Architecture](docs/architecture/schema_architecture_diagram.md) - Database and type schemas
- [Adapter Pattern](docs/architecture/adapter_pattern.md) - Core → API → Database transformation
- [Extractor Patterns](docs/architecture/extractor_patterns.md) - Multi-extractor orchestration
- [Plugin Architecture](docs/architecture/plugin_architecture.md) - Generator plugin system
- [Component Token Schema](docs/architecture/component_token_schema.md) - Token data structures

---

### Planning & Roadmaps

**Active Phase:** Phase 2.5 - Multi-Extractor Orchestrators

**Current Planning Docs:**
- [Implementation Roadmap](docs/planning/IMPLEMENTATION_ROADMAP.md) - Current implementation plan
- [Shadow Extraction Roadmap](docs/planning/SHADOW_EXTRACTION_ROADMAP.md) - Shadow token extraction
- [README](docs/planning/README.md) - Planning documentation overview

**Reference:**
- [2025-11-21 PRD](docs/planning/2025-11-21-prd.md) - Product requirements
- [2025-11-21 Roadmap](docs/planning/2025-11-21-roadmap.md) - Initial roadmap

---

### Guides & How-Tos

**Developer Guides:**
- [Testing Guide](docs/guides/TESTING.md) - Test suite and coverage strategies
- [Security Guide](docs/guides/SECURITY.md) - Security best practices
- [Cost Optimization](docs/guides/COST_OPTIMIZATION.md) - API cost management

**Operational:**
- [PATH_SETUP_GUIDE.md](docs/guides/PATH_SETUP_GUIDE.md) - Running commands from project root

---

### Feature Specifications

**Active Features:**
- [Mood Board Specification](MOOD_BOARD_SPECIFICATION.md) - AI-generated mood boards (NEW - 2025-12-12)
  - Claude Sonnet 4.5 + DALL-E 3 integration
  - Material focus vs Typography focus
  - Cost: ~$0.10-0.20 per mood board

---

## 🗄️ Archived Documentation

**Location:** `~/Documents/copy-that-archive/`

**Archive Statistics (2025-12-12 - Second Pass Complete):**
- **Sessions:** 120+ session handoff documents (2025-11 to 2025-12)
  - Includes 35 files from docs/sessions/, 10 from docs/handoff/, 21 testing session files
- **Architecture History:** 50+ historical architecture docs
  - Includes backend analysis, frontend analysis, design analysis, CV preprocessing
- **Planning History:** 20+ completed planning docs
  - Includes strategy docs, phase completions, issue summaries
- **Guides Deprecated:** 40+ deprecated guides
  - Includes legacy design, testing, workflow, ops history docs

**Categories:**
- `sessions/` - Session handoff documents
- `architecture-history/` - Superseded architecture docs (legacy pipeline retirement, one-time reviews)
- `planning-history/` - Completed phase plans and summaries
- `guides-deprecated/` - Outdated setup guides (to be populated)
- `archive-from-docs/` - Historical docs/archive directory
- `testing-legacy-archive/` - Legacy testing documentation

**Archive Manifest:** `~/Documents/copy-that-archive/ARCHIVE_MANIFEST.md`

---

## 📊 Documentation Maintenance

### When to Archive
- ✅ Session handoffs after work is merged
- ✅ Completed phase plans
- ✅ Deprecated setup guides
- ✅ One-time reviews/audits (architecture reviews, type safety audits)
- ✅ Historical documentation superseded by current versions

### When to Keep Active
- ✅ Current architecture documentation (8 core docs)
- ✅ Active roadmaps and phase plans
- ✅ Operational guides (testing, security, cost optimization)
- ✅ Feature specifications in development
- ✅ README and CLAUDE.md

### Update Frequency
- **README.md:** Monthly (or when major features ship)
- **CLAUDE.md:** After each session (session summary section)
- **DOCUMENTATION_INDEX.md:** Monthly (or when docs reorganized)
- **Architecture docs:** Quarterly (or when architecture changes significantly)

### Monthly Documentation Review
**Checklist:** [MONTHLY_DOCUMENTATION_REVIEW_CHECKLIST.md](MONTHLY_DOCUMENTATION_REVIEW_CHECKLIST.md)
**Frequency:** First week of each month
**Duration:** ~2 hours
**Owner:** Development Team Lead

**Review Includes:**
- Archive session handoffs and phase completions
- Update architecture documentation if changed
- Archive superseded analysis documents
- Update this index with new/removed documentation
- Update archive statistics

---

## 🔍 Finding Information

### By Topic

**"How do I run tests?"**
→ [Testing Guide](docs/guides/TESTING.md)

**"What's the current architecture?"**
→ [CURRENT_ARCHITECTURE_STATE.md](docs/architecture/CURRENT_ARCHITECTURE_STATE.md)

**"What's the roadmap?"**
→ [Current Architecture State - Section 6](docs/architecture/CURRENT_ARCHITECTURE_STATE.md#6-phase-roadmap)

**"How do extractors work?"**
→ [Extractor Patterns](docs/architecture/extractor_patterns.md)

**"What's the adapter pattern?"**
→ [Adapter Pattern](docs/architecture/adapter_pattern.md)

**"How do I use the mood board generator?"**
→ [Mood Board Specification](MOOD_BOARD_SPECIFICATION.md)

### By Role

**Frontend Developer:**
1. [Multimodal Components](docs/architecture/MULTIMODAL_COMPONENT_ARCHITECTURE.md) - Token-agnostic UI
2. [Frontend source](frontend/src/) - React + TypeScript codebase
3. [Testing Guide](docs/guides/TESTING.md) - Vitest + Playwright

**Backend Developer:**
1. [Extractor Patterns](docs/architecture/extractor_patterns.md) - Multi-extractor orchestration
2. [Current Architecture](docs/architecture/CURRENT_ARCHITECTURE_STATE.md) - Complete backend overview
3. [Schema Architecture](docs/architecture/schema_architecture_diagram.md) - Database models

**DevOps:**
1. [PATH_SETUP_GUIDE.md](docs/guides/PATH_SETUP_GUIDE.md) - Command execution
2. [Security Guide](docs/guides/SECURITY.md) - Security practices
3. [Cost Optimization](docs/guides/COST_OPTIMIZATION.md) - API cost management

**Product/Design:**
1. [Strategic Vision](docs/architecture/STRATEGIC_VISION_AND_ARCHITECTURE.md) - Platform vision
2. [README.md](README.md) - Product overview
3. [Mood Board Specification](MOOD_BOARD_SPECIFICATION.md) - AI design features

---

## 📝 Contributing to Documentation

### Creating New Documentation
1. Place in appropriate `docs/` subdirectory
2. Update this index (DOCUMENTATION_INDEX.md)
3. Link from related documents
4. Update README.md if public-facing

### Deprecating Documentation
1. Copy to `~/Documents/copy-that-archive/[category]/`
2. Update archive manifest (`~/Documents/copy-that-archive/ARCHIVE_MANIFEST.md`)
3. Remove from this index
4. Update CLAUDE.md if it was referenced

### Documentation Standards
- Use markdown (.md) format
- Include date in filename for time-sensitive docs
- Add "Last Updated" timestamp for living documents
- Link to other relevant documentation
- Keep active docs updated, archive outdated versions

---

## 📈 Documentation Statistics

**Active Documentation (2025-12-12 - Second Pass Complete):**
- **Root:** 7 files (README, CLAUDE, DOCUMENTATION_INDEX, CONSOLIDATION_PLAN, MOOD_BOARD_SPEC, LEGACY_AUDIT, MONTHLY_REVIEW)
- **Architecture:** 9 files (8 core + README)
- **Planning:** ~10 files (active roadmaps only)
- **Guides:** ~5 files (operational guides)
- **Total Active:** ~110 markdown files (down from 280+)

**Archived (2025-12-12 - Second Pass Complete):**
- **Total Archived:** 240+ files (167 in second pass + 74 in first pass)
- **Session Handoffs:** 120+ files
- **Architecture History:** 50+ files
- **Planning History:** 20+ files
- **Guides Deprecated:** 40+ files

**Consolidation Progress:**
- ✅ Phase 1: Archive structure created
- ✅ Phase 2: 241 files archived (2 passes)
- ✅ Phase 3: Index created + Monthly review checklist
- ⏳ Phase 4: Git cleanup (167 files staged for deletion)

---

## 🔗 External Resources

**Primary Repository:**
- GitHub: [Copy That](https://github.com/[your-org]/copy-that) *(update with actual URL)*

**API Documentation:**
- API Docs: [Coming Soon] *(to be added)*
- Swagger UI: [Coming Soon] *(to be added)*

**Deployment:**
- Production: [Coming Soon] *(to be added)*
- Staging: [Coming Soon] *(to be added)*

---

**Last Review:** 2025-12-12
**Next Review:** 2026-01-12 (monthly cadence)
**Maintained By:** Core Development Team

---

**Questions or Suggestions?**
Open an issue or update this file via pull request.

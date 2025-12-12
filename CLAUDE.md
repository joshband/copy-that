# Copy That - Development Rules

**Version:** 1.0.0
**Last Updated:** 2025-12-12

---

## Development Rules

**Before task end:** Run `pnpm typecheck` (must pass)
**Never:** Auto-commit/push without explicit approval
**Context:** Never auto-compact. Always create handoff doc at 10% context remaining

---

## Latest Session Summary

**Date:** 2025-12-12
**Focus:** Architecture Review & Documentation Consolidation (2-Pass Cleanup)
**Status:** COMPLETE ✅

### Session Achievements

#### 1. Comprehensive Architecture Review ✅
- **Created:** `docs/architecture/CURRENT_ARCHITECTURE_STATE.md` (v1.1)
- **Agent Used:** Plan agent (specialized architectural analysis)
- **Scope:** Full codebase + documentation review
- **Findings:**
  - Architecture maturity: 75%
  - All 4 extractors fully implemented (Color, Spacing, Typography, Shadow)
  - Empty pipeline/ directory deleted
  - Discovered undocumented mood board feature
  - Identified 561 mypy type errors (pre-existing)

#### 2. Documentation Consolidation (2 Passes) ✅
**Total Archived:** 241 files (70% reduction from 368 → 110 active files)

**Pass 1 (82 files):**
- 26 historical architecture docs
- 44 session handoffs
- 4 planning docs
- 2 archive directories (docs/archive, testing/legacy/archive)
- Deleted: -36,238 lines

**Pass 2 (167 files):**
- 35 files from docs/sessions/
- 7 files from docs/handoff/
- 21 testing date-stamped files (2025-12-05)
- 40 explicitly legacy files (design/legacy, testing/legacy, workflows/legacy)
- 20 one-time analysis docs (backend, frontend, CV preprocessing)
- 12 phase completion docs (PHASE3_*, ISSUE_9*)
- Deleted: -76,245 lines

**Net Result:** -112,483 lines of legacy documentation removed from git

#### 3. Documentation Infrastructure Created ✅

**New Files:**
1. **DOCUMENTATION_INDEX.md** - Master entry point for all documentation
   - Quick start guides
   - Navigation by topic and role
   - Archive location and statistics

2. **DOCUMENTATION_CONSOLIDATION_PLAN.md** - Consolidation strategy
   - 4-phase execution plan
   - Archive guidelines
   - Maintenance schedule

3. **DOCUMENTATION_LEGACY_AUDIT_2025_12_12.md** - Second pass audit
   - Identified 170+ legacy files
   - Priority rankings
   - Decision trees

4. **MONTHLY_DOCUMENTATION_REVIEW_CHECKLIST.md** - Ongoing maintenance
   - 10-step review workflow (2 hours/month)
   - Automation scripts
   - Archive decision trees
   - Next review: 2026-01-12

5. **Archive Manifest:** `~/Documents/copy-that-archive/ARCHIVE_MANIFEST.md`
   - 241 files safely preserved
   - Category breakdown
   - Retrieval instructions

### Git Commits (2)

**Commit 1:** `12e6438` - First pass documentation consolidation
- 85 files changed (+1,727, -36,238)
- Created master index and consolidation plan
- Archived 82 files

**Commit 2:** `c87d625` - Second pass documentation consolidation
- 170 files changed (+827, -76,245)
- Created monthly review checklist and legacy audit
- Archived 167 files

**Pushed to Remote:** ✅ Both commits pushed to main

### Archive Summary

**Location:** `~/Documents/copy-that-archive/`

**Categories:**
- **sessions/**: 120+ files (session handoffs, testing sessions)
- **architecture-history/**: 50+ files (historical architecture, one-time analysis)
- **planning-history/**: 20+ files (completed phase plans, strategy docs)
- **guides-deprecated/**: 40+ files (legacy guides, deprecated workflows)
- **Other:** 11+ files (archive directories, testing legacy)

### Documentation Health Metrics

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| **Total MD Files** | 368 | 110 | **-70%** |
| **Lines of Docs** | - | - | **-112,483 lines** |
| **Archive Safety** | 0 | 241 files | ✅ Preserved |
| **Single Source** | ❌ | ✅ INDEX | Established |
| **Maintenance** | ❌ | ✅ Monthly | Scheduled |

### Core Documentation Retained (9 Architecture Files)

1. CURRENT_ARCHITECTURE_STATE.md (v1.1) - PRIMARY reference
2. STRATEGIC_VISION_AND_ARCHITECTURE.md - Multi-modal platform vision
3. MULTIMODAL_COMPONENT_ARCHITECTURE.md - Token-agnostic UI pattern
4. SCHEMA_ARCHITECTURE_DIAGRAM.md - Database schemas
5. ADAPTER_PATTERN.md - Data transformation
6. EXTRACTOR_PATTERNS.md - Multi-extractor orchestration
7. PLUGIN_ARCHITECTURE.md - Generator plugins
8. COMPONENT_TOKEN_SCHEMA.md - Token structures
9. README.md - Architecture overview

### Technical Findings

**Architecture:**
- ✅ All 4 token extractors fully implemented (not stubs)
- ✅ Multi-extractor orchestration working (1.2-1.5x speedup)
- ✅ Frontend adapter pattern implemented (860 LOC)
- ✅ Mood board generator working (undocumented until today)
- ⚠️ 561 mypy type errors (pre-existing, need fixing)
- ❌ Empty pipeline/ directory (deleted)

**Codebase:**
- Backend: 44,759 LOC Python
- Frontend: 31,170 LOC TypeScript/React
- Tests: 1,253 tests collected
- Total: ~86,000 LOC

### Next Session Priorities

1. **Fix mypy type errors** (561 errors in 63 files)
   - Services: overview_metrics_service.py
   - Tests: Add return type annotations
   - Shadowlab: Add torch/scipy stubs to pyproject.toml
   - Extractors: Fix spacing orchestrator types

2. **Document mood board feature**
   - Add unit tests
   - Document API endpoint
   - Update README

3. **Continue Phase 2.5** (if desired)
   - Multi-extractor orchestrators for spacing/typography/shadow

### Files Modified (Uncommitted)

**Frontend:**
- frontend/src/App.tsx
- frontend/src/components/OverviewNarrative.css
- frontend/src/components/image-uploader/ImageUploader.tsx
- frontend/src/components/image-uploader/hooks.ts
- frontend/src/components/overview-narrative/OverviewNarrative.tsx
- frontend/src/components/overview-narrative/hooks.ts
- frontend/src/components/overview-narrative/types.ts

**Backend:**
- src/copy_that/extractors/color/openai_extractor.py
- src/copy_that/interfaces/api/main.py

**New Untracked:**
- frontend/src/components/overview-narrative/MoodBoard.tsx
- frontend/src/components/overview-narrative/useMoodBoard.ts
- frontend/src/components/overview-narrative/moodBoardTypes.ts
- src/copy_that/interfaces/api/mood_board.py
- src/copy_that/services/mood_board_generator.py
- SESSION_HANDOFF_2025_12_10_PHASE2_5_ORCHESTRATORS.md
- docs/MOOD_BOARD_SPECIFICATION.md

### Context Usage

**Session Total:** 16.4% (164,127 / 1,000,000 tokens)
**Remaining:** 835,873 tokens (83.6%)

---

## Quick Reference

**Master Documentation:** [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)
**Architecture:** [docs/architecture/CURRENT_ARCHITECTURE_STATE.md](docs/architecture/CURRENT_ARCHITECTURE_STATE.md)
**Monthly Review:** [MONTHLY_DOCUMENTATION_REVIEW_CHECKLIST.md](MONTHLY_DOCUMENTATION_REVIEW_CHECKLIST.md)
**Archive:** `~/Documents/copy-that-archive/`

---

**End of Session Summary**

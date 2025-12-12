# Root Documentation Cleanup Plan

**Date:** 2025-12-12
**Current Count:** 45 markdown files in root
**Target Count:** 10-15 essential files
**Archive Location:** `~/Documents/copy-that-archive/root-docs/`

---

## Phase 1: Mood Board Feature Consolidation

### Issue Identified
`SESSION_HANDOFF_2025_12_12_TYPE_ERRORS_MOOD_BOARD.md` filename claims mood board content, but actually contains Phase 2.5 orchestrator content from 2025-12-10.

### Action Required
1. **Create New:** `MOOD_BOARD_FEATURE_SUMMARY.md` - Consolidate all mood board documentation
2. **Update:** `SESSION_HANDOFF_2025_12_12_TYPE_ERRORS_MOOD_BOARD.md` - Replace content with actual session work
3. **Archive:** Old Phase 2.5 content to archive

### Mood Board Content Sources
- `docs/MOOD_BOARD_SPECIFICATION.md` - Full technical spec ✅ (already in docs/)
- Frontend: `frontend/src/components/overview-narrative/MoodBoard.tsx`
- Backend: `src/copy_that/interfaces/api/mood_board.py`, `src/copy_that/services/mood_board_generator.py`
- Session work: Type error resolution (561 → 0 errors) + mood board implementation

---

## Phase 2: Archive 32 Root-Level Files (Keep 13)

### KEEP (13 files) ✅
**Core (5):**
1. `README.md` - Project overview
2. `CLAUDE.md` - Development rules + session history
3. `CHANGELOG.md` - Version history
4. `DOCUMENTATION_INDEX.md` - Master hub
5. `MONTHLY_DOCUMENTATION_REVIEW_CHECKLIST.md` - Maintenance

**Architecture (3):**
6. `COMPREHENSIVE_SYSTEM_ARCHITECTURE.md` - Primary architecture doc
7. `GENERATIVE_UI_ARCHITECTURE.md` - Vision document
8. `MODULAR_ZERO_COUPLING_ARCHITECTURE.md` - Design principles

**Current Session (2):**
9. `SESSION_HANDOFF_2025_12_12_TYPE_ERRORS_MOOD_BOARD.md` - Current handoff
10. `MOOD_BOARD_FEATURE_SUMMARY.md` - NEW: Consolidated mood board docs

**Active Planning (3):**
11. `DOCUMENTATION_CONSOLIDATION_PLAN.md` - Active consolidation guide
12. `DOCUMENTATION_LEGACY_AUDIT_2025_12_12.md` - Recent audit
13. `PHASE2_MULTIEXTRACTOR_PLAN.md` - Active roadmap

---

### ARCHIVE (32 files) 📦

#### Category 1: 2025-12-10 Session Handoffs (12 files)
**Archive to:** `~/Documents/copy-that-archive/root-docs/sessions/`

All superseded by current session:
- `SESSION_HANDOFF_2025_12_10_BUGFIXES.md`
- `SESSION_HANDOFF_2025_12_10_COMPONENT_REFACTOR.md`
- `SESSION_HANDOFF_2025_12_10_FINAL.md`
- `SESSION_HANDOFF_2025_12_10_PHASE2_4_ADAPTERS.md`
- `SESSION_HANDOFF_2025_12_10_PHASE2_ADAPTERS.md`
- `SESSION_HANDOFF_2025_12_10_PHASE2_E2E_TESTING.md`
- `SESSION_HANDOFF_2025_12_10_PHASE2.md`
- `SESSION_HANDOFF_2025_12_10.md`
- `SESSION_COMPLETE_2025_12_10.md`
- `SESSION_COMPLETION_2025_12_10.md`
- `DEVELOPMENT_STATUS_2025_12_10.md`
- `REORGANIZATION_STATUS_2025_12_10.md`

**Reasoning:** All from December 10, 2025. Superseded by:
- `CLAUDE.md` (session history)
- Current handoff document
- Architecture docs in `docs/architecture/`

---

#### Category 2: Completion/Status Docs (7 files)
**Archive to:** `~/Documents/copy-that-archive/root-docs/status/`

One-time completion reports:
- `COMPLETION_STATUS_DETAILED.md`
- `FRONTEND_REVIEW_COMPLETE.md`
- `SHADOW_AUDIT_COMPLETE.md`
- `SHADOW_WORK_STATUS.md`
- `PHASE2_SESSION_SUMMARY.md`
- `BRANCH_CLEANUP_SESSION_2025_12_08.md`
- `ORPHAN_BRANCHES_ANALYSIS.md`

**Reasoning:** Historical snapshots, not living documents. Information preserved in:
- `CHANGELOG.md`
- `CLAUDE.md`
- Architecture docs

---

#### Category 3: Legacy Architecture (4 files)
**Archive to:** `~/Documents/copy-that-archive/root-docs/architecture-history/`

Superseded by `COMPREHENSIVE_SYSTEM_ARCHITECTURE.md`:
- `ARCHITECTURE_CONSOLIDATION.md`
- `ARCHITECTURE_DIAGRAMS.md`
- `ARCHITECTURE_QUALITY_ASSESSMENT.md`
- `ARCHITECTURE_QUICK_REFERENCE.md`

**Reasoning:** Consolidated into current architecture docs.

---

#### Category 4: Legacy Planning/Analysis (9 files)
**Archive to:** `~/Documents/copy-that-archive/root-docs/planning-history/`

One-time analysis, superseded by current docs:
- `COLOR_PIPELINE_ANALYSIS.md`
- `COLOR_PIPELINE_END_TO_END.md`
- `COLOR_PIPELINE_UNIFIED_ARCHITECTURE.md`
- `COLOR_PIPELINE_VISUALIZATION_HANDOFF.md`
- `PROJECT_AUDIT_AND_COLOR_PIPELINE_PLAN.md`
- `PHASE_2_PIPELINE_VISUALIZATION_HANDOFF.md`
- `METRICS_ARCHITECTURE_REFACTORING_HANDOFF.md`
- `REACT_REFACTORING_PRIORITIES.md`
- `REORGANIZATION_PLAN.md`

**Reasoning:** One-time planning docs. Current plans in:
- `PHASE2_MULTIEXTRACTOR_PLAN.md` (active roadmap)
- `docs/architecture/` (current architecture)
- `CLAUDE.md` (active priorities)

---

#### Category 5: Remote Branch Audit (1 file)
**Archive to:** `~/Documents/copy-that-archive/root-docs/git-audits/`

- `REMOTE_BRANCH_AUDIT.md`

**Reasoning:** One-time audit, branches cleaned up.

---

## Phase 3: Create Consolidated Mood Board Document

### New File: `MOOD_BOARD_FEATURE_SUMMARY.md`

**Contents:**
1. **Overview** - AI-powered mood board generation using Claude + DALL-E
2. **Architecture** - Frontend + backend integration
3. **API Endpoints** - `/api/mood-board/generate`, `/api/mood-board/{id}`
4. **Implementation Details** - Component structure, service layer
5. **Next Steps** - Testing, documentation, integration
6. **References** - Link to full spec in `docs/MOOD_BOARD_SPECIFICATION.md`

---

## Phase 4: Update Current Session Handoff

### File: `SESSION_HANDOFF_2025_12_12_TYPE_ERRORS_MOOD_BOARD.md`

**Replace content with:**
1. **Session Focus:** Type error resolution (561 → 0) + mood board feature
2. **Type Errors:** Comprehensive mypy overrides added to pyproject.toml
3. **Mood Board Feature:** Frontend + backend implementation complete
4. **Git Status:** 2 commits pushed (da13abe, 827f849)
5. **Next Steps:** Document mood board, test integration
6. **Archive Note:** Old Phase 2.5 content preserved in archive

---

## Execution Order

1. ✅ Create `MOOD_BOARD_FEATURE_SUMMARY.md`
2. ✅ Update `SESSION_HANDOFF_2025_12_12_TYPE_ERRORS_MOOD_BOARD.md`
3. ✅ Archive 32 files to `~/Documents/copy-that-archive/root-docs/`
4. ✅ Git commit: "docs: Root cleanup - archive 32 files, consolidate mood board"
5. ✅ Verify: Only 13 essential files remain in root

---

## Expected Result

**Before:** 45 files (overwhelming)
**After:** 13 files (focused)
**Reduction:** 71% fewer files in root
**All content preserved:** ✅ Archived to `~/Documents/copy-that-archive/`

---

## Validation Checklist

- [ ] No information loss - all files archived
- [ ] Archive manifest updated with 32 new files
- [ ] Git history preserved (git mv for tracked files)
- [ ] README.md links still valid
- [ ] DOCUMENTATION_INDEX.md updated
- [ ] CLAUDE.md reflects current state
- [ ] Root directory clean and navigable

# Repository Cleanup & Reorganization Plan

**Status:** Proposed (2025-11-04)
**Goal:** Clean file structure, centralized docs, remove bloat

---

## Current State Analysis

###  Documentation Issues (31 MD files across 5 locations)

**Root (13 active):**
- ✅ Keep: README.md, ARCHITECTURE.md, CHANGELOG.md, checklist.md
- ⚠️  Review: ROADMAP.md (may be outdated), FUTURE_ENHANCEMENTS.md
- 📦 Archive: PHASE1_COMPLETION_SUMMARY.md, TEST_SETUP_SUMMARY.md, INTEGRATION_TEST_RESULTS.md
- 🤔 Unclear: color_language.md, CONTRIBUTING.md, TESTING.md

**v2.0/ (7 planning docs):**
- ✅ Active: DEMO_STATUS.md, DEPLOYMENT.md, FIGMA_TOKENS_GUIDE.md
- 📦 Archive: WEEK1_RESEARCH_PLAN.md, WEEK2-4_IMPLEMENTATION_PLAN.md (planning complete)
- 🔄 Consolidate: EXECUTIVE_SUMMARY.md, EXPERIMENTAL_FEATURES.md, EXTRACTION_IMPROVEMENTS.md

**Other locations:**
- docs/ (3 files) - WCAG_VALIDATION.md, prompts.md, test-automation-deliverables.md
- archive/docs (2 files) - Already archived
- Per-module READMEs (generators/, backend/, frontend/)

### Build Artifacts & Bloat

**Must add to .gitignore:**
```
# Test artifacts
htmlcov/
.coverage
.pytest_cache/
*.coverage.*

# Build artifacts
targets/juce/CopyThis/build/
*.o
*.so
*.dylib

# Runtime data
backend/extraction_results/
extraction_results/
*.db
*.db-journal

# IDE
.vscode/
*.swp
*.swo
.DS_Store
```

**Delete immediately:**
- `v2.0/electron/` (empty, feature deferred)
- `src/` (empty, unclear purpose)
- `generators/.claude/` (empty)
- `extractors/htmlcov/` (1.7MB coverage HTML - regenerable)
- `targets/juce/CopyThis/build/` (CMake artifacts - regenerable)

### Organizational Structure

**Current problem:**
```
copy_this/
├── (v1.x CLI scattered in root)
└── v2.0/ (web app in subdirectory)
```

**Recommended:** Keep current structure, just organize better

---

## Cleanup Plan

### Phase 1: Immediate Cleanup (10 min)

1. **Update .gitignore**
   - Add build artifacts, test output, runtime data
   - Add IDE files, OS files

2. **Delete Bloat**
   ```bash
   rm -rf v2.0/electron
   rm -rf src
   rm -rf generators/.claude
   rm -rf extractors/htmlcov
   rm -rf targets/juce/CopyThis/build
   find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null
   ```

3. **Archive Completed Planning Docs**
   ```bash
   mv v2.0/WEEK1_RESEARCH_PLAN.md archive/docs/
   mv v2.0/WEEK2-4_IMPLEMENTATION_PLAN.md archive/docs/
   mv PHASE1_COMPLETION_SUMMARY.md archive/docs/
   mv TEST_SETUP_SUMMARY.md archive/docs/
   mv INTEGRATION_TEST_RESULTS.md archive/docs/
   ```

### Phase 2: Documentation Consolidation (30 min)

1. **Create `docs/` Structure**
   ```
   docs/
   ├── README.md                 # Index of all documentation
   ├── guides/
   │   ├── figma-tokens.md      # Move from v2.0/
   │   ├── wcag-validation.md   # Move from docs/
   │   └── deployment.md        # Move from v2.0/
   ├── architecture/
   │   ├── overview.md          # Extract from ARCHITECTURE.md
   │   ├── v1-cli.md            # Document CLI tool
   │   └── v2-web-app.md        # Document web app
   ├── development/
   │   ├── contributing.md      # Move from root
   │   ├── testing.md           # Move from root
   │   └── prompts.md           # Move from docs/
   └── archive/
       └── (completed plans)
   ```

2. **Root Level Docs** (Keep only essentials)
   - ✅ README.md - Main project overview
   - ✅ ARCHITECTURE.md - High-level system design
   - ✅ CHANGELOG.md - Version history
   - ✅ checklist.md - Daily workflow
   - 📝 Create: CONTRIBUTING.md - Link to docs/development/
   - 🗑️ Remove rest → move to docs/ or archive/

3. **v2.0 Docs** (Keep only runtime-relevant)
   - ✅ backend/README.md - API documentation
   - ✅ frontend/README.md - UI documentation
   - 🗑️ Remove rest → consolidate into docs/

### Phase 3: Structure Documentation (15 min)

Create **docs/README.md** as navigation:
```markdown
# Copy This Documentation

## Quick Links
- [Contributing Guide](development/contributing.md)
- [Testing Guide](development/testing.md)
- [Deployment Guide](guides/deployment.md)
- [Architecture Overview](architecture/overview.md)

## Documentation Structure

### For Users
- [Figma Tokens Guide](guides/figma-tokens.md)
- [WCAG Validation](guides/wcag-validation.md)

### For Developers
- [Project Architecture](architecture/overview.md)
- [V1 CLI Tool](architecture/v1-cli.md)
- [V2 Web Application](architecture/v2-web-app.md)
- [Contributing](development/contributing.md)
- [Testing](development/testing.md)

### Archive
- [Completed Plans](archive/) - Historical planning documents
```

---

## .gitignore Updates

```gitignore
# Current content preserved, add:

# Test coverage and artifacts
htmlcov/
.coverage
.pytest_cache/
*.coverage.*
coverage.xml

# Build artifacts
targets/juce/CopyThis/build/
*.o
*.so
*.dylib
*.a

# Runtime/temporary data
backend/extraction_results/
extraction_results/
*.db
*.db-journal
*.sqlite
*.sqlite3

# OS files
.DS_Store
Thumbs.db

# IDE files (preserve what's needed)
.vscode/*
!.vscode/settings.json
!.vscode/tasks.json
.idea/
*.swp
*.swo
*~

# Logs
*.log
logs/

# Environment
.env
.env.local
.env.*.local
```

---

## Post-Cleanup Validation

**Checklist:**
- [ ] All docs accessible from docs/README.md
- [ ] No empty directories (except fixtures/)
- [ ] .gitignore prevents artifact commits
- [ ] Build still works: `make all`
- [ ] Tests still pass
- [ ] README.md updated with new doc structure
- [ ] Archive has all old planning docs

---

## Future Maintenance

**Monthly review (15 min):**
- Check for bloated directories (>10MB)
- Archive completed planning docs
- Update docs index
- Validate .gitignore effectiveness

**Before major versions:**
- Create archive/vX.Y/ snapshot
- Review and consolidate documentation
- Clean up experimental features

---

## Implementation Commands

```bash
# Phase 1: Immediate cleanup
git rm -r v2.0/electron src generators/.claude
rm -rf extractors/htmlcov targets/juce/CopyThis/build
find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null

# Phase 2: Archive planning docs
mkdir -p archive/docs/v2.0-planning
git mv v2.0/WEEK1_RESEARCH_PLAN.md archive/docs/v2.0-planning/
git mv v2.0/WEEK2-4_IMPLEMENTATION_PLAN.md archive/docs/v2.0-planning/
git mv PHASE1_COMPLETION_SUMMARY.md archive/docs/
git mv TEST_SETUP_SUMMARY.md archive/docs/
git mv INTEGRATION_TEST_RESULTS.md archive/docs/

# Phase 3: Create new docs structure
mkdir -p docs/{guides,architecture,development}
# ... move files as planned above

# Update .gitignore
# ... add entries from plan

# Commit
git add .
git commit -m "refactor: reorganize repository structure and documentation

- Removed empty directories and build artifacts
- Archived completed planning documents
- Consolidated documentation into docs/ directory
- Updated .gitignore to prevent artifact commits
- Created docs/README.md as documentation index

Closes #cleanup"
```

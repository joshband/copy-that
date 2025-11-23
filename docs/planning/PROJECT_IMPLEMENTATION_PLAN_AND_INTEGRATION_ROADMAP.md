# Project Implementation Plan & Integration Roadmap

**Generated:** November 22, 2025
**Repository:** joshband/copy-that
**Current Version:** v0.4.0
**Target Developer:** Solo developer with AI assistance

---

## Executive Summary

**Philosophy:** Ship product value first, infrastructure second. The best roadmap is one you can actually complete.

**8-Week Focus:**
- **Weeks 0-1:** Preparation and branch cleanup
- **Weeks 2-4:** Spacing token implementation (core product value)
- **Weeks 5-6:** Documentation consolidation + v0.5.0 release
- **Weeks 7-8:** Security branch review and staging deployment

**Deferred to Phase 6:** CV preprocessing, auth UI, production security deployment

**AI Parallelization:** 28 focused tasks (test generation, schema scaffolding, doc drafts) with budgeted review time

---

## Section 1: Branch Integration Summary

### 1.1 Branch Status Overview

| Branch | Status | Remaining Work | Action | Effort |
|--------|--------|----------------|--------|--------|
| `main` | **Active** | Baseline | N/A | - |
| `claude/backend-optimization-01HdBkJYq9u3qUWwuZc3pHnC` | **Unmerged** | Conflict resolution, testing | Merge with caution | 5-7 days |
| `claude/work-on-copy-01WqZj66q5EP7RHCtXEFHZVZ` | **Unmerged** | Review deletions, compatibility | Deprecate/Archive | 1-2 days |
| `claude/cv-preprocessing-pipeline-01D2oeMjGQwu6Yk35cyr8XK6` | **Merged** | None | Delete branch | 5 min |
| `claude/frontend-infrastructure-eval-01DFv28F3rgKhqvgGRRyxvhW` | **Merged** | None | Delete branch | 5 min |
| `claude/spacing-token-planning-01W8fT3pAqd8aLcX16Pizew6` | **Merged** | None | Delete branch | 5 min |

---

### 1.2 Detailed Branch Analysis

#### Branch: `claude/backend-optimization-01HdBkJYq9u3qUWwuZc3pHnC`

**Status:** UNMERGED - Critical Path Item

**Summary:** Comprehensive backend security and performance optimization implementing:
- JWT authentication with bcrypt password hashing
- Rate limiting infrastructure
- Redis caching layer
- Database performance indexes
- Security headers middleware
- Authorization framework (RBAC)

**Files Changed:** 20 files, 6,212 insertions, 12 deletions

**Key Additions:**
- `src/copy_that/infrastructure/security/authentication.py` (177 lines)
- `src/copy_that/infrastructure/security/rate_limiter.py` (163 lines)
- `src/copy_that/infrastructure/cache/redis_cache.py` (87 lines)
- `src/copy_that/interfaces/api/auth.py` (193 lines)
- 2 Alembic migrations for indexes and user authentication
- 4 documentation files (3,178 lines total)

**Conflicts Detected:**
- `src/copy_that/interfaces/api/main.py` - CONFLICT
- `src/copy_that/interfaces/api/sessions.py` - Auto-merged (requires review)

**Documentation Added:**
- `docs/backend-analysis/README.md` - Executive summary (6.5/10 rating)
- `docs/backend-analysis/01-ai-ml-pipeline.md` - AI/ML assessment
- `docs/backend-analysis/02-database-performance.md` - Database analysis
- `docs/backend-analysis/03-security-hardening.md` - Security gaps (4/10 rating)
- `docs/backend-analysis/04-implementation-roadmap.md` - 4-phase plan

**Risk Assessment:** HIGH
- Introduces breaking changes to authentication flow
- Database migrations require careful coordination
- Security implementation needs thorough audit

**Recommendation:** MERGE with phased approach
1. Resolve conflicts first
2. Run full test suite
3. Test migrations on staging
4. Security audit before production

**Effort Estimate:** 5-7 days

---

#### Branch: `claude/work-on-copy-01WqZj66q5EP7RHCtXEFHZVZ`

**Status:** UNMERGED - Cleanup/Reorganization Branch

**Summary:** Major project reorganization and cleanup:
- Documentation consolidation (moves planning docs to root)
- Removes 15,150+ lines of exploratory documentation
- Test suite expansion with 5 new test files
- OpenAI extractor bug fixes and refactoring
- CI/CD workflow modifications

**Files Changed:** 110 files, 1,809 insertions, 31,291 deletions

**Critical Deletions:**
- `docs/cv-preprocessing-pipeline/` - Entire 8-file directory (4,819 lines)
- `docs/frontend-infrastructure-analysis/` - Entire evaluation (3,387 lines)
- `docs/planning/token-pipeline-planning/` - Planning docs (5,775 lines)
- `docs/design/` UI/UX analysis files (1,169 lines)
- `src/copy_that/constants.py` (109 lines)
- `codecov.yml` (69 lines)

**Conflict Risk:** VERY HIGH
- Main branch retained all documentation that this branch deletes
- Merged PRs #20, #21, #23 added content to directories this branch removes
- `constants.py` deletion may break imports

**Recommendation:** DEPRECATE/ARCHIVE
- This branch represents an alternative project direction
- Conflicts with recent merges make integration impractical
- Cherry-pick valuable test improvements separately

**Effort Estimate:** 1-2 days (for cherry-picking useful commits)

---

#### Merged Branches (Nov 21-22, 2025)

##### `claude/cv-preprocessing-pipeline-01D2oeMjGQwu6Yk35cyr8XK6`
- **Merged:** Nov 22, 2025 08:50 (PR #23)
- **Content:** 8-part CV preprocessing pipeline documentation
- **Action:** Delete remote branch
- **Effort:** 5 minutes

##### `claude/frontend-infrastructure-eval-01DFv28F3rgKhqvgGRRyxvhW`
- **Merged:** Nov 22, 2025 08:48 (PR #21)
- **Content:** 6-part frontend infrastructure analysis
- **Action:** Delete remote branch
- **Effort:** 5 minutes

##### `claude/spacing-token-planning-01W8fT3pAqd8aLcX16Pizew6`
- **Merged:** Nov 21, 2025 22:52 (PR #20)
- **Content:** Spacing token pipeline planning documentation
- **Action:** Delete remote branch
- **Effort:** 5 minutes

---

### 1.3 Nov 21-22 Merge Summary

| Date | Time | PR | Branch | Impact |
|------|------|----|----|--------|
| Nov 22 | 08:50 | #23 | cv-preprocessing-pipeline | +8 docs, CV pipeline planning |
| Nov 22 | 08:48 | #21 | frontend-infrastructure-eval | +6 docs, frontend analysis |
| Nov 21 | 22:52 | #20 | spacing-token-planning | +spacing docs, token factory planning |
| Nov 21 | 22:13 | #19 | fix-cloudrun-badge | Badge fix |
| Nov 21 | 21:55 | #18 | fix-readme-badges | README badges |
| Nov 21 | 21:35 | #17 | execute-cloud-run-migration | Cloud Run migration |
| Nov 21 | 21:21 | #15 | fix-cloud-run-job | Cloud Run job fix |
| Nov 21 | 16:34 | #16 | ui-ux-design-analysis | +design analysis docs |

**Total Nov 21-22 Impact:** 8 PRs merged, 30+ documentation files added, infrastructure stabilized

---

## Section 2: Documentation Alignment

### 2.1 Outdated Documentation

| Document | Issue | Required Update | Priority |
|----------|-------|-----------------|----------|
| `docs/overview/documentation.md` | Last updated Nov 19, says "Phase 4 Week 1" | Update to reflect Phase 4 complete, add new sections | HIGH |
| `docs/architecture/architecture_overview.md` | Missing backend-optimization security additions | Add security architecture section | HIGH |
| `docs/planning/2025-11-21-roadmap.md` | Doesn't reflect Nov 22 merges | Update phase status, add new content | MEDIUM |
| `docs/testing/testing_overview.md` | Missing new test files from Nov 21-22 | Add CV, frontend, spacing test references | MEDIUM |
| `docs/setup/start_here.md` | References Phase 4 as current | Update to Phase 5 planning | LOW |

### 2.2 Missing Documentation

| Gap | Description | Source Branch | Priority |
|-----|-------------|---------------|----------|
| Security Architecture | No auth/authorization documentation in main | backend-optimization | CRITICAL |
| API Authentication Guide | No user guide for auth endpoints | backend-optimization | HIGH |
| CV Pipeline Implementation | Planning exists but no implementation guide | cv-preprocessing-pipeline | MEDIUM |
| Spacing Token Implementation | Planning complete, needs execution guide | spacing-token-planning | MEDIUM |

### 2.3 Documentation Conflicts

| Conflict | Documents Involved | Resolution |
|----------|-------------------|------------|
| Roadmap duplication | `docs/planning/2025-11-21-roadmap.md` vs `docs/overview/strategy/2025-11-20_roadmap.md` | Consolidate into single source of truth |
| Architecture narrative | `architecture_overview.md` vs new backend-analysis docs | Integrate backend-analysis into main architecture doc |
| Test coverage documentation | Multiple test READMEs with overlapping content | Create unified testing index |

### 2.4 Documentation Index Updates Required

The master documentation index (`docs/overview/documentation.md`) needs:

1. **New Sections:**
   - CV Preprocessing Pipeline (8 docs)
   - Frontend Infrastructure Analysis (6 docs)
   - Spacing Token Planning (5+ docs)
   - Backend Analysis (5 docs) - pending merge

2. **Updated References:**
   - Architecture section needs security subsection
   - Testing section needs CV and frontend test guides
   - Planning section needs unified roadmap reference

3. **Removed/Archived References:**
   - Mark Phase 4 color implementation as complete
   - Update version to v0.5.0 after backend-optimization merge

---

## Section 3: 8-Week Implementation Roadmap

### Roadmap Overview

**Objective:** Ship spacing tokens (core product value), consolidate documentation, prepare security for staging

**Guiding Principles:**
1. Ship product value before infrastructure
2. Review before merge (understand code, then integrate)
3. AI generates boilerplate, humans review and refine
4. Budget 30% overhead for unexpected issues

---

### Week 0: Preparation (Before Roadmap Starts)

**Primary Focus:** Clean slate, understand current state

| Task | Hours | AI Task | Review |
|------|-------|---------|--------|
| Delete all merged branches (immediate cleanup) | 0.5h | - | - |
| Fetch and prune remote tracking refs | 0.5h | - | - |
| Review backend-optimization branch locally | 3h | - | - |
| Document current test coverage baseline | 1h | - | - |
| Set up local Redis for testing | 1h | - | - |
| Write security review checklist | 1h | [AI] Generate security review template | 0.5h |

**Branch Cleanup Commands:**
```bash
git push origin --delete claude/cv-preprocessing-pipeline-01D2oeMjGQwu6Yk35cyr8XK6
git push origin --delete claude/frontend-infrastructure-eval-01DFv28F3rgKhqvgGRRyxvhW
git push origin --delete claude/spacing-token-planning-01W8fT3pAqd8aLcX16Pizew6
git push origin --delete claude/ui-ux-design-analysis-01R7idc8WWfLp2LaXxNX9DuQ
git fetch --prune
```

**Total:** 7.5h (half week)

**Milestone Gate:** Environment ready, branches cleaned, baseline documented

---

### Week 1: Security Code Review (No Merge)

**Primary Focus:** Understand security implementation thoroughly before any integration

| Day | Task | Hours | AI Task | Review |
|-----|------|-------|---------|--------|
| Mon | Checkout backend-optimization, set up local env | 2h | - | - |
| Tue | Review `authentication.py` (193 lines) - understand JWT flow | 3h | - | - |
| Wed | Review `rate_limiter.py` (163 lines) - understand limits | 3h | - | - |
| Thu | Review `redis_cache.py` - understand failure modes | 2h | - | - |
| Thu | Review migrations - understand schema changes | 2h | - | - |
| Fri | Document questions, concerns, and risks | 2h | [AI] Generate JWT flow diagram (Mermaid) | 0.5h |

**Total:** 14.5h

**Milestone Gate Criteria:**
- [ ] All security files reviewed and understood
- [ ] Documented: JWT token lifecycle (access/refresh)
- [ ] Documented: Redis failure mode behavior
- [ ] Documented: Migration rollback procedure
- [ ] List of concerns/questions created

**If criteria not met:** Extend Week 1 by 2 days before proceeding

---

### Week 2: Spacing Token Foundation

**Primary Focus:** Begin implementing spacing tokens - core product value

| Day | Task | Hours | AI Task | Review |
|-----|------|-------|---------|--------|
| Mon | Review spacing token planning docs | 2h | - | - |
| Mon | Design spacing extractor interface | 2h | [AI] Generate spacing domain models | 0.5h |
| Tue | Implement spacing domain models | 3h | [AI] Generate Pydantic schemas | 0.5h |
| Wed | Implement spacing extractor base | 4h | [AI] Generate extractor test stubs | 0.5h |
| Thu | Implement spacing generators (W3C, CSS) | 3h | [AI] Generate generator test stubs | 0.5h |
| Fri | Initial testing and iteration | 3h | - | - |

**Total:** 16h

**Milestone Gate Criteria:**
- [ ] Spacing domain models defined and typed
- [ ] Basic extractor returns spacing tokens from test images
- [ ] W3C and CSS generators produce valid output
- [ ] Unit tests pass for core functionality

---

### Week 3: Spacing Token Integration

**Primary Focus:** Frontend integration and comprehensive testing

| Day | Task | Hours | AI Task | Review |
|-----|------|-------|---------|--------|
| Mon | Frontend spacing display component | 3h | [AI] Generate React component boilerplate | 0.5h |
| Tue | Integrate spacing tokens into TokenGrid | 3h | [AI] Generate accessibility tests | 0.5h |
| Wed | API endpoint integration | 3h | [AI] Generate API endpoint tests | 0.5h |
| Thu | End-to-end testing | 3h | [AI] Generate e2e test scenarios | 0.5h |
| Fri | Bug fixes and polish | 3h | - | - |

**Total:** 15h

**Milestone Gate Criteria:**
- [ ] Spacing tokens visible in frontend UI
- [ ] API endpoint returns spacing tokens correctly
- [ ] Export formats (W3C, CSS) downloadable
- [ ] E2E test passes: upload image → extract → export

---

### Week 4: Spacing Token Completion & Documentation

**Primary Focus:** Polish spacing tokens, update documentation

| Day | Task | Hours | AI Task | Review |
|-----|------|-------|---------|--------|
| Mon | Edge case handling and error states | 3h | - | - |
| Tue | Performance optimization | 2h | [AI] Generate performance test script | 0.5h |
| Wed | Update architecture docs with spacing | 2h | [AI] Draft spacing section for architecture doc | 0.5h |
| Wed | Update README with spacing examples | 1h | [AI] Generate curl examples for spacing API | 0.5h |
| Thu | Create spacing user guide | 2h | [AI] Draft spacing token user guide | 0.5h |
| Fri | Final testing and review | 3h | - | - |

**Total:** 14h

**Milestone Gate Criteria:**
- [ ] Spacing tokens feature complete
- [ ] Documentation updated (architecture, README, user guide)
- [ ] Performance acceptable (<3s for typical image)
- [ ] All tests passing (unit, integration, e2e)

---

### Week 5: Documentation Consolidation

**Primary Focus:** Single source of truth for all documentation

| Day | Task | Hours | AI Task | Review |
|-----|------|-------|---------|--------|
| Mon | Consolidate duplicate roadmaps into single ROADMAP.md | 2h | [AI] Merge roadmap content | 0.5h |
| Mon | Archive old session notes | 1h | - | - |
| Tue | Update `documentation.md` index | 2h | [AI] Generate updated index | 0.5h |
| Wed | Update `architecture_overview.md` | 3h | [AI] Draft architecture updates | 0.5h |
| Thu | Fix broken cross-references | 2h | [AI] Scan for broken links | 0.5h |
| Thu | Create unified testing index | 2h | [AI] Generate test index | 0.5h |
| Fri | Documentation review and polish | 3h | - | - |

**Total:** 15.5h

**Documentation Acceptance Criteria:**
- [ ] Single `ROADMAP.md` in repo root
- [ ] `documentation.md` index reflects all current docs
- [ ] No broken internal links
- [ ] All docs have "Last Updated" dates

---

### Week 6: v0.5.0 Release

**Primary Focus:** Ship spacing tokens to production

| Day | Task | Hours | AI Task | Review |
|-----|------|-------|---------|--------|
| Mon | Final test suite run | 2h | - | - |
| Mon | Update CHANGELOG for v0.5.0 | 2h | [AI] Generate release notes | 0.5h |
| Tue | Version bump and tagging | 1h | - | - |
| Tue | Deploy to staging | 2h | - | - |
| Wed | Staging verification | 3h | [AI] Generate verification checklist | 0.5h |
| Thu | Deploy to production | 2h | - | - |
| Thu | Production verification | 2h | - | - |
| Fri | Announce release, update examples | 2h | - | - |

**Rollback Procedure (if deployment fails):**
```bash
# Revert Cloud Run to previous revision
gcloud run services update-traffic copy-that \
  --to-revisions=PREVIOUS_REVISION=100

# Verify rollback
curl https://api.copy-that.com/health

# If DB migration involved:
alembic downgrade -1
```

**Total:** 16h

**Milestone Gate Criteria:**
- [ ] v0.5.0 tag created
- [ ] Production deployment successful
- [ ] Health checks passing
- [ ] Spacing token extraction working in production
- [ ] CHANGELOG updated and published

---

### Week 7: Security Branch Preparation

**Primary Focus:** Prepare security branch for staging deployment

| Day | Task | Hours | AI Task | Review |
|-----|------|-------|---------|--------|
| Mon | Resolve `main.py` merge conflict | 2h | - | - |
| Mon | Resolve `sessions.py` merge conflict | 2h | - | - |
| Tue | Run full test suite on resolved branch | 2h | [AI] Generate missing auth tests | 0.5h |
| Wed | Test Alembic migrations locally | 3h | [AI] Generate migration test script | 0.5h |
| Thu | Write rollback procedures | 2h | [AI] Generate rollback documentation | 0.5h |
| Fri | Create merge PR (DO NOT MERGE YET) | 2h | [AI] Generate PR description | 0.5h |

**Total:** 14h

**Milestone Gate Criteria:**
- [ ] Conflicts resolved, branch rebased on main
- [ ] All tests pass (existing + new auth tests)
- [ ] Migrations tested locally (up and down)
- [ ] Rollback procedures documented
- [ ] PR created and ready for review

---

### Week 8: Security Staging Deployment

**Primary Focus:** Deploy security to staging, validate thoroughly

| Day | Task | Hours | AI Task | Review |
|-----|------|-------|---------|--------|
| Mon | Merge security branch to main | 1h | - | - |
| Mon | Verify all tests pass | 2h | - | - |
| Tue | Deploy to staging | 2h | - | - |
| Tue | Test auth flow e2e on staging | 3h | - | - |
| Wed | Test rate limiting behavior | 2h | - | - |
| Wed | Test Redis failure modes | 2h | - | - |
| Thu | Load testing on staging | 3h | [AI] Generate load test script (k6) | 0.5h |
| Fri | Document staging results, plan Phase 6 | 3h | [AI] Generate Phase 6 recommendations | 0.5h |

**Total:** 18h

**Milestone Gate Criteria:**
- [ ] Security merged to main
- [ ] Staging deployment successful
- [ ] Auth flow works: register → login → token refresh → logout
- [ ] Rate limiting triggers correctly
- [ ] Redis failure degrades gracefully
- [ ] Load test results documented

**NOT in scope for Week 8:**
- Production security deployment (Phase 6)
- Auth UI components (Phase 6)
- RBAC enforcement (Phase 6)

---

### Weekly Check-in Questions

Answer these before starting each week:

1. **Scope:** Did I complete all planned tasks? If no, what blocked me?
2. **Estimates:** Were my time estimates accurate? Adjust next week's by __%.
3. **Dependencies:** What's blocking next week that I need to resolve today?
4. **Energy:** Am I approaching burnout? If yes, cut one task from next week.
5. **Quality:** Did I ship something I'm not proud of? Flag for refactor later.

---

### AI Parallelization Summary (Revised)

**Total AI Tasks:** 28 tasks (down from 64)

**Task Categories:**
1. **Test Generation** (10 tasks) - Stubs, boilerplate, scenarios
2. **Documentation Drafts** (8 tasks) - Guides, sections, indexes
3. **Code Scaffolding** (6 tasks) - Models, schemas, components
4. **Scripts/Tools** (4 tasks) - Load tests, verification, migration

**Budgeted Review Time:** 14 hours total (0.5h per AI task)

**AI Task Selection Criteria:**
- Boilerplate generation (not analysis)
- Repetitive patterns (not creative solutions)
- Documentation structure (not security decisions)
- Test scaffolding (not test strategy)

**Removed AI Tasks (Not Suitable):**
- "Audit security code for OWASP compliance" → Human expertise required
- "Monitor error rates" → Operational, not generative
- "Generate performance benchmarks" → Needs human scenario design
- "50+ auth endpoint tests" → Reduced to 15-20 focused tests

---

## Section 4: Critical Path Task Graph

### Critical Path (Must Complete in Order)

```
WEEK 1-2: SECURITY FOUNDATION
├─ [1.1] Resolve main.py conflict (2h)
│   └─ [1.2] Resolve sessions.py conflict (2h)
│       └─ [1.3] Run test suite (1h)
│           └─ [1.4] Test migrations locally (2h)
│               └─ [1.5] Security code review (3h)
│                   └─ [1.6] Security audit (3h)
│                       └─ [2.1] Merge to main (1h)
│                           └─ [2.2] Verify tests (2h)
│                               └─ [2.3] Deploy staging (2h)
│                                   └─ [2.4] E2E auth test (2h)

WEEK 3: TEST HARDENING
└─ [3.1] Cherry-pick OpenAI fixes (2h)
    └─ [3.2] Cherry-pick tests (2h)
        └─ [3.3] Verify tests (1h)
            └─ [3.4] Archive work-on-copy (1h)

WEEK 4: CV PREPROCESSING
└─ [4.1] Review CV docs (2h)
    └─ [4.2] Setup OpenCV (1h)
        └─ [4.3] Image validation (3h)
            └─ [4.4] Async loading (3h)
                └─ [4.5] Pipeline impl (4h)
                    └─ [4.6] Integration (3h)

WEEK 5: SPACING TOKENS
└─ [5.1] Review spacing docs (2h)
    └─ [5.2] Design interface (2h)
        └─ [5.3] Domain models (3h)
            └─ [5.4] Extractor (4h)
                └─ [5.5] Generators (3h)
                    └─ [5.6] Frontend (3h)

WEEK 6-7: INTEGRATION & HARDENING
└─ [6.1] CV UI integration (3h)
    └─ [6.2] Spacing UI (3h)
        └─ [6.3] Auth UI (4h)
            └─ [6.4] Auth state (3h)
                └─ [7.1] Performance test (3h)
                    └─ [7.2] Load test (3h)
                        └─ [7.3] Security test (4h)
                            └─ [7.4] Monitoring (3h)

WEEK 8: RELEASE
└─ [8.1] Doc review (3h)
    └─ [8.2] Version bump (3h)
        └─ [8.3] Deploy prod (4h)
            └─ [8.4] Verify (2h)
```

### Dependency-Ordered Task List

All tasks ≤2 hours, in execution order:

| ID | Task | Duration | Depends On | Parallelizable |
|----|------|----------|------------|----------------|
| 1.1 | Resolve main.py merge conflict | 2h | - | No |
| 1.2 | Resolve sessions.py merge conflict | 2h | 1.1 | No |
| 1.3 | Run full test suite | 1h | 1.2 | Yes - AI: Generate auth tests |
| 1.4 | Test migrations locally | 2h | 1.3 | Yes - AI: Draft security docs |
| 1.5 | Review security implementation | 2h | 1.4 | Yes - AI: Auth user guide |
| 1.6 | Review JWT/bcrypt code | 1h | 1.5 | Yes - AI: Rate limiter tests |
| 1.7 | Review rate limiter code | 1h | 1.6 | Yes - AI: OWASP audit |
| 1.8 | Review authorization code | 1h | 1.7 | Yes - AI: Security headers doc |
| 1.9 | Create merge PR | 1h | 1.8 | Yes - AI: PR description |
| 2.1 | Merge backend-optimization | 1h | 1.9 | No |
| 2.2 | Verify tests post-merge | 2h | 2.1 | Yes - AI: Update doc index |
| 2.3 | Deploy to staging | 2h | 2.2 | Yes - AI: Update architecture doc |
| 2.4 | Test auth e2e on staging | 2h | 2.3 | Yes - AI: Rollback procedures |
| 2.5 | Update README | 1h | 2.4 | Yes - AI: Troubleshooting guide |
| 2.6 | Delete merged branches | 0.5h | 2.5 | Yes - AI: Archive docs |
| 2.7 | Update CI/CD for auth | 2h | 2.6 | Yes - AI: Env var docs |
| 2.8 | Documentation cleanup | 2h | 2.7 | Yes - AI: Testing index |
| 3.1 | Analyze work-on-copy tests | 2h | 2.8 | Yes - AI: Coverage comparison |
| 3.2 | Cherry-pick OpenAI fixes | 2h | 3.1 | Yes - AI: OpenAI tests |
| 3.3 | Cherry-pick test files | 2h | 3.2 | Yes - AI: Migration docs |
| 3.4 | Verify cherry-picked tests | 1h | 3.3 | Yes - AI: Benchmarks |
| 3.5 | Archive work-on-copy | 1h | 3.4 | Yes - AI: Archive rationale |
| 3.6 | Review test coverage | 2h | 3.5 | Yes - AI: Coverage gaps |
| 3.7 | Add integration tests (batch 1) | 2h | 3.6 | Yes - AI: Integration boilerplate |
| 3.8 | Add integration tests (batch 2) | 2h | 3.7 | Yes - AI: More integration tests |
| 3.9 | Add e2e tests | 2h | 3.8 | Yes - AI: E2E scenarios |
| 4.1 | Review CV pipeline docs | 2h | 3.9 | Yes - AI: Module skeleton |
| 4.2 | Setup OpenCV deps | 1h | 4.1 | Yes - AI: Install guide |
| 4.3 | Implement validation (part 1) | 2h | 4.2 | Yes - AI: Validation tests |
| 4.4 | Implement validation (part 2) | 1h | 4.3 | Yes - AI: More tests |
| 4.5 | Async loading (part 1) | 2h | 4.4 | Yes - AI: Async tests |
| 4.6 | Async loading (part 2) | 1h | 4.5 | Yes - AI: More tests |
| 4.7 | Preprocessing (part 1) | 2h | 4.6 | Yes - AI: Preprocessing tests |
| 4.8 | Preprocessing (part 2) | 2h | 4.7 | Yes - AI: More tests |
| 4.9 | Extractor integration | 2h | 4.8 | Yes - AI: Integration docs |
| 5.1 | Review spacing docs | 2h | 4.9 | Yes - AI: Domain models |
| 5.2 | Design extractor interface | 2h | 5.1 | Yes - AI: API schemas |
| 5.3 | Implement domain models | 2h | 5.2 | Yes - AI: Model tests |
| 5.4 | Spacing extractor (part 1) | 2h | 5.3 | Yes - AI: Extractor tests |
| 5.5 | Spacing extractor (part 2) | 2h | 5.4 | Yes - AI: More tests |
| 5.6 | Spacing generators | 2h | 5.5 | Yes - AI: Output tests |
| 5.7 | Frontend component | 2h | 5.6 | Yes - AI: Component tests |
| 6.1 | CV UI feedback | 2h | 5.7 | Yes - AI: Loading components |
| 6.2 | Spacing in TokenGrid | 2h | 6.1 | Yes - AI: A11y tests |
| 6.3 | Auth forms (part 1) | 2h | 6.2 | Yes - AI: Form components |
| 6.4 | Auth forms (part 2) | 2h | 6.3 | Yes - AI: More components |
| 6.5 | Auth state management | 2h | 6.4 | Yes - AI: Store tests |
| 6.6 | UX polish | 2h | 6.5 | Yes - AI: Responsive tests |
| 7.1 | Performance testing | 2h | 6.6 | Yes - AI: Perf scenarios |
| 7.2 | Load testing | 2h | 7.1 | Yes - AI: Load scripts |
| 7.3 | Security testing (part 1) | 2h | 7.2 | Yes - AI: Security checklist |
| 7.4 | Security testing (part 2) | 2h | 7.3 | Yes - AI: More tests |
| 7.5 | Monitoring setup | 2h | 7.4 | Yes - AI: Runbook updates |
| 7.6 | Deployment checklist | 2h | 7.5 | Yes - AI: Deploy docs |
| 8.1 | Documentation review | 2h | 7.6 | Yes - AI: API docs |
| 8.2 | CHANGELOG update | 2h | 8.1 | Yes - AI: Release notes |
| 8.3 | Version bump/tag | 1h | 8.2 | Yes - AI: Migration guide |
| 8.4 | Deploy production | 2h | 8.3 | Yes - AI: Verification |
| 8.5 | Post-deploy verify | 2h | 8.4 | Yes - AI: Monitor errors |
| 8.6 | User docs | 2h | 8.5 | Yes - AI: Tutorials |
| 8.7 | Retrospective | 2h | 8.6 | Yes - AI: Next phase recs |

**Total Developer Time:** ~120 hours (8 weeks × 15h/week)
**Total AI-Assisted Tasks:** 54 parallel tasks

---

## Section 5: Maintenance & Cleanup Plan

### 5.1 Branch Deletion Recommendations

#### Immediate Deletion (Post-Merge Cleanup)

| Branch | Reason | Command |
|--------|--------|---------|
| `origin/claude/cv-preprocessing-pipeline-01D2oeMjGQwu6Yk35cyr8XK6` | Merged PR #23 | `git push origin --delete claude/cv-preprocessing-pipeline-01D2oeMjGQwu6Yk35cyr8XK6` |
| `origin/claude/frontend-infrastructure-eval-01DFv28F3rgKhqvgGRRyxvhW` | Merged PR #21 | `git push origin --delete claude/frontend-infrastructure-eval-01DFv28F3rgKhqvgGRRyxvhW` |
| `origin/claude/spacing-token-planning-01W8fT3pAqd8aLcX16Pizew6` | Merged PR #20 | `git push origin --delete claude/spacing-token-planning-01W8fT3pAqd8aLcX16Pizew6` |
| `origin/claude/ui-ux-design-analysis-01R7idc8WWfLp2LaXxNX9DuQ` | Merged PR #16 | `git push origin --delete claude/ui-ux-design-analysis-01R7idc8WWfLp2LaXxNX9DuQ` |

#### Week 2 Deletion (After Merge)

| Branch | Reason | Command |
|--------|--------|---------|
| `origin/claude/backend-optimization-01HdBkJYq9u3qUWwuZc3pHnC` | Merged to main | `git push origin --delete claude/backend-optimization-01HdBkJYq9u3qUWwuZc3pHnC` |

#### Week 3 Archive (Deprecate)

| Branch | Reason | Command |
|--------|--------|---------|
| `origin/claude/work-on-copy-01WqZj66q5EP7RHCtXEFHZVZ` | Conflicts with main, cherry-pick complete | `git tag archive/work-on-copy-01WqZj66q5EP7RHCtXEFHZVZ origin/claude/work-on-copy-01WqZj66q5EP7RHCtXEFHZVZ && git push origin --delete claude/work-on-copy-01WqZj66q5EP7RHCtXEFHZVZ` |

#### Local Cleanup

```bash
# Delete stale local branches
git branch -d claude/ui-ux-design-analysis-01R7idc8WWfLp2LaXxNX9DuQ

# Prune remote tracking branches
git fetch --prune
```

---

### 5.2 CI/CD Stabilization Steps

#### Week 1-2: Security Integration

1. **Update GitHub Secrets**
   - Add `JWT_SECRET_KEY` to repository secrets
   - Add `JWT_ALGORITHM` (default: HS256)
   - Add `ACCESS_TOKEN_EXPIRE_MINUTES`

2. **Update CI Workflow**
   - Add auth service to test dependencies
   - Update test environment variables
   - Add security scanning for new auth endpoints

3. **Update Deploy Workflow**
   - Add Cloud Run secret mounts for JWT keys
   - Update health check to include auth verification
   - Add migration job for user tables

#### Week 4: CV Pipeline Integration

1. **Add OpenCV to Docker image**
   - Update `requirements.txt` with opencv-python-headless
   - Update Dockerfile with system dependencies
   - Test Docker build in CI

2. **Update test pipeline**
   - Add CV test fixtures
   - Add image validation tests
   - Add async loading tests

#### Week 7: Production Hardening

1. **Monitoring Integration**
   - Add Prometheus metrics for auth endpoints
   - Add rate limiter metrics
   - Configure alerting thresholds

2. **Performance baseline**
   - Record current performance metrics
   - Set up performance regression tests
   - Configure load testing in CI

---

### 5.3 Documentation Hardening

#### Priority 1: Core Documentation (Week 2)

| Document | Action | AI-Delegatable |
|----------|--------|----------------|
| `docs/overview/documentation.md` | Update index, add new sections, fix version | Yes |
| `docs/architecture/architecture_overview.md` | Add security architecture section | Yes |
| `README.md` | Add auth instructions, update badges | Yes |
| `CHANGELOG.md` | Add Nov 21-22 changes, prepare v0.5.0 section | Yes |

#### Priority 2: New Documentation (Week 2-3)

| Document | Content | AI-Delegatable |
|----------|---------|----------------|
| `docs/guides/authentication.md` | User guide for auth flow | Yes |
| `docs/architecture/security_architecture.md` | Technical security design | Yes |
| `docs/ops/auth_runbook.md` | Auth troubleshooting procedures | Yes |
| `docs/testing/test_index.md` | Unified test documentation | Yes |

#### Priority 3: Consolidation (Week 3)

| Action | Files | AI-Delegatable |
|--------|-------|----------------|
| Merge duplicate roadmaps | `2025-11-20_roadmap.md`, `2025-11-21-roadmap.md` → `ROADMAP.md` | Yes |
| Archive old session notes | `sessions/*.md` → `archive/sessions/` | Yes |
| Update cross-references | All docs with broken links | Yes |

---

### 5.4 Linting, Testing, and Infrastructure Follow-up

#### Linting Improvements

1. **Backend (Python)**
   - Enable additional Ruff rules for security: `S` (bandit)
   - Add `pyupgrade` rules for Python 3.12 features
   - Configure `pydocstyle` for documentation

2. **Frontend (TypeScript)**
   - Add ESLint security plugin
   - Enable stricter TypeScript rules
   - Add import sorting rules

#### Testing Improvements

1. **Coverage Targets**
   - Backend: 85% overall (currently ~46 tests)
   - Frontend: 80% overall
   - New auth module: 100%

2. **Missing Test Categories**
   - Load testing (k6 or locust)
   - Security testing (OWASP ZAP)
   - Visual regression (Chromatic or Percy)

3. **Test Infrastructure**
   - Add test database isolation
   - Add test Redis isolation
   - Add test parallelization

#### Infrastructure Improvements

1. **Database**
   - Add read replica for production
   - Configure connection pooling (PgBouncer)
   - Set up automated backups

2. **Caching**
   - Implement cache invalidation strategy
   - Add cache metrics
   - Configure Redis persistence

3. **Security**
   - Enable Cloud Run IAM authentication
   - Configure VPC Service Controls
   - Set up DDoS protection

4. **Monitoring**
   - Add structured logging (JSON)
   - Configure distributed tracing
   - Set up error tracking (Sentry)

---

### 5.5 Branch Naming Convention Enforcement

Going forward, enforce branch naming:

```
claude/{feature-description}-{session-id}
```

**Examples:**
- `claude/add-typography-tokens-01ABC123`
- `claude/fix-auth-flow-01DEF456`

**Configure branch protection:**
```yaml
# .github/branch-protection.yml
branches:
  - main:
      required_reviews: 1
      require_status_checks: true
      required_checks:
        - lint
        - test
        - security
```

---

## Appendix A: AI Task Delegation Templates

### Template 1: Test Generation

```
Generate comprehensive tests for [module/function] that cover:
- Happy path scenarios
- Edge cases (empty input, max values, invalid types)
- Error handling
- Async behavior (if applicable)

Requirements:
- Use pytest with pytest-asyncio
- Include fixtures for common test data
- Mock external dependencies
- Aim for 100% branch coverage
- Follow AAA pattern (Arrange, Act, Assert)

Module location: src/copy_that/[path]
Test location: tests/unit/[path]
```

### Template 2: Documentation Generation

```
Generate documentation for [component/feature] including:
- Overview and purpose
- Installation/setup requirements
- API reference with examples
- Configuration options
- Troubleshooting guide
- Related documentation links

Format: Markdown with code blocks
Audience: Intermediate developers
Tone: Technical, concise
Length: 1,500-2,500 words
```

### Template 3: Code Scaffolding

```
Generate skeleton code for [feature] following Copy That patterns:
- Domain model in src/copy_that/domain/
- Use case in src/copy_that/application/
- API endpoint in src/copy_that/interfaces/api/
- Pydantic schemas for request/response

Requirements:
- Type hints on all functions
- Docstrings in Google style
- Follow existing patterns in codebase
- Include __init__.py exports
```

---

## Appendix B: Risk Matrix

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Security vulnerabilities in auth | Medium | Critical | Week 1 security audit, OWASP testing |
| Migration failures in production | Low | High | Staging testing, rollback procedures |
| CV dependencies break Docker | Medium | Medium | Test in CI before merge |
| Documentation falls behind | High | Medium | AI parallel documentation tasks |
| Test coverage regression | Medium | Medium | Coverage gates in CI |
| Performance degradation | Low | High | Week 7 performance testing |

---

## Appendix C: Success Metrics

### Week 4 Checkpoint
- [ ] Backend-optimization merged
- [ ] Test coverage >75%
- [ ] All documentation current
- [ ] Staging deployment working
- [ ] CV preprocessing functional

### Week 8 Final
- [ ] v0.5.0 released to production
- [ ] Test coverage >85%
- [ ] All branches cleaned up
- [ ] Full documentation suite
- [ ] Monitoring operational
- [ ] Spacing tokens functional

---

## Section 6: Expert Review Feedback

Four domain experts reviewed this roadmap with awareness of the **50+ token type vision** (colors, spacing, typography, shadows, gradients, animations, component tokens, and more). Their consolidated feedback is captured below.

---

### 6.1 Principal Architect / PM / Full-Stack Developer

**Overall Assessment:** Plan has good bones but scope is 2-3x too large for 8 weeks. Engineering-focused, not experience-focused.

**Critical Issues Identified:**

1. **Scope Overload** - 120 hours across 8 weeks attempts major security merge + two token types + production release + documentation overhaul. Each is a 2-4 week project alone.

2. **Priority Inversion** - Security merge (Week 1-2) before spacing tokens contradicts "ship product value first" principle. Security adds complexity before proving the pattern.

3. **AI Task Debt** - 64 AI tasks creates review overhead. Each task needs 15+ minutes review = 16 unbudgeted hours.

4. **Missing Buffers** - No time for unexpected issues (expect 30% on unplanned work). No sick days, no vacation = burnout risk.

**Key Recommendations:**

- Reorder: Spacing tokens → Documentation → Security staging
- Cut AI tasks from 64 to ~28 (focused on boilerplate, not analysis)
- Add Week 0 for preparation
- Add explicit go/no-go criteria for milestone gates
- Budget 0.5h review time per AI task
- Define "deferred" section to document what's not being done and why

**Best Quote:** "The best roadmap is one you can actually complete."

---

### 6.2 PhD Computer Vision / Image Processing Researcher

**Overall Assessment:** Strong color science foundations (ColorAide, Delta-E) but significant CV infrastructure gaps that will cause problems before Phase 6.

**Critical Issues Identified:**

1. **SSRF Vulnerability** - Current `requests.get(image_url)` has zero validation. Cloud metadata URLs could fetch credentials.

2. **No Size Limits** - 100MB image will crash Cloud Run. CV pipeline docs estimate 34MB peak memory for 4K images.

3. **Synchronous Blocking** - Every image fetch blocks async event loop. 5 concurrent extractions = timeouts.

4. **No Image Preprocessing** - Sending raw 4K images to Claude increases API cost and reduces quality.

**Quick Wins That Should NOT Be Deferred (1-2 days):**

| Task | Hours | Impact |
|------|-------|--------|
| Image validation (magic bytes, size limits) | 4-6h | Security + reliability |
| SSRF protection (private IP blocking) | 2-3h | Security |
| Async HTTP migration (httpx) | 3-4h | Performance |
| Auto-orientation (EXIF) | 2h | Spacing accuracy |

**Spacing Token Extraction Guidance:**

- Use hybrid approach: OpenCV for pixel measurements, Claude for semantic classification
- Essential preprocessing: grayscale, bilateral filtering, CLAHE contrast enhancement
- Edge detection (Canny) + contour analysis for spacing measurements
- AI can't provide pixel-precise values - must use traditional CV

**Key Recommendations:**

1. **Must-Have:** Async HTTP + SSRF protection + size limits (Week 2)
2. **Must-Have:** Image preprocessing before AI calls (resize, CLAHE, WebP encoding)
3. **Should-Have:** Use Claude's structured outputs (JSON mode / tool use)
4. **Should-Have:** Redis caching by image hash
5. **Nice-to-Have:** Cross-validate AI prominence claims with histogram analysis

**Best Quote:** "Validation and async HTTP are not 'preprocessing' - they're prerequisites for safe operation."

---

### 6.3 Senior UI/UX Designer (Educational / Visual Storytelling)

**Overall Assessment:** Solid technical foundation but significant untapped design potential. UI feels like developer tool rather than educational design companion.

**Critical Issues Identified:**

1. **Engineering-Focused Roadmap** - Extensive planning for security, migrations, CI/CD but almost nothing about visual token relationships, learning journeys, or delight moments.

2. **Missing Educational Experience** - Current interface *describes* concepts (harmony, accessibility) rather than *demonstrating* them visually.

3. **No Token Relationship Visualization** - Each token type treated as isolated. No cross-token storytelling (how colors relate to spacing).

4. **Learning Sidebar Overwhelms** - Exposes everything upfront instead of progressive disclosure.

**Design Vision for 50+ Token Types:**

- **Token Origin Overlay** - Highlight source regions in image when hovering over tokens
- **Design System Health Score** - Gamified quality metrics (grid alignment, harmony, accessibility)
- **Token Browser with Hierarchy** - Collapsible tree navigation for 50+ types
- **View Mode Evolution** - Grid, List, Tree, Timeline, Graph views for different token types
- **Quick Preview on Hover** - Floating panel with live preview (color as button, spacing as padding)

**Key Recommendations:**

| Priority | Recommendation | Why |
|----------|----------------|-----|
| **Must-Have** | Token Origin Overlay | Foundation of educational promise |
| **Must-Have** | Design System Health Score | Guides users toward quality outcomes |
| **Should-Have** | Token Comparison Mode | Side-by-side decision making |
| **Should-Have** | Animated Extraction Progress | Turn waiting into learning |
| **Should-Have** | Token Quick Preview | Efficient browsing at scale |
| **Nice-to-Have** | Token Graduation/Curation Flow | Teaches intentional design system building |
| **Nice-to-Have** | Export Preview with Syntax Highlighting | Professional polish |
| **Nice-to-Have** | Empty State Storytelling | First impression moments |

**Whimsy Suggestions:**

- Animated micro-interactions (tokens "settle" with spring physics)
- Optional sound design (soft chimes on extraction)
- Playful copy ("Let's see what colors are hiding..." vs "Processing image...")
- Achievement moments ("Your first perfect 8px grid!")

**Best Quote:** "The platform's unique position is being both a professional tool and an educational companion. Don't sacrifice either for the other - they reinforce each other."

---

### 6.4 Senior AI/ML Researcher

**Overall Assessment:** Solid MVP for colors but architecture won't survive scaling to 50 token types. Regex parsing is biggest liability.

**Critical Issues Identified:**

1. **Fragile Parsing** - Regex-based parsing of Claude output loses 60-70% of structured data quality. Hardcoded fallback confidence (0.85) hides model uncertainty.

2. **Inconsistent Model Usage** - OpenAI uses JSON mode, Claude uses freeform text. Both should use structured outputs.

3. **No Retry/Fallback** - Single API call, no retries on failure, no automatic model fallback.

4. **Per-Type Code Duplication** - Current architecture requires 50 separate extractor classes with copy-pasted parsing logic.

5. **Cost at Scale** - At 50 token types with separate calls, extraction costs ~$0.75/image vs ~$0.03 with multi-token extraction.

**Recommended Model Strategy:**

| Token Category | Recommended Model | Rationale |
|----------------|-------------------|-----------|
| Colors, Gradients | Claude Sonnet 4.5 | Best color perception |
| Typography (fonts) | GPT-4V | Better OCR |
| Spacing/Layout | Claude or Gemini 1.5 Flash | Spatial reasoning |
| Animations | Gemini 1.5 Pro | Video understanding |

**Key Recommendations:**

| Priority | Recommendation | Impact |
|----------|----------------|--------|
| **Must-Have** | Switch Claude to Tool Use (structured output) | Eliminates parsing failures, guarantees schema |
| **Must-Have** | Create Base Extractor Abstraction | Enables 50 types without duplication |
| **Must-Have** | Implement Multi-Token Extraction | 80% cost reduction (5 types in 1 call) |
| **Must-Have** | Add Result Caching (Redis) | Eliminates redundant API calls |
| **Should-Have** | Build Prompt Template Library (YAML) | Maintainable prompts, version control |
| **Should-Have** | Implement Model Router | Optimal model per token type |
| **Should-Have** | Add Automatic Fallback Chain | 99.9% availability |
| **Should-Have** | Create Evaluation Pipeline | Golden dataset, catch regressions |

**Structured Output Pattern (Tool Use):**

```python
tools = [{
    "name": "report_color_tokens",
    "input_schema": {
        "type": "object",
        "properties": {
            "colors": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "hex": {"type": "string", "pattern": "^#[0-9A-Fa-f]{6}$"},
                        "name": {"type": "string"},
                        "confidence": {"type": "number"}
                    }
                }
            }
        }
    }
}]

response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    tools=tools,
    tool_choice={"type": "tool", "name": "report_color_tokens"},
    messages=[...]
)

# Result is guaranteed to match schema - no regex needed!
color_data = response.content[0].input
```

**Best Quote:** "Switching to Tool Use is a 2-3 day change that will immediately improve reliability and unlock proper schema handling."

---

### 6.5 Cross-Expert Consensus

**Universal Agreement:**

1. **Ship product value first** - Spacing tokens before security infrastructure
2. **Async HTTP is non-negotiable** - Current synchronous approach will cause failures
3. **Structured outputs required** - Regex parsing won't scale to 50 token types
4. **Caching is critical** - Redis caching by image hash for cost and performance
5. **Documentation should teach** - Not just describe, but demonstrate and delight

**Conflicting Priorities Resolved:**

| Conflict | Resolution |
|----------|------------|
| CV preprocessing timing | Defer full pipeline to Phase 6, but implement validation + async HTTP in Week 2 (CV researcher) |
| AI task count | Reduce from 64 to 28, budget review time (Principal) |
| Security merge timing | Week 7-8 staging only, production in Phase 6 (Principal) |
| UI investment | Must-have: Token Origin Overlay, Health Score (Designer) during spacing work |

**Recommended Additional Experts:**

Consider consulting:
- **Accessibility Specialist** - For WCAG compliance across 50+ token visualizations
- **Technical Writer** - For consistent documentation voice across growing doc corpus

---

### 6.7 Application Security Engineer

**Overall Assessment:** Security rating 4/10. Critical vulnerabilities require immediate attention before production.

**Critical Vulnerabilities Confirmed:**

1. **SSRF (CRITICAL)** - `requests.get(image_url)` can fetch GCP metadata, internal services
2. **No Authentication** - All API endpoints publicly accessible
3. **No Size Limits** - 100MB images will OOM Cloud Run
4. **No Rate Limiting** - API abuse possible

**Auth Implementation Gaps:**
- Missing token revocation list
- Missing refresh token rotation
- Missing JTI tracking for replay attacks
- Missing account lockout for brute force

**Key Recommendations:**

| Priority | Recommendation | Impact |
|----------|----------------|--------|
| **CRITICAL** | SSRF protection (validate URLs, block private IPs) | Prevents cloud credential theft |
| **CRITICAL** | Async HTTP with size limits | Prevents DoS |
| **HIGH** | Make security CI blocking (remove `continue-on-error`) | Stops vulnerable deployments |
| **HIGH** | Rate limiting before auth | Prevents API abuse |
| **MEDIUM** | GCP Secret Manager integration | Proper secret handling |
| **MEDIUM** | Security headers middleware | Prevents XSS, clickjacking |

**Best Quote:** "Do not deploy to production with the current SSRF vulnerability."

---

### 6.8 QA Engineer / Test Architect

**Overall Assessment:** Test architecture rating 4/10. Critical scalability challenges for 50+ token types.

**Critical Issues:**

1. **Test Explosion Risk** - 50 types × 20 tests = 1,000+ tests without proper patterns
2. **Missing Golden Datasets** - No regression detection for AI output drift
3. **No Determinism Testing** - Same image may produce different tokens
4. **No Contract Testing** - Schema drift undetected between frontend/backend

**Recommended Testing Patterns:**

| Pattern | Purpose | Priority |
|---------|---------|----------|
| **Golden Dataset Testing** | Detect AI output drift | CRITICAL |
| **Contract Testing (Pact)** | Schema compliance | CRITICAL |
| **Fixture Factory Pattern** | Scalable test data | HIGH |
| **Test Parallelization (pytest-xdist)** | Fast CI runs | HIGH |
| **Property-Based Testing** | Edge case discovery | MEDIUM |

**Coverage Targets (Realistic):**
- Overall: 70% (not 85% - maintenance burden)
- Critical paths: 95%
- Golden datasets: 10 images per token type

**Key Recommendations:**

1. **Implement golden dataset testing** - Human-verified baseline for regression detection
2. **Switch to contract testing with Tool Use** - Schema compliance guaranteed
3. **Add pytest-xdist parallelization** - 30min → 8min CI runs
4. **Create fixture factory pattern** - Avoid 50 duplicate test patterns
5. **Add coverage gates to CI** - Enforce 70% minimum

**Best Quote:** "The testing strategy needs to evolve from 'test individual components' to 'test the extraction pipeline at scale.'"

---

### 6.9 DevOps / Cloud Infrastructure Engineer

**Overall Assessment:** Solid MVP foundation but critical gaps for production batch processing.

**Critical Infrastructure Issues:**

1. **Memory severely underprovisioned** - 512Mi-1Gi cannot handle 34MB peak per 4K image
2. **Concurrency too high** - 80 concurrent requests with image processing = guaranteed OOM
3. **Wrong Dockerfile deployed** - Optimized version exists but minimal version used
4. **No canary deployments** - No gradual rollout or automated rollback

**Recommended Configuration:**

| Setting | Current | Recommended |
|---------|---------|-------------|
| Memory | 512Mi-1Gi | **2Gi minimum** |
| Concurrency | 80 | **25-30** |
| Max Instances | 100 | **20 initially** |
| Service Account | Key in secrets | **Workload Identity** |

**Cost Risks at Scale:**
- Without caching: $150/day in AI costs (5,000 images)
- Runaway scaling: max 100 instances can cause surprise bills

**Key Recommendations:**

| Priority | Recommendation | Impact |
|----------|----------------|--------|
| **CRITICAL** | Increase memory to 2Gi, reduce concurrency to 25 | Prevent OOM |
| **CRITICAL** | Fix Dockerfile.cloudrun (multi-stage, non-root) | Security + performance |
| **HIGH** | Implement Workload Identity | Security best practice |
| **HIGH** | Add budget alerts ($100 staging, $500 prod) | Cost protection |
| **HIGH** | Add Redis caching for extractions | 70% cost reduction |
| **MEDIUM** | Implement canary deployments | Safe rollouts |

**Best Quote:** "Current 512Mi cannot handle 34MB peak per 4K image. With 80 concurrent requests = guaranteed OOM."

---

### 6.10 AI-Assisted Development Expert (10x Productivity)

**Overall Assessment:** 28 AI tasks are well-scoped but significantly under-utilize AI capabilities for 50+ token types. With proper patterns, solo developer can achieve 5-10x productivity.

**Current AI Task Gaps:**

| Gap | Missing Tasks | Potential Savings |
|-----|---------------|-------------------|
| Schema generation | 40-50 tasks for all token types | 20-30 hours |
| Type definitions | TypeScript from Pydantic | 20-30 hours |
| API route generation | FastAPI endpoints from schemas | 15-20 hours |
| Component generation | React from design specs | 15-20 hours |

**10x Productivity Patterns:**

1. **Golden Template Pattern** - Perfect one implementation, AI replicates for 50 types (10x)
2. **AI Assembly Line** - Always have AI working 2-3 steps ahead (3-5x)
3. **Specification-First Loop** - Write 5-line spec → AI generates 100+ lines (3-5x)
4. **Parallel Universe** - Generate multiple implementations, pick best (2x)

**Multi-Agent Orchestration Strategy:**

Split work across AI tools by their strengths:

| Tool | Best For | Use Cases |
|------|----------|-----------|
| **Claude Code** | Multi-file architecture, complex logic | New token types, refactoring |
| **GitHub Copilot** | Inline completion, boilerplate | Method bodies, repetitive code |
| **Gemini** | Long context, video understanding | Animation tokens, documentation |
| **GPT-4** | Broad knowledge, API design | Architecture decisions |
| **Cursor** | Full-file generation, chat-in-editor | Quick fixes, exploration |

**Agent Handoff Patterns:**

```
PATTERN 1: Specialist Pipeline
Claude Code (architecture) → Copilot (implementation) → Claude Code (tests)

PATTERN 2: Parallel Specialists
Terminal 1: Claude Code (backend extractor)
Terminal 2: Cursor (frontend component)
Terminal 3: Copilot (inline completions)

PATTERN 3: Review Chain
Claude Code (generate) → GPT-4 (review) → Claude Code (refine)
```

**Managing Multiple AI Agents:**

1. **Single Source of Truth** - Keep specs/schemas in repo, all agents read same files
2. **Clear Boundaries** - Each agent owns specific file sets (no overlap)
3. **Validation Gate** - All AI output goes through same lint/test/type-check
4. **Context Sync** - Share CLAUDE.md context file across all tools

**Key Recommendations:**

| Multiplier | Recommendation |
|------------|----------------|
| **10x** | Build token type generator script (meta-generator) |
| **5x** | Implement multi-token extraction (batch API calls) |
| **4x** | AI-assisted test generation pipeline |
| **3x** | Switch to Tool Use structured output immediately |
| **3x** | Create custom slash command library |
| **2-3x** | Establish AI pair programming sessions |
| **2x** | Build context preloader for better AI output |
| **2x** | Implement nightly AI task queue |

**Daily Workflow with Multiple Agents:**

```
MORNING (High Energy - Human Judgment)
- 30 min: Review overnight AI outputs from all agents
- 1 hour: Merge good work, provide refinement prompts
- 1 hour: Core implementation requiring human judgment
- Queue day's AI tasks across multiple agents

AFTERNOON (Lower Energy - Review & Integration)
- 1 hour: Review Claude Code generated tests
- 1 hour: Review Copilot completions
- 30 min: Validate all AI output through CI
- 30 min: Queue evening batch tasks

EVENING (Optional - Async Generation)
- Queue overnight tasks to different agents
- Large generations run in parallel
- Review results in morning
```

**Best Quote:** "These patterns compound. Realistic expectation: 5-10x productivity on suitable tasks, 2-3x overall when including human-judgment tasks."

---

### 6.6 Revised Priority Matrix (Expert Consensus)

**Week 2 Must-Haves (Before Spacing):**

| Task | Expert | Hours |
|------|--------|-------|
| Async HTTP migration (httpx) | CV | 3-4h |
| SSRF protection + size limits | CV | 6h |
| Switch Claude to Tool Use | AI/ML | 8h |
| Image preprocessing (resize, CLAHE) | CV | 4h |

**Week 3-4 With Spacing Implementation:**

| Task | Expert | Hours |
|------|--------|-------|
| Base Extractor Abstraction | AI/ML | 8h |
| Token Origin Overlay (UI) | UX | 8h |
| Hybrid CV/AI spacing pipeline | CV | 10h |
| Result caching (Redis) | AI/ML | 4h |

**Week 5-6 During Documentation/Release:**

| Task | Expert | Hours |
|------|--------|-------|
| Design System Health Score | UX | 8h |
| Prompt Template Library | AI/ML | 6h |
| Token Comparison Mode | UX | 6h |
| Multi-token extraction | AI/ML | 8h |

---

## Appendix D: Expert Review Summary Table

| Expert | Primary Concern | Highest-Priority Recommendation | Timeline Impact |
|--------|-----------------|----------------------------------|-----------------|
| Principal Architect | Scope too large (2-3x) | Reorder: spacing first, security last | Realistic |
| CV Researcher | Security + reliability gaps | Async HTTP + SSRF protection (Week 2) | +1 day Week 2 |
| UI/UX Designer | Missing educational experience | Token Origin Overlay + Health Score | +2 days Weeks 3-4 |
| AI/ML Researcher | Fragile parsing won't scale | Switch to Tool Use structured output | +1 day Week 2 |
| Security Engineer | SSRF vulnerability critical | Block private IPs, validate URLs | +1 day Week 1 |
| QA/Test Architect | Test patterns won't scale | Golden datasets + fixture factory | +2 days Weeks 3-4 |
| DevOps Engineer | Memory underprovisioned | 2Gi memory, reduce concurrency to 25 | Configuration only |
| AI-Assisted Dev Expert | Under-utilizing AI capabilities | Build token type meta-generator (10x) | Productivity gain |

---

## Appendix E: Multi-Agent AI Orchestration Guide

### Tool Selection Matrix

| Task Type | Primary Tool | Secondary Tool | Notes |
|-----------|-------------|----------------|-------|
| Architecture design | Claude Code | GPT-4 | Use GPT-4 for second opinion |
| Multi-file implementation | Claude Code | - | Claude excels at coordinated changes |
| Inline completion | GitHub Copilot | Cursor | Copilot for speed, Cursor for chat |
| Documentation | Gemini | Claude Code | Gemini handles long context |
| Test generation | Claude Code | Copilot | Claude for strategy, Copilot for boilerplate |
| Code review | GPT-4 | Claude Code | GPT-4 for broad patterns |
| Debugging | Cursor | Claude Code | Cursor for chat-in-editor |
| Animation tokens | Gemini | - | Only Gemini handles video |

### Handoff Protocol

```
1. SPECIFICATION (Human → Any AI)
   - Write clear requirements
   - Specify file paths
   - Include examples

2. GENERATION (AI → Filesystem)
   - AI generates to specific files
   - Never mix outputs from multiple AIs in same file

3. VALIDATION (Filesystem → CI)
   - Run lint, type-check, tests
   - All AI output through same gate

4. REVIEW (Human → AI)
   - Request specific fixes
   - Provide error messages
   - Never manually fix what AI can learn from

5. MERGE (Human → Git)
   - Human makes final merge decision
   - AI can assist with PR description
```

### Context Sharing Across Agents

Create a shared context file all agents read:

**`CLAUDE.md` / `AI_CONTEXT.md`:**
```markdown
# Project Context for AI Assistants

## Architecture
- Clean architecture pattern
- PostgreSQL + Redis + Cloud Run
- Claude Sonnet 4.5 for AI extraction

## Current Focus
- Implementing spacing tokens (Week 2-4)
- Using Tool Use for structured output
- Target: 50+ token types

## Patterns
- Extractors: src/copy_that/application/*_extractor.py
- Generators: src/copy_that/generators/*_generator.py
- Tests follow pytest + pytest-asyncio

## Do Not Change Without Asking
- alembic/versions/*
- .github/workflows/*
- deploy/terraform/*
```

### Cost Management Across Agents

| Agent | Cost Model | Daily Budget |
|-------|------------|--------------|
| Claude Code | Per token | $5-10 |
| GitHub Copilot | Subscription | Fixed |
| Cursor | Subscription | Fixed |
| GPT-4 API | Per token | $2-5 |
| Gemini API | Per token | $1-3 |

**Total daily AI budget:** ~$10-20 for aggressive parallel usage

---

---

## Section 7: AI Agent Orchestration Architecture

### 7.1 Overview

The Copy That platform implements a **pipeline-based agent orchestration system** for extracting and processing 50+ design token types.

**Key Principles:**
- Agents organized by **pipeline stage**, not token type
- Single ExtractionAgent handles all token types via configuration
- Parallel processing across images
- Circuit breakers for fault tolerance

### 7.2 Pipeline Architecture

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│PREPROCESS│ → │ EXTRACT  │ → │AGGREGATE │ → │ VALIDATE │ → │ GENERATE │
└──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
```

| Stage | Responsibility | Concurrency |
|-------|---------------|-------------|
| Preprocess | Download, validate, enhance images | 10 |
| Extract | AI extraction (configurable by token type) | 3 |
| Aggregate | Deduplicate, merge, track provenance | 10 |
| Validate | Schema validation, WCAG accessibility | 10 |
| Generate | Output to W3C, CSS, React, etc. | 10 |

### 7.3 Session Prompts (Claude Code Web)

Each session implements one pipeline stage. Run Session 0 first, then Sessions 1-5 in parallel.

| Session | Pipeline Stage | Doc |
|---------|---------------|-----|
| 0 | Interfaces & Types | [session-0-interfaces.md](sessions/session-0-interfaces.md) |
| 1 | Preprocessing | [session-1-preprocessing.md](sessions/session-1-preprocessing.md) |
| 2 | Extraction | [session-2-extraction.md](sessions/session-2-extraction.md) |
| 3 | Aggregation | [session-3-aggregation.md](sessions/session-3-aggregation.md) |
| 4 | Validation | [session-4-validation.md](sessions/session-4-validation.md) |
| 5 | Generator | [session-5-generator.md](sessions/session-5-generator.md) |
| 6 | Orchestrator | [session-6-orchestrator.md](sessions/session-6-orchestrator.md) |

### 7.4 Execution Order

```
Day 1: Session 0 (must complete first)
Day 2-5: Sessions 1-5 (run in parallel)
Day 6: Session 6 + Integration merge
```

### 7.5 Development Rules

1. **TDD First** - Write tests before implementation
2. **Defensive Coding** - Validate all inputs, handle all errors
3. **Security First** - SSRF protection in preprocessing
4. **95%+ Coverage** - Required for all pipeline components

---

**End of Document**

*Generated by Integration Bot for joshband/copy-that*
*Pipeline-based architecture: November 23, 2025*

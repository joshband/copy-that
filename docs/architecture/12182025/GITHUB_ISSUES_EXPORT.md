# GITHUB_ISSUES_EXPORT.md
# Copy That – Roadmap Issues (Ready for GitHub)

This document converts ROADMAP_05, ROADMAP_06, and ROADMAP_07 into
GitHub-ready issues with labels, milestones, and acceptance criteria.

---

## Milestone: ROADMAP_05 – Architecture & Refactor Foundation

### Issue: Enforce Domain Boundaries
**Labels:** architecture, backend, refactor
**Milestone:** ROADMAP_05

**Context**
Backend layers imply DDD but boundaries are not enforced.

**Tasks**
- Remove cross-layer imports
- Introduce application services
- Refactor domain to be framework-free

**Acceptance Criteria**
- Domain has no FastAPI/SQLAlchemy imports
- Application services testable without I/O

---

### Issue: Standardize Multi-Extractor Orchestration
**Labels:** architecture, extractors
**Milestone:** ROADMAP_05

**Tasks**
- Create shared orchestrator interface
- Normalize extractor metadata
- Centralize logging/metrics

**Acceptance Criteria**
- All extractors use same orchestrator
- Shared E2E tests pass

---

## Milestone: ROADMAP_06 – CI/CD & Security Hardening

### Issue: Consolidate CI Pipelines
**Labels:** ci, infra
**Milestone:** ROADMAP_06

**Tasks**
- Remove duplicate workflows
- Make ci-tiered canonical
- Update branch protections

**Acceptance Criteria**
- Single CI source of truth
- Reduced duplicate job runs

---

### Issue: Secure Cloud Run Deployments
**Labels:** security, infra
**Milestone:** ROADMAP_06

**Tasks**
- Remove allow-unauthenticated
- Implement auth strategy
- Update health checks

**Acceptance Criteria**
- Services reject unauthenticated traffic
- Health checks remain functional

---

## Milestone: ROADMAP_07 – Platform Expansion

### Issue: Token Dependency Graph
**Labels:** platform, backend
**Milestone:** ROADMAP_07

**Tasks**
- Build token graph
- Detect circular dependencies
- Expose API queries

**Acceptance Criteria**
- Circular refs detected
- Impact analysis available

---

### Issue: Generator Plugin System
**Labels:** platform, generators
**Milestone:** ROADMAP_07

**Tasks**
- Define plugin interface
- Registry + versioning
- Author docs

**Acceptance Criteria**
- Multiple generators share interface
- Plugins versioned independently

# Documentation Drift Prevention Checklist

## Purpose

This checklist ensures that when making architectural changes (routes, components, APIs, etc.), all documentation is updated consistently across the project.

## When to Use This Checklist

Use this checklist whenever you:
- Add/remove/rename routes or pages
- Change API endpoints
- Modify component structure
- Update the tech stack
- Change build/deployment process
- Consolidate or split features
- Refactor major systems

## Core Documentation Files

### 1. **Root Directory**
- [ ] `README.md` - Project overview, features, quick start
- [ ] `CHANGELOG.md` - Version history and changes
- [ ] `ARCHITECTURE.md` (if exists) - System architecture

### 2. **docs/ Directory**
- [ ] `docs/README.md` - Documentation index
- [ ] `docs/architecture/ARCHITECTURE.md` - Technical architecture
- [ ] `docs/development/ROADMAP.md` - Version timeline and metrics
- [ ] `docs/development/VERSION_STATUS_ALIGNMENT.md` - Version status tracking
- [ ] `docs/guides/CONTRIBUTING.md` - Contribution guidelines

### 3. **Feature-Specific Docs**
- [ ] `frontend/DEMO_README.md` - Frontend demo documentation
- [ ] `extractors/README.md` - Extractor system docs
- [ ] Any `*_GUIDE.md` or `*_MANUAL.md` files

### 4. **Configuration Files**
- [ ] `package.json` - Scripts and dependencies
- [ ] `tsconfig.json` - TypeScript configuration
- [ ] `vite.config.ts` / `vitest.config.ts` - Build configuration
- [ ] `.github/workflows/*.yml` - CI/CD pipelines

## Search Patterns for Common Changes

### Route/Page Changes

When adding/removing/renaming routes, search for:
```bash
# Search for old route patterns
grep -r "/old-route" docs/ README.md frontend/
grep -r "OldComponentName" docs/ README.md frontend/

# Check for references to removed pages
grep -r "MobileDemo\|TokenEnhancementsDemo" docs/ README.md
```

Common files to update:
- `App.tsx` - Route definitions
- `README.md` - Feature list and architecture diagram
- `docs/development/ROADMAP.md` - Metrics (e.g., "Frontend Pages: X")
- `frontend/DEMO_README.md` - Component usage examples
- `CHANGELOG.md` - Document the change

### API Endpoint Changes

When adding/removing/renaming endpoints, search for:
```bash
# Search for old endpoint patterns
grep -r "/api/old-endpoint" docs/ frontend/src/ README.md

# Check API documentation
grep -r "POST /api" docs/
```

Common files to update:
- `backend/routers/*.py` - Router definitions
- `frontend/src/api/client.ts` - API client
- `docs/api/` - API documentation (if exists)
- OpenAPI/Swagger specs
- `README.md` - API feature list

### Component Changes

When refactoring components, search for:
```bash
# Search for component references
grep -r "OldComponent" docs/ README.md frontend/

# Check import statements
grep -r "import.*OldComponent" frontend/src/
```

Common files to update:
- Component README files
- Usage examples in docs
- Test files
- Storybook stories (if exists)

### Technology Stack Changes

When updating dependencies or tech stack:
```bash
# Search for old library names
grep -r "old-library" docs/ README.md package.json
```

Common files to update:
- `README.md` - Tech stack section
- `package.json` - Dependencies
- `docs/development/` - Development guides
- `CONTRIBUTING.md` - Setup instructions

## Verification Strategy

### 1. Automated Search
```bash
# Run comprehensive grep for common terms
grep -r "SEARCH_TERM" \
  README.md \
  docs/ \
  frontend/DEMO_README.md \
  CHANGELOG.md \
  --include="*.md"
```

### 2. Documentation Test
Consider adding a test that validates documentation consistency:
```typescript
// docs/tests/documentation.test.ts
describe('Documentation Consistency', () => {
  it('should not reference removed routes', () => {
    const removedRoutes = ['/mobile', '/demo/comprehensive'];
    const docs = readAllMarkdownFiles();

    removedRoutes.forEach(route => {
      docs.forEach(doc => {
        expect(doc.content).not.toContain(route);
      });
    });
  });
});
```

### 3. Manual Checklist
After making changes, verify:
- [ ] All code references updated
- [ ] All docs references updated
- [ ] CHANGELOG.md has entry for this version
- [ ] README.md reflects current state
- [ ] No broken links in documentation
- [ ] Build scripts still work
- [ ] CI/CD pipeline reflects changes

## Example: Route Consolidation (v2.4.1)

**Change**: Consolidated 5 React demo routes → 2 routes

**Files Updated**:
1. ✅ `frontend/src/App.tsx` - Removed 4 routes
2. ✅ `frontend/src/pages/HomePage.tsx` - Simplified nav
3. ✅ `README.md` - Updated architecture diagram
4. ✅ `docs/development/ROADMAP.md` - Changed "5 Production Frontend Pages" to "2 routes"
5. ✅ `frontend/DEMO_README.md` - Updated component list

**Search Commands Used**:
```bash
grep -r "TokenEnhancementsDemo\|ComprehensiveTokenDemo\|MobileDemo" docs/ README.md
grep -r "/mobile\|/demo/comprehensive\|/demo/progressive\|/extract/comprehensive" docs/ frontend/
```

## Prevention Tips

1. **Keep a Documentation Map**: Maintain a list of all docs and their purpose
2. **Use Consistent Terminology**: Agree on names before implementing
3. **Atomic Commits**: Update docs in the same commit as code changes
4. **PR Checklist**: Include "Documentation updated?" in PR template
5. **Version Alignment**: Keep VERSION_STATUS_ALIGNMENT.md in sync
6. **Search Before Commit**: Always grep for old terms before committing

## Documentation Owner

- **Primary**: Project maintainer
- **Backup**: Technical writer (if available)
- **Community**: Contributors via PR reviews

## Last Updated

2025-11-08 - Created after v2.4.1 route consolidation

---

**Remember**: Documentation is code. Treat it with the same rigor as your codebase.

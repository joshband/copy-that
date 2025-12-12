# Monthly Documentation Review Checklist
**Purpose:** Maintain clean, up-to-date documentation
**Frequency:** First week of each month
**Owner:** Development Team Lead
**Duration:** ~2 hours

---

## Review Checklist

### 1. Session & Handoff Documents (15 min)

**Check For:**
- [ ] Session handoffs from previous month in docs/
- [ ] Handoff documents in any subdirectories
- [ ] Phase completion documents (PHASE_*, ISSUE_*)
- [ ] Date-stamped documents from previous month

**Action:**
```bash
# Find session/handoff docs from last month
find docs -name "*session*" -o -name "*handoff*" -o -name "*HANDOFF*" -o -name "*SESSION*" 2>/dev/null

# Find date-stamped docs from last month (adjust date)
find docs -name "*2025-12-*" -type f 2>/dev/null
```

**If Found:** Archive to `~/Documents/copy-that-archive/sessions/`

---

### 2. Architecture Documentation (20 min)

**Review:**
- [ ] docs/architecture/CURRENT_ARCHITECTURE_STATE.md - Is it current?
- [ ] Are there duplicate/overlapping architecture docs?
- [ ] Are there one-time analysis docs that are now complete?

**Questions:**
- Has the architecture changed significantly since last update?
- Are technical debt items still accurate?
- Are the phase roadmaps still correct?

**Action:**
- Update CURRENT_ARCHITECTURE_STATE.md if architecture changed
- Archive superseded architecture analysis docs
- Update version number (e.g., v1.1 → v1.2)

---

### 3. Planning Documentation (15 min)

**Review:**
- [ ] docs/planning/ - Are roadmaps current?
- [ ] Are there completed phase plans?
- [ ] Are implementation checklists up-to-date?

**Questions:**
- Have any phases been completed?
- Are roadmaps aligned with current work?
- Are there abandoned/outdated plans?

**Action:**
- Archive completed phase plans to `~/Documents/copy-that-archive/planning-history/`
- Update active roadmaps if priorities changed
- Remove or archive abandoned plans

---

### 4. Testing Documentation (15 min)

**Review:**
- [ ] docs/testing/ - Are test strategies current?
- [ ] Are there test session summaries from last month?
- [ ] Are test coverage reports up-to-date?

**Questions:**
- Has the test strategy changed?
- Are there date-stamped test docs from last month?
- Are test execution guides still accurate?

**Action:**
- Archive test session docs
- Update TESTING_GUIDE.md if strategy changed
- Remove outdated test reports

---

### 5. Guides & How-Tos (10 min)

**Review:**
- [ ] docs/guides/ - Are operational guides current?
- [ ] Are there deprecated setup guides?
- [ ] Are there tools/processes no longer in use?

**Questions:**
- Have any tools been deprecated?
- Are setup instructions still accurate?
- Are cost optimization strategies current?

**Action:**
- Archive deprecated guides to `~/Documents/copy-that-archive/guides-deprecated/`
- Update guides if processes changed
- Add new guides for new tools/processes

---

### 6. Feature Specifications (10 min)

**Review:**
- [ ] Root-level feature specs (e.g., MOOD_BOARD_SPECIFICATION.md)
- [ ] Are specs for completed features still in root?
- [ ] Are new features documented?

**Questions:**
- Which features were completed last month?
- Are there new features that need documentation?
- Are feature specs accurate?

**Action:**
- Archive completed feature specs
- Create specs for new features in development
- Update specs if requirements changed

---

### 7. Legacy Directories (10 min)

**Check For:**
- [ ] New */legacy/* directories created
- [ ] Files moved to legacy but not archived
- [ ] Explicitly marked deprecated docs

**Action:**
```bash
# Find legacy directories
find docs -path "*/legacy/*" -type f 2>/dev/null
```

**If Found:** Archive to appropriate category

---

### 8. Date-Stamped Documents (15 min)

**Check For:**
- [ ] Documents with dates from 2+ months ago
- [ ] Analysis documents that are now completed
- [ ] Session-specific documents

**Action:**
```bash
# Find all date-stamped files (adjust date range)
find docs -name "*2025-*" -type f | sort
```

**Review Each:** Is this still relevant or should it be archived?

---

### 9. Documentation Index (10 min)

**Review:**
- [ ] DOCUMENTATION_INDEX.md - Are all links working?
- [ ] Are new docs added to the index?
- [ ] Are archived docs removed from index?

**Action:**
- Update "Last Updated" timestamp
- Add new documentation to appropriate category
- Remove archived docs from index
- Update statistics (active files, archived files)

---

### 10. Archive Maintenance (10 min)

**Review:**
- [ ] ~/Documents/copy-that-archive/ARCHIVE_MANIFEST.md
- [ ] Are statistics up-to-date?
- [ ] Are archive categories organized?

**Action:**
- Update archive statistics
- Add new archive subdirectories if needed
- Update "Last Update" timestamp

---

## Documentation Metrics

### Track Monthly:

**Active Documentation:**
- Total markdown files in docs/: `find docs -name "*.md" | wc -l`
- Architecture docs: `ls docs/architecture/*.md | wc -l`
- Planning docs: `find docs/planning -name "*.md" | wc -l`
- Guide docs: `find docs/guides -name "*.md" | wc -l`

**Archived Documentation:**
- Total archived: `find ~/Documents/copy-that-archive -name "*.md" | wc -l`
- Session archives: `ls ~/Documents/copy-that-archive/sessions/*.md | wc -l`
- Architecture archives: `ls ~/Documents/copy-that-archive/architecture-history/*.md | wc -l`

**Record in:** DOCUMENTATION_INDEX.md (Documentation Statistics section)

---

## Automation Opportunities

### Optional Scripts:

**1. Find Session Docs:**
```bash
#!/bin/bash
# find-session-docs.sh
LAST_MONTH=$(date -v-1m "+%Y-%m")
echo "Session/handoff docs from $LAST_MONTH:"
find docs -name "*session*" -o -name "*handoff*" | grep "$LAST_MONTH"
```

**2. Archive Date-Stamped Docs:**
```bash
#!/bin/bash
# archive-old-docs.sh
CUTOFF_DATE="2025-11"  # Adjust monthly
find docs -name "*$CUTOFF_DATE*" -type f -exec echo "Archive: {}" \;
```

**3. Documentation Health Check:**
```bash
#!/bin/bash
# doc-health-check.sh
echo "=== Documentation Health Check ==="
echo "Active docs: $(find docs -name '*.md' | wc -l)"
echo "Archived docs: $(find ~/Documents/copy-that-archive -name '*.md' | wc -l)"
echo "Broken links: (check manually)"
```

---

## Decision Tree

### Should I Archive This Document?

```
Is it a session handoff or phase completion?
├─ YES → Archive to sessions/
└─ NO ↓

Is it date-stamped from 2+ months ago?
├─ YES → Review: Still relevant?
│        ├─ NO → Archive to appropriate category
│        └─ YES → Keep, update date if actively maintained
└─ NO ↓

Is it in a */legacy/* directory?
├─ YES → Archive to guides-deprecated/
└─ NO ↓

Is it a one-time analysis (backend-analysis, design audit, etc.)?
├─ YES → Has it been acted upon?
│        ├─ YES → Archive to architecture-history/
│        └─ NO → Keep until implemented
└─ NO ↓

Is it superseded by current documentation?
├─ YES → Archive to appropriate category
└─ NO → KEEP (active documentation)
```

---

## Archive Categories Quick Reference

| Document Type | Archive Location |
|---------------|------------------|
| Session handoffs | `~/Documents/copy-that-archive/sessions/` |
| Phase completions | `~/Documents/copy-that-archive/planning-history/` |
| Historical architecture | `~/Documents/copy-that-archive/architecture-history/` |
| Deprecated guides | `~/Documents/copy-that-archive/guides-deprecated/` |
| Legacy code reviews | `~/Documents/copy-that-archive/legacy-code-review/` |

---

## Post-Review Actions

### After Review (Required):

1. **Update DOCUMENTATION_INDEX.md:**
   - [ ] Update "Last Review" timestamp
   - [ ] Update statistics
   - [ ] Add/remove links as needed

2. **Update ARCHIVE_MANIFEST.md:**
   - [ ] Update statistics
   - [ ] Update "Last Update" timestamp
   - [ ] Add note about what was archived this month

3. **Commit Changes:**
   ```bash
   git add docs/
   git commit -m "docs: Monthly review YYYY-MM - archive N files"
   ```

4. **Optional: Clean Git History:**
   If many files archived:
   ```bash
   git rm [archived files]
   git commit -m "docs: Remove archived documentation from git"
   ```

---

## Review History Template

### YYYY-MM Review

**Date:** YYYY-MM-DD
**Reviewer:** [Name]
**Duration:** [Time spent]

**Archived:**
- Session docs: N files
- Architecture docs: N files
- Planning docs: N files
- Guides: N files
- **Total:** N files

**Updated:**
- DOCUMENTATION_INDEX.md
- CURRENT_ARCHITECTURE_STATE.md (if applicable)
- Archive manifest

**Issues Found:**
- [List any issues]

**Actions Taken:**
- [List actions]

**Next Review:** YYYY-MM-DD

---

## Tips for Efficient Reviews

1. **Set a Calendar Reminder:** First Monday of each month
2. **Block 2 Hours:** Uninterrupted time for thorough review
3. **Use the Checklist:** Don't skip sections
4. **Be Ruthless:** If in doubt, archive it (files are never deleted)
5. **Update as You Go:** Don't batch updates at the end
6. **Test Links:** Verify links in DOCUMENTATION_INDEX.md work
7. **Document Decisions:** Note why you kept/archived specific files

---

## Questions or Issues?

**Contact:** Development Team Lead
**Reference:** DOCUMENTATION_CONSOLIDATION_PLAN.md

---

**Last Updated:** 2025-12-12
**Next Review:** 2026-01-12 (First Monday of January)

# Branch Cleanup Guide

## Current Status

✅ **Complete:**
- Main branch consolidated with all changes from `feat/missing-updates-and-validations`
- 20 local branches deleted
- Main pushed to GitHub

⏳ **Pending:**
- Delete 35 remaining remote branches on GitHub

---

## Quick Start (3 Steps)

### Step 1: Update GitHub Token Permissions

**Option A: Quick Re-authentication (Recommended)**
```bash
gh auth login
# Select GitHub.com → Authorize → Done
```

**Option B: Generate New Token**
1. Visit: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name it: `claude-code-branch-cleanup`
4. Enable scopes:
   - ✓ `repo` (full control of private repositories)
5. Generate and copy the token
6. Run: `gh auth login` and paste the token

**Option C: Update Existing Token**
1. Visit: https://github.com/settings/tokens
2. Select your current token
3. Add `repo` scope for write access
4. Save changes

### Step 2: Verify Permissions

```bash
gh auth status
```

Should show `repo` in scopes. Example output:
```
Token scopes: 'admin:public_key', 'gist', 'read:org', 'repo'
```

### Step 3: Run the Cleanup Script

```bash
# From project root:
./scripts/cleanup-remote-branches.sh

# Or manually delete one by one:
gh api repos/joshband/copy-that/git/refs/heads/{branch-name} -X DELETE
```

---

## Manual Deletion Commands

### Delete Individual Branches

```bash
# Format:
gh api repos/joshband/copy-that/git/refs/heads/{branch-name} -X DELETE

# Example:
gh api repos/joshband/copy-that/git/refs/heads/chore/centralize-spacing-cv -X DELETE
gh api repos/joshband/copy-that/git/refs/heads/feat/missing-updates-and-validations -X DELETE
```

### Batch Deletion Script (Advanced)

```bash
# Get list of merged branches
MERGED=$(git branch -r --merged origin/main | grep -v origin/main | sed 's/^  origin\///')

# Delete each one
echo "$MERGED" | while read branch; do
  gh api repos/joshband/copy-that/git/refs/heads/$branch -X DELETE && \
  echo "✓ Deleted: $branch" || \
  echo "✗ Failed: $branch"
done
```

---

## Branches to Delete

**Total: 35 branches** (all merged into main)

### Feature Branches (13)
```
feat/color-token-enhancements-100
feat/frontend-upload
feat/missing-updates-and-validations
feat/oklch-clustering
feat/region-color-extraction
feat/spacing-gapmap-hough
feat/spacing-grid-cv
feat/token-graph
feat/token-playground-cleanup
feat/typography-recommendation-hardening
feat/ui-quick-wins
```

### Claude Session Branches (12)
```
claude/check-recent-remote-branch-018jUhpQm1KZNuBGpQNZS97D
claude/fix-ruff-linting-015FpLfhVm8gA8uzx2gzEWJm
claude/implement-spacing-tokens-01JXWN18nVnMicZJR3bQpD6c
claude/review-shadow-docs-011xD6JT3WURrnVeLEEsrvwe
claude/session7-demo-enhancements
claude/setup-cloud-01XSDcrpPXtsa2WZswWiU9Pz
claude/shadow-pipeline-1-01BXp8VVMptR3eLiH7umHTmW
claude/shadow-pipeline-docs-01WwU7zD4MFv1ebCsaGmDNch
claude/shadow-token-lifecycle-01WrwgwNhb1q1grj97cW786Z
claude/speed-up-cicd-tests-01BAtMfgaTXNtAUikXRg6dX6
claude/update-color-pipeline-demos-014m3MCXvGLWwVTdcFPBSvg4
```

### Chore Branches (2)
```
chore/centralize-spacing-cv
chore/w3c-export-contracts
```

### Bug Fix Branches (3)
```
fix/colors-export-json
fix/spacing-api-hardening
fix/token-graph-main-merge
```

### Dependabot Branches (5)
```
dependabot/github_actions/actions/upload-artifact-5
dependabot/github_actions/github/codeql-action-4
dependabot/github_actions/google-github-actions/setup-gcloud-3
dependabot/npm_and_yarn/jsdom-27.2.0
dependabot/npm_and_yarn/tanstack/react-query-5.90.11
(+ 5 more dependabot branches)
```

---

## Verification

After deletion, verify the cleanup:

```bash
# Count remaining remote branches
git fetch origin
git branch -r | grep -v main | grep -v HEAD | wc -l

# List remaining branches (should be 0 or only main-related)
git branch -r | grep -v main | grep -v HEAD
```

---

## Troubleshooting

### "Token Missing Repo Scope"
```
Error: Token missing 'repo' scope
```
→ Solution: Update permissions in Step 1

### "Permission Denied"
```
Error: Resource not accessible by integration
```
→ Check your GitHub token has write access at: https://github.com/settings/tokens

### "Branch Not Found"
```
Error: Could not resolve to a PullRequest with that ID
```
→ Branch may already be deleted, or the name might be wrong. Check exact name with:
```bash
git branch -r | grep -i "search-term"
```

### "SSL Certificate Error"
```
fatal: unable to access 'https://...': SSL: certificate problem
```
→ Switch to SSH: `gh auth login` and select SSH

---

## What Happens When You Delete Branches?

✓ **Safe to delete** - All branches are merged into main
✓ **Reversible** - GitHub keeps deleted branch history for 90 days
✓ **No code loss** - All commits are in main
✗ **Cannot recover via git** - Must use GitHub's restore feature

---

## Next Steps

1. Update your GitHub token (Step 1)
2. Verify permissions (Step 2)
3. Run cleanup script (Step 3)
4. Verify deletion

**Estimated time:** 5 minutes

---

## Questions?

For detailed GitHub CLI documentation:
```bash
gh api --help
gh auth --help
```

Or visit: https://cli.github.com/manual

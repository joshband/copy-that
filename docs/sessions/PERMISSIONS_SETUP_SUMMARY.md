# GitHub Token Permissions Setup Summary

## Current Situation

Your GitHub CLI is authenticated but the token doesn't have write permissions needed to delete branches via the CLI.

```
Current Token Status:
  Account: joshband
  Scopes: admin:public_key, gist, read:org, repo (partial)
  Protocol: SSH
  Issue: Missing full 'repo' write scope for branch deletion
```

---

## The Problem

The `repo` scope in your token is read-only. To delete branches via the CLI, you need write access.

**Example of what happens now:**
```bash
$ git push origin --delete feat/test-branch
error: unable to delete 'feat/test-branch': remote ref does not exist

# OR

$ gh api repos/joshband/copy-that/git/refs/heads/feat/test-branch -X DELETE
error: Resource not accessible by integration
```

---

## The Solution

You have **3 options** to fix this. Choose one:

### ✅ **Option 1: Re-authenticate (Fastest)**

```bash
gh auth login
```

Then:
- Select "GitHub.com"
- Choose authentication method (HTTPS recommended for this)
- GitHub will prompt you to authorize scopes
- Accept all scopes
- Done!

**Time: ~1 minute**

---

### ✅ **Option 2: Generate New Token (Most Control)**

1. Go to: **https://github.com/settings/tokens**

2. Click blue "Generate new token" → "Generate new token (classic)"

3. Fill in form:
   - Token name: `claude-code-branch-cleanup` (or your preference)
   - Expiration: 90 days (or as needed)

4. Select **Scopes** (click each checkbox):
   - ✓ `repo` → Full control of private repositories
     - `repo:status` (automatically included)
     - `repo_deployment` (automatically included)
     - `public_repo` (automatically included)
     - `repo:invite` (automatically included)
   - ✓ `admin:public_key` (keep - for SSH keys)
   - ✓ `gist` (keep - for gist access)
   - ✓ `read:org` (keep - for org read)

5. Click green "Generate token" button

6. **IMPORTANT:** Copy the token immediately (you won't see it again!)
   ```
   ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

7. Use the token with gh:
   ```bash
   gh auth login
   # Paste the token when prompted
   ```

**Time: ~2-3 minutes**

---

### ✅ **Option 3: Update Existing Token (If You Have GitHub Access)**

1. Go to: **https://github.com/settings/tokens**

2. Find and click on your existing token (should show recent activity)

3. Scroll down to "Scopes" section

4. Find `repo` and check the parent checkbox
   - This expands to show sub-scopes
   - Ensure all are checked

5. Scroll to bottom and click "Update token"

6. Your token is now updated with full `repo` permissions

**Time: ~30 seconds**

---

## Verification Step

After updating, verify your permissions:

```bash
gh auth status
```

**Expected output:**
```
github.com
  ✓ Logged in to github.com account joshband (keyring)
  - Active account: true
  - Git operations protocol: ssh
  - Token: gho_****...
  - Token scopes: 'admin:public_key', 'gist', 'read:org', 'repo'
                                                              ^^^^^
                                        This should now be here!
```

---

## After You Update: Delete Branches

Once permissions are updated, use any of these methods:

### Method 1: Automated Script (Recommended)
```bash
./scripts/cleanup-remote-branches.sh
```

The script will:
- ✓ Check your permissions
- ✓ Find all merged branches
- ✓ Ask for confirmation
- ✓ Delete them safely
- ✓ Verify the cleanup

### Method 2: Manual CLI Commands
```bash
# Delete one branch at a time
gh api repos/joshband/copy-that/git/refs/heads/feat/color-token-enhancements-100 -X DELETE

# Delete with gh repo command (if available)
gh repo delete-branch copy-that -b feat/missing-updates-and-validations
```

### Method 3: Batch Delete Script
```bash
# Get merged branches
MERGED=$(git branch -r --merged origin/main | sed 's/^  origin\///' | grep -v main)

# Delete each one
echo "$MERGED" | while read branch; do
  echo "Deleting: $branch"
  gh api repos/joshband/copy-that/git/refs/heads/$branch -X DELETE
done
```

---

## Why This Happens

GitHub has two layers of access control:

1. **Repository Permissions** (on GitHub)
   - Your account has "Admin" access to the repo ✓

2. **Token Scopes** (in your token)
   - Limits what your token can do
   - Different tokens can have different scopes
   - Your current token has read-only `repo` scope

When you delete branches via CLI, GitHub checks **both**. Even though your account can delete branches, your token can't because it lacks the write scope.

This is a security feature to prevent compromised tokens from doing too much damage.

---

## Security Note

After generating a new token:

- ✓ Safe: Store token in GitHub CLI (uses system keyring)
- ✓ Safe: Use token with authenticated CLI commands
- ✗ Never: Paste token in code or git files
- ✗ Never: Share token with others
- ✗ Never: Commit token to version control

If you accidentally expose a token:
1. Go to https://github.com/settings/tokens
2. Click the token
3. Click "Delete"
4. Generate a new one

GitHub will automatically revoke exposed tokens.

---

## Quick Reference

| Method | Time | Easiest? |
|--------|------|----------|
| Re-authenticate | 1 min | ✓ YES |
| New token | 2-3 min | - |
| Update token | 30 sec | ✓ YES |

---

## Files Created for You

1. **BRANCH_CLEANUP_GUIDE.md** - Detailed step-by-step guide
2. **scripts/cleanup-remote-branches.sh** - Automated cleanup script
3. **This file** - Permissions overview

---

## What's Next?

1. Choose one option above (recommendation: Option 1)
2. Update your token permissions
3. Run `gh auth status` to verify
4. Run the cleanup script or manual commands
5. Done!

**Total time to fully cleanup branches: 5-10 minutes**

---

## Still Having Issues?

Check these resources:

```bash
# GitHub CLI help
gh auth --help
gh api --help

# Debug your token
gh auth status --show-token

# List what you can do
gh api user
```

Or visit: https://cli.github.com/manual/gh_auth_login

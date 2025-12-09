# Developer Workflow - Copy That

**Last Updated:** 2025-12-08
**For:** Solo Developer (Josh)

---

## 🎯 Goal

Prevent lint/type/test errors from reaching CI by catching them early in your local development workflow.

---

## 🚀 Setup (One-Time)

### 1. IDE Integration (Recommended)

Open the project in VS Code:
```bash
code .
```

**What happens automatically:**
- ✅ VS Code prompts to install recommended extensions
- ✅ Ruff linter shows errors as you type
- ✅ Mypy type checker runs in background
- ✅ Auto-format on save (Ruff)
- ✅ Auto-fix imports on save

**Recommended Extensions:**
- `charliermarsh.ruff` - Python linting/formatting
- `ms-python.python` - Python language support
- `ms-python.vscode-pylance` - Type checking
- `esbenp.prettier-vscode` - TypeScript formatting
- `dbaeumer.vscode-eslint` - JavaScript linting

### 2. Pre-commit Hooks (Already Installed)

```bash
# Verify hooks are installed
ls -la .git/hooks/ | grep -E "pre-commit|pre-push"

# Should show:
# pre-commit  (runs ruff, gitleaks)
# pre-push    (runs mypy, pytest fast)
```

**What runs automatically:**
- **On commit:** Ruff lint, format, gitleaks, file checks
- **Before push:** Mypy type check, fast unit tests

---

## 💻 Daily Development Workflow

### Option 1: With IDE Integration (Fastest Feedback)

```bash
# 1. Open VS Code
code .

# 2. Start development server
docker-compose up api postgres

# 3. Make changes
# - Errors show in VS Code as you type
# - Auto-format on save
# - No surprises at commit time!

# 4. Commit (pre-commit hooks run automatically)
git add .
git commit -m "feat: my feature"

# 5. Push (pre-push hooks run: mypy + tests)
git push origin main
```

**Errors caught:**
- ✅ Line 1: Syntax errors (VS Code)
- ✅ Line 10: Import errors (VS Code)
- ✅ Line 50: Type errors (mypy in background)
- ✅ Before commit: Ruff auto-fixes
- ✅ Before push: Full type check + tests

### Option 2: Manual Validation (No IDE)

```bash
# Before committing, run quick validation
./scripts/validate.sh

# What it checks:
# 1. Ruff linting
# 2. Ruff formatting
# 3. Mypy type checking
# 4. Fast unit tests

# If all pass:
git commit -m "feat: my feature"
git push origin main
```

### Option 3: Pre-commit Only (Minimal)

```bash
# Just commit - hooks run automatically
git add .
git commit -m "feat: my feature"  # Ruff auto-fixes here

# Push - mypy + tests run here
git push origin main
```

---

## 🔍 Catching Errors Early

### Stage 1: While Coding (IDE - Instant Feedback)

**VS Code shows:**
- 🔴 Red squiggles for syntax errors
- 🟡 Yellow squiggles for type errors
- 🔵 Blue squiggles for style issues

**Example:**
```python
# This shows error immediately in VS Code:
def get_user(id: int):  # ← Missing return type annotation
    return User.query.get(id)  # ← Type error if User is unknown
```

### Stage 2: On Save (IDE - Auto-Fix)

**VS Code automatically:**
- ✅ Formats code (Ruff)
- ✅ Organizes imports
- ✅ Fixes style issues

### Stage 3: On Commit (Pre-commit Hook - 2-5 seconds)

**Runs automatically:**
```bash
ruff check --fix               # Auto-fix lint issues
ruff format                    # Format code
gitleaks                       # Check for secrets
trailing-whitespace            # File cleanups
```

**If errors found:**
- Auto-fixes are applied
- Commit proceeds with fixes
- You see what was changed

### Stage 4: Before Push (Pre-push Hook - 30-60 seconds)

**Runs automatically:**
```bash
mypy src/                                           # Type check
pytest tests/unit -x -q -m "not slow" --tb=line    # Fast tests
```

**If errors found:**
- Push is **BLOCKED**
- You fix errors locally
- Try push again

### Stage 5: In CI (GitHub Actions - 5-8 minutes)

**Full validation:**
- Security scan
- Lint + type check (all files)
- Full test suite (unit + integration)
- Docker build
- Deployment

**Only runs if push succeeds** (hooks already validated)

---

## 🛡️ Why This Prevents CI Failures

### Before (No IDE Integration)

```
Code → Commit → Push → CI Fails → Fix → Repeat
│                        ↑
│                        └─ 10-15 min wasted
└─ No feedback
```

**Result:** 5-10 failed CI runs before success

### After (With IDE Integration)

```
Code → IDE Errors → Fix → Commit → Pre-commit → Push → Pre-push → CI Success
│      ↑ instant    ↑     ↑        ↑ 2-5 sec    ↑      ↑ 1 min   ↑ 5-8 min
│      └─ Fix now  saved          auto-fix             validate   deploy!
└─ See errors as you type
```

**Result:** First push succeeds, zero wasted CI runs

---

## 🔧 Troubleshooting

### Issue: VS Code not showing errors

**Solution:**
```bash
# 1. Select Python interpreter
Cmd+Shift+P → "Python: Select Interpreter" → .venv/bin/python

# 2. Reload window
Cmd+Shift+P → "Developer: Reload Window"

# 3. Check extension is installed
Extensions → search "Ruff" → Install
```

### Issue: Pre-commit hooks not running

**Solution:**
```bash
# Reinstall hooks
pre-commit install
pre-commit install --hook-type pre-push

# Test manually
pre-commit run --all-files
```

### Issue: Mypy errors in pre-push but not in IDE

**Solution:**
```bash
# Run mypy manually with same config
mypy src/

# Or use validation script
./scripts/validate.sh
```

### Issue: Pre-push is too slow

**Solution:**
```bash
# Skip hooks temporarily (use sparingly!)
git push --no-verify

# Or configure faster tests
# Edit .pre-commit-config.yaml:
#   pytest tests/unit -x -q  # -x = stop on first failure
```

---

## 📝 Git Workflow Best Practices

### Small, Frequent Commits

```bash
# Good: Small commits, fast validation
git add src/api/colors.py
git commit -m "feat: add color validation"  # ← Fast, targeted

# Bad: Large commits, slow validation
git add .
git commit -m "feat: everything"  # ← Slow, hard to debug
```

### Fix Errors Immediately

```bash
# When pre-commit auto-fixes:
# 1. Review the changes
git diff

# 2. If good, amend commit
git add .
git commit --amend --no-edit

# 3. If bad, fix manually and commit again
```

### Use Validation Script Before Big Changes

```bash
# Before refactoring
./scripts/validate.sh  # Baseline: all passing

# After refactoring
./scripts/validate.sh  # Check: still passing?
```

---

## 🎓 Learning Resources

### Mypy
- [Mypy Cheat Sheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html)
- Common fixes:
  ```python
  # Add return type
  def get_user(id: int) -> User:  # ← Add this
      return User.query.get(id)

  # Add parameter types
  def process(data: dict[str, Any]) -> None:  # ← Add these
      print(data)

  # Handle None
  user: User | None = get_user(1)  # ← Use | None for optional
  if user:
      print(user.name)
  ```

### Ruff
- [Ruff Rules](https://docs.astral.sh/ruff/rules/)
- Auto-fix most issues: `ruff check --fix .`

---

## 📊 Expected Workflow Times

| Activity | Time | Feedback |
|----------|------|----------|
| Coding | Continuous | IDE: instant errors |
| Save file | 0s | IDE: auto-format |
| Commit | 2-5s | Pre-commit: auto-fix |
| Push | 30-60s | Pre-push: mypy + tests |
| CI validation | 5-8min | Full suite |

**Total time to deploy:** ~6-9 minutes (vs 30-45 min with failed CIs)

---

## ✅ Success Checklist

Daily workflow setup:
- [ ] VS Code opened in project directory
- [ ] Python interpreter set to `.venv/bin/python`
- [ ] Recommended extensions installed
- [ ] Pre-commit hooks installed
- [ ] Pre-push hooks installed
- [ ] `./scripts/validate.sh` runs successfully

Ready to code!

---

**Maintained By:** Josh (Solo Developer)

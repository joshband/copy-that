# Monthly Documentation Review Checklist

**Purpose:** Keep the **core** docs tree accurate and small.
**Frequency:** First week of each month · **Duration:** ~60–90 min
**Live nav:** [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)
**Archive:** `~/Documents/copy-that-archive/` (`ARCHIVE_MANIFEST.md`)

---

## 1. Index & SoTs (15 min)

- [ ] [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) matches `docs/**/*.md`
- [ ] Planning SoT: [MVP_EXPANSION_ROADMAP.md](docs/planning/MVP_EXPANSION_ROADMAP.md)
- [ ] Architecture SoT: [CURRENT_ARCHITECTURE_STATE.md](docs/architecture/CURRENT_ARCHITECTURE_STATE.md)
- [ ] W3C SoT: [W3C_CONFORMANCE.md](docs/domain/W3C_CONFORMANCE.md)
- [ ] `.env.example` ↔ [ENVIRONMENT_VARIABLES.md](docs/configuration/ENVIRONMENT_VARIABLES.md)

## 2. Accuracy spot-checks (20 min)

- [ ] Setup: [start_here.md](docs/setup/start_here.md) still boots (`make install`, `pnpm type-check`, `/health`, `/docs`)
- [ ] README Quick Start: extract curl includes `project_id` or points to UI
- [ ] Runbook paths: `/health`, `/docs` (not invented `/api/v1/health`)
- [ ] Mood and Lighting documented as opt-in tabs; parked API surfaces labeled; nav intent links to [featureFlags.ts](frontend/src/config/featureFlags.ts)
- [ ] No teaching `pnpm typecheck` (script is `pnpm type-check`)
- [ ] Validation docs match `Makefile`, root/frontend scripts, and `.github/workflows/ci.yml`: `make verify`, separate security gates, and fresh-port mocked MVP Playwright
- [ ] Backend tests live in `tests/unit` or `tests/integration`; browser tests live in `frontend/tests/playwright`; no new tests outside CI collection
- [ ] Run the [extraction accuracy evaluation](tests/unit/regression/test_extraction_accuracy.py); investigate score regressions without lowering floors to hide them
- [ ] AI model identifiers remain centralized in [ai_models.py](src/copy_that/infrastructure/ai_models.py); docs describe overrides rather than copying default IDs
- [ ] Environment variants, private keys, Terraform state, connector secrets, and generated outputs remain ignored; only `.env.example` may be tracked
- [ ] Dependency audit and secret-scan results reviewed; unresolved findings have an owner and next action
- [ ] Paid generation still requires an explicit action; compare mounted API routes and access controls with documented product scope
- [ ] Dated work notes go in `CHANGELOG.md`; roadmap and architecture describe current intent and decisions

```bash
rg -n 'pnpm typecheck|/api/v1/health' --glob '*.md' || true
```

## 3. Archive candidates (15 min)

- [ ] Session/handoff / date-stamped one-offs → `~/Documents/copy-that-archive/sessions/`
- [ ] Superseded planning/architecture long-form → `planning-history/` / `architecture-history/`
- [ ] Prefer **move + ARCHIVE_MANIFEST** over delete

```bash
find docs -iname '*handoff*' -o -iname '*session*' 2>/dev/null | head
```

## 4. Evidence retention (5 min)

- [ ] `docs/evidence/*` READMEs still state retain-until (~90 days from evidence date)
- [ ] Do **not** archive evidence early (e.g. 2026-09-20 packs → keep until ~2026-12-20)

## 5. Link scan (10 min)

```bash
# Relative md links from docs/ and root SoTs — fix broken targets
python3 - <<'PY'
from pathlib import Path
import re
root = Path('.')
files = list(root.glob('*.md')) + list(Path('docs').rglob('*.md'))
link_re = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')
broken = []
for f in files:
    text = f.read_text(encoding='utf-8', errors='replace')
    for m in link_re.finditer(text):
        url = m.group(2).split('#')[0].split('?')[0].strip()
        if not url or url.startswith(('http://','https://','mailto:','`')): continue
        target = (f.parent / url).resolve()
        if not target.exists():
            broken.append(f'{f}: {url}')
print(f'broken={len(broken)}')
for b in broken[:50]: print(b)
PY
```

## 6. Close-out

- [ ] Update `ARCHIVE_MANIFEST.md` for any moves this month
- [ ] Bump “Last Updated” on touched SoTs
- [ ] Note open risks in the review PR/notes (stale screenshots, parked-feature drift)

**Done when:** index accurate, SoTs consistent with code flags, zero known broken relative links in live md, evidence still retained per policy.

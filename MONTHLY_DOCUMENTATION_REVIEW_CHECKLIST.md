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
- [ ] Parked features labeled (mood board P4, sessions P5, multi-extract demo)
- [ ] No teaching `pnpm typecheck` (script is `pnpm type-check`)

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

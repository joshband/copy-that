# Hiring Pages Showcase Implementation Plan

> **For agentic workers:** Execute task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild `site/` as a dual-audience hiring showcase (Home + Engineering) deployed via existing Actions Pages.

**Architecture:** Static HTML/CSS/JS under `site/`. Shared `assets/site.css` + `assets/site.js`. Absorb compressed visual media from current explainer. Do not touch engineering markdown under `docs/` except this plan/spec tree and README link notes.

**Tech Stack:** Hand-authored HTML5, CSS (IBM Plex, Fieldwork accents), vanilla JS (IntersectionObserver). GitHub Actions `pages.yml` path `site`.

---

### Task 1: Shared CSS/JS shell

**Files:**
- Create: `site/assets/site.css`
- Create: `site/assets/site.js`
- Delete or stop linking: `site/style.css`, `site/script.js` after pages migrate

- [ ] Dark charcoal default; `--rc2` warm accent, `--rc1` cool proof/link
- [ ] Layout: `.wrap`, `.site-header`, `.hero`, `.section`, `.cta-row`, proof/code, galleries, footer
- [ ] Motions: hero atmosphere, `[data-reveal]` rise-in, proof focus
- [ ] JS: reveal observer + optional reduced-motion skip

### Task 2: Home `index.html`

**Files:**
- Replace: `site/index.html`

- [ ] Dual-brand hero + CTAs (Proof / Engineering / GitHub)
- [ ] What this proves (3 claims)
- [ ] Agentic practice section
- [ ] Proof gallery (W3C, CSS, verification)
- [ ] Compressed visual overview (synth → Fieldwork → illustrative apps)
- [ ] Boundary + About/contact
- [ ] Honesty labels on illustrative media

### Task 3: Engineering `engineering.html`

**Files:**
- Create: `site/engineering.html`

- [ ] Problem, architecture diagram (SVG/HTML), hard parts, proof table, decisions, next
- [ ] Deep links to GitHub blob paths for docs/tests/CI

### Task 4: README + site README + cleanup

**Files:**
- Modify: `README.md`
- Modify: `site/README.md`
- Remove unused: `site/style.css`, `site/script.js` if fully replaced

- [ ] Document Home + Engineering URLs; Actions deploy from `site/` (not branch `/docs`)

### Task 5: Local verify

- [ ] Open `site/index.html` and `engineering.html` via `python3 -m http.server` in `site/`
- [ ] Check nav, anchors, image paths, honesty labels, mobile wrap

---

## Spec coverage

| Spec item | Task |
|-----------|------|
| Dual-brand hero | 2 |
| What this proves / agentic / proof / visual / boundary / about | 2 |
| Engineering page sections | 3 |
| Visual accents + motion | 1 |
| README Pages notes | 4 |
| Honesty / illustrative labels | 2, 3 |
| `site/` not `/docs` | all |

# Copy That — hiring Pages site

Static two-page showcase for GitHub Pages (Actions deploy from `site/`).

## Pages

| File | Role |
|------|------|
| `index.html` | Home — hiring skim |
| `engineering.html` | Engineering case study |
| `assets/site.css` | Shared styles |
| `assets/site.js` | Reveal / motion |
| `assets/*` | Media (synth panels, Fieldwork sheets, illustrative apps) |

## Preview

```bash
cd site && python3 -m http.server 8080
# open http://localhost:8080/
```

## Deploy

Repo workflow `.github/workflows/pages.yml` uploads `site/` on push to `main`.  
Live: https://joshband.github.io/copy-that/

Do **not** switch Pages to branch `/docs` — `docs/` is the engineering documentation tree.

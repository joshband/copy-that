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

## Accuracy and release

Product claims follow the current README and architecture; illustrative visuals
and export snippets are labelled separately from captured extraction evidence.
When product scope or validation commands change, update both pages in the same PR.
Site changes publish after merge to main through `pages.yml`; a branch preview is
not a live-site update. Check local asset links and mobile/desktop rendering before publishing.

## Responsive layout and media

The shared stylesheet keeps the 1080px content span and left-aligned text measures.
The original phone threshold moves from 520px to 560px for the scrolling gallery;
700px and 899px are the two additional layout thresholds. Guide sheets retain three
columns on iPad portrait, then become a snap row at 700px. The applied gallery uses
intrinsic image ratios in one desktop row, a tablet 2×2 grid, and a phone snap row.
The scope grid fits its columns intrinsically; the phone proof table shares 560px.

Images declare dimensions and use native lazy loading. The seven large PNGs retain
their original fallback URLs, with full-size and smaller WebP alternatives selected
by `picture`, `srcset`, and `sizes`. A small tiled PNG replaces the full-screen SVG
grain filter. Content is visible without JavaScript or functioning observers;
JavaScript adds entrance motion, and reduced-motion disables animations and transitions.

Before release, capture both pages in Chromium and WebKit at 390×844, 744×1133,
820×1180, 1024×768, 1180×820, and 1440×900. Check document overflow, gallery
alignment at 900px and wider, JavaScript-disabled rendering, and reduced motion.
Exercise snap rows so native lazy loading fetches their offscreen images. Browser
emulation supplements physical iPhone/iPad testing; it does not replace it.

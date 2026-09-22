# Copy That — explainer site

A single-page, self-contained explainer for the [Copy That](https://github.com/joshband/copy-that)
design-token extraction project.

## Structure

```
index.html      All markup and content
style.css       All styling (design tokens live in :root as CSS variables)
script.js       One small IntersectionObserver — reveals the illustrative
                "token system unlocks" cards on scroll
assets/         Every image used on the page, referenced by relative path
```

No build step, no dependencies. Open `index.html` directly in a browser,
or serve the folder with anything static, e.g.:

```
python3 -m http.server 8000
```

## Page flow

1. **Hero** — byline, headline, subhead, CTA
2. **Ships today** — scope blurb + stack strip (FastAPI, React+TS, W3C DTCG, …)
3. **Why it matters** + **How it works** (4 numbered steps: upload → read → tokens → export)
4. **Four real inputs** — the hand-painted synth panel photos used as sample input
5. **It reads more than colors** — HTML token mock cards (foundations / materials / components)
6. **A complete style guide** — three `fieldwork-*.png` sheets + compact W3C/CSS proof snippets
7. **What a token system unlocks** — illustrative apps/plugins (not auto-built by the product)
8. Closing note + footer

## Design tokens

The palette used throughout (`--rc1` … `--rc5` in `style.css`) was extracted from
`assets/synth-panel-floral.jpg`:

| Token | Name | Hex |
|---|---|---|
| `--rc1` | Panel Blue | `#4BA4C7` |
| `--rc2` | Signal Orange | `#F47A24` |
| `--rc3` | Warm Cream | `#F3DFB4` |
| `--rc4` | Field Green | `#364F39` |
| `--rc5` | Studio Black | `#15171C` |

Type stack is IBM Plex (Serif / Sans / Mono), loaded from Google Fonts in the
`<head>` of `index.html`.

## Known constraints worth knowing before editing

- The four "Then it builds with it" images (`grove-app.png`, `field-notes-app.png`,
  `tideline-app.png`, `drift-plugin.png`) and the three `fieldwork-*.png` images have
  their backgrounds chroma-keyed to transparent PNG — they're meant to sit directly on
  the page background with a CSS `drop-shadow`, not inside a bordered card.
- The four `synth-panel-*.jpg` images are plain photos and are shown inside a
  `.mock-window` (the little browser-chrome frame with three dots) elsewhere in the CSS.
- Everything is one `<style>` block worth of CSS with no preprocessor — plain nested
  media queries at a single `max-width: 760px` breakpoint.

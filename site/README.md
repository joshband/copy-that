# Copy That — explainer site

A single-page, self-contained explainer for the [Copy That](https://github.com/joshband/copy-that)
design-token extraction project.

## Structure

```
index.html      All markup and content
style.css       All styling (design tokens live in :root as CSS variables)
script.js       One small IntersectionObserver — triggers the "Then it
                builds with it" cards to animate in on scroll
assets/         Every image used on the page, referenced by relative path
```

No build step, no dependencies. Open `index.html` directly in a browser,
or serve the folder with anything static, e.g.:

```
python3 -m http.server 8000
```

## Page flow

1. **Hero** — headline, subhead, CTA
2. **Why it matters** + **How it works** (4 numbered steps)
3. **Four real inputs** — the hand-painted synth panel photos used as sample input
4. **It reads more than colors** — reference imagery showing the depth of a full style
   guide (foundations / components / application)
5. **A complete style guide** — the actual token output: color, type, materials,
   spacing, shape, plus a small components preview built from those tokens
6. **Then it builds with it** — four example outputs (mobile app, desktop app,
   production tool, audio plugin) built from the same style guide
7. Closing note + footer

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

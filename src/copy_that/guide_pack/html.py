"""Self-contained HTML renderer for Design Guide Pack."""

from __future__ import annotations

import html
from typing import Any

from copy_that.guide_pack.schema import GuidePack


def _esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def render_guide_html(pack: GuidePack, *, w3c_flat: dict[str, Any] | None = None) -> str:
    """Render a Fieldwork-inspired self-contained HTML guide."""
    brand = pack.brand
    foundations = pack.foundations
    counts = pack.meta.source_counts
    coverage_rows = "".join(
        f"<tr><td>{_esc(k)}</td><td>{_esc(v)}</td></tr>"
        for k, v in sorted(pack.meta.type_coverage.items())
    )

    def swatches(section: str, ids: list[str]) -> str:
        if not w3c_flat or not ids:
            return "<p class='muted'>No tokens in this foundation.</p>"
        entries = w3c_flat.get(section) or {}
        chips = []
        for token_id in ids[:24]:
            entry = entries.get(token_id) if isinstance(entries, dict) else None
            value = ""
            if isinstance(entry, dict):
                value = entry.get("$value") or entry.get("value") or ""
            style = ""
            if section == "color" and isinstance(value, str) and value.startswith("#"):
                style = f"background:{_esc(value)}"
            elif section == "gradient" and isinstance(value, dict):
                stops = value.get("stops") or []
                if isinstance(stops, list) and len(stops) >= 2:
                    parts = []
                    for s in stops:
                        if isinstance(s, dict) and s.get("color"):
                            parts.append(f"{s['color']} {float(s.get('position', 0)) * 100:.0f}%")
                    if parts:
                        angle = value.get("angle", 90)
                        style = f"background:linear-gradient({angle}deg, {', '.join(parts)})"
            label = _esc(token_id.split(".")[-1])
            chips.append(
                f"<div class='chip'><div class='swatch' style='{style}'></div>"
                f"<code>{_esc(token_id)}</code><span>{label}</span></div>"
            )
        return f"<div class='chips'>{''.join(chips)}</div>" if chips else "<p class='muted'>—</p>"

    components_html = ""
    for comp in pack.components:
        slots = "".join(
            f"<li><strong>{_esc(s.name)}</strong> → <code>{_esc(s.token_ref or '—')}</code>"
            f" <em class='tag'>{_esc(comp.source)}</em></li>"
            for s in comp.slots
        )
        components_html += (
            f"<article class='card'><h3>{_esc(comp.name)}</h3>"
            f"<p>{_esc(comp.description)}</p><ul>{slots}</ul></article>"
        )

    apps_html = "".join(
        f"<article class='card'><h3>{_esc(a.title)}</h3><p>{_esc(a.notes)}</p>"
        f"<p class='tag'>source: {_esc(a.source)}</p></article>"
        for a in pack.applications
    )

    insights = "".join(f"<li>{_esc(i)}</li>" for i in pack.insights) or "<li class='muted'>None</li>"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{_esc(pack.meta.title)}</title>
<style>
  :root {{
    --ink: #1a1a1a;
    --paper: #f7f4ef;
    --rule: #d9d2c5;
    --accent: #2f5d50;
    --muted: #6b6560;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
    color: var(--ink);
    background:
      radial-gradient(1200px 600px at 10% -10%, #fff 0%, transparent 60%),
      linear-gradient(180deg, #fbf8f3 0%, var(--paper) 40%, #efe8dc 100%);
    line-height: 1.45;
  }}
  header {{
    padding: 4.5rem 6vw 2rem;
    border-bottom: 1px solid var(--rule);
  }}
  .brand {{
    font-size: clamp(2.4rem, 6vw, 4.2rem);
    letter-spacing: -0.03em;
    margin: 0 0 0.4rem;
    font-weight: 600;
  }}
  .voice {{ max-width: 42rem; color: var(--muted); font-size: 1.05rem; }}
  main {{ padding: 2rem 6vw 4rem; display: grid; gap: 2.5rem; }}
  h2 {{
    font-family: "Avenir Next", "Segoe UI", sans-serif;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: var(--accent);
    margin: 0 0 0.8rem;
  }}
  h3 {{ margin: 0 0 0.4rem; font-size: 1.15rem; }}
  .strip {{
    display: flex; flex-wrap: wrap; gap: 0.6rem;
    font-family: "Avenir Next", "Segoe UI", sans-serif;
    font-size: 0.85rem;
  }}
  .pill {{
    border: 1px solid var(--rule);
    background: rgba(255,255,255,0.55);
    padding: 0.35rem 0.7rem;
  }}
  .chips {{ display: flex; flex-wrap: wrap; gap: 0.75rem; }}
  .chip {{
    width: 7.5rem;
    font-family: "Avenir Next", "Segoe UI", sans-serif;
    font-size: 0.72rem;
  }}
  .swatch {{
    height: 3.2rem;
    border: 1px solid var(--rule);
    background: repeating-linear-gradient(45deg, #eee, #eee 6px, #fafafa 6px, #fafafa 12px);
    margin-bottom: 0.35rem;
  }}
  code {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 0.7rem; }}
  .grid {{ display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }}
  .card {{
    border-top: 1px solid var(--rule);
    padding-top: 0.8rem;
  }}
  .muted {{ color: var(--muted); }}
  .tag {{
    font-family: "Avenir Next", "Segoe UI", sans-serif;
    font-size: 0.7rem;
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    font-family: "Avenir Next", "Segoe UI", sans-serif;
    font-size: 0.85rem;
  }}
  td, th {{ border-bottom: 1px solid var(--rule); padding: 0.35rem 0.2rem; text-align: left; }}
  footer {{
    padding: 1.5rem 6vw 3rem;
    border-top: 1px solid var(--rule);
    color: var(--muted);
    font-family: "Avenir Next", "Segoe UI", sans-serif;
    font-size: 0.8rem;
  }}
</style>
</head>
<body>
  <header>
    <p class="tag">Design Guide Pack · v{_esc(pack.meta.version)}</p>
    <h1 class="brand">{_esc(brand.name)}</h1>
    <p class="voice">{_esc(brand.voice)}</p>
    <div class="strip" style="margin-top:1.2rem">
      <span class="pill">extract {counts.get('extract', 0)}</span>
      <span class="pill">derive {counts.get('derive', 0)}</span>
      <span class="pill">synth {counts.get('synth', 0)}</span>
      <span class="pill">preset {counts.get('preset', 0)}</span>
      <span class="pill">snapshot {_esc(pack.meta.token_snapshot_hash)}</span>
    </div>
  </header>
  <main>
    <section>
      <h2>Foundations · Color</h2>
      {swatches('color', foundations.colors)}
    </section>
    <section>
      <h2>Foundations · Gradient</h2>
      <p class="tag">Extract preferred; synth only when CV finds nothing</p>
      {swatches('gradient', foundations.gradients)}
    </section>
    <section>
      <h2>Foundations · Type &amp; Space</h2>
      <div class="grid">
        <div><h3>Typography</h3><ul>{''.join(f'<li><code>{_esc(i)}</code></li>' for i in foundations.typography[:12]) or '<li class="muted">—</li>'}</ul></div>
        <div><h3>Spacing</h3><ul>{''.join(f'<li><code>{_esc(i)}</code></li>' for i in foundations.spacing[:12]) or '<li class="muted">—</li>'}</ul></div>
        <div><h3>Shadow</h3><ul>{''.join(f'<li><code>{_esc(i)}</code></li>' for i in foundations.shadows[:12]) or '<li class="muted">—</li>'}</ul></div>
      </div>
    </section>
    <section>
      <h2>Components <span class="tag">(illustrative)</span></h2>
      <div class="grid">{components_html or '<p class="muted">No component sketches.</p>'}</div>
    </section>
    <section>
      <h2>Application notes <span class="tag">(illustrative)</span></h2>
      <div class="grid">{apps_html}</div>
    </section>
    <section>
      <h2>13-type honesty</h2>
      <table><thead><tr><th>$type</th><th>capability</th></tr></thead><tbody>{coverage_rows}</tbody></table>
    </section>
    <section>
      <h2>Insights</h2>
      <ul>{insights}</ul>
    </section>
  </main>
  <footer>
    Generated {_esc(pack.meta.generated_at)} · Official DTCG $types only ·
    Product semantics in com.copythat.* $extensions ·
    Component/application sections labeled illustrative when not from extract.
  </footer>
</body>
</html>
"""

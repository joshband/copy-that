"""
HTML demo page generator

Generates an interactive HTML demo page showing all extracted color tokens
"""

import logging

from .base_generator import BaseGenerator

logger = logging.getLogger(__name__)


class HTMLDemoGenerator(BaseGenerator):
    """Generate interactive HTML demo page"""

    def generate(self) -> str:
        """
        Generate HTML demo page with color swatches

        Returns:
            HTML string with interactive demo
        """
        colors_html = self._generate_color_swatches()
        stats_html = self._generate_statistics()

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Color Token Library</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f5f5;
            padding: 2rem;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        header {{
            background: white;
            padding: 2rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }}

        h1 {{
            font-size: 2rem;
            margin-bottom: 0.5rem;
            color: #333;
        }}

        .subtitle {{
            color: #666;
            font-size: 1rem;
        }}

        .stats {{
            background: white;
            padding: 2rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
        }}

        .stat {{
            text-align: center;
        }}

        .stat-value {{
            font-size: 2rem;
            font-weight: bold;
            color: #333;
        }}

        .stat-label {{
            color: #666;
            font-size: 0.9rem;
            margin-top: 0.25rem;
        }}

        .colors-section {{
            background: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }}

        .colors-section h2 {{
            margin-bottom: 1.5rem;
            color: #333;
        }}

        .filters {{
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
            flex-wrap: wrap;
        }}

        .filters input, .filters select {{
            padding: 0.5rem 0.75rem;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 0.95rem;
        }}

        .colors-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 1.5rem;
        }}

        .color-card {{
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            border: 1px solid #eee;
        }}

        .color-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        }}

        .color-swatch {{
            width: 100%;
            height: 150px;
            position: relative;
        }}

        .color-info {{
            padding: 1rem;
            background: white;
        }}

        .color-name {{
            font-weight: 600;
            color: #333;
            margin-bottom: 0.25rem;
        }}

        .color-value {{
            font-family: monospace;
            font-size: 0.85rem;
            color: #666;
            margin-bottom: 0.5rem;
        }}

        .color-role {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            background: #f0f0f0;
            border-radius: 12px;
            font-size: 0.75rem;
            color: #666;
            margin-right: 0.5rem;
        }}

        .color-metadata {{
            font-size: 0.8rem;
            color: #999;
            margin-top: 0.5rem;
            line-height: 1.4;
        }}

        .copy-button {{
            padding: 0.25rem 0.75rem;
            background: none;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 0.75rem;
            cursor: pointer;
            transition: all 0.2s;
            margin-top: 0.5rem;
            width: 100%;
        }}

        .copy-button:hover {{
            background: #f0f0f0;
            border-color: #999;
        }}

        .details-panel {{
            margin-top: 1rem;
            font-size: 0.85rem;
            color: #555;
            display: grid;
            gap: 0.35rem;
        }}

        .tag {{
            display: inline-block;
            padding: 0.15rem 0.5rem;
            border-radius: 999px;
            background: #eef2ff;
            color: #4338ca;
            font-size: 0.75rem;
            margin-right: 0.35rem;
            margin-top: 0.25rem;
        }}

        .badge {{
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 6px;
            font-size: 0.75rem;
            background: #f5f5f5;
            color: #555;
            margin-right: 0.35rem;
        }}

        footer {{
            text-align: center;
            color: #999;
            font-size: 0.85rem;
            margin-top: 2rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Color Token Library</h1>
            <p class="subtitle">Extracted and aggregated color tokens from design images</p>
        </header>

        {stats_html}

        <section class="colors-section">
            <h2>Color Tokens</h2>
            <div class="filters">
                <input type="text" id="searchInput" placeholder="Search name or hex..." oninput="filterColors()" />
                <select id="contrastFilter" onchange="filterColors()">
                    <option value="">All contrasts</option>
                    <option value="aa">WCAG AA</option>
                    <option value="aaa">WCAG AAA</option>
                </select>
                <select id="harmonyFilter" onchange="filterColors()">
                    <option value="">Any harmony</option>
                    <option value="complementary">Complementary</option>
                    <option value="analogous">Analogous</option>
                    <option value="triadic">Triadic</option>
                    <option value="split-complementary">Split-complementary</option>
                </select>
            </div>
            <div class="colors-grid">
                {colors_html}
            </div>
        </section>

        <footer>
            <p>Generated by Copy That - Universal Multi-Modal Token Platform</p>
        </footer>
    </div>

    <script>
        function copyToClipboard(text, button) {{
            navigator.clipboard.writeText(text).then(() => {{
                const original = button.textContent;
                button.textContent = 'Copied!';
                setTimeout(() => button.textContent = original, 1500);
            }});
        }}

        function filterColors() {{
            const search = document.getElementById('searchInput').value.toLowerCase();
            const contrast = document.getElementById('contrastFilter').value;
            const harmony = document.getElementById('harmonyFilter').value;
            const cards = document.querySelectorAll('.color-card');

            cards.forEach(card => {{
                const name = card.getAttribute('data-name');
                const hex = card.getAttribute('data-hex');
                const hasAA = card.getAttribute('data-aa') === 'true';
                const hasAAA = card.getAttribute('data-aaa') === 'true';
                const cardHarmony = card.getAttribute('data-harmony') || '';

                const matchesSearch = name.includes(search) || hex.includes(search);
                const matchesContrast = !contrast || (contrast === 'aa' && hasAA) || (contrast === 'aaa' && hasAAA);
                const matchesHarmony = !harmony || cardHarmony === harmony;

                if (matchesSearch && matchesContrast && matchesHarmony) {{
                    card.style.display = 'block';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }}
    </script>
</body>
</html>"""

        return html

    def _generate_color_swatches(self) -> str:
        """Generate HTML for color swatches"""
        if not self.library.tokens:
            return "<p>No colors available</p>"

        swatches = []
        for token in self.library.tokens:
            role_badge = f'<span class="color-role">{token.role}</span>' if token.role else ""
            temperature_tag = (
                f'<span class="tag">Temperature: {getattr(token, "temperature", "")}</span>'
                if getattr(token, "temperature", None)
                else ""
            )
            harmony_tag = (
                f'<span class="tag">Harmony: {getattr(token, "harmony", "")}</span>'
                if getattr(token, "harmony", None)
                else ""
            )
            wcag_badges = []
            if getattr(token, "wcag_aa_compliant_text", None):
                wcag_badges.append('<span class="badge">AA Text</span>')
            if getattr(token, "wcag_aaa_compliant_text", None):
                wcag_badges.append('<span class="badge">AAA Text</span>')
            if getattr(token, "colorblind_safe", None):
                wcag_badges.append('<span class="badge">Colorblind Safe</span>')

            swatch_html = f"""<div class="color-card"
                data-name="{token.name.lower()}"
                data-hex="{token.hex.lower()}"
                data-harmony="{getattr(token, "harmony", "") or ""}"
                data-aa="{str(getattr(token, "wcag_aa_compliant_text", False)).lower()}"
                data-aaa="{str(getattr(token, "wcag_aaa_compliant_text", False)).lower()}"
            >
                <div class="color-swatch" style="background-color: {token.hex};"></div>
                <div class="color-info">
                    <div class="color-name">{token.name}</div>
                    <div class="color-value">{token.hex}</div>
                    {role_badge}
                    {" ".join(wcag_badges)}
                    <div class="color-metadata">
                        Confidence: {token.confidence:.0%} | Sources: {len(token.provenance)}
                        <br/>RGB: {getattr(token, "rgb", "") or "n/a"} | HSL: {getattr(token, "hsl", "") or "n/a"}
                        <br/>Contrast (W/B): {getattr(token, "wcag_contrast_on_white", "n/a")} / {getattr(token, "wcag_contrast_on_black", "n/a")}
                    </div>
                    <div class="details-panel">
                        {temperature_tag}{harmony_tag}
                        <div>{getattr(token, "semantic_names", "") or ""}</div>
                        <div class="badge">Closest: {getattr(token, "closest_css_named", "") or "n/a"}</div>
                    </div>
                    <div class="copy-button" onclick="copyToClipboard('{token.hex}', this)">Copy Hex</div>
                </div>
            </div>"""

            swatches.append(swatch_html)

        return "".join(swatches)

    def _generate_statistics(self) -> str:
        """Generate HTML for statistics section"""
        stats = self.library.statistics

        stats_html = f"""<div class="stats">
            <div class="stat">
                <div class="stat-value">{stats.get("color_count", 0)}</div>
                <div class="stat-label">Total Colors</div>
            </div>
            <div class="stat">
                <div class="stat-value">{stats.get("image_count", 0)}</div>
                <div class="stat-label">Images Analyzed</div>
            </div>
            <div class="stat">
                <div class="stat-value">{stats.get("avg_confidence", 0):.0%}</div>
                <div class="stat-label">Avg. Confidence</div>
            </div>
            <div class="stat">
                <div class="stat-value">{stats.get("multi_image_colors", 0)}</div>
                <div class="stat-label">Multi-Source Colors</div>
            </div>
        </div>"""

        return stats_html

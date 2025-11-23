"""
HTML Demo Page Generator for Spacing Tokens

Generates an interactive HTML demo page showing all extracted spacing tokens.
Follows the pattern of html_demo_generator.py for color tokens.
"""

import logging

from copy_that.tokens.spacing.aggregator import SpacingTokenLibrary

from .base_generator import BaseGenerator

logger = logging.getLogger(__name__)


class SpacingHTMLDemoGenerator(BaseGenerator):
    """Generate interactive HTML demo page for spacing tokens"""

    def __init__(self, library: SpacingTokenLibrary):
        """
        Initialize the HTML demo generator.

        Args:
            library: SpacingTokenLibrary to generate from
        """
        self.library = library

    def generate(self) -> str:
        """
        Generate HTML demo page with spacing visualizations.

        Returns:
            HTML string with interactive demo
        """
        spacings_html = self._generate_spacing_cards()
        stats_html = self._generate_statistics()
        scale_visual = self._generate_scale_visualization()

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spacing Token Library</title>
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
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
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

        .scale-section {{
            background: white;
            padding: 2rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }}

        .scale-section h2 {{
            margin-bottom: 1.5rem;
            color: #333;
        }}

        .scale-visual {{
            display: flex;
            align-items: flex-end;
            gap: 1rem;
            padding: 1rem;
            background: #fafafa;
            border-radius: 4px;
            overflow-x: auto;
        }}

        .scale-bar {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 0.5rem;
        }}

        .scale-bar-fill {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 4px;
            min-width: 40px;
            transition: transform 0.2s;
        }}

        .scale-bar-fill:hover {{
            transform: scaleY(1.1);
        }}

        .scale-bar-label {{
            font-size: 0.75rem;
            color: #666;
            text-align: center;
        }}

        .scale-bar-value {{
            font-weight: 600;
            font-size: 0.85rem;
            color: #333;
        }}

        .spacings-section {{
            background: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }}

        .spacings-section h2 {{
            margin-bottom: 1.5rem;
            color: #333;
        }}

        .spacings-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.5rem;
        }}

        .spacing-card {{
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            background: white;
            border: 1px solid #e0e0e0;
        }}

        .spacing-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        }}

        .spacing-visual {{
            padding: 1.5rem;
            background: #fafafa;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 1rem;
        }}

        .spacing-box {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
            font-size: 0.85rem;
        }}

        .spacing-demo {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .spacing-demo-box {{
            width: 20px;
            height: 20px;
            background: #e0e0e0;
            border-radius: 2px;
        }}

        .spacing-demo-gap {{
            background: rgba(102, 126, 234, 0.3);
            border: 1px dashed #667eea;
            border-radius: 2px;
        }}

        .spacing-info {{
            padding: 1rem;
            background: white;
        }}

        .spacing-name {{
            font-weight: 600;
            color: #333;
            margin-bottom: 0.25rem;
        }}

        .spacing-values {{
            font-family: monospace;
            font-size: 0.85rem;
            color: #666;
            margin-bottom: 0.5rem;
        }}

        .spacing-role {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            background: #f0f0f0;
            border-radius: 12px;
            font-size: 0.75rem;
            color: #666;
            margin-right: 0.5rem;
        }}

        .spacing-grid-badge {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 500;
        }}

        .grid-aligned {{
            background: #d4edda;
            color: #155724;
        }}

        .grid-misaligned {{
            background: #fff3cd;
            color: #856404;
        }}

        .spacing-metadata {{
            font-size: 0.8rem;
            color: #999;
            margin-top: 0.5rem;
        }}

        .copy-buttons {{
            display: flex;
            gap: 0.5rem;
            margin-top: 0.75rem;
        }}

        .copy-button {{
            flex: 1;
            padding: 0.5rem;
            background: none;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 0.75rem;
            cursor: pointer;
            transition: all 0.2s;
        }}

        .copy-button:hover {{
            background: #f0f0f0;
            border-color: #999;
        }}

        footer {{
            text-align: center;
            color: #999;
            font-size: 0.85rem;
            margin-top: 2rem;
        }}

        .code-preview {{
            background: #2d2d2d;
            border-radius: 4px;
            padding: 1rem;
            margin-top: 1rem;
            overflow-x: auto;
        }}

        .code-preview code {{
            color: #f8f8f2;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.8rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Spacing Token Library</h1>
            <p class="subtitle">Extracted and aggregated spacing tokens from design images</p>
        </header>

        {stats_html}

        <section class="scale-section">
            <h2>Spacing Scale</h2>
            {scale_visual}
        </section>

        <section class="spacings-section">
            <h2>Spacing Tokens</h2>
            <div class="spacings-grid">
                {spacings_html}
            </div>
        </section>

        <footer>
            <p>Generated by Copy That - Universal Multi-Modal Token Platform</p>
        </footer>
    </div>

    <script>
        function copyToClipboard(text, button) {{
            navigator.clipboard.writeText(text).then(() => {{
                const originalText = button.textContent;
                button.textContent = 'Copied!';
                setTimeout(() => {{
                    button.textContent = originalText;
                }}, 2000);
            }});
        }}
    </script>
</body>
</html>"""

        return html

    def _generate_spacing_cards(self) -> str:
        """Generate HTML for spacing cards."""
        if not self.library.tokens:
            return "<p>No spacing tokens available</p>"

        cards = []
        for token in self.library.tokens:
            role_badge = f'<span class="spacing-role">{token.role}</span>' if token.role else ""

            grid_badge = ""
            if token.grid_aligned is not None:
                if token.grid_aligned:
                    grid_badge = '<span class="spacing-grid-badge grid-aligned">Grid Aligned</span>'
                else:
                    grid_badge = '<span class="spacing-grid-badge grid-misaligned">Off Grid</span>'

            # Create visual representation
            box_size = min(token.value_px, 100)  # Cap at 100px for display
            box_style = f"width: {box_size}px; height: {box_size}px;"

            # Demo with gap
            gap_style = f"width: {min(token.value_px, 60)}px; height: 20px;"

            card_html = f"""<div class="spacing-card">
                <div class="spacing-visual">
                    <div class="spacing-box" style="{box_style}">{token.value_px}px</div>
                    <div class="spacing-demo">
                        <div class="spacing-demo-box"></div>
                        <div class="spacing-demo-gap" style="{gap_style}"></div>
                        <div class="spacing-demo-box"></div>
                    </div>
                </div>
                <div class="spacing-info">
                    <div class="spacing-name">{token.name}</div>
                    <div class="spacing-values">{token.value_px}px | {token.value_rem}rem</div>
                    {role_badge}
                    {grid_badge}
                    <div class="spacing-metadata">
                        Confidence: {token.confidence:.0%} | Sources: {len(token.provenance)}
                    </div>
                    <div class="copy-buttons">
                        <button class="copy-button" onclick="copyToClipboard('{token.value_px}px', this)">Copy px</button>
                        <button class="copy-button" onclick="copyToClipboard('{token.value_rem}rem', this)">Copy rem</button>
                        <button class="copy-button" onclick="copyToClipboard('--{token.name}', this)">Copy var</button>
                    </div>
                </div>
            </div>"""

            cards.append(card_html)

        return "".join(cards)

    def _generate_statistics(self) -> str:
        """Generate HTML for statistics section."""
        stats = self.library.statistics

        stats_html = f"""<div class="stats">
            <div class="stat">
                <div class="stat-value">{stats.get("spacing_count", 0)}</div>
                <div class="stat-label">Total Spacings</div>
            </div>
            <div class="stat">
                <div class="stat-value">{stats.get("image_count", 0)}</div>
                <div class="stat-label">Images Analyzed</div>
            </div>
            <div class="stat">
                <div class="stat-value">{stats.get("scale_system", "custom")}</div>
                <div class="stat-label">Scale System</div>
            </div>
            <div class="stat">
                <div class="stat-value">{stats.get("base_unit", 0)}px</div>
                <div class="stat-label">Base Unit</div>
            </div>
            <div class="stat">
                <div class="stat-value">{stats.get("grid_compliance", 0):.0%}</div>
                <div class="stat-label">Grid Compliance</div>
            </div>
            <div class="stat">
                <div class="stat-value">{stats.get("multi_image_spacings", 0)}</div>
                <div class="stat-label">Multi-Source</div>
            </div>
        </div>"""

        return stats_html

    def _generate_scale_visualization(self) -> str:
        """Generate visual representation of the spacing scale."""
        if not self.library.tokens:
            return "<p>No spacing tokens available</p>"

        bars = []
        max_value = max(t.value_px for t in self.library.tokens)

        for token in self.library.tokens:
            # Calculate bar height (max 200px)
            bar_height = min(200, (token.value_px / max_value) * 200) if max_value > 0 else 0

            bar_html = f"""<div class="scale-bar">
                <div class="scale-bar-fill" style="height: {bar_height}px;"></div>
                <div class="scale-bar-value">{token.value_px}px</div>
                <div class="scale-bar-label">{token.role or token.name}</div>
            </div>"""

            bars.append(bar_html)

        return f'<div class="scale-visual">{"".join(bars)}</div>'

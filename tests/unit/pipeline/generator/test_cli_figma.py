"""Tests for generate_figma_tokens CLI helper."""

from pathlib import Path

from scripts.generate_figma_tokens import generate_figma


def test_generate_figma(tmp_path: Path):
    """Ensure figma output is produced from simple token JSON."""
    input_path = tmp_path / "tokens.json"
    output_path = tmp_path / "figma.json"
    input_path.write_text(
        """
        {
          "tokens": [
            {
              "name": "primary",
              "path": ["color", "brand"],
              "token_type": "color",
              "w3c_type": "color",
              "value": "#FF6B35",
              "confidence": 0.95,
              "description": "Primary brand color"
            }
          ]
        }
        """
    )

    generate_figma(input_path, output_path)

    content = output_path.read_text()
    assert '"version": "1.0"' in content
    assert '"collections"' in content

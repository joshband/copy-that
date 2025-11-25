#!/usr/bin/env python
"""
Generate Figma design tokens JSON from a simple token JSON file.

Input JSON shape (list or { "tokens": [...] }):
[
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
"""

import argparse
import json
from pathlib import Path
from typing import Any

from copy_that.pipeline import TokenResult, TokenType, W3CTokenType
from copy_that.pipeline.generator.agent import GeneratorAgent, OutputFormat


def load_tokens(input_path: Path) -> list[TokenResult]:
    raw = json.loads(input_path.read_text())
    items: list[dict[str, Any]] = (
        raw["tokens"] if isinstance(raw, dict) and "tokens" in raw else raw
    )
    tokens: list[TokenResult] = []
    for item in items:
        tokens.append(
            TokenResult(
                token_type=TokenType(item["token_type"]),
                name=item["name"],
                path=item.get("path", []),
                w3c_type=W3CTokenType(item["w3c_type"]) if item.get("w3c_type") else None,
                value=item["value"],
                description=item.get("description"),
                reference=item.get("reference"),
                confidence=float(item.get("confidence", 1.0)),
                extensions=item.get("extensions"),
                metadata=item.get("metadata"),
            )
        )
    return tokens


def generate_figma(input_path: Path, output_path: Path) -> None:
    tokens = load_tokens(input_path)
    agent = GeneratorAgent(output_format=OutputFormat.FIGMA)
    output = agent._env.get_template("figma.j2").render(
        tokens=tokens, token_tree={}, format="figma"
    )  # noqa: SLF001
    output_path.write_text(output)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Figma tokens JSON from token list.")
    parser.add_argument("--input", required=True, help="Path to input token JSON")
    parser.add_argument("--output", required=True, help="Path to write figma JSON")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    generate_figma(input_path, output_path)
    print(f"Figma tokens written to {output_path}")


if __name__ == "__main__":
    main()

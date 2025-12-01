"""Simple CLI to inspect a token graph from a W3C JSON file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from core.tokens.adapters import w3c
from core.tokens.graph import TokenGraph
from core.tokens.repository import InMemoryTokenRepository


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect a token graph from W3C JSON.")
    parser.add_argument("path", type=Path, help="Path to W3C design tokens JSON file")
    args = parser.parse_args()

    data = json.loads(args.path.read_text())
    repo = InMemoryTokenRepository()
    w3c.w3c_to_tokens(data, repo)
    graph = TokenGraph(repo)
    summary = graph.summarize()

    print("Token Graph Summary")
    print("-------------------")
    print(f"Counts: {summary.get('counts', {})}")
    print(f"Relations: {summary.get('relation_counts', {})}")
    print(f"Dangling relations: {len(summary.get('dangling_relations', []))}")
    if summary.get("dangling_relations"):
        for entry in summary["dangling_relations"]:
            print(f"  {entry['source']} -> {entry['target']} ({entry['type']})")
    print(f"Cycles: {summary.get('cycle_count', 0)}")
    if summary.get("cycles"):
        for cycle in summary["cycles"]:
            print("  cycle:", " -> ".join(cycle))


if __name__ == "__main__":
    main()

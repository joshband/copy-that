"""Resolver document helpers for W3C Design Tokens 2025.10."""

from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Any


def make_resolver_2025_10(
    sources: dict[str, str],
    contexts: dict[str, Sequence[str]],
    resolution_priority: Sequence[str],
) -> dict[str, object]:
    """Build a resolver document for the 2025.10 spec."""
    return {
        "version": "2025.10",
        "sources": sources,
        "contexts": {name: list(values) for name, values in contexts.items()},
        "resolutionOrder": list(resolution_priority),
    }


def resolver_json(
    sources: dict[str, str],
    contexts: dict[str, Sequence[str]],
    resolution_priority: Sequence[str],
) -> str:
    """Serialize a resolver document to JSON."""
    return json.dumps(
        make_resolver_2025_10(sources, contexts, resolution_priority),
        indent=2,
    )


def validate_resolver_cross_fields(resolver: dict[str, Any]) -> list[str]:
    """Return cross-field validation errors for resolver documents."""
    errors: list[str] = []
    sources = resolver.get("sources")
    contexts = resolver.get("contexts")
    resolution_order = resolver.get("resolutionOrder")

    if not isinstance(sources, dict):
        return ["sources must be an object"]
    if not isinstance(contexts, dict):
        return ["contexts must be an object"]
    if not isinstance(resolution_order, list):
        return ["resolutionOrder must be an array"]

    source_names = set(sources.keys())
    context_names = set(contexts.keys())

    for ctx_name, ctx_sources in contexts.items():
        if not isinstance(ctx_sources, list):
            errors.append(f"context '{ctx_name}' must list sources")
            continue
        missing_sources = sorted(src for src in ctx_sources if src not in source_names)
        if missing_sources:
            errors.append(
                f"context '{ctx_name}' references unknown sources: {', '.join(missing_sources)}"
            )

    for ctx in resolution_order:
        if ctx not in context_names:
            errors.append(f"resolutionOrder references unknown context: {ctx}")

    missing_contexts = sorted(context_names - set(resolution_order))
    if missing_contexts:
        errors.append(f"resolutionOrder missing contexts: {', '.join(missing_contexts)}")

    return errors

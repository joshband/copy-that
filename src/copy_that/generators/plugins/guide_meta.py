"""Helpers shared by generators for optional GuidePack / brand grouping."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def guide_pack_comment_block(component_meta: Mapping[str, Any] | None) -> list[str]:
    """Emit comment lines grouping output by brand roles when GuidePack meta is present."""
    if not isinstance(component_meta, Mapping):
        return []
    brand = component_meta.get("brand")
    if not isinstance(brand, Mapping):
        return []
    lines = ["/* Guide Pack brand grouping */"]
    name = brand.get("name")
    if name:
        lines.append(f"/* Brand: {name} */")
    roles = brand.get("roles")
    if isinstance(roles, Mapping) and roles:
        lines.append("/* Roles: */")
        for role, token_id in sorted(roles.items(), key=lambda kv: str(kv[0])):
            lines.append(f"/*   {role} -> {token_id} */")
    foundations = component_meta.get("foundations")
    if isinstance(foundations, Mapping):
        for family in ("colors", "gradients", "typography", "shadows"):
            ids = foundations.get(family)
            if isinstance(ids, list) and ids:
                preview = ", ".join(str(i) for i in ids[:6])
                more = f" (+{len(ids) - 6} more)" if len(ids) > 6 else ""
                lines.append(f"/* Foundations.{family}: {preview}{more} */")
    snap = component_meta.get("token_snapshot_hash")
    if snap:
        lines.append(f"/* token_snapshot: {snap} */")
    return lines


def guide_pack_ts_comment_block(component_meta: Mapping[str, Any] | None) -> list[str]:
    """TypeScript/JS comment variant of :func:`guide_pack_comment_block`."""
    css_lines = guide_pack_comment_block(component_meta)
    out: list[str] = []
    for line in css_lines:
        if line.startswith("/* ") and line.endswith(" */"):
            out.append("// " + line[3:-3])
        elif line.startswith("/*") and line.endswith("*/"):
            out.append("// " + line[2:-2].strip())
        else:
            out.append("// " + line)
    return out

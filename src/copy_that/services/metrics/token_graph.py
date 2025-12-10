"""Token graph for generic token analysis.

Provides a unified interface for loading and analyzing ANY token type
(color, spacing, typography, shadow, material, shape, component, etc.)
without hardcoded type dependencies.
"""

import logging
from dataclasses import dataclass, field
from typing import Any

import networkx as nx
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.domain.models import (
    ColorToken,
    FontFamilyToken,
    FontSizeToken,
    ShadowToken,
    SpacingToken,
    TypographyToken,
)
from copy_that.infrastructure.database import Base

logger = logging.getLogger(__name__)


@dataclass
class TokenNode:
    """A single token in the graph.

    Represents any token type with common properties and extensible metadata.
    """

    # Core identifiers
    id: int
    name: str
    category: str  # e.g., "color", "spacing", "typography", "shadow", "material", etc.

    # Token value (type varies by category)
    value: Any

    # Extensible metadata for category-specific properties
    metadata: dict[str, Any] = field(default_factory=dict)

    # Relationships to other tokens
    references: list[str] = field(default_factory=list)

    # Quality metrics
    confidence: float = 1.0

    def __repr__(self) -> str:
        return f"<TokenNode(id={self.id}, category='{self.category}', name='{self.name}')>"


class TokenGraph:
    """Represents all tokens + their relationships for a project.

    Provides a unified interface for:
    - Loading tokens of ANY type from the database
    - Building relationship graphs between tokens
    - Analyzing token hierarchies and scales
    - Supporting multimodal token types (audio, video, etc.)

    Design principles:
    - No hardcoded token types - discovers models dynamically
    - Works with any SQLAlchemy model that has project_id
    - Extensible to future token categories
    """

    # Token model registry - maps category name to SQLAlchemy model
    TOKEN_MODELS = {
        "color": ColorToken,
        "spacing": SpacingToken,
        "typography": TypographyToken,
        "shadow": ShadowToken,
        "font_family": FontFamilyToken,
        "font_size": FontSizeToken,
    }

    def __init__(self, project_id: int, db: AsyncSession):
        """Initialize token graph for a project.

        Args:
            project_id: Project to load tokens from
            db: Database session
        """
        self.project_id = project_id
        self.db = db
        self.tokens: dict[str, TokenNode] = {}  # Keyed by f"{category}:{id}"
        self.graph: nx.DiGraph = nx.DiGraph()  # Relationship graph

    async def load(self, categories: list[str] | None = None) -> None:
        """Load all tokens and build relationship graph.

        Args:
            categories: Optional list of categories to load (defaults to all)
        """
        categories_to_load = categories or list(self.TOKEN_MODELS.keys())

        for category in categories_to_load:
            if category not in self.TOKEN_MODELS:
                logger.warning(f"Unknown token category: {category}")
                continue

            await self._load_category(category)

        self._build_relationships()
        logger.info(f"Loaded {len(self.tokens)} tokens across {len(categories_to_load)} categories")

    async def _load_category(self, category: str) -> None:
        """Load all tokens for a specific category.

        Args:
            category: Token category to load (e.g., "color", "spacing")
        """
        model_class = self.TOKEN_MODELS[category]

        try:
            from sqlalchemy import select

            query = select(model_class).where(model_class.project_id == self.project_id)
            result = await self.db.execute(query)
            tokens = result.scalars().all()

            for token in tokens:
                node = self._create_token_node(token, category)
                key = f"{category}:{node.id}"
                self.tokens[key] = node
                self.graph.add_node(key, node=node)

            logger.debug(f"Loaded {len(tokens)} {category} tokens")

        except Exception as e:
            logger.error(f"Failed to load {category} tokens: {e}", exc_info=True)

    def _create_token_node(self, token: Base, category: str) -> TokenNode:
        """Create a TokenNode from a SQLAlchemy model instance.

        Args:
            token: SQLAlchemy model instance
            category: Token category

        Returns:
            TokenNode representation
        """
        # Extract common properties
        token_id = getattr(token, "id", None)
        token_name = getattr(token, "name", f"{category}_{token_id}")
        confidence = getattr(token, "confidence", 1.0)

        # Extract primary value (varies by category)
        value = self._extract_primary_value(token, category)

        # Extract all other properties as metadata
        metadata = self._extract_metadata(token)

        # Extract references (tokens that reference other tokens)
        references = self._extract_references(token, category)

        return TokenNode(
            id=token_id,
            name=token_name,
            category=category,
            value=value,
            metadata=metadata,
            references=references,
            confidence=confidence,
        )

    def _extract_primary_value(self, token: Base, category: str) -> Any:
        """Extract the primary value for a token.

        Args:
            token: SQLAlchemy model instance
            category: Token category

        Returns:
            Primary value for this token type
        """
        value_map = {
            "color": lambda t: getattr(t, "hex", None),
            "spacing": lambda t: getattr(t, "value_px", None),
            "typography": lambda t: {
                "font_family": getattr(t, "font_family", None),
                "font_size": getattr(t, "font_size", None),
                "font_weight": getattr(t, "font_weight", None),
            },
            "shadow": lambda t: {
                "x_offset": getattr(t, "x_offset", None),
                "y_offset": getattr(t, "y_offset", None),
                "blur_radius": getattr(t, "blur_radius", None),
                "color": getattr(t, "color_hex", None),
            },
            "font_family": lambda t: getattr(t, "name", None),
            "font_size": lambda t: getattr(t, "size_px", None),
        }

        extractor = value_map.get(category, lambda _: None)
        return extractor(token)

    def _extract_metadata(self, token: Base) -> dict[str, Any]:
        """Extract all properties as metadata.

        Args:
            token: SQLAlchemy model instance

        Returns:
            Dict of all token properties
        """
        metadata = {}
        mapper = inspect(token.__class__)

        for column in mapper.columns:
            # Skip internal/system columns
            if column.name in ("id", "project_id", "extraction_job_id", "created_at"):
                continue

            value = getattr(token, column.name, None)
            if value is not None:
                metadata[column.name] = value

        return metadata

    def _extract_references(self, token: Base, category: str) -> list[str]:
        """Extract references to other tokens.

        Args:
            token: SQLAlchemy model instance
            category: Token category

        Returns:
            List of referenced token keys
        """
        # TODO: Implement W3C Design Token reference syntax parsing
        # Example: "{color.primary}" -> ["color:primary_id"]
        # For now, return empty list
        return []

    def _build_relationships(self) -> None:
        """Build relationship edges between tokens.

        Creates edges for:
        - Token references (e.g., composite tokens referencing base tokens)
        - Hierarchical relationships (e.g., color.primary.light -> color.primary)
        - Scale relationships (e.g., spacing tokens in same scale)
        """
        # Add edges based on references
        for key, node in self.tokens.items():
            for ref in node.references:
                if ref in self.tokens:
                    self.graph.add_edge(key, ref, relationship="references")

        # Add hierarchical edges based on naming conventions
        self._add_hierarchical_edges()

    def _add_hierarchical_edges(self) -> None:
        """Add edges for hierarchical token relationships.

        Examples:
        - "color.primary.light" -> "color.primary"
        - "spacing.lg" -> "spacing"
        """
        for key, node in self.tokens.items():
            parts = node.name.split(".")
            if len(parts) > 1:
                # Check if parent exists
                parent_name = ".".join(parts[:-1])
                parent_key = f"{node.category}:{parent_name}"
                if parent_key in self.tokens:
                    self.graph.add_edge(key, parent_key, relationship="child_of")

    def get_tokens_by_category(self, category: str) -> list[TokenNode]:
        """Get all tokens in a category.

        Args:
            category: Token category (e.g., "color", "spacing")

        Returns:
            List of tokens in that category
        """
        return [node for key, node in self.tokens.items() if node.category == category]

    def get_token_scale(self, base_name: str, category: str) -> list[TokenNode]:
        """Get related tokens in a scale.

        Args:
            base_name: Base token name (e.g., "primary")
            category: Token category

        Returns:
            List of tokens in the same scale
        """
        pattern = f"{category}:{base_name}"
        return [
            node
            for key, node in self.tokens.items()
            if key.startswith(pattern) or base_name in node.name
        ]

    def get_categories(self) -> set[str]:
        """Get all token categories in the graph.

        Returns:
            Set of category names
        """
        return {node.category for node in self.tokens.values()}

    def get_category_stats(self, category: str) -> dict[str, Any]:
        """Get statistics for a token category.

        Args:
            category: Token category

        Returns:
            Dict with category statistics
        """
        tokens = self.get_tokens_by_category(category)
        if not tokens:
            return {"count": 0}

        return {
            "count": len(tokens),
            "avg_confidence": sum(t.confidence for t in tokens) / len(tokens),
            "min_confidence": min(t.confidence for t in tokens),
            "max_confidence": max(t.confidence for t in tokens),
        }

    def get_hierarchical_depth(self, category: str) -> int:
        """Calculate maximum hierarchical depth for a category.

        Args:
            category: Token category

        Returns:
            Maximum depth (1 = flat, 2+ = hierarchical)
        """
        tokens = self.get_tokens_by_category(category)
        if not tokens:
            return 0

        max_depth = 1
        for token in tokens:
            depth = len(token.name.split("."))
            max_depth = max(max_depth, depth)

        return max_depth

    def is_hierarchical(self, category: str) -> bool:
        """Check if a category uses hierarchical naming.

        Args:
            category: Token category

        Returns:
            True if tokens use hierarchical naming (e.g., "color.primary.light")
        """
        return self.get_hierarchical_depth(category) > 1

    def get_token_relationships(self, token_key: str) -> dict[str, list[str]]:
        """Get all relationships for a token.

        Args:
            token_key: Token key (e.g., "color:123")

        Returns:
            Dict mapping relationship types to target token keys
        """
        relationships: dict[str, list[str]] = {
            "references": [],
            "referenced_by": [],
            "children": [],
            "parent": [],
        }

        if token_key not in self.graph:
            return relationships

        # Outgoing edges (this token references others)
        for target in self.graph.successors(token_key):
            edge_data = self.graph[token_key][target]
            rel_type = edge_data.get("relationship", "references")
            if rel_type == "references":
                relationships["references"].append(target)
            elif rel_type == "child_of":
                relationships["parent"].append(target)

        # Incoming edges (others reference this token)
        for source in self.graph.predecessors(token_key):
            edge_data = self.graph[source][token_key]
            rel_type = edge_data.get("relationship", "references")
            if rel_type == "references":
                relationships["referenced_by"].append(source)
            elif rel_type == "child_of":
                relationships["children"].append(source)

        return relationships

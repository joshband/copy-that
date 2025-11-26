"""
AggregationAgent module

Orchestrates deduplication and provenance tracking for token aggregation.
Supports K-means clustering for grouping related tokens.
"""

from datetime import datetime
from typing import Any

from copy_that.pipeline import (
    AggregationError,
    BasePipelineAgent,
    PipelineTask,
    TokenResult,
    TokenType,
)
from copy_that.pipeline.aggregation.deduplicator import ColorDeduplicator
from copy_that.pipeline.aggregation.provenance import ProvenanceRecord, ProvenanceTracker


class AggregationAgent(BasePipelineAgent):
    """
    Pipeline agent for aggregating and deduplicating tokens.

    Orchestrates ColorDeduplicator and ProvenanceTracker to:
    - Deduplicate similar colors using Delta-E comparison
    - Track provenance (source images) for each token
    - Optionally cluster tokens using K-means

    Example:
        >>> agent = AggregationAgent()
        >>> task = PipelineTask(
        ...     task_id="task-001",
        ...     image_url="https://example.com/design.png",
        ...     token_types=[TokenType.COLOR],
        ...     context={"input_tokens": tokens}
        ... )
        >>> results = await agent.process(task)
    """

    def __init__(self) -> None:
        """Initialize with deduplicator and provenance tracker."""
        self._deduplicator = ColorDeduplicator()
        self._provenance_tracker = ProvenanceTracker()

    @property
    def agent_type(self) -> str:
        """Return the agent type identifier."""
        return "aggregator"

    @property
    def stage_name(self) -> str:
        """Return the pipeline stage name."""
        return "aggregation"

    async def process(self, task: PipelineTask) -> list[TokenResult]:
        """
        Process task: deduplicate, track provenance, cluster.

        Args:
            task: Pipeline task with input tokens in context

        Returns:
            List of aggregated TokenResult objects with provenance

        Raises:
            AggregationError: If processing fails
        """
        try:
            # Extract configuration from context
            context = task.context or {}
            enable_deduplication = context.get("enable_deduplication", True)
            enable_provenance = context.get("enable_provenance", True)
            enable_clustering = context.get("enable_clustering", False)
            n_clusters = context.get("n_clusters", 5)
            deduplication_threshold = context.get("deduplication_threshold", 2.0)

            # Also check nested configuration format from tests
            if "clustering" in context:
                clustering_config = context["clustering"]
                enable_clustering = clustering_config.get("enabled", enable_clustering)
                n_clusters = clustering_config.get("n_clusters", n_clusters)

            if "deduplication" in context:
                dedup_config = context["deduplication"]
                deduplication_threshold = dedup_config.get("threshold", deduplication_threshold)

            # Check for force_error in context (for testing)
            if context.get("force_error"):
                raise AggregationError(
                    "Forced error for testing", details={"task_id": task.task_id}
                )

            # Extract input tokens
            tokens = self._extract_input_tokens(task)

            if not tokens:
                return []

            # Track provenance for each token
            if enable_provenance:
                self._track_provenance(tokens, task)

            # Deduplicate color tokens
            if enable_deduplication:
                # Update deduplicator threshold if different from default
                if deduplication_threshold != 2.0:
                    self._deduplicator = ColorDeduplicator(threshold=deduplication_threshold)

                tokens = self._deduplicator.deduplicate(tokens)

            # Apply provenance to tokens
            if enable_provenance:
                tokens = self._apply_provenance(tokens)

            # Optionally cluster tokens
            if enable_clustering and len(tokens) > 0:
                # Validate n_clusters
                if n_clusters <= 0:
                    raise AggregationError(
                        f"Invalid n_clusters value: {n_clusters}",
                        details={"task_id": task.task_id, "n_clusters": n_clusters},
                    )
                tokens = self._cluster_tokens(tokens, n_clusters)

            return tokens

        except AggregationError:
            raise
        except Exception as e:
            raise AggregationError(
                f"Aggregation failed: {str(e)}",
                details={"task_id": task.task_id, "error_type": type(e).__name__},
            ) from e

    async def health_check(self) -> bool:
        """
        Check if agent is healthy.

        Verifies that ColorDeduplicator and ProvenanceTracker are available.

        Returns:
            True if healthy, False otherwise
        """
        try:
            # Verify deduplicator is available
            if self._deduplicator is None:
                return False

            # Verify provenance tracker is available
            return self._provenance_tracker is not None
        except Exception:
            return False

    def _cluster_tokens(self, tokens: list[TokenResult], n_clusters: int) -> list[TokenResult]:
        """
        Group tokens using K-means clustering on color values.

        Args:
            tokens: List of tokens to cluster
            n_clusters: Number of clusters to create

        Returns:
            List of representative tokens from each cluster
        """
        # Separate color tokens from non-color tokens
        color_tokens = [t for t in tokens if t.token_type == TokenType.COLOR]
        non_color_tokens = [t for t in tokens if t.token_type != TokenType.COLOR]

        if len(color_tokens) <= n_clusters:
            # Not enough tokens to cluster meaningfully
            return tokens

        # Extract RGB values from colors
        rgb_values = []
        valid_tokens = []
        for token in color_tokens:
            rgb = self._extract_rgb(token.value)
            if rgb is not None:
                rgb_values.append(rgb)
                valid_tokens.append(token)

        if len(valid_tokens) <= n_clusters:
            return tokens

        # Perform K-means clustering
        try:
            clustered = self._kmeans_cluster(valid_tokens, rgb_values, n_clusters)
        except Exception:
            # Fallback: return original tokens if clustering fails
            return tokens

        # Combine clustered color tokens with non-color tokens
        return clustered + non_color_tokens

    def _extract_input_tokens(self, task: PipelineTask) -> list[TokenResult]:
        """
        Extract input tokens from task context.

        Args:
            task: Pipeline task

        Returns:
            List of TokenResult objects from context

        Raises:
            AggregationError: If tokens are invalid
        """
        context = task.context or {}
        input_tokens = context.get("input_tokens", [])

        if input_tokens is None:
            return []

        if not isinstance(input_tokens, list):
            raise AggregationError(
                "Invalid input_tokens type",
                details={"expected": "list", "got": type(input_tokens).__name__},
            )

        # Validate each token
        result = []
        for i, token in enumerate(input_tokens):
            if isinstance(token, TokenResult):
                result.append(token)
            elif isinstance(token, dict):
                # Try to convert dict to TokenResult
                try:
                    result.append(TokenResult(**token))
                except Exception as e:
                    raise AggregationError(
                        f"Invalid token at index {i}: {str(e)}",
                        details={"index": i, "token": token},
                    ) from e
            else:
                raise AggregationError(
                    f"Invalid token type at index {i}",
                    details={"index": i, "type": type(token).__name__},
                )

        return result

    def _track_provenance(self, tokens: list[TokenResult], task: PipelineTask) -> None:
        """
        Track provenance for each token.

        Args:
            tokens: List of tokens to track
            task: Pipeline task containing source information
        """
        context = task.context or {}
        provenance_config = context.get("provenance", {})
        source_id = provenance_config.get("source_id", task.image_url)
        include_timestamps = provenance_config.get("include_timestamps", True)

        timestamp = datetime.utcnow() if include_timestamps else datetime.min

        for token in tokens:
            # Generate a unique token ID based on name and path
            token_id = self._generate_token_id(token)

            record = ProvenanceRecord(
                image_id=source_id,
                confidence=token.confidence,
                timestamp=timestamp,
                metadata={
                    "task_id": task.task_id,
                    "token_type": token.token_type
                    if isinstance(token.token_type, str)
                    else token.token_type.value,
                },
            )

            self._provenance_tracker.add_provenance(token_id, record)

    def _apply_provenance(self, tokens: list[TokenResult]) -> list[TokenResult]:
        """
        Apply provenance information to tokens.

        Args:
            tokens: List of tokens to update

        Returns:
            List of tokens with provenance in extensions
        """
        result = []
        for token in tokens:
            token_id = self._generate_token_id(token)
            updated_token = self._provenance_tracker.apply_to_token(token_id, token)
            result.append(updated_token)

        return result

    def _generate_token_id(self, token: TokenResult) -> str:
        """
        Generate a unique ID for a token.

        Args:
            token: Token to generate ID for

        Returns:
            Unique string identifier
        """
        if token.path:
            return ".".join(token.path + [token.name])
        return token.name

    def _extract_rgb(self, color_value: Any) -> tuple[int, int, int] | None:
        """
        Extract RGB values from a color value.

        Args:
            color_value: Color in various formats (hex, rgb, etc.)

        Returns:
            Tuple of (R, G, B) values or None if extraction fails
        """
        if not isinstance(color_value, str):
            return None

        color_str = color_value.strip().lower()

        # Handle hex format
        if color_str.startswith("#"):
            hex_color = color_str[1:]
            if len(hex_color) == 3:
                # Short hex format
                hex_color = "".join(c * 2 for c in hex_color)
            if len(hex_color) == 6:
                try:
                    r = int(hex_color[0:2], 16)
                    g = int(hex_color[2:4], 16)
                    b = int(hex_color[4:6], 16)
                    return (r, g, b)
                except ValueError:
                    return None
            elif len(hex_color) == 8:
                # Hex with alpha
                try:
                    r = int(hex_color[0:2], 16)
                    g = int(hex_color[2:4], 16)
                    b = int(hex_color[4:6], 16)
                    return (r, g, b)
                except ValueError:
                    return None

        # Handle rgb/rgba format
        if color_str.startswith("rgb"):
            try:
                # Extract numbers from rgb(r, g, b) or rgba(r, g, b, a)
                parts = color_str.replace("rgba", "").replace("rgb", "")
                parts = parts.replace("(", "").replace(")", "")
                values = [v.strip() for v in parts.split(",")]
                r = int(float(values[0]))
                g = int(float(values[1]))
                b = int(float(values[2]))
                return (r, g, b)
            except (ValueError, IndexError):
                return None

        # Handle hsl/hsla format - convert to RGB
        if color_str.startswith("hsl"):
            try:
                parts = color_str.replace("hsla", "").replace("hsl", "")
                parts = parts.replace("(", "").replace(")", "")
                values = [v.strip().rstrip("%") for v in parts.split(",")]
                h = float(values[0]) / 360.0
                s = float(values[1]) / 100.0
                l_val = float(values[2]) / 100.0

                # HSL to RGB conversion
                if s == 0:
                    r = g = b = int(l_val * 255)
                else:

                    def hue_to_rgb(p: float, q: float, t: float) -> float:
                        if t < 0:
                            t += 1
                        if t > 1:
                            t -= 1
                        if t < 1 / 6:
                            return p + (q - p) * 6 * t
                        if t < 1 / 2:
                            return q
                        if t < 2 / 3:
                            return p + (q - p) * (2 / 3 - t) * 6
                        return p

                    q = l_val * (1 + s) if l_val < 0.5 else l_val + s - l_val * s
                    p = 2 * l_val - q
                    r = int(hue_to_rgb(p, q, h + 1 / 3) * 255)
                    g = int(hue_to_rgb(p, q, h) * 255)
                    b = int(hue_to_rgb(p, q, h - 1 / 3) * 255)

                return (r, g, b)
            except (ValueError, IndexError):
                return None

        return None

    def _kmeans_cluster(
        self, tokens: list[TokenResult], rgb_values: list[tuple[int, int, int]], n_clusters: int
    ) -> list[TokenResult]:
        """
        Perform K-means clustering on tokens.

        Uses sklearn if available, otherwise falls back to simple implementation.

        Args:
            tokens: Tokens to cluster
            rgb_values: RGB values for each token
            n_clusters: Number of clusters

        Returns:
            Representative tokens from each cluster
        """
        try:
            # Try to use sklearn for K-means
            import numpy as np
            from sklearn.cluster import KMeans  # type: ignore[import-not-found,import-untyped]

            # Convert to numpy array
            X = np.array(rgb_values)

            # Perform K-means
            kmeans = KMeans(n_clusters=min(n_clusters, len(tokens)), random_state=42, n_init=10)
            labels = kmeans.fit_predict(X)

            # Select best token from each cluster (highest confidence)
            clusters: dict[int, list[tuple[TokenResult, tuple[int, int, int]]]] = {}
            for i, label in enumerate(labels):
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append((tokens[i], rgb_values[i]))

            result = []
            for cluster_tokens in clusters.values():
                # Select token with highest confidence
                best_token = max(cluster_tokens, key=lambda x: x[0].confidence)[0]

                # Add cluster metadata
                if best_token.metadata is None:
                    updated_token = TokenResult(
                        token_type=best_token.token_type,
                        name=best_token.name,
                        path=best_token.path,
                        w3c_type=best_token.w3c_type,
                        value=best_token.value,
                        description=best_token.description,
                        reference=best_token.reference,
                        confidence=best_token.confidence,
                        extensions=best_token.extensions,
                        metadata={"cluster_size": len(cluster_tokens)},
                    )
                else:
                    metadata = dict(best_token.metadata)
                    metadata["cluster_size"] = len(cluster_tokens)
                    updated_token = TokenResult(
                        token_type=best_token.token_type,
                        name=best_token.name,
                        path=best_token.path,
                        w3c_type=best_token.w3c_type,
                        value=best_token.value,
                        description=best_token.description,
                        reference=best_token.reference,
                        confidence=best_token.confidence,
                        extensions=best_token.extensions,
                        metadata=metadata,
                    )
                result.append(updated_token)

            return result

        except ImportError:
            # Fallback to simple K-means implementation
            return self._simple_kmeans(tokens, rgb_values, n_clusters)

    def _simple_kmeans(
        self, tokens: list[TokenResult], rgb_values: list[tuple[int, int, int]], n_clusters: int
    ) -> list[TokenResult]:
        """
        Simple K-means implementation without external dependencies.

        Args:
            tokens: Tokens to cluster
            rgb_values: RGB values for each token
            n_clusters: Number of clusters

        Returns:
            Representative tokens from each cluster
        """
        import random

        n_clusters = min(n_clusters, len(tokens))

        # Initialize centroids randomly
        indices = random.sample(range(len(tokens)), n_clusters)
        centroids = [rgb_values[i] for i in indices]

        # Run K-means iterations
        max_iterations = 100
        for _ in range(max_iterations):
            # Assign points to nearest centroid
            clusters: dict[int, list[int]] = {i: [] for i in range(n_clusters)}
            for i, rgb in enumerate(rgb_values):
                min_dist = float("inf")
                nearest_cluster = 0
                for j, centroid in enumerate(centroids):
                    dist = sum((a - b) ** 2 for a, b in zip(rgb, centroid, strict=False))
                    if dist < min_dist:
                        min_dist = dist
                        nearest_cluster = j
                clusters[nearest_cluster].append(i)

            # Update centroids
            new_centroids = []
            for j in range(n_clusters):
                if clusters[j]:
                    avg_r = sum(rgb_values[i][0] for i in clusters[j]) // len(clusters[j])
                    avg_g = sum(rgb_values[i][1] for i in clusters[j]) // len(clusters[j])
                    avg_b = sum(rgb_values[i][2] for i in clusters[j]) // len(clusters[j])
                    new_centroids.append((avg_r, avg_g, avg_b))
                else:
                    new_centroids.append(centroids[j])

            # Check for convergence
            if new_centroids == centroids:
                break
            centroids = new_centroids

        # Select best token from each cluster
        result = []
        for j in range(n_clusters):
            if clusters[j]:
                cluster_tokens = [tokens[i] for i in clusters[j]]
                best_token = max(cluster_tokens, key=lambda t: t.confidence)

                # Add cluster metadata
                if best_token.metadata is None:
                    updated_token = TokenResult(
                        token_type=best_token.token_type,
                        name=best_token.name,
                        path=best_token.path,
                        w3c_type=best_token.w3c_type,
                        value=best_token.value,
                        description=best_token.description,
                        reference=best_token.reference,
                        confidence=best_token.confidence,
                        extensions=best_token.extensions,
                        metadata={"cluster_size": len(clusters[j])},
                    )
                else:
                    metadata = dict(best_token.metadata)
                    metadata["cluster_size"] = len(clusters[j])
                    updated_token = TokenResult(
                        token_type=best_token.token_type,
                        name=best_token.name,
                        path=best_token.path,
                        w3c_type=best_token.w3c_type,
                        value=best_token.value,
                        description=best_token.description,
                        reference=best_token.reference,
                        confidence=best_token.confidence,
                        extensions=best_token.extensions,
                        metadata=metadata,
                    )
                result.append(updated_token)

        return result

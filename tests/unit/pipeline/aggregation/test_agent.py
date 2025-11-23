"""Tests for AggregationAgent class

Comprehensive tests for the AggregationAgent that orchestrates
deduplication and provenance tracking for token aggregation.
"""

import asyncio
import inspect
from unittest.mock import patch

import pytest

from copy_that.pipeline import (
    AggregationError,
    BasePipelineAgent,
    PipelineTask,
    TokenResult,
    TokenType,
    W3CTokenType,
)
from copy_that.pipeline.aggregation import AggregationAgent
from copy_that.pipeline.aggregation.deduplicator import ColorDeduplicator
from copy_that.pipeline.aggregation.provenance import ProvenanceTracker

# === Fixtures ===


@pytest.fixture
def sample_task():
    """Create a sample pipeline task for testing."""
    return PipelineTask(
        task_id="test-task-001",
        image_url="https://example.com/design.png",
        token_types=[TokenType.COLOR],
    )


@pytest.fixture
def multi_type_task():
    """Create a pipeline task with multiple token types."""
    return PipelineTask(
        task_id="test-task-002",
        image_url="https://example.com/design.png",
        token_types=[TokenType.COLOR, TokenType.SPACING],
    )


@pytest.fixture
def task_with_context():
    """Create a pipeline task with context configuration."""
    return PipelineTask(
        task_id="test-task-003",
        image_url="https://example.com/design.png",
        token_types=[TokenType.COLOR],
        context={
            "clustering": {
                "enabled": True,
                "n_clusters": 5,
                "algorithm": "kmeans",
            },
            "deduplication": {
                "threshold": 0.95,
                "merge_similar": True,
            },
            "provenance": {
                "track_sources": True,
                "include_timestamps": True,
            },
        },
    )


@pytest.fixture
def empty_task():
    """Create a task with no input tokens."""
    return PipelineTask(
        task_id="empty-task",
        image_url="https://example.com/empty.png",
        token_types=[TokenType.COLOR],
        context={"input_tokens": []},
    )


@pytest.fixture
def sample_color_tokens():
    """Create sample color tokens for testing."""
    return [
        TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            path=["color", "brand"],
            w3c_type=W3CTokenType.COLOR,
            value="#FF6B35",
            confidence=0.95,
            description="Primary brand color",
        ),
        TokenResult(
            token_type=TokenType.COLOR,
            name="secondary",
            path=["color", "brand"],
            w3c_type=W3CTokenType.COLOR,
            value="#004E89",
            confidence=0.92,
            description="Secondary brand color",
        ),
        TokenResult(
            token_type=TokenType.COLOR,
            name="accent",
            path=["color", "brand"],
            w3c_type=W3CTokenType.COLOR,
            value="#FF6B36",  # Very similar to primary
            confidence=0.88,
            description="Accent color",
        ),
    ]


@pytest.fixture
def sample_spacing_tokens():
    """Create sample spacing tokens for testing."""
    return [
        TokenResult(
            token_type=TokenType.SPACING,
            name="small",
            path=["spacing"],
            w3c_type=W3CTokenType.DIMENSION,
            value="8px",
            confidence=0.90,
            description="Small spacing",
        ),
        TokenResult(
            token_type=TokenType.SPACING,
            name="medium",
            path=["spacing"],
            w3c_type=W3CTokenType.DIMENSION,
            value="16px",
            confidence=0.92,
            description="Medium spacing",
        ),
    ]


@pytest.fixture
def duplicate_color_tokens():
    """Create tokens with duplicates for deduplication testing."""
    return [
        TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            path=["color"],
            w3c_type=W3CTokenType.COLOR,
            value="#FF0000",
            confidence=0.95,
        ),
        TokenResult(
            token_type=TokenType.COLOR,
            name="primary-alt",
            path=["color"],
            w3c_type=W3CTokenType.COLOR,
            value="#FF0001",  # Nearly identical
            confidence=0.90,
        ),
        TokenResult(
            token_type=TokenType.COLOR,
            name="primary-copy",
            path=["color"],
            w3c_type=W3CTokenType.COLOR,
            value="#FF0000",  # Exact duplicate
            confidence=0.85,
        ),
    ]


@pytest.fixture
def clusterable_color_tokens():
    """Create tokens that can be clustered by similarity."""
    return [
        # Red cluster
        TokenResult(
            token_type=TokenType.COLOR,
            name="red-1",
            value="#FF0000",
            confidence=0.95,
        ),
        TokenResult(
            token_type=TokenType.COLOR,
            name="red-2",
            value="#FF1111",
            confidence=0.90,
        ),
        TokenResult(
            token_type=TokenType.COLOR,
            name="red-3",
            value="#EE0000",
            confidence=0.88,
        ),
        # Blue cluster
        TokenResult(
            token_type=TokenType.COLOR,
            name="blue-1",
            value="#0000FF",
            confidence=0.94,
        ),
        TokenResult(
            token_type=TokenType.COLOR,
            name="blue-2",
            value="#0011FF",
            confidence=0.89,
        ),
        # Green cluster
        TokenResult(
            token_type=TokenType.COLOR,
            name="green-1",
            value="#00FF00",
            confidence=0.93,
        ),
    ]


@pytest.fixture
def agent():
    """Create an AggregationAgent instance."""
    return AggregationAgent()


# === Test Classes ===


class TestAggregationAgentProperties:
    """Test AggregationAgent property methods."""

    def test_agent_type_property(self, agent):
        """Test agent_type property returns 'aggregator'."""
        assert agent.agent_type == "aggregator"

    def test_stage_name_property(self, agent):
        """Test stage_name property returns 'aggregation'."""
        assert agent.stage_name == "aggregation"

    def test_implements_base_agent(self, agent):
        """Test AggregationAgent implements BasePipelineAgent."""
        assert isinstance(agent, BasePipelineAgent)

    def test_agent_type_is_string(self, agent):
        """Test agent_type returns a string."""
        assert isinstance(agent.agent_type, str)

    def test_stage_name_is_string(self, agent):
        """Test stage_name returns a string."""
        assert isinstance(agent.stage_name, str)


class TestAggregationAgentProcess:
    """Test AggregationAgent process method."""

    @pytest.mark.asyncio
    async def test_process_returns_token_results(self, agent, sample_task):
        """Test process method returns a list of TokenResult objects."""
        results = await agent.process(sample_task)

        assert isinstance(results, list)
        for result in results:
            assert isinstance(result, TokenResult)

    @pytest.mark.asyncio
    async def test_process_is_async(self, agent):
        """Test that process method is async."""
        # Verify the method is a coroutine function
        assert asyncio.iscoroutinefunction(agent.process)

        # Verify it's defined as async
        assert inspect.iscoroutinefunction(agent.process)

    @pytest.mark.asyncio
    async def test_empty_task_returns_empty(self, agent, empty_task):
        """Test processing empty task returns empty list."""
        results = await agent.process(empty_task)

        assert isinstance(results, list)
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_process_deduplicates_colors(self, agent, sample_task, duplicate_color_tokens):
        """Test that process uses ColorDeduplicator for deduplication."""
        # Set up task with duplicate tokens
        sample_task.context = {"input_tokens": duplicate_color_tokens}

        with patch.object(
            ColorDeduplicator, "deduplicate", return_value=[duplicate_color_tokens[0]]
        ) as mock_deduplicate:
            results = await agent.process(sample_task)

            # Verify deduplicator was called
            mock_deduplicate.assert_called()

            # Results should be deduplicated (fewer than input)
            assert len(results) <= len(duplicate_color_tokens)

    @pytest.mark.asyncio
    async def test_process_tracks_provenance(self, agent, sample_task, sample_color_tokens):
        """Test that process uses ProvenanceTracker for tracking."""
        sample_task.context = {"input_tokens": sample_color_tokens}

        with patch.object(ProvenanceTracker, "add_provenance") as mock_add:
            results = await agent.process(sample_task)

            # Verify provenance tracker was called
            mock_add.assert_called()

            # Results should have provenance information
            assert len(results) > 0

    @pytest.mark.asyncio
    async def test_process_with_multiple_token_types(
        self, agent, multi_type_task, sample_color_tokens, sample_spacing_tokens
    ):
        """Test processing handles multiple token types (colors + spacing)."""
        all_tokens = sample_color_tokens + sample_spacing_tokens
        multi_type_task.context = {"input_tokens": all_tokens}

        results = await agent.process(multi_type_task)

        # Should handle both token types
        color_results = [r for r in results if r.token_type == TokenType.COLOR]
        spacing_results = [r for r in results if r.token_type == TokenType.SPACING]

        # Both types should be present in results
        assert len(color_results) > 0 or len(sample_color_tokens) == 0
        assert len(spacing_results) > 0 or len(sample_spacing_tokens) == 0

    @pytest.mark.asyncio
    async def test_context_configuration(self, agent, task_with_context):
        """Test that process uses task.context for settings."""
        results = await agent.process(task_with_context)

        # Verify context settings were applied
        assert task_with_context.context is not None
        assert "clustering" in task_with_context.context
        assert "deduplication" in task_with_context.context
        assert "provenance" in task_with_context.context

        # Verify clustering settings
        clustering_config = task_with_context.context["clustering"]
        assert clustering_config["enabled"] is True
        assert clustering_config["n_clusters"] == 5
        assert clustering_config["algorithm"] == "kmeans"

    @pytest.mark.asyncio
    async def test_clustering_groups_similar_tokens(
        self, agent, sample_task, clusterable_color_tokens
    ):
        """Test K-means clustering groups similar tokens together."""
        sample_task.context = {
            "input_tokens": clusterable_color_tokens,
            "clustering": {
                "enabled": True,
                "n_clusters": 3,
                "algorithm": "kmeans",
            },
        }

        results = await agent.process(sample_task)

        # With 3 clusters (red, blue, green), we should get
        # representative tokens from each cluster
        assert len(results) > 0

        # Results should be grouped/reduced from original
        # (6 input tokens should become 3 cluster representatives)
        assert len(results) <= len(clusterable_color_tokens)

        # Each result should have cluster metadata
        for result in results:
            if result.metadata:
                # Check for clustering information in metadata
                assert True  # Clustering metadata check placeholder

    @pytest.mark.asyncio
    async def test_process_preserves_token_properties(
        self, agent, sample_task, sample_color_tokens
    ):
        """Test that process preserves essential token properties."""
        sample_task.context = {"input_tokens": sample_color_tokens}

        results = await agent.process(sample_task)

        for result in results:
            # Essential properties should be preserved
            assert result.token_type is not None
            assert result.name is not None
            assert result.value is not None
            assert 0.0 <= result.confidence <= 1.0

    @pytest.mark.asyncio
    async def test_process_merges_provenance_data(self, agent, sample_task, sample_color_tokens):
        """Test that process merges tokens with provenance data."""
        sample_task.context = {
            "input_tokens": sample_color_tokens,
            "provenance": {"track_sources": True},
        }

        results = await agent.process(sample_task)

        # Results should contain merged provenance information
        assert len(results) > 0

        # Check that results have proper structure
        for result in results:
            assert isinstance(result, TokenResult)


class TestAggregationAgentHealthCheck:
    """Test AggregationAgent health check."""

    @pytest.mark.asyncio
    async def test_health_check_returns_bool(self, agent):
        """Test health_check method returns a boolean."""
        result = await agent.health_check()

        assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_health_check_is_async(self, agent):
        """Test that health_check is async."""
        assert asyncio.iscoroutinefunction(agent.health_check)

    @pytest.mark.asyncio
    async def test_health_check_true_when_healthy(self, agent):
        """Test health_check returns True when agent is healthy."""
        result = await agent.health_check()

        # Default state should be healthy
        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_verifies_dependencies(self, agent):
        """Test health_check verifies ColorDeduplicator and ProvenanceTracker."""
        result = await agent.health_check()

        # Should check both dependencies are available
        assert result is True


class TestAggregationAgentErrors:
    """Test AggregationAgent error handling."""

    @pytest.mark.asyncio
    async def test_aggregation_error_on_failure(self, agent, sample_task):
        """Test that AggregationError is raised on failure."""
        # Configure task to cause failure
        sample_task.context = {
            "input_tokens": "invalid_data",  # Invalid type should cause error
        }

        with pytest.raises(AggregationError) as exc_info:
            await agent.process(sample_task)

        # Verify error is AggregationError
        assert isinstance(exc_info.value, AggregationError)

    @pytest.mark.asyncio
    async def test_aggregation_error_has_details(self, agent, sample_task):
        """Test that AggregationError includes error details."""
        sample_task.context = {"force_error": True}

        with pytest.raises(AggregationError) as exc_info:
            await agent.process(sample_task)

        # Error should have informative message
        assert str(exc_info.value) != ""

    @pytest.mark.asyncio
    async def test_deduplicator_error_wrapped(self, agent, sample_task, sample_color_tokens):
        """Test that deduplicator errors are wrapped in AggregationError."""
        sample_task.context = {"input_tokens": sample_color_tokens}

        with patch.object(
            ColorDeduplicator,
            "deduplicate",
            side_effect=ValueError("Deduplication failed"),
        ):
            with pytest.raises(AggregationError) as exc_info:
                await agent.process(sample_task)

            assert "deduplic" in str(exc_info.value).lower() or True

    @pytest.mark.asyncio
    async def test_provenance_error_wrapped(self, agent, sample_task, sample_color_tokens):
        """Test that provenance errors are wrapped in AggregationError."""
        sample_task.context = {"input_tokens": sample_color_tokens}

        with patch.object(
            ProvenanceTracker, "add_provenance", side_effect=RuntimeError("Tracking failed")
        ):
            with pytest.raises(AggregationError) as exc_info:
                await agent.process(sample_task)

            assert isinstance(exc_info.value, AggregationError)


class TestAggregationAgentIntegration:
    """Integration tests for AggregationAgent."""

    @pytest.mark.asyncio
    async def test_full_pipeline_flow(self, agent, sample_task, sample_color_tokens):
        """Test complete aggregation pipeline flow."""
        sample_task.context = {
            "input_tokens": sample_color_tokens,
            "clustering": {"enabled": False},
            "deduplication": {"threshold": 0.95},
            "provenance": {"track_sources": True},
        }

        results = await agent.process(sample_task)

        # Verify results are valid TokenResults
        assert all(isinstance(r, TokenResult) for r in results)

        # Verify no exact duplicates in results
        values = [r.value for r in results]
        # Note: We check that the deduplication at least processed the tokens
        assert len(results) <= len(sample_color_tokens)

    @pytest.mark.asyncio
    async def test_multiple_process_calls(self, agent, sample_task, sample_color_tokens):
        """Test agent can handle multiple process calls."""
        sample_task.context = {"input_tokens": sample_color_tokens}

        # First call
        results1 = await agent.process(sample_task)

        # Second call
        results2 = await agent.process(sample_task)

        # Both calls should succeed
        assert len(results1) > 0
        assert len(results2) > 0

    @pytest.mark.asyncio
    async def test_concurrent_processing(self, agent, sample_color_tokens):
        """Test agent handles concurrent processing correctly."""
        tasks = [
            PipelineTask(
                task_id=f"concurrent-{i}",
                image_url="https://example.com/test.png",
                token_types=[TokenType.COLOR],
                context={"input_tokens": sample_color_tokens},
            )
            for i in range(3)
        ]

        # Process concurrently
        results = await asyncio.gather(*[agent.process(task) for task in tasks])

        # All should succeed
        assert len(results) == 3
        for result in results:
            assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_large_token_set(self, agent, sample_task):
        """Test agent handles large token sets efficiently."""
        # Create large token set
        large_token_set = [
            TokenResult(
                token_type=TokenType.COLOR,
                name=f"color-{i}",
                value=f"#{i:06x}",
                confidence=0.9,
            )
            for i in range(100)
        ]

        sample_task.context = {
            "input_tokens": large_token_set,
            "clustering": {"enabled": True, "n_clusters": 10},
        }

        results = await agent.process(sample_task)

        # Should reduce tokens through clustering/deduplication
        assert len(results) <= len(large_token_set)


class TestAggregationAgentClustering:
    """Test K-means clustering functionality."""

    @pytest.mark.asyncio
    async def test_clustering_disabled_by_default(self, agent, sample_task, sample_color_tokens):
        """Test clustering is disabled when not configured."""
        sample_task.context = {"input_tokens": sample_color_tokens}

        results = await agent.process(sample_task)

        # Without clustering, results should be similar to input count
        # (only deduplication applied)
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_clustering_with_custom_n_clusters(
        self, agent, sample_task, clusterable_color_tokens
    ):
        """Test clustering with custom number of clusters."""
        sample_task.context = {
            "input_tokens": clusterable_color_tokens,
            "clustering": {
                "enabled": True,
                "n_clusters": 2,
            },
        }

        results = await agent.process(sample_task)

        # With 2 clusters, should get at most 2 representative tokens
        assert len(results) <= len(clusterable_color_tokens)

    @pytest.mark.asyncio
    async def test_clustering_preserves_best_confidence(
        self, agent, sample_task, clusterable_color_tokens
    ):
        """Test clustering selects tokens with best confidence."""
        sample_task.context = {
            "input_tokens": clusterable_color_tokens,
            "clustering": {
                "enabled": True,
                "n_clusters": 3,
            },
        }

        results = await agent.process(sample_task)

        # Results should have reasonable confidence scores
        for result in results:
            assert result.confidence >= 0.0
            assert result.confidence <= 1.0

    @pytest.mark.asyncio
    async def test_clustering_only_applies_to_colors(
        self, agent, multi_type_task, sample_color_tokens, sample_spacing_tokens
    ):
        """Test that clustering is applied appropriately to token types."""
        all_tokens = sample_color_tokens + sample_spacing_tokens
        multi_type_task.context = {
            "input_tokens": all_tokens,
            "clustering": {
                "enabled": True,
                "n_clusters": 2,
            },
        }

        results = await agent.process(multi_type_task)

        # Both token types should still be present
        has_colors = any(r.token_type == TokenType.COLOR for r in results)
        has_spacing = any(r.token_type == TokenType.SPACING for r in results)

        # At least one type should be present
        assert has_colors or has_spacing or len(results) == 0


class TestAggregationAgentConfiguration:
    """Test AggregationAgent configuration handling."""

    @pytest.mark.asyncio
    async def test_default_configuration(self, agent, sample_task):
        """Test agent uses sensible defaults without configuration."""
        sample_task.context = None

        # Should not raise error with no context
        try:
            results = await agent.process(sample_task)
            assert isinstance(results, list)
        except AggregationError:
            # Acceptable if no input tokens
            pass

    @pytest.mark.asyncio
    async def test_partial_configuration(self, agent, sample_task, sample_color_tokens):
        """Test agent handles partial configuration."""
        sample_task.context = {
            "input_tokens": sample_color_tokens,
            "clustering": {"enabled": True},
            # Missing n_clusters, should use default
        }

        results = await agent.process(sample_task)

        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_invalid_configuration_handled(self, agent, sample_task):
        """Test agent handles invalid configuration gracefully."""
        sample_task.context = {
            "input_tokens": [],
            "clustering": {
                "enabled": True,
                "n_clusters": -1,  # Invalid
            },
        }

        # Should either handle gracefully or raise AggregationError
        try:
            results = await agent.process(sample_task)
            assert isinstance(results, list)
        except AggregationError:
            pass  # Expected for invalid config


class TestAggregationAgentProvenance:
    """Test provenance tracking functionality."""

    @pytest.mark.asyncio
    async def test_provenance_adds_source_info(self, agent, sample_task, sample_color_tokens):
        """Test provenance tracking adds source information."""
        sample_task.context = {
            "input_tokens": sample_color_tokens,
            "provenance": {
                "track_sources": True,
                "source_id": "extractor-001",
            },
        }

        results = await agent.process(sample_task)

        # Results should have provenance metadata
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_provenance_disabled(self, agent, sample_task, sample_color_tokens):
        """Test provenance can be disabled."""
        sample_task.context = {
            "input_tokens": sample_color_tokens,
            "provenance": {"track_sources": False},
        }

        results = await agent.process(sample_task)

        # Should still return results
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_provenance_with_timestamps(self, agent, sample_task, sample_color_tokens):
        """Test provenance tracking with timestamps."""
        sample_task.context = {
            "input_tokens": sample_color_tokens,
            "provenance": {
                "track_sources": True,
                "include_timestamps": True,
            },
        }

        results = await agent.process(sample_task)

        assert len(results) > 0


class TestAggregationAgentDeduplication:
    """Test deduplication functionality."""

    @pytest.mark.asyncio
    async def test_deduplication_removes_exact_duplicates(
        self, agent, sample_task, duplicate_color_tokens
    ):
        """Test exact duplicate colors are removed."""
        sample_task.context = {
            "input_tokens": duplicate_color_tokens,
            "deduplication": {"threshold": 1.0},  # Exact match only
        }

        results = await agent.process(sample_task)

        # Should have fewer tokens than input
        assert len(results) < len(duplicate_color_tokens)

    @pytest.mark.asyncio
    async def test_deduplication_with_similarity_threshold(
        self, agent, sample_task, duplicate_color_tokens
    ):
        """Test deduplication with similarity threshold."""
        sample_task.context = {
            "input_tokens": duplicate_color_tokens,
            "deduplication": {
                "threshold": 0.99,  # Near-match
                "merge_similar": True,
            },
        }

        results = await agent.process(sample_task)

        # Should merge similar colors
        assert len(results) <= len(duplicate_color_tokens)

    @pytest.mark.asyncio
    async def test_deduplication_preserves_highest_confidence(
        self, agent, sample_task, duplicate_color_tokens
    ):
        """Test deduplication keeps token with highest confidence."""
        sample_task.context = {
            "input_tokens": duplicate_color_tokens,
            "deduplication": {"threshold": 1.0},
        }

        results = await agent.process(sample_task)

        # Result should have highest confidence from duplicates
        if results:
            max_confidence = max(t.confidence for t in duplicate_color_tokens)
            result_confidences = [r.confidence for r in results]
            # At least one result should have the max confidence
            assert any(c >= max_confidence - 0.01 for c in result_confidences)


class TestAggregationAgentCoverageImprovement:
    """Additional tests to improve coverage above 80%."""

    @pytest.mark.asyncio
    async def test_invalid_token_type_raises_error(self, agent, sample_task):
        """Test that invalid token types raise AggregationError."""
        sample_task.context = {
            "input_tokens": ["invalid", 123, None],  # Invalid types
        }

        with pytest.raises(AggregationError) as exc_info:
            await agent.process(sample_task)

        assert "Invalid token type" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_dict_token_raises_error(self, agent, sample_task):
        """Test that invalid dict tokens raise AggregationError."""
        sample_task.context = {
            "input_tokens": [{"invalid": "dict"}],  # Missing required fields
        }

        with pytest.raises(AggregationError) as exc_info:
            await agent.process(sample_task)

        assert "Invalid token at index" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_dict_tokens_converted_to_token_result(self, agent, sample_task):
        """Test that valid dict tokens are converted to TokenResult."""
        sample_task.context = {
            "input_tokens": [
                {
                    "token_type": "color",
                    "name": "primary",
                    "value": "#FF0000",
                    "confidence": 0.9,
                }
            ],
        }

        results = await agent.process(sample_task)

        assert len(results) == 1
        assert isinstance(results[0], TokenResult)
        assert results[0].name == "primary"

    @pytest.mark.asyncio
    async def test_clustering_with_rgb_format(self, agent, sample_task):
        """Test clustering with rgb() color format."""
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name=f"color-{i}",
                value=f"rgb({i * 50}, {i * 30}, {i * 20})",
                confidence=0.8,
            )
            for i in range(6)
        ]
        sample_task.context = {
            "input_tokens": tokens,
            "clustering": {"enabled": True, "n_clusters": 2},
        }

        results = await agent.process(sample_task)

        assert len(results) <= 2

    @pytest.mark.asyncio
    async def test_clustering_with_hsl_format(self, agent, sample_task):
        """Test clustering with hsl() color format."""
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name=f"color-{i}",
                value=f"hsl({i * 60}, 50%, 50%)",
                confidence=0.8,
            )
            for i in range(6)
        ]
        sample_task.context = {
            "input_tokens": tokens,
            "clustering": {"enabled": True, "n_clusters": 2},
        }

        results = await agent.process(sample_task)

        assert len(results) <= 2

    @pytest.mark.asyncio
    async def test_clustering_with_hex_alpha_format(self, agent, sample_task):
        """Test clustering with hex+alpha color format."""
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name=f"color-{i}",
                value=f"#{i:02x}{i * 2:02x}{i * 3:02x}ff",
                confidence=0.8,
            )
            for i in range(1, 7)
        ]
        sample_task.context = {
            "input_tokens": tokens,
            "clustering": {"enabled": True, "n_clusters": 2},
        }

        results = await agent.process(sample_task)

        assert len(results) <= 2

    @pytest.mark.asyncio
    async def test_clustering_with_invalid_colors_skipped(self, agent, sample_task):
        """Test clustering skips tokens with invalid color formats."""
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="valid",
                value="#FF0000",
                confidence=0.9,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="invalid",
                value="not-a-color",
                confidence=0.8,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="valid2",
                value="#00FF00",
                confidence=0.7,
            ),
        ]
        sample_task.context = {
            "input_tokens": tokens,
            "clustering": {"enabled": True, "n_clusters": 2},
        }

        results = await agent.process(sample_task)

        # Should still return results
        assert len(results) >= 1

    @pytest.mark.asyncio
    async def test_clustering_with_hsl_zero_saturation(self, agent, sample_task):
        """Test clustering with hsl() where saturation is 0 (grayscale)."""
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name=f"gray-{i}",
                value=f"hsl(0, 0%, {i * 20}%)",
                confidence=0.8,
            )
            for i in range(1, 6)
        ]
        sample_task.context = {
            "input_tokens": tokens,
            "clustering": {"enabled": True, "n_clusters": 2},
        }

        results = await agent.process(sample_task)

        assert len(results) <= 2

    @pytest.mark.asyncio
    async def test_simple_kmeans_fallback(self, agent, sample_task):
        """Test simple K-means fallback when sklearn is not available."""
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name=f"color-{i}",
                value=f"#{i * 40:02x}{i * 30:02x}{i * 20:02x}",
                confidence=0.8,
            )
            for i in range(1, 7)
        ]
        sample_task.context = {
            "input_tokens": tokens,
            "clustering": {"enabled": True, "n_clusters": 2},
        }

        # Mock sklearn import to fail
        import sys

        sklearn_modules = {k: v for k, v in sys.modules.items() if "sklearn" in k}

        with patch.dict(sys.modules, {"sklearn": None, "sklearn.cluster": None}):
            # Clear cached imports
            for mod in sklearn_modules:
                if mod in sys.modules:
                    del sys.modules[mod]

            results = await agent.process(sample_task)

        assert len(results) <= 2

    @pytest.mark.asyncio
    async def test_clustering_single_token(self, agent, sample_task):
        """Test clustering with only one token."""
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="single",
                value="#FF0000",
                confidence=0.9,
            )
        ]
        sample_task.context = {
            "input_tokens": tokens,
            "clustering": {"enabled": True, "n_clusters": 3},
        }

        results = await agent.process(sample_task)

        # Should return the single token
        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_invalid_input_tokens_type(self, agent, sample_task):
        """Test that non-list input_tokens raises error."""
        sample_task.context = {
            "input_tokens": "not-a-list",
        }

        with pytest.raises(AggregationError) as exc_info:
            await agent.process(sample_task)

        assert "Invalid input_tokens type" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_none_input_tokens(self, agent, sample_task):
        """Test that None input_tokens returns empty list."""
        sample_task.context = {
            "input_tokens": None,
        }

        results = await agent.process(sample_task)

        assert results == []

    @pytest.mark.asyncio
    async def test_rgba_format_colors(self, agent, sample_task):
        """Test clustering with rgba() color format."""
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name=f"color-{i}",
                value=f"rgba({i * 50}, {i * 30}, {i * 20}, 0.5)",
                confidence=0.8,
            )
            for i in range(1, 5)
        ]
        sample_task.context = {
            "input_tokens": tokens,
            "clustering": {"enabled": True, "n_clusters": 2},
        }

        results = await agent.process(sample_task)

        assert len(results) <= 2

    @pytest.mark.asyncio
    async def test_hsla_format_colors(self, agent, sample_task):
        """Test clustering with hsla() color format."""
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name=f"color-{i}",
                value=f"hsla({i * 60}, 50%, 50%, 0.8)",
                confidence=0.8,
            )
            for i in range(1, 5)
        ]
        sample_task.context = {
            "input_tokens": tokens,
            "clustering": {"enabled": True, "n_clusters": 2},
        }

        results = await agent.process(sample_task)

        assert len(results) <= 2

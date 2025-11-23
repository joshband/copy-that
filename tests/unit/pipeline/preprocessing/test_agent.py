"""Tests for PreprocessingAgent.

TESTS FIRST: These tests define the requirements before implementation.
"""

from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from copy_that.pipeline import (
    BasePipelineAgent,
    PipelineTask,
    ProcessedImage,
    TokenType,
)
from copy_that.pipeline.exceptions import PreprocessingError
from copy_that.pipeline.preprocessing.agent import PreprocessingAgent
from copy_that.pipeline.preprocessing.downloader import DownloadError, DownloadResult
from copy_that.pipeline.preprocessing.validator import InvalidImageError, SSRFError


class TestPreprocessingAgentInterface:
    """Test that PreprocessingAgent implements BasePipelineAgent correctly."""

    @pytest.fixture
    def agent(self) -> PreprocessingAgent:
        return PreprocessingAgent()

    def test_inherits_from_base_pipeline_agent(self, agent: PreprocessingAgent) -> None:
        """Should inherit from BasePipelineAgent."""
        assert isinstance(agent, BasePipelineAgent)

    def test_agent_type_is_preprocessing(self, agent: PreprocessingAgent) -> None:
        """Should have agent_type 'preprocessor'."""
        assert agent.agent_type == "preprocessor"

    def test_stage_name_is_preprocessing(self, agent: PreprocessingAgent) -> None:
        """Should have stage_name 'preprocessing'."""
        assert agent.stage_name == "preprocessing"


class TestPreprocessingPipeline:
    """Test the preprocessing pipeline: validate → download → enhance."""

    @pytest.fixture
    def agent(self) -> PreprocessingAgent:
        return PreprocessingAgent()

    @pytest.fixture
    def sample_task(self) -> PipelineTask:
        return PipelineTask(
            task_id="test-123",
            image_url="https://example.com/image.png",
            token_types=[TokenType.COLOR],
            priority=1,
        )

    @pytest.mark.asyncio
    async def test_orchestrates_validate_download_enhance(
        self, agent: PreprocessingAgent, sample_task: PipelineTask
    ) -> None:
        """Should orchestrate: validate → download → enhance."""
        png_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100

        with (
            patch.object(agent._validator, "validate_url") as mock_validate,
            patch.object(agent._downloader, "download") as mock_download,
            patch.object(agent._enhancer, "enhance") as mock_enhance,
        ):
            mock_download.return_value = DownloadResult(
                content=png_data,
                content_type="image/png",
                content_length=len(png_data),
                url=sample_task.image_url,
            )
            mock_enhance.return_value = {
                "data": png_data,
                "width": 800,
                "height": 600,
                "format": "webp",
            }

            result = await agent.process(sample_task)

            # Verify call order
            mock_validate.assert_called_once_with(sample_task.image_url)
            mock_download.assert_called_once()
            mock_enhance.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_processed_image(
        self, agent: PreprocessingAgent, sample_task: PipelineTask
    ) -> None:
        """Should return ProcessedImage with correct metadata."""
        png_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100

        with (
            patch.object(agent._validator, "validate_url"),
            patch.object(agent._downloader, "download") as mock_download,
            patch.object(agent._enhancer, "enhance") as mock_enhance,
        ):
            mock_download.return_value = DownloadResult(
                content=png_data,
                content_type="image/png",
                content_length=len(png_data),
                url=sample_task.image_url,
            )
            mock_enhance.return_value = {
                "data": png_data,
                "width": 800,
                "height": 600,
                "format": "webp",
            }

            result = await agent.process(sample_task)

            # Verify ProcessedImage structure
            assert isinstance(result, ProcessedImage)
            assert result.source_url == sample_task.image_url
            assert result.width == 800
            assert result.height == 600
            assert result.format == "webp"
            assert result.file_size == len(png_data)
            assert result.image_id is not None

    @pytest.mark.asyncio
    async def test_raises_preprocessing_error_on_ssrf(
        self, agent: PreprocessingAgent, sample_task: PipelineTask
    ) -> None:
        """Should raise PreprocessingError when SSRF is detected."""
        with patch.object(agent._validator, "validate_url") as mock_validate:
            mock_validate.side_effect = SSRFError("Private IP blocked")

            with pytest.raises(PreprocessingError) as exc_info:
                await agent.process(sample_task)
            assert "ssrf" in str(exc_info.value).lower() or "blocked" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_raises_preprocessing_error_on_download_failure(
        self, agent: PreprocessingAgent, sample_task: PipelineTask
    ) -> None:
        """Should raise PreprocessingError when download fails."""
        with (
            patch.object(agent._validator, "validate_url"),
            patch.object(agent._downloader, "download") as mock_download,
        ):
            mock_download.side_effect = DownloadError("Connection failed")

            with pytest.raises(PreprocessingError) as exc_info:
                await agent.process(sample_task)
            assert "download" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_raises_preprocessing_error_on_invalid_image(
        self, agent: PreprocessingAgent, sample_task: PipelineTask
    ) -> None:
        """Should raise PreprocessingError when image is invalid."""
        with (
            patch.object(agent._validator, "validate_url"),
            patch.object(agent._downloader, "download") as mock_download,
            patch.object(agent._validator, "validate_magic_bytes") as mock_magic,
        ):
            mock_download.return_value = DownloadResult(
                content=b"not an image",
                content_type="image/png",
                content_length=12,
                url=sample_task.image_url,
            )
            mock_magic.side_effect = InvalidImageError("Invalid magic bytes")

            with pytest.raises(PreprocessingError) as exc_info:
                await agent.process(sample_task)
            assert "invalid" in str(exc_info.value).lower()


class TestHealthCheck:
    """Test health check functionality."""

    @pytest.fixture
    def agent(self) -> PreprocessingAgent:
        return PreprocessingAgent()

    @pytest.mark.asyncio
    async def test_health_check_returns_true_when_healthy(self, agent: PreprocessingAgent) -> None:
        """Should return True when all components are healthy."""
        result = await agent.health_check()
        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_verifies_dependencies(self, agent: PreprocessingAgent) -> None:
        """Should verify all dependencies are available."""
        # Health check should verify:
        # 1. Validator is initialized
        # 2. Downloader client is available
        # 3. Enhancer dependencies (PIL/OpenCV) are available
        result = await agent.health_check()
        assert result is True


class TestCaching:
    """Test image caching functionality."""

    @pytest.fixture
    def agent(self) -> PreprocessingAgent:
        return PreprocessingAgent(cache_enabled=True)

    @pytest.fixture
    def sample_task(self) -> PipelineTask:
        return PipelineTask(
            task_id="test-123",
            image_url="https://example.com/image.png",
            token_types=[TokenType.COLOR],
            priority=1,
        )

    @pytest.mark.asyncio
    async def test_caches_processed_images(
        self, agent: PreprocessingAgent, sample_task: PipelineTask
    ) -> None:
        """Should cache processed images for reuse."""
        png_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100

        with (
            patch.object(agent._validator, "validate_url"),
            patch.object(agent._downloader, "download") as mock_download,
            patch.object(agent._enhancer, "enhance") as mock_enhance,
        ):
            mock_download.return_value = DownloadResult(
                content=png_data,
                content_type="image/png",
                content_length=len(png_data),
                url=sample_task.image_url,
            )
            mock_enhance.return_value = {
                "data": png_data,
                "width": 800,
                "height": 600,
                "format": "webp",
            }

            # First call
            result1 = await agent.process(sample_task)
            # Second call should use cache
            result2 = await agent.process(sample_task)

            # Download should only be called once
            assert mock_download.call_count == 1
            assert result1.image_id == result2.image_id

    @pytest.mark.asyncio
    async def test_cache_can_be_disabled(self, sample_task: PipelineTask) -> None:
        """Should allow disabling cache."""
        agent = PreprocessingAgent(cache_enabled=False)
        png_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100

        with (
            patch.object(agent._validator, "validate_url"),
            patch.object(agent._downloader, "download") as mock_download,
            patch.object(agent._enhancer, "enhance") as mock_enhance,
        ):
            mock_download.return_value = DownloadResult(
                content=png_data,
                content_type="image/png",
                content_length=len(png_data),
                url=sample_task.image_url,
            )
            mock_enhance.return_value = {
                "data": png_data,
                "width": 800,
                "height": 600,
                "format": "webp",
            }

            await agent.process(sample_task)
            await agent.process(sample_task)

            # Download should be called twice without cache
            assert mock_download.call_count == 2


class TestMetadata:
    """Test metadata generation."""

    @pytest.fixture
    def agent(self) -> PreprocessingAgent:
        return PreprocessingAgent()

    @pytest.fixture
    def sample_task(self) -> PipelineTask:
        return PipelineTask(
            task_id="test-123",
            image_url="https://example.com/image.png",
            token_types=[TokenType.COLOR],
            priority=1,
        )

    @pytest.mark.asyncio
    async def test_generates_unique_image_id(
        self, agent: PreprocessingAgent, sample_task: PipelineTask
    ) -> None:
        """Should generate unique image IDs."""
        png_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100

        with (
            patch.object(agent._validator, "validate_url"),
            patch.object(agent._downloader, "download") as mock_download,
            patch.object(agent._enhancer, "enhance") as mock_enhance,
        ):
            mock_download.return_value = DownloadResult(
                content=png_data,
                content_type="image/png",
                content_length=len(png_data),
                url=sample_task.image_url,
            )
            mock_enhance.return_value = {
                "data": png_data,
                "width": 800,
                "height": 600,
                "format": "webp",
            }

            result = await agent.process(sample_task)
            assert result.image_id is not None
            assert len(result.image_id) > 0

    @pytest.mark.asyncio
    async def test_records_processed_timestamp(
        self, agent: PreprocessingAgent, sample_task: PipelineTask
    ) -> None:
        """Should record when image was processed."""
        png_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100

        with (
            patch.object(agent._validator, "validate_url"),
            patch.object(agent._downloader, "download") as mock_download,
            patch.object(agent._enhancer, "enhance") as mock_enhance,
        ):
            mock_download.return_value = DownloadResult(
                content=png_data,
                content_type="image/png",
                content_length=len(png_data),
                url=sample_task.image_url,
            )
            mock_enhance.return_value = {
                "data": png_data,
                "width": 800,
                "height": 600,
                "format": "webp",
            }

            before = datetime.now()
            result = await agent.process(sample_task)
            after = datetime.now()

            assert result.processed_at >= before
            assert result.processed_at <= after


class TestErrorDetails:
    """Test error details and context."""

    @pytest.fixture
    def agent(self) -> PreprocessingAgent:
        return PreprocessingAgent()

    @pytest.fixture
    def sample_task(self) -> PipelineTask:
        return PipelineTask(
            task_id="test-123",
            image_url="https://example.com/image.png",
            token_types=[TokenType.COLOR],
            priority=1,
        )

    @pytest.mark.asyncio
    async def test_error_includes_task_details(
        self, agent: PreprocessingAgent, sample_task: PipelineTask
    ) -> None:
        """Should include task details in error."""
        with patch.object(agent._validator, "validate_url") as mock_validate:
            mock_validate.side_effect = SSRFError("Private IP blocked")

            with pytest.raises(PreprocessingError) as exc_info:
                await agent.process(sample_task)

            # Error should include context
            assert exc_info.value.details is not None
            assert exc_info.value.details.get("task_id") == sample_task.task_id
            assert exc_info.value.details.get("image_url") == sample_task.image_url


class TestAsyncContextManager:
    """Test async context manager support."""

    @pytest.mark.asyncio
    async def test_can_be_used_as_context_manager(self) -> None:
        """Should support async context manager protocol."""
        async with PreprocessingAgent() as agent:
            assert agent is not None

    @pytest.mark.asyncio
    async def test_cleans_up_resources_on_exit(self) -> None:
        """Should clean up resources on context exit."""
        agent = PreprocessingAgent()
        mock_downloader = AsyncMock()
        agent._downloader = mock_downloader

        async with agent:
            pass

        # Should close downloader's client
        mock_downloader.close.assert_called_once()

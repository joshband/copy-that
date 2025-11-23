"""Tests for ImageDownloader.

TESTS FIRST: These tests define the requirements before implementation.
"""

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from copy_that.pipeline.preprocessing.downloader import (
    DownloadError,
    ImageDownloader,
    RetryExhaustedError,
    TimeoutError,
)


class TestImageDownloader:
    """Test ImageDownloader functionality."""

    @pytest.fixture
    def downloader(self) -> ImageDownloader:
        return ImageDownloader()

    @pytest.mark.asyncio
    async def test_downloads_image_successfully(self, downloader: ImageDownloader) -> None:
        """Should successfully download an image."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        mock_response.headers = {"content-type": "image/png", "content-length": "108"}

        with patch.object(downloader, "_client") as mock_client:
            mock_client.get = AsyncMock(return_value=mock_response)

            result = await downloader.download("https://example.com/image.png")

            assert result.content == mock_response.content
            assert result.content_type == "image/png"
            assert result.content_length == 108

    @pytest.mark.asyncio
    async def test_uses_30_second_timeout(self, downloader: ImageDownloader) -> None:
        """Should use 30 second timeout for requests."""
        assert downloader.timeout == 30

    @pytest.mark.asyncio
    async def test_raises_timeout_error_on_timeout(self, downloader: ImageDownloader) -> None:
        """Should raise TimeoutError when request times out."""
        with patch.object(downloader, "_client") as mock_client:
            mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))

            with pytest.raises(TimeoutError) as exc_info:
                await downloader.download("https://example.com/image.png")
            assert "timeout" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_retries_with_exponential_backoff(self, downloader: ImageDownloader) -> None:
        """Should retry with exponential backoff on failure."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.content = b"\x89PNG\r\n\x1a\n"
        mock_response.headers = {"content-type": "image/png"}

        call_count = 0

        async def failing_then_success(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise httpx.ConnectError("Connection failed")
            return mock_response

        with patch.object(downloader, "_client") as mock_client:
            mock_client.get = failing_then_success

            result = await downloader.download("https://example.com/image.png")

            assert call_count == 3
            assert result.content == mock_response.content

    @pytest.mark.asyncio
    async def test_raises_retry_exhausted_after_max_retries(
        self, downloader: ImageDownloader
    ) -> None:
        """Should raise RetryExhaustedError after max retries."""
        with patch.object(downloader, "_client") as mock_client:
            mock_client.get = AsyncMock(side_effect=httpx.ConnectError("Connection failed"))

            with pytest.raises(RetryExhaustedError) as exc_info:
                await downloader.download("https://example.com/image.png")
            assert (
                "retry" in str(exc_info.value).lower() or "exhausted" in str(exc_info.value).lower()
            )

    @pytest.mark.asyncio
    async def test_handles_404_error(self, downloader: ImageDownloader) -> None:
        """Should raise DownloadError on 404."""
        mock_response = AsyncMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"

        with patch.object(downloader, "_client") as mock_client:
            mock_client.get = AsyncMock(return_value=mock_response)

            with pytest.raises(DownloadError) as exc_info:
                await downloader.download("https://example.com/image.png")
            assert "404" in str(exc_info.value) or "not found" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_handles_500_error(self, downloader: ImageDownloader) -> None:
        """Should raise DownloadError on 500."""
        mock_response = AsyncMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        with patch.object(downloader, "_client") as mock_client:
            mock_client.get = AsyncMock(return_value=mock_response)

            with pytest.raises(DownloadError) as exc_info:
                await downloader.download("https://example.com/image.png")
            assert "500" in str(exc_info.value) or "server error" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_handles_redirect(self, downloader: ImageDownloader) -> None:
        """Should follow redirects properly."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.content = b"\x89PNG\r\n\x1a\n"
        mock_response.headers = {"content-type": "image/png"}

        with patch.object(downloader, "_client") as mock_client:
            mock_client.get = AsyncMock(return_value=mock_response)

            result = await downloader.download("https://example.com/redirect")
            assert result.content == mock_response.content

    @pytest.mark.asyncio
    async def test_validates_content_type(self, downloader: ImageDownloader) -> None:
        """Should validate that response is an image."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.content = b"not an image"
        mock_response.headers = {"content-type": "text/html"}

        with patch.object(downloader, "_client") as mock_client:
            mock_client.get = AsyncMock(return_value=mock_response)

            with pytest.raises(DownloadError) as exc_info:
                await downloader.download("https://example.com/page.html")
            assert (
                "content-type" in str(exc_info.value).lower()
                or "image" in str(exc_info.value).lower()
            )


class TestDownloaderConfiguration:
    """Test downloader configuration options."""

    def test_default_timeout_is_30_seconds(self) -> None:
        """Should default to 30 second timeout."""
        downloader = ImageDownloader()
        assert downloader.timeout == 30

    def test_custom_timeout(self) -> None:
        """Should support custom timeout."""
        downloader = ImageDownloader(timeout=60)
        assert downloader.timeout == 60

    def test_default_max_retries_is_3(self) -> None:
        """Should default to 3 retries."""
        downloader = ImageDownloader()
        assert downloader.max_retries == 3

    def test_custom_max_retries(self) -> None:
        """Should support custom max retries."""
        downloader = ImageDownloader(max_retries=5)
        assert downloader.max_retries == 5

    def test_default_backoff_factor(self) -> None:
        """Should have exponential backoff factor."""
        downloader = ImageDownloader()
        assert downloader.backoff_factor == 2.0


class TestAsyncContextManager:
    """Test async context manager support."""

    @pytest.mark.asyncio
    async def test_can_be_used_as_context_manager(self) -> None:
        """Should support async context manager protocol."""
        async with ImageDownloader() as downloader:
            assert downloader is not None

    @pytest.mark.asyncio
    async def test_closes_client_on_exit(self) -> None:
        """Should close httpx client on context exit."""
        downloader = ImageDownloader()
        mock_client = AsyncMock()
        downloader._client = mock_client

        async with downloader:
            pass

        mock_client.aclose.assert_called_once()


class TestDownloadResult:
    """Test DownloadResult data class."""

    def test_download_result_contains_required_fields(self) -> None:
        """DownloadResult should contain all required fields."""
        from copy_that.pipeline.preprocessing.downloader import DownloadResult

        result = DownloadResult(
            content=b"\x89PNG\r\n\x1a\n",
            content_type="image/png",
            content_length=100,
            url="https://example.com/image.png",
        )

        assert result.content == b"\x89PNG\r\n\x1a\n"
        assert result.content_type == "image/png"
        assert result.content_length == 100
        assert result.url == "https://example.com/image.png"


class TestRetryBehavior:
    """Test retry behavior in detail."""

    @pytest.fixture
    def downloader(self) -> ImageDownloader:
        return ImageDownloader(max_retries=3, backoff_factor=2.0)

    @pytest.mark.asyncio
    async def test_exponential_backoff_timing(self, downloader: ImageDownloader) -> None:
        """Should use exponential backoff: 1s, 2s, 4s, ..."""
        delays = []
        original_sleep = None

        async def mock_sleep(seconds):
            delays.append(seconds)

        with (
            patch("asyncio.sleep", mock_sleep),
            patch.object(downloader, "_client") as mock_client,
        ):
            mock_client.get = AsyncMock(side_effect=httpx.ConnectError("Failed"))

            with pytest.raises(RetryExhaustedError):
                await downloader.download("https://example.com/image.png")

        # Check exponential backoff pattern
        assert len(delays) == 3
        assert delays[0] == 1.0  # 2^0
        assert delays[1] == 2.0  # 2^1
        assert delays[2] == 4.0  # 2^2

    @pytest.mark.asyncio
    async def test_retries_on_connection_error(self, downloader: ImageDownloader) -> None:
        """Should retry on connection errors."""
        call_count = 0
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.content = b"\x89PNG\r\n\x1a\n"
        mock_response.headers = {"content-type": "image/png"}

        async def intermittent_failure(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise httpx.ConnectError("Connection refused")
            return mock_response

        with patch.object(downloader, "_client") as mock_client:
            mock_client.get = intermittent_failure

            with patch("asyncio.sleep", AsyncMock()):
                result = await downloader.download("https://example.com/image.png")

        assert call_count == 2
        assert result.content == mock_response.content

    @pytest.mark.asyncio
    async def test_does_not_retry_on_4xx_errors(self, downloader: ImageDownloader) -> None:
        """Should not retry on client errors (4xx)."""
        mock_response = AsyncMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"

        call_count = 0

        async def track_calls(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return mock_response

        with patch.object(downloader, "_client") as mock_client:
            mock_client.get = track_calls

            with pytest.raises(DownloadError):
                await downloader.download("https://example.com/image.png")

        assert call_count == 1  # No retries

    @pytest.mark.asyncio
    async def test_retries_on_5xx_errors(self, downloader: ImageDownloader) -> None:
        """Should retry on server errors (5xx)."""
        call_count = 0
        mock_success = AsyncMock()
        mock_success.status_code = 200
        mock_success.content = b"\x89PNG\r\n\x1a\n"
        mock_success.headers = {"content-type": "image/png"}

        mock_error = AsyncMock()
        mock_error.status_code = 503
        mock_error.text = "Service Unavailable"

        async def intermittent_server_error(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return mock_error
            return mock_success

        with patch.object(downloader, "_client") as mock_client:
            mock_client.get = intermittent_server_error

            with patch("asyncio.sleep", AsyncMock()):
                result = await downloader.download("https://example.com/image.png")

        assert call_count == 3
        assert result.content == mock_success.content


class TestUserAgent:
    """Test user agent configuration."""

    def test_sets_user_agent(self) -> None:
        """Should set appropriate user agent."""
        downloader = ImageDownloader()
        assert "copy-that" in downloader.user_agent.lower() or "CopyThat" in downloader.user_agent

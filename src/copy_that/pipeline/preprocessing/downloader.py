"""Async image downloader with retry and exponential backoff.

Uses httpx for async HTTP requests with configurable timeout and retries.
"""

import asyncio
from dataclasses import dataclass
from typing import Self

import httpx


class DownloadError(Exception):
    """Base download error."""

    pass


class TimeoutError(DownloadError):
    """Request timed out."""

    pass


class RetryExhaustedError(DownloadError):
    """All retry attempts exhausted."""

    pass


@dataclass
class DownloadResult:
    """Result of image download."""

    content: bytes
    content_type: str
    content_length: int
    url: str


class ImageDownloader:
    """Async image downloader with retry and exponential backoff."""

    def __init__(
        self,
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
    ) -> None:
        """Initialize downloader.

        Args:
            timeout: Request timeout in seconds (default 30)
            max_retries: Maximum retry attempts (default 3)
            backoff_factor: Exponential backoff multiplier (default 2.0)
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.user_agent = "CopyThat/1.0 (Image Preprocessor)"

        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                follow_redirects=True,
                headers={"User-Agent": self.user_agent},
            )
        return self._client

    async def download(self, url: str) -> DownloadResult:
        """Download image from URL.

        Args:
            url: Image URL to download

        Returns:
            DownloadResult with content and metadata

        Raises:
            TimeoutError: If request times out
            RetryExhaustedError: If all retries are exhausted
            DownloadError: For other download failures
        """
        client = await self._get_client()
        last_error: Exception | None = None

        for attempt in range(self.max_retries + 1):
            try:
                response = await client.get(url)

                # Don't retry on client errors (4xx)
                if 400 <= response.status_code < 500:
                    raise DownloadError(f"HTTP {response.status_code}: {response.text[:200]}")

                # Retry on server errors (5xx)
                if response.status_code >= 500:
                    if attempt < self.max_retries:
                        delay = self.backoff_factor**attempt
                        await asyncio.sleep(delay)
                        continue
                    raise DownloadError(
                        f"HTTP {response.status_code}: Server error after {self.max_retries} retries"
                    )

                # Success - validate content type
                content_type = response.headers.get("content-type", "")
                if not self._is_valid_content_type(content_type):
                    raise DownloadError(f"Invalid content-type: {content_type}. Expected image/*")

                # Parse content length
                content_length = int(response.headers.get("content-length", len(response.content)))

                return DownloadResult(
                    content=response.content,
                    content_type=content_type,
                    content_length=content_length,
                    url=str(response.url),
                )

            except httpx.TimeoutException as e:
                raise TimeoutError(f"Request timeout after {self.timeout}s: {e}")

            except (httpx.ConnectError, httpx.NetworkError) as e:
                last_error = e
                if attempt < self.max_retries:
                    delay = self.backoff_factor**attempt
                    await asyncio.sleep(delay)
                    continue
                raise RetryExhaustedError(
                    f"Retry exhausted after {self.max_retries + 1} attempts: {e}"
                )

            except DownloadError:
                raise

            except Exception as e:
                raise DownloadError(f"Download failed: {e}")

        # Should not reach here, but just in case
        raise RetryExhaustedError(f"Retry exhausted: {last_error}")

    def _is_valid_content_type(self, content_type: str) -> bool:
        """Check if content type is valid image type.

        Args:
            content_type: HTTP Content-Type header value

        Returns:
            True if valid image content type
        """
        if not content_type:
            return False

        # Extract main type, ignoring charset and other params
        main_type = content_type.split(";")[0].strip().lower()

        # Accept image/* content types
        if main_type.startswith("image/"):
            return True

        # Also accept application/octet-stream as some servers misconfigure this
        return main_type == "application/octet-stream"

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> Self:
        """Async context manager entry."""
        await self._get_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()

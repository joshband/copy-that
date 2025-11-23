"""Preprocessing pipeline agent.

Orchestrates: validate → download → enhance → cache
Returns ProcessedImage with metadata for downstream agents.
"""

import hashlib
import uuid
from datetime import datetime
from typing import Self

from copy_that.pipeline import (
    BasePipelineAgent,
    PipelineTask,
    ProcessedImage,
)
from copy_that.pipeline.exceptions import PreprocessingError

from .downloader import (
    DownloadError,
    ImageDownloader,
    RetryExhaustedError,
    TimeoutError,
)
from .enhancer import EnhancementError, ImageEnhancer
from .validator import (
    FileSizeError,
    ImageValidator,
    InvalidImageError,
    SSRFError,
    ValidationError,
)


class PreprocessingAgent(BasePipelineAgent):
    """Agent that preprocesses images for the extraction pipeline.

    Orchestrates the full preprocessing flow:
    1. Validate URL (SSRF protection)
    2. Download image (with retry)
    3. Validate image content (magic bytes, size)
    4. Enhance image (resize, contrast, format conversion)
    5. Cache result (optional)

    Returns ProcessedImage with metadata for downstream extraction agents.
    """

    def __init__(
        self,
        cache_enabled: bool = True,
        max_file_size_mb: int = 10,
        timeout: int = 30,
        max_retries: int = 3,
    ) -> None:
        """Initialize preprocessing agent.

        Args:
            cache_enabled: Enable image caching (default True)
            max_file_size_mb: Maximum file size in MB (default 10)
            timeout: Download timeout in seconds (default 30)
            max_retries: Maximum download retries (default 3)
        """
        self._validator = ImageValidator(max_file_size_mb=max_file_size_mb)
        self._downloader = ImageDownloader(timeout=timeout, max_retries=max_retries)
        self._enhancer = ImageEnhancer()

        self._cache_enabled = cache_enabled
        self._cache: dict[str, ProcessedImage] = {}

    @property
    def agent_type(self) -> str:
        """Unique identifier for this agent."""
        return "preprocessor"

    @property
    def stage_name(self) -> str:
        """Pipeline stage name."""
        return "preprocessing"

    async def process(self, task: PipelineTask) -> ProcessedImage:
        """Process a pipeline task.

        Orchestrates: validate → download → enhance

        Args:
            task: Pipeline task with image URL

        Returns:
            ProcessedImage with metadata

        Raises:
            PreprocessingError: If any step fails
        """
        url = task.image_url

        # Check cache first
        if self._cache_enabled:
            cache_key = self._get_cache_key(url)
            if cache_key in self._cache:
                return self._cache[cache_key]

        try:
            # Step 1: Validate URL (SSRF protection)
            self._validator.validate_url(url)

            # Step 2: Download image
            download_result = await self._downloader.download(url)

            # Step 3: Validate image content
            self._validator.validate_file_size(download_result.content)
            self._validator.validate_magic_bytes(download_result.content)

            # Step 4: Enhance image
            enhanced = self._enhancer.enhance(download_result.content)

            # Step 5: Create ProcessedImage
            processed_image = ProcessedImage(
                image_id=self._generate_image_id(url, download_result.content),
                source_url=url,
                width=enhanced["width"],
                height=enhanced["height"],
                format=enhanced["format"],
                file_size=len(enhanced["data"]),
                preprocessed_data={
                    "enhanced_data": enhanced["data"],
                    "original_size": len(download_result.content),
                    "content_type": download_result.content_type,
                },
                processed_at=datetime.now(),
            )

            # Cache result
            if self._cache_enabled:
                self._cache[cache_key] = processed_image

            return processed_image

        except SSRFError as e:
            raise PreprocessingError(
                f"SSRF blocked: {e}",
                details={"task_id": task.task_id, "image_url": url},
            )

        except InvalidImageError as e:
            raise PreprocessingError(
                f"Invalid image: {e}",
                details={"task_id": task.task_id, "image_url": url},
            )

        except FileSizeError as e:
            raise PreprocessingError(
                f"File size error: {e}",
                details={"task_id": task.task_id, "image_url": url},
            )

        except ValidationError as e:
            raise PreprocessingError(
                f"Validation error: {e}",
                details={"task_id": task.task_id, "image_url": url},
            )

        except (DownloadError, TimeoutError, RetryExhaustedError) as e:
            raise PreprocessingError(
                f"Download failed: {e}",
                details={"task_id": task.task_id, "image_url": url},
            )

        except EnhancementError as e:
            raise PreprocessingError(
                f"Enhancement failed: {e}",
                details={"task_id": task.task_id, "image_url": url},
            )

        except Exception as e:
            raise PreprocessingError(
                f"Preprocessing failed: {e}",
                details={"task_id": task.task_id, "image_url": url},
            )

    async def health_check(self) -> bool:
        """Check if agent and dependencies are healthy.

        Returns:
            True if healthy
        """
        try:
            # Check validator is initialized
            if not self._validator:
                return False

            # Check downloader is available
            if not self._downloader:
                return False

            # Check enhancer is available
            return bool(self._enhancer)

        except Exception:
            return False

    def _get_cache_key(self, url: str) -> str:
        """Generate cache key for URL.

        Args:
            url: Image URL

        Returns:
            Cache key string
        """
        return hashlib.sha256(url.encode()).hexdigest()

    def _generate_image_id(self, url: str, content: bytes) -> str:
        """Generate unique image ID.

        Args:
            url: Image URL
            content: Image content bytes

        Returns:
            Unique image ID
        """
        # Combine URL and content hash for uniqueness
        content_hash = hashlib.sha256(content).hexdigest()[:8]
        url_hash = hashlib.sha256(url.encode()).hexdigest()[:8]
        unique_part = uuid.uuid4().hex[:8]

        return f"img_{url_hash}_{content_hash}_{unique_part}"

    def clear_cache(self) -> None:
        """Clear the image cache."""
        self._cache.clear()

    async def close(self) -> None:
        """Close resources."""
        await self._downloader.close()
        self.clear_cache()

    async def __aenter__(self) -> Self:
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()

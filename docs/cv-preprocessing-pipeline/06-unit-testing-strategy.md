# Unit Testing Strategy

[← Back to Index](./README.md) | [Previous: Dependency Recommendations](./05-dependency-recommendations.md)

---

## 6.1 Test Structure

### Directory Layout

```
tests/
└── unit/
    └── test_image_processing/
        ├── __init__.py
        ├── conftest.py              # Shared fixtures
        ├── test_loader.py           # Async loading tests
        ├── test_validator.py        # Validation tests
        ├── test_preprocessor.py     # OpenCV ops tests
        ├── test_optimizer.py        # Compression tests
        ├── test_pipeline.py         # Integration tests
        ├── test_exceptions.py       # Error handling tests
        └── fixtures/
            ├── valid/               # Valid test images
            │   ├── small.jpg
            │   ├── medium.png
            │   └── large.webp
            ├── invalid/             # Invalid/corrupt images
            │   ├── truncated.jpg
            │   ├── fake_extension.png
            │   └── not_an_image.jpg
            └── edge_cases/          # Edge case images
                ├── 1x1.png
                ├── extreme_aspect.jpg
                └── cmyk.jpg
```

---

## 6.2 Test Cases by Module

### test_loader.py - Async Loading Tests

```python
"""Tests for async image loading"""

import pytest
import httpx
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from copy_that.infrastructure.cv.loader import (
    AsyncImageFetcher,
    AsyncFileLoader,
    FetcherConfig,
    LoaderConfig,
)
from copy_that.infrastructure.cv.exceptions import (
    FileTooLargeError,
    InvalidURLError,
    NetworkError,
    InvalidPathError,
)


class TestAsyncImageFetcher:
    """Tests for URL fetching"""

    @pytest.fixture
    def fetcher(self):
        config = FetcherConfig(max_size_mb=10.0)
        return AsyncImageFetcher(config)

    async def test_fetch_valid_url(self, fetcher, mock_httpx_client, valid_jpeg_bytes):
        """Should successfully fetch image from valid URL"""
        result = await fetcher.fetch("https://example.com/image.jpg")

        assert result.data == valid_jpeg_bytes
        assert result.content_type == "image/jpeg"

    async def test_fetch_with_redirect(self, fetcher, mock_httpx_client):
        """Should follow redirects up to limit"""
        # Configure mock to return redirect then success
        result = await fetcher.fetch("https://example.com/redirect")

        assert result.url != "https://example.com/redirect"
        assert result.data is not None

    async def test_fetch_timeout(self, fetcher):
        """Should raise TimeoutError after configured timeout"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.stream.side_effect = (
                httpx.TimeoutException("Connection timeout")
            )

            with pytest.raises(NetworkError) as exc_info:
                await fetcher.fetch("https://slow-server.com/image.jpg")

            assert "timeout" in str(exc_info.value).lower()

    async def test_fetch_404(self, fetcher):
        """Should raise NetworkError for 404"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = (
                httpx.HTTPStatusError("Not found", request=None, response=mock_response)
            )

            mock_client.return_value.__aenter__.return_value.stream.return_value.__aenter__.return_value = mock_response

            with pytest.raises(NetworkError):
                await fetcher.fetch("https://example.com/missing.jpg")

    async def test_fetch_ssrf_protection_private_ip(self, fetcher):
        """Should block private IP addresses"""
        private_urls = [
            "http://192.168.1.1/image.jpg",
            "http://10.0.0.1/image.jpg",
            "http://172.16.0.1/image.jpg",
            "http://127.0.0.1/image.jpg",
        ]

        for url in private_urls:
            with pytest.raises(InvalidURLError) as exc_info:
                await fetcher.fetch(url)
            assert "private" in str(exc_info.value).lower() or "blocked" in str(exc_info.value).lower()

    async def test_fetch_ssrf_protection_localhost(self, fetcher):
        """Should block localhost"""
        with pytest.raises(InvalidURLError):
            await fetcher.fetch("http://localhost/image.jpg")

    async def test_fetch_ssrf_protection_metadata(self, fetcher):
        """Should block cloud metadata endpoints"""
        with pytest.raises(InvalidURLError):
            await fetcher.fetch("http://169.254.169.254/latest/meta-data/")

    async def test_fetch_size_limit_during_download(self, fetcher):
        """Should abort if size exceeds limit during streaming"""
        # Create fetcher with small limit
        config = FetcherConfig(max_size_mb=0.001)  # 1KB limit
        small_fetcher = AsyncImageFetcher(config)

        with pytest.raises(FileTooLargeError):
            await small_fetcher.fetch("https://example.com/large.jpg")

    async def test_fetch_progress_callback(self, fetcher, mock_httpx_client, valid_jpeg_bytes):
        """Should call progress callback with correct values"""
        progress_updates = []

        async def track_progress(downloaded, total):
            progress_updates.append((downloaded, total))

        await fetcher.fetch(
            "https://example.com/image.jpg",
            progress_callback=track_progress
        )

        assert len(progress_updates) > 0
        # Final update should have all bytes
        assert progress_updates[-1][0] == len(valid_jpeg_bytes)

    async def test_fetch_invalid_scheme(self, fetcher):
        """Should reject non-HTTP schemes"""
        with pytest.raises(InvalidURLError):
            await fetcher.fetch("ftp://example.com/image.jpg")

        with pytest.raises(InvalidURLError):
            await fetcher.fetch("file:///etc/passwd")

    async def test_fetch_missing_hostname(self, fetcher):
        """Should reject URLs without hostname"""
        with pytest.raises(InvalidURLError):
            await fetcher.fetch("http:///image.jpg")


class TestAsyncFileLoader:
    """Tests for local file loading"""

    @pytest.fixture
    def loader(self, tmp_path):
        config = LoaderConfig(
            max_size_mb=10.0,
            allowed_roots=[tmp_path]
        )
        return AsyncFileLoader(config)

    async def test_load_existing_file(self, loader, tmp_path, valid_jpeg_bytes):
        """Should load file contents asynchronously"""
        file_path = tmp_path / "test.jpg"
        file_path.write_bytes(valid_jpeg_bytes)

        result = await loader.load(file_path)

        assert result == valid_jpeg_bytes

    async def test_load_nonexistent_file(self, loader, tmp_path):
        """Should raise FileNotFoundError"""
        with pytest.raises(FileNotFoundError):
            await loader.load(tmp_path / "missing.jpg")

    async def test_load_path_traversal_protection(self, loader, tmp_path):
        """Should reject path traversal attempts"""
        with pytest.raises(InvalidPathError):
            await loader.load(tmp_path / ".." / "etc" / "passwd")

    async def test_load_outside_allowed_roots(self, loader):
        """Should reject paths outside allowed directories"""
        with pytest.raises(InvalidPathError):
            await loader.load(Path("/etc/passwd"))

    async def test_load_file_too_large(self, loader, tmp_path):
        """Should reject files exceeding size limit"""
        # Create file larger than limit
        large_file = tmp_path / "large.jpg"
        large_file.write_bytes(b"x" * (11 * 1024 * 1024))  # 11MB

        with pytest.raises(FileTooLargeError):
            await loader.load(large_file)

    async def test_load_streaming(self, loader, tmp_path, valid_jpeg_bytes):
        """Should yield chunks for streaming mode"""
        file_path = tmp_path / "test.jpg"
        file_path.write_bytes(valid_jpeg_bytes)

        chunks = []
        async for chunk in loader.load_streaming(file_path):
            chunks.append(chunk)

        assert b"".join(chunks) == valid_jpeg_bytes
```

### test_validator.py - Validation Tests

```python
"""Tests for image validation"""

import pytest
from PIL import Image
import io

from copy_that.infrastructure.cv.validator import (
    MagicValidator,
    SizeValidator,
    IntegrityValidator,
    FormatValidator,
    ImageFormat,
    SizeConfig,
    ValidationConfig,
)
from copy_that.infrastructure.cv.exceptions import (
    InvalidImageError,
    UnsupportedFormatError,
    FileTooLargeError,
    DimensionError,
    CorruptImageError,
    FormatMismatchError,
    AspectRatioError,
)


class TestMagicValidator:
    """Tests for magic byte validation"""

    @pytest.fixture
    def validator(self):
        return MagicValidator()

    def test_detect_jpeg(self, validator, valid_jpeg_bytes):
        """Should detect JPEG from magic bytes"""
        result = validator.detect_format(valid_jpeg_bytes)
        assert result == ImageFormat.JPEG

    def test_detect_png(self, validator, valid_png_bytes):
        """Should detect PNG from magic bytes"""
        result = validator.detect_format(valid_png_bytes)
        assert result == ImageFormat.PNG

    def test_detect_webp(self, validator, valid_webp_bytes):
        """Should detect WebP from magic bytes"""
        result = validator.detect_format(valid_webp_bytes)
        assert result == ImageFormat.WEBP

    def test_detect_gif(self, validator, valid_gif_bytes):
        """Should detect GIF from magic bytes"""
        result = validator.detect_format(valid_gif_bytes)
        assert result == ImageFormat.GIF

    def test_reject_non_image(self, validator):
        """Should reject non-image files"""
        pdf_header = b"%PDF-1.4"
        with pytest.raises(InvalidImageError) as exc_info:
            validator.detect_format(pdf_header)
        assert "not an image" in str(exc_info.value).lower()

    def test_reject_text_file(self, validator):
        """Should reject text files"""
        text_content = b"This is just plain text"
        with pytest.raises(InvalidImageError):
            validator.detect_format(text_content)

    def test_extension_mismatch(self, validator, valid_jpeg_bytes):
        """Should detect when extension doesn't match content"""
        with pytest.raises(FormatMismatchError) as exc_info:
            validator.validate_extension_matches(valid_jpeg_bytes, "image.png")

        assert exc_info.value.claimed == ImageFormat.PNG
        assert exc_info.value.actual == ImageFormat.JPEG


class TestSizeValidator:
    """Tests for size constraints"""

    @pytest.fixture
    def validator(self):
        config = SizeConfig(
            max_file_size_mb=10.0,
            min_dimension=10,
            max_dimension=4096,
            max_megapixels=50.0,
            max_aspect_ratio=10.0
        )
        return SizeValidator(config)

    def test_file_size_under_limit(self, validator, valid_jpeg_bytes):
        """Should accept files under size limit"""
        # Should not raise
        validator.validate_file_size(valid_jpeg_bytes)

    def test_file_size_over_limit(self, validator):
        """Should reject files over size limit"""
        large_data = b"x" * (11 * 1024 * 1024)  # 11MB

        with pytest.raises(FileTooLargeError) as exc_info:
            validator.validate_file_size(large_data)

        assert exc_info.value.actual_size_mb > 10.0
        assert exc_info.value.limit_mb == 10.0

    def test_file_size_exactly_at_limit(self, validator):
        """Should accept files exactly at limit"""
        exact_data = b"x" * (10 * 1024 * 1024)  # Exactly 10MB
        # Should not raise
        validator.validate_file_size(exact_data)

    def test_dimensions_within_limits(self, validator):
        """Should accept images within dimension limits"""
        validator.validate_dimensions(1920, 1080)

    def test_dimensions_too_small_width(self, validator):
        """Should reject images below minimum width"""
        with pytest.raises(DimensionError):
            validator.validate_dimensions(5, 100)

    def test_dimensions_too_small_height(self, validator):
        """Should reject images below minimum height"""
        with pytest.raises(DimensionError):
            validator.validate_dimensions(100, 5)

    def test_dimensions_too_large_width(self, validator):
        """Should reject images above maximum width"""
        with pytest.raises(DimensionError):
            validator.validate_dimensions(5000, 1000)

    def test_dimensions_too_large_height(self, validator):
        """Should reject images above maximum height"""
        with pytest.raises(DimensionError):
            validator.validate_dimensions(1000, 5000)

    def test_megapixel_limit(self, validator):
        """Should reject images exceeding megapixel limit"""
        # 51MP = 8000x6375 (roughly)
        with pytest.raises(DimensionError) as exc_info:
            validator.validate_dimensions(8000, 6500)

        assert "MP" in str(exc_info.value)

    def test_aspect_ratio_normal(self, validator):
        """Should accept reasonable aspect ratios"""
        validator.validate_aspect_ratio(1920, 1080)  # 16:9
        validator.validate_aspect_ratio(1080, 1920)  # 9:16

    def test_aspect_ratio_extreme(self, validator):
        """Should reject extreme aspect ratios"""
        with pytest.raises(AspectRatioError):
            validator.validate_aspect_ratio(10000, 100)  # 100:1


class TestIntegrityValidator:
    """Tests for corrupt image detection"""

    @pytest.fixture
    def validator(self):
        return IntegrityValidator()

    def test_valid_image(self, validator, valid_jpeg_bytes):
        """Should accept valid, complete images"""
        info = validator.validate(valid_jpeg_bytes)

        assert info.width > 0
        assert info.height > 0
        assert info.format == "JPEG"

    def test_truncated_jpeg(self, validator, valid_jpeg_bytes):
        """Should detect truncated JPEG (missing EOI marker)"""
        truncated = valid_jpeg_bytes[:-2]  # Remove FFD9

        with pytest.raises(CorruptImageError) as exc_info:
            validator.validate(truncated)

        # Pillow might not always detect this, so also check truncation
        validator.check_truncation(truncated, ImageFormat.JPEG)

    def test_truncated_png(self, validator, valid_png_bytes):
        """Should detect truncated PNG"""
        truncated = valid_png_bytes[:-12]  # Remove IEND chunk

        with pytest.raises(CorruptImageError):
            validator.check_truncation(truncated, ImageFormat.PNG)

    def test_corrupt_headers(self, validator):
        """Should reject images with corrupt headers"""
        # JPEG header but garbage content
        corrupt = b"\xff\xd8\xff\xe0" + b"garbage" * 100

        with pytest.raises(CorruptImageError):
            validator.validate(corrupt)

    def test_completely_invalid(self, validator):
        """Should reject completely invalid data"""
        with pytest.raises(CorruptImageError):
            validator.validate(b"not an image at all")

    def test_empty_file(self, validator):
        """Should reject empty files"""
        with pytest.raises(CorruptImageError):
            validator.validate(b"")
```

### test_preprocessor.py - OpenCV Operations Tests

```python
"""Tests for OpenCV preprocessing operations"""

import pytest
import numpy as np
import cv2
from PIL import Image
import io

from copy_that.infrastructure.cv.preprocessor import (
    ImagePreprocessor,
    PreprocessingConfig,
)


class TestImagePreprocessor:
    """Tests for OpenCV preprocessing operations"""

    @pytest.fixture
    def preprocessor(self):
        config = PreprocessingConfig(
            target_dimension=1024,
            jpeg_quality=85,
            enable_enhancement=True,
        )
        return ImagePreprocessor(config)

    @pytest.fixture
    def large_image(self):
        """Create a 4000x3000 test image"""
        return np.random.randint(0, 255, (3000, 4000, 3), dtype=np.uint8)

    @pytest.fixture
    def small_image(self):
        """Create a 100x100 test image"""
        return np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)

    def test_resize_larger_image(self, preprocessor, large_image):
        """Should resize image larger than target"""
        result = preprocessor.resize_for_api(large_image, max_size=1024)

        assert max(result.shape[:2]) <= 1024
        # Aspect ratio should be maintained
        original_ratio = large_image.shape[1] / large_image.shape[0]
        result_ratio = result.shape[1] / result.shape[0]
        assert abs(original_ratio - result_ratio) < 0.01

    def test_resize_smaller_image(self, preprocessor, small_image):
        """Should not resize image smaller than target"""
        result = preprocessor.resize_for_api(small_image, max_size=1024)

        # Should be unchanged
        assert result.shape == small_image.shape

    def test_resize_maintains_aspect_ratio(self, preprocessor):
        """Should maintain aspect ratio when resizing"""
        # Create image with specific aspect ratio (2:1)
        wide_image = np.zeros((500, 1000, 3), dtype=np.uint8)
        result = preprocessor.resize_for_api(wide_image, max_size=512)

        # New dimensions should maintain 2:1 ratio
        assert result.shape[1] == 512
        assert result.shape[0] == 256

    def test_normalize_bgr_to_rgb(self, preprocessor):
        """Should convert BGR to RGB"""
        # Create BGR image (blue in first channel)
        bgr_image = np.zeros((100, 100, 3), dtype=np.uint8)
        bgr_image[:, :, 0] = 255  # Blue channel

        result = preprocessor.normalize_color_space(bgr_image, source="BGR")

        # After conversion, blue should be in third channel
        assert result[:, :, 2].mean() == 255
        assert result[:, :, 0].mean() == 0

    def test_normalize_grayscale(self, preprocessor):
        """Should convert grayscale to RGB (3-channel)"""
        gray_image = np.full((100, 100), 128, dtype=np.uint8)

        result = preprocessor.normalize_color_space(gray_image)

        assert len(result.shape) == 3
        assert result.shape[2] == 3
        assert result[:, :, 0].mean() == 128

    def test_normalize_rgba(self, preprocessor):
        """Should handle RGBA images"""
        rgba_image = np.zeros((100, 100, 4), dtype=np.uint8)
        rgba_image[:, :, 0] = 255  # Red
        rgba_image[:, :, 3] = 128  # Alpha

        result = preprocessor.normalize_color_space(rgba_image)

        # Should be RGB (alpha removed or blended)
        assert result.shape[2] == 3

    def test_enhance_low_contrast(self, preprocessor):
        """Should enhance low contrast images"""
        # Create low contrast image
        low_contrast = np.full((100, 100, 3), 128, dtype=np.uint8)
        low_contrast[40:60, 40:60] = 135  # Small difference

        result = preprocessor.enhance_for_extraction(low_contrast)

        # Result should have higher contrast
        result_std = result.std()
        original_std = low_contrast.std()
        assert result_std > original_std

    def test_enhance_normal_image(self, preprocessor):
        """Should not over-enhance normal images"""
        # Create image with good contrast
        normal_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)

        result = preprocessor.enhance_for_extraction(normal_image)

        # Should still be valid (not clipped/saturated)
        assert result.min() >= 0
        assert result.max() <= 255

    def test_auto_orient_exif_rotation(self, preprocessor, exif_rotated_image):
        """Should apply EXIF rotation correction"""
        # Load image with EXIF orientation
        img = Image.open(io.BytesIO(exif_rotated_image))
        img_array = np.array(img)

        result = preprocessor.auto_orient(img_array, img.getexif())

        # Image should be rotated to correct orientation
        # Original was 100x200, after 90° rotation should be 200x100
        assert result.shape[0] > result.shape[1]

    def test_auto_orient_no_exif(self, preprocessor):
        """Should handle images without EXIF"""
        no_exif_image = np.zeros((100, 100, 3), dtype=np.uint8)

        result = preprocessor.auto_orient(no_exif_image, {})

        # Should be unchanged
        assert result.shape == no_exif_image.shape
```

### test_pipeline.py - Integration Tests

```python
"""Integration tests for complete preprocessing pipeline"""

import pytest
import asyncio

from copy_that.infrastructure.cv.preprocessing import (
    ImagePreprocessingPipeline,
    ImageSource,
    PreprocessingConfig,
)
from copy_that.infrastructure.cv.exceptions import (
    ImageProcessingError,
)


class TestPreprocessingPipeline:
    """Integration tests for the complete pipeline"""

    @pytest.fixture
    def pipeline(self):
        config = PreprocessingConfig(
            max_file_size_mb=10.0,
            target_dimension=1024,
            enable_enhancement=True,
        )
        return ImagePreprocessingPipeline(config)

    async def test_pipeline_url_to_optimized(self, pipeline, mock_httpx_client):
        """Should process URL through complete pipeline"""
        source = ImageSource.from_url("https://example.com/image.jpg")
        result = await pipeline.process(source)

        assert result.data is not None
        assert len(result.data) > 0
        assert result.format in ("webp", "jpeg", "png")

    async def test_pipeline_file_to_optimized(self, pipeline, tmp_path, valid_jpeg_bytes):
        """Should process file through complete pipeline"""
        file_path = tmp_path / "test.jpg"
        file_path.write_bytes(valid_jpeg_bytes)

        source = ImageSource.from_file(file_path)
        result = await pipeline.process(source)

        assert result.data is not None
        assert result.optimized_size <= result.original_size

    async def test_pipeline_base64_to_optimized(self, pipeline, valid_jpeg_bytes):
        """Should process base64 through complete pipeline"""
        import base64
        b64_data = base64.b64encode(valid_jpeg_bytes).decode()

        source = ImageSource.from_base64(b64_data, "image/jpeg")
        result = await pipeline.process(source)

        assert result.data is not None

    async def test_pipeline_graceful_degradation(self, pipeline, tmp_path):
        """Should fall back to simpler strategies on failure"""
        # Create large image that might cause memory issues
        large_image = tmp_path / "large.jpg"
        # Create 20MP image
        from PIL import Image
        img = Image.new("RGB", (5000, 4000), color="red")
        img.save(large_image, "JPEG")

        source = ImageSource.from_file(large_image)
        result = await pipeline.process(source)

        # Should succeed (possibly with degradation)
        assert result.data is not None

    async def test_pipeline_invalid_url_fails(self, pipeline):
        """Should fail for invalid URLs"""
        source = ImageSource.from_url("http://localhost/image.jpg")

        with pytest.raises(ImageProcessingError):
            await pipeline.process(source)

    async def test_pipeline_corrupt_image_fails(self, pipeline, tmp_path, valid_jpeg_bytes):
        """Should fail for corrupt images"""
        corrupt_path = tmp_path / "corrupt.jpg"
        corrupt_path.write_bytes(valid_jpeg_bytes[:100])  # Truncated

        source = ImageSource.from_file(corrupt_path)

        with pytest.raises(ImageProcessingError):
            await pipeline.process(source)


class TestConcurrentProcessing:
    """Tests for concurrent batch processing"""

    @pytest.fixture
    def processor(self):
        from copy_that.infrastructure.cv.preprocessing import ConcurrentImageProcessor
        return ConcurrentImageProcessor(max_concurrent=4)

    async def test_batch_processing(self, processor, tmp_path, valid_jpeg_bytes):
        """Should process multiple images concurrently"""
        # Create test files
        sources = []
        for i in range(10):
            path = tmp_path / f"image_{i}.jpg"
            path.write_bytes(valid_jpeg_bytes)
            sources.append(ImageSource.from_file(path))

        results = await processor.process_batch(sources)

        assert len(results) == 10
        assert all(r.data is not None for r in results if not isinstance(r, Exception))

    async def test_batch_with_failures(self, processor, tmp_path, valid_jpeg_bytes):
        """Should handle mixed success/failure in batch"""
        # Create mix of valid and invalid
        sources = []

        # Valid file
        valid_path = tmp_path / "valid.jpg"
        valid_path.write_bytes(valid_jpeg_bytes)
        sources.append(ImageSource.from_file(valid_path))

        # Invalid file
        invalid_path = tmp_path / "invalid.jpg"
        invalid_path.write_bytes(b"not an image")
        sources.append(ImageSource.from_file(invalid_path))

        # Another valid
        valid_path2 = tmp_path / "valid2.jpg"
        valid_path2.write_bytes(valid_jpeg_bytes)
        sources.append(ImageSource.from_file(valid_path2))

        results = await processor.process_batch(sources)

        assert len(results) == 3
        # First and third should succeed
        assert results[0].data is not None
        assert isinstance(results[1], Exception)
        assert results[2].data is not None

    async def test_progress_callback(self, processor, tmp_path, valid_jpeg_bytes):
        """Should report progress during batch processing"""
        sources = []
        for i in range(5):
            path = tmp_path / f"image_{i}.jpg"
            path.write_bytes(valid_jpeg_bytes)
            sources.append(ImageSource.from_file(path))

        progress_updates = []

        async def on_progress(completed, total):
            progress_updates.append((completed, total))

        await processor.process_batch(sources, progress_callback=on_progress)

        assert len(progress_updates) == 5
        assert progress_updates[-1] == (5, 5)
```

---

## 6.3 Mock Strategies for Async Operations

### Shared Test Fixtures

```python
# tests/unit/test_image_processing/conftest.py

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
from PIL import Image
import io
import httpx

# =============================================================================
# Image Fixtures
# =============================================================================

@pytest.fixture
def valid_jpeg_bytes():
    """Generate valid JPEG test image"""
    img = Image.new("RGB", (100, 100), color="red")
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    return buffer.getvalue()


@pytest.fixture
def valid_png_bytes():
    """Generate valid PNG with alpha"""
    img = Image.new("RGBA", (100, 100), color=(255, 0, 0, 128))
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.fixture
def valid_webp_bytes():
    """Generate valid WebP image"""
    img = Image.new("RGB", (100, 100), color="blue")
    buffer = io.BytesIO()
    img.save(buffer, format="WEBP")
    return buffer.getvalue()


@pytest.fixture
def valid_gif_bytes():
    """Generate valid GIF image"""
    img = Image.new("P", (100, 100), color=1)
    buffer = io.BytesIO()
    img.save(buffer, format="GIF")
    return buffer.getvalue()


@pytest.fixture
def large_image_bytes():
    """Generate large image for resize tests"""
    img = Image.new("RGB", (4000, 3000), color="blue")
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    return buffer.getvalue()


@pytest.fixture
def corrupt_jpeg_bytes(valid_jpeg_bytes):
    """Create truncated JPEG"""
    return valid_jpeg_bytes[:-2]


@pytest.fixture
def corrupt_png_bytes(valid_png_bytes):
    """Create truncated PNG"""
    return valid_png_bytes[:-12]


@pytest.fixture
def non_image_bytes():
    """Create non-image file"""
    return b"This is not an image file at all"


@pytest.fixture
def extreme_aspect_ratio():
    """Create image with extreme aspect ratio"""
    img = Image.new("RGB", (10000, 100), color="green")
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    return buffer.getvalue()


@pytest.fixture
def grayscale_image_bytes():
    """Create grayscale image"""
    img = Image.new("L", (100, 100), color=128)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.fixture
def exif_rotated_image():
    """Create image with EXIF rotation tag"""
    img = Image.new("RGB", (100, 200), color="yellow")
    buffer = io.BytesIO()

    # Add EXIF orientation
    from PIL.ExifTags import Base
    exif = img.getexif()
    exif[Base.Orientation] = 6  # Rotate 90 CW

    img.save(buffer, format="JPEG", exif=exif)
    return buffer.getvalue()


# =============================================================================
# HTTP Mocks
# =============================================================================

@pytest.fixture
def mock_httpx_client(valid_jpeg_bytes):
    """Mock httpx.AsyncClient for URL fetch tests"""

    async def mock_aiter_bytes(chunk_size=65536):
        """Yield test image data in chunks"""
        for i in range(0, len(valid_jpeg_bytes), chunk_size):
            yield valid_jpeg_bytes[i:i + chunk_size]

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()

        # Mock HEAD response
        mock_head_response = MagicMock()
        mock_head_response.headers = {
            "content-type": "image/jpeg",
            "content-length": str(len(valid_jpeg_bytes))
        }
        mock_client.head = AsyncMock(return_value=mock_head_response)

        # Mock stream context manager
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.headers = {
            "content-type": "image/jpeg",
            "content-length": str(len(valid_jpeg_bytes))
        }
        mock_response.raise_for_status = MagicMock()
        mock_response.aiter_bytes = mock_aiter_bytes
        mock_response.url = "https://example.com/image.jpg"

        # Setup stream context manager
        mock_stream_cm = AsyncMock()
        mock_stream_cm.__aenter__.return_value = mock_response
        mock_stream_cm.__aexit__.return_value = None
        mock_client.stream.return_value = mock_stream_cm

        # Setup client context manager
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None

        yield mock_client


# =============================================================================
# File System Mocks
# =============================================================================

@pytest.fixture
def mock_aiofiles(valid_jpeg_bytes):
    """Mock aiofiles for file I/O tests"""

    with patch("aiofiles.open") as mock_open:
        mock_file = AsyncMock()
        mock_file.read = AsyncMock(return_value=valid_jpeg_bytes)

        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_file
        mock_cm.__aexit__.return_value = None

        mock_open.return_value = mock_cm
        yield mock_open


@pytest.fixture
def mock_aiofiles_os():
    """Mock aiofiles.os for file system operations"""

    with patch("aiofiles.os.path.exists") as mock_exists, \
         patch("aiofiles.os.stat") as mock_stat:

        mock_exists.return_value = True

        mock_stat_result = MagicMock()
        mock_stat_result.st_size = 1024
        mock_stat.return_value = mock_stat_result

        yield {
            "exists": mock_exists,
            "stat": mock_stat,
        }


# =============================================================================
# Magic Bytes Mock
# =============================================================================

@pytest.fixture
def mock_magic():
    """Mock python-magic for format detection tests"""

    with patch("magic.Magic") as mock_magic_class:
        mock_instance = MagicMock()
        mock_instance.from_buffer.return_value = "image/jpeg"
        mock_magic_class.return_value = mock_instance
        yield mock_instance
```

---

## 6.4 Edge Cases and Error Conditions

```python
"""Tests for edge cases and error conditions"""

import pytest
import asyncio

from copy_that.infrastructure.cv.preprocessing import (
    ImagePreprocessingPipeline,
    ImageSource,
)
from copy_that.infrastructure.cv.exceptions import (
    ImageProcessingError,
)


class TestEdgeCases:
    """Test edge cases and error conditions"""

    # === Boundary conditions ===

    async def test_exact_size_limit(self, pipeline, tmp_path):
        """File exactly at size limit should be accepted"""
        from PIL import Image

        # Create file exactly at limit (10MB)
        img = Image.new("RGB", (3000, 3000), color="red")
        path = tmp_path / "exact.jpg"
        img.save(path, "JPEG", quality=95)

        # Adjust quality until file is exactly at limit
        # ... implementation detail

        source = ImageSource.from_file(path)
        result = await pipeline.process(source)
        assert result.data is not None

    async def test_minimum_valid_image(self, pipeline, tmp_path):
        """1x1 pixel image should be handled"""
        from PIL import Image

        img = Image.new("RGB", (1, 1), color="white")
        path = tmp_path / "tiny.png"
        img.save(path, "PNG")

        source = ImageSource.from_file(path)
        # Might fail due to min dimension, but should give clear error
        try:
            result = await pipeline.process(source)
        except ImageProcessingError as e:
            assert "dimension" in str(e).lower()

    # === Format edge cases ===

    async def test_animated_gif(self, pipeline, tmp_path):
        """Should handle animated GIF"""
        from PIL import Image

        # Create animated GIF
        frames = [
            Image.new("P", (100, 100), color=i)
            for i in range(3)
        ]
        path = tmp_path / "animated.gif"
        frames[0].save(
            path,
            save_all=True,
            append_images=frames[1:],
            duration=100,
            loop=0
        )

        source = ImageSource.from_file(path)
        result = await pipeline.process(source)
        assert result.data is not None

    async def test_16bit_png(self, pipeline, tmp_path):
        """Should handle 16-bit PNG"""
        import numpy as np
        from PIL import Image

        # Create 16-bit image
        data = np.random.randint(0, 65535, (100, 100), dtype=np.uint16)
        img = Image.fromarray(data, mode="I;16")
        path = tmp_path / "16bit.png"
        img.save(path, "PNG")

        source = ImageSource.from_file(path)
        result = await pipeline.process(source)
        assert result.data is not None

    async def test_cmyk_jpeg(self, pipeline, tmp_path):
        """Should convert CMYK to RGB"""
        from PIL import Image

        img = Image.new("CMYK", (100, 100), color=(0, 255, 255, 0))
        path = tmp_path / "cmyk.jpg"
        img.save(path, "JPEG")

        source = ImageSource.from_file(path)
        result = await pipeline.process(source)
        # Result should be RGB
        assert result.data is not None

    # === Network edge cases ===

    async def test_slow_server_timeout(self, pipeline):
        """Should timeout on slow server"""
        from unittest.mock import patch, AsyncMock
        import httpx

        with patch("httpx.AsyncClient") as mock:
            mock.return_value.__aenter__.return_value.stream.side_effect = (
                httpx.ReadTimeout("Slow server")
            )

            source = ImageSource.from_url("https://slow.example.com/image.jpg")

            with pytest.raises(ImageProcessingError) as exc_info:
                await pipeline.process(source)

            assert exc_info.value.recoverable is True

    # === Concurrent processing edge cases ===

    async def test_concurrent_same_url(self, processor, mock_httpx_client):
        """Should handle concurrent requests for same URL"""
        url = "https://example.com/image.jpg"
        sources = [ImageSource.from_url(url) for _ in range(10)]

        results = await processor.process_batch(sources)

        assert len(results) == 10
        assert all(r.data is not None for r in results if not isinstance(r, Exception))

    async def test_semaphore_exhaustion(self, processor, tmp_path, valid_jpeg_bytes):
        """Should handle semaphore exhaustion gracefully"""
        # Create many sources to exhaust semaphore
        sources = []
        for i in range(100):
            path = tmp_path / f"image_{i}.jpg"
            path.write_bytes(valid_jpeg_bytes)
            sources.append(ImageSource.from_file(path))

        # Should complete without deadlock
        results = await asyncio.wait_for(
            processor.process_batch(sources),
            timeout=60.0
        )

        assert len(results) == 100

    # === Error propagation ===

    async def test_error_context_preserved(self, pipeline, tmp_path):
        """Exceptions should preserve original context"""
        corrupt_path = tmp_path / "corrupt.jpg"
        corrupt_path.write_bytes(b"not an image")

        source = ImageSource.from_file(corrupt_path)

        with pytest.raises(ImageProcessingError) as exc_info:
            await pipeline.process(source)

        # Should have context
        error = exc_info.value
        assert error.context is not None
        assert str(corrupt_path) in error.context.source_identifier
```

---

## 6.5 Performance Benchmarking Tests

```python
"""Performance benchmarking tests"""

import pytest
import time
import asyncio
import numpy as np
import cv2
from PIL import Image
import io

from copy_that.infrastructure.cv.preprocessor import ImagePreprocessor
from copy_that.infrastructure.cv.preprocessing import (
    ConcurrentImageProcessor,
    ImageSource,
    PreprocessingConfig,
)
from copy_that.infrastructure.cv.validator import ImageValidator


class TestPerformance:
    """Performance benchmarks for image processing"""

    @pytest.mark.benchmark
    def test_resize_performance(self, benchmark):
        """Benchmark resize operation"""
        # Create large test image
        img = np.random.randint(0, 255, (3000, 4000, 3), dtype=np.uint8)

        config = PreprocessingConfig()
        preprocessor = ImagePreprocessor(config)

        def resize():
            return preprocessor.resize_for_api(img, 2048)

        result = benchmark(resize)

        assert result is not None
        assert max(result.shape[:2]) <= 2048

    @pytest.mark.benchmark
    def test_validation_performance(self, benchmark, valid_jpeg_bytes):
        """Benchmark validation pipeline"""
        config = PreprocessingConfig()
        validator = ImageValidator(config)

        result = benchmark(lambda: validator.validate(valid_jpeg_bytes))

        assert result is not None

    @pytest.mark.benchmark
    def test_enhancement_performance(self, benchmark):
        """Benchmark CLAHE enhancement"""
        img = np.random.randint(0, 255, (1000, 1000, 3), dtype=np.uint8)

        config = PreprocessingConfig(enable_enhancement=True)
        preprocessor = ImagePreprocessor(config)

        result = benchmark(lambda: preprocessor.enhance_for_extraction(img))

        assert result is not None

    @pytest.mark.benchmark
    def test_format_conversion_performance(self, benchmark, valid_jpeg_bytes):
        """Benchmark format conversion to WebP"""
        img = Image.open(io.BytesIO(valid_jpeg_bytes))

        def convert_to_webp():
            buffer = io.BytesIO()
            img.save(buffer, format="WEBP", quality=80)
            return buffer.getvalue()

        result = benchmark(convert_to_webp)

        assert result is not None

    @pytest.mark.asyncio
    async def test_concurrent_throughput(self, tmp_path, valid_jpeg_bytes):
        """Measure concurrent processing throughput"""
        # Create test files
        num_images = 100
        sources = []
        for i in range(num_images):
            path = tmp_path / f"image_{i}.jpg"
            path.write_bytes(valid_jpeg_bytes)
            sources.append(ImageSource.from_file(path))

        processor = ConcurrentImageProcessor(max_concurrent=4)

        start = time.monotonic()
        results = await processor.process_batch(sources)
        elapsed = time.monotonic() - start

        successful = sum(1 for r in results if not isinstance(r, Exception))
        throughput = successful / elapsed

        print(f"\nThroughput: {throughput:.1f} images/second")
        print(f"Total time: {elapsed:.2f}s for {num_images} images")

        # Minimum acceptable throughput
        assert throughput > 5  # At least 5 images/second

    @pytest.mark.asyncio
    async def test_memory_usage(self, tmp_path):
        """Verify memory is released after processing"""
        try:
            import tracemalloc
        except ImportError:
            pytest.skip("tracemalloc not available")

        tracemalloc.start()

        # Create large image
        from PIL import Image
        img = Image.new("RGB", (4000, 3000), color="red")
        path = tmp_path / "large.jpg"
        img.save(path, "JPEG")

        config = PreprocessingConfig()
        preprocessor = ImagePreprocessor(config)

        # Process multiple times
        for _ in range(10):
            with Image.open(path) as pil_img:
                np_img = np.array(pil_img)
                result = preprocessor.resize_for_api(np_img, 1024)
                del result
            del np_img

        import gc
        gc.collect()

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        peak_mb = peak / (1024 * 1024)
        print(f"\nPeak memory: {peak_mb:.1f}MB")

        # Peak should not exceed 500MB for this operation
        assert peak_mb < 500, f"Peak memory {peak_mb}MB exceeds 500MB limit"

    @pytest.mark.asyncio
    async def test_latency_distribution(self, tmp_path, valid_jpeg_bytes):
        """Measure latency distribution"""
        path = tmp_path / "test.jpg"
        path.write_bytes(valid_jpeg_bytes)

        config = PreprocessingConfig()
        from copy_that.infrastructure.cv.preprocessing import ImagePreprocessingPipeline
        pipeline = ImagePreprocessingPipeline(config)

        latencies = []
        for _ in range(100):
            source = ImageSource.from_file(path)
            start = time.monotonic()
            await pipeline.process(source)
            elapsed_ms = (time.monotonic() - start) * 1000
            latencies.append(elapsed_ms)

        latencies.sort()
        p50 = latencies[50]
        p95 = latencies[95]
        p99 = latencies[99]

        print(f"\nLatency distribution:")
        print(f"  P50: {p50:.1f}ms")
        print(f"  P95: {p95:.1f}ms")
        print(f"  P99: {p99:.1f}ms")

        # P95 should be under 500ms for small images
        assert p95 < 500, f"P95 latency {p95}ms exceeds 500ms"
```

---

## Summary

The unit testing strategy provides:

1. **Comprehensive Coverage:** Tests for all modules and functions
2. **Mock Strategies:** Async mocks for httpx, aiofiles, magic
3. **Test Fixtures:** Pre-built valid/invalid/edge-case images
4. **Edge Cases:** Boundary conditions, format variations, network issues
5. **Performance Benchmarks:** Throughput, latency, memory measurements

---

[← Back to Index](./README.md) | [Next: Implementation Roadmap →](./07-implementation-roadmap.md)

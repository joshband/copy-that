"""Tests for ImageEnhancer.

TESTS FIRST: These tests define the requirements before implementation.
"""

from io import BytesIO

import pytest
from PIL import Image

from copy_that.pipeline.preprocessing.enhancer import (
    EnhancementError,
    ImageEnhancer,
)


class TestImageEnhancer:
    """Test ImageEnhancer functionality."""

    @pytest.fixture
    def enhancer(self) -> ImageEnhancer:
        return ImageEnhancer()

    @pytest.fixture
    def sample_png_image(self) -> bytes:
        """Create a sample PNG image for testing."""
        img = Image.new("RGB", (100, 100), color=(255, 0, 0))
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

    @pytest.fixture
    def sample_rgba_image(self) -> bytes:
        """Create a sample RGBA image for testing."""
        img = Image.new("RGBA", (100, 100), color=(255, 0, 0, 128))
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

    @pytest.fixture
    def sample_large_image(self) -> bytes:
        """Create a large image that needs resizing."""
        img = Image.new("RGB", (3000, 2000), color=(0, 255, 0))
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

    def test_enhance_returns_dict_with_required_keys(
        self, enhancer: ImageEnhancer, sample_png_image: bytes
    ) -> None:
        """Should return dict with data, width, height, format."""
        result = enhancer.enhance(sample_png_image)

        assert "data" in result
        assert "width" in result
        assert "height" in result
        assert "format" in result
        assert isinstance(result["data"], bytes)
        assert isinstance(result["width"], int)
        assert isinstance(result["height"], int)
        assert isinstance(result["format"], str)

    def test_enhance_converts_to_webp_by_default(
        self, enhancer: ImageEnhancer, sample_png_image: bytes
    ) -> None:
        """Should convert to WebP format by default."""
        result = enhancer.enhance(sample_png_image)
        assert result["format"] == "webp"

    def test_enhance_resizes_large_images(
        self, enhancer: ImageEnhancer, sample_large_image: bytes
    ) -> None:
        """Should resize images larger than max dimensions."""
        result = enhancer.enhance(sample_large_image)

        # Should be resized to fit within 1920x1080
        assert result["width"] <= 1920
        assert result["height"] <= 1080

    def test_enhance_maintains_aspect_ratio(
        self, enhancer: ImageEnhancer, sample_large_image: bytes
    ) -> None:
        """Should maintain aspect ratio when resizing."""
        # Original is 3000x2000 (3:2 ratio)
        result = enhancer.enhance(sample_large_image)

        # Calculate aspect ratio
        original_ratio = 3000 / 2000
        result_ratio = result["width"] / result["height"]

        # Should be approximately the same
        assert abs(original_ratio - result_ratio) < 0.01

    def test_enhance_does_not_upscale_small_images(
        self, enhancer: ImageEnhancer, sample_png_image: bytes
    ) -> None:
        """Should not upscale images smaller than max dimensions."""
        result = enhancer.enhance(sample_png_image)

        # Original is 100x100, should stay the same
        assert result["width"] == 100
        assert result["height"] == 100

    def test_enhance_handles_rgba_images(
        self, enhancer: ImageEnhancer, sample_rgba_image: bytes
    ) -> None:
        """Should handle RGBA images by converting to RGB."""
        result = enhancer.enhance(sample_rgba_image)

        assert result["data"] is not None
        assert result["format"] == "webp"

    def test_enhance_handles_palette_images(self, enhancer: ImageEnhancer) -> None:
        """Should handle palette (P mode) images."""
        # Create a palette image
        img = Image.new("P", (100, 100))
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        palette_image = buffer.getvalue()

        result = enhancer.enhance(palette_image)
        assert result["data"] is not None

    def test_enhance_handles_grayscale_images(self, enhancer: ImageEnhancer) -> None:
        """Should handle grayscale (L mode) images."""
        img = Image.new("L", (100, 100), color=128)
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        grayscale_image = buffer.getvalue()

        result = enhancer.enhance(grayscale_image)
        assert result["data"] is not None

    def test_enhance_raises_error_on_invalid_data(self, enhancer: ImageEnhancer) -> None:
        """Should raise EnhancementError on invalid image data."""
        with pytest.raises(EnhancementError):
            enhancer.enhance(b"not an image")

    def test_enhance_raises_error_on_empty_data(self, enhancer: ImageEnhancer) -> None:
        """Should raise EnhancementError on empty data."""
        with pytest.raises(EnhancementError):
            enhancer.enhance(b"")


class TestEnhancerConfiguration:
    """Test enhancer configuration options."""

    def test_default_max_dimensions(self) -> None:
        """Should default to 1920x1080 max dimensions."""
        enhancer = ImageEnhancer()
        assert enhancer.max_width == 1920
        assert enhancer.max_height == 1080

    def test_custom_max_dimensions(self) -> None:
        """Should support custom max dimensions."""
        enhancer = ImageEnhancer(max_width=800, max_height=600)
        assert enhancer.max_width == 800
        assert enhancer.max_height == 600

    def test_default_output_format(self) -> None:
        """Should default to WebP output format."""
        enhancer = ImageEnhancer()
        assert enhancer.output_format == "webp"

    def test_custom_output_format(self) -> None:
        """Should support custom output format."""
        enhancer = ImageEnhancer(output_format="jpeg")
        assert enhancer.output_format == "jpeg"

    def test_default_webp_quality(self) -> None:
        """Should default to 85% WebP quality."""
        enhancer = ImageEnhancer()
        assert enhancer.webp_quality == 85

    def test_custom_webp_quality(self) -> None:
        """Should support custom WebP quality."""
        enhancer = ImageEnhancer(webp_quality=90)
        assert enhancer.webp_quality == 90

    def test_clahe_enabled_by_default(self) -> None:
        """Should have CLAHE enabled by default."""
        enhancer = ImageEnhancer()
        assert enhancer.apply_clahe is True

    def test_clahe_can_be_disabled(self) -> None:
        """Should allow disabling CLAHE."""
        enhancer = ImageEnhancer(apply_clahe=False)
        assert enhancer.apply_clahe is False


class TestOutputFormats:
    """Test different output format conversions."""

    @pytest.fixture
    def sample_image(self) -> bytes:
        """Create a sample image for testing."""
        img = Image.new("RGB", (100, 100), color=(255, 0, 0))
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

    def test_convert_to_jpeg(self, sample_image: bytes) -> None:
        """Should convert to JPEG format."""
        enhancer = ImageEnhancer(output_format="jpeg")
        result = enhancer.enhance(sample_image)
        assert result["format"] == "jpeg"

    def test_convert_to_png(self, sample_image: bytes) -> None:
        """Should convert to PNG format."""
        enhancer = ImageEnhancer(output_format="png")
        result = enhancer.enhance(sample_image)
        assert result["format"] == "png"

    def test_convert_to_webp(self, sample_image: bytes) -> None:
        """Should convert to WebP format."""
        enhancer = ImageEnhancer(output_format="webp")
        result = enhancer.enhance(sample_image)
        assert result["format"] == "webp"


class TestGetImageInfo:
    """Test get_image_info helper method."""

    @pytest.fixture
    def enhancer(self) -> ImageEnhancer:
        return ImageEnhancer()

    def test_get_image_info_returns_dimensions(self, enhancer: ImageEnhancer) -> None:
        """Should return image dimensions."""
        img = Image.new("RGB", (200, 150), color=(0, 0, 255))
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        image_data = buffer.getvalue()

        info = enhancer.get_image_info(image_data)

        assert info["width"] == 200
        assert info["height"] == 150

    def test_get_image_info_returns_format(self, enhancer: ImageEnhancer) -> None:
        """Should return image format."""
        img = Image.new("RGB", (100, 100))
        buffer = BytesIO()
        img.save(buffer, format="JPEG")
        image_data = buffer.getvalue()

        info = enhancer.get_image_info(image_data)
        assert info["format"] == "jpeg"

    def test_get_image_info_returns_mode(self, enhancer: ImageEnhancer) -> None:
        """Should return image mode."""
        img = Image.new("RGBA", (100, 100))
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        image_data = buffer.getvalue()

        info = enhancer.get_image_info(image_data)
        assert info["mode"] == "RGBA"

    def test_get_image_info_raises_on_invalid_data(self, enhancer: ImageEnhancer) -> None:
        """Should raise EnhancementError on invalid data."""
        with pytest.raises(EnhancementError):
            enhancer.get_image_info(b"not an image")


class TestCLAHEEnhancement:
    """Test CLAHE contrast enhancement."""

    @pytest.fixture
    def sample_image(self) -> bytes:
        """Create a sample image for testing."""
        img = Image.new("RGB", (100, 100), color=(128, 128, 128))
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

    def test_clahe_applied_when_enabled(self, sample_image: bytes) -> None:
        """Should apply CLAHE when enabled."""
        enhancer = ImageEnhancer(apply_clahe=True)
        result = enhancer.enhance(sample_image)
        assert result["data"] is not None

    def test_clahe_skipped_when_disabled(self, sample_image: bytes) -> None:
        """Should skip CLAHE when disabled."""
        enhancer = ImageEnhancer(apply_clahe=False)
        result = enhancer.enhance(sample_image)
        assert result["data"] is not None


class TestEXIFOrientation:
    """Test EXIF orientation handling."""

    @pytest.fixture
    def enhancer(self) -> ImageEnhancer:
        return ImageEnhancer()

    def test_handles_image_without_exif(self, enhancer: ImageEnhancer) -> None:
        """Should handle images without EXIF data."""
        img = Image.new("RGB", (100, 100))
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        image_data = buffer.getvalue()

        result = enhancer.enhance(image_data)
        assert result["data"] is not None

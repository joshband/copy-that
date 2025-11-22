# Image Validation & Error Handling Plan

[← Back to Index](./README.md) | [Previous: Async Loading Strategy](./03-async-loading-strategy.md)

---

## 4.1 python-magic File Type Detection

### Magic Byte Validation

```python
# src/copy_that/infrastructure/cv/validator.py

import magic
from enum import Enum

class ImageFormat(str, Enum):
    """Supported image formats"""
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"
    GIF = "gif"
    BMP = "bmp"
    TIFF = "tiff"
    HEIC = "heic"
    AVIF = "avif"

class MagicValidator:
    """Validate image format using magic bytes (libmagic)"""

    # Map MIME types to our formats
    MIME_TO_FORMAT = {
        "image/jpeg": ImageFormat.JPEG,
        "image/png": ImageFormat.PNG,
        "image/webp": ImageFormat.WEBP,
        "image/gif": ImageFormat.GIF,
        "image/bmp": ImageFormat.BMP,
        "image/tiff": ImageFormat.TIFF,
        "image/heic": ImageFormat.HEIC,
        "image/heif": ImageFormat.HEIC,
        "image/avif": ImageFormat.AVIF,
        # Variants
        "image/x-ms-bmp": ImageFormat.BMP,
        "image/x-tiff": ImageFormat.TIFF,
    }

    def __init__(self):
        self._magic = magic.Magic(mime=True)

    def detect_format(self, data: bytes) -> ImageFormat:
        """Detect image format from magic bytes"""

        # Only need first 2KB for detection
        mime_type = self._magic.from_buffer(data[:2048])

        if not mime_type.startswith("image/"):
            raise InvalidImageError(
                f"File is not an image: {mime_type}",
                detected_type=mime_type
            )

        format_ = self.MIME_TO_FORMAT.get(mime_type)
        if format_ is None:
            raise UnsupportedFormatError(
                f"Unsupported image format: {mime_type}",
                mime_type=mime_type
            )

        return format_

    def validate_extension_matches(
        self,
        data: bytes,
        filename: str
    ) -> None:
        """Ensure file extension matches actual content"""

        detected = self.detect_format(data)
        ext = Path(filename).suffix.lower().lstrip(".")

        # Map extensions to formats
        ext_map = {
            "jpg": ImageFormat.JPEG,
            "jpeg": ImageFormat.JPEG,
            "png": ImageFormat.PNG,
            "webp": ImageFormat.WEBP,
            "gif": ImageFormat.GIF,
            "bmp": ImageFormat.BMP,
            "tiff": ImageFormat.TIFF,
            "tif": ImageFormat.TIFF,
            "heic": ImageFormat.HEIC,
            "heif": ImageFormat.HEIC,
            "avif": ImageFormat.AVIF,
        }

        ext_format = ext_map.get(ext)

        if ext_format and ext_format != detected:
            raise FormatMismatchError(
                f"Extension .{ext} doesn't match content ({detected.value})",
                claimed=ext_format,
                actual=detected
            )
```

### Why Magic Bytes?

| Method | Pros | Cons |
|--------|------|------|
| **Extension-based** | Fast | Easily spoofed, unreliable |
| **Content-Type header** | Standard | Server can lie |
| **Magic bytes** | Accurate, secure | Requires libmagic |

---

## 4.2 Format Validation (Supported Formats)

### Format Capabilities

```python
class FormatValidator:
    """Validate image format compatibility"""

    FORMAT_CAPABILITIES = {
        ImageFormat.JPEG: {
            "max_dimensions": (65535, 65535),
            "supports_alpha": False,
            "supports_animation": False,
            "pillow_support": True,
            "opencv_support": True,
            "web_safe": True,
        },
        ImageFormat.PNG: {
            "max_dimensions": (2147483647, 2147483647),
            "supports_alpha": True,
            "supports_animation": True,  # APNG
            "pillow_support": True,
            "opencv_support": True,
            "web_safe": True,
        },
        ImageFormat.WEBP: {
            "max_dimensions": (16383, 16383),
            "supports_alpha": True,
            "supports_animation": True,
            "pillow_support": True,
            "opencv_support": True,  # OpenCV 4.x+
            "web_safe": True,
        },
        ImageFormat.GIF: {
            "max_dimensions": (65535, 65535),
            "supports_alpha": True,
            "supports_animation": True,
            "pillow_support": True,
            "opencv_support": False,  # Limited
            "web_safe": True,
        },
        ImageFormat.BMP: {
            "max_dimensions": (32767, 32767),
            "supports_alpha": False,
            "supports_animation": False,
            "pillow_support": True,
            "opencv_support": True,
            "web_safe": False,
        },
        ImageFormat.TIFF: {
            "max_dimensions": (2147483647, 2147483647),
            "supports_alpha": True,
            "supports_animation": False,
            "pillow_support": True,
            "opencv_support": True,
            "web_safe": False,
        },
        ImageFormat.HEIC: {
            "max_dimensions": (8192, 8192),
            "supports_alpha": True,
            "supports_animation": False,
            "pillow_support": False,  # Requires pillow-heif
            "opencv_support": False,
            "web_safe": False,
        },
        ImageFormat.AVIF: {
            "max_dimensions": (65535, 65535),
            "supports_alpha": True,
            "supports_animation": True,
            "pillow_support": False,  # Requires plugin
            "opencv_support": False,
            "web_safe": True,
        },
    }

    def __init__(self, config: ValidationConfig):
        self.config = config
        self.supported = set(
            ImageFormat(f) for f in config.supported_formats
        )

    def validate(
        self,
        format_: ImageFormat,
        dimensions: tuple[int, int]
    ) -> None:
        """Validate format is supported and within limits"""

        if format_ not in self.supported:
            supported_list = ", ".join(f.value for f in self.supported)
            raise UnsupportedFormatError(
                f"Format {format_.value} not supported. "
                f"Supported: {supported_list}"
            )

        caps = self.FORMAT_CAPABILITIES.get(format_, {})
        max_dims = caps.get("max_dimensions", (65535, 65535))

        if dimensions[0] > max_dims[0] or dimensions[1] > max_dims[1]:
            raise DimensionError(
                f"Dimensions {dimensions} exceed format limit {max_dims}"
            )

    def needs_conversion(self, format_: ImageFormat) -> bool:
        """Check if format needs conversion for processing"""
        caps = self.FORMAT_CAPABILITIES.get(format_, {})
        return not caps.get("opencv_support", False)
```

---

## 4.3 Size Limits and Enforcement

```python
class SizeValidator:
    """Validate image size constraints"""

    def __init__(self, config: SizeConfig):
        self.config = config

    def validate_file_size(self, data: bytes) -> None:
        """Enforce file size limit"""

        size_bytes = len(data)
        size_mb = size_bytes / (1024 * 1024)

        if size_mb > self.config.max_file_size_mb:
            raise FileTooLargeError(
                f"File size {size_mb:.1f}MB exceeds "
                f"limit of {self.config.max_file_size_mb}MB",
                actual_size_mb=size_mb,
                limit_mb=self.config.max_file_size_mb
            )

    def validate_dimensions(self, width: int, height: int) -> None:
        """Enforce dimension limits"""

        # Minimum dimensions
        if width < self.config.min_dimension:
            raise DimensionError(
                f"Image width {width}px is below minimum "
                f"{self.config.min_dimension}px"
            )
        if height < self.config.min_dimension:
            raise DimensionError(
                f"Image height {height}px is below minimum "
                f"{self.config.min_dimension}px"
            )

        # Maximum dimensions
        if width > self.config.max_dimension:
            raise DimensionError(
                f"Image width {width}px exceeds maximum "
                f"{self.config.max_dimension}px"
            )
        if height > self.config.max_dimension:
            raise DimensionError(
                f"Image height {height}px exceeds maximum "
                f"{self.config.max_dimension}px"
            )

        # Pixel count (memory protection)
        pixels = width * height
        max_pixels = self.config.max_megapixels * 1_000_000

        if pixels > max_pixels:
            actual_mp = pixels / 1_000_000
            raise DimensionError(
                f"Image {actual_mp:.1f}MP exceeds "
                f"limit of {self.config.max_megapixels}MP"
            )

    def validate_aspect_ratio(self, width: int, height: int) -> None:
        """Validate aspect ratio is reasonable"""

        ratio = max(width, height) / max(min(width, height), 1)

        if ratio > self.config.max_aspect_ratio:
            raise AspectRatioError(
                f"Aspect ratio {ratio:.1f}:1 exceeds "
                f"limit of {self.config.max_aspect_ratio}:1"
            )

class SizeConfig(BaseModel):
    """Size validation configuration"""
    max_file_size_mb: float = 20.0
    min_dimension: int = 10
    max_dimension: int = 16384
    max_megapixels: float = 100.0
    max_aspect_ratio: float = 20.0
```

### Recommended Limits

| Limit | Default | Rationale |
|-------|---------|-----------|
| Max file size | 20 MB | Reasonable for web uploads |
| Min dimension | 10 px | Too small = no useful data |
| Max dimension | 16384 px | Format limits, memory |
| Max megapixels | 100 MP | ~300MB uncompressed |
| Max aspect ratio | 20:1 | Prevent abuse |

---

## 4.4 Corrupt Image Detection

```python
from PIL import Image, UnidentifiedImageError
from PIL.Image import DecompressionBombError
import io

class IntegrityValidator:
    """Detect corrupt or truncated images"""

    def validate(self, data: bytes) -> ImageInfo:
        """
        Attempt to decode image and extract metadata.
        Raises CorruptImageError if decoding fails.
        """

        try:
            with Image.open(io.BytesIO(data)) as img:
                # Force decode to detect truncation
                img.load()

                # Verify image (checks for issues)
                img.verify()

                return ImageInfo(
                    width=img.width,
                    height=img.height,
                    format=img.format,
                    mode=img.mode,
                    is_animated=getattr(img, "is_animated", False),
                    n_frames=getattr(img, "n_frames", 1),
                )

        except UnidentifiedImageError as e:
            raise CorruptImageError(
                "Cannot identify image file - may be corrupt",
                original_error=str(e)
            )

        except DecompressionBombError as e:
            raise DimensionError(
                f"Image exceeds PIL safety limits: {e}",
                original_error=str(e)
            )

        except OSError as e:
            raise CorruptImageError(
                f"Failed to decode image: {e}",
                original_error=str(e)
            )

        except Exception as e:
            raise CorruptImageError(
                f"Unexpected error decoding image: {e}",
                original_error=str(e)
            )

    def check_truncation(self, data: bytes, format_: ImageFormat) -> None:
        """Check for common truncation patterns"""

        # JPEG should end with FFD9 (EOI marker)
        if format_ == ImageFormat.JPEG:
            if len(data) < 2:
                raise CorruptImageError("JPEG file too small")
            if not data.endswith(b"\xff\xd9"):
                # Check for common near-end patterns
                if b"\xff\xd9" not in data[-100:]:
                    raise CorruptImageError(
                        "JPEG appears truncated (missing EOI marker)"
                    )

        # PNG should end with IEND chunk
        elif format_ == ImageFormat.PNG:
            if b"IEND" not in data[-20:]:
                raise CorruptImageError(
                    "PNG appears truncated (missing IEND chunk)"
                )

        # GIF should end with trailer byte
        elif format_ == ImageFormat.GIF:
            if not data.endswith(b"\x3b"):
                raise CorruptImageError(
                    "GIF appears truncated (missing trailer)"
                )
```

---

## 4.5 Graceful Degradation Strategies

### Processing Result with Metadata

```python
@dataclass
class ProcessingResult:
    """Result of image processing with metadata"""
    image: ProcessedImage
    strategy_used: str
    degraded: bool
    warnings: list[str]
    processing_time_ms: float

class GracefulProcessor:
    """Process images with graceful degradation on failures"""

    async def process_with_fallbacks(
        self,
        source: ImageSource
    ) -> ProcessingResult:
        """Attempt processing with multiple fallback strategies"""

        strategies = [
            ("full", self._full_processing),
            ("reduced", self._reduced_processing),
            ("minimal", self._minimal_processing),
            ("passthrough", self._passthrough),
        ]

        errors = []
        start_time = time.monotonic()

        for name, strategy in strategies:
            try:
                result = await strategy(source)

                elapsed_ms = (time.monotonic() - start_time) * 1000

                if errors:
                    logger.warning(
                        f"Image processed with '{name}' strategy "
                        f"after {len(errors)} failures"
                    )

                return ProcessingResult(
                    image=result,
                    strategy_used=name,
                    degraded=name != "full",
                    warnings=[f"Fell back to {name}: {e}" for e in errors],
                    processing_time_ms=elapsed_ms,
                )

            except MemoryError:
                errors.append(f"{name}: Out of memory")
                gc.collect()
                continue

            except Exception as e:
                errors.append(f"{name}: {str(e)}")
                continue

        # All strategies failed
        raise ImageProcessingError(
            "All processing strategies failed",
            errors=errors,
            recoverable=False
        )

    async def _full_processing(self, source: ImageSource) -> ProcessedImage:
        """Full pipeline: load → validate → preprocess → optimize"""
        # All operations enabled
        pass

    async def _reduced_processing(self, source: ImageSource) -> ProcessedImage:
        """Reduced: load → validate → resize only"""
        # Skip enhancement, denoising
        pass

    async def _minimal_processing(self, source: ImageSource) -> ProcessedImage:
        """Minimal: aggressive resize (512px), no processing"""
        # 512px max, JPEG output
        pass

    async def _passthrough(self, source: ImageSource) -> ProcessedImage:
        """Just validate and return original"""
        # No processing, just validation
        pass
```

### Strategy Comparison

| Strategy | Max Dimension | Enhancement | Format | Use Case |
|----------|---------------|-------------|--------|----------|
| Full | 2048 | CLAHE | WebP | Normal |
| Reduced | 2048 | None | WebP | Memory pressure |
| Minimal | 512 | None | JPEG | Critical memory |
| Passthrough | Original | None | Original | Last resort |

---

## 4.6 Error Messages and User Feedback

### Exception Hierarchy

```python
# src/copy_that/infrastructure/cv/exceptions.py

from dataclasses import dataclass
from typing import Any

@dataclass
class ImageErrorContext:
    """Context information for error reporting"""
    source_type: str       # "url", "file", "base64"
    source_identifier: str # URL, path, or truncated hash
    stage: str             # "fetch", "validate", "preprocess", "optimize"
    details: dict[str, Any]

class ImageProcessingError(Exception):
    """Base exception for image processing errors"""

    def __init__(
        self,
        message: str,
        *,
        user_message: str | None = None,
        recoverable: bool = True,
        context: ImageErrorContext | None = None,
        suggestions: list[str] | None = None,
    ):
        super().__init__(message)
        self.user_message = user_message or message
        self.recoverable = recoverable
        self.context = context
        self.suggestions = suggestions or []

    def to_api_error(self) -> dict:
        """Convert to API error response format"""
        return {
            "error": self.__class__.__name__,
            "message": self.user_message,
            "recoverable": self.recoverable,
            "suggestions": self.suggestions,
        }
```

### Specific Exception Types

```python
class FileTooLargeError(ImageProcessingError):
    """File exceeds size limit"""

    def __init__(self, message: str, actual_size_mb: float, limit_mb: float):
        super().__init__(
            message,
            user_message=(
                f"Image is too large ({actual_size_mb:.1f}MB). "
                f"Maximum size is {limit_mb}MB."
            ),
            recoverable=False,
            suggestions=[
                "Compress the image before uploading",
                "Use a lower resolution version",
                "Convert to WebP format for smaller file sizes",
            ]
        )
        self.actual_size_mb = actual_size_mb
        self.limit_mb = limit_mb


class UnsupportedFormatError(ImageProcessingError):
    """Image format not supported"""

    def __init__(self, message: str, mime_type: str | None = None):
        super().__init__(
            message,
            user_message=f"Image format not supported: {mime_type or 'unknown'}",
            recoverable=False,
            suggestions=[
                "Convert to JPEG, PNG, or WebP format",
                "Supported formats: JPEG, PNG, WebP, GIF, BMP, TIFF",
            ]
        )
        self.mime_type = mime_type


class CorruptImageError(ImageProcessingError):
    """Image file is corrupt or incomplete"""

    def __init__(self, message: str, original_error: str | None = None):
        super().__init__(
            message,
            user_message="The image file appears to be corrupt or incomplete.",
            recoverable=False,
            suggestions=[
                "Try downloading or exporting the image again",
                "Open the image in an editor and re-save it",
                "Check that the file transfer completed successfully",
            ]
        )
        self.original_error = original_error


class DimensionError(ImageProcessingError):
    """Image dimensions invalid"""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            recoverable=False,
            suggestions=[
                "Resize the image to within acceptable limits",
                "Maximum dimensions: 16384x16384 pixels",
                "Maximum resolution: 100 megapixels",
            ],
            **kwargs
        )


class AspectRatioError(ImageProcessingError):
    """Image aspect ratio too extreme"""

    def __init__(self, message: str):
        super().__init__(
            message,
            recoverable=False,
            suggestions=[
                "Crop the image to a more standard aspect ratio",
                "Maximum aspect ratio is 20:1",
            ]
        )


class NetworkError(ImageProcessingError):
    """Network error fetching image"""

    def __init__(self, message: str, url: str | None = None):
        super().__init__(
            message,
            user_message="Failed to download image from URL.",
            recoverable=True,
            suggestions=[
                "Check that the URL is correct and accessible",
                "Ensure the image server allows external access",
                "Try uploading the image directly instead",
            ]
        )
        self.url = url


class InvalidURLError(ImageProcessingError):
    """URL validation failed"""

    def __init__(self, message: str):
        super().__init__(
            message,
            user_message="The provided URL is not valid.",
            recoverable=False,
            suggestions=[
                "Ensure the URL starts with http:// or https://",
                "Check for typos in the URL",
                "Private/internal URLs are not allowed",
            ]
        )


class InvalidPathError(ImageProcessingError):
    """File path validation failed"""

    def __init__(self, message: str):
        super().__init__(
            message,
            user_message="The provided file path is not valid.",
            recoverable=False,
            suggestions=[
                "Check that the file path is correct",
                "Ensure you have permission to access the file",
            ]
        )


class FormatMismatchError(ImageProcessingError):
    """File extension doesn't match content"""

    def __init__(self, message: str, claimed: ImageFormat, actual: ImageFormat):
        super().__init__(
            message,
            user_message=(
                f"File extension suggests {claimed.value} but content is "
                f"{actual.value}. Rename or re-export the file."
            ),
            recoverable=False,
            suggestions=[
                f"Rename the file with .{actual.value} extension",
                "Re-export the image from the original application",
            ]
        )
        self.claimed = claimed
        self.actual = actual
```

### API Error Response Format

```python
# Example API error response
{
    "error": "FileTooLargeError",
    "message": "Image is too large (25.3MB). Maximum size is 20MB.",
    "recoverable": false,
    "suggestions": [
        "Compress the image before uploading",
        "Use a lower resolution version",
        "Convert to WebP format for smaller file sizes"
    ]
}
```

---

## Summary

The validation and error handling plan provides:

1. **Magic Byte Detection:** Accurate format identification
2. **Comprehensive Validation:** Format, size, dimensions, integrity
3. **Clear Size Limits:** Configurable with sensible defaults
4. **Corruption Detection:** Multiple checks for truncated files
5. **Graceful Degradation:** Multiple fallback strategies
6. **User-Friendly Errors:** Actionable suggestions for each error type

---

[← Back to Index](./README.md) | [Next: Dependency Recommendations →](./05-dependency-recommendations.md)

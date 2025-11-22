# OpenCV Preprocessing Pipeline Design

[← Back to Index](./README.md) | [Previous: Current State Assessment](./01-current-state-assessment.md)

---

## 2.1 Architecture Diagram

```
                    ┌─────────────────────────────────────────┐
                    │        ImagePreprocessingPipeline       │
                    └─────────────────────────────────────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    ▼                   ▼                   ▼
            ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
            │   Loader     │   │  Validator   │   │ Preprocessor │
            └──────────────┘   └──────────────┘   └──────────────┘
                    │                   │                   │
            ┌───────┴───────┐   ┌───────┴───────┐   ┌───────┴───────┐
            │ URL Fetcher   │   │ Magic Check   │   │ Resize        │
            │ File Reader   │   │ Size Check    │   │ Normalize     │
            │ Base64 Decode │   │ Format Check  │   │ Color Space   │
            └───────────────┘   │ Corrupt Check │   │ Enhancement   │
                                └───────────────┘   └───────────────┘
                                                            │
                                                    ┌───────┴───────┐
                                                    │   Optimizer   │
                                                    └───────────────┘
                                                            │
                                                    ┌───────┴───────┐
                                                    │ Quality Assess│
                                                    │ Format Convert│
                                                    │ Compress      │
                                                    └───────────────┘
```

---

## 2.2 Module Structure

```
src/copy_that/infrastructure/cv/
├── __init__.py               # Public API exports
├── preprocessing.py          # Main pipeline orchestrator
├── loader.py                 # Async image loading
├── validator.py              # Image validation
├── preprocessor.py           # OpenCV operations
├── optimizer.py              # Compression & format conversion
├── exceptions.py             # Custom exceptions
└── config.py                 # Pipeline configuration
```

### Module Responsibilities

| Module | Responsibility | Key Classes |
|--------|----------------|-------------|
| `preprocessing.py` | Pipeline orchestration, error recovery | `ImagePreprocessingPipeline` |
| `loader.py` | Async I/O (URL, file, base64) | `AsyncImageFetcher`, `AsyncFileLoader` |
| `validator.py` | Format, size, integrity checks | `MagicValidator`, `SizeValidator`, `IntegrityValidator` |
| `preprocessor.py` | OpenCV operations | `ImagePreprocessor` |
| `optimizer.py` | Format conversion, compression | `ImageOptimizer` |
| `exceptions.py` | Custom error types | See [Validation & Error Handling](./04-validation-error-handling.md) |
| `config.py` | Pydantic configuration | `PreprocessingConfig` |

---

## 2.3 Preprocessing Steps

### Step 1: Image Loading (Priority: High)

```python
class ImageLoader:
    async def load_from_url(self, url: str) -> ImageData:
        """
        Async fetch with httpx
        - SSRF protection
        - Size limit during download
        - Progress tracking
        Returns raw bytes + metadata
        """

    async def load_from_file(self, path: Path) -> ImageData:
        """
        Async file read with aiofiles
        - Path traversal protection
        - Size validation
        """

    async def load_from_base64(self, data: str, media_type: str) -> ImageData:
        """
        Decode base64 in thread pool to avoid blocking
        - Validate media type
        - Size check after decode
        """
```

### Step 2: Validation (Priority: Critical)

```python
class ImageValidator:
    def validate_magic_bytes(self, data: bytes) -> ImageFormat:
        """Use python-magic to detect actual file type"""

    def validate_dimensions(self, img: Image) -> None:
        """Check min/max dimensions"""

    def validate_file_size(self, data: bytes) -> None:
        """Enforce size limits (e.g., 20MB max)"""

    def validate_integrity(self, data: bytes) -> None:
        """Verify image can be decoded without errors"""
```

### Step 3: Preprocessing Operations (Priority: High)

| Operation | Purpose | OpenCV Function | Default Config |
|-----------|---------|-----------------|----------------|
| **Resize** | Fit API limits, reduce memory | `cv2.resize()` | Max 2048x2048 |
| **Color Space** | Normalize to RGB | `cv2.cvtColor()` | BGR→RGB |
| **Denoise** | Improve extraction quality | `cv2.fastNlMeansDenoisingColored()` | Optional (off) |
| **Contrast** | Enhance visibility | `cv2.convertScaleAbs()` | CLAHE |
| **Sharpen** | Improve edge detection | `cv2.filter2D()` | Optional (off) |
| **Auto-Orient** | Fix EXIF rotation | Custom | Always on |

```python
class ImagePreprocessor:
    def resize_for_api(self, img: np.ndarray, max_size: int = 2048) -> np.ndarray:
        """
        Resize maintaining aspect ratio
        - Use INTER_LANCZOS4 for quality downscaling
        - Use INTER_CUBIC for upscaling (rare)
        """

    def normalize_color_space(self, img: np.ndarray) -> np.ndarray:
        """
        Convert to RGB
        - Handle BGR (OpenCV default)
        - Handle grayscale (convert to 3-channel)
        - Handle RGBA (remove or preserve alpha)
        """

    def enhance_for_extraction(self, img: np.ndarray) -> np.ndarray:
        """
        Apply CLAHE contrast enhancement
        - Convert to LAB color space
        - Apply CLAHE to L channel
        - Convert back to RGB
        """

    def auto_orient(self, img: np.ndarray, exif: dict) -> np.ndarray:
        """
        Apply EXIF orientation correction
        - Read orientation tag
        - Apply rotation/flip
        - Strip orientation tag after
        """
```

### Step 4: Optimization (Priority: Medium)

```python
class ImageOptimizer:
    def compress_for_api(self, img: np.ndarray, target_kb: int = 500) -> bytes:
        """
        Progressive compression to target size
        - Start at quality 95
        - Reduce quality until size target met
        - Stop at quality 50 (minimum)
        """

    def convert_format(self, data: bytes, target: ImageFormat) -> bytes:
        """
        Convert to optimal format
        - WebP recommended for size/quality ratio
        - JPEG for maximum compatibility
        - PNG for lossless/transparency
        """

    def strip_metadata(self, data: bytes) -> bytes:
        """
        Remove EXIF for privacy
        - Keep orientation (applied already)
        - Remove GPS, camera info, etc.
        """
```

---

## 2.4 Pipeline Configuration Strategy

```python
# src/copy_that/infrastructure/cv/config.py

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

class PreprocessingConfig(BaseSettings):
    """Pipeline configuration with environment overrides"""

    # Size limits
    max_file_size_mb: float = Field(default=20.0)
    max_dimension: int = Field(default=4096)
    target_dimension: int = Field(default=2048)
    min_dimension: int = Field(default=10)

    # Quality settings
    jpeg_quality: int = Field(default=85, ge=1, le=100)
    webp_quality: int = Field(default=80, ge=1, le=100)
    target_size_kb: int = Field(default=500)

    # Processing flags
    enable_denoising: bool = Field(default=False)
    enable_enhancement: bool = Field(default=True)
    strip_metadata: bool = Field(default=True)
    auto_orient: bool = Field(default=True)

    # Supported formats
    supported_formats: list[str] = [
        "jpeg", "png", "webp", "gif", "bmp", "tiff"
    ]
    output_format: str = Field(default="webp")

    # Memory limits (for Cloud Run)
    max_concurrent_ops: int = Field(default=4)
    chunk_size_kb: int = Field(default=64)
    max_memory_mb: int = Field(default=512)

    class Config:
        env_prefix = "CV_"

# Load configuration
preprocessing_config = PreprocessingConfig()
```

### Configuration Profiles

```python
# Development profile
DEV_CONFIG = PreprocessingConfig(
    max_file_size_mb=50.0,
    max_dimension=8192,
    max_concurrent_ops=8,
    enable_denoising=True,
)

# Production profile (Cloud Run 1GB)
PROD_CONFIG = PreprocessingConfig(
    max_file_size_mb=20.0,
    max_dimension=4096,
    target_dimension=2048,
    max_concurrent_ops=4,
    enable_denoising=False,
)

# Resource-constrained profile (Cloud Run 512MB)
MINIMAL_CONFIG = PreprocessingConfig(
    max_file_size_mb=10.0,
    max_dimension=2048,
    target_dimension=1024,
    max_concurrent_ops=2,
    enable_denoising=False,
    enable_enhancement=False,
)
```

---

## 2.5 Memory Optimization for Cloud Run

Cloud Run instances have limited memory (256MB-32GB). Key strategies:

### Memory Usage Estimation

```python
def estimate_memory_usage(width: int, height: int, channels: int = 3) -> int:
    """
    Estimate memory needed for image array

    Formula: width × height × channels × dtype_size

    Example: 4000x3000 RGB image
    = 4000 × 3000 × 3 × 1 (uint8)
    = 36,000,000 bytes
    = 34.3 MB per copy

    With processing copies: ~100-150MB peak
    """
    return width * height * channels * 1  # uint8 = 1 byte
```

### Memory-Efficient Processing Strategies

| Strategy | Description | Impact |
|----------|-------------|--------|
| **Lazy Loading** | Don't decode until needed | Reduces idle memory |
| **Streaming Decode** | Use Pillow's lazy loading | Reduces peak memory |
| **Early Downscale** | Resize before full decode if possible | Significant reduction |
| **Explicit Cleanup** | `del` arrays and `gc.collect()` | Prevents accumulation |
| **Thread Pool Sizing** | Limit concurrent OpenCV ops | Controls peak usage |
| **Format Selection** | Prefer WebP (smaller decoded) | Modest reduction |

### Memory-Efficient Processor Implementation

```python
class MemoryEfficientProcessor:
    """Process images with minimal memory footprint"""

    def __init__(self, max_memory_mb: int = 512):
        self.max_memory_mb = max_memory_mb

    async def process_streaming(self, source: ImageSource) -> AsyncIterator[bytes]:
        """Stream processing for large images"""
        # 1. Load in chunks (for very large files)
        # 2. Process incrementally
        # 3. Yield results immediately
        # 4. Release memory after each step

    def should_downscale_early(self, width: int, height: int) -> bool:
        """Check if image needs early downscaling for memory"""
        estimated_mb = self.estimate_memory_usage(width, height) / (1024 * 1024)
        # Use 50% threshold to leave room for processing
        return estimated_mb > (self.max_memory_mb * 0.5)

    def get_early_downscale_factor(self, width: int, height: int) -> float:
        """Calculate downscale factor to fit in memory"""
        target_pixels = (self.max_memory_mb * 0.3 * 1024 * 1024) / 3
        current_pixels = width * height
        if current_pixels <= target_pixels:
            return 1.0
        return (target_pixels / current_pixels) ** 0.5
```

### Cloud Run Recommendations

| Memory Tier | Recommended Config |
|-------------|-------------------|
| 256MB | Not recommended for image processing |
| 512MB | `MINIMAL_CONFIG`, max 2MP images |
| 1GB | `PROD_CONFIG`, max 16MP images |
| 2GB+ | `DEV_CONFIG`, up to 64MP images |

---

## 2.6 Error Recovery Patterns

### Graceful Degradation Pipeline

```python
class PreprocessingPipeline:
    """Main pipeline with comprehensive error recovery"""

    async def process(self, source: ImageSource) -> ProcessedImage:
        """Process image with fallback strategies"""

        strategies = [
            ("full", self._full_preprocess),
            ("reduced", self._reduced_preprocess),
            ("minimal", self._minimal_preprocess),
            ("passthrough", self._passthrough),
        ]

        errors = []

        for name, strategy in strategies:
            try:
                result = await strategy(source)

                if errors:
                    logger.warning(
                        f"Image processed with '{name}' strategy "
                        f"after {len(errors)} failures: {errors}"
                    )

                return ProcessingResult(
                    image=result,
                    strategy_used=name,
                    degraded=name != "full",
                    warnings=errors,
                )

            except MemoryError:
                errors.append(f"{name}: Out of memory")
                gc.collect()  # Try to free memory before retry
                continue

            except Exception as e:
                errors.append(f"{name}: {e}")
                continue

        # All strategies failed
        raise ImageProcessingError(
            "All processing strategies failed",
            errors=errors,
            recoverable=False
        )
```

### Strategy Definitions

| Strategy | Operations | Use Case |
|----------|------------|----------|
| **Full** | Load → Validate → Resize → Enhance → Optimize | Normal operation |
| **Reduced** | Load → Validate → Resize → Optimize | Memory pressure |
| **Minimal** | Load → Validate → Aggressive resize (512px) | Critical memory |
| **Passthrough** | Load → Validate only | Last resort |

### Retry Logic for Transient Failures

```python
async def fetch_with_retry(
    self,
    url: str,
    max_retries: int = 3,
    backoff_base: float = 1.0
) -> bytes:
    """Fetch URL with exponential backoff retry"""

    last_error = None

    for attempt in range(max_retries):
        try:
            return await self._fetch(url)

        except (httpx.TimeoutException, httpx.NetworkError) as e:
            last_error = e
            if attempt < max_retries - 1:
                delay = backoff_base * (2 ** attempt)
                logger.warning(
                    f"Fetch failed (attempt {attempt + 1}), "
                    f"retrying in {delay}s: {e}"
                )
                await asyncio.sleep(delay)

        except httpx.HTTPStatusError as e:
            # Only retry on specific status codes
            if e.response.status_code in (429, 500, 502, 503, 504):
                last_error = e
                if attempt < max_retries - 1:
                    delay = backoff_base * (2 ** attempt)
                    await asyncio.sleep(delay)
            else:
                raise

    raise NetworkError(f"Failed after {max_retries} attempts: {last_error}")
```

---

## 2.7 Pipeline Flow Example

```python
# Example usage of the complete pipeline

async def process_image_for_extraction(url: str) -> ProcessedImage:
    """Complete flow from URL to optimized image"""

    # 1. Create pipeline with configuration
    config = PreprocessingConfig()
    pipeline = ImagePreprocessingPipeline(config)

    # 2. Create source
    source = ImageSource.from_url(url)

    # 3. Process (handles all steps internally)
    result = await pipeline.process(source)

    # 4. Result contains:
    # - result.data: Optimized image bytes
    # - result.format: Output format (e.g., "webp")
    # - result.dimensions: (width, height)
    # - result.original_size: Original file size
    # - result.optimized_size: Final file size
    # - result.strategy_used: Which strategy succeeded
    # - result.warnings: Any degradation warnings

    return result
```

---

## Summary

The OpenCV preprocessing pipeline provides:

1. **Modular Architecture:** Separate concerns into distinct modules
2. **Configurable Operations:** Environment-based configuration
3. **Memory Safety:** Strategies for Cloud Run constraints
4. **Error Recovery:** Graceful degradation with multiple fallbacks
5. **Quality Optimization:** Balanced size/quality for AI APIs

---

[← Back to Index](./README.md) | [Next: Async Loading Strategy →](./03-async-loading-strategy.md)

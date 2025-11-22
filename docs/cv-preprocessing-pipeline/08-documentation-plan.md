# Documentation Plan

[← Back to Index](./README.md) | [Previous: Implementation Roadmap](./07-implementation-roadmap.md)

---

## Overview

This plan outlines the documentation to be created for the CV preprocessing pipeline, ensuring comprehensive coverage for developers, operators, and troubleshooters.

---

## 8.1 API Documentation for New Modules

**Location:** `docs/api/image-processing.md`

### Content Structure

```markdown
# Image Processing API Reference

## Table of Contents
1. [Pipeline Classes](#pipeline-classes)
2. [Configuration](#configuration)
3. [Exceptions](#exceptions)
4. [Data Types](#data-types)

## Pipeline Classes

### ImagePreprocessingPipeline

Main entry point for image preprocessing.

#### Constructor

```python
pipeline = ImagePreprocessingPipeline(config: PreprocessingConfig = None)
```

**Parameters:**
- `config`: PreprocessingConfig | None - Pipeline configuration. Uses defaults if None.

#### Methods

##### process(source: ImageSource) -> ProcessedImage

Process a single image through the pipeline.

**Parameters:**
- `source`: ImageSource - Image source (URL, file, or base64)

**Returns:**
- ProcessedImage with processed bytes and metadata

**Raises:**
- FileTooLargeError: File exceeds size limit
- UnsupportedFormatError: Format not supported
- CorruptImageError: Image is corrupt/truncated
- NetworkError: Failed to fetch URL
- InvalidURLError: URL validation failed
- DimensionError: Dimensions invalid

**Example:**

```python
from copy_that.infrastructure.cv import (
    ImagePreprocessingPipeline,
    ImageSource,
)

pipeline = ImagePreprocessingPipeline()

# From URL
result = await pipeline.process(
    ImageSource.from_url("https://example.com/image.jpg")
)

# From file
result = await pipeline.process(
    ImageSource.from_file(Path("/path/to/image.png"))
)

# From base64
result = await pipeline.process(
    ImageSource.from_base64(data, "image/jpeg")
)

print(f"Processed: {result.dimensions}, {result.optimized_size} bytes")
```

---

### ConcurrentImageProcessor

Process multiple images concurrently with controlled parallelism.

#### Constructor

```python
processor = ConcurrentImageProcessor(max_concurrent: int = 4)
```

**Parameters:**
- `max_concurrent`: int - Maximum concurrent operations

#### Methods

##### process_batch(sources, progress_callback) -> list[ProcessedImage | Exception]

Process multiple images concurrently.

**Parameters:**
- `sources`: list[ImageSource] - List of image sources
- `progress_callback`: Callable[[int, int], Awaitable[None]] | None

**Returns:**
- List of ProcessedImage or Exception for each source

**Example:**

```python
processor = ConcurrentImageProcessor(max_concurrent=4)

sources = [
    ImageSource.from_url(url) for url in urls
]

async def on_progress(completed: int, total: int):
    print(f"Progress: {completed}/{total}")

results = await processor.process_batch(sources, on_progress)

for i, result in enumerate(results):
    if isinstance(result, Exception):
        print(f"Failed {i}: {result}")
    else:
        print(f"Processed {i}: {result.dimensions}")
```

---

## Configuration

### PreprocessingConfig

Pipeline configuration with environment variable support.

```python
from copy_that.infrastructure.cv import PreprocessingConfig

config = PreprocessingConfig(
    # Size limits
    max_file_size_mb=20.0,
    max_dimension=4096,
    target_dimension=2048,
    min_dimension=10,
    max_megapixels=100.0,
    max_aspect_ratio=20.0,

    # Quality
    jpeg_quality=85,
    webp_quality=80,
    target_size_kb=500,

    # Processing
    enable_denoising=False,
    enable_enhancement=True,
    strip_metadata=True,
    auto_orient=True,

    # Output
    supported_formats=["jpeg", "png", "webp", "gif", "bmp", "tiff"],
    output_format="webp",

    # Performance
    max_concurrent_ops=4,
)
```

### Environment Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| CV_MAX_FILE_SIZE_MB | float | 20.0 | Maximum file size in MB |
| CV_MAX_DIMENSION | int | 4096 | Maximum input dimension |
| CV_TARGET_DIMENSION | int | 2048 | Target output dimension |
| CV_MIN_DIMENSION | int | 10 | Minimum dimension |
| CV_MAX_MEGAPIXELS | float | 100.0 | Maximum megapixels |
| CV_JPEG_QUALITY | int | 85 | JPEG output quality |
| CV_WEBP_QUALITY | int | 80 | WebP output quality |
| CV_ENABLE_DENOISING | bool | false | Enable denoising |
| CV_ENABLE_ENHANCEMENT | bool | true | Enable CLAHE enhancement |
| CV_OUTPUT_FORMAT | str | webp | Output format |
| CV_MAX_CONCURRENT | int | 4 | Max concurrent operations |

---

## Exceptions

### Hierarchy

```
ImageProcessingError (base)
├── FileTooLargeError
├── UnsupportedFormatError
├── CorruptImageError
├── DimensionError
├── AspectRatioError
├── NetworkError
├── InvalidURLError
├── InvalidPathError
└── FormatMismatchError
```

### Exception Details

#### ImageProcessingError

Base exception with user-friendly messages.

**Attributes:**
- `message`: str - Technical message
- `user_message`: str - User-friendly message
- `recoverable`: bool - Whether retry might help
- `suggestions`: list[str] - Actionable suggestions

**Methods:**
- `to_api_error()`: Convert to API response format

---

## Data Types

### ImageSource

```python
@dataclass
class ImageSource:
    source_type: Literal["url", "file", "base64"]
    url: str | None
    path: Path | None
    data: str | None
    media_type: str | None

    @classmethod
    def from_url(cls, url: str) -> ImageSource
    @classmethod
    def from_file(cls, path: Path) -> ImageSource
    @classmethod
    def from_base64(cls, data: str, media_type: str) -> ImageSource
```

### ProcessedImage

```python
@dataclass
class ProcessedImage:
    data: bytes                    # Processed image bytes
    format: str                    # Output format (webp, jpeg, etc.)
    dimensions: tuple[int, int]    # (width, height)
    original_size: int             # Original file size
    optimized_size: int            # Final file size
    strategy_used: str             # Processing strategy
    degraded: bool                 # Whether fallback was used
    warnings: list[str]            # Any warnings
    processing_time_ms: float      # Processing duration
```
```

---

## 8.2 Code Examples for Common Use Cases

**Location:** `docs/examples/image-processing-examples.md`

### Content Structure

```markdown
# Image Processing Examples

## Basic Usage

### Single Image Processing

```python
from copy_that.infrastructure.cv import (
    ImagePreprocessingPipeline,
    ImageSource,
    PreprocessingConfig,
)

async def process_image_url(url: str) -> bytes:
    """Process image from URL"""
    pipeline = ImagePreprocessingPipeline()
    result = await pipeline.process(ImageSource.from_url(url))
    return result.data

# Usage
image_data = await process_image_url("https://example.com/photo.jpg")
```

### Batch Processing with Progress

```python
from copy_that.infrastructure.cv import ConcurrentImageProcessor, ImageSource

async def process_batch_with_progress(urls: list[str]) -> list[bytes]:
    """Process multiple images with progress tracking"""

    processor = ConcurrentImageProcessor(max_concurrent=4)
    sources = [ImageSource.from_url(url) for url in urls]

    async def on_progress(completed: int, total: int):
        percentage = (completed / total) * 100
        print(f"\rProcessing: {percentage:.0f}% ({completed}/{total})", end="")

    results = await processor.process_batch(sources, on_progress)
    print()  # New line after progress

    # Filter successful results
    return [r.data for r in results if not isinstance(r, Exception)]
```

---

## Integration with Color Extraction

### Preprocessing Before AI Extraction

```python
from copy_that.application.services import ImageService
from copy_that.application import AIColorExtractor

async def extract_colors_optimized(image_url: str) -> list[ColorToken]:
    """Extract colors with preprocessing optimization"""

    # Step 1: Preprocess image
    service = ImageService()
    processed = await service.preprocess_for_extraction(image_url)

    # Step 2: Get base64 for API
    base64_data, media_type = service.get_base64_for_api(processed)

    # Step 3: Extract colors from optimized image
    extractor = AIColorExtractor()
    colors = extractor.extract_colors_from_base64(
        base64_data,
        media_type,
        max_colors=10
    )

    return colors
```

### Batch Color Extraction

```python
async def batch_extract_colors(image_urls: list[str]) -> dict[str, list]:
    """Extract colors from multiple images"""

    service = ImageService()
    extractor = AIColorExtractor()

    # Preprocess all images
    processed_images = await service.preprocess_batch(image_urls)

    # Extract colors from each
    results = {}
    for url, processed in zip(image_urls, processed_images):
        try:
            base64_data, media_type = service.get_base64_for_api(processed)
            colors = extractor.extract_colors_from_base64(
                base64_data, media_type
            )
            results[url] = colors
        except Exception as e:
            results[url] = {"error": str(e)}

    return results
```

---

## Error Handling

### Comprehensive Error Handling

```python
from copy_that.infrastructure.cv import (
    ImagePreprocessingPipeline,
    ImageSource,
    FileTooLargeError,
    UnsupportedFormatError,
    CorruptImageError,
    NetworkError,
    InvalidURLError,
    DimensionError,
)

async def safe_process_image(url: str) -> dict:
    """Process image with comprehensive error handling"""

    pipeline = ImagePreprocessingPipeline()
    source = ImageSource.from_url(url)

    try:
        result = await pipeline.process(source)
        return {
            "success": True,
            "size": result.optimized_size,
            "dimensions": result.dimensions,
            "format": result.format,
        }

    except FileTooLargeError as e:
        return {
            "success": False,
            "error": "file_too_large",
            "message": e.user_message,
            "suggestions": e.suggestions,
        }

    except UnsupportedFormatError as e:
        return {
            "success": False,
            "error": "unsupported_format",
            "message": e.user_message,
            "suggestions": e.suggestions,
        }

    except CorruptImageError as e:
        return {
            "success": False,
            "error": "corrupt_image",
            "message": e.user_message,
            "suggestions": e.suggestions,
        }

    except NetworkError as e:
        return {
            "success": False,
            "error": "network_error",
            "message": e.user_message,
            "recoverable": True,
        }

    except InvalidURLError as e:
        return {
            "success": False,
            "error": "invalid_url",
            "message": e.user_message,
        }

    except DimensionError as e:
        return {
            "success": False,
            "error": "dimension_error",
            "message": e.user_message,
            "suggestions": e.suggestions,
        }
```

### FastAPI Endpoint Integration

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class ProcessImageRequest(BaseModel):
    image_url: str

class ProcessImageResponse(BaseModel):
    size: int
    width: int
    height: int
    format: str

@router.post("/process-image", response_model=ProcessImageResponse)
async def process_image_endpoint(request: ProcessImageRequest):
    """Process image and return metadata"""

    pipeline = ImagePreprocessingPipeline()

    try:
        result = await pipeline.process(
            ImageSource.from_url(request.image_url)
        )

        return ProcessImageResponse(
            size=result.optimized_size,
            width=result.dimensions[0],
            height=result.dimensions[1],
            format=result.format,
        )

    except ImageProcessingError as e:
        raise HTTPException(
            status_code=400,
            detail=e.to_api_error()
        )
```

---

## Custom Configuration

### Memory-Constrained Environment

```python
from copy_that.infrastructure.cv import (
    PreprocessingConfig,
    ImagePreprocessingPipeline,
)

# Configuration for 512MB Cloud Run instance
config = PreprocessingConfig(
    max_file_size_mb=10.0,        # Smaller files
    target_dimension=1024,         # Smaller output
    max_dimension=4096,            # Reject very large
    max_megapixels=30.0,           # Lower MP limit
    max_concurrent_ops=2,          # Less parallelism
    enable_denoising=False,        # Skip expensive ops
    enable_enhancement=False,      # Skip CLAHE
    output_format="jpeg",          # JPEG is lighter
    jpeg_quality=75,               # Lower quality
)

pipeline = ImagePreprocessingPipeline(config)
```

### High-Quality Processing

```python
# Configuration for quality-focused processing
config = PreprocessingConfig(
    max_file_size_mb=50.0,         # Allow larger files
    target_dimension=4096,          # Higher resolution
    max_dimension=16384,            # Support large images
    max_megapixels=100.0,           # Higher MP limit
    enable_denoising=True,          # Enable denoising
    enable_enhancement=True,        # Enable CLAHE
    output_format="png",            # Lossless
)
```
```

---

## 8.3 Troubleshooting Guide for Image Issues

**Location:** `docs/troubleshooting/image-processing.md`

### Content Structure

```markdown
# Image Processing Troubleshooting Guide

## Common Errors

### FileTooLargeError

**Error Message:**
```
Image is too large (25.3MB). Maximum size is 20MB.
```

**Causes:**
- Image file exceeds configured size limit
- Uncompressed BMP or TIFF files

**Solutions:**
1. Compress image before uploading
2. Use lower resolution
3. Convert to WebP format
4. Increase `CV_MAX_FILE_SIZE_MB` if appropriate

**Configuration:**
```bash
# Increase limit
export CV_MAX_FILE_SIZE_MB=50
```

---

### UnsupportedFormatError

**Error Message:**
```
Image format not supported: application/pdf
```

**Causes:**
- File is not a supported image format
- File extension doesn't match content
- Trying to process PDF, SVG, or other non-raster formats

**Solutions:**
1. Convert to supported format (JPEG, PNG, WebP)
2. Verify file is actually an image
3. Check for renamed file extensions

**Supported Formats:**
- JPEG (.jpg, .jpeg)
- PNG (.png)
- WebP (.webp)
- GIF (.gif)
- BMP (.bmp)
- TIFF (.tiff, .tif)

---

### CorruptImageError

**Error Messages:**
```
JPEG appears truncated (missing EOI marker)
Cannot identify image file - may be corrupt
```

**Causes:**
- Incomplete file download
- File corrupted during transfer
- Intentionally malformed file

**Solutions:**
1. Re-download the image
2. Open in image editor and re-save
3. Check network stability
4. Verify source file integrity

**Verification:**
```bash
# Check file with ImageMagick
identify -verbose image.jpg

# Check with file command
file image.jpg
```

---

### NetworkError

**Error Message:**
```
Failed to download image from URL.
```

**Causes:**
- Source server unavailable
- Timeout during download
- DNS resolution failed
- SSL certificate issues

**Solutions:**
1. Check URL is accessible
2. Verify server allows external access
3. Try uploading file directly
4. Check for rate limiting

**Debugging:**
```bash
# Test URL accessibility
curl -I "https://example.com/image.jpg"

# Check with timeout
curl --max-time 30 -o /dev/null "https://example.com/image.jpg"
```

---

### MemoryError

**Error Message:**
```
Memory error during image processing
```

**Causes:**
- Image dimensions too large
- Too many concurrent operations
- Memory leak
- Cloud Run instance undersized

**Solutions:**
1. Increase Cloud Run memory
2. Reduce `CV_MAX_DIMENSION`
3. Reduce `CV_MAX_CONCURRENT`
4. Lower `CV_MAX_MEGAPIXELS`

**Memory Sizing:**
| Image Size | Recommended Memory |
|------------|-------------------|
| Up to 8MP | 512MB |
| Up to 16MP | 1GB |
| Up to 64MP | 2GB |
| Up to 100MP | 4GB |

---

## Debugging Tips

### Enable Debug Logging

```python
import logging

# Enable debug logging for image processing
logging.getLogger("copy_that.infrastructure.cv").setLevel(logging.DEBUG)

# More verbose
logging.basicConfig(level=logging.DEBUG)
```

### Check Image Properties

```python
from copy_that.infrastructure.cv import ImageValidator

validator = ImageValidator()

# Read and validate image
with open("image.jpg", "rb") as f:
    data = f.read()

info = validator.validate(data)
print(f"Format: {info.format}")
print(f"Dimensions: {info.width}x{info.height}")
print(f"Mode: {info.mode}")
print(f"Animated: {info.is_animated}")
print(f"Frames: {info.n_frames}")
```

### Check Configuration

```python
from copy_that.infrastructure.cv import PreprocessingConfig

config = PreprocessingConfig()

print(f"Max file size: {config.max_file_size_mb}MB")
print(f"Max dimension: {config.max_dimension}px")
print(f"Target dimension: {config.target_dimension}px")
print(f"Output format: {config.output_format}")
print(f"Enhancement: {config.enable_enhancement}")
```

### Memory Profiling

```bash
# Install memory profiler
pip install memory-profiler

# Run with memory profiling
python -m memory_profiler your_script.py
```

```python
# Profile specific function
from memory_profiler import profile

@profile
async def process_image(url: str):
    pipeline = ImagePreprocessingPipeline()
    return await pipeline.process(ImageSource.from_url(url))
```

---

## Logs to Check

### Application Logs

```bash
# Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision" --limit=100

# Filter for image processing
gcloud logging read 'textPayload:"image processing"' --limit=50
```

### Key Log Patterns

```
# Successful processing
INFO - Processed image: 2048x1536, 450KB -> 120KB WebP

# Degraded processing
WARNING - Image processed with 'reduced' strategy after 1 failures

# Validation failure
ERROR - Validation failed: File size 25.3MB exceeds limit of 20MB

# Network error
ERROR - Failed to fetch https://example.com/image.jpg: Connection timeout
```
```

---

## 8.4 Performance Tuning Guide

**Location:** `docs/performance/image-processing-tuning.md`

### Content Structure

```markdown
# Image Processing Performance Tuning Guide

## Quick Wins

### 1. Use WebP Output Format

WebP provides 25-34% smaller files than JPEG at equivalent quality.

```bash
export CV_OUTPUT_FORMAT=webp
export CV_WEBP_QUALITY=80
```

### 2. Optimize Concurrency

Match concurrent operations to available resources.

```bash
# For 2 vCPU Cloud Run instance
export CV_MAX_CONCURRENT=4  # 2x cores for I/O-bound work

# For memory-constrained
export CV_MAX_CONCURRENT=2
```

### 3. Right-Size Target Dimensions

Smaller output = faster processing and smaller payloads.

```bash
# For thumbnails
export CV_TARGET_DIMENSION=512

# For standard processing
export CV_TARGET_DIMENSION=2048

# For high-quality
export CV_TARGET_DIMENSION=4096
```

---

## Configuration Profiles

### Development (Local Machine)

```bash
export CV_MAX_FILE_SIZE_MB=50
export CV_MAX_DIMENSION=8192
export CV_TARGET_DIMENSION=2048
export CV_MAX_CONCURRENT=8
export CV_ENABLE_DENOISING=true
export CV_ENABLE_ENHANCEMENT=true
```

### Production (Cloud Run 1GB)

```bash
export CV_MAX_FILE_SIZE_MB=20
export CV_MAX_DIMENSION=4096
export CV_TARGET_DIMENSION=2048
export CV_MAX_CONCURRENT=4
export CV_ENABLE_DENOISING=false
export CV_ENABLE_ENHANCEMENT=true
```

### Production (Cloud Run 512MB)

```bash
export CV_MAX_FILE_SIZE_MB=10
export CV_MAX_DIMENSION=2048
export CV_TARGET_DIMENSION=1024
export CV_MAX_CONCURRENT=2
export CV_ENABLE_DENOISING=false
export CV_ENABLE_ENHANCEMENT=false
export CV_OUTPUT_FORMAT=jpeg
export CV_JPEG_QUALITY=75
```

---

## Benchmarks

### Typical Processing Times

| Operation | Time (avg) | Memory | Notes |
|-----------|------------|--------|-------|
| URL fetch (1MB) | 200ms | 1MB | Network dependent |
| Format detection | 1ms | 2KB | Magic bytes only |
| Full validation | 50ms | Image size | Includes decode |
| Resize (4K→2K) | 80ms | 2x image | LANCZOS4 |
| CLAHE enhancement | 120ms | 2x image | LAB conversion |
| WebP encode | 60ms | 1x image | Quality 80 |
| **Total pipeline** | **500ms** | **3-4x image** | Typical flow |

### Throughput by Configuration

| Config | Images/sec | Notes |
|--------|------------|-------|
| Full pipeline, 1 concurrent | 2 | Baseline |
| Full pipeline, 4 concurrent | 6 | Standard |
| Reduced pipeline, 4 concurrent | 10 | No enhancement |
| Minimal pipeline, 4 concurrent | 20 | Resize only |

### Memory Usage

| Image Size | Peak Memory | Recommended RAM |
|------------|-------------|-----------------|
| 1MP (1000x1000) | 50MB | 256MB |
| 4MP (2000x2000) | 150MB | 512MB |
| 16MP (4000x4000) | 500MB | 1GB |
| 64MP (8000x8000) | 2GB | 4GB |

---

## Cost Optimization

### Reduce AI API Costs

Preprocessing images before sending to Claude/GPT-4V reduces:
- API latency (smaller payload)
- Token costs (smaller base64)
- Rate limiting impact

**Example Savings:**

| Before | After | Reduction |
|--------|-------|-----------|
| 4000x3000 JPEG (2.5MB) | 2048x1536 WebP (150KB) | 94% |
| API tokens ~3000 | API tokens ~500 | 83% |

**Estimated cost reduction: 40-60% per extraction**

### Reduce Cloud Run Costs

1. **Right-size instances**: Use minimum memory that works
2. **Scale to zero**: Set min instances to 0
3. **Batch processing**: Process multiple images per request
4. **Caching**: Enable Redis cache for repeated images

```yaml
# Cloud Run config for cost optimization
min_instances: 0
max_instances: 10
memory: 1Gi
cpu: 2
```

---

## Monitoring

### Key Metrics to Track

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Processing latency P95 | <500ms | >1000ms |
| Error rate | <0.5% | >1% |
| Memory usage | <80% | >90% |
| Throughput | >10/sec | <5/sec |

### Logging for Metrics

```python
import time
import logging

logger = logging.getLogger(__name__)

async def process_with_metrics(source: ImageSource) -> ProcessedImage:
    start = time.monotonic()

    result = await pipeline.process(source)

    elapsed_ms = (time.monotonic() - start) * 1000
    reduction = (1 - result.optimized_size / result.original_size) * 100

    logger.info(
        f"Processed image: "
        f"{result.dimensions[0]}x{result.dimensions[1]}, "
        f"{result.original_size//1024}KB -> {result.optimized_size//1024}KB "
        f"({reduction:.0f}% reduction), "
        f"{elapsed_ms:.0f}ms"
    )

    return result
```
```

---

## Summary

The documentation plan provides:

1. **API Reference:** Complete documentation of all public classes and methods
2. **Code Examples:** Runnable examples for common use cases
3. **Troubleshooting:** Solutions for common errors with debugging tips
4. **Performance Tuning:** Configuration profiles and optimization strategies

---

[← Back to Index](./README.md)

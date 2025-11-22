# Implementation Roadmap

[← Back to Index](./README.md) | [Previous: Unit Testing Strategy](./06-unit-testing-strategy.md)

---

## Overview

The implementation is divided into three phases, progressing from foundational components to production optimization.

```
Phase 1                    Phase 2                    Phase 3
───────────────────────    ───────────────────────    ───────────────────────
Core Dependencies          Preprocessing Pipeline     Optimization & Production
& Basic Loading            & Integration              Hardening

- Add dependencies         - OpenCV preprocessor      - Memory optimization
- Create module structure  - Image optimizer          - Caching layer
- Async loading            - Pipeline orchestrator    - Circuit breaker
- Basic validation         - Application service      - Documentation
- Initial tests            - Integration tests        - Performance testing
```

---

## Phase 1: Core Dependencies and Basic Loading

### Objective

Establish the foundation with dependencies, module structure, async loading, and validation.

---

### Task 1.1: Update Dependencies

**Files Modified:**
- `pyproject.toml`
- `Dockerfile`
- `requirements.txt` (if used)

**Steps:**

1. Add new dependencies to `pyproject.toml`:

```toml
# Add to [project.dependencies]
"opencv-python-headless>=4.9.0",
"httpx[http2]>=0.27.0",
"aiofiles>=23.2.0",
"python-magic>=0.4.27",

# Update Pillow
"pillow>=10.4.0",  # Was 10.2.0

# Pin numpy upper bound
"numpy>=1.26.0,<2.0",
```

2. Update Dockerfile to install libmagic:

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*
```

3. Run dependency resolution:

```bash
pip install -e ".[dev]"
pip check  # Verify no conflicts
```

4. Verify installation:

```python
python -c "import cv2; import httpx; import aiofiles; import magic; print('OK')"
```

**Acceptance Criteria:**
- [ ] All dependencies install without conflicts
- [ ] Docker image builds successfully
- [ ] Import verification passes

---

### Task 1.2: Create Infrastructure Structure

**Files Created:**
- `src/copy_that/infrastructure/cv/__init__.py`
- `src/copy_that/infrastructure/cv/exceptions.py`
- `src/copy_that/infrastructure/cv/config.py`

**Steps:**

1. Create directory structure:

```bash
mkdir -p src/copy_that/infrastructure/cv
touch src/copy_that/infrastructure/cv/__init__.py
```

2. Implement `exceptions.py` with all custom exceptions:
   - `ImageProcessingError` (base)
   - `FileTooLargeError`
   - `UnsupportedFormatError`
   - `CorruptImageError`
   - `DimensionError`
   - `NetworkError`
   - `InvalidURLError`
   - `InvalidPathError`
   - `FormatMismatchError`
   - `AspectRatioError`

3. Implement `config.py` with Pydantic configuration:
   - `PreprocessingConfig`
   - `FetcherConfig`
   - `LoaderConfig`
   - `SizeConfig`
   - `ValidationConfig`

4. Set up `__init__.py` exports:

```python
from .exceptions import *
from .config import *
```

**Acceptance Criteria:**
- [ ] All exception types defined with user-friendly messages
- [ ] Configuration loads from environment variables
- [ ] Module imports work correctly

---

### Task 1.3: Implement Async Loading

**Files Created:**
- `src/copy_that/infrastructure/cv/loader.py`

**Implementation:**

```python
# Core classes to implement
class AsyncImageFetcher:
    """httpx-based URL fetching"""
    async def fetch(self, url: str, progress_callback=None) -> FetchResult
    def _validate_url(self, url: str) -> None
    def _validate_headers(self, headers) -> None

class AsyncFileLoader:
    """aiofiles-based file loading"""
    async def load(self, path: Path) -> bytes
    async def load_streaming(self, path: Path) -> AsyncIterator[bytes]
    def _validate_path(self, path: Path) -> None

class ImageSource:
    """Unified image source abstraction"""
    @classmethod
    def from_url(cls, url: str) -> ImageSource
    @classmethod
    def from_file(cls, path: Path) -> ImageSource
    @classmethod
    def from_base64(cls, data: str, media_type: str) -> ImageSource
```

**Key Features:**
- SSRF protection in URL validation
- Path traversal protection
- Size limit enforcement during download
- Progress tracking support
- Connection pooling with httpx

**Acceptance Criteria:**
- [ ] Can fetch images from URLs asynchronously
- [ ] Can load local files asynchronously
- [ ] SSRF protection blocks private IPs
- [ ] Size limits enforced during download
- [ ] Progress callback works correctly

---

### Task 1.4: Implement Basic Validation

**Files Created:**
- `src/copy_that/infrastructure/cv/validator.py`

**Implementation:**

```python
# Core classes to implement
class MagicValidator:
    """python-magic based format detection"""
    def detect_format(self, data: bytes) -> ImageFormat
    def validate_extension_matches(self, data: bytes, filename: str) -> None

class SizeValidator:
    """Size constraint validation"""
    def validate_file_size(self, data: bytes) -> None
    def validate_dimensions(self, width: int, height: int) -> None
    def validate_aspect_ratio(self, width: int, height: int) -> None

class IntegrityValidator:
    """Corrupt image detection"""
    def validate(self, data: bytes) -> ImageInfo
    def check_truncation(self, data: bytes, format_: ImageFormat) -> None

class FormatValidator:
    """Format compatibility validation"""
    def validate(self, format_: ImageFormat, dimensions: tuple) -> None
    def needs_conversion(self, format_: ImageFormat) -> bool

class ImageValidator:
    """Composite validator"""
    def validate(self, data: bytes) -> ImageInfo
```

**Key Features:**
- Magic byte detection with python-magic
- Comprehensive size validation
- Corrupt/truncated image detection
- Format compatibility checks

**Acceptance Criteria:**
- [ ] Correctly identifies image formats
- [ ] Rejects non-image files
- [ ] Enforces size and dimension limits
- [ ] Detects truncated images
- [ ] Returns accurate ImageInfo

---

### Task 1.5: Initial Tests

**Files Created:**
- `tests/unit/test_image_processing/__init__.py`
- `tests/unit/test_image_processing/conftest.py`
- `tests/unit/test_image_processing/test_loader.py`
- `tests/unit/test_image_processing/test_validator.py`

**Test Coverage:**

| Module | Test Count | Coverage Target |
|--------|------------|-----------------|
| loader.py | ~20 tests | 90% |
| validator.py | ~25 tests | 90% |

**Acceptance Criteria:**
- [ ] All tests pass
- [ ] Coverage ≥80% for new code
- [ ] Mocks work correctly for async operations
- [ ] Test fixtures generate valid test images

---

### Phase 1 Deliverables

1. ✅ Working async image fetching with httpx
2. ✅ Working async file loading with aiofiles
3. ✅ Comprehensive validation pipeline
4. ✅ SSRF and path traversal protection
5. ✅ Unit tests with 80%+ coverage

---

## Phase 2: Preprocessing Pipeline

### Objective

Implement OpenCV preprocessing, image optimization, and pipeline orchestration.

---

### Task 2.1: Implement OpenCV Preprocessor

**Files Created:**
- `src/copy_that/infrastructure/cv/preprocessor.py`

**Implementation:**

```python
class ImagePreprocessor:
    """OpenCV-based image preprocessing"""

    def resize_for_api(self, img: np.ndarray, max_size: int) -> np.ndarray:
        """Resize maintaining aspect ratio"""

    def normalize_color_space(self, img: np.ndarray, source: str = "BGR") -> np.ndarray:
        """Convert to RGB, handle grayscale/RGBA"""

    def enhance_for_extraction(self, img: np.ndarray) -> np.ndarray:
        """Apply CLAHE contrast enhancement"""

    def auto_orient(self, img: np.ndarray, exif: dict) -> np.ndarray:
        """Apply EXIF orientation correction"""

    def denoise(self, img: np.ndarray) -> np.ndarray:
        """Optional denoising"""
```

**Key Features:**
- High-quality resize with LANCZOS4
- Color space normalization (BGR→RGB, grayscale→RGB)
- CLAHE contrast enhancement
- EXIF orientation correction

**Acceptance Criteria:**
- [ ] Resize maintains aspect ratio
- [ ] Color space conversion works for all input types
- [ ] Enhancement improves low-contrast images
- [ ] EXIF rotation applied correctly

---

### Task 2.2: Implement Optimizer

**Files Created:**
- `src/copy_that/infrastructure/cv/optimizer.py`

**Implementation:**

```python
class ImageOptimizer:
    """Image compression and format conversion"""

    def compress_for_api(self, img: np.ndarray, target_kb: int) -> bytes:
        """Progressive compression to target size"""

    def convert_format(self, data: bytes, target: ImageFormat) -> bytes:
        """Convert to target format (WebP recommended)"""

    def strip_metadata(self, data: bytes) -> bytes:
        """Remove EXIF for privacy"""
```

**Key Features:**
- Progressive quality reduction to hit size target
- WebP conversion for size/quality ratio
- Metadata stripping for privacy

**Acceptance Criteria:**
- [ ] Output size close to target
- [ ] WebP conversion works correctly
- [ ] Metadata removed while keeping orientation

---

### Task 2.3: Create Pipeline Orchestrator

**Files Created:**
- `src/copy_that/infrastructure/cv/preprocessing.py`

**Implementation:**

```python
class ImagePreprocessingPipeline:
    """Main orchestrator with error recovery"""

    async def process(self, source: ImageSource) -> ProcessedImage:
        """Full pipeline: load → validate → preprocess → optimize"""

    async def _full_preprocess(self, source: ImageSource) -> ProcessedImage
    async def _reduced_preprocess(self, source: ImageSource) -> ProcessedImage
    async def _minimal_preprocess(self, source: ImageSource) -> ProcessedImage
    async def _passthrough(self, source: ImageSource) -> ProcessedImage

class ConcurrentImageProcessor:
    """Batch processing with controlled concurrency"""

    async def process_batch(
        self,
        sources: list[ImageSource],
        progress_callback=None
    ) -> list[ProcessedImage | Exception]:
        """Process multiple images concurrently"""
```

**Key Features:**
- Graceful degradation with multiple strategies
- Controlled concurrency with semaphore
- Progress tracking for batches
- Memory error recovery

**Acceptance Criteria:**
- [ ] Full pipeline processes images correctly
- [ ] Graceful degradation works on failures
- [ ] Batch processing maintains concurrency limit
- [ ] Progress callback reports accurately

---

### Task 2.4: Create Application Service

**Files Created:**
- `src/copy_that/application/services/image_service.py`

**Implementation:**

```python
class ImageService:
    """High-level image processing service"""

    def __init__(self, config: PreprocessingConfig | None = None):
        self.pipeline = ImagePreprocessingPipeline(config or PreprocessingConfig())

    async def preprocess_for_extraction(
        self,
        source: str | Path | bytes,
        source_type: str = "auto"
    ) -> ProcessedImage:
        """Preprocess image for AI extraction"""

    async def preprocess_batch(
        self,
        sources: list[str | Path],
        progress_callback=None
    ) -> list[ProcessedImage]:
        """Preprocess multiple images"""

    def get_base64_for_api(self, processed: ProcessedImage) -> tuple[str, str]:
        """Get base64-encoded data for AI APIs"""
```

**Integration Points:**
- Replace direct `requests.get()` in extractors
- Integrate with batch_extractor.py
- Provide base64 encoding for AI APIs

**Acceptance Criteria:**
- [ ] Service provides simple API for application layer
- [ ] Integrates with existing extractors
- [ ] Handles all source types (URL, file, base64)

---

### Task 2.5: Integration Tests

**Files Created:**
- `tests/unit/test_image_processing/test_preprocessor.py`
- `tests/unit/test_image_processing/test_optimizer.py`
- `tests/unit/test_image_processing/test_pipeline.py`

**Test Coverage:**

| Module | Test Count | Coverage Target |
|--------|------------|-----------------|
| preprocessor.py | ~15 tests | 85% |
| optimizer.py | ~10 tests | 85% |
| preprocessing.py | ~20 tests | 85% |

**Acceptance Criteria:**
- [ ] All integration tests pass
- [ ] End-to-end pipeline works correctly
- [ ] Concurrent processing handles failures
- [ ] Coverage ≥85% for Phase 2 code

---

### Phase 2 Deliverables

1. ✅ OpenCV preprocessing operations
2. ✅ Image optimization and format conversion
3. ✅ Pipeline orchestration with graceful degradation
4. ✅ Application service for integration
5. ✅ Integration tests passing

---

## Phase 3: Optimization and Production

### Objective

Optimize for production, add caching, harden for reliability, and complete documentation.

---

### Task 3.1: Memory Optimization

**Files Modified:**
- `src/copy_that/infrastructure/cv/preprocessing.py`
- `src/copy_that/infrastructure/cv/preprocessor.py`

**Optimizations:**

```python
class MemoryEfficientProcessor:
    """Memory-optimized processing for Cloud Run"""

    def estimate_memory_usage(self, width: int, height: int) -> int
    def should_downscale_early(self, width: int, height: int) -> bool
    def get_early_downscale_factor(self, width: int, height: int) -> float

    async def process_streaming(self, source: ImageSource) -> AsyncIterator[bytes]:
        """Stream processing for very large images"""
```

**Strategies:**
- Early downscaling for memory-constrained environments
- Streaming processing for large images
- Explicit garbage collection after heavy operations
- Memory usage monitoring

**Acceptance Criteria:**
- [ ] Can process 16MP images in 1GB Cloud Run instance
- [ ] Peak memory stays under configured limits
- [ ] No memory leaks over multiple operations

---

### Task 3.2: Caching Layer (Optional)

**Files Created:**
- `src/copy_that/infrastructure/cv/cache.py`

**Implementation:**

```python
class ProcessedImageCache:
    """Redis-based cache for processed images"""

    def __init__(self, redis_url: str, ttl_seconds: int = 3600):
        self.redis = aioredis.from_url(redis_url)
        self.ttl = ttl_seconds

    async def get(self, key: str) -> ProcessedImage | None:
        """Retrieve cached processed image"""

    async def set(self, key: str, image: ProcessedImage) -> None:
        """Cache processed image"""

    def generate_key(self, source: ImageSource, config: PreprocessingConfig) -> str:
        """Generate cache key from source and config"""
```

**Key Features:**
- Content-based cache keys (hash of source + config)
- Configurable TTL
- Optional (can disable in config)

**Acceptance Criteria:**
- [ ] Cache hits return correct data
- [ ] Cache misses don't block
- [ ] TTL expiration works correctly

---

### Task 3.3: Production Hardening

**Files Modified:**
- `src/copy_that/infrastructure/cv/loader.py`
- `src/copy_that/infrastructure/cv/preprocessing.py`

**Hardening:**

```python
class CircuitBreaker:
    """Circuit breaker for external URL fetching"""

    def __init__(
        self,
        failure_threshold: int = 5,
        reset_timeout: float = 60.0
    ):
        self.state = "closed"
        self.failures = 0
        self.last_failure_time = 0

    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
```

**Features:**
- Circuit breaker for external URLs
- Structured logging with context
- Metrics collection (processing time, size, format)
- Health check endpoint support

**Acceptance Criteria:**
- [ ] Circuit breaker trips after threshold failures
- [ ] Circuit breaker resets after timeout
- [ ] Logs include sufficient context
- [ ] Metrics are accurate

---

### Task 3.4: Documentation

**Files Created:**
- `docs/api/image-processing.md`
- `docs/examples/image-processing-examples.md`
- `docs/troubleshooting/image-processing.md`
- `docs/performance/image-processing-tuning.md`

**Documentation Sections:**

1. **API Reference**
   - All public classes and methods
   - Configuration options
   - Environment variables

2. **Examples**
   - Basic usage
   - Batch processing
   - Integration with extractors
   - Error handling

3. **Troubleshooting**
   - Common errors and solutions
   - Debugging tips
   - Log analysis

4. **Performance Tuning**
   - Configuration by environment
   - Benchmarks
   - Cost optimization

**Acceptance Criteria:**
- [ ] All public APIs documented
- [ ] Examples are runnable
- [ ] Troubleshooting covers common issues
- [ ] Performance guide includes benchmarks

---

### Task 3.5: Performance Testing

**Files Created:**
- `tests/performance/test_image_processing_perf.py`

**Tests:**

```python
class TestLoadPerformance:
    """Load testing for image processing"""

    async def test_sustained_load(self):
        """Process images for 5 minutes at steady rate"""

    async def test_burst_load(self):
        """Handle sudden burst of 100 images"""

    async def test_memory_under_load(self):
        """Monitor memory during sustained processing"""

class TestLatencyPerformance:
    """Latency benchmarks"""

    async def test_p99_latency(self):
        """Measure P99 latency over 1000 operations"""

    async def test_latency_by_image_size(self):
        """Measure latency for different image sizes"""
```

**Metrics to Collect:**
- Throughput (images/second)
- Latency (P50, P95, P99)
- Memory usage (peak, average)
- Error rate under load

**Acceptance Criteria:**
- [ ] Throughput ≥ 10 images/second
- [ ] P95 latency < 500ms for typical images
- [ ] Error rate < 0.1% under normal load
- [ ] No memory growth over time

---

### Phase 3 Deliverables

1. ✅ Memory-optimized processing for Cloud Run
2. ✅ Optional caching layer
3. ✅ Production hardening (circuit breaker, logging)
4. ✅ Complete documentation
5. ✅ Performance testing results

---

## Summary

### Total Tasks

| Phase | Tasks | Focus |
|-------|-------|-------|
| Phase 1 | 5 | Foundation |
| Phase 2 | 5 | Core Pipeline |
| Phase 3 | 5 | Production |

### Key Milestones

1. **End of Phase 1:** Can fetch, validate, and load images asynchronously
2. **End of Phase 2:** Full preprocessing pipeline working, integrated with app
3. **End of Phase 3:** Production-ready with documentation and performance validation

### Dependencies

```
Phase 1 → Phase 2 → Phase 3
   │         │         │
   └─────────┴─────────┴─── Each phase depends on previous
```

---

[← Back to Index](./README.md) | [Next: Documentation Plan →](./08-documentation-plan.md)

# Async Image Loading & Fetching Strategy

[← Back to Index](./README.md) | [Previous: OpenCV Pipeline Design](./02-opencv-pipeline-design.md)

---

## 3.1 httpx Integration for Async URL Fetching

### Core Implementation

```python
# src/copy_that/infrastructure/cv/loader.py

import httpx
from contextlib import asynccontextmanager
from typing import AsyncIterator

class AsyncImageFetcher:
    """Production-ready async image fetching with httpx"""

    def __init__(self, config: FetcherConfig):
        self.config = config
        self._client: httpx.AsyncClient | None = None

    @asynccontextmanager
    async def get_client(self) -> AsyncIterator[httpx.AsyncClient]:
        """Get or create httpx client with connection pooling"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(
                    connect=5.0,
                    read=30.0,
                    write=10.0,
                    pool=5.0
                ),
                limits=httpx.Limits(
                    max_connections=100,
                    max_keepalive_connections=20,
                    keepalive_expiry=30.0
                ),
                follow_redirects=True,
                max_redirects=5,
                http2=True,
            )
        yield self._client

    async def fetch(self, url: str, progress_callback=None) -> FetchResult:
        """Fetch image from URL with validation and progress tracking"""

        # 1. Validate URL (prevent SSRF)
        self._validate_url(url)

        async with self.get_client() as client:
            # 2. HEAD request to check content-type and size
            head_resp = await client.head(url)
            self._validate_headers(head_resp.headers)

            # 3. Stream download with progress
            async with client.stream("GET", url) as response:
                response.raise_for_status()

                total = int(response.headers.get("content-length", 0))
                chunks = []
                downloaded = 0

                async for chunk in response.aiter_bytes(chunk_size=65536):
                    chunks.append(chunk)
                    downloaded += len(chunk)

                    # Enforce size limit during download
                    if downloaded > self.config.max_size_bytes:
                        raise FileTooLargeError(
                            f"File exceeds {self.config.max_size_mb}MB limit"
                        )

                    if progress_callback:
                        await progress_callback(downloaded, total)

                return FetchResult(
                    data=b"".join(chunks),
                    content_type=response.headers.get("content-type"),
                    url=str(response.url),
                )
```

### SSRF Protection

```python
def _validate_url(self, url: str) -> None:
    """Prevent SSRF attacks"""
    from urllib.parse import urlparse
    import ipaddress

    parsed = urlparse(url)

    # Only allow HTTP/HTTPS
    if parsed.scheme not in ("http", "https"):
        raise InvalidURLError(f"Invalid scheme: {parsed.scheme}")

    # Block private/local addresses
    hostname = parsed.hostname
    if not hostname:
        raise InvalidURLError("Missing hostname")

    try:
        ip = ipaddress.ip_address(hostname)
        if ip.is_private or ip.is_loopback or ip.is_reserved:
            raise InvalidURLError("Private/local URLs not allowed")
    except ValueError:
        pass  # Hostname is not an IP

    # Block common internal hostnames
    blocked = [
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
        "metadata.google",
        "169.254.169.254",
        "metadata.google.internal",
    ]
    if any(b in hostname.lower() for b in blocked):
        raise InvalidURLError("Blocked hostname")

def _validate_headers(self, headers: httpx.Headers) -> None:
    """Validate response headers before downloading"""

    # Check content-type
    content_type = headers.get("content-type", "")
    if not content_type.startswith("image/"):
        raise InvalidImageError(f"Not an image: {content_type}")

    # Check content-length if available
    content_length = headers.get("content-length")
    if content_length:
        size_bytes = int(content_length)
        if size_bytes > self.config.max_size_bytes:
            size_mb = size_bytes / (1024 * 1024)
            raise FileTooLargeError(
                f"File {size_mb:.1f}MB exceeds limit"
            )
```

---

## 3.2 aiofiles Integration for Local File Handling

```python
import aiofiles
import aiofiles.os
from pathlib import Path

class AsyncFileLoader:
    """Async local file operations with aiofiles"""

    def __init__(self, config: LoaderConfig):
        self.config = config
        self.allowed_roots = [
            Path("/tmp"),
            Path.home() / "uploads",
        ]

    async def load(self, path: Path) -> bytes:
        """Load file asynchronously with validation"""

        # 1. Validate path (prevent traversal)
        self._validate_path(path)

        # 2. Check file exists and get size
        if not await aiofiles.os.path.exists(path):
            raise FileNotFoundError(f"Image not found: {path}")

        stat = await aiofiles.os.stat(path)
        if stat.st_size > self.config.max_size_bytes:
            raise FileTooLargeError(
                f"File {stat.st_size / 1024 / 1024:.1f}MB exceeds limit"
            )

        # 3. Read file
        async with aiofiles.open(path, "rb") as f:
            return await f.read()

    async def load_streaming(self, path: Path) -> AsyncIterator[bytes]:
        """Stream file for memory-efficient processing"""

        self._validate_path(path)

        async with aiofiles.open(path, "rb") as f:
            while chunk := await f.read(65536):
                yield chunk

    def _validate_path(self, path: Path) -> None:
        """Prevent path traversal attacks"""
        resolved = path.resolve()

        if not any(
            resolved.is_relative_to(root) for root in self.allowed_roots
        ):
            raise InvalidPathError(
                f"Path not in allowed directories: {path}"
            )

        # Additional checks
        if ".." in str(path):
            raise InvalidPathError("Path traversal detected")
```

---

## 3.3 Connection Pooling and Timeout Strategies

### Configuration Model

```python
from pydantic import BaseModel
import httpx

class ConnectionConfig(BaseModel):
    """Configuration for HTTP connections"""

    # Timeouts
    connect_timeout: float = 5.0       # Connection establishment
    read_timeout: float = 30.0         # Data transfer
    write_timeout: float = 10.0        # Sending request
    pool_timeout: float = 5.0          # Waiting for connection from pool

    # Pool limits
    max_connections: int = 100         # Total connections
    max_keepalive: int = 20            # Keep-alive connections
    keepalive_expiry: float = 30.0     # Seconds before closing idle

    # Retry configuration
    max_retries: int = 3
    retry_statuses: list[int] = [429, 500, 502, 503, 504]
    retry_backoff_base: float = 1.0    # Base backoff in seconds

    # HTTP/2 settings
    enable_http2: bool = True

    @property
    def timeout(self) -> httpx.Timeout:
        return httpx.Timeout(
            connect=self.connect_timeout,
            read=self.read_timeout,
            write=self.write_timeout,
            pool=self.pool_timeout,
        )

    @property
    def limits(self) -> httpx.Limits:
        return httpx.Limits(
            max_connections=self.max_connections,
            max_keepalive_connections=self.max_keepalive,
            keepalive_expiry=self.keepalive_expiry,
        )
```

### Timeout Recommendations

| Scenario | Connect | Read | Pool | Notes |
|----------|---------|------|------|-------|
| **Default** | 5s | 30s | 5s | Balanced for most images |
| **Fast Network** | 2s | 15s | 3s | Low latency networks |
| **Large Images** | 5s | 60s | 5s | For 10MB+ images |
| **Slow Sources** | 10s | 120s | 10s | Unreliable CDNs |

### Connection Pool Sizing

```python
# Rule of thumb for pool sizing
max_connections = expected_concurrent_requests * 1.5
max_keepalive = max_connections * 0.2

# Example for batch processing 50 concurrent images
config = ConnectionConfig(
    max_connections=75,      # 50 * 1.5
    max_keepalive=15,        # 75 * 0.2
    keepalive_expiry=30.0,   # Keep connections warm
)
```

---

## 3.4 Progress Tracking for Large Images

### Progress Data Structure

```python
from dataclasses import dataclass
from typing import Callable, Awaitable
import time

@dataclass
class DownloadProgress:
    """Progress information for image downloads"""
    bytes_downloaded: int
    bytes_total: int | None
    elapsed_seconds: float
    url: str

    @property
    def percentage(self) -> float | None:
        if self.bytes_total and self.bytes_total > 0:
            return (self.bytes_downloaded / self.bytes_total) * 100
        return None

    @property
    def speed_mbps(self) -> float:
        if self.elapsed_seconds > 0:
            mb_downloaded = self.bytes_downloaded / (1024 * 1024)
            return mb_downloaded / self.elapsed_seconds
        return 0.0

    @property
    def eta_seconds(self) -> float | None:
        if self.bytes_total and self.speed_mbps > 0:
            remaining_mb = (self.bytes_total - self.bytes_downloaded) / (1024 * 1024)
            return remaining_mb / self.speed_mbps
        return None

ProgressCallback = Callable[[DownloadProgress], Awaitable[None]]
```

### Progress Tracker Implementation

```python
class ProgressTracker:
    """Track and report download progress"""

    def __init__(
        self,
        url: str,
        callback: ProgressCallback | None = None,
        report_interval: float = 0.5  # Minimum seconds between reports
    ):
        self.url = url
        self.callback = callback
        self.report_interval = report_interval
        self.start_time = time.monotonic()
        self.last_report_time = 0.0

    async def update(self, downloaded: int, total: int | None) -> None:
        """Update progress and potentially call callback"""
        if not self.callback:
            return

        current_time = time.monotonic()
        elapsed = current_time - self.start_time

        # Rate limit progress reports
        if current_time - self.last_report_time < self.report_interval:
            # Always report on completion
            if total and downloaded < total:
                return

        progress = DownloadProgress(
            bytes_downloaded=downloaded,
            bytes_total=total,
            elapsed_seconds=elapsed,
            url=self.url,
        )

        await self.callback(progress)
        self.last_report_time = current_time
```

### Usage Example

```python
async def download_with_progress(url: str):
    """Example: Download image with progress reporting"""

    async def on_progress(progress: DownloadProgress):
        if progress.percentage:
            print(
                f"\rDownloading: {progress.percentage:.1f}% "
                f"({progress.speed_mbps:.1f} MB/s) "
                f"ETA: {progress.eta_seconds:.0f}s",
                end=""
            )
        else:
            print(
                f"\rDownloading: {progress.bytes_downloaded / 1024:.0f} KB "
                f"({progress.speed_mbps:.1f} MB/s)",
                end=""
            )

    fetcher = AsyncImageFetcher(FetcherConfig())
    result = await fetcher.fetch(url, progress_callback=on_progress)
    print()  # New line after progress
    return result
```

---

## 3.5 Concurrent Processing Patterns

### Semaphore-Controlled Concurrency

```python
class ConcurrentImageProcessor:
    """Process multiple images concurrently with controlled parallelism"""

    def __init__(self, max_concurrent: int = 4):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.fetcher = AsyncImageFetcher(FetcherConfig())
        self.pipeline = PreprocessingPipeline(PreprocessingConfig())

    async def process_batch(
        self,
        sources: list[ImageSource],
        progress_callback: Callable[[int, int], Awaitable[None]] | None = None
    ) -> list[ProcessedImage | ImageProcessingError]:
        """Process batch with semaphore-controlled concurrency"""

        completed = 0
        total = len(sources)
        results_lock = asyncio.Lock()

        async def process_one(source: ImageSource, index: int):
            nonlocal completed

            async with self.semaphore:
                try:
                    result = await self.pipeline.process(source)
                except Exception as e:
                    result = ImageProcessingError(str(e), source=source)

                async with results_lock:
                    completed += 1
                    if progress_callback:
                        await progress_callback(completed, total)

                return index, result

        # Launch all tasks (semaphore controls actual concurrency)
        tasks = [
            process_one(source, i)
            for i, source in enumerate(sources)
        ]

        results = await asyncio.gather(*tasks)

        # Sort by original index and extract results
        results.sort(key=lambda x: x[0])
        return [r[1] for r in results]
```

### Streaming Processing Pattern

```python
async def process_streaming(
    self,
    sources: AsyncIterator[ImageSource]
) -> AsyncIterator[ProcessedImage]:
    """Stream processing for unknown-length sources"""

    async for source in sources:
        async with self.semaphore:
            try:
                yield await self.pipeline.process(source)
            except ImageProcessingError as e:
                logger.error(f"Failed to process {source}: {e}")
                yield e
```

### Producer-Consumer Pattern

```python
async def process_with_queue(
    self,
    sources: list[ImageSource],
    num_workers: int = 4
) -> list[ProcessedImage]:
    """Use queue for fine-grained control"""

    queue = asyncio.Queue()
    results = {}

    # Add tasks to queue
    for i, source in enumerate(sources):
        await queue.put((i, source))

    async def worker(worker_id: int):
        while True:
            try:
                index, source = await asyncio.wait_for(
                    queue.get(), timeout=1.0
                )
            except asyncio.TimeoutError:
                break

            try:
                result = await self.pipeline.process(source)
                results[index] = result
            except Exception as e:
                results[index] = ImageProcessingError(str(e))
            finally:
                queue.task_done()

    # Start workers
    workers = [
        asyncio.create_task(worker(i))
        for i in range(num_workers)
    ]

    # Wait for completion
    await queue.join()

    # Cancel workers
    for w in workers:
        w.cancel()

    # Return sorted results
    return [results[i] for i in range(len(sources))]
```

### Concurrency Recommendations

| Scenario | max_concurrent | Notes |
|----------|----------------|-------|
| **CPU-bound ops** | Number of CPU cores | Resize, enhancement |
| **I/O-bound ops** | 10-50 | Network fetching |
| **Memory-constrained** | 2-4 | Large images, limited RAM |
| **Balanced** | 4-8 | Mixed operations |

```python
# Auto-detect optimal concurrency
import os

def get_optimal_concurrency() -> int:
    """Get optimal concurrency based on environment"""

    cpu_count = os.cpu_count() or 4

    # Check if memory-constrained
    try:
        import psutil
        available_mb = psutil.virtual_memory().available / (1024 * 1024)
        if available_mb < 1024:  # Less than 1GB available
            return min(2, cpu_count)
    except ImportError:
        pass

    # Default: 2x CPU for mixed I/O and CPU ops
    return min(cpu_count * 2, 8)
```

---

## 3.6 Client Lifecycle Management

### Application-Level Client

```python
class ImageLoaderService:
    """Manages httpx client lifecycle at application level"""

    _client: httpx.AsyncClient | None = None

    @classmethod
    async def get_client(cls) -> httpx.AsyncClient:
        """Get shared client instance"""
        if cls._client is None:
            cls._client = httpx.AsyncClient(
                timeout=httpx.Timeout(connect=5, read=30, write=10, pool=5),
                limits=httpx.Limits(max_connections=100, max_keepalive=20),
                http2=True,
            )
        return cls._client

    @classmethod
    async def close(cls) -> None:
        """Close client on application shutdown"""
        if cls._client:
            await cls._client.aclose()
            cls._client = None

# FastAPI integration
from fastapi import FastAPI

app = FastAPI()

@app.on_event("shutdown")
async def shutdown_event():
    await ImageLoaderService.close()
```

### Request-Level Context Manager

```python
# For short-lived operations
async def fetch_single_image(url: str) -> bytes:
    """Fetch single image with dedicated client"""

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.content
```

---

## Summary

The async loading strategy provides:

1. **httpx Integration:** HTTP/2, connection pooling, streaming downloads
2. **aiofiles Integration:** Non-blocking file I/O
3. **Security:** SSRF protection, path traversal prevention
4. **Progress Tracking:** Real-time feedback for large images
5. **Concurrency Control:** Semaphore-based parallelism
6. **Lifecycle Management:** Proper client management

---

[← Back to Index](./README.md) | [Next: Validation & Error Handling →](./04-validation-error-handling.md)

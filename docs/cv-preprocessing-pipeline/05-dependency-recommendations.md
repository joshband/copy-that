# Dependency Recommendations

[← Back to Index](./README.md) | [Previous: Validation & Error Handling](./04-validation-error-handling.md)

---

## 5.1 Updated pyproject.toml Section

### Complete Dependencies Section

```toml
[project]
dependencies = [
    # === Web Framework ===
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",

    # === Database ===
    "sqlalchemy>=2.0.25",
    "asyncpg>=0.29.0",
    "alembic>=1.13.0",

    # === Task Queue ===
    "celery[redis]>=5.3.0",
    "redis>=5.0.0",

    # === AI APIs ===
    "anthropic>=0.18.0",
    "openai>=1.0.0",
    "google-cloud-vision>=3.7.0",

    # === Utilities ===
    "python-decouple>=3.8",

    # === Color Science ===
    "coloraide>=3.0.0",

    # === Image Processing (Core) ===
    "pillow>=10.4.0",
    "numpy>=1.26.0,<2.0",

    # === NEW: CV Preprocessing Dependencies ===
    "opencv-python-headless>=4.9.0",
    "httpx[http2]>=0.27.0",
    "aiofiles>=23.2.0",
    "python-magic>=0.4.27",
]

[project.optional-dependencies]
# Additional image format support
image-extras = [
    "pillow-heif>=0.15.0",
    "pillow-avif-plugin>=1.4.0",
]

# Development dependencies
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
    "pytest-benchmark>=4.0.0",
    "httpx>=0.27.0",
    "aiosqlite>=0.19.0",
    "mypy>=1.8.0",
    "ruff>=0.2.0",
    "faker>=22.0.0",
]
```

---

## 5.2 Dependency Justifications

### New Dependencies

| Package | Version | Purpose | Justification |
|---------|---------|---------|---------------|
| **opencv-python-headless** | >=4.9.0 | Computer vision operations | Core CV library for resize, color space conversion, enhancement. **Headless** variant has no GUI dependencies, essential for containerized/serverless deployment. Smaller footprint than full opencv-python. |
| **httpx[http2]** | >=0.27.0 | Async HTTP client | Modern async HTTP with connection pooling, HTTP/2 support, streaming downloads, and excellent typing. Preferred over aiohttp for FastAPI projects (same author). Already used by FastAPI's TestClient. |
| **aiofiles** | >=23.2.0 | Async file I/O | Simple, well-maintained wrapper for non-blocking file operations. Essential for async context to avoid blocking event loop on file reads. |
| **python-magic** | >=0.4.27 | File type detection | Wrapper for libmagic, the standard for accurate file type detection via magic bytes. Critical for security (prevents extension spoofing). |

### Updated Dependencies

| Package | Old Version | New Version | Reason |
|---------|-------------|-------------|--------|
| **pillow** | >=10.2.0 | >=10.4.0 | Security fixes (CVE-2024-28219, CVE-2024-4629). Contains memory safety improvements. |
| **numpy** | >=1.26.0 | >=1.26.0,<2.0 | Upper bound to prevent OpenCV compatibility issues with NumPy 2.0. |

### Why Headless OpenCV?

```
opencv-python          → Includes Qt/GTK GUI backends
opencv-python-headless → No GUI, smaller, server-friendly

Size comparison:
- opencv-python:          ~50MB + Qt dependencies (~100MB)
- opencv-python-headless: ~50MB (no additional deps)

Container benefits:
- No libGL, libX11, libQt dependencies
- Smaller image size
- No display server issues
```

---

## 5.3 Dependency Conflict Analysis

### Potential Conflicts

#### 1. numpy Version Pinning

**Issue:** OpenCV bundles its own numpy and may conflict with explicit pins.

**Solution:**
```toml
"numpy>=1.26.0,<2.0"  # Allow OpenCV's compatible version
```

**Verification:**
```bash
pip install numpy==1.26.4 opencv-python-headless==4.9.0
# Should install without conflicts
```

#### 2. httpx vs requests

**Current State:** The codebase uses `requests` for synchronous HTTP calls.

**Strategy:** Keep both during migration
```toml
# Both can coexist
"httpx[http2]>=0.27.0",  # New async code
# requests is a transitive dependency of other packages
```

**Migration Path:**
1. Add httpx for new async code
2. Gradually migrate existing sync code
3. Eventually remove explicit requests dependency

#### 3. python-magic System Dependency

**Issue:** Requires `libmagic` shared library.

**Docker Solution:**
```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*
```

**macOS (development):**
```bash
brew install libmagic
```

**Linux (development):**
```bash
apt-get install libmagic1
# or
yum install file-libs
```

#### 4. PIL Image Class Imports

**Issue:** Inconsistent imports between `PIL.Image` and `Pillow`.

**Solution:** Standardize imports
```python
# Good
from PIL import Image

# Avoid
import PIL
img = PIL.Image.open(...)
```

### Version Compatibility Matrix

| Package | Min Python | Depends On | Notes |
|---------|------------|------------|-------|
| opencv-python-headless 4.9 | 3.8 | numpy 1.21+ | Uses bundled numpy |
| httpx 0.27 | 3.8 | anyio 3+, httpcore 1+ | Pure Python |
| aiofiles 23.2 | 3.8 | - | Pure Python |
| python-magic 0.4 | 3.6 | libmagic 5+ | C extension |
| pillow 10.4 | 3.8 | - | C extension |

### Resolved Dependency Tree

```
copy-that
├── opencv-python-headless 4.9.0
│   └── numpy 1.26.4
├── httpx 0.27.0
│   ├── anyio 4.2.0
│   ├── httpcore 1.0.2
│   ├── certifi
│   ├── idna
│   └── sniffio
├── aiofiles 23.2.1
├── python-magic 0.4.27
└── pillow 10.4.0
```

---

## 5.4 Docker Image Size Impact Estimation

### Current Image Breakdown

```dockerfile
FROM python:3.11-slim  # ~120MB base

# Current installed packages: ~450MB
# Total: ~600MB
```

### New Dependencies Impact

| Package | Installed Size | Wheel Size | Notes |
|---------|----------------|------------|-------|
| opencv-python-headless | ~47MB | ~15MB | Binary wheels |
| httpx | ~5MB | ~300KB | Pure Python |
| aiofiles | ~50KB | ~20KB | Pure Python |
| python-magic | ~100KB | ~50KB | + libmagic ~2MB |
| libmagic1 (apt) | ~2MB | - | System package |

**Total New Dependencies: ~55MB**

### Image Size Comparison

| Version | Size | Change |
|---------|------|--------|
| Current | ~600MB | - |
| With CV deps | ~660MB | +60MB (+10%) |
| Optimized | ~580MB | -20MB (-3%) |

### Optimization Strategies

#### 1. Multi-Stage Build

```dockerfile
# Stage 1: Build
FROM python:3.11-slim AS builder

RUN pip install --no-cache-dir --target=/install \
    opencv-python-headless httpx aiofiles python-magic

# Stage 2: Runtime
FROM python:3.11-slim

COPY --from=builder /install /usr/local/lib/python3.11/site-packages/
```

#### 2. Minimal Base Image

```dockerfile
# Use slim variant with specific OS
FROM python:3.11-slim-bookworm AS runtime
```

#### 3. Aggressive Cleanup

```dockerfile
RUN apt-get update \
    && apt-get install -y --no-install-recommends libmagic1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /root/.cache/pip
```

#### 4. .dockerignore

```dockerignore
# Exclude from build context
__pycache__
*.pyc
*.pyo
.git
.gitignore
.env
.venv
tests/
docs/
*.md
.mypy_cache
.pytest_cache
.coverage
htmlcov/
```

### Optimized Dockerfile

```dockerfile
# Optimized Dockerfile for CV preprocessing
FROM python:3.11-slim-bookworm AS runtime

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libmagic1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ src/

# Set environment
ENV PYTHONPATH=/app/src
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "copy_that.interfaces.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Cloud Run Considerations

| Aspect | Recommendation |
|--------|----------------|
| **Min instances** | 0 (scale to zero) |
| **Max instances** | Based on load |
| **Memory** | 1GB minimum for image processing |
| **CPU** | 2 vCPU for good performance |
| **Startup** | ~660MB image = ~5-10s cold start |

---

## 5.5 Optional Dependencies

### HEIC/HEIF Support

```toml
[project.optional-dependencies]
image-extras = [
    "pillow-heif>=0.15.0",
]
```

**Usage:**
```python
# Register HEIF plugin
from pillow_heif import register_heif_opener
register_heif_opener()

# Now Pillow can open HEIC files
from PIL import Image
img = Image.open("photo.heic")
```

**Note:** Adds ~5MB to image size.

### AVIF Support

```toml
[project.optional-dependencies]
image-extras = [
    "pillow-avif-plugin>=1.4.0",
]
```

### Performance Profiling

```toml
[project.optional-dependencies]
profiling = [
    "memory-profiler>=0.61.0",
    "py-spy>=0.3.14",
]
```

---

## 5.6 Installation Commands

### Development Setup

```bash
# Clone and enter directory
git clone <repo>
cd copy-that

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"

# Install image extras (optional)
pip install -e ".[image-extras]"

# Install system dependency (macOS)
brew install libmagic

# Install system dependency (Ubuntu)
sudo apt-get install libmagic1
```

### Production Setup

```bash
# Install production dependencies only
pip install --no-cache-dir -r requirements.txt

# Or from pyproject.toml
pip install --no-cache-dir .
```

### Verify Installation

```python
# verify_deps.py
import sys

def check_dependency(name, import_name=None):
    import_name = import_name or name
    try:
        module = __import__(import_name)
        version = getattr(module, "__version__", "unknown")
        print(f"✅ {name}: {version}")
        return True
    except ImportError as e:
        print(f"❌ {name}: {e}")
        return False

deps = [
    ("opencv-python-headless", "cv2"),
    ("httpx", "httpx"),
    ("aiofiles", "aiofiles"),
    ("python-magic", "magic"),
    ("Pillow", "PIL"),
    ("numpy", "numpy"),
]

all_ok = all(check_dependency(name, imp) for name, imp in deps)
sys.exit(0 if all_ok else 1)
```

---

## Summary

### Dependencies to Add

| Package | Version | Size Impact |
|---------|---------|-------------|
| opencv-python-headless | >=4.9.0 | +47MB |
| httpx[http2] | >=0.27.0 | +5MB |
| aiofiles | >=23.2.0 | +50KB |
| python-magic | >=0.4.27 | +2MB |

### System Requirements

- libmagic1 (apt/brew)
- Python 3.11+

### Total Impact

- **Docker image:** +60MB (~10% increase)
- **Cold start:** +1-2 seconds
- **Compatibility:** No conflicts with existing deps

---

[← Back to Index](./README.md) | [Next: Unit Testing Strategy →](./06-unit-testing-strategy.md)

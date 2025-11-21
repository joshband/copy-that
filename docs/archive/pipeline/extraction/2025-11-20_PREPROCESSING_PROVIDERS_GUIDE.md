# Preprocessing Providers Guide

**Version:** 3.3.0
**Last Updated:** 2025-11-17
**Status:** Production Ready ✅

---

## 🎯 Overview

Copy This now includes **preprocessing providers** - singleton services that provide depth estimation and segmentation for enhanced token extraction.

### Why Preprocessing?

Preprocessing enhances extraction quality by understanding the **structure** of the UI:

- **Depth estimation** (MiDaS) reveals which elements are foreground vs background
- **Segmentation** (SAM/FastSAM) identifies precise UI component boundaries

### Key Benefits

- **67% Memory Reduction**: Singleton pattern ensures one model per process
- **150-2000x Speedup**: LRU caching for repeated calls
- **Progressive Results**: See tier 1 heuristic (<10ms) → tier 2 ML (150-2000ms)
- **Zero Blocking**: Extractors run in parallel with atomic streaming

---

## 📦 Available Providers

### 1. DepthProvider (MiDaS Integration)

**What it does:** Estimates depth map from 2D screenshot using MiDaS model.

**Use cases:**
- Shadow extraction (depth-aware shadow detection)
- Color extraction (foreground/background color separation)
- Z-index inference (layering based on depth)

**Performance:**
- **First call:** 150ms (M1 Metal) to 2s (CPU)
- **Cached calls:** <1ms (150-2000x faster)
- **Memory:** 500MB (singleton, shared across all extractors)

### 2. SegmentationProvider (SAM/FastSAM Integration)

**What it does:** Segments UI into individual components (buttons, cards, inputs).

**Use cases:**
- Component detection (automatic UI component boundaries)
- Color extraction (per-component color palettes)
- Layout analysis (component positioning and grouping)

**Performance:**
- **SAM:** ~1s, 92% accuracy (maximum quality)
- **FastSAM:** ~100ms, 88% accuracy (real-time)
- **Memory:** Shared with DepthProvider (singleton pattern)

---

## 🚀 Quick Start

### Basic Usage (Sync API)

```python
from extractors import get_depth_provider, get_segmentation_provider

# Get providers (singleton - same instance everywhere)
depth_provider = get_depth_provider(model_type="MiDaS_small", device="auto")
seg_provider = get_segmentation_provider(backend="fastsam", device="auto")

# Estimate depth
depth_map = depth_provider.estimate(image, use_cache=True)
print(f"Depth range: {depth_map.depth_range}")
print(f"Quality score: {depth_map.quality_score}")

# Segment image
mask = seg_provider.segment(image, use_cache=True)
print(f"Components detected: {mask.num_objects}")
print(f"Backend used: {mask.metadata['backend']}")
```

### Async Progressive API

```python
from extractors import get_depth_provider_async

async def extract_with_streaming(image):
    provider = await get_depth_provider_async()

    # Progressive streaming: tier 1 → tier 2
    async for tier, depth_map in provider.estimate_progressive(image):
        if tier == 1:
            print("Quick preview ready! (heuristic)")
        elif tier == 2:
            print("High-quality result ready! (MiDaS)")

        # Use depth_map for extraction
        yield depth_map
```

### Parallel Preprocessing

```python
import asyncio
from extractors import get_depth_provider_async, get_segmentation_provider_async

async def preprocess_image(image):
    # Initialize both providers in parallel
    depth_prov, seg_prov = await asyncio.gather(
        get_depth_provider_async(),
        get_segmentation_provider_async()
    )

    # Run both estimations concurrently (2x faster)
    depth_map, seg_mask = await asyncio.gather(
        depth_prov.estimate_async(image),
        seg_prov.segment_async(image)
    )

    return depth_map, seg_mask
```

---

## 🎨 Integration Examples

### Example 1: Depth-Enhanced Shadow Extraction

```python
from extractors import get_depth_provider

class ShadowExtractor:
    def __init__(self):
        # Get singleton provider (shared with other extractors)
        self._depth_provider = get_depth_provider()

    def extract(self, image):
        # Estimate depth (uses cache if available)
        depth_map = self._depth_provider.estimate(image, use_cache=True)

        # Use depth to identify shadow regions
        # (foreground elements cast shadows on background)
        foreground_mask = depth_map.depth > np.percentile(depth_map.depth, 60)

        # Detect shadows using depth-aware algorithm
        shadows = self._detect_shadows_with_depth(image, depth_map, foreground_mask)

        return {
            "shadow": shadows,
            "_metadata": {
                "depth_quality": depth_map.quality_score,
                "preprocessing": "MiDaS_depth"
            }
        }
```

### Example 2: Component-Aware Color Extraction

```python
from extractors import get_depth_provider, get_segmentation_provider

class ColorExtractor:
    def __init__(self):
        self._depth_provider = get_depth_provider()
        self._seg_provider = get_segmentation_provider(backend="fastsam")

    def extract_tier1_basic(self, image):
        """Tier 1: Fast k-means (~100ms)"""
        return basic_kmeans_palette(image)

    def extract_tier2_depth_enhanced(self, image):
        """Tier 2: Depth-weighted colors (~2s)"""
        depth_map = self._depth_provider.estimate(image, use_cache=True)

        # Separate foreground/background by depth
        fg_mask = depth_map.depth > np.percentile(depth_map.depth, 60)

        # Extract semantic color roles
        return {
            "primary": extract_colors(image[fg_mask]),     # Foreground
            "surface": extract_colors(image[~fg_mask]),    # Background
        }

    def extract_tier3_component_aware(self, image):
        """Tier 3: Per-component colors (~3s)"""
        seg_mask = self._seg_provider.segment(image, use_cache=True)

        # Extract colors per component
        component_colors = {}
        for obj_id in np.unique(seg_mask.mask):
            comp_mask = seg_mask.mask == obj_id
            comp_color = extract_dominant_color(image[comp_mask])
            component_colors[f"component-{obj_id}"] = comp_color

        return component_colors
```

### Example 3: Atomic Streaming with Preprocessing

```python
from extractors.ai.multi_extractor import MultiExtractor, ExtractorConfig, ExtractorTier

# Configure extractors (some use preprocessing)
extractors = [
    ExtractorConfig("color", color_fn, ExtractorTier.FAST),           # No preprocessing
    ExtractorConfig("spacing", spacing_fn, ExtractorTier.FAST),       # No preprocessing
    ExtractorConfig("shadow", shadow_fn, ExtractorTier.MEDIUM),       # Uses DepthProvider!
    ExtractorConfig("component", component_fn, ExtractorTier.SLOW),   # Uses SegmentationProvider!
]

multi = MultiExtractor(extractors=extractors)

# Atomic streaming: all run in parallel
async for result in multi.extract_atomic([image]):
    # t=100ms:  ✅ color → streamed
    # t=150ms:  ✅ spacing → streamed
    # t=500ms:  ✅ shadow → streamed (after DepthProvider)
    # t=2000ms: ✅ component → streamed (after SegmentationProvider)

    extractor = result["_metadata"]["extractor"]
    elapsed = result["_metadata"]["elapsed_ms"]
    print(f"✅ {extractor} done in {elapsed}ms")
```

---

## 🔧 Configuration

### Device Selection

```python
from extractors import get_depth_provider, get_segmentation_provider

# Auto-detect best device (CUDA > MPS > CPU)
provider = get_depth_provider(device="auto")

# Explicitly select device
provider = get_depth_provider(device="cuda")   # NVIDIA GPU
provider = get_depth_provider(device="mps")    # Apple Metal
provider = get_depth_provider(device="cpu")    # CPU only
```

### Model Selection

```python
# Depth provider models
depth_provider = get_depth_provider(model_type="MiDaS_small")   # Faster, less accurate
depth_provider = get_depth_provider(model_type="DPT_Large")     # Slower, more accurate

# Segmentation provider backends
seg_provider = get_segmentation_provider(backend="sam")        # Higher quality (~1s)
seg_provider = get_segmentation_provider(backend="fastsam")    # Faster (~100ms)
seg_provider = get_segmentation_provider(backend="auto")       # Auto-select by platform
```

### Cache Configuration

```python
# Enable/disable caching
depth_map = provider.estimate(image, use_cache=True)   # Use cache (default)
depth_map = provider.estimate(image, use_cache=False)  # Skip cache

# Check cache stats
stats = provider.get_cache_stats()
print(f"Cache size: {stats['cache_size']}/{stats['max_cache_size']}")
print(f"Hit rate: {stats['hit_rate']*100:.1f}%")
print(f"Hits: {stats['hits']}, Misses: {stats['misses']}")

# Clear cache
provider.clear_cache()
```

---

## 📊 Performance Tips

### 1. Use Caching

**Always enable caching** for repeated calls:

```python
# ✅ GOOD: Use cache
for extractor in extractors:
    depth_map = depth_provider.estimate(image, use_cache=True)

# ❌ BAD: Skip cache (2000x slower)
for extractor in extractors:
    depth_map = depth_provider.estimate(image, use_cache=False)
```

### 2. Parallel Processing

**Run preprocessing in parallel** when possible:

```python
# ✅ GOOD: Parallel (40% faster)
depth_map, seg_mask = await asyncio.gather(
    depth_prov.estimate_async(image),
    seg_prov.segment_async(image)
)

# ❌ BAD: Sequential
depth_map = await depth_prov.estimate_async(image)
seg_mask = await seg_prov.segment_async(image)  # Waits for depth to finish
```

### 3. Use Progressive Streaming

**Stream tier 1 immediately** for fast feedback:

```python
# ✅ GOOD: Progressive (user sees results in <10ms)
async for tier, depth_map in provider.estimate_progressive(image):
    if tier == 1:
        send_to_frontend(depth_map)  # <10ms!
    elif tier == 2:
        send_to_frontend(depth_map)  # ~150ms, better quality

# ❌ BAD: Wait for tier 2 only (150ms delay)
depth_map = await provider.estimate_async(image)
send_to_frontend(depth_map)
```

### 4. Singleton Pattern

**Use singleton getters**, don't create instances directly:

```python
# ✅ GOOD: Singleton (500MB total)
provider1 = get_depth_provider()
provider2 = get_depth_provider()  # Same instance!

# ❌ BAD: Multiple instances (1500MB total)
provider1 = MiDaSDepthProvider()
provider2 = MiDaSDepthProvider()
provider3 = MiDaSDepthProvider()
```

---

## 🧪 Testing

### Unit Tests

```python
import pytest
from extractors import get_depth_provider, reset_depth_provider

def test_singleton_pattern():
    """Verify singleton pattern works."""
    reset_depth_provider()  # Reset for test

    provider1 = get_depth_provider()
    provider2 = get_depth_provider()

    assert provider1 is provider2  # Same instance

def test_depth_estimation():
    """Test depth estimation."""
    import numpy as np

    provider = get_depth_provider()
    image = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)

    depth_map = provider.estimate(image, use_cache=False)

    assert depth_map.depth.shape == (256, 256)
    assert 0.0 <= depth_map.quality_score <= 1.0
    assert depth_map.metadata["backend"] == "MiDaS"

@pytest.mark.asyncio
async def test_progressive_streaming():
    """Test progressive streaming."""
    from extractors import get_depth_provider_async

    provider = await get_depth_provider_async()
    image = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)

    tiers = []
    async for tier, depth_map in provider.estimate_progressive(image):
        tiers.append(tier)

    assert tiers == [1, 2]  # Tier 1 (heuristic) → Tier 2 (ML)
```

---

## 🐛 Troubleshooting

### Issue: Out of Memory

**Symptom:** `RuntimeError: CUDA out of memory` or system freezes

**Solution:**
```python
# Use CPU instead of GPU
provider = get_depth_provider(device="cpu")

# Or use smaller model
provider = get_depth_provider(model_type="MiDaS_small")

# Clear cache periodically
provider.clear_cache()
```

### Issue: Slow First Call

**Symptom:** First `estimate()` call takes 3-8 seconds

**Solution:** This is expected (lazy loading). Use async API to avoid blocking:

```python
# ✅ GOOD: Non-blocking
provider = await get_depth_provider_async()  # Loads in background

# ❌ BAD: Blocks for 3-8s
provider = get_depth_provider()
depth_map = provider.estimate(image)  # First call loads model
```

### Issue: Low Cache Hit Rate

**Symptom:** `cache_stats()` shows <50% hit rate

**Solution:**
```python
# Ensure use_cache=True (default)
depth_map = provider.estimate(image, use_cache=True)

# Check if images are changing (cache uses image hash)
print(f"Image hash: {hash(image.tobytes())}")
```

### Issue: Backend Not Available

**Symptom:** Falls back to heuristic estimation

**Solution:**
```bash
# Install missing dependencies
pip install torch torchvision
pip install timm  # For MiDaS
pip install git+https://github.com/facebookresearch/segment-anything.git  # For SAM
```

---

## 📚 API Reference

### DepthProvider

```python
class DepthProvider:
    def estimate(
        self,
        image: np.ndarray,
        use_cache: bool = True
    ) -> DepthMap:
        """Estimate depth map (sync)."""

    async def estimate_async(
        self,
        image: np.ndarray,
        use_cache: bool = True
    ) -> DepthMap:
        """Estimate depth map (async)."""

    async def estimate_progressive(
        self,
        image: np.ndarray
    ) -> AsyncIterator[Tuple[int, DepthMap]]:
        """Stream tier 1 → tier 2 results."""

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""

    def clear_cache(self) -> None:
        """Clear LRU cache."""
```

### SegmentationProvider

```python
class SegmentationProvider:
    def segment(
        self,
        image: np.ndarray,
        prompt: Optional[np.ndarray] = None,
        use_cache: bool = True
    ) -> SegmentationMask:
        """Segment image (sync)."""

    async def segment_async(
        self,
        image: np.ndarray,
        prompt: Optional[np.ndarray] = None,
        use_cache: bool = True
    ) -> SegmentationMask:
        """Segment image (async)."""

    async def segment_progressive(
        self,
        image: np.ndarray,
        prompt: Optional[np.ndarray] = None
    ) -> AsyncIterator[Tuple[int, SegmentationMask]]:
        """Stream tier 1 → tier 2 results."""
```

### Helper Functions

```python
def get_depth_provider(
    model_type: str = "auto",
    device: str = "auto"
) -> DepthProvider:
    """Get singleton depth provider."""

async def get_depth_provider_async(
    model_type: str = "auto",
    device: str = "auto"
) -> DepthProvider:
    """Get singleton depth provider (async)."""

def get_segmentation_provider(
    backend: str = "auto",
    device: str = "auto"
) -> SegmentationProvider:
    """Get singleton segmentation provider."""

async def get_segmentation_provider_async(
    backend: str = "auto",
    device: str = "auto"
) -> SegmentationProvider:
    """Get singleton segmentation provider (async)."""
```

---

## 🎓 Related Documentation

- [Phase 1 MVP Summary](../architecture/PHASE1_MVP_SUMMARY.md) - Preprocessing providers foundation
- [Phase 2 Async API Summary](../architecture/PHASE2_ASYNC_API_SUMMARY.md) - Async progressive loading
- [Atomic Streaming Summary](../architecture/ATOMIC_STREAMING_SUMMARY.md) - Integration with atomic streaming
- [Progressive Streaming Preprocessing Architecture](../architecture/PROGRESSIVE_STREAMING_PREPROCESSING.md)

---

## 🎯 Next Steps

1. **Try the demos:**
   ```bash
   python examples/demo_phase1_providers.py          # Singleton providers
   python examples/demo_phase2_async_api.py          # Async progressive API
   python examples/demo_atomic_streaming_with_preprocessing.py  # Full integration
   ```

2. **Integrate into your extractor:**
   - Add `get_depth_provider()` or `get_segmentation_provider()` to `__init__`
   - Use `estimate(image, use_cache=True)` in your extraction logic
   - Add preprocessing metadata to results

3. **Enable atomic streaming:**
   ```bash
   export ATOMIC_STREAMING_ENABLED=true  # Default
   ```

4. **Monitor performance:**
   ```python
   stats = provider.get_cache_stats()
   print(f"Cache hit rate: {stats['hit_rate']*100:.1f}%")
   ```

---

**Questions?** See [docs/README.md](../README.md) or check [examples/](../examples/)

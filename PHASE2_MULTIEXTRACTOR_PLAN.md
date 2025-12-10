# Phase 2: Multi-Extractor Color Pipeline - Implementation Plan

**Date:** 2025-12-10
**Status:** Ready to implement
**Prerequisites:** Phase 1 (Streaming Metrics) COMPLETE ✅

---

## 🎯 Goal

Enable multiple color extractors to run in parallel and aggregate results with Delta-E deduplication, confidence-weighted merging, and provenance tracking.

---

## 📋 Current State Analysis

### Existing Infrastructure ✅

**Already Built:**
1. ✅ `ColorAggregator` - Delta-E deduplication (`src/copy_that/tokens/color/aggregator.py`)
2. ✅ Multiple extractors:
   - `extractor.py` - Claude Sonnet 4.5 AI extraction
   - `openai_extractor.py` - GPT-4 Vision extraction
   - `cv_extractor.py` - Computer vision extraction
   - `clustering.py` - K-means clustering
3. ✅ `AggregatedColorToken` - Provenance tracking
4. ✅ `TokenLibrary` - Library statistics

**What's Missing:**
- ❌ Orchestrator to run extractors in parallel
- ❌ Configuration for which extractors to use
- ❌ Performance comparison/benchmarking
- ❌ Frontend integration for multi-extractor results

---

## 🏗️ Architecture Design

### High-Level Flow

```
┌─────────────────────────────────────────────┐
│  Image Upload                               │
└─────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│  Multi-Extractor Orchestrator               │
│  - Runs extractors in parallel             │
│  - Collects results asynchronously          │
└─────────────────────────────────────────────┘
       ↓          ↓          ↓          ↓
   ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
   │ Claude │ │ GPT-4  │ │ K-means│ │  CV    │
   │Sonnet  │ │ Vision │ │Cluster │ │Extract │
   └────────┘ └────────┘ └────────┘ └────────┘
       ↓          ↓          ↓          ↓
┌─────────────────────────────────────────────┐
│  ColorAggregator                            │
│  - Delta-E deduplication (ΔE < 2.3)        │
│  - Confidence-weighted merging              │
│  - Provenance tracking                      │
└─────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│  TokenLibrary                               │
│  - Deduplicated color tokens                │
│  - Statistics (counts, confidence ranges)   │
│  - Ready for database storage               │
└─────────────────────────────────────────────┘
```

---

## 📁 File Structure

### New Files to Create

```
src/copy_that/
├── extractors/
│   └── color/
│       ├── __init__.py              (update exports)
│       ├── extractor.py             (existing - Claude)
│       ├── openai_extractor.py      (existing - GPT-4)
│       ├── cv_extractor.py          (existing - CV)
│       ├── clustering.py            (existing - K-means)
│       ├── base.py                  (NEW - Base extractor interface)
│       └── orchestrator.py          (NEW - Multi-extractor orchestrator)
├── tokens/
│   └── color/
│       ├── aggregator.py            (existing - Delta-E dedup)
│       └── __init__.py              (existing)
└── interfaces/
    └── api/
        ├── colors.py                (update endpoint)
        └── extraction.py            (NEW - Multi-extractor endpoint)
```

---

## 🔧 Implementation Steps

### Step 1: Create Base Extractor Interface (30 min)

**File:** `src/copy_that/extractors/color/base.py`

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol

@dataclass
class ExtractionResult:
    """Result from a single color extractor"""
    colors: list[ExtractedColorToken]
    extractor_name: str
    execution_time_ms: float
    confidence_range: tuple[float, float]

class ColorExtractorProtocol(Protocol):
    """Protocol for color extractors"""

    @property
    def name(self) -> str:
        """Extractor name for provenance tracking"""
        ...

    async def extract(self, image_data: bytes) -> ExtractionResult:
        """Extract colors from image"""
        ...
```

**Purpose:**
- Standardize interface for all extractors
- Enable swappable extractors
- Track performance metrics

---

### Step 2: Update Existing Extractors (1 hour)

**Files to modify:**
- `extractor.py` - Add `name` property, wrap results in `ExtractionResult`
- `openai_extractor.py` - Same updates
- `cv_extractor.py` - Same updates
- `clustering.py` - Create extractor wrapper

**Example:**
```python
class ClaudeColorExtractor:
    @property
    def name(self) -> str:
        return "claude_sonnet_4.5"

    async def extract(self, image_data: bytes) -> ExtractionResult:
        start = time.time()
        colors = await self._extract_colors(image_data)
        duration = (time.time() - start) * 1000

        return ExtractionResult(
            colors=colors,
            extractor_name=self.name,
            execution_time_ms=duration,
            confidence_range=(
                min(c.confidence for c in colors),
                max(c.confidence for c in colors)
            )
        )
```

---

### Step 3: Create Orchestrator (1 hour)

**File:** `src/copy_that/extractors/color/orchestrator.py`

```python
class MultiExtractorOrchestrator:
    """Run multiple color extractors in parallel and aggregate"""

    def __init__(
        self,
        extractors: list[ColorExtractorProtocol],
        aggregator: ColorAggregator,
        max_concurrent: int = 4
    ):
        self.extractors = extractors
        self.aggregator = aggregator
        self.max_concurrent = max_concurrent

    async def extract_all(
        self,
        image_data: bytes,
        image_id: str
    ) -> TokenLibrary:
        """Run all extractors and aggregate results"""

        # 1. Run extractors in parallel
        results = await asyncio.gather(*[
            extractor.extract(image_data)
            for extractor in self.extractors
        ])

        # 2. Aggregate with ColorAggregator
        for result in results:
            for color in result.colors:
                self.aggregator.add_color(
                    color,
                    image_id=f"{image_id}_{result.extractor_name}"
                )

        # 3. Return deduplicated library
        return self.aggregator.get_library()
```

**Features:**
- Parallel execution with asyncio
- Error handling per extractor
- Performance tracking
- Fallback if some extractors fail

---

### Step 4: Create API Endpoint (30 min)

**File:** `src/copy_that/interfaces/api/extraction.py`

```python
@router.post("/extract/colors/multi")
async def extract_colors_multi(
    file: UploadFile,
    extractors: list[str] = Query(["claude", "kmeans", "cv"]),
    delta_e_threshold: float = Query(2.3)
):
    """
    Extract colors using multiple extractors in parallel

    Args:
        file: Image file to extract from
        extractors: List of extractor names to use
        delta_e_threshold: Delta-E threshold for deduplication

    Returns:
        TokenLibrary with aggregated, deduplicated colors
    """
    # 1. Load extractors by name
    extractor_instances = load_extractors(extractors)

    # 2. Create orchestrator
    orchestrator = MultiExtractorOrchestrator(
        extractors=extractor_instances,
        aggregator=ColorAggregator(delta_e_threshold)
    )

    # 3. Extract
    image_data = await file.read()
    library = await orchestrator.extract_all(image_data, file.filename)

    # 4. Return results
    return library.to_dict()
```

**Benefits:**
- Single endpoint for all extractors
- Configurable extractor selection
- Adjustable deduplication threshold

---

### Step 5: Frontend Integration (1 hour)

**Update:** `frontend/src/api/client.ts`

```typescript
async extractColorsMulti(
  file: File,
  extractors: string[] = ['claude', 'kmeans', 'cv']
): Promise<TokenLibrary> {
  const formData = new FormData()
  formData.append('file', file)

  const params = new URLSearchParams()
  extractors.forEach(e => params.append('extractors', e))

  const response = await fetch(
    `${this.baseURL}/extract/colors/multi?${params}`,
    {
      method: 'POST',
      body: formData
    }
  )

  return response.json()
}
```

**Update:** `frontend/src/components/ImageUploader.tsx`

Add toggle for multi-extractor mode:
```tsx
const [useMultiExtractor, setUseMultiExtractor] = useState(true)
const [selectedExtractors, setSelectedExtractors] = useState([
  'claude', 'kmeans', 'cv'
])
```

---

## 📊 Performance Expectations

### Single Extractor (Current)
- **Claude:** 2-5s per image
- **Result:** 10-20 colors

### Multi-Extractor (Phase 2)
- **Claude + K-means + CV:** 2-5s total (parallel)
- **Result:** 30-50 colors → deduplicated to 15-25 colors
- **Confidence:** Higher (multiple sources validate)
- **Coverage:** Better (different extractors catch different colors)

### Deduplication Impact
- **Before:** 50 colors from 3 extractors
- **After (ΔE < 2.3):** 20 colors (60% reduction)
- **Provenance:** Track which extractors found each color

---

## 🧪 Testing Strategy

### Unit Tests

```python
# test_orchestrator.py
async def test_parallel_extraction():
    """Test extractors run in parallel"""
    orchestrator = MultiExtractorOrchestrator([
        MockExtractor("mock1"),
        MockExtractor("mock2")
    ], ColorAggregator())

    result = await orchestrator.extract_all(image_data, "test")
    assert len(result.tokens) > 0

async def test_extractor_failure_graceful():
    """Test one extractor failing doesn't break others"""
    orchestrator = MultiExtractorOrchestrator([
        MockExtractor("good"),
        FailingExtractor("bad")
    ], ColorAggregator())

    result = await orchestrator.extract_all(image_data, "test")
    # Should still have results from good extractor
    assert len(result.tokens) > 0
```

### Integration Tests

```python
# test_api_multi_extract.py
async def test_multi_extract_endpoint():
    """Test /extract/colors/multi endpoint"""
    response = client.post(
        "/extract/colors/multi",
        files={"file": ("test.jpg", image_bytes)},
        params={"extractors": ["claude", "kmeans"]}
    )

    assert response.status_code == 200
    data = response.json()
    assert "tokens" in data
    assert "statistics" in data
```

---

## 📈 Success Metrics

### Phase 2 Complete When:
- [ ] Orchestrator runs 3+ extractors in parallel
- [ ] ColorAggregator deduplicates with Delta-E
- [ ] API endpoint `/extract/colors/multi` working
- [ ] Frontend toggle for multi-extractor mode
- [ ] Tests passing (unit + integration)
- [ ] Performance <= 5s for 3 extractors
- [ ] Documentation updated

### Key Metrics to Track:
- **Extraction Time:** Target <5s for 3 extractors
- **Color Count:** 15-25 deduplicated colors
- **Deduplication Rate:** 50-70% reduction
- **Confidence:** Average >0.75
- **Provenance Coverage:** 80%+ colors from 2+ extractors

---

## 🚀 Deployment Strategy

### Phase 2A: Backend Only (Week 1)
1. Implement orchestrator
2. Update extractors
3. Create API endpoint
4. Test backend thoroughly

### Phase 2B: Frontend Integration (Week 2)
1. Add multi-extractor toggle
2. Display provenance in UI
3. Show extractor performance stats
4. A/B test vs single extractor

### Phase 2C: Optimization (Week 3)
1. Cache extractor results
2. Smart extractor selection
3. Adaptive thresholds
4. Performance tuning

---

## 🔗 Dependencies

### Required Packages (Already Installed)
- ✅ `coloraide` - Delta-E calculations
- ✅ `asyncio` - Parallel execution
- ✅ `anthropic` - Claude API
- ✅ `openai` - GPT-4 Vision API
- ✅ `opencv-python` - CV extraction
- ✅ `scikit-learn` - K-means clustering

### Optional Enhancements
- `numpy` - Faster color math
- `pillow` - Image preprocessing
- `redis` - Result caching

---

## 💡 Future Enhancements

### Phase 2+: Advanced Features
1. **Smart Extractor Selection**
   - Analyze image characteristics
   - Choose best extractors automatically
   - Example: Photo → Claude + K-means, UI screenshot → CV + GPT-4

2. **Adaptive Thresholds**
   - Adjust Delta-E based on color distribution
   - Tight clustering → higher threshold
   - Sparse palette → lower threshold

3. **Confidence Calibration**
   - Learn from user feedback
   - Adjust extractor weights
   - Improve aggregation accuracy

4. **Result Caching**
   - Cache extractor results by image hash
   - Skip redundant extractions
   - Serve cached results instantly

---

## 📞 Next Steps

### To Start Phase 2:
1. Read this plan
2. Review existing code:
   - `src/copy_that/tokens/color/aggregator.py`
   - `src/copy_that/extractors/color/`
3. Begin with Step 1 (Base Extractor Interface)
4. Follow steps sequentially
5. Test after each step

### Estimated Time:
- **Backend:** 3-4 hours
- **Frontend:** 1-2 hours
- **Testing:** 1 hour
- **Total:** 5-7 hours (1 focused day)

---

## 📚 References

- `SESSION_COMPLETE_2025_12_10.md` - Phase 1 completion
- `SESSION_HANDOFF_2025_12_10_FINAL.md` - Original handoff
- `src/copy_that/tokens/color/aggregator.py` - Existing aggregator
- `src/copy_that/extractors/color/` - Existing extractors

---

**Status:** Ready to implement
**Next Session:** Start with Step 1 (Base Extractor Interface)
**Context:** 117K/200K tokens used (58%), fresh start recommended

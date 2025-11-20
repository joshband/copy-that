# Multi-Extractor Ensemble Architecture

> **✅ Integration Status (2025-11-05)**: The MultiExtractor class is fully integrated and production ready! The backend now uses a 3-extractor ensemble: OpenCV CV + GPT-4 Vision + Claude Sonnet 4.5. See V2.2B_INTEGRATION_COMPLETE.md for details.

**Version**: v2.2b ✅ COMPLETE (November 2025)
**Code Status**: ✅ Complete (extractors/extractors/ai/multi_extractor.py)
**Backend Integration**: ✅ Integrated and Working
**Production Status**: ✅ Production Ready (3-extractor ensemble)
**Architecture**: Many-to-Many with Progressive Enhancement

---

## Current Production Configuration (v2.2b)

**Active Ensemble**: 3 extractors
- **Tier 1 (FAST)**: OpenCV CV baseline (~1.04s, free)
- **Tier 3 (SLOW)**: GPT-4 Vision (~32 tokens, $0.02/image)
- **Tier 3 (SLOW)**: Claude Sonnet 4.5 (~19 tokens, $0.05/image)

**Performance**:
- Time to first result: 1.04s (CV)
- Total extraction time: 64s (full AI ensemble)
- Cost per image: $0.07 (with both AI models)
- Confidence: Up to 95% with unanimous voting

**Integration Test**: `examples/test_v2.2b_integration.py` (285 lines, all passing)

---

## Overview

The multi-extractor system orchestrates **multiple extraction methods** (CV libraries, AI models, specialized extractors) to produce high-confidence design tokens through:

1. **Tiered Progressive Execution** - Fast extractors run first, slow ones later
2. **Weighted Voting & Consensus** - Multiple methods vote on each token value
3. **Cross-Validation** - Agreement → high confidence, disagreement → conflict flagging
4. **Cost Management** - Budget limits, cost tracking, graceful degradation

This replaces the "dual" (CV + AI) approach with a flexible **ensemble** that can combine any number of extractors.

---

## Why Multi-Extractor?

### Traditional Approach (Single Extractor)
```
Image → OpenCV → Tokens
```
- **Pros**: Fast, simple
- **Cons**: No validation, confidence unknown

### Dual Approach (CV + AI)
```
Image → OpenCV (required) → Tokens
     → GPT-4V (optional) → Enhanced Tokens
```
- **Pros**: Semantic enhancement, validation
- **Cons**: Limited to 2 methods, single AI provider

### Multi-Extractor Ensemble (v2.2)
```
Image → Tier 1: [OpenCV, scikit-image, PIL] → Fast CV results (300ms)
     → Tier 2: [LLaVA local, specialized CV] → Enhanced results (1.5s)
     → Tier 3: [GPT-4V, Claude, Gemini] → AI-enhanced with high confidence (4s)
```
- **Pros**: Flexible, high confidence through voting, cost-controlled, progressive UX
- **Cons**: More complex orchestration

---

## Architecture

### Extractor Tiers

Extractors are grouped by performance to enable **progressive enhancement**:

| Tier | Type | Speed | Cost | Use Case |
|------|------|-------|------|----------|
| **1 - FAST** | CV (OpenCV, PIL) | <500ms | $0 | Required baseline, immediate results |
| **2 - MEDIUM** | Local AI, specialized CV | 1-2s | $0 | Enhanced detection, offline capable |
| **3 - SLOW** | API-based AI (GPT-4V, Claude) | 2-5s | $0.01-0.02 | Semantic understanding, validation |
| **4 - VERY_SLOW** | Complex AI processing | 5-10s | $0.03-0.05 | Deep analysis, component detection |

**Progressive Flow**:
```
t=0ms:    Request received
t=300ms:  Tier 1 complete → stream CV results to frontend
t=1.5s:   Tier 2 complete → stream enhanced results
t=4.2s:   Tier 3 complete → stream final high-confidence results
```

---

## Weighted Voting & Consensus

Each extractor contributes votes with assigned weights. The ensemble builds consensus through weighted voting.

### Example: Color Token Extraction

**Extractor Results**:
```python
# Tier 1: OpenCV
opencv_result = {"primary": "#F15925"}  # weight: 1.0

# Tier 2: Local LLaVA
llava_result = {"primary": "#F25A27"}  # weight: 0.9 (slightly less confident)

# Tier 3: GPT-4 Vision
gpt4v_result = {"primary": "#F15925"}  # weight: 1.2 (higher semantic confidence)

# Tier 3: Claude Vision
claude_result = {"primary": "#F15925"}  # weight: 1.1
```

**Voting Process**:
```
Color: #F15925
  - OpenCV: 1.0
  - GPT-4V: 1.2
  - Claude: 1.1
  Total: 3.3

Color: #F25A27
  - LLaVA: 0.9
  Total: 0.9

Consensus: #F15925 (3.3 / 4.2 = 78.6% agreement)
```

**Output**:
```json
{
  "palette": {
    "primary": {
      "hex": "#F15925",
      "confidence": 0.93,
      "votes": 4,
      "consensus": true,
      "agreement": 0.786
    }
  }
}
```

---

## Configuration

### Extractor Configuration

Each extractor is configured with:

```python
from extractors.ai.multi_extractor import ExtractorConfig, ExtractorTier

ExtractorConfig(
    name="opencv_color",              # Unique identifier
    extract_fn=opencv_color_fn,       # Extraction function
    tier=ExtractorTier.FAST,          # Performance tier
    weight=1.0,                       # Voting weight (0-2)
    cost_per_call=0.0,                # Cost in dollars
    enabled=True,                     # Enable/disable
    timeout_seconds=None,             # Optional timeout
    required=False                    # If True, failure stops pipeline
)
```

---

### Example: Full Configuration

```python
from extractors.ai.multi_extractor import MultiExtractor, ExtractorConfig, ExtractorTier
from extractors.color_extractor import kmeans_palette, role_map_from_palette
from extractors.ai.gpt4_vision_extractor import GPT4VisionExtractor
import os

# Configure ensemble
extractors = [
    # Tier 1: Fast CV (always enabled, required)
    ExtractorConfig(
        name="opencv_color",
        extract_fn=lambda imgs: {"palette": role_map_from_palette(kmeans_palette(imgs[0], k=12))},
        tier=ExtractorTier.FAST,
        weight=1.0,
        cost_per_call=0.0,
        enabled=True,
        required=True  # Failure stops extraction
    ),

    ExtractorConfig(
        name="opencv_spacing",
        extract_fn=extract_spacing_fn,
        tier=ExtractorTier.FAST,
        weight=1.0,
        enabled=True
    ),

    # Tier 2: Local AI (optional, offline)
    ExtractorConfig(
        name="llava_local",
        extract_fn=llava_extract_fn,
        tier=ExtractorTier.MEDIUM,
        weight=0.9,
        cost_per_call=0.0,
        enabled=bool(os.getenv("LLAVA_MODEL_PATH"))  # Only if model available
    ),

    # Tier 3: API-based AI (optional, expensive)
    ExtractorConfig(
        name="gpt4_vision",
        extract_fn=GPT4VisionExtractor().extract,
        tier=ExtractorTier.SLOW,
        weight=1.2,
        cost_per_call=0.02,
        enabled=bool(os.getenv("OPENAI_API_KEY"))
    ),

    ExtractorConfig(
        name="claude_vision",
        extract_fn=claude_vision_fn,
        tier=ExtractorTier.SLOW,
        weight=1.1,
        cost_per_call=0.015,
        enabled=bool(os.getenv("ANTHROPIC_API_KEY"))
    ),

    ExtractorConfig(
        name="gemini_vision",
        extract_fn=gemini_vision_fn,
        tier=ExtractorTier.SLOW,
        weight=1.0,
        cost_per_call=0.01,
        enabled=bool(os.getenv("GOOGLE_API_KEY"))
    ),
]

# Create multi-extractor
multi = MultiExtractor(
    extractors=extractors,
    max_cost=0.10,  # Budget limit: $0.10
    enable_cross_validation=True,
    confidence_threshold=0.7
)

# Extract progressively
async for result in multi.extract_progressive(images):
    tier = result["_metadata"]["tier"]
    confidence = result["palette"]["primary"]["confidence"]
    cost = result["_metadata"]["total_cost"]

    print(f"Tier {tier} complete: confidence={confidence:.2f}, cost=${cost:.4f}")

    # Stream to frontend
    await websocket.send_json(result)
```

---

## Progressive Streaming

### Backend (FastAPI WebSocket)

```python
from fastapi import WebSocket
from extractors.ai.multi_extractor import MultiExtractor

@app.websocket("/extract/progressive")
async def extract_progressive(websocket: WebSocket):
    await websocket.accept()

    # Receive images from client
    data = await websocket.receive_json()
    images = load_images(data["images"])

    # Configure extractors
    multi = MultiExtractor(extractors, max_cost=0.10)

    # Stream results progressively
    async for result in multi.extract_progressive(images):
        await websocket.send_json({
            "stage": result["_metadata"]["stage"],
            "tier": result["_metadata"]["tier"],
            "tokens": result,
            "confidence": result["palette"]["primary"]["confidence"],
            "cost": result["_metadata"]["total_cost"]
        })
```

### Frontend (React)

```typescript
const ws = new WebSocket("ws://localhost:8000/api/v1/extract/progressive");

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.tier === 1) {
        // Tier 1 (CV): Show immediate results
        setTokens(data.tokens);
        setStatus("CV extraction complete - enhancing with AI...");
        setConfidence(data.confidence);  // ~0.75
    }

    if (data.tier === 2) {
        // Tier 2 (local AI): Enhanced results
        setTokens(data.tokens);
        setStatus("Local AI enhancement complete - validating...");
        setConfidence(data.confidence);  // ~0.85
    }

    if (data.tier === 3) {
        // Tier 3 (API AI): Final high-confidence results
        setTokens(data.tokens);
        setStatus(`Complete! Confidence: ${(data.confidence * 100).toFixed(0)}%`);
        setConfidence(data.confidence);  // ~0.95
        setCost(data.cost);
    }
};
```

---

## Cost Management

### Budget Limits

```python
# Maximum $0.50 total cost
multi = MultiExtractor(extractors, max_cost=0.50)

async for result in multi.extract_progressive(images):
    cost = result["_metadata"]["total_cost"]
    if cost >= 0.45:  # 90% of budget
        logger.warning(f"⚠️  Approaching budget limit: ${cost:.4f} / $0.50")
```

**Behavior when budget exceeded**:
- Tier 1 (free CV) always runs
- Tier 2 (local AI) runs if budget allows
- Tier 3+ (expensive AI) skipped if budget exceeded
- Returns best available result with warning

---

### Cost Tracking

```python
# After extraction
total_cost = result["_metadata"]["total_cost"]  # e.g., 0.047
extractors_run = result["_metadata"]["extractors_completed"]  # e.g., 5

print(f"Total cost: ${total_cost:.4f} ({extractors_run} extractors)")

# Breakdown by extractor
for extractor in extractors:
    if extractor.cost_per_call > 0:
        print(f"  {extractor.name}: ${extractor.cost_per_call:.3f}")
```

---

## Confidence Scoring

### Agreement-Based Confidence

```
Confidence = 0.5 + (agreement_percentage × 0.45)

Examples:
- 100% agreement → 0.95 confidence (very high)
- 80% agreement → 0.86 confidence (high)
- 60% agreement → 0.77 confidence (medium)
- 40% agreement → 0.68 confidence (below threshold)
```

### Conflict Handling

When extractors disagree significantly:

```json
{
  "palette": {
    "primary": {
      "hex": "#F15925",
      "confidence": 0.65,
      "votes": 5,
      "consensus": false,
      "conflict": {
        "status": "low_agreement",
        "votes": [
          {"extractor": "opencv", "value": "#F15925", "weight": 1.0},
          {"extractor": "gpt4v", "value": "#F25A27", "weight": 1.2},
          {"extractor": "claude", "value": "#F15925", "weight": 1.1}
        ],
        "recommendation": "manual_review"
      }
    }
  }
}
```

---

## Adding New Extractors

### 1. Create Extractor Function

```python
def my_custom_extractor(images: List[np.ndarray]) -> Dict[str, Any]:
    """Custom color extraction using scikit-image."""
    from skimage.color import rgb2lab

    # Your extraction logic
    palette = extract_colors_skimage(images)

    return {"palette": palette}
```

### 2. Add to Configuration

```python
extractors.append(
    ExtractorConfig(
        name="skimage_color",
        extract_fn=my_custom_extractor,
        tier=ExtractorTier.MEDIUM,  # Slower than OpenCV
        weight=0.95,  # Slightly less weight
        cost_per_call=0.0,  # Free (local)
        enabled=True
    )
)
```

### 3. The ensemble automatically:
- Runs your extractor in Tier 2 (after fast CV)
- Includes votes in consensus building
- Cross-validates against other extractors
- Streams results progressively

---

## Comparison: Single vs Dual vs Multi

| Feature | Single (CV only) | Dual (CV + AI) | Multi (Ensemble) |
|---------|------------------|----------------|------------------|
| **Extractors** | 1 | 2 | N (unlimited) |
| **Confidence** | ~70% | ~85-95% | ~95% (voting) |
| **Speed** | 300ms | 2-5s | Progressive |
| **Cost** | $0 | $0.02 | Tiered ($0-0.10) |
| **Validation** | None | CV ↔ AI | All ↔ All |
| **Flexibility** | Fixed | Fixed | Configurable |
| **Offline** | ✅ | ⚠️ (CV fallback) | ✅ (Tier 1+2) |
| **Progressive UX** | ❌ | ❌ | ✅ |

---

## Best Practices

### 1. Always Include Required CV Extractor

```python
ExtractorConfig(
    name="opencv_baseline",
    extract_fn=opencv_fn,
    tier=ExtractorTier.FAST,
    required=True  # ← Ensures baseline result
)
```

### 2. Set Realistic Budget Limits

```python
# Development
multi = MultiExtractor(extractors, max_cost=0.01)  # Cheap, may skip AI

# Production
multi = MultiExtractor(extractors, max_cost=0.10)  # Full ensemble
```

### 3. Weight Extractors Appropriately

```
CV extractors:        1.0 (baseline)
Local AI:             0.8-1.0 (good but unvalidated)
API AI (GPT-4V):      1.1-1.3 (high semantic quality)
Specialized CV:       0.9-1.1 (depends on domain)
```

### 4. Enable Graceful Degradation

```python
# Optional extractors don't stop pipeline
ExtractorConfig(
    name="expensive_ai",
    tier=ExtractorTier.SLOW,
    required=False  # ← Failure is logged but not fatal
)
```

### 5. Monitor Confidence and Review Conflicts

```python
result = await multi.extract_progressive(images).asend(None)

for token_name, token_data in result["palette"].items():
    if token_data["confidence"] < 0.7:
        print(f"⚠️  Low confidence for {token_name}: {token_data['confidence']}")

    if not token_data.get("consensus"):
        print(f"🔍 Conflict detected for {token_name} - manual review recommended")
```

---

## Future Enhancements

- [ ] **Auto-weighting**: ML model learns optimal weights from historical data
- [ ] **Adaptive budgets**: Spend more on complex images, less on simple ones
- [ ] **Result caching**: Cache tier results to avoid re-running expensive extractors
- [ ] **A/B testing**: Compare extractor performance on labeled datasets
- [ ] **Real-time monitoring**: Dashboard showing extractor performance, cost, confidence

---

## Summary

The **multi-extractor ensemble** provides:

✅ **Flexibility** - Add any number of CV libraries, AI models, or custom extractors
✅ **High Confidence** - Weighted voting and cross-validation
✅ **Progressive UX** - Fast results first, enhanced results later
✅ **Cost Control** - Budget limits, tiered execution
✅ **Graceful Degradation** - Always returns best available result
✅ **Offline Capable** - Tier 1+2 work without internet

**Recommended Configuration**:
- Tier 1: OpenCV (required, baseline)
- Tier 2: Local AI if available
- Tier 3: 1-2 API-based AI models for validation

This architecture scales from **CV-only** (free, fast) to **full ensemble** (high confidence, validated) based on budget and requirements.

---

**Related Documentation**:
- [multi_extractor.py](../../extractors/extractors/ai/multi_extractor.py) - Implementation
- [CV vs AI Architecture](../architecture/CV_VS_AI_ARCHITECTURE.md) - Design decisions
- [DUAL_EXTRACTION.md](./DUAL_EXTRACTION.md) - Legacy dual extraction guide

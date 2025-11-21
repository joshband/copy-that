# Progressive Extraction Quick Start

> **Status update (2025-11-05)**: The live backend currently supports CV-only progressive streaming. Use the AI and multi-extractor steps below as forward-looking guidance.

**Get started with v2.2 asynchronous progressive extraction in 5 minutes**

---

## What is Progressive Extraction?

Progressive extraction streams design token results **as they become available** instead of waiting for everything to complete:

```
Traditional:  Upload → Wait 3s → Get results

Progressive:  Upload → Get CV results (300ms)
                    → Get enhanced results (1.5s)
                    → Get AI-validated results (4s)
```

**Benefits**: Faster perceived performance, non-blocking UX, graceful degradation

---

## Quick Start (Backend)

### 1. Install Dependencies

```bash
# Core dependencies (already installed)
pip install fastapi websockets numpy opencv-python

# Optional: AI enhancement
export OPENAI_API_KEY="sk-..."  # For GPT-4 Vision
export ANTHROPIC_API_KEY="sk-..."  # For Claude Vision
```

### 2. Basic Usage (Python)

```python
from extractors.ai.multi_extractor import (
    MultiExtractor,
    ExtractorConfig,
    ExtractorTier
)
from extractors.color_extractor import kmeans_palette, role_map_from_palette
import numpy as np
import cv2

# Load images
images = [cv2.imread("ref1.png"), cv2.imread("ref2.png")]

# Configure extractors
extractors = [
    # Tier 1: Fast CV (required)
    ExtractorConfig(
        name="opencv_color",
        extract_fn=lambda imgs: {
            "palette": role_map_from_palette(kmeans_palette(imgs[0], k=12))
        },
        tier=ExtractorTier.FAST,
        weight=1.0,
        required=True
    )
]

# Create multi-extractor
multi = MultiExtractor(
    extractors=extractors,
    max_cost=0.10,
    enable_cross_validation=True
)

# Extract progressively
async for result in multi.extract_progressive(images):
    tier = result["_metadata"]["tier"]
    confidence = result["palette"]["primary"]["confidence"]

    print(f"Tier {tier}: Confidence {confidence:.2f}")
    print(f"Primary color: {result['palette']['primary']['hex']}")
```

**Output**:
```
Tier 1: Confidence 0.75
Primary color: #F15925
```

---

## Quick Start (Frontend)

### React Component

```typescript
import { useState, useEffect } from 'react';

function TokenExtractor() {
    const [tokens, setTokens] = useState(null);
    const [status, setStatus] = useState("idle");
    const [confidence, setConfidence] = useState(0);

    const extractTokens = (imageFiles: File[]) => {
        const ws = new WebSocket("ws://localhost:8000/api/v1/extract/progressive");

        ws.onopen = async () => {
            setStatus("extracting");

            // Convert files to base64
            const base64Images = await Promise.all(
                imageFiles.map(file => fileToBase64(file))
            );

            // Send extraction request
            ws.send(JSON.stringify({
                action: "extract",
                images: base64Images,
                use_ai: true
            }));
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);

            // Update UI progressively
            setTokens(data.tokens);
            setConfidence(data.confidence);

            if (data.tier === 1) {
                setStatus("CV extraction complete - enhancing with AI...");
            } else if (data.tier === 3) {
                setStatus(`Complete! ${(data.confidence * 100).toFixed(0)}% confidence`);
            }
        };

        ws.onclose = () => setStatus("complete");
        ws.onerror = () => setStatus("error");
    };

    return (
        <div>
            <FileUpload onChange={extractTokens} />

            <Status>{status}</Status>

            {tokens && (
                <TokenPreview
                    tokens={tokens}
                    confidence={confidence}
                />
            )}
        </div>
    );
}

function fileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result as string);
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}
```

---

## Adding AI Enhancement

### Step 1: Set API Key

```bash
# Option 1: Environment variable
export OPENAI_API_KEY="sk-..."

# Option 2: .env file
echo "OPENAI_API_KEY=sk-..." >> backend/.env
```

### Step 2: Add AI Extractor

```python
from extractors.ai.gpt4_vision_extractor import GPT4VisionExtractor

extractors.append(
    ExtractorConfig(
        name="gpt4_vision",
        extract_fn=GPT4VisionExtractor().extract,
        tier=ExtractorTier.SLOW,
        weight=1.2,
        cost_per_call=0.02,
        enabled=bool(os.getenv("OPENAI_API_KEY"))
    )
)
```

### Step 3: Run Extraction

```python
async for result in multi.extract_progressive(images):
    if result["_metadata"]["tier"] == 1:
        print("✅ CV complete (fast)")
    elif result["_metadata"]["tier"] == 3:
        print("✅ AI complete (high confidence)")
        print(f"   Cost: ${result['_metadata']['total_cost']:.4f}")
```

**Output**:
```
✅ CV complete (fast)
✅ AI complete (high confidence)
   Cost: $0.0200
```

---

## Progressive UI Example

### Show Results as They Arrive

```typescript
function ProgressiveTokenDisplay({ ws }: { ws: WebSocket }) {
    const [results, setResults] = useState<any[]>([]);

    useEffect(() => {
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);

            // Add new result to list (don't replace, append)
            setResults(prev => [...prev, data]);
        };
    }, [ws]);

    return (
        <div>
            {results.map((result, i) => (
                <div key={i} className={`tier-${result.tier}`}>
                    <h3>Tier {result.tier} Results</h3>
                    <p>Confidence: {(result.confidence * 100).toFixed(0)}%</p>
                    <p>Time: {result.elapsed_ms}ms</p>

                    <ColorPalette
                        colors={result.tokens.palette}
                        tier={result.tier}
                    />
                </div>
            ))}
        </div>
    );
}
```

**Visual Output**:
```
┌─────────────────────────────────────┐
│ Tier 1 Results      (300ms)         │
│ Confidence: 75%                     │
│ ███ #F15925  ███ #1C5D6B           │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Tier 3 Results      (4200ms)        │
│ Confidence: 95% ⭐                  │
│ ███ #F15925 "molten-copper"        │
│ ███ #1C5D6B "ocean-deep"           │
└─────────────────────────────────────┘
```

---

## Cost Management

### Set Budget Limit

```python
# Limit: $0.05 total cost
multi = MultiExtractor(extractors, max_cost=0.05)

async for result in multi.extract_progressive(images):
    cost = result["_metadata"]["total_cost"]

    if cost >= 0.045:  # 90% of budget
        print(f"⚠️  Warning: ${cost:.4f} / $0.05 budget used")
```

**Behavior**:
- Tier 1 (free CV) always runs
- Tier 2 (local AI) runs if available
- Tier 3 (expensive AI) skipped if budget exceeded
- Returns best available result with warning

---

## Error Handling

### Graceful Degradation

```python
try:
    async for result in multi.extract_progressive(images):
        # Process result
        process_tokens(result)

except Exception as e:
    # If any tier fails, you still get previous tier's results
    logger.error(f"Extraction error: {e}")
    # result contains best available data before failure
```

### Frontend Error Handling

```typescript
ws.onerror = (error) => {
    console.error("WebSocket error:", error);
    setStatus("error");

    // Fallback: Use traditional polling endpoint
    fetch("/api/v1/extract", {
        method: "POST",
        body: formData
    });
};
```

---

## Testing

### Test Progressive Extraction

```python
import pytest
from extractors.ai.multi_extractor import MultiExtractor, ExtractorConfig, ExtractorTier

@pytest.mark.asyncio
async def test_progressive_extraction():
    """Test that results stream progressively."""

    # Mock extractors
    def mock_fast(imgs):
        return {"palette": {"primary": "#F15925"}}

    def mock_slow(imgs):
        return {"palette": {"primary": {"hex": "#F15925", "name": "molten-copper"}}}

    extractors = [
        ExtractorConfig("fast", mock_fast, ExtractorTier.FAST, weight=1.0),
        ExtractorConfig("slow", mock_slow, ExtractorTier.SLOW, weight=1.2),
    ]

    multi = MultiExtractor(extractors)
    results = []

    async for result in multi.extract_progressive([mock_image]):
        results.append(result)

    # Assert we got 2 progressive results
    assert len(results) == 2
    assert results[0]["_metadata"]["tier"] == 1
    assert results[1]["_metadata"]["tier"] == 3
    assert results[1]["palette"]["primary"]["name"] == "molten-copper"
```

---

## Common Patterns

### Pattern 1: CV-Only (Free, Fast)

```python
# Minimal configuration for development
extractors = [
    ExtractorConfig("opencv", opencv_fn, ExtractorTier.FAST, required=True)
]

multi = MultiExtractor(extractors)

# Returns in ~300ms, no cost
async for result in multi.extract_progressive(images):
    print(f"CV result: {result}")
```

---

### Pattern 2: CV + Single AI (Budget-Friendly)

```python
# One AI model for validation
extractors = [
    ExtractorConfig("opencv", opencv_fn, ExtractorTier.FAST, required=True),
    ExtractorConfig("gpt4v", gpt4v_fn, ExtractorTier.SLOW, cost=0.02),
]

multi = MultiExtractor(extractors, max_cost=0.03)

# Tier 1: CV (300ms, free)
# Tier 3: CV + GPT-4V (4s, $0.02)
```

---

### Pattern 3: Full Ensemble (Production)

```python
# Multiple AI models for high confidence
extractors = [
    ExtractorConfig("opencv", opencv_fn, ExtractorTier.FAST, weight=1.0, required=True),
    ExtractorConfig("llava", llava_fn, ExtractorTier.MEDIUM, weight=0.9),
    ExtractorConfig("gpt4v", gpt4v_fn, ExtractorTier.SLOW, weight=1.2, cost=0.02),
    ExtractorConfig("claude", claude_fn, ExtractorTier.SLOW, weight=1.1, cost=0.015),
]

multi = MultiExtractor(extractors, max_cost=0.10)

# Tier 1: CV (300ms)
# Tier 2: CV + LLaVA (1.5s)
# Tier 3: Full ensemble with 95%+ confidence (4s)
```

---

## Next Steps

1. **Read Full Documentation**:
   - [Multi-Extractor Architecture](./MULTI_EXTRACTOR_ARCHITECTURE.md)
   - [v2.2 Implementation Summary](../development/V2.2_ASYNC_PROGRESSIVE_ARCHITECTURE.md)

2. **Try Examples**:
   - `examples/progressive_extraction_demo.py`
   - `frontend/src/components/ProgressiveExtractor.tsx`

3. **Add Custom Extractors**:
   - See [Adding New Extractors](./MULTI_EXTRACTOR_ARCHITECTURE.md#adding-new-extractors)

4. **Configure for Production**:
   - Set up API keys
   - Configure budget limits
   - Enable monitoring/logging

---

## Troubleshooting

### Issue: WebSocket Connection Failed

```typescript
// Error: WebSocket connection to 'ws://localhost:8000' failed
```

**Solution**: Make sure FastAPI server is running with WebSocket support:
```bash
cd backend
uvicorn main:app --reload
```

---

### Issue: No AI Results

```python
# Only getting Tier 1 (CV) results, no AI enhancement
```

**Solution**: Check API key and AI availability:
```python
from extractors.ai.config import config

print(f"AI enabled: {config.is_ai_enabled}")
print(f"OpenAI key set: {bool(config.openai_api_key)}")
```

---

### Issue: Budget Exceeded

```python
# Warning: Budget exceeded, skipping expensive extractors
```

**Solution**: Increase budget or reduce AI extractors:
```python
# Increase budget
multi = MultiExtractor(extractors, max_cost=0.20)  # Was 0.10

# OR reduce AI extractors
extractors = [opencv_only]  # Remove expensive AI
```

---

## Summary

**Quick Start Checklist**:

✅ Import `MultiExtractor` and `ExtractorConfig`
✅ Configure extractors (at minimum: 1 CV extractor)
✅ Create `MultiExtractor` with budget limit
✅ Use `async for` to stream progressive results
✅ Update UI as each tier completes
✅ Handle errors gracefully (always get best available result)

**5-Minute Setup**:
1. Copy basic example above
2. Load your reference images
3. Run extraction
4. See results in ~300ms (CV) and ~4s (AI-enhanced)

**Need Help?** See [MULTI_EXTRACTOR_ARCHITECTURE.md](./MULTI_EXTRACTOR_ARCHITECTURE.md) for detailed documentation.

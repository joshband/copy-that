# Progressive, Non-Blocking Color Extraction Architecture

## Current State (Blocking)

```
IMAGE → Claude Vision (blocking) → Parse Response →
Compute All Properties (synchronous) → Return All Results

Problem: User sees nothing until all colors processed
Latency: 5-10+ seconds before first color appears
```

---

## Proposed: Streaming Architecture

```
IMAGE
  ↓
Claude Vision (blocking, but unavoidable API constraint)
  ↓
Color Stream Handler (async)
  ├─ Hex Code #1 → Validate → Compute Properties → Store → Emit
  ├─ Hex Code #2 → Validate → Compute Properties → Store → Emit
  ├─ Hex Code #3 → Validate → Compute Properties → Store → Emit
  └─ ... (atomic operations, each can fail independently)
  ↓
WebSocket/SSE → Frontend
  ↓
Frontend (Real-time UI updates)
  ├─ Show color #1 immediately (with skeleton loading)
  ├─ Show color #2 as computed
  └─ Progressive enhancement as colors arrive
```

---

## Architecture Components

### 1. **Async Extraction Pipeline**
**File:** `src/copy_that/application/async_color_extractor.py` (NEW)

```python
from typing import AsyncIterator
from pydantic import BaseModel
import asyncio

class ColorExtractionEvent(BaseModel):
    """Streamed color event"""
    type: str  # "color_parsed", "color_computed", "color_stored", "error"
    color_id: Optional[int]
    hex: str
    data: dict  # Partial or complete ColorToken data
    error: Optional[str]
    progress: {"current": int, "total": int}

async def extract_colors_streaming(
    image_url: str,
    project_id: int,
    max_colors: int = 10
) -> AsyncIterator[ColorExtractionEvent]:
    """
    Stream color extraction events as they complete

    Yields:
        ColorExtractionEvent with incremental updates
    """
    # Step 1: Claude Vision (blocking - API limitation)
    hex_colors = await claude_extract_hex_codes(image_url, max_colors)
    total_colors = len(hex_colors)

    # Step 2-4: Process each color atomically and stream results
    for idx, hex_code in enumerate(hex_colors):
        try:
            # Step 2: Validate color (fast)
            yield ColorExtractionEvent(
                type="color_parsed",
                hex=hex_code,
                progress={"current": idx + 1, "total": total_colors}
            )

            # Step 3: Compute properties (ColorAide - moderate latency)
            properties = await compute_color_properties_async(hex_code)
            yield ColorExtractionEvent(
                type="color_computed",
                hex=hex_code,
                data=properties,
                progress={"current": idx + 1, "total": total_colors}
            )

            # Step 4: Store to database (I/O - moderate latency)
            color_id = await store_color_token_async(
                project_id=project_id,
                hex=hex_code,
                properties=properties
            )
            yield ColorExtractionEvent(
                type="color_stored",
                color_id=color_id,
                hex=hex_code,
                data=properties,
                progress={"current": idx + 1, "total": total_colors}
            )

        except Exception as e:
            yield ColorExtractionEvent(
                type="error",
                hex=hex_code,
                error=str(e),
                progress={"current": idx + 1, "total": total_colors}
            )
            continue  # Continue with next color
```

---

### 2. **WebSocket Endpoint**
**File:** `src/copy_that/interfaces/api/main.py` (EXTEND)

```python
from fastapi import WebSocket

@app.websocket("/api/v1/colors/extract/stream")
async def websocket_extract_colors(
    websocket: WebSocket,
    image_url: str,
    project_id: int,
    max_colors: int = 10
):
    """
    WebSocket endpoint for real-time color extraction streaming

    Client connects → Server starts streaming → Frontend updates live
    """
    await websocket.accept()

    try:
        async for event in extract_colors_streaming(
            image_url, project_id, max_colors
        ):
            # Send each event immediately as it's ready
            await websocket.send_json(event.dict())

    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "error": str(e)
        })
    finally:
        await websocket.close()
```

---

### 3. **Background Task Processing (Celery)**
**File:** `src/copy_that/infrastructure/celery_tasks.py` (NEW)

```python
from celery import Celery, group
from src.copy_that.application.async_color_extractor import extract_colors_streaming

app = Celery('copy_that')

@app.task(bind=True)
def process_color_extraction(self, image_url: str, project_id: int):
    """
    Background task that processes color extraction
    Emits progress updates to WebSocket/Redis channel
    """
    channel = f"color_extraction:{project_id}"

    try:
        async for event in extract_colors_streaming(image_url, project_id):
            # Publish to Redis channel (picked up by WebSocket)
            app.send_task(
                'publish_extraction_event',
                args=[channel, event.dict()]
            )
    except Exception as e:
        app.send_task(
            'publish_extraction_event',
            args=[channel, {"type": "error", "error": str(e)}]
        )
```

---

### 4. **Frontend Consumer (React)**
**File:** `frontend/src/hooks/useColorExtractionStream.ts` (NEW)

```typescript
import { useEffect, useRef, useState } from 'react';

interface ExtractionEvent {
  type: 'color_parsed' | 'color_computed' | 'color_stored' | 'error';
  hex?: string;
  color_id?: number;
  data?: ColorToken;
  error?: string;
  progress: { current: number; total: number };
}

export function useColorExtractionStream(
  imageUrl: string,
  projectId: number,
  maxColors: number = 10
) {
  const [colors, setColors] = useState<ColorToken[]>([]);
  const [loading, setLoading] = useState(true);
  const [progress, setProgress] = useState({ current: 0, total: 0 });
  const [errors, setErrors] = useState<string[]>([]);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Connect to WebSocket
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws.current = new WebSocket(
      `${protocol}//${window.location.host}/api/v1/colors/extract/stream?` +
      `image_url=${encodeURIComponent(imageUrl)}&` +
      `project_id=${projectId}&` +
      `max_colors=${maxColors}`
    );

    ws.current.onmessage = (event) => {
      const message: ExtractionEvent = JSON.parse(event.data);

      setProgress(message.progress);

      switch (message.type) {
        case 'color_parsed':
          // Show skeleton/loading state
          setColors(prev => [...prev, {
            hex: message.hex,
            name: `Loading #${message.hex?.slice(1)}`,
            confidence: 0
          } as ColorToken]);
          break;

        case 'color_computed':
          // Update with computed properties
          setColors(prev =>
            prev.map(c => c.hex === message.hex
              ? { ...c, ...message.data }
              : c
            )
          );
          break;

        case 'color_stored':
          // Mark as persisted
          setColors(prev =>
            prev.map(c => c.hex === message.hex
              ? { ...c, id: message.color_id, stored: true }
              : c
            )
          );
          break;

        case 'error':
          setErrors(prev => [...prev, message.error || 'Unknown error']);
          // Remove failed color
          setColors(prev => prev.filter(c => c.hex !== message.hex));
          break;
      }
    };

    ws.current.onclose = () => {
      setLoading(false);
    };

    return () => {
      ws.current?.close();
    };
  }, [imageUrl, projectId, maxColors]);

  return { colors, loading, progress, errors };
}
```

---

### 5. **Frontend UI Component**
**File:** `frontend/src/components/ProgressiveColorPalette.tsx` (NEW)

```typescript
import { useColorExtractionStream } from '../hooks/useColorExtractionStream';

export function ProgressiveColorPalette({
  imageUrl,
  projectId
}: {
  imageUrl: string;
  projectId: number;
}) {
  const { colors, loading, progress, errors } = useColorExtractionStream(
    imageUrl,
    projectId
  );

  return (
    <div className="color-palette">
      <div className="progress-bar">
        <div className="progress" style={{
          width: `${(progress.current / progress.total) * 100}%`
        }} />
        <span>{progress.current}/{progress.total}</span>
      </div>

      <div className="color-grid">
        {colors.map((color) => (
          <div
            key={color.hex}
            className={`color-card ${!color.stored ? 'loading' : 'loaded'}`}
          >
            <div
              className="color-swatch"
              style={{ backgroundColor: color.hex }}
            />
            <div className="color-info">
              {color.stored ? (
                <>
                  <h4>{color.name}</h4>
                  <p>{color.design_intent}</p>
                  {color.harmony && <p>Harmony: {color.harmony}</p>}
                </>
              ) : (
                <div className="skeleton-loader" />
              )}
            </div>
          </div>
        ))}
      </div>

      {errors.length > 0 && (
        <div className="errors">
          {errors.map((err, i) => <p key={i}>{err}</p>)}
        </div>
      )}
    </div>
  );
}
```

---

## Benefits

### User Experience
- ✅ **Progressive Enhancement**: See first colors in 1-2 seconds
- ✅ **Visual Feedback**: Progress bar shows work in progress
- ✅ **Error Recovery**: Single color failure doesn't block others
- ✅ **Interactive**: Can start using colors before full extraction completes

### Technical
- ✅ **Non-Blocking**: Each color processed independently
- ✅ **Atomic Operations**: DB writes are isolated transactions
- ✅ **Scalability**: Celery enables background processing
- ✅ **Resilience**: Failure of one color doesn't crash pipeline

### Performance
- ✅ **TTFCP** (Time to First Color Parsed): ~1 second
- ✅ **TTFC** (Time to First Color Computed): ~2-3 seconds
- ✅ **Full Extraction**: Still ~5-10 seconds (Claude bottleneck)
- ✅ **Better perceived performance** (streaming > waiting)

---

## Implementation Phases

### Phase 5.1: Async Infrastructure (1-2 days)
- Create async_color_extractor.py with event streaming
- Add WebSocket endpoint to FastAPI
- Write tests for streaming behavior
- **NOT** dependent on Celery yet

### Phase 5.2: Frontend Integration (1 day)
- Create useColorExtractionStream hook
- Build ProgressiveColorPalette component
- Add CSS animations for loading states
- Test WebSocket connection

### Phase 5.3: Background Processing (Optional, 1 day)
- Set up Celery worker
- Move extraction to background tasks
- Implement Redis channel for pub/sub
- Add job tracking UI

---

## Database Atomicity

Each color write is independent:

```sql
-- Per-color atomic transaction
BEGIN;
  INSERT INTO color_tokens (project_id, hex, rgb, name, ...)
  VALUES (1, '#FF5733', 'rgb(255, 87, 51)', 'Sunset Orange', ...);

  -- If this fails, transaction rolls back
  -- Other colors continue processing
COMMIT;
```

---

## Architecture Constraints & Tradeoffs

### Constraint: Claude Vision is Blocking
- No streaming API support for vision + structured outputs
- Must wait for complete analysis (~2-3 seconds)
- **Workaround**: Return hex codes quickly, compute properties in parallel

### Constraint: Database I/O
- Each color write incurs ~50-100ms latency
- **Solution**: Batch inserts for final confirmation, stream intermediate states

### Tradeoff: Complexity
- Adds async/await, WebSocket, potentially Celery
- **Worth it for**: Better UX, scalability, resilience

---

## Comparison: Current vs Proposed

| Aspect | Current (Blocking) | Proposed (Streaming) |
|--------|-------------------|----------------------|
| Time to First Color | 5-10s | 1-2s |
| User Feedback | None | Progressive |
| Error Recovery | All-or-nothing | Per-color atomic |
| Scalability | Sync bottleneck | Async/Celery |
| Code Complexity | Simple | Medium |
| UX Polish | Basic | Professional |

---

## Next Steps

1. **Short-term (Phase 5)**: Implement async extraction without WebSocket
   - Keep current HTTP endpoint but use async/await internally
   - Faster response, no UI changes needed

2. **Medium-term (Phase 5+)**: Add WebSocket streaming
   - Real-time progress to frontend
   - Progressive color rendering

3. **Long-term (Phase 6)**: Background processing with Celery
   - Queue large batch extractions
   - Webhook notifications to frontend
   - Job tracking and history

---

## Code Examples

### Simple Async (No WebSocket)
```python
# Return colors as soon as computed
async def extract_colors_async(image_url: str) -> ColorExtractionResult:
    hex_codes = await claude_extract(image_url)

    colors = []
    for hex_code in hex_codes:
        properties = await compute_properties_async(hex_code)
        colors.append(ColorToken(hex=hex_code, **properties))

    return ColorExtractionResult(colors=colors, ...)
```

### Full Streaming (WebSocket)
```python
# Already implemented above in Architecture Components section
```

---

## Metrics to Track

Once implemented:
- **TTFCP**: Time to First Color Parsed
- **TTFC**: Time to First Color Computed
- **TTFE**: Time to Full Extraction Complete
- **Error Rate**: Per-color failure rate
- **WebSocket Connection Stability**: Uptime %, reconnect count
- **User Engagement**: Do users interact with colors before completion?

---

## Related Documents

- `COLORAIDE_INTEGRATION.md` — ColorAide property computation
- `COLOR_INTEGRATION_ROADMAP.md` — Phase roadmap
- `PHASE_4_COMPLETION_STATUS.md` — Current architecture

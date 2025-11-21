# API Testing Strategy - Copy This Backend

**Version:** 2.0
**Last Updated:** 2025-11-07
**Status:** Ready for Implementation

---

## Executive Summary

### Current State
- **Test Coverage:** ~35% (8 test files, limited WebSocket coverage)
- **Testing Frameworks:** pytest, httpx, FastAPI TestClient, Locust (load testing)
- **Existing Tests:**
  - ✅ Basic extraction API (POST /api/extract)
  - ✅ Job status polling (GET /api/extract/{job_id})
  - ✅ Contract validation (Pydantic schemas)
  - ✅ Basic load testing (Locust script)
  - ✅ Progressive WebSocket (limited coverage)
  - ❌ No WebSocket stress testing
  - ❌ No AI API mocking strategy
  - ❌ No end-to-end timeout testing (64-second extractions)
  - ❌ No concurrent WebSocket connection tests
  - ❌ No circuit breaker validation

### Target State
- **Test Coverage:** 85% (comprehensive API coverage)
- **WebSocket Coverage:** 90% (progressive extraction, security, timeouts)
- **Performance Testing:** Automated CI/CD integration
- **Mock Strategy:** Zero-cost AI API testing
- **Test Data:** 50+ fixture images covering edge cases

### Critical Gaps
1. **WebSocket Testing:** Only 1 basic test, needs 15+ scenarios
2. **AI API Mocking:** Currently tests hit real APIs ($$$)
3. **Timeout Scenarios:** No 64-second extraction timeout tests
4. **Circuit Breaker:** No validation of OpenAI/Claude/CLIP fallback logic
5. **Concurrent Load:** No WebSocket connection limit testing (max 3/IP)

---

## 1. Test Pyramid Analysis

### Current Distribution (Non-Ideal)

```
        /\
       /  \  E2E: 5%
      /----\
     /      \ Integration: 25%
    /--------\
   /          \ Unit: 70%
  /____________\
```

**Issues:**
- Too many unit tests for legacy extractors (53 extractors × multiple tests)
- Not enough integration tests for multi-extractor coordination
- Missing WebSocket E2E tests
- No AI provider integration tests with mocks

### Target Distribution (Ideal)

```
        /\
       /  \  E2E: 10% (WebSocket, full extraction flow)
      /----\
     /      \ Integration: 30% (Multi-extractor, AI fallback)
    /--------\
   /          \ Unit: 60% (Individual extractors, utilities)
  /____________\
```

**Benefits:**
- Faster test suite (reduce redundant extractor unit tests)
- Better confidence in API contracts
- Comprehensive WebSocket coverage
- Realistic AI API failure scenarios

---

## 2. WebSocket Testing Plan

### Test Scenarios (15 Total)

#### A. Connection Management (5 tests)

**Test 1: Basic Connection & Extraction**
```python
async def test_websocket_connection_success():
    """Test successful WebSocket connection and CV extraction"""
    async with AsyncClient(app=app, base_url="ws://test") as client:
        async with client.websocket_connect("/api/extract/progressive") as ws:
            await ws.send_json({
                "action": "extract",
                "images": [base64_image],
                "use_ai": False
            })

            # Expect cv_complete stage
            response = await ws.receive_json()
            assert response["stage"] == "cv_complete"
            assert "tokens" in response
            assert response["metadata"]["elapsed_ms"] < 2000  # <2s
```

**Test 2: Connection Limit Enforcement**
```python
async def test_websocket_connection_limit():
    """Test max 3 connections per IP"""
    connections = []
    async with AsyncClient(app=app, base_url="ws://test") as client:
        # Open 3 connections (should succeed)
        for i in range(3):
            ws = await client.websocket_connect("/api/extract/progressive")
            connections.append(ws)

        # 4th connection should fail
        with pytest.raises(WebSocketException) as exc:
            await client.websocket_connect("/api/extract/progressive")

        assert "Maximum 3 connections per IP exceeded" in str(exc.value)
```

**Test 3: Rate Limit - Message Spam**
```python
async def test_websocket_message_rate_limit():
    """Test 20 messages/minute rate limit"""
    async with client.websocket_connect("/api/extract/progressive") as ws:
        # Send 21 messages rapidly
        for i in range(21):
            await ws.send_json({"action": "ping"})
            if i < 20:
                assert (await ws.receive_json())["action"] == "pong"
            else:
                # 21st message should trigger rate limit
                error = await ws.receive_json()
                assert "rate limit exceeded" in error.get("error", "").lower()
```

**Test 4: Auto-Reconnect Simulation**
```python
async def test_websocket_reconnect():
    """Test client reconnection after disconnect"""
    # First connection
    async with client.websocket_connect("/api/extract/progressive") as ws1:
        await ws1.send_json({"action": "ping"})
        await ws1.receive_json()
        # Connection closed

    # Reconnect immediately (should succeed)
    async with client.websocket_connect("/api/extract/progressive") as ws2:
        await ws2.send_json({"action": "ping"})
        pong = await ws2.receive_json()
        assert pong["action"] == "pong"
```

**Test 5: Concurrent Connections from Different IPs**
```python
async def test_websocket_concurrent_different_ips():
    """Test multiple clients can connect simultaneously"""
    # Mock different X-Forwarded-For headers
    headers_1 = {"X-Forwarded-For": "192.168.1.1"}
    headers_2 = {"X-Forwarded-For": "192.168.1.2"}

    async with client.websocket_connect(
        "/api/extract/progressive", headers=headers_1
    ) as ws1:
        async with client.websocket_connect(
            "/api/extract/progressive", headers=headers_2
        ) as ws2:
            # Both should succeed
            await ws1.send_json({"action": "ping"})
            await ws2.send_json({"action": "ping"})

            assert (await ws1.receive_json())["action"] == "pong"
            assert (await ws2.receive_json())["action"] == "pong"
```

#### B. Progressive Extraction (4 tests)

**Test 6: CV-Only Extraction**
```python
async def test_websocket_cv_only_extraction():
    """Test fast CV extraction (~1 second)"""
    start_time = time.time()

    async with client.websocket_connect("/api/extract/progressive") as ws:
        await ws.send_json({
            "action": "extract",
            "images": [base64_image],
            "use_ai": False
        })

        response = await ws.receive_json()
        elapsed = time.time() - start_time

        assert response["stage"] == "cv_complete"
        assert elapsed < 2.0  # Should complete in <2 seconds
        assert "palette" in response["tokens"]
        assert response["metadata"]["ai_enhancement"] is False
```

**Test 7: Progressive AI Enhancement**
```python
@pytest.mark.slow
async def test_websocket_progressive_ai():
    """Test multi-stage progressive extraction (CV → CLIP → GPT-4)"""
    stages_received = []

    async with client.websocket_connect("/api/extract/progressive") as ws:
        await ws.send_json({
            "action": "extract",
            "images": [base64_image],
            "use_ai": True
        })

        # Collect all stages
        async for message in ws.iter_json():
            stage = message.get("stage")
            stages_received.append(stage)

            if stage == "ai_complete":
                break

        # Should receive cv_complete first, then ai_complete
        assert "cv_complete" in stages_received
        assert "ai_complete" in stages_received
        assert stages_received.index("cv_complete") < stages_received.index("ai_complete")
```

**Test 8: Token Merging Across Stages**
```python
async def test_websocket_token_merging():
    """Test that AI stages enhance CV tokens (don't replace)"""
    async with client.websocket_connect("/api/extract/progressive") as ws:
        await ws.send_json({
            "action": "extract",
            "images": [base64_image],
            "use_ai": True
        })

        cv_tokens = None
        ai_tokens = None

        async for message in ws.iter_json():
            if message["stage"] == "cv_complete":
                cv_tokens = message["tokens"]
            elif message["stage"] == "ai_complete":
                ai_tokens = message["tokens"]
                break

        # AI should have all CV tokens plus enhancements
        assert cv_tokens is not None
        assert ai_tokens is not None

        # Check CV palette is preserved
        for role in cv_tokens["palette"]:
            assert role in ai_tokens["palette"]

        # Check AI added extractors attribution
        primary = ai_tokens["palette"]["primary"]
        assert "opencv_cv" in primary["extractors"]
        assert len(primary["extractors"]) > 1  # AI should add more
```

**Test 9: Partial Results Handling**
```python
async def test_websocket_partial_results():
    """Test client can use partial CV results while waiting for AI"""
    async with client.websocket_connect("/api/extract/progressive") as ws:
        await ws.send_json({
            "action": "extract",
            "images": [base64_image],
            "use_ai": True
        })

        # Get CV results immediately
        cv_message = await ws.receive_json()
        assert cv_message["stage"] == "cv_complete"

        # Simulate client using CV tokens immediately
        cv_tokens = cv_message["tokens"]
        assert validate_tokens_schema(cv_tokens)

        # Continue waiting for AI enhancement
        ai_message = await ws.receive_json()
        assert ai_message["stage"] == "ai_complete"
```

#### C. Error Handling (3 tests)

**Test 10: Invalid Image Format**
```python
async def test_websocket_invalid_image():
    """Test error handling for malformed base64"""
    async with client.websocket_connect("/api/extract/progressive") as ws:
        await ws.send_json({
            "action": "extract",
            "images": ["invalid_base64!!!"],
            "use_ai": False
        })

        error = await ws.receive_json()
        assert error["stage"] == "failed"
        assert "Failed to decode image" in error["error"]
```

**Test 11: Too Many Images**
```python
async def test_websocket_too_many_images():
    """Test rejection of >10 images"""
    async with client.websocket_connect("/api/extract/progressive") as ws:
        await ws.send_json({
            "action": "extract",
            "images": [base64_image] * 11,  # 11 images
            "use_ai": False
        })

        error = await ws.receive_json()
        assert error.get("error") == "Maximum 10 images allowed"
```

**Test 12: AI API Failure Graceful Degradation**
```python
@patch('backend.routers.extraction.GPT4VisionExtractor')
async def test_websocket_ai_failure_graceful(mock_gpt4):
    """Test graceful degradation when AI APIs fail"""
    # Mock GPT-4 failure
    mock_gpt4.side_effect = Exception("OpenAI API timeout")

    async with client.websocket_connect("/api/extract/progressive") as ws:
        await ws.send_json({
            "action": "extract",
            "images": [base64_image],
            "use_ai": True
        })

        # Should still get CV results
        cv_message = await ws.receive_json()
        assert cv_message["stage"] == "cv_complete"

        # May receive ai_skipped or ai_complete with fallback
        next_message = await ws.receive_json()
        assert next_message["stage"] in ["ai_skipped", "ai_complete"]
```

#### D. Timeout & Performance (3 tests)

**Test 13: Long Extraction Timeout (64 seconds)**
```python
@pytest.mark.slow
@pytest.mark.timeout(70)
async def test_websocket_long_extraction():
    """Test extraction doesn't timeout before 64 seconds"""
    async with client.websocket_connect("/api/extract/progressive") as ws:
        # Send large, complex image
        complex_image = generate_complex_ui_image(size=(3840, 2160))

        await ws.send_json({
            "action": "extract",
            "images": [complex_image],
            "use_ai": True
        })

        # Should complete within 70 seconds
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(ws.receive_json(), timeout=70)
```

**Test 14: Connection Keepalive (Ping/Pong)**
```python
async def test_websocket_ping_pong():
    """Test ping/pong keepalive mechanism"""
    async with client.websocket_connect("/api/extract/progressive") as ws:
        await ws.send_json({"action": "ping"})

        pong = await ws.receive_json()
        assert pong["action"] == "pong"
        assert "timestamp" in pong
```

**Test 15: Message Ordering**
```python
async def test_websocket_message_ordering():
    """Test messages arrive in correct order (CV before AI)"""
    async with client.websocket_connect("/api/extract/progressive") as ws:
        await ws.send_json({
            "action": "extract",
            "images": [base64_image],
            "use_ai": True
        })

        messages = []
        async for msg in ws.iter_json():
            messages.append(msg["stage"])
            if msg["stage"] == "ai_complete":
                break

        # Verify ordering
        if "cv_complete" in messages and "ai_complete" in messages:
            cv_idx = messages.index("cv_complete")
            ai_idx = messages.index("ai_complete")
            assert cv_idx < ai_idx
```

### WebSocket Test Implementation

**File:** `backend/tests/test_websocket_progressive.py`

```python
"""
Comprehensive WebSocket Progressive Extraction Tests

Tests cover:
- Connection management (limits, rate limiting)
- Progressive extraction (CV → AI stages)
- Error handling (invalid inputs, API failures)
- Performance (timeouts, keepalive)
"""

import asyncio
import base64
import io
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from PIL import Image

from backend.main import app
from backend.database import init_db


@pytest.fixture(scope="module")
async def setup_database():
    """Initialize test database"""
    await init_db()


@pytest.fixture
def base64_image() -> str:
    """Generate test image as base64 string"""
    img = Image.new("RGB", (800, 600), color=(241, 89, 37))
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


@pytest.fixture
def complex_ui_image() -> str:
    """Generate complex UI screenshot for performance testing"""
    # Simulate complex UI with gradients, text, shadows
    import numpy as np

    array = np.zeros((2160, 3840, 3), dtype=np.uint8)
    # Add gradient background
    for i in range(2160):
        array[i, :, 0] = int(255 * i / 2160)
    # Add noise for texture
    noise = np.random.randint(0, 50, (2160, 3840, 3), dtype=np.uint8)
    array = np.clip(array + noise, 0, 255).astype(np.uint8)

    img = Image.fromarray(array)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


class TestWebSocketConnectionManagement:
    """Test WebSocket connection limits and security"""

    # [Tests 1-5 from above]
    pass


class TestWebSocketProgressiveExtraction:
    """Test multi-stage progressive extraction"""

    # [Tests 6-9 from above]
    pass


class TestWebSocketErrorHandling:
    """Test error scenarios and graceful degradation"""

    # [Tests 10-12 from above]
    pass


class TestWebSocketPerformance:
    """Test timeouts, keepalive, and message ordering"""

    # [Tests 13-15 from above]
    pass
```

---

## 3. AI API Mocking Strategy

### Problem: Expensive AI API Calls in Tests

**Current Issue:**
- GPT-4 Vision: $0.01 per image
- Claude Vision: $0.015 per image
- Running full test suite = $5-10 per run
- CI/CD pipeline = $100-200/month

### Solution: Multi-Level Mocking

#### Level 1: Mock AI Responses (Unit Tests)

```python
# backend/tests/mocks/ai_responses.py

"""
Pre-recorded AI API responses for deterministic testing
"""

MOCK_GPT4_VISION_RESPONSE = {
    "palette": {
        "primary": {
            "hex": "#F15927",
            "name": "Vibrant Orange",
            "extractors": ["opencv_cv", "gpt4_vision"]
        },
        "secondary": {
            "hex": "#1E40AF",
            "name": "Deep Blue",
            "extractors": ["opencv_cv", "gpt4_vision"]
        }
    },
    "typography": {
        "family": "Inter, system-ui, sans-serif",
        "weights": [400, 600, 700],
        "extractors": ["gpt4_vision"]
    },
    "_metadata": {
        "extractor": "gpt4_vision",
        "confidence": 0.92,
        "cost": 0.01
    }
}

MOCK_CLAUDE_VISION_RESPONSE = {
    "semantic": {
        "brand": {
            "primary": "{orange.500}",
            "mood": "energetic, modern, tech-forward"
        }
    },
    "components": {
        "button": {
            "padding": "12px 24px",
            "borderRadius": "8px"
        }
    },
    "_metadata": {
        "extractor": "claude_vision",
        "confidence": 0.89,
        "cost": 0.015
    }
}

MOCK_CLIP_SEMANTIC_RESPONSE = {
    "semantic_tags": ["dashboard", "data-visualization", "modern-ui"],
    "style": "minimalist",
    "domain": "enterprise-saas",
    "_metadata": {
        "extractor": "clip_semantics",
        "confidence": 0.85,
        "cost": 0.0  # Zero-cost local model
    }
}
```

#### Level 2: Mock Extractors (Integration Tests)

```python
# backend/tests/conftest.py

"""
Pytest fixtures for mocking AI extractors
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from backend.tests.mocks.ai_responses import (
    MOCK_GPT4_VISION_RESPONSE,
    MOCK_CLAUDE_VISION_RESPONSE,
    MOCK_CLIP_SEMANTIC_RESPONSE
)


@pytest.fixture
def mock_gpt4_extractor():
    """Mock GPT-4 Vision extractor"""
    with patch('extractors.ai.gpt4_vision_extractor.GPT4VisionExtractor') as mock:
        instance = MagicMock()
        instance.extract.return_value = MOCK_GPT4_VISION_RESPONSE
        instance.refine.return_value = MOCK_GPT4_VISION_RESPONSE
        mock.return_value = instance
        yield mock


@pytest.fixture
def mock_claude_extractor():
    """Mock Claude Vision extractor"""
    with patch('extractors.ai.claude_vision_extractor.ClaudeVisionExtractor') as mock:
        instance = MagicMock()
        instance.extract.return_value = MOCK_CLAUDE_VISION_RESPONSE
        mock.return_value = instance
        yield mock


@pytest.fixture
def mock_clip_extractor():
    """Mock CLIP semantic extractor (local)"""
    with patch('extractors.ai.clip_semantic_extractor.ClipSemanticExtractor') as mock:
        instance = MagicMock()
        instance.extract.return_value = MOCK_CLIP_SEMANTIC_RESPONSE
        mock.return_value = instance
        yield mock


@pytest.fixture
def mock_all_ai_extractors(mock_gpt4_extractor, mock_claude_extractor, mock_clip_extractor):
    """Mock all AI extractors at once"""
    return {
        "gpt4": mock_gpt4_extractor,
        "claude": mock_claude_extractor,
        "clip": mock_clip_extractor
    }
```

#### Level 3: Mock HTTP Calls (E2E Tests)

```python
# backend/tests/test_extraction_mocked.py

"""
End-to-end extraction tests with mocked AI APIs
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch

from backend.main import app
from backend.tests.mocks.ai_responses import MOCK_GPT4_VISION_RESPONSE


@pytest.mark.asyncio
async def test_extraction_with_ai_mocked(mock_all_ai_extractors, base64_image):
    """Test full extraction flow with mocked AI APIs"""
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/extract",
            files=[("files", ("test.png", io.BytesIO(base64_image), "image/png"))],
            data={"use_ai": "true"}
        )

        assert response.status_code == 200
        job_id = response.json()["job_id"]

        # Poll for completion
        for _ in range(20):
            await asyncio.sleep(0.5)
            status_response = await client.get(f"/api/extract/{job_id}")
            status = status_response.json()

            if status["status"] == "completed":
                tokens = status["tokens"]

                # Verify AI extractors were called
                primary = tokens["palette"]["primary"]
                assert "gpt4_vision" in primary["extractors"]

                # Verify zero cost (mocked)
                return

        pytest.fail("Extraction did not complete in time")


@pytest.mark.asyncio
async def test_ai_api_failure_fallback(base64_image):
    """Test graceful degradation when AI APIs fail"""
    # Mock GPT-4 to raise exception
    with patch('extractors.ai.gpt4_vision_extractor.GPT4VisionExtractor') as mock_gpt4:
        mock_gpt4.side_effect = Exception("OpenAI API timeout")

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/extract",
                files=[("files", ("test.png", io.BytesIO(base64_image), "image/png"))],
                data={"use_ai": "true"}
            )

            # Should still succeed with CV-only results
            assert response.status_code == 200
```

#### Level 4: VCR Cassettes (Record/Replay Real API Calls)

**Use for:** Integration testing against real API schemas without costs

```python
# backend/tests/test_extraction_vcr.py

"""
Use pytest-recording to record real API calls once, replay in CI
"""

import pytest


@pytest.mark.vcr()
async def test_gpt4_vision_real_api_schema(base64_image):
    """
    Record real GPT-4 Vision API call once, replay in CI.

    First run: Hits real API, records response to fixtures/vcr_cassettes/
    Subsequent runs: Replays recorded response (zero cost)
    """
    extractor = GPT4VisionExtractor()
    tokens = extractor.extract([base64_image])

    # Validate real API response schema
    assert "palette" in tokens
    assert "typography" in tokens
    assert "_metadata" in tokens
```

**Setup:**
```bash
# Install pytest-recording
pip install pytest-recording vcrpy

# First run: Record cassettes (costs money, run once)
pytest tests/test_extraction_vcr.py --record-mode=once

# CI/CD: Replay cassettes (zero cost)
pytest tests/test_extraction_vcr.py --record-mode=none
```

### Mock Strategy Summary

| Test Type | Mock Level | Use Case | Cost |
|-----------|-----------|----------|------|
| Unit Tests | Response Dicts | Fast extractor logic tests | $0 |
| Integration Tests | Mock Classes | Multi-extractor coordination | $0 |
| E2E Tests | HTTP Mocks | Full API flow validation | $0 |
| Schema Tests | VCR Cassettes | Real API schema validation | $0.05 (one-time) |
| Manual QA | Real APIs | Production validation | $2-5 per session |

---

## 4. Performance Testing Suite

### Load Testing with Locust

**Enhancement:** `backend/tests/load_test_extraction.py` (already exists)

```python
"""
Enhanced Load Testing for Copy This Backend

Scenarios:
1. Baseline: 10 users, 60s (normal traffic)
2. Stress: 50 users, 120s (peak traffic)
3. Spike: 100 users, 60s (sudden surge)
4. Endurance: 25 users, 600s (stability)
5. WebSocket: 20 concurrent connections (real-time load)
"""

# Add WebSocket load testing
class WebSocketLoadUser(HttpUser):
    """Load test WebSocket progressive extraction"""

    wait_time = between(2, 5)

    @task
    def websocket_extraction(self):
        """Test WebSocket progressive extraction under load"""
        import websocket

        ws = websocket.WebSocket()
        ws.connect(f"ws://{self.host}/api/extract/progressive")

        ws.send(json.dumps({
            "action": "extract",
            "images": [self.test_image_base64],
            "use_ai": False
        }))

        # Measure time to cv_complete
        start = time.time()
        while True:
            response = json.loads(ws.recv())
            if response.get("stage") == "cv_complete":
                elapsed = time.time() - start
                # Record custom metric
                events.request.fire(
                    request_type="websocket",
                    name="progressive_extraction",
                    response_time=elapsed * 1000,
                    response_length=len(json.dumps(response))
                )
                break

        ws.close()
```

### k6 Performance Testing (Alternative)

**File:** `backend/tests/k6_load_test.js`

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');

// Load test configuration
export const options = {
  stages: [
    { duration: '30s', target: 10 },  // Ramp up to 10 users
    { duration: '1m', target: 10 },   // Stay at 10 users
    { duration: '30s', target: 50 },  // Spike to 50 users
    { duration: '1m', target: 50 },   // Stay at 50 users
    { duration: '30s', target: 0 },   // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'],  // 95% of requests under 2s
    errors: ['rate<0.1'],                // Error rate < 10%
  },
};

// Test image as base64
const testImageBase64 = '...'; // Truncated for brevity

export default function () {
  // Test extraction endpoint
  const payload = {
    files: [{
      filename: 'test.png',
      data: testImageBase64,
      content_type: 'image/png'
    }],
    use_ai: false
  };

  const response = http.post(
    'http://localhost:5000/api/extract',
    JSON.stringify(payload),
    { headers: { 'Content-Type': 'application/json' } }
  );

  const success = check(response, {
    'status is 200': (r) => r.status === 200,
    'has job_id': (r) => JSON.parse(r.body).job_id !== undefined,
    'response time < 2s': (r) => r.timings.duration < 2000,
  });

  errorRate.add(!success);

  sleep(1);
}
```

**Run:**
```bash
# Install k6
brew install k6

# Run load test
k6 run backend/tests/k6_load_test.js

# Generate HTML report
k6 run --out json=test_results.json backend/tests/k6_load_test.js
k6 report test_results.json --export test_report.html
```

### Performance Test Scenarios

| Scenario | Users | Duration | Expected RPS | Max Latency | Pass Criteria |
|----------|-------|----------|--------------|-------------|---------------|
| Baseline | 10 | 60s | 5-10 | <1s | 0% failures |
| Stress | 50 | 120s | 20-30 | <2s | <5% failures |
| Spike | 100 | 60s | 40-50 | <3s | <10% failures |
| Endurance | 25 | 600s | 10-15 | <1.5s | <2% failures |
| WebSocket | 20 | 120s | 5-10 | <2s | 0% disconnects |

---

## 5. Contract Testing Setup

### OpenAPI Schema Validation

**File:** `backend/tests/test_openapi_contract.py`

```python
"""
OpenAPI 3.0 Contract Testing

Validates that API responses match OpenAPI specification
"""

import pytest
from fastapi.testclient import TestClient
from openapi_spec_validator import validate_spec
from openapi_spec_validator.readers import read_from_filename

from backend.main import app


@pytest.fixture(scope="module")
def openapi_spec():
    """Load OpenAPI spec from FastAPI app"""
    client = TestClient(app)
    response = client.get("/openapi.json")
    return response.json()


def test_openapi_spec_valid(openapi_spec):
    """Test that OpenAPI spec is valid"""
    # Validate spec structure
    validate_spec(openapi_spec)


def test_extraction_endpoint_matches_spec(openapi_spec):
    """Test POST /api/extract matches OpenAPI spec"""
    spec = openapi_spec

    # Get endpoint definition
    extract_post = spec["paths"]["/api/extract"]["post"]

    # Validate request body schema
    request_schema = extract_post["requestBody"]["content"]["multipart/form-data"]["schema"]
    assert "files" in request_schema["properties"]
    assert "use_ai" in request_schema["properties"]

    # Validate response schema
    response_schema = extract_post["responses"]["200"]["content"]["application/json"]["schema"]
    assert "job_id" in response_schema["properties"]
    assert "status" in response_schema["properties"]


def test_response_matches_schema(openapi_spec):
    """Test actual API response matches OpenAPI schema"""
    from jsonschema import validate as validate_json_schema

    client = TestClient(app)

    # Make real request
    response = client.post(
        "/api/extract",
        files=[("files", ("test.png", io.BytesIO(test_image), "image/png"))],
        data={"use_ai": "false"}
    )

    # Get schema from OpenAPI spec
    extract_post = openapi_spec["paths"]["/api/extract"]["post"]
    response_schema = extract_post["responses"]["200"]["content"]["application/json"]["schema"]

    # Validate response matches schema
    validate_json_schema(instance=response.json(), schema=response_schema)
```

### Pydantic Schema Testing (Already Exists)

**Enhancement:** `backend/tests/test_api_contracts.py`

```python
# Add version compatibility tests

class TestSchemaVersioning:
    """Test backward compatibility across API versions"""

    def test_v1_tokens_compatible_with_v2():
        """Test v1 token format still works in v2 API"""
        v1_tokens = {
            "palette": {
                "primary": "#FF5733",  # v1: string
                "secondary": "#1E40AF"
            },
            "spacing": {"sm": 8, "md": 16, "lg": 24},
            "typography": {"family": "Inter", "weights": [400, 700]}
        }

        # Should upgrade to v2 format (with extractors)
        v2_tokens = upgrade_tokens_to_v2(v1_tokens)

        assert isinstance(v2_tokens["palette"]["primary"], dict)
        assert v2_tokens["palette"]["primary"]["hex"] == "#FF5733"
        assert "extractors" in v2_tokens["palette"]["primary"]
```

### Consumer-Driven Contract Testing (Pact)

**Optional:** For frontend-backend contract enforcement

```python
# backend/tests/test_pact_contracts.py

"""
Pact Contract Testing - Backend Provider Tests

Validates that backend API meets frontend consumer expectations
"""

import pytest
from pact import Verifier

@pytest.fixture(scope="module")
def pact_verifier():
    """Initialize Pact verifier"""
    return Verifier(
        provider="CopyThisBackend",
        provider_base_url="http://localhost:5000"
    )

def test_verify_frontend_contract(pact_verifier):
    """Verify backend meets frontend contract"""
    # Pact broker configuration
    pact_verifier.verify_with_broker(
        broker_url="https://pact-broker.example.com",
        broker_username="pact_user",
        broker_password="pact_password",
        publish_version="2.0.0",
        publish_verification_results=True
    )
```

---

## 6. Test Data Management

### Fixture Image Library

**Directory:** `backend/tests/fixtures/images/`

```
fixtures/images/
├── basic/
│   ├── solid_color.png          # Simple color extraction
│   ├── gradient.png              # Gradient detection
│   └── two_colors.png            # Color palette extraction
├── typography/
│   ├── heading_body.png          # Font size extraction
│   ├── multiweight.png           # Font weight detection
│   └── custom_fonts.png          # Font family recognition
├── components/
│   ├── buttons.png               # Button component detection
│   ├── forms.png                 # Input field extraction
│   ├── cards.png                 # Card component detection
│   └── navigation.png            # Navigation bar extraction
├── layouts/
│   ├── dashboard.png             # Complex dashboard layout
│   ├── mobile_ui.png             # Mobile responsive design
│   └── grid_system.png           # Grid/layout detection
├── edge_cases/
│   ├── very_small.png            # 32×32 icon
│   ├── very_large.png            # 4K screenshot (3840×2160)
│   ├── low_contrast.png          # Accessibility challenge
│   ├── monochrome.png            # Grayscale image
│   ├── transparent_bg.png        # PNG with alpha channel
│   └── corrupted_partial.png    # Partially corrupted file
├── ai_specific/
│   ├── audio_plugin_ui.png       # Audio plugin components
│   ├── 3d_elements.png           # Depth map extraction
│   ├── animation_frames.gif      # Animation detection
│   └── video_preview.mp4         # Video thumbnail extraction
└── performance/
    ├── complex_dashboard_4k.png  # Performance stress test
    └── 10_images_batch/          # Batch extraction test
        ├── img_01.png
        ├── img_02.png
        └── ...
```

### Expected Outputs Repository

**Directory:** `backend/tests/fixtures/expected_outputs/`

```python
# backend/tests/fixtures/expected_outputs/solid_color.json

{
  "palette": {
    "primary": {
      "hex": "#F15927",
      "extractors": ["opencv_cv"]
    }
  },
  "spacing": {
    "xs": 4,
    "sm": 8,
    "md": 16,
    "lg": 24
  },
  "_test_metadata": {
    "fixture": "solid_color.png",
    "expected_extraction_time_ms": 500,
    "expected_extractors": ["opencv_cv"]
  }
}
```

### Test Data Factory

**File:** `backend/tests/factories.py`

```python
"""
Test data factories using factory_boy
"""

import factory
from factory import Faker, LazyAttribute
from PIL import Image
import io
import numpy as np

class ImageFactory(factory.Factory):
    """Generate test images programmatically"""

    class Meta:
        model = Image.Image

    width = 800
    height = 600
    mode = "RGB"
    color = (241, 89, 37)  # Orange

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return Image.new(
            kwargs.get("mode", "RGB"),
            (kwargs.get("width", 800), kwargs.get("height", 600)),
            color=kwargs.get("color", (241, 89, 37))
        )


class GradientImageFactory(ImageFactory):
    """Generate gradient images"""

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        width = kwargs.get("width", 800)
        height = kwargs.get("height", 600)

        array = np.zeros((height, width, 3), dtype=np.uint8)
        for i in range(height):
            array[i, :, 0] = int(255 * i / height)  # Red gradient
            array[i, :, 2] = int(255 * (1 - i / height))  # Blue gradient

        return Image.fromarray(array, "RGB")


class ComplexUIFactory(ImageFactory):
    """Generate complex UI screenshots"""

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        width = kwargs.get("width", 1920)
        height = kwargs.get("height", 1080)

        # Create complex UI with multiple elements
        array = np.random.randint(50, 200, (height, width, 3), dtype=np.uint8)

        # Add header bar
        array[0:80, :] = [30, 41, 59]  # Dark blue header

        # Add sidebar
        array[:, 0:200] = [45, 55, 72]  # Gray sidebar

        # Add cards with shadows
        for y in range(150, 900, 250):
            for x in range(250, 1700, 400):
                array[y:y+200, x:x+350] = [255, 255, 255]  # White card
                # Shadow
                array[y+200:y+210, x+10:x+360] = [0, 0, 0]

        return Image.fromarray(array, "RGB")


# Usage in tests
@pytest.fixture
def test_image():
    return ImageFactory()

@pytest.fixture
def gradient_image():
    return GradientImageFactory()

@pytest.fixture
def complex_ui():
    return ComplexUIFactory(width=3840, height=2160)  # 4K
```

---

## 7. CI/CD Integration Plan

### GitHub Actions Workflow

**File:** `.github/workflows/api-tests.yml`

```yaml
name: API Test Suite

on:
  push:
    branches: [main, develop]
    paths:
      - 'backend/**'
      - 'extractors/**'
      - 'tests/**'
  pull_request:
    branches: [main, develop]

env:
  PYTHON_VERSION: "3.11"

jobs:
  unit-tests:
    name: Unit Tests
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('backend/requirements.txt') }}

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio

      - name: Run unit tests
        run: |
          cd backend
          pytest tests/ -v --cov=. --cov-report=xml --cov-report=term \
            -m "not slow and not integration"

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./backend/coverage.xml
          flags: unittests

  integration-tests:
    name: Integration Tests
    runs-on: ubuntu-latest
    timeout-minutes: 15

    services:
      # Optional: Add Redis/PostgreSQL if needed
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: copythis_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install system dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y libopencv-dev

      - name: Install Python dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-asyncio

      - name: Run integration tests
        env:
          DATABASE_URL: postgresql://postgres:testpass@localhost/copythis_test
          # Use mock AI APIs (zero cost)
          OPENAI_API_KEY: mock-key-for-testing
          ANTHROPIC_API_KEY: mock-key-for-testing
        run: |
          cd backend
          pytest tests/ -v -m "integration" --tb=short

  contract-tests:
    name: Contract Tests
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest openapi-spec-validator jsonschema

      - name: Run contract tests
        run: |
          cd backend
          pytest tests/test_api_contracts.py -v
          pytest tests/test_openapi_contract.py -v

  websocket-tests:
    name: WebSocket Tests
    runs-on: ubuntu-latest
    timeout-minutes: 20

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-asyncio websockets

      - name: Run WebSocket tests
        run: |
          cd backend
          pytest tests/test_websocket_progressive.py -v --tb=short

  load-tests:
    name: Load Tests
    runs-on: ubuntu-latest
    timeout-minutes: 15
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: |
          pip install locust

      - name: Start backend server
        run: |
          cd backend
          pip install -r requirements.txt
          uvicorn main:app --host 0.0.0.0 --port 5000 &
          sleep 10  # Wait for server to start

      - name: Run load tests
        run: |
          cd backend/tests
          locust -f load_test_extraction.py \
            --host=http://localhost:5000 \
            --headless -u 10 -r 2 --run-time 60s \
            --html=load_test_report.html \
            --csv=load_test_results

      - name: Upload load test report
        uses: actions/upload-artifact@v3
        with:
          name: load-test-report
          path: backend/tests/load_test_report.html

  test-summary:
    name: Test Summary
    runs-on: ubuntu-latest
    needs: [unit-tests, integration-tests, contract-tests, websocket-tests]
    if: always()

    steps:
      - name: Generate summary
        run: |
          echo "# Test Results Summary" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "| Test Suite | Status |" >> $GITHUB_STEP_SUMMARY
          echo "|------------|--------|" >> $GITHUB_STEP_SUMMARY
          echo "| Unit Tests | ${{ needs.unit-tests.result }} |" >> $GITHUB_STEP_SUMMARY
          echo "| Integration Tests | ${{ needs.integration-tests.result }} |" >> $GITHUB_STEP_SUMMARY
          echo "| Contract Tests | ${{ needs.contract-tests.result }} |" >> $GITHUB_STEP_SUMMARY
          echo "| WebSocket Tests | ${{ needs.websocket-tests.result }} |" >> $GITHUB_STEP_SUMMARY
```

### Pre-commit Hooks

**File:** `.pre-commit-config.yaml`

```yaml
repos:
  - repo: local
    hooks:
      - id: pytest-fast
        name: Run fast tests
        entry: bash -c 'cd backend && pytest tests/ -v -m "not slow" --tb=short'
        language: system
        pass_filenames: false
        always_run: true

      - id: api-contract-check
        name: Check API contracts
        entry: bash -c 'cd backend && pytest tests/test_api_contracts.py -v'
        language: system
        pass_filenames: false
        files: ^backend/routers/.*\.py$
```

### Test Coverage Reporting

**File:** `backend/pytest.ini`

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Markers
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks integration tests
    websocket: marks WebSocket tests
    load: marks load/performance tests

# Coverage
addopts =
    --strict-markers
    --cov=backend
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    --cov-fail-under=85

# Asyncio
asyncio_mode = auto

# Timeout
timeout = 300

# Output
console_output_style = progress
```

---

## 8. Test Coverage Roadmap

### Phase 1: Foundation (Week 1)
**Goal:** 50% → 65% coverage

- ✅ Set up pytest fixtures and factories
- ✅ Implement AI API mocking strategy
- ✅ Add 10 WebSocket connection tests
- ✅ Create test data fixtures library
- ✅ Set up CI/CD pipeline

### Phase 2: WebSocket Coverage (Week 2)
**Goal:** 65% → 75% coverage

- ✅ Add 5 progressive extraction tests
- ✅ Implement timeout/keepalive tests
- ✅ Add error handling scenarios
- ✅ Test concurrent connection limits
- ✅ Validate message ordering

### Phase 3: Integration Testing (Week 3)
**Goal:** 75% → 85% coverage

- ✅ Add multi-extractor coordination tests
- ✅ Test AI fallback scenarios (CV → CLIP → GPT-4 → Claude)
- ✅ Validate circuit breaker logic
- ✅ Test database retry logic
- ✅ Add export endpoint tests (React, Figma, MUI, JUCE)

### Phase 4: Performance Testing (Week 4)
**Goal:** 85%+ coverage + performance benchmarks

- ✅ Run load tests in CI/CD
- ✅ Add k6 performance tests
- ✅ Set up monitoring/alerting for test results
- ✅ Document performance baselines
- ✅ Create regression test suite

### Coverage Targets by Module

| Module | Current | Target | Priority |
|--------|---------|--------|----------|
| `routers/extraction.py` | 45% | 90% | High |
| `routers/export.py` | 60% | 85% | Medium |
| `routers/projects.py` | 70% | 85% | Low |
| `websocket_security.py` | 30% | 95% | High |
| `ai_enhancer.py` | 40% | 80% | High |
| `comprehensive_enhancer.py` | 35% | 75% | Medium |
| `circuit_breaker.py` | 50% | 90% | High |
| `database.py` | 80% | 90% | Low |

---

## 9. Example Test Cases

### Test Case 1: Basic Extraction Flow

```python
"""
Test Case: Basic CV Extraction
Validates end-to-end extraction without AI enhancement
"""

@pytest.mark.asyncio
async def test_basic_extraction_flow():
    """
    GIVEN: A valid PNG image (800×600, solid orange color)
    WHEN: POST /api/extract with use_ai=false
    THEN: Returns job_id immediately
    AND: Job completes within 2 seconds
    AND: Extracted tokens contain valid palette, spacing, typography
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Step 1: Upload image
        image_bytes = ImageFactory(color=(241, 89, 37)).tobytes()

        response = await client.post(
            "/api/extract",
            files=[("files", ("test.png", io.BytesIO(image_bytes), "image/png"))],
            data={"use_ai": "false"}
        )

        assert response.status_code == 200
        job_data = response.json()
        assert "job_id" in job_data
        assert job_data["status"] in ["pending", "extracting"]

        job_id = job_data["job_id"]

        # Step 2: Poll for completion
        start_time = time.time()
        completed_job = None

        for _ in range(20):
            await asyncio.sleep(0.2)

            status_response = await client.get(f"/api/extract/{job_id}")
            assert status_response.status_code == 200

            status_data = status_response.json()

            if status_data["status"] == "completed":
                completed_job = status_data
                break

        # Step 3: Validate completion time
        elapsed = time.time() - start_time
        assert elapsed < 2.0, f"Extraction took {elapsed:.2f}s (expected <2s)"

        # Step 4: Validate tokens
        assert completed_job is not None, "Job did not complete in time"
        tokens = completed_job["tokens"]

        # Validate palette
        assert "palette" in tokens
        assert "primary" in tokens["palette"]
        primary = tokens["palette"]["primary"]
        assert primary["hex"] == "#F15927" or primary["hex"].startswith("#")
        assert "opencv_cv" in primary["extractors"]

        # Validate spacing
        assert "spacing" in tokens
        assert tokens["spacing"]["xs"] < tokens["spacing"]["sm"]
        assert tokens["spacing"]["sm"] < tokens["spacing"]["md"]

        # Validate typography
        assert "typography" in tokens
        assert len(tokens["typography"]["family"]) > 0
        assert len(tokens["typography"]["weights"]) > 0
```

### Test Case 2: AI Enhancement Progressive

```python
"""
Test Case: Progressive AI Enhancement
Validates multi-stage extraction (CV → CLIP → GPT-4 → Claude)
"""

@pytest.mark.slow
@pytest.mark.asyncio
async def test_progressive_ai_enhancement(mock_all_ai_extractors):
    """
    GIVEN: A complex UI screenshot
    WHEN: POST /api/extract with use_ai=true
    THEN: Returns CV results within 2 seconds
    AND: Returns CLIP enhancements within 5 seconds
    AND: Returns GPT-4 enhancements within 10 seconds
    AND: Returns Claude enhancements within 60 seconds
    AND: Each stage enhances previous tokens (no replacement)
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Upload complex image
        complex_image = ComplexUIFactory(width=1920, height=1080)
        buffer = io.BytesIO()
        complex_image.save(buffer, format="PNG")
        buffer.seek(0)

        response = await client.post(
            "/api/extract",
            files=[("files", ("dashboard.png", buffer, "image/png"))],
            data={"use_ai": "true", "mode": "comprehensive"}
        )

        assert response.status_code == 200
        job_id = response.json()["job_id"]

        # Track tokens evolution
        cv_tokens = None
        ai_tokens = None

        start_time = time.time()

        for attempt in range(100):  # Max 100 attempts (20 seconds)
            await asyncio.sleep(0.2)

            status_response = await client.get(f"/api/extract/{job_id}")
            status_data = status_response.json()

            elapsed = time.time() - start_time

            if status_data["status"] == "completed" and not cv_tokens:
                # First completion: CV-only
                cv_tokens = status_data["tokens"]
                assert elapsed < 2.0, "CV extraction took too long"

            if status_data["status"] == "completed" and status_data.get("progress", 0) == 100:
                # Final completion: All AI enhancements
                ai_tokens = status_data["tokens"]
                break

        # Validate CV tokens
        assert cv_tokens is not None
        assert "palette" in cv_tokens
        assert "primary" in cv_tokens["palette"]
        assert "opencv_cv" in cv_tokens["palette"]["primary"]["extractors"]

        # Validate AI tokens enhanced CV tokens
        assert ai_tokens is not None

        # Check palette enhanced
        primary_ai = ai_tokens["palette"]["primary"]
        assert len(primary_ai["extractors"]) > 1  # Should have CV + AI extractors

        # Check AI added semantic information
        if "name" in primary_ai:
            assert len(primary_ai["name"]) > 0  # GPT-4 added color name

        # Check completeness
        if "_metadata" in ai_tokens and "completeness_analysis" in ai_tokens["_metadata"]:
            completeness = ai_tokens["_metadata"]["completeness_analysis"]
            assert completeness["completeness_score"] > 70  # At least 70% complete
```

### Test Case 3: Circuit Breaker Validation

```python
"""
Test Case: Circuit Breaker - AI API Failure
Validates graceful degradation when AI APIs fail
"""

@pytest.mark.asyncio
async def test_circuit_breaker_ai_failure():
    """
    GIVEN: GPT-4 API is down (simulated)
    WHEN: POST /api/extract with use_ai=true
    THEN: Returns CV results immediately
    AND: Attempts AI enhancement
    AND: Gracefully degrades to CV-only results
    AND: Logs AI failure but doesn't fail entire extraction
    """
    # Mock GPT-4 to raise exception
    with patch('extractors.ai.gpt4_vision_extractor.GPT4VisionExtractor') as mock_gpt4:
        mock_gpt4.side_effect = Exception("OpenAI API timeout")

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            image_bytes = ImageFactory().tobytes()

            response = await client.post(
                "/api/extract",
                files=[("files", ("test.png", io.BytesIO(image_bytes), "image/png"))],
                data={"use_ai": "true"}
            )

            assert response.status_code == 200
            job_id = response.json()["job_id"]

            # Wait for completion
            for _ in range(20):
                await asyncio.sleep(0.5)

                status_response = await client.get(f"/api/extract/{job_id}")
                status_data = status_response.json()

                if status_data["status"] == "completed":
                    tokens = status_data["tokens"]

                    # Should have CV tokens
                    assert "palette" in tokens
                    assert "primary" in tokens["palette"]

                    # Should only have opencv_cv extractor (AI failed)
                    primary = tokens["palette"]["primary"]
                    assert "opencv_cv" in primary["extractors"]

                    # Should not have AI extractors
                    assert "gpt4_vision" not in primary["extractors"]

                    return

            pytest.fail("Job did not complete in time")
```

### Test Case 4: Rate Limiting

```python
"""
Test Case: Rate Limiting
Validates 10 requests/minute limit per IP
"""

@pytest.mark.asyncio
async def test_rate_limiting():
    """
    GIVEN: Rate limit of 10 requests/minute
    WHEN: Client sends 11 requests in rapid succession
    THEN: First 10 requests succeed (200)
    AND: 11th request fails with 429 (Too Many Requests)
    AND: Response includes Retry-After header
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        image_bytes = ImageFactory().tobytes()

        # Send 11 requests
        responses = []
        for i in range(11):
            response = await client.post(
                "/api/extract",
                files=[("files", (f"test_{i}.png", io.BytesIO(image_bytes), "image/png"))],
                data={"use_ai": "false"}
            )
            responses.append(response)

        # First 10 should succeed
        for i in range(10):
            assert responses[i].status_code == 200, f"Request {i} failed"

        # 11th should be rate limited
        assert responses[10].status_code == 429
        assert "Retry-After" in responses[10].headers or "detail" in responses[10].json()
```

### Test Case 5: Malformed Input Validation

```python
"""
Test Case: Input Validation
Validates rejection of invalid inputs
"""

@pytest.mark.asyncio
async def test_malformed_input_validation():
    """
    GIVEN: Various invalid inputs
    WHEN: POST /api/extract with invalid data
    THEN: Returns 400 Bad Request with descriptive error
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:

        # Test 1: No files
        response = await client.post("/api/extract", data={"use_ai": "false"})
        assert response.status_code == 400
        assert "No files uploaded" in response.json()["detail"]

        # Test 2: Too many files
        files = [("files", (f"test_{i}.png", io.BytesIO(b"fake"), "image/png")) for i in range(11)]
        response = await client.post("/api/extract", files=files, data={"use_ai": "false"})
        assert response.status_code == 400
        assert "Maximum 10 images allowed" in response.json()["detail"]

        # Test 3: Invalid file type
        response = await client.post(
            "/api/extract",
            files=[("files", ("test.txt", io.BytesIO(b"not an image"), "text/plain"))],
            data={"use_ai": "false"}
        )
        assert response.status_code == 400
        assert "Invalid file type" in str(response.json())

        # Test 4: Corrupted image
        response = await client.post(
            "/api/extract",
            files=[("files", ("corrupted.png", io.BytesIO(b"\x89PNG\r\n\x1a\n...truncated"), "image/png"))],
            data={"use_ai": "false"}
        )
        assert response.status_code == 400
```

---

## 10. Implementation Checklist

### Immediate Actions (Week 1)

- [ ] **Set up test infrastructure**
  - [ ] Install pytest-asyncio, pytest-timeout, pytest-recording
  - [ ] Create `backend/tests/conftest.py` with fixtures
  - [ ] Set up `backend/tests/mocks/` directory
  - [ ] Add `backend/tests/factories.py` for test data generation

- [ ] **Implement AI API mocking**
  - [ ] Create mock responses (`mocks/ai_responses.py`)
  - [ ] Add mock extractors (`conftest.py` fixtures)
  - [ ] Set up VCR cassettes for schema validation
  - [ ] Document mock strategy in `tests/README.md`

- [ ] **Add WebSocket tests (basic 5)**
  - [ ] Test 1: Basic connection & extraction
  - [ ] Test 2: Connection limit enforcement
  - [ ] Test 3: Rate limit - message spam
  - [ ] Test 4: Auto-reconnect simulation
  - [ ] Test 5: Concurrent connections from different IPs

- [ ] **Set up CI/CD pipeline**
  - [ ] Create `.github/workflows/api-tests.yml`
  - [ ] Add test coverage reporting (Codecov)
  - [ ] Configure pre-commit hooks
  - [ ] Set up test result notifications (Slack/email)

### Short-term Goals (Weeks 2-3)

- [ ] **Complete WebSocket test suite (15 total)**
  - [ ] Add progressive extraction tests (Tests 6-9)
  - [ ] Add error handling tests (Tests 10-12)
  - [ ] Add timeout/performance tests (Tests 13-15)

- [ ] **Expand integration tests**
  - [ ] Multi-extractor coordination tests
  - [ ] AI fallback scenario tests
  - [ ] Circuit breaker validation tests
  - [ ] Database retry logic tests

- [ ] **Add contract testing**
  - [ ] OpenAPI schema validation
  - [ ] Pydantic schema versioning tests
  - [ ] Breaking change detection
  - [ ] (Optional) Set up Pact consumer-driven contracts

- [ ] **Create test data library**
  - [ ] Generate 50+ fixture images
  - [ ] Create expected output JSONs
  - [ ] Document fixture usage in tests

### Long-term Goals (Week 4+)

- [ ] **Performance testing**
  - [ ] Run Locust load tests in CI (baseline, stress, spike)
  - [ ] Add k6 performance tests
  - [ ] Set up performance regression detection
  - [ ] Document performance baselines

- [ ] **Monitoring & observability**
  - [ ] Set up test result dashboards (Grafana)
  - [ ] Add test failure alerting
  - [ ] Track test execution times (detect regressions)
  - [ ] Generate weekly test health reports

- [ ] **Documentation**
  - [ ] Update `CONTRIBUTING.md` with test guidelines
  - [ ] Create test writing guide for new contributors
  - [ ] Document common test patterns
  - [ ] Add troubleshooting guide for flaky tests

---

## Conclusion

This comprehensive API testing strategy provides:

1. **85% test coverage target** (up from current 35%)
2. **15 WebSocket tests** covering all critical scenarios
3. **Zero-cost AI API testing** via multi-level mocking
4. **Automated CI/CD pipeline** with GitHub Actions
5. **Performance benchmarks** using Locust and k6
6. **Contract validation** with OpenAPI schemas

### Next Steps

1. **Review & approve** this strategy with the team
2. **Allocate 4 weeks** for implementation (1 developer)
3. **Start with Phase 1** (Foundation - Week 1)
4. **Track progress** weekly using checklist above
5. **Adjust** strategy based on learnings

### Success Metrics

- ✅ Test coverage: 35% → 85%
- ✅ WebSocket coverage: 10% → 90%
- ✅ CI/CD test run time: <15 minutes
- ✅ Test reliability: >99% pass rate
- ✅ AI API costs in tests: $0/month (mocked)
- ✅ Performance baselines documented
- ✅ Zero production incidents from untested code paths

---

**Document Version:** 2.0
**Last Updated:** 2025-11-07
**Owner:** Backend Team
**Reviewers:** Engineering Lead, QA Lead, DevOps Lead

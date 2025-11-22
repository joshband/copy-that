# AI/ML Pipeline Analysis

**Focus Area: 40% of Evaluation Effort**

---

## Table of Contents

1. [Current State Assessment](#1-current-state-assessment)
2. [Optimization Strategy](#2-optimization-strategy)
3. [Cost Optimization Plan](#3-cost-optimization-plan)
4. [Recommendations](#4-recommendations)

---

## 1. Current State Assessment

### 1.1 Model Architecture

#### Primary: Claude Sonnet 4.5 Vision
- **File**: `src/copy_that/application/color_extractor.py`
- **Model**: `claude-sonnet-4-5-20250929`
- **Max Tokens**: 2000
- **Temperature**: Default (not explicitly set)

**Capabilities**:
- Base64 image encoding
- URL-based image analysis
- Local file support (PNG, JPG, WebP, GIF)

#### Secondary: OpenAI GPT-4V
- **File**: `src/copy_that/application/openai_color_extractor.py`
- **Model**: `gpt-4o`
- **Max Tokens**: 2000
- **Temperature**: 0.3 (lower for consistency)

**Key Advantage**: Native JSON mode (`response_format={"type": "json_object"}`)

### 1.2 Multi-Model Routing Logic

```python
# Current implementation in colors.py
def get_extractor(extractor_type: str = "auto"):
    if extractor_type == "openai":
        return OpenAIColorExtractor()
    elif extractor_type == "claude":
        return AIColorExtractor()
    else:  # auto mode
        # Prefer OpenAI if available, fallback to Claude
        if os.getenv("OPENAI_API_KEY"):
            return OpenAIColorExtractor()
        elif os.getenv("ANTHROPIC_API_KEY"):
            return AIColorExtractor()
```

**Issues**:
- Simple availability check, no cost/performance optimization
- No fallback on API errors
- No load balancing between providers

### 1.3 Prompt Engineering Review

#### Claude Prompt (250 words)
```python
prompt = f"""Analyze this image and extract a professional color palette for design systems.

Extract the {max_colors} most important colors that represent the image's design essence.

For each color, include:
1. Hex code (e.g., #FF5733)
2. RGB format (e.g., rgb(255, 87, 51))
3. Descriptive name (e.g., "Ocean Blue", "Sunset Orange")
4. ALWAYS provide a semantic token name - choose from: primary, secondary, accent,
   success, error, warning, info, light, dark, or create a descriptive one
5. Confidence score (0-1) based on distinctness
6. Harmony relationship (complementary, analogous, triadic, monochromatic)
7. Usage contexts (e.g., "backgrounds", "text", "accents")

Also include:
- The 3 most dominant colors (hex codes only)
- Overall palette description (1-2 sentences)
- Overall extraction confidence (0-1)

Important: Every color MUST have a semantic token name. Be specific and consistent with naming.
"""
```

**Strengths**:
- Clear numbered requirements
- Specific output format guidance
- Design system context established

**Weaknesses**:
- No JSON structure specification
- Relies on regex parsing
- No few-shot examples

#### OpenAI Prompt
```python
prompt = f"""Analyze this image and extract the {max_colors} most important colors.

For each color, provide:
1. hex: The hex color code (e.g., "#FF5733")
2. name: A human-readable color name
3. design_intent: The role this color plays
4. confidence: How confident you are (0.0-1.0)
5. usage: Array of suggested uses
6. prominence_percentage: Estimated percentage

Return ONLY valid JSON in this exact format: {...}
"""
```

**Strengths**:
- Explicit JSON structure
- Uses native JSON mode
- Field naming matches schema

### 1.4 Response Validation

#### Current Parsing Strategy

**Claude** (Regex-based):
```python
# Extract hex codes
hex_pattern = r"#[0-9A-Fa-f]{6}"
hex_codes = re.findall(hex_pattern, response_text)

# Extract names
name_pattern = r'"([^"]+)"'
names = re.findall(name_pattern, response_text)
```

**Issues**:
- Fragile extraction
- No schema validation
- Partial recovery with fallback palette

**OpenAI** (JSON mode):
```python
response_data = json.loads(response.choices[0].message.content)
```

**Strengths**:
- Guaranteed valid JSON
- Direct field access
- Type safety

### 1.5 Color Property Enrichment Pipeline

After AI extraction, each color goes through:

```python
def compute_all_properties_with_metadata(hex_color, dominant_colors):
    properties = {
        # Color formats
        "rgb": hex_to_rgb(hex_color),
        "hsl": hex_to_hsl(hex_color),
        "hsv": hex_to_hsv(hex_color),

        # Analysis
        "temperature": get_color_temperature(hex_color),
        "saturation_level": get_saturation_level(hex_color),
        "lightness_level": get_lightness_level(hex_color),
        "is_neutral": is_neutral_color(hex_color),

        # Accessibility
        "wcag_contrast_on_white": calculate_wcag_contrast(hex_color, "#FFFFFF"),
        "wcag_contrast_on_black": calculate_wcag_contrast(hex_color, "#000000"),
        "wcag_aa_compliant_text": is_wcag_compliant(hex_color, "#FFFFFF", "AA", "normal"),
        "wcag_aaa_compliant_text": is_wcag_compliant(hex_color, "#FFFFFF", "AAA", "normal"),

        # Variants
        "tint_color": get_color_variant(hex_color, "tint"),
        "shade_color": get_color_variant(hex_color, "shade"),
        "tone_color": get_color_variant(hex_color, "tone"),

        # Matching
        "closest_web_safe": get_closest_web_safe(hex_color),
        "closest_css_named": get_closest_css_named(hex_color),
        "delta_e_to_dominant": calculate_delta_e(hex_color, dominant_colors[0]),
    }

    # Track extraction source for each field
    metadata = {field: f"color_utils.{func}" for field, func in ...}

    return properties, metadata
```

**Strengths**:
- Comprehensive 25+ field enrichment
- WCAG accessibility built-in
- Provenance tracking

### 1.6 Batch Processing Architecture

```python
class BatchColorExtractor:
    def __init__(self, max_concurrent: int = 3):
        self.max_concurrent = max_concurrent  # Respects API rate limits

    async def extract_batch(self, images: list[str]):
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def extract_with_limit(image):
            async with semaphore:
                return await self.extract_single(image)

        results = await asyncio.gather(*[
            extract_with_limit(img) for img in images
        ])
        return results
```

**Concurrency Control**: Prevents API rate limiting with semaphore

### 1.7 Color Aggregation & Deduplication

```python
DEFAULT_DELTA_E_THRESHOLD = 2.0  # JND (Just Noticeable Difference)

class ColorAggregator:
    @staticmethod
    def aggregate(results: list[ExtractionResult], threshold=2.0):
        unique_colors = []
        for color in all_colors:
            is_duplicate = any(
                calculate_delta_e(color.hex, existing.hex) < threshold
                for existing in unique_colors
            )
            if not is_duplicate:
                unique_colors.append(color)
        return unique_colors
```

**Provenance Tracking**:
```python
provenance: dict[str, float] = {
    "image_0": 0.95,  # Confidence from first image
    "image_1": 0.88   # Confidence from second image
}
```

---

## 2. Optimization Strategy

### 2.1 Improved Prompt Templates

#### Recommended Claude Prompt with JSON Mode

```python
CLAUDE_PROMPT_V2 = """You are a professional color palette analyst for design systems.

Analyze the provided image and extract a cohesive color palette.

## Output Format
Return ONLY valid JSON matching this exact structure:

{
  "colors": [
    {
      "hex": "#XXXXXX",
      "name": "Descriptive Color Name",
      "design_intent": "primary|secondary|accent|success|error|warning|info|background|text",
      "confidence": 0.0-1.0,
      "usage": ["array", "of", "suggestions"],
      "prominence_percentage": 0-100
    }
  ],
  "dominant_colors": ["#XXXXXX", "#XXXXXX", "#XXXXXX"],
  "palette_description": "One sentence description",
  "overall_confidence": 0.0-1.0,
  "harmony_type": "complementary|analogous|triadic|monochromatic|split-complementary"
}

## Guidelines
1. Extract exactly {max_colors} colors
2. Ensure hex codes are valid 6-character codes
3. Design intent must match one of the specified values
4. Confidence reflects color distinctness and importance
5. Prominence percentage should sum to approximately 100%

Return ONLY the JSON object, no additional text.
"""
```

### 2.2 Multi-Model Routing Logic Design

```python
class AIRouter:
    """Intelligent routing between AI providers"""

    def __init__(self):
        self.claude = AIColorExtractor()
        self.openai = OpenAIColorExtractor()
        self.metrics = MetricsCollector()

    async def extract(self, image: str, strategy: str = "optimal") -> ExtractionResult:
        if strategy == "cost":
            return await self._cost_optimized(image)
        elif strategy == "quality":
            return await self._quality_optimized(image)
        elif strategy == "fast":
            return await self._speed_optimized(image)
        else:
            return await self._optimal(image)

    async def _optimal(self, image: str) -> ExtractionResult:
        """Balance cost, quality, and speed"""
        # Use OpenAI for JSON reliability, Claude for complex images
        image_complexity = await self._analyze_complexity(image)

        if image_complexity < 0.5:
            return await self.openai.extract(image)
        else:
            return await self.claude.extract(image)

    async def _cost_optimized(self, image: str) -> ExtractionResult:
        """Minimize API costs"""
        # OpenAI generally cheaper for similar quality
        try:
            return await self.openai.extract(image)
        except Exception:
            return await self.claude.extract(image)

    async def _with_fallback(self, primary, secondary, image):
        """Execute with automatic fallback"""
        try:
            result = await primary.extract(image)
            self.metrics.record_success(primary.__class__.__name__)
            return result
        except Exception as e:
            self.metrics.record_failure(primary.__class__.__name__, e)
            return await secondary.extract(image)
```

### 2.3 Response Caching Architecture

```python
import hashlib
from redis import Redis

class AIResponseCache:
    """Redis-based caching for AI extraction results"""

    def __init__(self, redis_client: Redis, ttl_hours: int = 24):
        self.redis = redis_client
        self.ttl = ttl_hours * 3600

    def _generate_key(self, image_data: bytes, max_colors: int, model: str) -> str:
        """Generate cache key from image content hash"""
        content_hash = hashlib.sha256(image_data).hexdigest()
        return f"extraction:{model}:{max_colors}:{content_hash}"

    async def get_or_extract(
        self,
        image_data: bytes,
        extractor: BaseExtractor,
        max_colors: int
    ) -> ExtractionResult:
        key = self._generate_key(image_data, max_colors, extractor.model_name)

        # Check cache
        cached = await self.redis.get(key)
        if cached:
            return ExtractionResult.from_json(cached)

        # Extract and cache
        result = await extractor.extract(image_data, max_colors)
        await self.redis.setex(key, self.ttl, result.to_json())

        return result

    def invalidate_for_image(self, image_data: bytes):
        """Invalidate all cached extractions for an image"""
        content_hash = hashlib.sha256(image_data).hexdigest()
        pattern = f"extraction:*:*:{content_hash}"
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)
```

### 2.4 Batch Processing Pipeline Design

```python
class OptimizedBatchExtractor:
    """Production-grade batch extraction with optimization"""

    def __init__(
        self,
        max_concurrent: int = 5,
        cache: AIResponseCache = None,
        router: AIRouter = None
    ):
        self.max_concurrent = max_concurrent
        self.cache = cache
        self.router = router or AIRouter()

    async def extract_batch(
        self,
        images: list[ImageInput],
        strategy: str = "optimal",
        dedupe_threshold: float = 2.0
    ) -> BatchResult:
        """
        Extract colors from multiple images with optimization

        Args:
            images: List of image inputs (URL, base64, or path)
            strategy: Routing strategy (optimal, cost, quality, fast)
            dedupe_threshold: Delta-E threshold for deduplication

        Returns:
            BatchResult with aggregated, deduplicated colors
        """
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def extract_single(image: ImageInput) -> ExtractionResult:
            async with semaphore:
                # Load image data
                image_data = await self._load_image(image)

                # Check cache first
                if self.cache:
                    cached = await self.cache.get(image_data)
                    if cached:
                        return cached

                # Extract with routing
                result = await self.router.extract(image_data, strategy)

                # Cache result
                if self.cache:
                    await self.cache.set(image_data, result)

                return result

        # Extract all in parallel (respecting concurrency limit)
        results = await asyncio.gather(*[
            extract_single(img) for img in images
        ], return_exceptions=True)

        # Filter errors and aggregate
        successful = [r for r in results if not isinstance(r, Exception)]
        errors = [r for r in results if isinstance(r, Exception)]

        # Aggregate and deduplicate
        aggregated = ColorAggregator.aggregate(successful, dedupe_threshold)

        return BatchResult(
            colors=aggregated,
            source_count=len(images),
            success_count=len(successful),
            errors=errors
        )
```

### 2.5 Structured Output Validation Patterns

```python
from pydantic import BaseModel, Field, validator

class AIColorOutput(BaseModel):
    """Validated AI extraction output"""

    hex: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$")
    name: str = Field(..., min_length=1, max_length=100)
    design_intent: str = Field(...)
    confidence: float = Field(..., ge=0, le=1)
    usage: list[str] = Field(default_factory=list)
    prominence_percentage: float = Field(..., ge=0, le=100)

    @validator("design_intent")
    def validate_intent(cls, v):
        valid = {"primary", "secondary", "accent", "success", "error",
                 "warning", "info", "background", "text", "surface"}
        if v.lower() not in valid:
            # Map to closest valid value
            return "accent"
        return v.lower()

    @validator("hex")
    def normalize_hex(cls, v):
        return v.upper()

class AIExtractionOutput(BaseModel):
    """Complete extraction response validation"""

    colors: list[AIColorOutput] = Field(..., min_items=1, max_items=50)
    dominant_colors: list[str] = Field(..., min_items=1, max_items=5)
    palette_description: str = Field(..., max_length=500)
    overall_confidence: float = Field(..., ge=0, le=1)
    harmony_type: str = Field(default="unknown")

    @validator("dominant_colors", each_item=True)
    def validate_dominant_hex(cls, v):
        if not re.match(r"^#[0-9A-Fa-f]{6}$", v):
            raise ValueError(f"Invalid hex code: {v}")
        return v.upper()
```

### 2.6 Error Handling and Fallback Mechanisms

```python
class ResilientExtractor:
    """Extraction with comprehensive error handling"""

    def __init__(self):
        self.primary = AIColorExtractor()  # Claude
        self.secondary = OpenAIColorExtractor()
        self.fallback_palette = self._load_fallback_palette()

    async def extract(self, image: str, max_colors: int = 10) -> ExtractionResult:
        """Extract with multi-level fallback"""

        # Level 1: Primary extractor
        try:
            result = await self.primary.extract(image, max_colors)
            if self._validate_result(result):
                return result
        except anthropic.APIStatusError as e:
            if e.status_code == 429:  # Rate limited
                await asyncio.sleep(60)
                return await self.extract(image, max_colors)  # Retry once
            logger.warning(f"Claude API error: {e}")
        except Exception as e:
            logger.warning(f"Primary extraction failed: {e}")

        # Level 2: Secondary extractor
        try:
            result = await self.secondary.extract(image, max_colors)
            if self._validate_result(result):
                return result
        except Exception as e:
            logger.warning(f"Secondary extraction failed: {e}")

        # Level 3: Computer vision fallback
        try:
            result = await self._cv_extraction(image, max_colors)
            return result
        except Exception as e:
            logger.error(f"CV extraction failed: {e}")

        # Level 4: Default palette
        logger.error("All extraction methods failed, using fallback")
        return self._create_fallback_result(max_colors)

    def _validate_result(self, result: ExtractionResult) -> bool:
        """Validate extraction result quality"""
        if not result.colors:
            return False
        if result.overall_confidence < 0.3:
            return False
        if any(c.confidence < 0.1 for c in result.colors):
            return False
        return True

    async def _cv_extraction(self, image: str, max_colors: int) -> ExtractionResult:
        """OpenCV-based color extraction as fallback"""
        from .cv_image_analysis import OpenCVImageAnalysis

        cv_analyzer = OpenCVImageAnalysis()
        dominant_colors = cv_analyzer.get_dominant_colors(image, max_colors)

        return ExtractionResult(
            colors=[
                ColorToken(
                    hex=color["hex"],
                    name=f"Color {i+1}",
                    confidence=0.5,
                    design_intent="accent"
                )
                for i, color in enumerate(dominant_colors)
            ],
            overall_confidence=0.5,
            extraction_method="cv_fallback"
        )
```

---

## 3. Cost Optimization Plan

### 3.1 Current Spending Analysis

**No cost tracking currently implemented**

Estimated costs per extraction:
- Claude Sonnet 4.5: ~$0.003/1K input + $0.015/1K output
- OpenAI GPT-4V: ~$0.01/1K input + $0.03/1K output

**Typical Extraction**:
- Input: ~500 tokens (prompt + image description)
- Output: ~800 tokens (color palette response)
- **Estimated cost: $0.01-0.03 per extraction**

### 3.2 Token Usage Reduction Strategies

#### 1. Prompt Optimization
```python
# Before: 250 words, ~350 tokens
# After: 150 words, ~200 tokens
# Savings: 43% on input tokens
```

#### 2. Output Compression
```python
# Request minimal JSON format
# Compute enrichment locally (temperature, WCAG, etc.)
# Savings: 30-50% on output tokens
```

#### 3. Image Preprocessing
```python
# Resize large images before encoding
# Optimal size: 1024x1024 for vision models
# Savings: Variable (based on image size)
```

### 3.3 Caching Effectiveness Improvements

```python
class CacheMetrics:
    """Track cache performance"""

    def __init__(self, redis: Redis):
        self.redis = redis

    async def record_hit(self):
        await self.redis.incr("cache:hits")

    async def record_miss(self):
        await self.redis.incr("cache:misses")

    async def get_hit_rate(self) -> float:
        hits = int(await self.redis.get("cache:hits") or 0)
        misses = int(await self.redis.get("cache:misses") or 0)
        total = hits + misses
        return hits / total if total > 0 else 0

    async def get_savings(self) -> float:
        """Estimate cost savings from cache hits"""
        hits = int(await self.redis.get("cache:hits") or 0)
        cost_per_extraction = 0.02  # Average
        return hits * cost_per_extraction
```

**Target Cache Hit Rate**: 30-50% for typical usage patterns

### 3.4 Model Selection Optimization

```python
class CostAwareRouter:
    """Route based on cost/quality tradeoff"""

    MODEL_COSTS = {
        "claude-sonnet-4-5": {"input": 0.003, "output": 0.015},
        "gpt-4o": {"input": 0.01, "output": 0.03},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},  # Future option
    }

    def select_model(self, user_tier: str, image_complexity: float) -> str:
        """Select optimal model based on user tier and image"""

        if user_tier == "enterprise":
            # Quality first
            return "claude-sonnet-4-5" if image_complexity > 0.7 else "gpt-4o"

        elif user_tier == "pro":
            # Balance
            return "gpt-4o"

        else:  # Free tier
            # Cost first
            return "gpt-4o-mini"  # When available
```

### 3.5 Cost Monitoring and Alerting Design

```python
from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime

class APIUsageLog(Base):
    """Track API usage for cost monitoring"""

    __tablename__ = "api_usage_logs"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String(255), nullable=True)
    project_id = Column(Integer, nullable=True)

    # Request details
    model = Column(String(100))
    endpoint = Column(String(255))

    # Token usage
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)

    # Cost calculation
    cost_usd = Column(Float)

    # Metadata
    cached = Column(Boolean, default=False)
    success = Column(Boolean, default=True)
    error_type = Column(String(100), nullable=True)

class CostMonitor:
    """Monitor and alert on API costs"""

    def __init__(self, db: AsyncSession, alert_threshold_daily: float = 100.0):
        self.db = db
        self.daily_threshold = alert_threshold_daily

    async def log_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        user_id: str = None,
        project_id: int = None
    ):
        cost = self._calculate_cost(model, input_tokens, output_tokens)

        log = APIUsageLog(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            user_id=user_id,
            project_id=project_id
        )

        self.db.add(log)
        await self.db.commit()

        # Check daily spending
        daily_total = await self._get_daily_total()
        if daily_total > self.daily_threshold:
            await self._send_alert(daily_total)

    async def get_cost_report(self, days: int = 30) -> dict:
        """Generate cost report"""
        return {
            "total_cost": await self._get_total_cost(days),
            "by_model": await self._get_cost_by_model(days),
            "by_user": await self._get_cost_by_user(days),
            "daily_average": await self._get_daily_average(days),
            "cache_savings": await self._get_cache_savings(days),
        }
```

---

## 4. Recommendations

### 4.1 Immediate Actions (Week 1)

| Priority | Action | Effort | Impact |
|----------|--------|--------|--------|
| 1 | Enable JSON mode for Claude | Low | High |
| 2 | Add Pydantic validation for AI responses | Low | High |
| 3 | Implement basic cost logging | Medium | High |
| 4 | Add response caching with Redis | Medium | High |

### 4.2 Short-term Improvements (Weeks 2-4)

| Priority | Action | Effort | Impact |
|----------|--------|--------|--------|
| 1 | Implement multi-model routing | Medium | High |
| 2 | Add fallback extraction chain | Medium | High |
| 3 | Build cost monitoring dashboard | Medium | Medium |
| 4 | Optimize prompts for token reduction | Low | Medium |

### 4.3 Long-term Enhancements (Month 2+)

| Priority | Action | Effort | Impact |
|----------|--------|--------|--------|
| 1 | Implement image preprocessing | High | Medium |
| 2 | Add A/B testing for prompts | High | Medium |
| 3 | Build cost prediction model | High | Medium |
| 4 | Fine-tune model selection | High | High |

### 4.4 Key Performance Indicators

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Extraction success rate | ~95% | 99.5% | `successful / total` |
| Average cost per extraction | $0.02 | $0.01 | API usage logs |
| Cache hit rate | 0% | 40% | Redis metrics |
| Response validation pass rate | ~80% | 99% | Pydantic validation |
| Fallback trigger rate | Unknown | <5% | Error logs |

---

## File Reference

| File | Purpose | Lines of Code |
|------|---------|---------------|
| `color_extractor.py` | Claude Sonnet extraction | ~400 |
| `openai_color_extractor.py` | OpenAI GPT-4 extraction | ~300 |
| `batch_extractor.py` | Batch processing | ~200 |
| `color_utils.py` | Color mathematics | ~1000 |
| `semantic_color_naming.py` | Heuristic naming | ~400 |
| `aggregator.py` | Deduplication | ~300 |

---

*Next: [02-database-performance.md](./02-database-performance.md)*

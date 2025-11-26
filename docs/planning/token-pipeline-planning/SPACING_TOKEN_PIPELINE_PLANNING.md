# Spacing Token Pipeline: Comprehensive Implementation Planning

**Version:** 1.0 | **Date:** 2025-11-22 | **Status:** Planning Document

This document provides a comprehensive implementation plan for the spacing token pipeline, modeled after the proven color token implementation patterns.

---

## Executive Summary

The spacing token pipeline will extract, process, aggregate, and export spacing-related design tokens from images. Following the established patterns from the color token implementation, this pipeline will support:

- AI-powered spacing extraction using Claude/OpenAI vision
- Parallel asynchronous batch processing
- Real-time SSE streaming for progress updates
- Delta-based deduplication and aggregation
- Multiple export formats (W3C, CSS, React, etc.)

---

## 1. Architecture Overview

### 1.1 Pipeline Flow Diagram

```
1. Image Input (URL/Base64/File)
       |
       v
2. AI Spacing Extractor (Claude/OpenAI)
   - Sends image to AI vision model
   - Receives spacing measurements with context
       |
       v
3. Response Parsing
   - Extract spacing values from AI response
   - Determine semantic intent (padding, margin, gap)
       |
       v
4. Property Computation (spacing_utils.py)
   - compute_all_spacing_properties()
   - Returns: properties dict + extraction_metadata dict

   Computes:
   - rem/em conversions
   - scale position detection (xs, sm, md, lg, xl)
   - base unit inference (4px, 8px systems)
   - rhythm analysis (consistent/irregular)
   - grid compliance detection
   - responsive breakpoint suggestions
       |
       v
5. Semantic Naming (semantic_spacing_naming.py)
   - analyze_spacing() returns names dict:
     {simple, descriptive, contextual, scale_position}
       |
       v
6. SpacingToken Construction
   - Merge AI results + computed properties + semantic names
   - Track extraction_metadata for provenance
       |
       v
7. For Batch Extraction: Aggregation (aggregator.py)
   - SpacingAggregator.aggregate_batch()
   - Deduplicate using percentage threshold (default 10%)
   - Track provenance: which images contributed each spacing
   - Generate statistics
       |
       v
8. Database Persistence
   - Create ExtractionJob record
   - Insert SpacingToken records to spacing_tokens table
   - Link to project_id and library_id
       |
       v
9. API Response
   - Transform to SpacingTokenDetailResponse schema
   - JSON serialize nested fields
       |
       v
10. Export (generators/)
    - BaseGenerator subclass transforms TokenLibrary
    - W3C, CSS, React, Tailwind formats
```

### 1.2 Directory Structure

```
src/copy_that/
├── application/
│   ├── spacing_extractor.py          # Main AI spacing extractor
│   ├── openai_spacing_extractor.py   # Alternative OpenAI extractor
│   ├── spacing_utils.py              # Utility functions for spacing
│   └── semantic_spacing_naming.py    # Perceptual naming
├── tokens/
│   └── spacing/
│       ├── __init__.py
│       ├── aggregator.py             # Batch deduplication
│       └── models.py                 # Pydantic models
├── domain/
│   └── models.py                     # Add SpacingToken SQLAlchemy model
├── generators/
│   ├── spacing_w3c_generator.py      # W3C Design Tokens format
│   ├── spacing_css_generator.py      # CSS custom properties
│   └── spacing_react_generator.py    # React theme exports
└── interfaces/api/
    └── spacing.py                    # FastAPI router
```

---

## 2. Data Models

### 2.1 SpacingToken Pydantic Model

```python
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class SpacingScale(str, Enum):
    NONE = "none"
    XXS = "2xs"
    XS = "xs"
    SM = "sm"
    MD = "md"
    LG = "lg"
    XL = "xl"
    XXL = "2xl"
    XXXL = "3xl"

class SpacingType(str, Enum):
    PADDING = "padding"
    MARGIN = "margin"
    GAP = "gap"
    INSET = "inset"
    GUTTER = "gutter"
    MIXED = "mixed"

class SpacingToken(BaseModel):
    """Comprehensive spacing token with all computed properties"""

    # Core values
    value_px: int = Field(..., description="Spacing value in pixels")
    value_rem: float = Field(..., description="Spacing value in rem (base 16px)")
    value_em: float = Field(..., description="Spacing value in em")

    # Scale information
    scale: SpacingScale = Field(..., description="Position in spacing scale")
    base_unit: int = Field(default=4, description="Detected base unit (4px or 8px)")
    multiplier: float = Field(..., description="Multiplier of base unit")

    # Semantic information
    name: str = Field(..., description="Generated semantic name")
    spacing_type: SpacingType = Field(..., description="Type of spacing usage")
    design_intent: str = Field(..., description="AI-detected design intent")

    # Context information
    use_case: str = Field(..., description="Suggested use case")
    context: str = Field(..., description="Where spacing was detected")

    # Analysis
    confidence: float = Field(..., ge=0, le=1, description="Extraction confidence")
    is_grid_compliant: bool = Field(..., description="Fits common grid systems")
    rhythm_consistency: str = Field(..., description="consistent/irregular/mixed")

    # Responsive suggestions
    responsive_scales: dict | None = Field(default=None, description="Breakpoint adjustments")

    # Semantic names (like color)
    semantic_names: dict | None = Field(default=None, description="Multiple naming schemes")

    # Relationships
    related_to: list[str] | None = Field(default=None, description="Related spacing tokens")
    component_usage: list[str] | None = Field(default=None, description="Components using this")

    # Metadata
    extraction_metadata: dict | None = Field(default=None, description="Extraction provenance")
```

### 2.2 SQLAlchemy Model

```python
from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from copy_that.domain.base import Base

class SpacingToken(Base):
    """Database model for spacing tokens"""

    __tablename__ = "spacing_tokens"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    library_id = Column(Integer, ForeignKey("token_libraries.id"), nullable=True)
    extraction_job_id = Column(Integer, ForeignKey("extraction_jobs.id"), nullable=True)

    # Core values
    value_px = Column(Integer, nullable=False)
    value_rem = Column(Float, nullable=False)
    value_em = Column(Float, nullable=False)

    # Scale information
    scale = Column(String(20), nullable=False)
    base_unit = Column(Integer, default=4)
    multiplier = Column(Float, nullable=False)

    # Semantic information
    name = Column(String(255), nullable=False)
    spacing_type = Column(String(50), nullable=False)
    design_intent = Column(String(500))

    # Context
    use_case = Column(String(500))
    context = Column(String(500))

    # Analysis
    confidence = Column(Float, nullable=False)
    is_grid_compliant = Column(Boolean, default=True)
    rhythm_consistency = Column(String(50))

    # JSON fields
    responsive_scales = Column(JSON)
    semantic_names = Column(JSON)
    related_to = Column(JSON)
    component_usage = Column(JSON)
    extraction_metadata = Column(JSON)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="spacing_tokens")
    library = relationship("TokenLibrary", back_populates="spacing_tokens")
```

---

## 3. Core Components

### 3.1 AI Spacing Extractor

**File:** `src/copy_that/application/spacing_extractor.py`

```python
class AISpacingExtractor:
    """
    Extract spacing tokens from images using Claude Sonnet 4.5.

    Analyzes:
    - Component padding (internal spacing)
    - Margins between elements
    - Grid gaps and gutters
    - Vertical rhythm
    - Consistent spacing patterns

    Prompt Strategy:
    - Ask for pixel measurements
    - Request context (where spacing is used)
    - Identify spacing type (padding/margin/gap)
    - Detect base unit system (4px vs 8px)
    """

    def __init__(self, model: str = "claude-sonnet-4-5-20250929"):
        self.client = anthropic.Anthropic()
        self.model = model

    async def extract_spacing_from_image_url(
        self,
        image_url: str,
        max_spacing: int = 12
    ) -> SpacingExtractionResult:
        """Extract spacing from image URL"""
        pass

    async def extract_spacing_from_base64(
        self,
        image_data: str,
        media_type: str,
        max_spacing: int = 12
    ) -> SpacingExtractionResult:
        """Extract spacing from base64 encoded image"""
        pass

    def _build_extraction_prompt(self, max_spacing: int) -> str:
        """Build the spacing extraction prompt"""
        return f"""Analyze this UI/design image and extract up to {max_spacing} distinct spacing values.

For each spacing value, provide:
1. **value**: The pixel measurement (integer)
2. **type**: One of: padding, margin, gap, inset, gutter
3. **context**: Where this spacing appears (e.g., "card padding", "button margin")
4. **design_intent**: Why this spacing is used (e.g., "breathing room", "tight grouping")

Focus on:
- Component internal padding
- Spacing between elements
- Grid gutters and gaps
- Vertical rhythm patterns
- Consistent spacing scales

Return measurements in pixels. Look for patterns based on 4px or 8px base units.

Format as JSON array with objects containing: value, type, context, design_intent"""

    async def _parse_spacing_response(
        self,
        response_text: str,
        max_spacing: int
    ) -> SpacingExtractionResult:
        """Parse AI response and compute all properties"""
        # Parse JSON response
        # Compute additional properties using spacing_utils
        # Generate semantic names
        # Return SpacingExtractionResult
        pass
```

### 3.2 Spacing Utilities

**File:** `src/copy_that/application/spacing_utils.py`

```python
def compute_all_spacing_properties(
    value_px: int,
    spacing_type: str,
    context: str
) -> tuple[dict, dict]:
    """
    Compute all derived properties for a spacing value.

    Returns:
        (properties_dict, extraction_metadata_dict)
    """
    properties = {
        # Unit conversions
        'value_rem': px_to_rem(value_px),
        'value_em': px_to_em(value_px),

        # Scale detection
        'scale': detect_scale_position(value_px),
        'base_unit': detect_base_unit(value_px),
        'multiplier': calculate_multiplier(value_px),

        # Grid compliance
        'is_grid_compliant': check_grid_compliance(value_px),

        # Responsive suggestions
        'responsive_scales': suggest_responsive_scales(value_px, spacing_type),
    }

    metadata = {
        'computation_version': '1.0',
        'algorithms_used': ['unit_conversion', 'scale_detection', 'grid_analysis'],
        'computation_timestamp': datetime.utcnow().isoformat(),
    }

    return properties, metadata


def px_to_rem(px: int, base: int = 16) -> float:
    """Convert pixels to rem units"""
    return round(px / base, 3)


def px_to_em(px: int, base: int = 16) -> float:
    """Convert pixels to em units"""
    return round(px / base, 3)


def detect_scale_position(value_px: int) -> str:
    """
    Detect position in standard spacing scale.

    Common scales:
    - 4px system: 4, 8, 12, 16, 20, 24, 32, 40, 48, 64
    - 8px system: 8, 16, 24, 32, 40, 48, 64, 80, 96
    """
    scale_4px = {
        0: 'none', 4: '2xs', 8: 'xs', 12: 'sm',
        16: 'md', 20: 'md', 24: 'lg', 32: 'xl',
        40: 'xl', 48: '2xl', 64: '3xl'
    }

    # Find closest match
    closest = min(scale_4px.keys(), key=lambda x: abs(x - value_px))
    return scale_4px.get(closest, 'custom')


def detect_base_unit(value_px: int) -> int:
    """Detect if spacing follows 4px or 8px base unit"""
    if value_px % 8 == 0:
        return 8
    elif value_px % 4 == 0:
        return 4
    else:
        return 1  # Non-standard


def calculate_multiplier(value_px: int) -> float:
    """Calculate multiplier based on detected base unit"""
    base = detect_base_unit(value_px)
    return value_px / base if base > 0 else value_px


def check_grid_compliance(value_px: int) -> bool:
    """Check if value fits common grid systems (4px, 8px, 12-column)"""
    return value_px % 4 == 0 or value_px % 8 == 0


def suggest_responsive_scales(value_px: int, spacing_type: str) -> dict:
    """
    Suggest responsive adjustments for different breakpoints.

    Strategy:
    - Mobile: Keep or reduce slightly
    - Tablet: Keep original
    - Desktop: Keep or increase slightly
    """
    return {
        'mobile': int(value_px * 0.75),
        'tablet': value_px,
        'desktop': int(value_px * 1.25),
        'widescreen': int(value_px * 1.5)
    }


def analyze_rhythm_consistency(spacing_values: list[int]) -> str:
    """
    Analyze if spacing values follow consistent rhythm.

    Returns: 'consistent', 'irregular', or 'mixed'
    """
    if not spacing_values:
        return 'unknown'

    # Check if all values share common base
    base_4 = all(v % 4 == 0 for v in spacing_values)
    base_8 = all(v % 8 == 0 for v in spacing_values)

    if base_8:
        return 'consistent'  # Strict 8px system
    elif base_4:
        return 'consistent'  # 4px system
    else:
        return 'irregular'
```

### 3.3 Semantic Spacing Naming

**File:** `src/copy_that/application/semantic_spacing_naming.py`

```python
class SemanticSpacingNamer:
    """Generate semantic names for spacing values"""

    def analyze_spacing(
        self,
        value_px: int,
        spacing_type: str,
        context: str
    ) -> dict:
        """
        Generate multiple naming schemes for spacing.

        Returns:
            {
                'simple': 'md',
                'descriptive': 'medium-padding',
                'contextual': 'card-padding',
                'scale_position': 'spacing-4',
                'semantic': 'comfortable-breathing-room'
            }
        """
        scale = detect_scale_position(value_px)

        return {
            'simple': scale,
            'descriptive': f"{scale}-{spacing_type}",
            'contextual': self._generate_contextual_name(context, spacing_type),
            'scale_position': f"spacing-{value_px // 4}",
            'semantic': self._generate_semantic_name(value_px, spacing_type)
        }

    def _generate_contextual_name(self, context: str, spacing_type: str) -> str:
        """Generate name based on context"""
        # Simplify context to kebab-case
        simplified = context.lower().replace(' ', '-')
        return f"{simplified}-{spacing_type}"

    def _generate_semantic_name(self, value_px: int, spacing_type: str) -> str:
        """Generate semantic name based on perceived spacing"""
        if value_px <= 4:
            feel = "tight"
        elif value_px <= 8:
            feel = "compact"
        elif value_px <= 16:
            feel = "comfortable"
        elif value_px <= 24:
            feel = "relaxed"
        elif value_px <= 32:
            feel = "spacious"
        else:
            feel = "generous"

        return f"{feel}-{spacing_type}"
```

### 3.4 Spacing Aggregator

**File:** `core/tokens/aggregate.py` (spacing merge lives in token graph; legacy path removed)

```python
from dataclasses import dataclass, field

@dataclass
class AggregatedSpacingToken:
    """Spacing token with provenance tracking"""

    value_px: int
    value_rem: float
    scale: str
    spacing_type: str
    name: str

    # Provenance
    source_images: list[str] = field(default_factory=list)
    confidence_scores: list[float] = field(default_factory=list)

    @property
    def average_confidence(self) -> float:
        if not self.confidence_scores:
            return 0.0
        return sum(self.confidence_scores) / len(self.confidence_scores)

    @property
    def occurrence_count(self) -> int:
        return len(self.source_images)

    def add_provenance(self, image_id: str, confidence: float):
        """Track which image contributed this spacing"""
        self.source_images.append(image_id)
        self.confidence_scores.append(confidence)

    def merge_provenance(self, other: 'AggregatedSpacingToken'):
        """Merge provenance from another token"""
        self.source_images.extend(other.source_images)
        self.confidence_scores.extend(other.confidence_scores)


@dataclass
class SpacingTokenLibrary:
    """Aggregated spacing token set with statistics"""

    tokens: list[AggregatedSpacingToken]
    statistics: dict
    token_type: str = "spacing"

    def to_dict(self) -> dict:
        return {
            'token_type': self.token_type,
            'token_count': len(self.tokens),
            'tokens': [vars(t) for t in self.tokens],
            'statistics': self.statistics
        }


class SpacingAggregator:
    """
    Aggregate and deduplicate spacing tokens from multiple images.

    Uses percentage-based threshold for deduplication:
    - Default 10% threshold: 16px and 17px are considered same
    - Configurable for stricter/looser matching
    """

    DEFAULT_PERCENTAGE_THRESHOLD = 0.10  # 10% difference allowed

    @staticmethod
    def aggregate_batch(
        spacing_batch: list[list[dict]],
        percentage_threshold: float = DEFAULT_PERCENTAGE_THRESHOLD
    ) -> SpacingTokenLibrary:
        """
        Aggregate spacing tokens from multiple images.

        Args:
            spacing_batch: List of spacing lists (one per image)
            percentage_threshold: Max % difference for deduplication

        Returns:
            SpacingTokenLibrary with deduplicated tokens
        """
        aggregated_tokens: list[AggregatedSpacingToken] = []

        for image_idx, spacing_list in enumerate(spacing_batch):
            image_id = f"image_{image_idx}"

            for spacing in spacing_list:
                value_px = spacing['value_px']

                # Find matching token
                matching_token = SpacingAggregator._find_matching_token(
                    value_px,
                    aggregated_tokens,
                    percentage_threshold
                )

                if matching_token:
                    # Update existing token
                    matching_token.add_provenance(
                        image_id,
                        spacing.get('confidence', 0.5)
                    )
                else:
                    # Create new token
                    new_token = AggregatedSpacingToken(
                        value_px=value_px,
                        value_rem=spacing.get('value_rem', value_px / 16),
                        scale=spacing.get('scale', 'custom'),
                        spacing_type=spacing.get('spacing_type', 'mixed'),
                        name=spacing.get('name', f'spacing-{value_px}')
                    )
                    new_token.add_provenance(
                        image_id,
                        spacing.get('confidence', 0.5)
                    )
                    aggregated_tokens.append(new_token)

        # Sort by value
        aggregated_tokens.sort(key=lambda t: t.value_px)

        # Generate statistics
        statistics = SpacingAggregator._generate_statistics(
            aggregated_tokens,
            len(spacing_batch)
        )

        return SpacingTokenLibrary(
            tokens=aggregated_tokens,
            statistics=statistics
        )

    @staticmethod
    def _find_matching_token(
        value_px: int,
        existing_tokens: list[AggregatedSpacingToken],
        threshold: float
    ) -> AggregatedSpacingToken | None:
        """Find token within percentage threshold"""
        for token in existing_tokens:
            if token.value_px == 0 or value_px == 0:
                if token.value_px == value_px:
                    return token
            else:
                diff_percent = abs(token.value_px - value_px) / max(token.value_px, value_px)
                if diff_percent <= threshold:
                    return token
        return None

    @staticmethod
    def _generate_statistics(
        tokens: list[AggregatedSpacingToken],
        image_count: int
    ) -> dict:
        """Generate aggregation statistics"""
        if not tokens:
            return {'token_count': 0}

        values = [t.value_px for t in tokens]

        return {
            'token_count': len(tokens),
            'image_count': image_count,
            'min_spacing': min(values),
            'max_spacing': max(values),
            'avg_spacing': sum(values) / len(values),
            'base_unit_detected': detect_base_unit(values[0]) if values else 4,
            'rhythm_consistency': analyze_rhythm_consistency(values),
            'grid_compliant_ratio': sum(1 for t in tokens if t.value_px % 4 == 0) / len(tokens),
            'average_confidence': sum(t.average_confidence for t in tokens) / len(tokens)
        }
```

---

## 4. Async/Parallel/Streaming Patterns

### 4.1 Batch Processing with Semaphore

```python
class BatchSpacingExtractor:
    """Orchestrate parallel spacing extraction from multiple images"""

    def __init__(self, max_concurrent: int = 5):
        self.extractor = AISpacingExtractor()
        self.max_concurrent = max_concurrent

    async def extract_batch(
        self,
        image_urls: list[str],
        max_spacing: int = 12,
        percentage_threshold: float = 0.10
    ) -> tuple[SpacingTokenLibrary, dict]:
        """
        Extract spacing from multiple images in parallel.

        Returns:
            (aggregated_library, extraction_metadata)
        """
        # Extract all images in parallel with semaphore control
        all_spacing = await self._extract_all_images(image_urls, max_spacing)

        # Aggregate results
        library = SpacingAggregator.aggregate_batch(
            all_spacing,
            percentage_threshold
        )

        metadata = {
            'image_count': len(image_urls),
            'extraction_timestamp': datetime.utcnow().isoformat(),
            'threshold_used': percentage_threshold
        }

        return library, metadata

    async def _extract_all_images(
        self,
        image_urls: list[str],
        max_spacing: int
    ) -> list[list[dict]]:
        """Extract from all images with concurrency control"""

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def extract_with_limit(url: str, index: int):
            async with semaphore:
                result = await self._extract_single_image(url, max_spacing, index)
                return index, result

        # Extract all images concurrently
        tasks = [
            extract_with_limit(url, i)
            for i, url in enumerate(image_urls)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Sort by original index and handle errors
        valid_results = []
        for result in sorted(results, key=lambda x: x[0] if isinstance(x, tuple) else float('inf')):
            if isinstance(result, tuple):
                valid_results.append(result[1])
            else:
                logger.warning(f"Extraction failed: {result}")
                valid_results.append([])  # Empty list for failed extraction

        return valid_results

    async def _extract_single_image(
        self,
        url: str,
        max_spacing: int,
        index: int
    ) -> list[dict]:
        """Extract spacing from a single image"""
        try:
            result = await self.extractor.extract_spacing_from_image_url(
                url,
                max_spacing
            )
            return result.spacing_tokens
        except Exception as e:
            logger.error(f"Failed to extract from image {index}: {e}")
            return []
```

### 4.2 SSE Streaming Endpoint

```python
@router.post("/spacing/extract-streaming")
async def extract_spacing_streaming(
    request: SpacingExtractionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Extract spacing tokens with Server-Sent Events streaming.

    Phases:
    1. Fast extraction (stream as tokens are found)
    2. Property computation (progress updates)
    3. Aggregation (final results)
    """

    async def spacing_extraction_stream():
        try:
            extractor = AISpacingExtractor()

            # Phase 1: Initial extraction
            yield f"data: {json.dumps({
                'phase': 1,
                'status': 'starting',
                'message': 'Beginning spacing extraction...'
            })}\n\n"

            # Extract spacing
            result = await extractor.extract_spacing_from_base64(
                request.image_data,
                request.media_type,
                request.max_spacing
            )

            # Stream each token as it's processed
            for idx, token in enumerate(result.spacing_tokens):
                yield f"data: {json.dumps({
                    'phase': 1,
                    'status': 'token_extracted',
                    'progress': (idx + 1) / len(result.spacing_tokens),
                    'token': token
                })}\n\n"
                await asyncio.sleep(0.05)  # Small delay for UI updates

            # Phase 2: Property computation
            yield f"data: {json.dumps({
                'phase': 2,
                'status': 'computing_properties',
                'message': 'Computing derived properties...'
            })}\n\n"

            # Compute additional properties
            enriched_tokens = []
            for token in result.spacing_tokens:
                props, metadata = compute_all_spacing_properties(
                    token['value_px'],
                    token['spacing_type'],
                    token.get('context', '')
                )
                enriched_token = {**token, **props, 'extraction_metadata': metadata}
                enriched_tokens.append(enriched_token)

            # Phase 3: Complete
            yield f"data: {json.dumps({
                'phase': 3,
                'status': 'extraction_complete',
                'tokens': enriched_tokens,
                'statistics': {
                    'token_count': len(enriched_tokens),
                    'base_unit': detect_base_unit(enriched_tokens[0]['value_px']) if enriched_tokens else 4
                }
            })}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({
                'phase': -1,
                'status': 'error',
                'message': str(e)
            })}\n\n"

    return StreamingResponse(
        spacing_extraction_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
```

---

## 5. API Endpoints

### 5.1 Router Definition

**File:** `src/copy_that/interfaces/api/spacing.py`

```python
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/v1", tags=["spacing"])

# Endpoints to implement:

@router.post("/spacing/extract")
async def extract_spacing(
    request: SpacingExtractionRequest,
    db: AsyncSession = Depends(get_db)
) -> SpacingExtractionResponse:
    """Extract spacing from single image"""
    pass

@router.post("/spacing/extract-streaming")
async def extract_spacing_streaming(
    request: SpacingExtractionRequest,
    db: AsyncSession = Depends(get_db)
) -> StreamingResponse:
    """Extract with SSE streaming"""
    pass

@router.post("/spacing/extract-batch")
async def extract_spacing_batch(
    request: BatchSpacingRequest,
    db: AsyncSession = Depends(get_db)
) -> BatchSpacingResponse:
    """Extract from multiple images with aggregation"""
    pass

@router.get("/projects/{project_id}/spacing")
async def get_project_spacing(
    project_id: int,
    db: AsyncSession = Depends(get_db)
) -> list[SpacingTokenDetailResponse]:
    """Get all spacing tokens for a project"""
    pass

@router.get("/spacing/{spacing_id}")
async def get_spacing_token(
    spacing_id: int,
    db: AsyncSession = Depends(get_db)
) -> SpacingTokenDetailResponse:
    """Get single spacing token details"""
    pass

@router.post("/sessions/{session_id}/spacing/export")
async def export_spacing(
    session_id: int,
    format: ExportFormat,
    db: AsyncSession = Depends(get_db)
) -> ExportResponse:
    """Export spacing tokens in specified format"""
    pass
```

### 5.2 Request/Response Schemas

```python
from pydantic import BaseModel
from enum import Enum

class SpacingExtractionRequest(BaseModel):
    image_data: str  # Base64 encoded
    media_type: str  # image/png, image/jpeg
    max_spacing: int = 12
    project_id: int | None = None

class BatchSpacingRequest(BaseModel):
    image_urls: list[str]
    max_spacing: int = 12
    percentage_threshold: float = 0.10
    project_id: int | None = None

class SpacingExtractionResponse(BaseModel):
    job_id: int
    tokens: list[SpacingTokenResponse]
    statistics: dict

class SpacingTokenResponse(BaseModel):
    id: int
    value_px: int
    value_rem: float
    scale: str
    name: str
    spacing_type: str
    confidence: float

class SpacingTokenDetailResponse(SpacingTokenResponse):
    value_em: float
    base_unit: int
    multiplier: float
    design_intent: str
    use_case: str
    context: str
    is_grid_compliant: bool
    rhythm_consistency: str
    responsive_scales: dict | None
    semantic_names: dict | None
    extraction_metadata: dict | None

class ExportFormat(str, Enum):
    W3C = "w3c"
    CSS = "css"
    REACT = "react"
    TAILWIND = "tailwind"
    SCSS = "scss"
```

---

## 6. Export Generators

### 6.1 W3C Design Tokens Generator

```python
class SpacingW3CGenerator(BaseGenerator):
    """Generate W3C Design Tokens format for spacing"""

    def generate(self) -> str:
        tokens = {}

        for token in self.library.tokens:
            token_name = token.name.replace('-', '_')
            tokens[token_name] = {
                "$type": "dimension",
                "$value": f"{token.value_px}px",
                "$description": f"{token.spacing_type} spacing - {token.scale}",
                "$extensions": {
                    "copy-that": {
                        "value_rem": token.value_rem,
                        "scale": token.scale,
                        "confidence": token.average_confidence,
                        "source_count": token.occurrence_count
                    }
                }
            }

        return json.dumps({"spacing": tokens}, indent=2)
```

### 6.2 CSS Generator

```python
class SpacingCSSGenerator(BaseGenerator):
    """Generate CSS custom properties for spacing"""

    def generate(self) -> str:
        lines = [":root {"]

        for token in self.library.tokens:
            css_name = token.name.replace('_', '-')
            lines.append(f"  --spacing-{css_name}: {token.value_px}px;")
            lines.append(f"  --spacing-{css_name}-rem: {token.value_rem}rem;")

        lines.append("}")
        return "\n".join(lines)
```

### 6.3 React/TypeScript Generator

```python
class SpacingReactGenerator(BaseGenerator):
    """Generate React/TypeScript spacing theme"""

    def generate(self) -> str:
        spacing_dict = {}

        for token in self.library.tokens:
            key = token.scale if token.scale != 'custom' else token.name
            spacing_dict[key] = token.value_px

        return f"""export const spacing = {json.dumps(spacing_dict, indent=2)} as const;

export type SpacingScale = keyof typeof spacing;

export const spacingRem = {{
{self._generate_rem_entries()}
}} as const;
"""

    def _generate_rem_entries(self) -> str:
        entries = []
        for token in self.library.tokens:
            key = token.scale if token.scale != 'custom' else token.name
            entries.append(f"  {key}: '{token.value_rem}rem'")
        return ",\n".join(entries)
```

---

## 7. Database Migration

### 7.1 Alembic Migration Script

```python
"""Add spacing_tokens table

Revision ID: xxxx
Revises: yyyy
Create Date: 2025-11-22
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.create_table(
        'spacing_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('library_id', sa.Integer(), nullable=True),
        sa.Column('extraction_job_id', sa.Integer(), nullable=True),

        # Core values
        sa.Column('value_px', sa.Integer(), nullable=False),
        sa.Column('value_rem', sa.Float(), nullable=False),
        sa.Column('value_em', sa.Float(), nullable=False),

        # Scale information
        sa.Column('scale', sa.String(20), nullable=False),
        sa.Column('base_unit', sa.Integer(), default=4),
        sa.Column('multiplier', sa.Float(), nullable=False),

        # Semantic information
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('spacing_type', sa.String(50), nullable=False),
        sa.Column('design_intent', sa.String(500)),

        # Context
        sa.Column('use_case', sa.String(500)),
        sa.Column('context', sa.String(500)),

        # Analysis
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('is_grid_compliant', sa.Boolean(), default=True),
        sa.Column('rhythm_consistency', sa.String(50)),

        # JSON fields
        sa.Column('responsive_scales', postgresql.JSONB()),
        sa.Column('semantic_names', postgresql.JSONB()),
        sa.Column('related_to', postgresql.JSONB()),
        sa.Column('component_usage', postgresql.JSONB()),
        sa.Column('extraction_metadata', postgresql.JSONB()),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now()),

        # Primary key
        sa.PrimaryKeyConstraint('id')
    )

    # Foreign keys
    op.create_foreign_key(
        'fk_spacing_tokens_project',
        'spacing_tokens', 'projects',
        ['project_id'], ['id']
    )
    op.create_foreign_key(
        'fk_spacing_tokens_library',
        'spacing_tokens', 'token_libraries',
        ['library_id'], ['id']
    )
    op.create_foreign_key(
        'fk_spacing_tokens_job',
        'spacing_tokens', 'extraction_jobs',
        ['extraction_job_id'], ['id']
    )

    # Indexes
    op.create_index('ix_spacing_tokens_project_id', 'spacing_tokens', ['project_id'])
    op.create_index('ix_spacing_tokens_library_id', 'spacing_tokens', ['library_id'])
    op.create_index('ix_spacing_tokens_value_px', 'spacing_tokens', ['value_px'])
    op.create_index('ix_spacing_tokens_scale', 'spacing_tokens', ['scale'])

def downgrade():
    op.drop_table('spacing_tokens')
```

---

## 8. Testing Strategy

### 8.1 Unit Tests

```python
class TestSpacingExtractor:
    @pytest.fixture
    def extractor(self):
        return AISpacingExtractor()

    @pytest.fixture
    def sample_image(self):
        return load_test_image("ui_spacing_sample.png")

    async def test_extract_spacing_from_image(self, extractor, sample_image):
        """Test basic spacing extraction"""
        result = await extractor.extract_spacing_from_base64(
            sample_image, "image/png", max_spacing=8
        )

        assert len(result.spacing_tokens) > 0
        assert len(result.spacing_tokens) <= 8

    async def test_spacing_has_required_fields(self, extractor, sample_image):
        """Test all tokens have required fields"""
        result = await extractor.extract_spacing_from_base64(
            sample_image, "image/png"
        )

        for token in result.spacing_tokens:
            assert 'value_px' in token
            assert 'confidence' in token
            assert 'spacing_type' in token
            assert 0 <= token['confidence'] <= 1


class TestSpacingUtils:
    def test_px_to_rem_conversion(self):
        assert px_to_rem(16) == 1.0
        assert px_to_rem(24) == 1.5
        assert px_to_rem(8) == 0.5

    def test_detect_scale_position(self):
        assert detect_scale_position(8) == 'xs'
        assert detect_scale_position(16) == 'md'
        assert detect_scale_position(32) == 'xl'

    def test_detect_base_unit(self):
        assert detect_base_unit(16) == 8  # Divisible by 8
        assert detect_base_unit(12) == 4  # Only divisible by 4
        assert detect_base_unit(15) == 1  # Non-standard

    def test_grid_compliance(self):
        assert check_grid_compliance(16) == True
        assert check_grid_compliance(8) == True
        assert check_grid_compliance(15) == False


class TestSpacingAggregator:
    def test_aggregate_batch_deduplication(self):
        """Test that similar values are deduplicated"""
        batch = [
            [{'value_px': 16, 'confidence': 0.9, 'spacing_type': 'padding'}],
            [{'value_px': 17, 'confidence': 0.85, 'spacing_type': 'padding'}],  # Within 10%
        ]

        library = SpacingAggregator.aggregate_batch(batch, 0.10)

        # Should be deduplicated to one token
        assert len(library.tokens) == 1
        assert library.tokens[0].occurrence_count == 2

    def test_aggregate_batch_preserves_distinct(self):
        """Test that distinct values are preserved"""
        batch = [
            [{'value_px': 8, 'confidence': 0.9, 'spacing_type': 'padding'}],
            [{'value_px': 24, 'confidence': 0.9, 'spacing_type': 'margin'}],
        ]

        library = SpacingAggregator.aggregate_batch(batch)

        # Should have both tokens
        assert len(library.tokens) == 2
```

### 8.2 Integration Tests

```python
class TestSpacingPipeline:
    async def test_full_extraction_pipeline(self, client, test_db):
        """Test complete extraction → storage → retrieval"""
        # Upload image and extract
        response = await client.post(
            "/api/v1/spacing/extract",
            json={
                "image_data": base64_encode(load_test_image()),
                "media_type": "image/png",
                "max_spacing": 8,
                "project_id": 1
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "tokens" in data
        assert len(data["tokens"]) > 0

        # Verify storage
        tokens = await test_db.execute(
            select(SpacingToken).where(SpacingToken.project_id == 1)
        )
        assert len(tokens.scalars().all()) > 0

    async def test_streaming_extraction(self, client):
        """Test SSE streaming endpoint"""
        async with client.stream(
            "POST",
            "/api/v1/spacing/extract-streaming",
            json={
                "image_data": base64_encode(load_test_image()),
                "media_type": "image/png"
            }
        ) as response:
            events = []
            async for line in response.aiter_lines():
                if line.startswith("data:"):
                    events.append(json.loads(line[5:]))

            # Should have all phases
            phases = [e['phase'] for e in events]
            assert 1 in phases
            assert 2 in phases
            assert 3 in phases
```

---

## 9. Frontend Integration

### 9.1 Token Store Extension

```typescript
// frontend/src/store/tokenStore.ts

interface SpacingToken {
  id: number;
  value_px: number;
  value_rem: number;
  scale: string;
  name: string;
  spacing_type: string;
  confidence: number;
  // ... other fields
}

interface TokenStore {
  // Existing color tokens
  colorTokens: ColorToken[];

  // New spacing tokens
  spacingTokens: SpacingToken[];

  // Actions
  setSpacingTokens: (tokens: SpacingToken[]) => void;
  addSpacingToken: (token: SpacingToken) => void;

  // Streaming support
  isExtractingSpacing: boolean;
  spacingExtractionProgress: number;
}
```

### 9.2 Token Type Registry Extension

```typescript
// frontend/src/config/tokenTypeRegistry.tsx

export const tokenTypeRegistry: Record<string, TokenTypeSchema> = {
  color: {
    // ... existing color config
  },

  spacing: {
    name: 'Spacing',
    icon: SpacingIcon,
    primaryVisual: SpacingVisual,
    formatTabs: [
      { id: 'preview', label: 'Preview', component: SpacingPreview },
      { id: 'scale', label: 'Scale', component: SpacingScale },
      { id: 'responsive', label: 'Responsive', component: ResponsiveSpacing }
    ],
    playgroundTabs: [
      { id: 'component', label: 'Component', component: SpacingPlayground }
    ],
    filters: [
      { id: 'type', label: 'Type', options: ['padding', 'margin', 'gap'] },
      { id: 'scale', label: 'Scale', options: ['xs', 'sm', 'md', 'lg', 'xl'] }
    ]
  }
};
```

---

## 10. Implementation Checklist

### Phase 1: Foundation
- [ ] (Done) Use token graph utilities; legacy `copy_that/tokens/spacing` removed
- [ ] Define SpacingToken Pydantic model
- [ ] Define SpacingToken SQLAlchemy model
- [ ] Create Alembic migration
- [ ] Implement spacing_utils.py with core functions

### Phase 2: Extraction
- [ ] Implement AISpacingExtractor class
- [ ] Implement OpenAISpacingExtractor class (alternative)
- [ ] Create semantic_spacing_naming.py
- [ ] Create extractor factory function
- [ ] Write unit tests for extractors

### Phase 3: Aggregation
- [ ] Implement SpacingAggregator class
- [ ] Implement AggregatedSpacingToken dataclass
- [ ] Implement SpacingTokenLibrary dataclass
- [ ] Write unit tests for aggregation

### Phase 4: Batch Processing
- [ ] Implement BatchSpacingExtractor with semaphore
- [ ] Add persistence methods
- [ ] Write integration tests

### Phase 5: API
- [ ] Create spacing router
- [ ] Implement single extraction endpoint
- [ ] Implement streaming endpoint
- [ ] Implement batch endpoint
- [ ] Implement query endpoints
- [ ] Write API integration tests

### Phase 6: Export
- [ ] Implement SpacingW3CGenerator
- [ ] Implement SpacingCSSGenerator
- [ ] Implement SpacingReactGenerator
- [ ] Implement SpacingTailwindGenerator
- [ ] Write generator tests

### Phase 7: Frontend
- [ ] Extend token store with spacing
- [ ] Add spacing to token type registry
- [ ] Create SpacingVisual component
- [ ] Create SpacingPreview component
- [ ] Wire up API calls

### Phase 8: Documentation
- [ ] Update API documentation
- [ ] Update architecture diagrams
- [ ] Add spacing examples to docs/examples/

---

## 11. Performance Considerations

### 11.1 Extraction Optimization
- Use semaphore to limit concurrent API calls (default: 5)
- Cache extracted tokens by image hash
- Use streaming for real-time progress updates

### 11.2 Database Optimization
- Index on project_id, library_id, value_px, scale
- Use JSONB for flexible metadata fields
- Batch inserts for multiple tokens

### 11.3 Aggregation Optimization
- O(n*m) worst case for deduplication
- Consider spatial indexing for large batches
- Use percentage threshold instead of absolute difference

---

## 12. Related Documentation

- **[PLUGIN_ARCHITECTURE.md](../architecture/PLUGIN_ARCHITECTURE.md)** - Plugin system overview
- **[EXTRACTOR_PATTERNS.md](../architecture/EXTRACTOR_PATTERNS.md)** - Extractor best practices
- **[TOKEN_SYSTEM.md](../domain/TOKEN_SYSTEM.md)** - Token types and structure
- **[TOKEN_FACTORY_PLANNING.md](./TOKEN_FACTORY_PLANNING.md)** - Reusable token factory

---

**Version:** 1.0 | **Last Updated:** 2025-11-22 | **Status:** Planning Document

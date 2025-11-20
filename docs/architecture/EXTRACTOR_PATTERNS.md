# Extractor Patterns & Best Practices

**Version:** 1.0 | **Date:** 2025-11-19 | **Status:** Guide

This document describes the architecture patterns for building token extractors in Copy That.

---

## 🎯 What Are Extractors?

Extractors are **modular plugins** that analyze images and extract specific types of design tokens:

```
Image Upload
    ↓
ColorExtractor   → Extract colors
SpacingExtractor → Extract spacing
TypographyExtractor → Extract typography
    ↓
Tokens → Database → Frontend
```

**Key principle:** Each extractor is **independent** and can be used in any combination.

---

## 🏗️ Extractor Architecture

### Base Interface

All extractors implement a common interface:

```python
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

class BaseTokenExtractor(ABC):
    """Base class for all token extractors"""

    @abstractmethod
    def extract(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        """
        Extract tokens from image bytes

        Args:
            image_bytes: Raw image data

        Returns:
            List of extracted token dictionaries
        """
        pass

    @abstractmethod
    def validate(self, tokens: List[Dict[str, Any]]) -> bool:
        """Validate extracted tokens"""
        pass

    def extract_with_pipeline(
        self,
        image_bytes: bytes,
        preprocess: Optional[callable] = None,
        postprocess: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """Run extraction with preprocessing and postprocessing"""
        # Optional: preprocess image
        if preprocess:
            image_bytes = preprocess(image_bytes)

        # Core extraction
        tokens = self.extract(image_bytes)

        # Optional: postprocess results
        if postprocess:
            tokens = postprocess(tokens)

        return tokens
```

### Extractor Lifecycle

```
1. INIT
   └─ Load model, initialize resources

2. VALIDATE INPUT
   └─ Check image format, size, etc.

3. PREPROCESS
   └─ Resize, enhance contrast, etc.

4. EXTRACT
   └─ Run analysis and extract tokens

5. POSTPROCESS
   └─ Filter, merge, enrich

6. VALIDATE OUTPUT
   └─ Check quality, confidence

7. RETURN
   └─ List of token dictionaries
```

---

## 🎨 Example: ColorExtractor

### Basic Implementation

```python
from copy_that.infrastructure.extractors.base import BaseTokenExtractor
import numpy as np
from sklearn.cluster import KMeans

class ColorExtractor(BaseTokenExtractor):
    """Extract color palette from image using K-means clustering"""

    def __init__(self, num_colors: int = 12):
        self.num_colors = num_colors

    def extract(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        """
        Extract dominant colors using K-means clustering

        Process:
        1. Load image from bytes
        2. Convert to RGB if needed
        3. Reshape to pixels array
        4. Run K-means clustering
        5. Extract cluster centers (colors)
        6. Sort by frequency
        """
        import cv2
        from io import BytesIO
        from PIL import Image

        # Load image
        image = Image.open(BytesIO(image_bytes))
        image_array = np.array(image.convert('RGB'))

        # Reshape for clustering
        pixels = image_array.reshape(-1, 3)

        # K-means clustering
        kmeans = KMeans(n_clusters=self.num_colors, random_state=42)
        kmeans.fit(pixels)

        # Extract colors (cluster centers)
        colors = kmeans.cluster_centers_.astype(int)

        # Convert to hex and add confidence
        tokens = []
        for idx, color in enumerate(colors):
            # Calculate confidence as cluster size ratio
            cluster_size = np.sum(kmeans.labels_ == idx)
            confidence = cluster_size / len(kmeans.labels_)

            tokens.append({
                'hex': self._rgb_to_hex(color),
                'confidence': float(confidence),
                'token_type': 'color',
                'r': int(color[0]),
                'g': int(color[1]),
                'b': int(color[2])
            })

        # Sort by confidence (most frequent first)
        tokens.sort(key=lambda t: t['confidence'], reverse=True)

        return tokens

    def validate(self, tokens: List[Dict[str, Any]]) -> bool:
        """Validate extracted colors"""
        if not tokens:
            return False

        for token in tokens:
            # Check required fields
            if 'hex' not in token or 'confidence' not in token:
                return False

            # Check hex format
            if not isinstance(token['hex'], str) or not token['hex'].startswith('#'):
                return False

            # Check confidence in range
            if not (0 <= token['confidence'] <= 1):
                return False

        return True

    @staticmethod
    def _rgb_to_hex(rgb: np.ndarray) -> str:
        """Convert RGB tuple to hex string"""
        return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))
```

### Usage

```python
# Create extractor
extractor = ColorExtractor(num_colors=12)

# Load image
with open('design.png', 'rb') as f:
    image_bytes = f.read()

# Extract colors
colors = extractor.extract(image_bytes)

# Validate
if extractor.validate(colors):
    print(f"Extracted {len(colors)} colors")
    for color in colors:
        print(f"  {color['hex']} - {color['confidence']:.1%} confidence")
```

---

## 🔄 Multi-Extractor Orchestration

### Running Multiple Extractors

When you want to extract multiple token types from one image:

```python
from copy_that.infrastructure.extractors.color import ColorExtractor
from copy_that.infrastructure.extractors.spacing import SpacingExtractor
from copy_that.infrastructure.extractors.typography import TypographyExtractor

async def extract_all_tokens(image_bytes: bytes) -> Dict[str, List]:
    """Extract all token types from image"""

    # Run extractors in parallel
    color_extractor = ColorExtractor()
    spacing_extractor = SpacingExtractor()
    typography_extractor = TypographyExtractor()

    # Could be run in parallel with asyncio
    colors = await asyncio.to_thread(color_extractor.extract, image_bytes)
    spacing = await asyncio.to_thread(spacing_extractor.extract, image_bytes)
    typography = await asyncio.to_thread(typography_extractor.extract, image_bytes)

    return {
        'colors': colors,
        'spacing': spacing,
        'typography': typography
    }
```

### Graceful Degradation

If one extractor fails, others continue:

```python
async def extract_all_tokens_safe(image_bytes: bytes) -> Dict[str, List]:
    """Extract tokens with error handling"""

    results = {}

    # Try each extractor, catch errors
    try:
        results['colors'] = await asyncio.to_thread(
            ColorExtractor().extract, image_bytes
        )
    except Exception as e:
        logger.warning(f"Color extraction failed: {e}")
        results['colors'] = []

    try:
        results['spacing'] = await asyncio.to_thread(
            SpacingExtractor().extract, image_bytes
        )
    except Exception as e:
        logger.warning(f"Spacing extraction failed: {e}")
        results['spacing'] = []

    try:
        results['typography'] = await asyncio.to_thread(
            TypographyExtractor().extract, image_bytes
        )
    except Exception as e:
        logger.warning(f"Typography extraction failed: {e}")
        results['typography'] = []

    return results
```

---

## 🤖 AI-Powered Extractors

### Using Claude Structured Outputs

For more sophisticated extraction using Claude's vision API:

```python
from anthropic import Anthropic
from pydantic import BaseModel

class ColorTokenResponse(BaseModel):
    colors: List[Dict[str, str]]
    confidence: float
    analysis: str

class AIColorExtractor(BaseTokenExtractor):
    """Extract colors using Claude Sonnet 4.5 vision"""

    def __init__(self):
        self.client = Anthropic()

    def extract(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        """Extract colors using Claude with Structured Outputs"""
        import base64

        # Encode image
        encoded = base64.standard_b64encode(image_bytes).decode('utf-8')

        # Call Claude with Structured Outputs
        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "color_extraction",
                    "schema": ColorTokenResponse.model_json_schema()
                }
            },
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": encoded
                            }
                        },
                        {
                            "type": "text",
                            "text": "Extract the primary colors from this design image. Return hex values."
                        }
                    ]
                }
            ]
        )

        # Parse response
        content = response.content[0].text
        result = ColorTokenResponse.model_validate_json(content)

        # Convert to token format
        tokens = []
        for color in result.colors:
            tokens.append({
                'hex': color['hex'],
                'name': color.get('name', ''),
                'confidence': result.confidence,
                'token_type': 'color'
            })

        return tokens

    def validate(self, tokens: List[Dict[str, Any]]) -> bool:
        """Validate tokens"""
        return all(
            'hex' in t and 'confidence' in t
            for t in tokens
        )
```

---

## 🎯 Best Practices

### 1. Confidence Scores

**Always include confidence scores:**

```python
# ✅ Good - includes confidence
{
    'hex': '#FF6B35',
    'confidence': 0.95,  # High confidence
    'token_type': 'color'
}

# ❌ Bad - no confidence information
{
    'hex': '#FF6B35',
    'token_type': 'color'
}
```

**Why:** Allows downstream systems to decide whether to trust the extraction.

### 2. Validation

**Always validate before returning:**

```python
def extract(self, image_bytes: bytes) -> List[Dict[str, Any]]:
    # Extract
    tokens = self._do_extraction(image_bytes)

    # Validate
    if not self.validate(tokens):
        logger.error("Validation failed")
        return []

    return tokens
```

### 3. Error Handling

**Handle failures gracefully:**

```python
def extract(self, image_bytes: bytes) -> List[Dict[str, Any]]:
    try:
        # Validate input
        if not self._is_valid_image(image_bytes):
            logger.warning("Invalid image format")
            return []

        # Extract
        tokens = self._do_extraction(image_bytes)
        return tokens

    except Exception as e:
        logger.error(f"Extraction failed: {e}", exc_info=True)
        return []  # Return empty list on failure
```

### 4. Type Hints

**Use comprehensive type hints:**

```python
def extract(self, image_bytes: bytes) -> List[Dict[str, Any]]:
    """Extract tokens from image bytes"""
    pass

def validate(self, tokens: List[Dict[str, Any]]) -> bool:
    """Validate extracted tokens"""
    pass

def extract_with_pipeline(
    self,
    image_bytes: bytes,
    preprocess: Optional[Callable[[bytes], bytes]] = None,
    postprocess: Optional[Callable[[List], List]] = None
) -> List[Dict[str, Any]]:
    """Run extraction with optional pre/post processing"""
    pass
```

### 5. Composition

**Combine extractors without coupling:**

```python
class MultiExtractor:
    """Combine multiple extractors"""

    def __init__(self, extractors: Dict[str, BaseTokenExtractor]):
        self.extractors = extractors

    async def extract_all(self, image_bytes: bytes) -> Dict[str, List]:
        """Run all extractors and combine results"""
        tasks = {
            name: asyncio.to_thread(ext.extract, image_bytes)
            for name, ext in self.extractors.items()
        }
        return await asyncio.gather(*tasks.values())
```

---

## 🧪 Testing Extractors

### Unit Test Example

```python
import pytest
from pathlib import Path

class TestColorExtractor:
    @pytest.fixture
    def extractor(self):
        return ColorExtractor()

    @pytest.fixture
    def sample_image(self):
        # Load test image
        path = Path(__file__).parent / "fixtures/test_image.png"
        return path.read_bytes()

    def test_extract_colors(self, extractor, sample_image):
        """Test color extraction"""
        colors = extractor.extract(sample_image)

        assert len(colors) > 0
        assert len(colors) <= 12

    def test_colors_have_confidence(self, extractor, sample_image):
        """Test all colors have confidence scores"""
        colors = extractor.extract(sample_image)

        for color in colors:
            assert 'confidence' in color
            assert 0 <= color['confidence'] <= 1

    def test_validate_colors(self, extractor):
        """Test validation"""
        valid_colors = [
            {'hex': '#FF0000', 'confidence': 0.95, 'token_type': 'color'}
        ]
        assert extractor.validate(valid_colors)

        invalid_colors = [
            {'hex': 'invalid', 'confidence': 0.95}
        ]
        assert not extractor.validate(invalid_colors)
```

---

## 📊 Extractor Registry

### Dynamic Extractor Discovery

```python
from typing import Dict, Type

class ExtractorRegistry:
    """Registry of available extractors"""

    _extractors: Dict[str, Type[BaseTokenExtractor]] = {}

    @classmethod
    def register(cls, name: str, extractor_class: Type[BaseTokenExtractor]):
        """Register an extractor"""
        cls._extractors[name] = extractor_class

    @classmethod
    def get(cls, name: str) -> BaseTokenExtractor:
        """Get an extractor by name"""
        if name not in cls._extractors:
            raise ValueError(f"Unknown extractor: {name}")
        return cls._extractors[name]()

    @classmethod
    def list_available(cls) -> List[str]:
        """List all available extractors"""
        return list(cls._extractors.keys())

# Register extractors
ExtractorRegistry.register('color', ColorExtractor)
ExtractorRegistry.register('spacing', SpacingExtractor)
ExtractorRegistry.register('typography', TypographyExtractor)

# Usage
extractor = ExtractorRegistry.get('color')
```

---

## 🔄 Extractor Lifecycle in API

When an extraction request comes in:

```python
@router.post("/api/v1/extract/{token_type}")
async def extract_tokens(
    token_type: str,
    file: UploadFile,
    db: AsyncSession = Depends(get_db)
):
    """
    Extract tokens of specified type

    Flow:
    1. Get extractor from registry
    2. Create extraction job
    3. Read uploaded image
    4. Run extraction
    5. Store results in database
    6. Return to frontend
    """

    # 1. Get extractor
    try:
        extractor = ExtractorRegistry.get(token_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Unknown token type")

    # 2. Create job
    job = ExtractionJob(
        extraction_type=token_type,
        status="processing"
    )
    db.add(job)
    await db.commit()

    try:
        # 3. Read image
        image_bytes = await file.read()

        # 4. Extract
        tokens = extractor.extract(image_bytes)

        # 5. Store in database
        for token in tokens:
            db_token = create_token_from_dict(token, job.id)
            db.add(db_token)

        # 6. Update job
        job.status = "completed"
        await db.commit()

        return {"job_id": job.id, "tokens": tokens}

    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)
        await db.commit()
        raise HTTPException(status_code=500, detail="Extraction failed")
```

---

## 📚 Related Documentation

- **TOKEN_SYSTEM.md** - Token types and structure
- **ADAPTER_PATTERN.md** - Schema transformation
- **PLUGIN_ARCHITECTURE.md** - Plugin system overview

---

**Version:** 1.0 | **Last Updated:** 2025-11-19 | **Status:** Complete

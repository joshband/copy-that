# Token Factory: Reusable Abstraction for Token Pipelines

**Version:** 1.0 | **Date:** 2025-11-22 | **Status:** Planning Document

This document provides a comprehensive implementation plan for a reusable token factory abstraction that enables rapid development of new token types (color, spacing, typography, shadow, etc.) with built-in support for parallel async processing, streaming, and consistent patterns.

---

## Executive Summary

The Token Factory is a **meta-framework** that provides:

1. **Abstract Base Classes** - Template for all token types
2. **Registry System** - Dynamic plugin registration and discovery
3. **Async Pipeline Orchestration** - Parallel extraction with semaphore control
4. **Streaming Infrastructure** - SSE streaming with progress callbacks
5. **Aggregation Framework** - Configurable deduplication strategies
6. **Generator System** - Multiple export format support
7. **Testing Templates** - Pre-built test scaffolding

Each new token type (spacing, typography, shadow) can be created by extending these base classes, ensuring 80%+ code reuse and consistent behavior.

---

## 1. Core Architecture

### 1.1 Factory Pattern Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    TOKEN FACTORY CORE                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Abstract   │  │   Registry   │  │   Pipeline   │      │
│  │    Bases     │  │   System     │  │ Orchestrator │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Streaming   │  │ Aggregation  │  │  Generator   │      │
│  │   Engine     │  │  Framework   │  │   System     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │  Color   │   │ Spacing  │   │ Typography│
        │  Plugin  │   │  Plugin  │   │  Plugin   │
        └──────────┘   └──────────┘   └──────────┘
```

### 1.2 Directory Structure

```
src/copy_that/
├── tokens/
│   ├── __init__.py
│   ├── factory/                     # Token Factory Core
│   │   ├── __init__.py
│   │   ├── base_token.py           # Abstract token model
│   │   ├── base_extractor.py       # Abstract extractor
│   │   ├── base_aggregator.py      # Abstract aggregator
│   │   ├── base_generator.py       # Abstract generator (exists)
│   │   ├── registry.py             # Plugin registry
│   │   ├── pipeline.py             # Pipeline orchestrator
│   │   ├── streaming.py            # Streaming engine
│   │   └── utils.py                # Shared utilities
│   │
│   ├── color/                       # Color token implementation
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── extractor.py
│   │   ├── aggregator.py
│   │   └── generators/
│   │
│   ├── spacing/                     # Spacing token implementation
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── extractor.py
│   │   ├── aggregator.py
│   │   └── generators/
│   │
│   └── typography/                  # Typography token implementation
│       └── ... (same structure)
```

---

## 2. Abstract Base Classes

### 2.1 BaseToken - Abstract Token Model

**File:** `src/copy_that/tokens/factory/base_token.py`

```python
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from typing import Any, ClassVar
from datetime import datetime

class BaseToken(BaseModel, ABC):
    """
    Abstract base class for all token types.

    Every token implementation must define:
    - token_type: Class variable identifying the token type
    - Core fields specific to the token type
    - Computed properties via compute_properties()
    """

    # Class variables (must be overridden)
    token_type: ClassVar[str]

    # Common fields for all tokens
    confidence: float = Field(..., ge=0, le=1, description="Extraction confidence")
    name: str = Field(..., description="Semantic name")
    design_intent: str = Field(default="", description="AI-detected design intent")

    # Metadata
    extraction_metadata: dict | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @classmethod
    @abstractmethod
    def from_ai_response(cls, response: dict) -> 'BaseToken':
        """
        Create token instance from AI extraction response.

        Each token type implements parsing logic specific to its data.
        """
        pass

    @abstractmethod
    def compute_properties(self) -> dict:
        """
        Compute derived properties for this token.

        Returns dict of computed values to merge into token.
        """
        pass

    @abstractmethod
    def to_export_dict(self) -> dict:
        """
        Convert token to export-friendly dictionary.

        Used by generators for export formats.
        """
        pass

    @classmethod
    def get_token_type(cls) -> str:
        """Return the token type identifier"""
        return cls.token_type

    def get_w3c_type(self) -> str:
        """Return the W3C Design Token $type"""
        return self._w3c_type_mapping().get(self.token_type, "custom")

    @staticmethod
    def _w3c_type_mapping() -> dict:
        """Mapping of token types to W3C $type values"""
        return {
            "color": "color",
            "spacing": "dimension",
            "typography": "typography",
            "shadow": "shadow",
            "border": "border",
            "opacity": "number",
            "duration": "duration",
        }


class BaseTokenConfig:
    """Configuration for token behavior"""

    # Deduplication
    deduplication_enabled: bool = True
    deduplication_threshold: float = 0.10  # 10% default

    # Extraction
    max_tokens: int = 12
    min_confidence: float = 0.5

    # Streaming
    stream_delay_ms: int = 50  # Delay between streamed tokens

    # Export
    default_export_format: str = "w3c"
```

### 2.2 BaseExtractor - Abstract Extractor

**File:** `src/copy_that/tokens/factory/base_extractor.py`

```python
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, AsyncIterator
import anthropic
import asyncio

T = TypeVar('T', bound='BaseToken')

class ExtractionResult(Generic[T]):
    """Container for extraction results"""

    def __init__(
        self,
        tokens: list[T],
        metadata: dict | None = None
    ):
        self.tokens = tokens
        self.metadata = metadata or {}
        self.token_count = len(tokens)


class BaseExtractor(ABC, Generic[T]):
    """
    Abstract base class for all token extractors.

    Provides:
    - Multiple input source support (URL, base64, file)
    - AI provider abstraction (Claude, OpenAI)
    - Async extraction patterns
    - Streaming support
    - Error handling and retry logic
    """

    # Class variables (must be overridden)
    token_class: type[T]
    default_model: str = "claude-sonnet-4-5-20250929"

    def __init__(
        self,
        model: str | None = None,
        max_retries: int = 3
    ):
        self.model = model or self.default_model
        self.max_retries = max_retries
        self.client = anthropic.Anthropic()

    # === Main Extraction Methods ===

    async def extract_from_url(
        self,
        image_url: str,
        max_tokens: int = 12,
        **kwargs
    ) -> ExtractionResult[T]:
        """Extract tokens from image URL"""
        image_data = await self._fetch_image(image_url)
        return await self.extract_from_bytes(image_data, max_tokens, **kwargs)

    async def extract_from_base64(
        self,
        image_data: str,
        media_type: str,
        max_tokens: int = 12,
        **kwargs
    ) -> ExtractionResult[T]:
        """Extract tokens from base64 encoded image"""
        return await self._execute_extraction(
            image_data, media_type, max_tokens, **kwargs
        )

    async def extract_from_bytes(
        self,
        image_bytes: bytes,
        max_tokens: int = 12,
        **kwargs
    ) -> ExtractionResult[T]:
        """Extract tokens from raw bytes"""
        import base64
        encoded = base64.standard_b64encode(image_bytes).decode('utf-8')
        media_type = self._detect_media_type(image_bytes)
        return await self.extract_from_base64(encoded, media_type, max_tokens, **kwargs)

    # === Streaming Extraction ===

    async def extract_streaming(
        self,
        image_data: str,
        media_type: str,
        max_tokens: int = 12,
        on_token: callable | None = None,
        **kwargs
    ) -> AsyncIterator[dict]:
        """
        Extract tokens with streaming support.

        Yields progress updates and tokens as they are processed.
        """
        yield {
            'phase': 1,
            'status': 'starting',
            'message': f'Beginning {self.token_class.token_type} extraction...'
        }

        # Execute extraction
        result = await self._execute_extraction(
            image_data, media_type, max_tokens, **kwargs
        )

        # Stream each token
        for idx, token in enumerate(result.tokens):
            progress = (idx + 1) / len(result.tokens)

            yield {
                'phase': 1,
                'status': 'token_extracted',
                'progress': progress,
                'token': token.to_export_dict()
            }

            if on_token:
                await on_token(token)

            await asyncio.sleep(0.05)  # Small delay for UI

        # Compute properties phase
        yield {
            'phase': 2,
            'status': 'computing_properties',
            'message': 'Computing derived properties...'
        }

        # Enrich tokens
        enriched_tokens = []
        for token in result.tokens:
            computed = token.compute_properties()
            enriched = {**token.to_export_dict(), **computed}
            enriched_tokens.append(enriched)

        # Complete
        yield {
            'phase': 3,
            'status': 'extraction_complete',
            'tokens': enriched_tokens,
            'metadata': result.metadata
        }

    # === Abstract Methods (Must Implement) ===

    @abstractmethod
    def _build_extraction_prompt(self, max_tokens: int, **kwargs) -> str:
        """
        Build the prompt for AI extraction.

        Each token type has specific prompt requirements.
        """
        pass

    @abstractmethod
    def _parse_ai_response(self, response_text: str) -> list[T]:
        """
        Parse AI response into token instances.

        Each token type has specific parsing logic.
        """
        pass

    # === Internal Methods ===

    async def _execute_extraction(
        self,
        image_data: str,
        media_type: str,
        max_tokens: int,
        **kwargs
    ) -> ExtractionResult[T]:
        """Execute the extraction with retry logic"""
        prompt = self._build_extraction_prompt(max_tokens, **kwargs)

        for attempt in range(self.max_retries):
            try:
                response = await self._call_ai(image_data, media_type, prompt)
                tokens = self._parse_ai_response(response)

                return ExtractionResult(
                    tokens=tokens,
                    metadata={
                        'model': self.model,
                        'attempt': attempt + 1,
                        'token_type': self.token_class.token_type
                    }
                )

            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

    async def _call_ai(
        self,
        image_data: str,
        media_type: str,
        prompt: str
    ) -> str:
        """Call AI model with image and prompt"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )

        return response.content[0].text

    async def _fetch_image(self, url: str) -> bytes:
        """Fetch image from URL"""
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.content

    def _detect_media_type(self, image_bytes: bytes) -> str:
        """Detect image media type from bytes"""
        if image_bytes[:8] == b'\x89PNG\r\n\x1a\n':
            return 'image/png'
        elif image_bytes[:2] == b'\xff\xd8':
            return 'image/jpeg'
        elif image_bytes[:6] in (b'GIF87a', b'GIF89a'):
            return 'image/gif'
        elif image_bytes[:4] == b'RIFF' and image_bytes[8:12] == b'WEBP':
            return 'image/webp'
        else:
            return 'image/png'  # Default


class BatchExtractor(Generic[T]):
    """
    Orchestrate parallel extraction from multiple images.

    Features:
    - Semaphore-controlled concurrency
    - Progress callbacks
    - Error handling per image
    - Result aggregation
    """

    def __init__(
        self,
        extractor: BaseExtractor[T],
        max_concurrent: int = 5
    ):
        self.extractor = extractor
        self.max_concurrent = max_concurrent

    async def extract_batch(
        self,
        image_urls: list[str],
        max_tokens: int = 12,
        on_progress: callable | None = None,
        **kwargs
    ) -> tuple[list[list[T]], dict]:
        """
        Extract from multiple images in parallel.

        Args:
            image_urls: List of image URLs
            max_tokens: Max tokens per image
            on_progress: Callback for progress updates

        Returns:
            (results_per_image, metadata)
        """
        semaphore = asyncio.Semaphore(self.max_concurrent)
        results = []

        async def extract_with_limit(url: str, index: int):
            async with semaphore:
                try:
                    result = await self.extractor.extract_from_url(
                        url, max_tokens, **kwargs
                    )

                    if on_progress:
                        await on_progress(index, len(image_urls), 'success')

                    return index, result.tokens

                except Exception as e:
                    if on_progress:
                        await on_progress(index, len(image_urls), 'error', str(e))

                    return index, []

        # Run all extractions
        tasks = [
            extract_with_limit(url, i)
            for i, url in enumerate(image_urls)
        ]
        task_results = await asyncio.gather(*tasks)

        # Sort by index
        task_results.sort(key=lambda x: x[0])
        results = [tokens for _, tokens in task_results]

        metadata = {
            'image_count': len(image_urls),
            'successful': sum(1 for r in results if r),
            'failed': sum(1 for r in results if not r)
        }

        return results, metadata
```

### 2.3 BaseAggregator - Abstract Aggregator

**File:** `src/copy_that/tokens/factory/base_aggregator.py`

```python
from abc import ABC, abstractmethod
from typing import TypeVar, Generic
from dataclasses import dataclass, field

T = TypeVar('T', bound='BaseToken')

@dataclass
class AggregatedToken(Generic[T]):
    """
    Token with provenance tracking.

    Tracks which images contributed to this token
    and aggregates confidence scores.
    """

    token: T
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
        self.source_images.append(image_id)
        self.confidence_scores.append(confidence)

    def merge(self, other: 'AggregatedToken[T]'):
        self.source_images.extend(other.source_images)
        self.confidence_scores.extend(other.confidence_scores)


@dataclass
class TokenLibrary(Generic[T]):
    """
    Aggregated token collection with statistics.
    """

    tokens: list[AggregatedToken[T]]
    statistics: dict
    token_type: str

    def to_dict(self) -> dict:
        return {
            'token_type': self.token_type,
            'token_count': len(self.tokens),
            'tokens': [
                {
                    **t.token.to_export_dict(),
                    'occurrence_count': t.occurrence_count,
                    'average_confidence': t.average_confidence,
                    'source_images': t.source_images
                }
                for t in self.tokens
            ],
            'statistics': self.statistics
        }


class BaseAggregator(ABC, Generic[T]):
    """
    Abstract base class for token aggregation and deduplication.

    Each token type implements its own similarity measure.
    """

    token_type: str
    default_threshold: float = 0.10

    @classmethod
    def aggregate_batch(
        cls,
        token_batches: list[list[T]],
        threshold: float | None = None
    ) -> TokenLibrary[T]:
        """
        Aggregate tokens from multiple images.

        Args:
            token_batches: List of token lists (one per image)
            threshold: Similarity threshold for deduplication

        Returns:
            TokenLibrary with deduplicated tokens
        """
        if threshold is None:
            threshold = cls.default_threshold

        aggregated: list[AggregatedToken[T]] = []

        for image_idx, tokens in enumerate(token_batches):
            image_id = f"image_{image_idx}"

            for token in tokens:
                # Find matching token
                matching = cls._find_matching(token, aggregated, threshold)

                if matching:
                    matching.add_provenance(image_id, token.confidence)
                else:
                    # Create new aggregated token
                    new_agg = AggregatedToken(token=token)
                    new_agg.add_provenance(image_id, token.confidence)
                    aggregated.append(new_agg)

        # Sort tokens
        aggregated = cls._sort_tokens(aggregated)

        # Generate statistics
        statistics = cls._generate_statistics(aggregated, len(token_batches))

        return TokenLibrary(
            tokens=aggregated,
            statistics=statistics,
            token_type=cls.token_type
        )

    @classmethod
    @abstractmethod
    def _calculate_similarity(cls, token1: T, token2: T) -> float:
        """
        Calculate similarity between two tokens.

        Returns value between 0 (different) and 1 (identical).
        Each token type implements its own measure.
        """
        pass

    @classmethod
    @abstractmethod
    def _sort_tokens(
        cls,
        tokens: list[AggregatedToken[T]]
    ) -> list[AggregatedToken[T]]:
        """
        Sort tokens in meaningful order.

        Colors by frequency, spacing by value, etc.
        """
        pass

    @classmethod
    @abstractmethod
    def _generate_statistics(
        cls,
        tokens: list[AggregatedToken[T]],
        image_count: int
    ) -> dict:
        """Generate aggregation statistics specific to token type"""
        pass

    @classmethod
    def _find_matching(
        cls,
        token: T,
        existing: list[AggregatedToken[T]],
        threshold: float
    ) -> AggregatedToken[T] | None:
        """Find existing token within similarity threshold"""
        for agg in existing:
            similarity = cls._calculate_similarity(token, agg.token)
            if similarity >= (1 - threshold):
                return agg
        return None
```

### 2.4 BaseGenerator - Abstract Generator (Enhanced)

**File:** `src/copy_that/tokens/factory/base_generator.py`

```python
from abc import ABC, abstractmethod
from typing import TypeVar, Generic
import json

T = TypeVar('T', bound='TokenLibrary')

class BaseGenerator(ABC, Generic[T]):
    """
    Abstract base class for all export generators.

    Generates code/config from aggregated tokens.
    """

    format_name: str  # e.g., "w3c", "css", "react"
    file_extension: str  # e.g., ".json", ".css", ".ts"

    def __init__(self, library: T):
        self.library = library

    @abstractmethod
    def generate(self) -> str:
        """Generate the output string"""
        pass

    def get_filename(self, base_name: str = "tokens") -> str:
        """Get suggested filename"""
        return f"{base_name}{self.file_extension}"

    def get_metadata(self) -> dict:
        """Get generator metadata"""
        return {
            'format': self.format_name,
            'extension': self.file_extension,
            'token_count': len(self.library.tokens)
        }


class W3CGeneratorMixin:
    """
    Mixin for W3C Design Tokens format generation.

    Provides common W3C formatting utilities.
    """

    def _create_w3c_token(
        self,
        name: str,
        value: any,
        token_type: str,
        description: str = "",
        extensions: dict | None = None
    ) -> dict:
        """Create a W3C-compliant token object"""
        token = {
            "$type": token_type,
            "$value": value
        }

        if description:
            token["$description"] = description

        if extensions:
            token["$extensions"] = {
                "copy-that": extensions
            }

        return {name: token}


class CSSGeneratorMixin:
    """
    Mixin for CSS custom properties generation.
    """

    def _to_css_variable_name(self, name: str) -> str:
        """Convert token name to CSS variable name"""
        return f"--{name.replace('_', '-').lower()}"

    def _generate_css_root(self, variables: list[str]) -> str:
        """Generate :root block with variables"""
        lines = [":root {"]
        lines.extend(f"  {var}" for var in variables)
        lines.append("}")
        return "\n".join(lines)


class TypeScriptGeneratorMixin:
    """
    Mixin for TypeScript/React generation.
    """

    def _generate_const_export(
        self,
        name: str,
        value: dict,
        as_const: bool = True
    ) -> str:
        """Generate TypeScript const export"""
        json_value = json.dumps(value, indent=2)
        const_suffix = " as const" if as_const else ""
        return f"export const {name} = {json_value}{const_suffix};\n"

    def _generate_type_export(self, name: str, from_const: str) -> str:
        """Generate type from const"""
        return f"export type {name} = keyof typeof {from_const};\n"
```

---

## 3. Registry System

### 3.1 Plugin Registry

**File:** `src/copy_that/tokens/factory/registry.py`

```python
from typing import Type
import logging

logger = logging.getLogger(__name__)

class TokenRegistry:
    """
    Central registry for token types, extractors, and generators.

    Enables dynamic discovery and plugin-style architecture.
    """

    _token_types: dict[str, Type['BaseToken']] = {}
    _extractors: dict[str, Type['BaseExtractor']] = {}
    _aggregators: dict[str, Type['BaseAggregator']] = {}
    _generators: dict[str, dict[str, Type['BaseGenerator']]] = {}

    @classmethod
    def register_token_type(
        cls,
        token_type: str,
        token_class: Type['BaseToken'],
        extractor_class: Type['BaseExtractor'],
        aggregator_class: Type['BaseAggregator']
    ):
        """
        Register a complete token type with all components.

        Args:
            token_type: Identifier (e.g., "color", "spacing")
            token_class: Token model class
            extractor_class: Extractor class
            aggregator_class: Aggregator class
        """
        cls._token_types[token_type] = token_class
        cls._extractors[token_type] = extractor_class
        cls._aggregators[token_type] = aggregator_class
        cls._generators[token_type] = {}

        logger.info(f"Registered token type: {token_type}")

    @classmethod
    def register_generator(
        cls,
        token_type: str,
        format_name: str,
        generator_class: Type['BaseGenerator']
    ):
        """
        Register a generator for a token type.

        Args:
            token_type: Token type identifier
            format_name: Export format (e.g., "w3c", "css")
            generator_class: Generator class
        """
        if token_type not in cls._generators:
            cls._generators[token_type] = {}

        cls._generators[token_type][format_name] = generator_class
        logger.info(f"Registered generator: {token_type}/{format_name}")

    @classmethod
    def get_extractor(cls, token_type: str) -> 'BaseExtractor':
        """Get extractor instance for token type"""
        if token_type not in cls._extractors:
            raise ValueError(f"Unknown token type: {token_type}")
        return cls._extractors[token_type]()

    @classmethod
    def get_aggregator(cls, token_type: str) -> Type['BaseAggregator']:
        """Get aggregator class for token type"""
        if token_type not in cls._aggregators:
            raise ValueError(f"Unknown token type: {token_type}")
        return cls._aggregators[token_type]

    @classmethod
    def get_generator(
        cls,
        token_type: str,
        format_name: str,
        library: 'TokenLibrary'
    ) -> 'BaseGenerator':
        """Get generator instance for token type and format"""
        if token_type not in cls._generators:
            raise ValueError(f"Unknown token type: {token_type}")
        if format_name not in cls._generators[token_type]:
            raise ValueError(f"Unknown format for {token_type}: {format_name}")

        generator_class = cls._generators[token_type][format_name]
        return generator_class(library)

    @classmethod
    def list_token_types(cls) -> list[str]:
        """List all registered token types"""
        return list(cls._token_types.keys())

    @classmethod
    def list_generators(cls, token_type: str) -> list[str]:
        """List available generators for a token type"""
        return list(cls._generators.get(token_type, {}).keys())

    @classmethod
    def get_metadata(cls) -> dict:
        """Get metadata for all registered components"""
        return {
            'token_types': cls.list_token_types(),
            'generators': {
                tt: cls.list_generators(tt)
                for tt in cls._token_types
            }
        }


def register_token_plugin(
    token_type: str,
    token_class: Type['BaseToken'],
    extractor_class: Type['BaseExtractor'],
    aggregator_class: Type['BaseAggregator'],
    generators: dict[str, Type['BaseGenerator']] | None = None
):
    """
    Convenience function to register a complete token plugin.

    Usage:
        register_token_plugin(
            'spacing',
            SpacingToken,
            SpacingExtractor,
            SpacingAggregator,
            {
                'w3c': SpacingW3CGenerator,
                'css': SpacingCSSGenerator,
                'react': SpacingReactGenerator
            }
        )
    """
    TokenRegistry.register_token_type(
        token_type,
        token_class,
        extractor_class,
        aggregator_class
    )

    if generators:
        for format_name, generator_class in generators.items():
            TokenRegistry.register_generator(
                token_type,
                format_name,
                generator_class
            )
```

---

## 4. Pipeline Orchestrator

### 4.1 Unified Pipeline

**File:** `src/copy_that/tokens/factory/pipeline.py`

```python
from typing import TypeVar
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar('T', bound='BaseToken')

class TokenPipeline:
    """
    Unified pipeline for token extraction, aggregation, and export.

    Orchestrates the full flow from image to exported tokens.
    """

    def __init__(self, token_type: str):
        self.token_type = token_type
        self.extractor = TokenRegistry.get_extractor(token_type)
        self.aggregator = TokenRegistry.get_aggregator(token_type)

    async def extract_single(
        self,
        image_data: str,
        media_type: str,
        max_tokens: int = 12,
        **kwargs
    ) -> 'ExtractionResult':
        """Extract tokens from a single image"""
        return await self.extractor.extract_from_base64(
            image_data,
            media_type,
            max_tokens,
            **kwargs
        )

    async def extract_batch(
        self,
        image_urls: list[str],
        max_tokens: int = 12,
        threshold: float | None = None,
        on_progress: callable | None = None,
        **kwargs
    ) -> 'TokenLibrary':
        """
        Extract and aggregate tokens from multiple images.

        Returns aggregated library ready for export.
        """
        # Batch extraction
        batch_extractor = BatchExtractor(
            self.extractor,
            max_concurrent=5
        )

        results, metadata = await batch_extractor.extract_batch(
            image_urls,
            max_tokens,
            on_progress,
            **kwargs
        )

        # Aggregate
        library = self.aggregator.aggregate_batch(results, threshold)

        return library

    async def extract_and_persist(
        self,
        db: AsyncSession,
        project_id: int,
        image_urls: list[str],
        **kwargs
    ) -> tuple['TokenLibrary', int]:
        """
        Extract, aggregate, and persist to database.

        Returns (library, job_id)
        """
        # Create extraction job
        from copy_that.domain.models import ExtractionJob

        job = ExtractionJob(
            project_id=project_id,
            extraction_type=self.token_type,
            status="processing"
        )
        db.add(job)
        await db.commit()

        try:
            # Extract and aggregate
            library = await self.extract_batch(image_urls, **kwargs)

            # Persist tokens
            await self._persist_tokens(db, job.id, project_id, library)

            # Update job status
            job.status = "completed"
            job.result_data = library.statistics
            await db.commit()

            return library, job.id

        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            await db.commit()
            raise

    async def _persist_tokens(
        self,
        db: AsyncSession,
        job_id: int,
        project_id: int,
        library: 'TokenLibrary'
    ):
        """Persist aggregated tokens to database"""
        # Token-type specific model
        model_class = self._get_db_model_class()

        for agg_token in library.tokens:
            db_token = model_class(
                extraction_job_id=job_id,
                project_id=project_id,
                **agg_token.token.to_export_dict()
            )
            db.add(db_token)

        await db.commit()

    def _get_db_model_class(self):
        """Get SQLAlchemy model class for this token type"""
        from copy_that.domain import models

        mapping = {
            'color': models.ColorToken,
            'spacing': models.SpacingToken,
            'typography': models.TypographyToken,
        }

        return mapping.get(self.token_type)

    def export(
        self,
        library: 'TokenLibrary',
        format_name: str
    ) -> str:
        """Export library to specified format"""
        generator = TokenRegistry.get_generator(
            self.token_type,
            format_name,
            library
        )
        return generator.generate()

    def export_all_formats(
        self,
        library: 'TokenLibrary'
    ) -> dict[str, str]:
        """Export library to all available formats"""
        formats = TokenRegistry.list_generators(self.token_type)
        exports = {}

        for format_name in formats:
            try:
                exports[format_name] = self.export(library, format_name)
            except Exception as e:
                exports[format_name] = f"Error: {e}"

        return exports


class MultiTokenPipeline:
    """
    Run multiple token pipelines in parallel.

    Extract colors, spacing, typography simultaneously.
    """

    def __init__(self, token_types: list[str]):
        self.pipelines = {
            tt: TokenPipeline(tt)
            for tt in token_types
        }

    async def extract_all(
        self,
        image_urls: list[str],
        **kwargs
    ) -> dict[str, 'TokenLibrary']:
        """
        Extract all token types in parallel.

        Returns dict mapping token_type to library.
        """
        tasks = {
            tt: pipeline.extract_batch(image_urls, **kwargs)
            for tt, pipeline in self.pipelines.items()
        }

        results = await asyncio.gather(*tasks.values(), return_exceptions=True)

        return {
            tt: result
            for tt, result in zip(tasks.keys(), results)
            if not isinstance(result, Exception)
        }
```

---

## 5. Streaming Engine

### 5.1 SSE Streaming Support

**File:** `src/copy_that/tokens/factory/streaming.py`

```python
import json
import asyncio
from typing import AsyncIterator
from fastapi.responses import StreamingResponse

class StreamingEngine:
    """
    Server-Sent Events streaming support for token extraction.

    Provides real-time progress updates during extraction.
    """

    @staticmethod
    async def create_extraction_stream(
        pipeline: 'TokenPipeline',
        image_data: str,
        media_type: str,
        max_tokens: int = 12,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Create SSE stream for single image extraction.

        Yields SSE-formatted events.
        """
        async for event in pipeline.extractor.extract_streaming(
            image_data,
            media_type,
            max_tokens,
            **kwargs
        ):
            yield f"data: {json.dumps(event)}\n\n"

    @staticmethod
    async def create_batch_stream(
        pipeline: 'TokenPipeline',
        image_urls: list[str],
        max_tokens: int = 12,
        threshold: float | None = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Create SSE stream for batch extraction.

        Streams progress for each image and final aggregation.
        """
        total = len(image_urls)

        # Start event
        yield f"data: {json.dumps({
            'phase': 1,
            'status': 'starting',
            'message': f'Extracting from {total} images...',
            'total': total
        })}\n\n"

        # Progress callback
        async def on_progress(index, total, status, error=None):
            event = {
                'phase': 1,
                'status': 'image_processed',
                'index': index,
                'total': total,
                'progress': (index + 1) / total,
                'result': status
            }
            if error:
                event['error'] = error

        # Extract
        try:
            library = await pipeline.extract_batch(
                image_urls,
                max_tokens,
                threshold,
                on_progress,
                **kwargs
            )

            # Aggregation phase
            yield f"data: {json.dumps({
                'phase': 2,
                'status': 'aggregating',
                'message': 'Aggregating tokens...'
            })}\n\n"

            await asyncio.sleep(0.1)

            # Complete
            yield f"data: {json.dumps({
                'phase': 3,
                'status': 'complete',
                'library': library.to_dict()
            })}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({
                'phase': -1,
                'status': 'error',
                'message': str(e)
            })}\n\n"

    @staticmethod
    def create_streaming_response(
        stream: AsyncIterator[str]
    ) -> StreamingResponse:
        """Create FastAPI StreamingResponse for SSE"""
        return StreamingResponse(
            stream,
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
```

---

## 6. Creating New Token Types

### 6.1 Step-by-Step Template

To create a new token type (e.g., "typography"), follow this template:

#### Step 1: Define Token Model

```python
# src/copy_that/tokens/typography/models.py

from copy_that.tokens.factory.base_token import BaseToken
from pydantic import Field

class TypographyToken(BaseToken):
    token_type = "typography"

    # Core fields
    font_family: str
    font_size: int
    font_weight: int
    line_height: float
    letter_spacing: float

    # Analysis
    readability_score: float = 0.0
    suggested_use: str = ""

    @classmethod
    def from_ai_response(cls, response: dict) -> 'TypographyToken':
        return cls(
            font_family=response['font_family'],
            font_size=response['font_size'],
            font_weight=response.get('font_weight', 400),
            line_height=response.get('line_height', 1.5),
            letter_spacing=response.get('letter_spacing', 0),
            confidence=response.get('confidence', 0.5),
            name=response.get('name', 'body'),
            design_intent=response.get('design_intent', '')
        )

    def compute_properties(self) -> dict:
        return {
            'font_size_rem': self.font_size / 16,
            'readability_score': self._calculate_readability(),
            'suggested_use': self._suggest_use()
        }

    def to_export_dict(self) -> dict:
        return {
            'font_family': self.font_family,
            'font_size': self.font_size,
            'font_weight': self.font_weight,
            'line_height': self.line_height,
            'letter_spacing': self.letter_spacing,
            'confidence': self.confidence,
            'name': self.name
        }

    def _calculate_readability(self) -> float:
        # Readability based on size and line height
        if 14 <= self.font_size <= 18 and 1.4 <= self.line_height <= 1.8:
            return 0.95
        return 0.7

    def _suggest_use(self) -> str:
        if self.font_size >= 24:
            return "heading"
        elif self.font_size >= 16:
            return "body"
        else:
            return "caption"
```

#### Step 2: Implement Extractor

```python
# src/copy_that/tokens/typography/extractor.py

from copy_that.tokens.factory.base_extractor import BaseExtractor
from .models import TypographyToken

class TypographyExtractor(BaseExtractor[TypographyToken]):
    token_class = TypographyToken

    def _build_extraction_prompt(self, max_tokens: int, **kwargs) -> str:
        return f"""Analyze this UI/design image and extract up to {max_tokens} typography styles.

For each style, provide:
1. font_family: The font family (e.g., "Inter", "Roboto")
2. font_size: Size in pixels
3. font_weight: Weight (100-900)
4. line_height: Line height ratio
5. letter_spacing: Letter spacing in pixels
6. name: Semantic name (e.g., "heading-1", "body")
7. design_intent: Purpose of this typography

Return as JSON array."""

    def _parse_ai_response(self, response_text: str) -> list[TypographyToken]:
        import json
        data = json.loads(response_text)

        return [
            TypographyToken.from_ai_response(item)
            for item in data
        ]
```

#### Step 3: Implement Aggregator

```python
# src/copy_that/tokens/typography/aggregator.py

from copy_that.tokens.factory.base_aggregator import BaseAggregator, AggregatedToken
from .models import TypographyToken

class TypographyAggregator(BaseAggregator[TypographyToken]):
    token_type = "typography"
    default_threshold = 0.15  # 15% difference

    @classmethod
    def _calculate_similarity(cls, t1: TypographyToken, t2: TypographyToken) -> float:
        # Compare font family
        if t1.font_family.lower() != t2.font_family.lower():
            return 0.0

        # Compare size (within 15%)
        size_diff = abs(t1.font_size - t2.font_size) / max(t1.font_size, t2.font_size)
        if size_diff > 0.15:
            return 0.5

        # Compare weight
        weight_diff = abs(t1.font_weight - t2.font_weight) / 900
        if weight_diff > 0.2:
            return 0.7

        return 1.0

    @classmethod
    def _sort_tokens(cls, tokens: list[AggregatedToken[TypographyToken]]):
        return sorted(tokens, key=lambda t: t.token.font_size, reverse=True)

    @classmethod
    def _generate_statistics(cls, tokens, image_count) -> dict:
        if not tokens:
            return {'token_count': 0}

        sizes = [t.token.font_size for t in tokens]
        families = set(t.token.font_family for t in tokens)

        return {
            'token_count': len(tokens),
            'image_count': image_count,
            'font_families': list(families),
            'size_range': {'min': min(sizes), 'max': max(sizes)},
            'average_confidence': sum(t.average_confidence for t in tokens) / len(tokens)
        }
```

#### Step 4: Implement Generators

```python
# src/copy_that/tokens/typography/generators.py

from copy_that.tokens.factory.base_generator import (
    BaseGenerator,
    W3CGeneratorMixin,
    CSSGeneratorMixin
)

class TypographyW3CGenerator(BaseGenerator, W3CGeneratorMixin):
    format_name = "w3c"
    file_extension = ".json"

    def generate(self) -> str:
        import json
        tokens = {}

        for agg in self.library.tokens:
            t = agg.token
            tokens[t.name] = {
                "$type": "typography",
                "$value": {
                    "fontFamily": t.font_family,
                    "fontSize": f"{t.font_size}px",
                    "fontWeight": t.font_weight,
                    "lineHeight": t.line_height,
                    "letterSpacing": f"{t.letter_spacing}px"
                }
            }

        return json.dumps({"typography": tokens}, indent=2)


class TypographyCSSGenerator(BaseGenerator, CSSGeneratorMixin):
    format_name = "css"
    file_extension = ".css"

    def generate(self) -> str:
        lines = [":root {"]

        for agg in self.library.tokens:
            t = agg.token
            name = t.name.replace('_', '-')
            lines.append(f"  --font-{name}-family: {t.font_family};")
            lines.append(f"  --font-{name}-size: {t.font_size}px;")
            lines.append(f"  --font-{name}-weight: {t.font_weight};")
            lines.append(f"  --font-{name}-line-height: {t.line_height};")

        lines.append("}")
        return "\n".join(lines)
```

#### Step 5: Register Plugin

```python
# src/copy_that/tokens/typography/__init__.py

from copy_that.tokens.factory.registry import register_token_plugin
from .models import TypographyToken
from .extractor import TypographyExtractor
from .aggregator import TypographyAggregator
from .generators import TypographyW3CGenerator, TypographyCSSGenerator

# Register the complete typography plugin
register_token_plugin(
    'typography',
    TypographyToken,
    TypographyExtractor,
    TypographyAggregator,
    {
        'w3c': TypographyW3CGenerator,
        'css': TypographyCSSGenerator
    }
)
```

---

## 7. API Router Template

### 7.1 Generic Token Router

**File:** `src/copy_that/interfaces/api/token_router_template.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

def create_token_router(
    token_type: str,
    prefix: str,
    tags: list[str]
) -> APIRouter:
    """
    Factory function to create token-type-specific router.

    Usage:
        spacing_router = create_token_router(
            'spacing',
            '/api/v1/spacing',
            ['spacing']
        )
    """
    router = APIRouter(prefix=prefix, tags=tags)
    pipeline = TokenPipeline(token_type)

    @router.post("/extract")
    async def extract(
        request: ExtractionRequest,
        db: AsyncSession = Depends(get_db)
    ):
        """Extract tokens from single image"""
        result = await pipeline.extract_single(
            request.image_data,
            request.media_type,
            request.max_tokens
        )

        return {
            'tokens': [t.to_export_dict() for t in result.tokens],
            'metadata': result.metadata
        }

    @router.post("/extract-streaming")
    async def extract_streaming(
        request: ExtractionRequest,
        db: AsyncSession = Depends(get_db)
    ):
        """Extract with SSE streaming"""
        stream = StreamingEngine.create_extraction_stream(
            pipeline,
            request.image_data,
            request.media_type,
            request.max_tokens
        )
        return StreamingEngine.create_streaming_response(stream)

    @router.post("/extract-batch")
    async def extract_batch(
        request: BatchRequest,
        db: AsyncSession = Depends(get_db)
    ):
        """Extract from multiple images with aggregation"""
        library = await pipeline.extract_batch(
            request.image_urls,
            request.max_tokens,
            request.threshold
        )

        return library.to_dict()

    @router.post("/export/{format_name}")
    async def export(
        format_name: str,
        request: ExportRequest,
        db: AsyncSession = Depends(get_db)
    ):
        """Export tokens in specified format"""
        # Get library from database or request
        library = await get_library_from_db(db, request.library_id)

        output = pipeline.export(library, format_name)

        return {
            'format': format_name,
            'content': output
        }

    return router
```

---

## 8. Testing Infrastructure

### 8.1 Base Test Classes

```python
# tests/tokens/base_test.py

import pytest
from abc import ABC, abstractmethod

class BaseTokenTest(ABC):
    """Base test class for all token types"""

    @pytest.fixture
    @abstractmethod
    def token_class(self):
        """Return token class to test"""
        pass

    @pytest.fixture
    @abstractmethod
    def sample_data(self):
        """Return sample token data"""
        pass

    def test_from_ai_response(self, token_class, sample_data):
        token = token_class.from_ai_response(sample_data)
        assert token is not None
        assert 0 <= token.confidence <= 1

    def test_compute_properties(self, token_class, sample_data):
        token = token_class.from_ai_response(sample_data)
        props = token.compute_properties()
        assert isinstance(props, dict)

    def test_to_export_dict(self, token_class, sample_data):
        token = token_class.from_ai_response(sample_data)
        export = token.to_export_dict()
        assert isinstance(export, dict)
        assert 'confidence' in export


class BaseExtractorTest(ABC):
    """Base test class for extractors"""

    @pytest.fixture
    @abstractmethod
    def extractor(self):
        pass

    @pytest.fixture
    def sample_image(self):
        return load_test_image("sample_ui.png")

    async def test_extract_from_bytes(self, extractor, sample_image):
        result = await extractor.extract_from_bytes(sample_image)
        assert len(result.tokens) > 0


class BaseAggregatorTest(ABC):
    """Base test class for aggregators"""

    @pytest.fixture
    @abstractmethod
    def aggregator(self):
        pass

    def test_aggregate_batch_deduplication(self, aggregator, sample_batches):
        library = aggregator.aggregate_batch(sample_batches)
        assert len(library.tokens) <= sum(len(b) for b in sample_batches)
```

---

## 9. Frontend Integration

### 9.1 Token Type Registry Extension

```typescript
// frontend/src/config/tokenTypeRegistry.tsx

import { TokenTypeSchema } from '../types';

// Define schema for each token type
export const tokenTypeRegistry: Record<string, TokenTypeSchema> = {
  color: { /* existing */ },

  spacing: {
    name: 'Spacing',
    icon: SpacingIcon,
    primaryVisual: SpacingVisual,
    formatTabs: [
      { id: 'preview', label: 'Preview', component: SpacingPreview },
      { id: 'scale', label: 'Scale', component: SpacingScale }
    ],
    playgroundTabs: [
      { id: 'component', label: 'Component', component: SpacingPlayground }
    ],
    filters: [
      { id: 'type', label: 'Type', options: ['padding', 'margin', 'gap'] },
      { id: 'scale', label: 'Scale', options: ['xs', 'sm', 'md', 'lg', 'xl'] }
    ]
  },

  typography: {
    name: 'Typography',
    icon: TypographyIcon,
    primaryVisual: TypographyVisual,
    formatTabs: [
      { id: 'specimen', label: 'Specimen', component: TypographySpecimen },
      { id: 'scale', label: 'Type Scale', component: TypeScale }
    ],
    playgroundTabs: [
      { id: 'text', label: 'Text', component: TypographyPlayground }
    ],
    filters: [
      { id: 'family', label: 'Family', options: [] }, // Dynamic
      { id: 'weight', label: 'Weight', options: ['300', '400', '500', '600', '700'] }
    ]
  }
};
```

### 9.2 Generic Token Store

```typescript
// frontend/src/store/tokenStore.ts

interface TokenStore {
  // Generic token storage
  tokens: Record<string, any[]>;  // tokenType -> tokens

  // Actions
  setTokens: (tokenType: string, tokens: any[]) => void;
  addToken: (tokenType: string, token: any) => void;
  clearTokens: (tokenType: string) => void;

  // Streaming state
  extractionState: Record<string, {
    isExtracting: boolean;
    progress: number;
    phase: number;
  }>;

  // Actions
  setExtractionState: (tokenType: string, state: ExtractionState) => void;
}
```

---

## 10. Implementation Checklist

### Phase 1: Core Factory
- [ ] Create `tokens/factory/` directory structure
- [ ] Implement `base_token.py` with BaseToken class
- [ ] Implement `base_extractor.py` with BaseExtractor and BatchExtractor
- [ ] Implement `base_aggregator.py` with BaseAggregator
- [ ] Enhance `base_generator.py` with mixins
- [ ] Implement `registry.py` with TokenRegistry
- [ ] Write unit tests for all base classes

### Phase 2: Pipeline Infrastructure
- [ ] Implement `pipeline.py` with TokenPipeline
- [ ] Implement `streaming.py` with StreamingEngine
- [ ] Implement `utils.py` with shared utilities
- [ ] Write integration tests for pipeline

### Phase 3: Migrate Color Token
- [ ] Refactor existing ColorToken to extend BaseToken
- [ ] Refactor AIColorExtractor to extend BaseExtractor
- [ ] Refactor ColorAggregator to extend BaseAggregator
- [ ] Register color plugin with TokenRegistry
- [ ] Verify existing functionality works

### Phase 4: Implement Spacing Token
- [ ] Follow SPACING_TOKEN_PIPELINE_PLANNING.md
- [ ] Use factory abstractions
- [ ] Register spacing plugin

### Phase 5: Implement Typography Token
- [ ] Create TypographyToken model
- [ ] Create TypographyExtractor
- [ ] Create TypographyAggregator
- [ ] Create generators
- [ ] Register typography plugin

### Phase 6: API Integration
- [ ] Create generic token router factory
- [ ] Update existing routes to use factory
- [ ] Add new token type routes

### Phase 7: Frontend Integration
- [ ] Update token type registry
- [ ] Create generic token components
- [ ] Wire up API calls

### Phase 8: Documentation
- [ ] Document factory API
- [ ] Create plugin development guide
- [ ] Add examples for new token types

---

## 11. Benefits of This Approach

### 11.1 Code Reuse
- **80%+ shared code** between token types
- Base classes handle common patterns
- Only implement token-specific logic

### 11.2 Consistency
- **Same patterns** across all token types
- Consistent API responses
- Predictable behavior

### 11.3 Parallel Development
- **Multiple token types** can be developed simultaneously
- Independent plugins don't conflict
- Easy to add contributors

### 11.4 Testing
- **Base test classes** provide scaffolding
- Token-specific tests are minimal
- High coverage with less code

### 11.5 Extensibility
- **Add new token types** in hours, not days
- Generators automatically work
- Registry enables dynamic discovery

---

## 12. Related Documentation

- **[SPACING_TOKEN_PIPELINE_PLANNING.md](./SPACING_TOKEN_PIPELINE_PLANNING.md)** - Spacing implementation using factory
- **[PLUGIN_ARCHITECTURE.md](../../architecture/PLUGIN_ARCHITECTURE.md)** - Plugin system overview
- **[EXTRACTOR_PATTERNS.md](../../architecture/EXTRACTOR_PATTERNS.md)** - Extractor best practices
- **[TOKEN_SYSTEM.md](../../domain/TOKEN_SYSTEM.md)** - Token types and structure

---

**Version:** 1.0 | **Last Updated:** 2025-11-22 | **Status:** Planning Document

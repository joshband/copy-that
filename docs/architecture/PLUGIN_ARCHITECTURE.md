# Plugin Architecture: Modular Token Platform

**Version:** 1.0 | **Date:** 2025-11-19 | **Status:** Guide

This document explains the plugin architecture that enables Copy That's modular, extensible design.

---

## 🎯 Core Philosophy

Copy That follows a **plugin-based architecture** where:

- **Core Platform** - Minimal, stable, handles all token types
- **Plugins** - Modular extractors and generators that extend the platform
- **Loose Coupling** - Plugins are independent, can be mixed/matched
- **Registry** - Plugins register themselves at startup
- **Composition** - Run any combination of plugins on any input

```
Plugins:  Color | Spacing | Typography | Shadow | Border | Opacity
           ↑         ↑            ↑          ↑        ↑       ↑
           └─────────┴────────────┴──────────┴────────┴───────┘
                           ↓
                   Core Platform (Token Engine)
                           ↓
Generators: React | CSS | JSON | Figma | Material | Flutter | JUCE
             ↑      ↑     ↑      ↑        ↑        ↑        ↑
             └──────┴─────┴──────┴────────┴────────┴────────┘
```

---

## 📦 Plugin Types

### 1. Extractor Plugins

**Purpose:** Extract tokens from images

```python
class ColorExtractorPlugin(BasePlugin):
    """Extract color tokens"""

    name = "color_extractor"
    version = "1.0.0"
    description = "Extract color palette from images"

    def execute(self, image_bytes: bytes) -> List[Dict]:
        """Extract colors"""
        extractor = ColorExtractor()
        return extractor.extract(image_bytes)
```

**Examples:**
- ColorExtractor (K-means clustering)
- SpacingExtractor (SAM segmentation)
- TypographyExtractor (Font detection)
- ShadowExtractor (Depth analysis)

### 2. Generator Plugins

**Purpose:** Generate code/config from tokens

```python
class ReactGeneratorPlugin(BasePlugin):
    """Generate React theme"""

    name = "react_generator"
    version = "1.0.0"
    description = "Generate React CSS-in-JS theme"

    def execute(self, tokens: Dict) -> str:
        """Generate React code"""
        return f"""
export const theme = {{
  colors: {json.dumps(tokens['colors'])},
  spacing: {json.dumps(tokens['spacing'])}
}};
"""
```

**Examples:**
- ReactGenerator (CSS-in-JS)
- CSSGenerator (CSS Variables)
- JSONGenerator (W3C Tokens)
- FigmaGenerator (Design Tokens)
- MaterialGenerator (Material-UI)
- FlutterGenerator (Flutter theme)
- JUCEGenerator (C++ audio plugin)

### 3. Transformer Plugins

**Purpose:** Transform/enhance tokens

```python
class SemanticNamerPlugin(BasePlugin):
    """Add semantic names to tokens"""

    name = "semantic_namer"
    version = "1.0.0"

    def execute(self, tokens: Dict) -> Dict:
        """Add semantic names"""
        for color in tokens.get('colors', []):
            color['semantic_name'] = self.name_color(color['hex'])
        return tokens
```

---

## 🏗️ Plugin Base Class

All plugins inherit from `BasePlugin`:

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List

class BasePlugin(ABC):
    """Base class for all plugins"""

    # Plugin metadata
    name: str
    version: str
    description: str

    @property
    def plugin_id(self) -> str:
        """Unique plugin identifier"""
        return f"{self.name}@{self.version}"

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute plugin logic"""
        pass

    def validate_input(self, *args, **kwargs) -> bool:
        """Validate plugin input"""
        return True

    def on_startup(self):
        """Called when plugin is loaded"""
        pass

    def on_shutdown(self):
        """Called when plugin is unloaded"""
        pass

    def get_metadata(self) -> Dict[str, Any]:
        """Return plugin metadata"""
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'type': self.__class__.__name__
        }
```

---

## 📝 Plugin Registry

### Registration

Plugins register themselves at startup:

```python
from copy_that.infrastructure.plugins.registry import PluginRegistry

# Extractors
PluginRegistry.register_extractor('color', ColorExtractorPlugin())
PluginRegistry.register_extractor('spacing', SpacingExtractorPlugin())
PluginRegistry.register_extractor('typography', TypographyExtractorPlugin())

# Generators
PluginRegistry.register_generator('react', ReactGeneratorPlugin())
PluginRegistry.register_generator('css', CSSGeneratorPlugin())
PluginRegistry.register_generator('json', JSONGeneratorPlugin())

# Transformers
PluginRegistry.register_transformer('semantic_namer', SemanticNamerPlugin())
PluginRegistry.register_transformer('delta_e_merger', DeltaEMergerPlugin())
```

### Registry Implementation

```python
from typing import Dict, Type

class PluginRegistry:
    """Central registry for plugins"""

    _extractors: Dict[str, BasePlugin] = {}
    _generators: Dict[str, BasePlugin] = {}
    _transformers: Dict[str, BasePlugin] = {}

    @classmethod
    def register_extractor(cls, name: str, plugin: BasePlugin):
        """Register an extractor plugin"""
        cls._extractors[name] = plugin
        logger.info(f"Registered extractor: {plugin.plugin_id}")

    @classmethod
    def register_generator(cls, name: str, plugin: BasePlugin):
        """Register a generator plugin"""
        cls._generators[name] = plugin
        logger.info(f"Registered generator: {plugin.plugin_id}")

    @classmethod
    def register_transformer(cls, name: str, plugin: BasePlugin):
        """Register a transformer plugin"""
        cls._transformers[name] = plugin
        logger.info(f"Registered transformer: {plugin.plugin_id}")

    @classmethod
    def get_extractor(cls, name: str) -> BasePlugin:
        """Get extractor by name"""
        if name not in cls._extractors:
            raise PluginNotFound(f"Extractor '{name}' not found")
        return cls._extractors[name]

    @classmethod
    def list_extractors(cls) -> List[str]:
        """List all registered extractors"""
        return list(cls._extractors.keys())

    @classmethod
    def get_all_metadata(cls) -> Dict:
        """Get metadata for all plugins"""
        return {
            'extractors': {
                name: plugin.get_metadata()
                for name, plugin in cls._extractors.items()
            },
            'generators': {
                name: plugin.get_metadata()
                for name, plugin in cls._generators.items()
            },
            'transformers': {
                name: plugin.get_metadata()
                for name, plugin in cls._transformers.items()
            }
        }
```

---

## 🔄 Plugin Composition: Running Extractors

### Single Extractor

```python
async def extract_colors(image_bytes: bytes) -> List[Dict]:
    """Extract only colors"""
    extractor = PluginRegistry.get_extractor('color')
    return extractor.execute(image_bytes)
```

### Multiple Extractors (Parallel)

```python
async def extract_all(image_bytes: bytes) -> Dict[str, List]:
    """Extract all token types in parallel"""
    registry = PluginRegistry

    # Define extraction tasks
    tasks = {
        'colors': asyncio.to_thread(
            registry.get_extractor('color').execute,
            image_bytes
        ),
        'spacing': asyncio.to_thread(
            registry.get_extractor('spacing').execute,
            image_bytes
        ),
        'typography': asyncio.to_thread(
            registry.get_extractor('typography').execute,
            image_bytes
        ),
    }

    # Run in parallel
    results = await asyncio.gather(*tasks.values())

    # Combine results
    return dict(zip(tasks.keys(), results))
```

### With Error Handling (Graceful Degradation)

```python
async def extract_all_safe(image_bytes: bytes) -> Dict[str, List]:
    """Extract all types with error handling"""
    registry = PluginRegistry
    results = {}

    for extractor_name in registry.list_extractors():
        try:
            extractor = registry.get_extractor(extractor_name)
            tokens = extractor.execute(image_bytes)
            results[extractor_name] = tokens
        except Exception as e:
            logger.warning(f"Extractor '{extractor_name}' failed: {e}")
            results[extractor_name] = []

    return results
```

---

## 🎨 Plugin Composition: Running Generators

### Single Generator

```python
def generate_react_theme(tokens: Dict) -> str:
    """Generate React theme"""
    generator = PluginRegistry.get_generator('react')
    return generator.execute(tokens)
```

### Multiple Generators (Export as Multiple Formats)

```python
async def export_all_formats(tokens: Dict) -> Dict[str, str]:
    """Export tokens to all supported formats"""
    registry = PluginRegistry
    exports = {}

    for format_name in ['react', 'css', 'json', 'figma', 'flutter']:
        try:
            generator = registry.get_generator(format_name)
            exports[format_name] = generator.execute(tokens)
        except Exception as e:
            logger.error(f"Generator '{format_name}' failed: {e}")

    return exports
```

---

## 🔗 Plugin Chaining: Extractors → Transformers → Generators

### Full Pipeline

```python
async def full_extraction_pipeline(
    image_bytes: bytes,
    extraction_types: List[str],
    transformations: List[str],
    export_formats: List[str]
) -> Dict:
    """
    Complete pipeline:
    1. Extract tokens (parallel extractors)
    2. Transform tokens (chained transformers)
    3. Generate output (parallel generators)
    """

    registry = PluginRegistry

    # 1. EXTRACT: Run selected extractors
    print("Extracting tokens...")
    extracted = {}
    for token_type in extraction_types:
        extractor = registry.get_extractor(token_type)
        extracted[token_type] = extractor.execute(image_bytes)

    # 2. TRANSFORM: Apply transformations sequentially
    print("Transforming tokens...")
    tokens = extracted
    for transform_name in transformations:
        transformer = registry.get_transformer(transform_name)
        tokens = transformer.execute(tokens)

    # 3. GENERATE: Export to multiple formats
    print("Generating exports...")
    exports = {}
    for format_name in export_formats:
        generator = registry.get_generator(format_name)
        exports[format_name] = generator.execute(tokens)

    return {
        'extracted': extracted,
        'tokens': tokens,
        'exports': exports
    }

# Usage:
result = await full_extraction_pipeline(
    image_bytes=image_data,
    extraction_types=['color', 'spacing', 'typography'],
    transformations=['semantic_namer', 'delta_e_merger'],
    export_formats=['react', 'css', 'json', 'figma']
)
```

---

## 🌐 Plugin Discovery API

### Discover Available Plugins

```python
@router.get("/api/v1/plugins")
async def list_plugins() -> Dict:
    """List all available plugins"""
    return PluginRegistry.get_all_metadata()

# Response:
{
  "extractors": {
    "color": {
      "name": "color",
      "version": "1.0.0",
      "description": "Extract color palette from images"
    },
    "spacing": {...},
    "typography": {...}
  },
  "generators": {
    "react": {...},
    "css": {...},
    "json": {...},
    ...
  },
  "transformers": {
    "semantic_namer": {...},
    "delta_e_merger": {...}
  }
}
```

### Get Plugin Details

```python
@router.get("/api/v1/plugins/{plugin_type}/{plugin_name}")
async def get_plugin_details(
    plugin_type: str,
    plugin_name: str
) -> Dict:
    """Get details for specific plugin"""
    registry = PluginRegistry

    if plugin_type == 'extractor':
        plugin = registry.get_extractor(plugin_name)
    elif plugin_type == 'generator':
        plugin = registry.get_generator(plugin_name)
    elif plugin_type == 'transformer':
        plugin = registry.get_transformer(plugin_name)
    else:
        raise HTTPException(status_code=400, detail="Unknown plugin type")

    return plugin.get_metadata()
```

---

## 🧪 Testing Plugins

### Plugin Test Template

```python
import pytest
from copy_that.plugins.base import BasePlugin
from copy_that.plugins.extractors.color import ColorExtractorPlugin

class TestColorExtractorPlugin:
    @pytest.fixture
    def plugin(self):
        return ColorExtractorPlugin()

    def test_plugin_metadata(self, plugin):
        """Test plugin has required metadata"""
        assert plugin.name is not None
        assert plugin.version is not None
        assert plugin.description is not None

    def test_plugin_id(self, plugin):
        """Test plugin ID format"""
        assert plugin.plugin_id == f"{plugin.name}@{plugin.version}"

    def test_get_metadata(self, plugin):
        """Test metadata retrieval"""
        metadata = plugin.get_metadata()
        assert 'name' in metadata
        assert 'version' in metadata
        assert 'description' in metadata

    def test_extract_colors(self, plugin):
        """Test color extraction"""
        # Load test image
        image_bytes = load_test_image()

        # Execute plugin
        result = plugin.execute(image_bytes)

        # Validate result
        assert isinstance(result, list)
        assert len(result) > 0

        for token in result:
            assert 'hex' in token
            assert 'confidence' in token
```

---

## 🚀 Creating a New Plugin

### Step-by-Step

**1. Create plugin file** - `src/copy_that/plugins/extractors/my_extractor.py`

```python
from copy_that.plugins.base import BasePlugin

class MyExtractorPlugin(BasePlugin):
    name = "my_extractor"
    version = "1.0.0"
    description = "My custom extractor"

    def execute(self, image_bytes: bytes) -> List[Dict]:
        # Your extraction logic
        pass
```

**2. Register plugin** - In app initialization:

```python
from copy_that.plugins.extractors.my_extractor import MyExtractorPlugin

PluginRegistry.register_extractor('my_extractor', MyExtractorPlugin())
```

**3. Use in API**:

```python
@router.post("/api/v1/extract/my-tokens")
async def extract_my_tokens(file: UploadFile):
    image_bytes = await file.read()
    plugin = PluginRegistry.get_extractor('my_extractor')
    tokens = plugin.execute(image_bytes)
    return tokens
```

---

## 🔒 Plugin Security

### Sandboxing Considerations

```python
class SecurePluginRegistry(PluginRegistry):
    """Plugin registry with security controls"""

    @classmethod
    def register_extractor(cls, name: str, plugin: BasePlugin):
        """Register with validation"""

        # Validate plugin
        if not isinstance(plugin, BasePlugin):
            raise ValueError("Plugin must inherit from BasePlugin")

        # Check for suspicious methods
        suspicious_methods = ['__import__', 'eval', 'exec']
        for method in suspicious_methods:
            if hasattr(plugin, method):
                raise SecurityError(f"Plugin has suspicious method: {method}")

        # Rate limit plugins
        cls._enforce_plugin_limits(name)

        super().register_extractor(name, plugin)

    @classmethod
    def _enforce_plugin_limits(cls, name: str):
        """Enforce resource limits on plugins"""
        # CPU time limit
        # Memory limit
        # File system access restrictions
        pass
```

---

## 📊 Plugin Metrics

### Track Plugin Usage

```python
class PluginMetrics:
    """Track plugin execution metrics"""

    @classmethod
    def record_execution(cls, plugin_id: str, duration: float, success: bool):
        """Record plugin execution"""
        # Store metrics (prometheus, cloudwatch, etc.)
        pass

    @classmethod
    def get_plugin_stats(cls) -> Dict:
        """Get statistics for all plugins"""
        # Return execution counts, avg duration, error rates, etc.
        pass

# Middleware to track all plugin executions
@app.middleware("http")
async def track_plugin_execution(request, call_next):
    # Track execution time and success
    pass
```

---

## 🎯 Best Practices

### 1. **One Responsibility**
Each plugin should do one thing well.

### 2. **Graceful Degradation**
If a plugin fails, the system continues.

### 3. **Type Safety**
Use type hints throughout.

### 4. **Documentation**
Document what tokens each extractor produces.

### 5. **Testing**
Every plugin should have unit tests.

### 6. **Versioning**
Follow semantic versioning for plugins.

### 7. **Isolation**
Plugins should not depend on each other.

---

## 📚 Related Documentation

- **extractor_patterns.md** - How to build extractors
- **adapter_pattern.md** - Schema transformation
- **token_system.md** - Token types and structure

---

**Version:** 1.0 | **Last Updated:** 2025-11-19 | **Status:** Complete

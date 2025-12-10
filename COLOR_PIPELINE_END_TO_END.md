# Color Pipeline: End-to-End (CV → ML → AI → React Generation)

**Focus:** Comprehensive color extraction pipeline with production-ready React component generation
**Status:** Implementation roadmap with concrete code examples
**Timeline:** 3-4 weeks for full pipeline

---

## Architecture Overview

```
INPUT: Image (any UI design)
    ↓
PHASE 1: CV (Frontend, ~50ms)
├─ K-means color clustering
├─ Real-time display
└─ Initial TokenGraph

    ↓
PHASE 2: ML (Frontend/Backend, ~100ms-1s)
├─ Color science analysis
├─ Accessibility metrics
├─ Harmony detection
└─ TokenGraph enrichment

    ↓
PHASE 3: AI (Backend, async)
├─ Claude semantic naming
├─ Design intent detection
├─ Brand analysis
└─ Token relationships

    ↓
PHASE 4: React Generation
├─ Color palette component
├─ Color system documentation
├─ Figma integration
└─ Design tokens export

OUTPUT: React components + design tokens library
```

---

## Phase 1: CV - Frontend Color Extraction (50ms)

### 1.1 K-Means Implementation

```python
# backend/src/copy_that/extractors/color/kmeans.py
"""K-means color clustering - fast, accurate color extraction"""

import numpy as np
from typing import List, Tuple

class ColorKMeans:
    def __init__(self, k: int = 8, max_iterations: int = 100):
        self.k = k
        self.max_iterations = max_iterations

    def extract(self, image_array: np.ndarray) -> List[str]:
        """Extract top K colors using K-means clustering

        Args:
            image_array: Image as numpy array (H, W, 3) in RGB

        Returns:
            List of hex color strings sorted by prominence
        """
        # Reshape image to (pixels, 3)
        pixels = image_array.reshape(-1, 3).astype(np.float32)

        # Initialize centroids randomly
        indices = np.random.choice(pixels.shape[0], self.k, replace=False)
        centroids = pixels[indices].copy()

        for iteration in range(self.max_iterations):
            # Assign pixels to nearest centroid
            distances = np.cdist(pixels, centroids)
            assignments = np.argmin(distances, axis=1)

            # Update centroids
            new_centroids = np.array([
                pixels[assignments == i].mean(axis=0) if (assignments == i).any() else centroids[i]
                for i in range(self.k)
            ])

            # Check convergence
            if np.allclose(centroids, new_centroids):
                break

            centroids = new_centroids

        # Convert to hex and sort by prominence
        hex_colors = self._centroids_to_hex(centroids, assignments)
        hex_colors = self._sort_by_prominence(hex_colors, assignments)

        return hex_colors[:self.k]

    def _centroids_to_hex(self, centroids: np.ndarray, assignments: np.ndarray) -> List[str]:
        """Convert RGB centroids to hex colors"""
        hex_colors = []
        for i, centroid in enumerate(centroids):
            r, g, b = map(int, centroid)
            hex_color = f"#{r:02X}{g:02X}{b:02X}"
            hex_colors.append(hex_color)
        return hex_colors

    def _sort_by_prominence(self, hex_colors: List[str], assignments: np.ndarray) -> List[str]:
        """Sort colors by frequency in image"""
        counts = np.bincount(assignments, minlength=self.k)
        sorted_indices = np.argsort(-counts)
        return [hex_colors[i] for i in sorted_indices]
```

### 1.2 Frontend Streaming Component

```typescript
// frontend/src/components/ColorExtraction.tsx
import { useEffect, useState } from 'react';
import { useTokenGraphStore } from '@/store/tokenGraphStore';

interface ExtractedColor {
  hex: string;
  rgb: string;
  confidence: number;
}

export function ColorExtraction({ imageUrl: string }) {
  const [colors, setColors] = useState<ExtractedColor[]>([]);
  const [isExtracting, setIsExtracting] = useState(false);
  const addToken = useTokenGraphStore(s => s.addToken);

  useEffect(() => {
    extractColors();
  }, [imageUrl]);

  async function extractColors() {
    setIsExtracting(true);

    // Stream colors as they're extracted
    const response = await fetch('/api/v1/colors/extract-streaming', {
      method: 'POST',
      body: JSON.stringify({ image_base64: await imageToBase64(imageUrl) })
    });

    const reader = response.body?.getReader();
    if (!reader) return;

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const color = JSON.parse(line.slice(6)) as ExtractedColor;

          // Add to local state (real-time UI update)
          setColors(prev => [...prev, color]);

          // Add to TokenGraph
          addToken({
            id: `color/${colors.length.toString().padStart(2, '0')}`,
            type: 'COLOR',
            value: color.hex,
            attributes: {
              rgb: color.rgb,
              confidence: color.confidence
            }
          });
        }
      }
    }

    setIsExtracting(false);
  }

  return (
    <div className="color-grid">
      {colors.map((color, idx) => (
        <ColorSwatch
          key={idx}
          hex={color.hex}
          rgb={color.rgb}
          confidence={color.confidence}
        />
      ))}
    </div>
  );
}

function ColorSwatch({ hex, rgb, confidence }: ExtractedColor) {
  return (
    <div className="color-swatch">
      <div
        className="swatch-preview"
        style={{ backgroundColor: hex }}
      />
      <div className="swatch-info">
        <code>{hex}</code>
        <code>{rgb}</code>
        <span className="confidence">{Math.round(confidence * 100)}%</span>
      </div>
    </div>
  );
}
```

### 1.3 Backend Streaming Endpoint

```python
# backend/src/copy_that/interfaces/api/colors.py
from fastapi import APIRouter, Response
from fastapi.responses import StreamingResponse
import asyncio
import json
from copy_that.extractors.color.kmeans import ColorKMeans

router = APIRouter(prefix="/api/v1/colors")

@router.post("/extract-streaming")
async def extract_colors_streaming(request: dict):
    """Stream colors as they're extracted (Server-Sent Events)"""

    image_base64 = request.get("image_base64")
    image_array = base64_to_numpy(image_base64)

    async def stream_colors():
        kmeans = ColorKMeans(k=8)

        # Extract colors
        hex_colors = kmeans.extract(image_array)

        # Convert to RGB and send each color
        for i, hex_color in enumerate(hex_colors):
            color_data = {
                "hex": hex_color,
                "rgb": hex_to_rgb(hex_color),
                "confidence": 1.0 - (i * 0.05)  # Placeholder confidence
            }

            # SSE format
            yield f"data: {json.dumps(color_data)}\n\n"

            # Brief delay for streaming effect
            await asyncio.sleep(0.01)

    return StreamingResponse(
        stream_colors(),
        media_type="text/event-stream"
    )
```

---

## Phase 2: ML - Color Science Analysis

### 2.1 ColorAide Integration

```python
# backend/src/copy_that/extractors/color/color_utils.py
"""Color science utilities using ColorAide"""

import coloraide
from typing import Dict, Any

class ColorScience:
    """Comprehensive color analysis using ColorAide"""

    @staticmethod
    def analyze(hex_color: str) -> Dict[str, Any]:
        """Analyze a color comprehensively

        Returns:
        {
            "hex": "#FF5733",
            "rgb": "rgb(255, 87, 51)",
            "hsl": "hsl(9, 100%, 60%)",
            "is_neutral": False,
            "wcag_contrast_white": 3.5,
            "wcag_contrast_black": 8.2,
            "wcag_aa_text": True,
            "wcag_aaa_text": False,
            "harmony": "analogous",
            "temperature": "warm",
            "saturation": "vibrant",
            "lightness": "medium"
        }
        """
        color = coloraide.Color(hex_color)

        return {
            # Basic formats
            "hex": hex_color,
            "rgb": str(color),
            "hsl": color.convert("hsl").to_string(),
            "hsv": color.convert("hsv").to_string(),

            # Neutrality
            "is_neutral": ColorScience._is_neutral(color),

            # Accessibility
            "wcag_contrast_white": ColorScience._contrast(color, "#FFFFFF"),
            "wcag_contrast_black": ColorScience._contrast(color, "#000000"),
            "wcag_aa_text": ColorScience._is_wcag_aa_text(color),
            "wcag_aaa_text": ColorScience._is_wcag_aaa_text(color),
            "wcag_aa_large": ColorScience._is_wcag_aa_large(color),
            "wcag_aaa_large": ColorScience._is_wcag_aaa_large(color),

            # Color characteristics
            "harmony": ColorScience._detect_harmony(color),
            "temperature": ColorScience._detect_temperature(color),
            "saturation": ColorScience._detect_saturation(color),
            "lightness": ColorScience._detect_lightness(color),

            # Variants
            "tint": ColorScience._tint(hex_color, 50),
            "shade": ColorScience._shade(hex_color, 50),
            "tone": ColorScience._tone(hex_color, 50),
        }

    @staticmethod
    def _is_neutral(color: coloraide.Color) -> bool:
        """Is this a grayscale/neutral color?"""
        hsl = color.convert("hsl")
        return hsl["saturation"] < 5

    @staticmethod
    def _contrast(color1_hex: str, color2_hex: str) -> float:
        """Calculate WCAG contrast ratio"""
        c1 = coloraide.Color(color1_hex)
        c2 = coloraide.Color(color2_hex)
        lum1 = ColorScience._relative_luminance(c1)
        lum2 = ColorScience._relative_luminance(c2)
        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)
        return (lighter + 0.05) / (darker + 0.05)

    @staticmethod
    def _relative_luminance(color: coloraide.Color) -> float:
        """Calculate relative luminance for WCAG"""
        rgb = color.convert("srgb")
        r = ColorScience._linearize(rgb["red"])
        g = ColorScience._linearize(rgb["green"])
        b = ColorScience._linearize(rgb["blue"])
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    @staticmethod
    def _linearize(value: float) -> float:
        """Linearize RGB value for luminance calculation"""
        if value <= 0.03928:
            return value / 12.92
        return ((value + 0.055) / 1.055) ** 2.4

    @staticmethod
    def _is_wcag_aa_text(color: coloraide.Color) -> bool:
        """WCAG AA for normal text (4.5:1)"""
        return ColorScience._contrast(color.to_string(), "#FFFFFF") >= 4.5 or \
               ColorScience._contrast(color.to_string(), "#000000") >= 4.5

    @staticmethod
    def _is_wcag_aaa_text(color: coloraide.Color) -> bool:
        """WCAG AAA for normal text (7:1)"""
        return ColorScience._contrast(color.to_string(), "#FFFFFF") >= 7.0 or \
               ColorScience._contrast(color.to_string(), "#000000") >= 7.0

    @staticmethod
    def _is_wcag_aa_large(color: coloraide.Color) -> bool:
        """WCAG AA for large text (3:1)"""
        return ColorScience._contrast(color.to_string(), "#FFFFFF") >= 3.0 or \
               ColorScience._contrast(color.to_string(), "#000000") >= 3.0

    @staticmethod
    def _is_wcag_aaa_large(color: coloraide.Color) -> bool:
        """WCAG AAA for large text (4.5:1)"""
        return ColorScience._contrast(color.to_string(), "#FFFFFF") >= 4.5 or \
               ColorScience._contrast(color.to_string(), "#000000") >= 4.5

    @staticmethod
    def _detect_harmony(color: coloraide.Color) -> str:
        """Detect color harmony"""
        hsl = color.convert("hsl")
        hue = hsl["hue"]

        # Simplified harmony detection
        if 30 < hue < 60 or 210 < hue < 240:
            return "analogous"
        elif 170 < hue < 190 or 350 < hue < 10:
            return "complementary"
        else:
            return "triadic"

    @staticmethod
    def _detect_temperature(color: coloraide.Color) -> str:
        """Detect color temperature"""
        hsl = color.convert("hsl")
        hue = hsl["hue"]

        if 0 <= hue < 60 or hue >= 330:
            return "warm"
        elif 120 <= hue < 240:
            return "cool"
        else:
            return "neutral"

    @staticmethod
    def _detect_saturation(color: coloraide.Color) -> str:
        """Detect saturation level"""
        hsl = color.convert("hsl")
        sat = hsl["saturation"]

        if sat < 10:
            return "grayscale"
        elif sat < 30:
            return "muted"
        elif sat < 70:
            return "moderate"
        else:
            return "vibrant"

    @staticmethod
    def _detect_lightness(color: coloraide.Color) -> str:
        """Detect lightness"""
        hsl = color.convert("hsl")
        light = hsl["lightness"]

        if light < 25:
            return "very dark"
        elif light < 50:
            return "dark"
        elif light < 75:
            return "medium"
        else:
            return "light"

    @staticmethod
    def _tint(hex_color: str, amount: int) -> str:
        """Create a tint (add white)"""
        color = coloraide.Color(hex_color)
        white = coloraide.Color("#FFFFFF")
        blend = color.mix(white, amount / 100)
        return blend.convert("srgb").to_string(hex=True)

    @staticmethod
    def _shade(hex_color: str, amount: int) -> str:
        """Create a shade (add black)"""
        color = coloraide.Color(hex_color)
        black = coloraide.Color("#000000")
        blend = color.mix(black, amount / 100)
        return blend.convert("srgb").to_string(hex=True)

    @staticmethod
    def _tone(hex_color: str, amount: int) -> str:
        """Create a tone (add gray)"""
        color = coloraide.Color(hex_color)
        gray = coloraide.Color("#808080")
        blend = color.mix(gray, amount / 100)
        return blend.convert("srgb").to_string(hex=True)
```

---

## Phase 3: AI - Claude Semantic Analysis (Async)

```python
# backend/src/copy_that/extractors/color/ai_analyzer.py
"""AI-powered color analysis using Claude"""

import anthropic
import json
from typing import Dict, Any

class ColorAIAnalyzer:
    """Use Claude to understand color semantics and design intent"""

    def __init__(self):
        self.client = anthropic.Anthropic()

    async def analyze_palette(self, colors: list[str], context: str = "") -> Dict[str, Any]:
        """Analyze a color palette semantically

        Args:
            colors: List of hex color codes
            context: Optional context (e.g., "material design", "brand guidelines")

        Returns:
        {
            "palette_name": "Ocean Breeze",
            "design_intent": "Modern, calm, professional",
            "suggested_usage": {
                "#FF5733": "Primary action, calls-to-action",
                "#3498DB": "Secondary elements, links",
                ...
            },
            "accessibility_notes": "All colors meet WCAG AA for text",
            "design_patterns": ["Material Design 3", "Flat Design"]
        }
        """

        prompt = f"""Analyze this color palette and provide semantic insights:

Colors: {", ".join(colors)}
Context: {context or "General UI design"}

Provide:
1. Palette name
2. Design intent (mood, style, character)
3. Suggested usage for each color
4. Accessibility notes
5. Matching design patterns

Format as JSON."""

        message = await self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse response
        response_text = message.content[0].text
        try:
            return json.loads(response_text)
        except:
            # Fallback if not valid JSON
            return {
                "palette_name": "Custom Palette",
                "design_intent": response_text,
                "suggested_usage": {},
                "accessibility_notes": "",
                "design_patterns": []
            }

    async def suggest_naming(self, colors: list[str]) -> Dict[str, list[str]]:
        """Suggest semantic names for colors"""

        prompt = f"""Suggest 5 semantic names for each color that would work in a design system:

Colors: {json.dumps(dict(enumerate(colors)))}

Format: {{"#RRGGBB": ["name1", "name2", "name3", "name4", "name5"]}}"""

        message = await self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text
        try:
            return json.loads(response_text)
        except:
            return {color: ["color"] for color in colors}
```

---

## Phase 4: React Component Generation

### 4.1 Color System Component (Modular, Extensible)

```typescript
// frontend/src/components/ColorSystem/ColorSystem.tsx
/**
 * ColorSystem: Modular, extensible color palette display and management
 *
 * Extensibility:
 * - Add new display modes by extending ColorDisplay
 * - Add new analysis tools by extending ColorAnalyzer
 * - Add new export formats by extending ColorExporter
 */

import React, { useMemo } from 'react';
import { ColorToken } from '@/types/tokens';
import { useTokenGraphStore } from '@/store/tokenGraphStore';

// Display modes
import ColorGrid from './displays/ColorGrid';
import ColorWheel from './displays/ColorWheel';
import ColorHierarchy from './displays/ColorHierarchy';

// Analysis tools
import AccessibilityAnalyzer from './analyzers/AccessibilityAnalyzer';
import HarmonyAnalyzer from './analyzers/HarmonyAnalyzer';
import ContrastAnalyzer from './analyzers/ContrastAnalyzer';

// Export formats
import W3CExport from './exporters/W3CExport';
import CSSVariablesExport from './exporters/CSSVariablesExport';
import TailwindExport from './exporters/TailwindExport';

type DisplayMode = 'grid' | 'wheel' | 'hierarchy';
type AnalysisMode = 'accessibility' | 'harmony' | 'contrast';
type ExportFormat = 'w3c' | 'css' | 'tailwind';

interface ColorSystemProps {
  displayMode?: DisplayMode;
  analysisMode?: AnalysisMode;
  exportFormat?: ExportFormat;
  onExport?: (code: string, format: ExportFormat) => void;
}

export function ColorSystem({
  displayMode = 'grid',
  analysisMode = 'accessibility',
  exportFormat = 'w3c',
  onExport
}: ColorSystemProps) {
  const colors = useTokenGraphStore(s =>
    s.tokens.values()
      .filter(t => t.type === 'COLOR')
      .toArray() as ColorToken[]
  );

  // Render appropriate display mode
  const renderDisplay = () => {
    switch (displayMode) {
      case 'wheel':
        return <ColorWheel colors={colors} />;
      case 'hierarchy':
        return <ColorHierarchy colors={colors} />;
      default:
        return <ColorGrid colors={colors} />;
    }
  };

  // Render appropriate analyzer
  const renderAnalyzer = () => {
    switch (analysisMode) {
      case 'harmony':
        return <HarmonyAnalyzer colors={colors} />;
      case 'contrast':
        return <ContrastAnalyzer colors={colors} />;
      default:
        return <AccessibilityAnalyzer colors={colors} />;
    }
  };

  // Render appropriate exporter
  const renderExporter = () => {
    switch (exportFormat) {
      case 'css':
        return <CSSVariablesExport colors={colors} onExport={onExport} />;
      case 'tailwind':
        return <TailwindExport colors={colors} onExport={onExport} />;
      default:
        return <W3CExport colors={colors} onExport={onExport} />;
    }
  };

  return (
    <div className="color-system">
      <section className="display-section">
        {renderDisplay()}
      </section>

      <section className="analysis-section">
        {renderAnalyzer()}
      </section>

      <section className="export-section">
        {renderExporter()}
      </section>
    </div>
  );
}

export default ColorSystem;
```

### 4.2 Base Components (Extensible Abstractions)

```typescript
// frontend/src/components/ColorSystem/base/ColorDisplay.tsx
/**
 * Base class for color display modes
 * Extend this to add new visualization types
 */

import { ColorToken } from '@/types/tokens';

export abstract class ColorDisplay {
  abstract render(colors: ColorToken[]): React.ReactNode;
  abstract getName(): string;

  // Common utilities
  protected sortByLuminance(colors: ColorToken[]): ColorToken[] {
    return [...colors].sort((a, b) => {
      const lumA = this.getLuminance(a.value);
      const lumB = this.getLuminance(b.value);
      return lumA - lumB;
    });
  }

  protected getLuminance(hex: string): number {
    const rgb = this.hexToRgb(hex);
    const r = rgb.r / 255;
    const g = rgb.g / 255;
    const b = rgb.b / 255;

    const rs = r <= 0.03928 ? r / 12.92 : Math.pow((r + 0.055) / 1.055, 2.4);
    const gs = g <= 0.03928 ? g / 12.92 : Math.pow((g + 0.055) / 1.055, 2.4);
    const bs = b <= 0.03928 ? b / 12.92 : Math.pow((b + 0.055) / 1.055, 2.4);

    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
  }

  protected hexToRgb(hex: string): { r: number; g: number; b: number } {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : { r: 0, g: 0, b: 0 };
  }
}

// frontend/src/components/ColorSystem/displays/ColorGrid.tsx
import React from 'react';
import { ColorDisplay } from '../base/ColorDisplay';
import { ColorToken } from '@/types/tokens';

export class ColorGridImpl extends ColorDisplay {
  getName(): string {
    return 'Grid View';
  }

  render(colors: ColorToken[]): React.ReactNode {
    const sorted = this.sortByLuminance(colors);

    return (
      <div className="color-grid">
        {sorted.map((color) => (
          <div key={color.id} className="color-card">
            <div
              className="color-preview"
              style={{ backgroundColor: color.value }}
            />
            <div className="color-details">
              <code className="hex">{color.value}</code>
              <span className="name">{color.id}</span>
              {color.attributes?.confidence && (
                <span className="confidence">
                  {Math.round(color.attributes.confidence * 100)}%
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    );
  }
}

function ColorGrid({ colors }: { colors: ColorToken[] }) {
  const display = new ColorGridImpl();
  return <>{display.render(colors)}</>;
}

export default ColorGrid;
```

### 4.3 Exporters (Extensible Code Generation)

```typescript
// frontend/src/components/ColorSystem/base/ColorExporter.tsx
/**
 * Base class for exporting color systems
 * Extend to add new export formats
 */

import { ColorToken } from '@/types/tokens';

export abstract class ColorExporter {
  abstract export(colors: ColorToken[]): string;
  abstract getName(): string;
  abstract getFileExtension(): string;

  protected formatColorName(colorId: string): string {
    // Convert "color/primary-dark" to "primaryDark"
    return colorId
      .replace(/^color\//, '')
      .split('-')
      .map((part, i) => i === 0 ? part : part.charAt(0).toUpperCase() + part.slice(1))
      .join('');
  }
}

// frontend/src/components/ColorSystem/exporters/W3CExport.tsx
import React from 'react';
import { ColorExporter } from '../base/ColorExporter';
import { ColorToken } from '@/types/tokens';

class W3CExporter extends ColorExporter {
  getName(): string {
    return 'W3C Design Tokens';
  }

  getFileExtension(): string {
    return 'json';
  }

  export(colors: ColorToken[]): string {
    const tokens: any = {
      $schema: 'https://tokens.studio/json-schema/draft-only/index.json',
      $version: '1.0.0',
      color: {}
    };

    for (const color of colors) {
      const name = this.formatColorName(color.id);
      tokens.color[name] = {
        $type: 'color',
        $value: color.value,
        $description: color.attributes?.harmony || 'Extracted color'
      };
    }

    return JSON.stringify(tokens, null, 2);
  }
}

export function W3CExportComponent({
  colors,
  onExport
}: {
  colors: ColorToken[];
  onExport?: (code: string, format: string) => void;
}) {
  const exporter = new W3CExporter();

  const handleExport = () => {
    const code = exporter.export(colors);
    onExport?.(code, 'w3c');

    // Download
    const blob = new Blob([code], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `colors.${exporter.getFileExtension()}`;
    a.click();
  };

  return (
    <button onClick={handleExport}>
      Export {exporter.getName()}
    </button>
  );
}

// frontend/src/components/ColorSystem/exporters/CSSVariablesExport.tsx
class CSSVariablesExporter extends ColorExporter {
  getName(): string {
    return 'CSS Variables';
  }

  getFileExtension(): string {
    return 'css';
  }

  export(colors: ColorToken[]): string {
    let css = ':root {\n';

    for (const color of colors) {
      const name = this.formatColorName(color.id);
      css += `  --color-${name}: ${color.value};\n`;
    }

    css += '}\n';
    return css;
  }
}

// frontend/src/components/ColorSystem/exporters/TailwindExport.tsx
class TailwindExporter extends ColorExporter {
  getName(): string {
    return 'Tailwind Config';
  }

  getFileExtension(): string {
    return 'js';
  }

  export(colors: ColorToken[]): string {
    const colors_obj: any = {};

    for (const color of colors) {
      const name = this.formatColorName(color.id);
      colors_obj[name] = color.value;
    }

    return `module.exports = {
  theme: {
    extend: {
      colors: ${JSON.stringify(colors_obj, null, 8)}
    }
  }
}`;
  }
}
```

---

## Implementation Timeline

### Week 1: CV Extraction
- [ ] K-means implementation
- [ ] Frontend streaming UI
- [ ] Backend SSE endpoint
- [ ] Real-time color display

### Week 2: ML Analysis
- [ ] ColorAide integration
- [ ] Accessibility metrics
- [ ] Color science calculations
- [ ] Frontend analysis display

### Week 3: AI Enrichment (Optional)
- [ ] Claude API integration
- [ ] Semantic naming
- [ ] Design intent detection
- [ ] Async WebSocket updates

### Week 4: React Generation
- [ ] Modular component architecture
- [ ] Multiple export formats (W3C, CSS, Tailwind)
- [ ] Color visualization modes (grid, wheel, hierarchy)
- [ ] End-to-end testing

---

## Testing Strategy

```python
# backend/tests/test_color_pipeline.py
import pytest
from copy_that.extractors.color.kmeans import ColorKMeans
from copy_that.extractors.color.color_utils import ColorScience

@pytest.mark.asyncio
async def test_kmeans_extraction():
    kmeans = ColorKMeans(k=8)
    # Test with sample image
    colors = kmeans.extract(sample_image)
    assert len(colors) == 8
    assert all(c.startswith('#') for c in colors)

@pytest.mark.asyncio
async def test_color_science_analysis():
    analysis = ColorScience.analyze("#FF5733")
    assert analysis["hex"] == "#FF5733"
    assert "wcag_contrast_white" in analysis
    assert analysis["temperature"] in ["warm", "cool", "neutral"]

@pytest.mark.asyncio
async def test_ai_semantic_naming():
    analyzer = ColorAIAnalyzer()
    names = await analyzer.suggest_naming(["#FF5733", "#3498DB"])
    assert "#FF5733" in names
    assert len(names["#FF5733"]) == 5
```

```typescript
// frontend/src/components/__tests__/ColorSystem.test.tsx
import { render, screen } from '@testing-library/react';
import { ColorSystem } from '../ColorSystem';
import { useTokenGraphStore } from '@/store/tokenGraphStore';

describe('ColorSystem', () => {
  it('renders color grid', () => {
    // Setup
    const colors = [
      { id: 'color/primary', type: 'COLOR', value: '#FF5733' },
      { id: 'color/secondary', type: 'COLOR', value: '#3498DB' }
    ];

    // Mock store
    useTokenGraphStore.setState({ tokens: new Map(colors.map(c => [c.id, c])) });

    // Render
    render(<ColorSystem displayMode="grid" />);

    // Assert
    expect(screen.getByText('#FF5733')).toBeInTheDocument();
    expect(screen.getByText('#3498DB')).toBeInTheDocument();
  });

  it('exports W3C format', async () => {
    const onExport = jest.fn();
    render(<ColorSystem exportFormat="w3c" onExport={onExport} />);

    fireEvent.click(screen.getByText('Export W3C Design Tokens'));

    expect(onExport).toHaveBeenCalled();
    const exported = onExport.mock.calls[0][0];
    expect(JSON.parse(exported)).toHaveProperty('color');
  });
});
```

---

## Summary

This pipeline delivers:
- ✅ **Fast CV extraction** (50ms, frontend)
- ✅ **Comprehensive ML analysis** (color science, accessibility)
- ✅ **Optional AI enrichment** (semantic naming, async)
- ✅ **Modular React components** (extensible, reusable)
- ✅ **Multiple export formats** (W3C, CSS, Tailwind, more)

You can build this in 3-4 weeks with production-ready code.

# OpenAI Vision Integration Guide

Copy That integrates OpenAI's Vision API (GPT-4 Vision) to provide intelligent, semantic understanding of UI designs. This enhances traditional computer vision with AI-powered analysis.

## Features

### 1. Design Style Analysis
Extract comprehensive style information from UI references:
- Design system identification (Material Design, iOS, Fluent, etc.)
- Color palette description with semantic meaning
- Typography hierarchy and patterns
- Spacing and layout systems
- Corner radius and shape language
- Shadow and depth strategies
- Material properties and visual effects

### 2. Component Identification
Automatically identify and classify UI components:
- Component types (buttons, inputs, cards, etc.)
- Visual states (default, hover, active, disabled)
- Variants (primary, secondary, ghost, etc.)
- Size classifications
- Special properties (icons, badges, animations)

### 3. Design Token Extraction
Extract specific design token values:
- Color hex codes for all palette colors
- Spacing measurements and base units
- Typography specifications (sizes, weights, families)
- Effect values (shadows, borders, opacity)

### 4. Component Variation Suggestions
AI-powered recommendations for component variations:
- Size variations with exact dimensions
- Color schemes that match the style
- State variations (hover, active, etc.)
- Style variants (outlined, filled, ghost)

### 5. Design Comparison
Compare multiple design references:
- Identify visual similarities and differences
- Assess design system compatibility
- Recommendations for unified approach

## Setup

### 1. Install Dependencies

```bash
pip install openai python-dotenv
```

### 2. Configure API Key

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=your_api_key_here
```

### 3. Optional Configuration

You can customize the OpenAI settings in your `.env` file:

```env
# Model selection
OPENAI_MODEL=gpt-4o
OPENAI_VISION_MODEL=gpt-4o

# API parameters
OPENAI_MAX_TOKENS=4096
OPENAI_TEMPERATURE=0.7
```

## Usage Examples

### Quick Analysis

```python
from src.openai_vision import analyze_ui_with_vision

# Run comprehensive analysis
results = analyze_ui_with_vision('path/to/reference-ui.png')

print(results['style_analysis'])
print(results['components'])
print(results['design_tokens'])
```

### Detailed Analysis

```python
from src.openai_vision import OpenAIVisionAnalyzer

# Initialize analyzer
analyzer = OpenAIVisionAnalyzer()

# Analyze design style
style = analyzer.analyze_design_style('reference.png')
print(f"Design Style: {style['design_style']}")
print(f"Color Palette: {style['color_palette']}")

# Identify components
components = analyzer.identify_components('reference.png')
for comp in components['components']:
    print(f"- {comp['type']} ({comp['variant']}, {comp['state']})")

# Extract design tokens
tokens = analyzer.extract_design_tokens('reference.png')
print(f"Primary Color: {tokens['colors']['primary']}")
print(f"Base Unit: {tokens['spacing']['base_unit']}")

# Get variation suggestions
variations = analyzer.suggest_component_variations('reference.png', 'button')
print(f"Suggested variations: {variations}")
```

### Compare Multiple Designs

```python
from src.openai_vision import OpenAIVisionAnalyzer

analyzer = OpenAIVisionAnalyzer()

# Compare two designs
comparison = analyzer.compare_designs('design-v1.png', 'design-v2.png')

print(f"Compatibility Score: {comparison['compatibility_score']}/100")
print(f"Similarities: {comparison['similarities']}")
print(f"Differences: {comparison['differences']}")
print(f"Recommendations: {comparison['recommendations']}")
```

### Integrated with Image Processor

```python
from src.image_processor import analyze_image

# Run comprehensive analysis (CV + AI)
results = analyze_image(
    'reference.png',
    output_path='analysis-results.json',
    use_openai=True
)

# Access CV results
print(f"Detected shapes: {results['shapes']['total_shapes']}")
print(f"Base spacing unit: {results['spacing']['estimated_base_unit']}")

# Access AI results
print(f"AI design style: {results['ai_analysis']['style_analysis']}")
print(f"AI components: {results['ai_analysis']['components']}")
```

## Integration with Copy That Pipeline

The OpenAI Vision integration enhances the main Copy That pipeline:

```python
from copy_that_pipeline import CopyThatPipeline

# Initialize pipeline with OpenAI
pipeline = CopyThatPipeline(use_openai=True)

# Process reference image
design_system = pipeline.generate(
    'reference.png',
    output_dir='output/my-design-system'
)

# Results include both CV and AI analysis
print(design_system.visual_dna)  # Enhanced with AI insights
print(design_system.components)  # AI-identified components
print(design_system.tokens)      # AI-extracted tokens
```

## API Response Format

### Style Analysis Response

```json
{
  "design_style": "Material Design 3.0",
  "color_palette": {
    "primary": "#6750A4",
    "secondary": "#625B71",
    "accent": "#7D5260"
  },
  "typography": {
    "font_family": "Roboto",
    "heading_weight": 500,
    "body_weight": 400
  },
  "spacing": {
    "base_unit": "8px",
    "padding_pattern": "16px horizontal, 12px vertical"
  },
  "corners": "rounded (8px)",
  "shadows": "subtle elevation (2dp)",
  "materials": "matte with slight gradient",
  "hierarchy": "size and color based",
  "principles": ["minimalism", "clarity", "consistency"]
}
```

### Component Identification Response

```json
{
  "components": [
    {
      "type": "button",
      "state": "default",
      "variant": "primary",
      "size": "medium",
      "location": "center",
      "properties": ["rounded corners", "drop shadow", "icon"]
    },
    {
      "type": "input",
      "state": "focus",
      "variant": "outlined",
      "size": "medium",
      "location": "top-center",
      "properties": ["label", "helper text", "border accent"]
    }
  ]
}
```

### Design Tokens Response

```json
{
  "colors": {
    "primary": "#6750A4",
    "secondary": "#625B71",
    "background": "#FFFBFE",
    "surface": "#F7F2FA",
    "error": "#B3261E"
  },
  "spacing": {
    "base_unit": "8px",
    "xs": "4px",
    "sm": "8px",
    "md": "16px",
    "lg": "24px",
    "xl": "32px"
  },
  "typography": {
    "font_family": "Roboto",
    "sizes": {
      "h1": "32px",
      "h2": "24px",
      "body": "16px",
      "caption": "12px"
    },
    "weights": {
      "regular": 400,
      "medium": 500,
      "bold": 700
    }
  },
  "effects": {
    "border_radius": {
      "small": "4px",
      "medium": "8px",
      "large": "16px"
    },
    "shadows": [
      {
        "level": 1,
        "value": "0 1px 2px rgba(0,0,0,0.1)"
      },
      {
        "level": 2,
        "value": "0 2px 4px rgba(0,0,0,0.15)"
      }
    ]
  }
}
```

## Best Practices

### 1. Image Quality
- Use high-resolution reference images (1920px+ width recommended)
- Ensure good contrast and clarity
- Include multiple components in reference for better analysis

### 2. API Usage
- The Vision API has usage costs - monitor your usage
- Cache results when possible to avoid redundant calls
- Use batch analysis for multiple images

### 3. Combining CV and AI
- Use CV for precise measurements (pixels, exact colors)
- Use AI for semantic understanding (intent, style names)
- Cross-validate findings between both approaches

### 4. Error Handling
- Always handle API errors gracefully
- Provide fallback to CV-only analysis if API fails
- Validate and sanitize AI responses before using

## Troubleshooting

### API Key Issues

**Problem**: "OpenAI API key not found"

**Solution**:
```bash
# Verify .env file exists
ls -la .env

# Check if key is set
cat .env | grep OPENAI_API_KEY

# Reload environment
source .env
```

### Rate Limiting

**Problem**: "Rate limit exceeded"

**Solution**:
- Add delays between API calls
- Implement exponential backoff
- Cache results to reduce calls

```python
import time

analyzer = OpenAIVisionAnalyzer()

for image in images:
    result = analyzer.analyze_design_style(image)
    time.sleep(1)  # Rate limiting delay
```

### JSON Parsing Errors

**Problem**: AI returns non-JSON response

**Solution**:
The integration automatically handles this by:
1. Extracting JSON from markdown code blocks
2. Falling back to `raw_analysis` field if JSON parsing fails

```python
result = analyzer.analyze_design_style('image.png')

if 'raw_analysis' in result:
    print("Note: Response was not structured JSON")
    print(result['raw_analysis'])
else:
    # Normal JSON response
    print(result['design_style'])
```

## Cost Considerations

OpenAI Vision API pricing (as of 2025):
- **GPT-4 Vision**: ~$0.01-0.03 per image depending on detail level
- Comprehensive analysis uses 1-3 API calls per image
- Budget accordingly for large batch processing

**Cost Optimization Tips**:
1. Cache analysis results
2. Use lower detail level for initial scans
3. Only use AI for images that need semantic understanding
4. Batch related questions into single API calls

## Advanced Usage

### Custom Prompts

You can customize the analysis prompts for specific needs:

```python
from src.openai_vision import OpenAIVisionAnalyzer

analyzer = OpenAIVisionAnalyzer()

custom_prompt = """
Analyze this UI specifically for:
1. Accessibility features (contrast ratios, focus indicators)
2. Mobile responsiveness indicators
3. Animation and interaction patterns
Return as JSON.
"""

response = analyzer.client.chat.completions.create(
    model=analyzer.model,
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": custom_prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{analyzer.encode_image('ui.png')}"
                    }
                }
            ]
        }
    ],
    max_tokens=analyzer.max_tokens
)
```

### Batch Processing

```python
from pathlib import Path
from src.openai_vision import OpenAIVisionAnalyzer
import time

analyzer = OpenAIVisionAnalyzer()
results = {}

reference_dir = Path('references/')
for image_path in reference_dir.glob('*.png'):
    print(f"Analyzing {image_path.name}...")

    results[image_path.name] = analyzer.comprehensive_analysis(image_path)
    time.sleep(1)  # Rate limiting

# Save batch results
import json
with open('batch_analysis.json', 'w') as f:
    json.dump(results, f, indent=2)
```

## Future Enhancements

Planned improvements to OpenAI Vision integration:
- [ ] Streaming responses for real-time feedback
- [ ] Multi-modal analysis (combining screenshots + code)
- [ ] Fine-tuned models for specific design systems
- [ ] Automated component annotation
- [ ] Design critique and improvement suggestions

## Support

For issues related to:
- **OpenAI API**: Check [OpenAI documentation](https://platform.openai.com/docs)
- **Copy That integration**: Open an issue on GitHub
- **Usage examples**: See `examples/openai_vision_examples.py`

---

**Enhance your design analysis with AI-powered insights!**

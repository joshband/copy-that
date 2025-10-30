# Copy That

**A Generative UI Design System Engine**

Transform reference images into complete, production-ready design systems with parametric component generation and style-aware variations.

## Overview

Copy That reimagines UI design tooling by shifting from extraction to generation. Instead of cutting out existing UI elements, it analyzes visual styles and generates entirely new, consistent components following the discovered design language.

### Key Transformation

- **Traditional Tools**: Reference Image → Extract existing elements
- **Copy That**: Reference Image → Analyze visual DNA → Generate NEW elements

## Features

- **Visual DNA Extraction**: Analyzes color relationships, shape language, spacing rhythms, material properties
- **OpenAI Vision Integration**: Leverages GPT-4 Vision for semantic understanding and intelligent design analysis
- **Parametric Generation**: Creates new components using extracted style parameters
- **Variation Synthesis**: Generates size, color, theme, and state variations
- **Design System Builder**: Produces complete component libraries with tokens and documentation
- **Style Consistency**: Validates visual harmony across generated assets
- **AI-Powered Insights**: Component identification, design token extraction, and style comparison

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up your OpenAI API key (for AI-powered analysis)
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Generate a design system from reference image
python copy_that_pipeline.py your-reference-ui.png

# View results
open output/design-system/
```

## Documentation

- [Quick Start Guide](docs/QUICK_START.md) - Get started in minutes
- [Design Documentation](docs/DESIGN.md) - Architecture and technical approach
- [Implementation Guide](docs/IMPLEMENTATION.md) - Development details
- [OpenAI Vision Guide](docs/OPENAI_VISION.md) - AI-powered analysis features
- [Brand Guide](BRAND_GUIDE.md) - Visual identity and design principles

## Project Structure

```
copy-that/
├── src/                    # Source code
│   ├── visual_dna.py      # Style analysis engine
│   ├── parametric_generator.py
│   ├── variation_engine.py
│   └── design_system_builder.py
├── tests/                  # Test suite
├── docs/                   # Documentation
├── examples/               # Example reference images
└── output/                 # Generated design systems
```

## Technology Stack

- **Computer Vision**: OpenCV, scikit-image
- **AI Integration**: OpenAI Vision API (GPT-4 Vision)
- **Machine Learning**: PyTorch, Transformers
- **Generation**: SVG, Cairo, Pillow
- **Advanced (Optional)**: Stable Diffusion, ControlNet, StyleGAN2

## Use Cases

1. **Design System Generation**: Transform mockups into complete component libraries
2. **Style Exploration**: Compare multiple design directions by analyzing different references
3. **Brand Consistency**: Generate new components that match existing design language
4. **Rapid Prototyping**: Quickly create variations for A/B testing

## Requirements

- Python 3.8+
- 4GB+ RAM
- OpenAI API key (for AI-powered features)
- GPU recommended for neural style transfer (optional)

## License

[License type to be determined]

## Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Project Status

🚧 **In Development** - Copy That is currently under active development.

---

**Copy That transforms inspiration into implementation. 🎨 → 🚀**

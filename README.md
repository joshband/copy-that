# Copy That

**A Generative UI Design System Engine**

Transform reference images into complete, production-ready design systems with parametric component generation and style-aware variations.

## Overview

Copy That (Phase 13) reimagines UI design tooling by shifting from extraction to generation. Instead of cutting out existing UI elements, it analyzes visual styles and generates entirely new, consistent components following the discovered design language.

### Key Transformation

- **Traditional Tools**: Reference Image → Extract existing elements
- **Copy That**: Reference Image → Analyze visual DNA → Generate NEW elements

## Features

- **Visual DNA Extraction**: Analyzes color relationships, shape language, spacing rhythms, material properties
- **Parametric Generation**: Creates new components using extracted style parameters
- **Variation Synthesis**: Generates size, color, theme, and state variations
- **Design System Builder**: Produces complete component libraries with tokens and documentation
- **Style Consistency**: Validates visual harmony across generated assets

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Generate a design system from reference image
python phase13_pipeline.py your-reference-ui.png

# View results
open output-phase13/design-system/
```

## Documentation

- [Quick Start Guide](PHASE_13_QUICK_START.md) - Get started in minutes
- [Design Documentation](PHASE_13_DESIGN.md) - Architecture and technical approach
- [Implementation Guide](PHASE_13_IMPLEMENTATION.md) - Development details
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
└── output-phase13/         # Generated design systems
```

## Technology Stack

- **Computer Vision**: OpenCV, scikit-image
- **Machine Learning**: PyTorch, CLIP, Transformers
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
- GPU recommended for neural style transfer (optional)

## License

[License type to be determined]

## Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Project Status

🚧 **In Development** - Phase 13 is currently under active development.

---

**Phase 13 transforms inspiration into implementation. 🎨 → 🚀**

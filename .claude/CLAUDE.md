# Copy That - Claude Code Project Instructions

## Project Context

Copy That is a full-stack web application and generative UI design system engine that analyzes reference images and generates complete, production-ready design systems.

### Project Type
- **Full-stack web application**
- Python backend with computer vision and AI capabilities
- Frontend (to be implemented)
- OpenAI Vision API integration for semantic design analysis

## Key Principles

1. **Generation over Extraction**: We create NEW components, not extract existing ones
2. **Style-Aware**: All generation follows extracted visual DNA and style rules
3. **Consistency First**: Generated components must maintain visual harmony
4. **Production Quality**: Output should be ready for use in real products
5. **AI-Enhanced**: Combines traditional CV with OpenAI Vision for semantic understanding

## Project Structure

- `src/` - Core implementation modules (Python backend)
- `tests/` - Test suite for all components
- `docs/` - Architecture and design documentation
  - `DESIGN.md` - Technical architecture
  - `QUICK_START.md` - Quick start guide
  - `OPENAI_VISION.md` - AI integration guide
  - `DESIGN_SYSTEM_STRUCTURE.md` - Output format specification
  - `BRAND_GUIDE.md` - Visual identity
- `examples/` - Reference images for testing
- `.env` - Environment configuration (OpenAI API key)

## Development Guidelines

### When Working on Style Analysis
- Focus on extracting patterns and relationships, not objects
- Visual DNA should capture the "why" behind design choices
- Style rules must be actionable for generation

### When Working on Generation
- Use parametric approaches for consistency
- Always validate against extracted style rules
- Generate variations systematically (size, color, theme, state)

### When Adding Features
- Prioritize quality over quantity
- Test with diverse reference images
- Document new style parameters in visual DNA schema

## Testing Approach

- Unit tests for each module
- Integration tests for full pipeline
- Visual regression tests for generated components
- Style consistency validation

## Technology Preferences

- Python 3.8+ for main codebase
- PyTorch for ML components
- OpenCV for computer vision
- OpenAI Vision API for semantic analysis
- python-dotenv for environment management
- SVG for vector output

## OpenAI Integration

- OpenAI API key required for AI-powered features
- Configure via `.env` file with `OPENAI_API_KEY`
- See `docs/OPENAI_VISION.md` for full integration guide
- Combines traditional CV with GPT-4 Vision for enhanced analysis
- Used for: design style identification, component detection, token extraction

## Best Practices

- Always validate OpenAI API responses before using
- Cache AI analysis results to reduce API costs
- Provide fallback to CV-only analysis if API fails
- Cross-validate CV and AI findings for accuracy
- Document all design decisions in component metadata

## Implementation Status

**Status**: Initial Setup (0.1.0)
- ✅ Project structure created
- ✅ Documentation framework established
- ✅ OpenAI integration documented
- ⏳ Core modules to be implemented
- ⏳ Frontend to be developed

## Remember

- This is a computer vision agent project - leverage CV expertise
- Reference the design docs (DESIGN.md) for architecture decisions
- Use OpenAI Vision to enhance, not replace, traditional CV analysis
- Follow industry-standard design system structure (see DESIGN_SYSTEM_STRUCTURE.md)

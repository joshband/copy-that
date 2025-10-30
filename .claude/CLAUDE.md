# Copy That - Claude Code Project Instructions

## Project Context

Copy That is a generative UI design system engine that analyzes reference images and generates complete, production-ready design systems. This is Phase 13 of the UI Layer Decomposer evolution.

## Key Principles

1. **Generation over Extraction**: We create NEW components, not extract existing ones
2. **Style-Aware**: All generation follows extracted visual DNA and style rules
3. **Consistency First**: Generated components must maintain visual harmony
4. **Production Quality**: Output should be ready for use in real products

## Project Structure

- `src/` - Core implementation modules
- `tests/` - Test suite for all components
- `docs/` - Architecture and design documentation
- `examples/` - Reference images for testing
- `PHASE_13_*.md` - Design and implementation guides

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
- SVG for vector output

## Remember

- This is a computer vision agent project - leverage CV expertise
- Reference the design docs (PHASE_13_DESIGN.md) for architecture decisions
- Maintain backward compatibility with existing Phase 12 infrastructure where possible

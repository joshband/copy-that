# Session 5: Generator Pipeline

**Can Run in Parallel with Sessions 1-4**

## Branch
```bash
git checkout -b claude/generator-pipeline-{SESSION_ID}
```

## Mission
Implement GeneratorAgent: transform tokens to W3C, CSS, React, Tailwind formats.

## Owned Files

Create these files:
- `src/copy_that/pipeline/generator/__init__.py`
- `src/copy_that/pipeline/generator/agent.py`
- `src/copy_that/pipeline/generator/templates/w3c.j2`
- `src/copy_that/pipeline/generator/templates/css.j2`
- `src/copy_that/pipeline/generator/templates/react.j2`
- `src/copy_that/pipeline/generator/templates/tailwind.j2`
- `tests/unit/pipeline/generator/test_agent.py`
- `tests/unit/pipeline/generator/test_formats.py`

## Priority Tasks

### IMMEDIATE

#### 1. GeneratorAgent (Configurable by Format)
- Formats: w3c, css, scss, react, tailwind
- Use Jinja2 templates
- **TESTS FIRST**

#### 2. Core Templates
- W3C Design Tokens JSON
- CSS Custom Properties
- React theme object
- **TESTS FIRST**

### HIGH

#### 3. Additional Formats
- Tailwind config
- Figma tokens

#### 4. Interactive HTML Demo
- Visual preview of tokens

## Key Principle
**Single agent handles ALL output formats via configuration.**

## Exit Criteria
- [ ] Single agent handles all formats
- [ ] Jinja2 templates work correctly
- [ ] All tests written BEFORE implementation
- [ ] 95%+ coverage

## Commit Message
```
feat: implement generator pipeline with multi-format output
```

## Auto-Execute
1. Create branch
2. Write tests
3. Implement
4. Commit and push

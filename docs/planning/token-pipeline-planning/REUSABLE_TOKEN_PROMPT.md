# Reusable Claude Code Prompt for New Token Types

**Version:** 1.0 | **Date:** 2025-11-22 | **Purpose:** Template for creating new token pipelines

Use this prompt with Claude Code (web or CLI) to generate complete planning documentation and reference implementation for new token types like typography, shadow, border, artistic style, depth, etc.

---

## How to Use

1. Copy the prompt below
2. Replace `[TOKEN_TYPE]` with your token type (e.g., "typography", "shadow", "border")
3. Fill in the `[CUSTOMIZATION]` sections
4. Paste into Claude Code web or CLI
5. Claude will generate complete planning documentation

---

## The Prompt

```markdown
# Create [TOKEN_TYPE] Token Pipeline Planning

I need you to create a complete planning documentation package for a **[TOKEN_TYPE] token pipeline** for the Copy That platform.

## Context

Copy That is a design token extraction platform. It currently has:
- A working **color token pipeline** with AI extraction, aggregation, and export
- A planned **spacing token pipeline** (see reference docs below)
- A **token factory abstraction** for creating new token types

The new [TOKEN_TYPE] token should follow the exact same patterns.

## Reference Documentation Location

Look at these existing documents in the codebase for patterns to follow:

```
docs/planning/token-pipeline-planning/
├── SPACING_TOKEN_PIPELINE_PLANNING.md    # Pattern for technical spec
├── TOKEN_FACTORY_PLANNING.md             # Abstract base classes
├── SDLC_ATOMIC_TASKS.md                  # Pattern for task breakdown
├── IMPLEMENTATION_ROADMAP.md             # Pattern for roadmap
└── reference-implementation/             # Code patterns
    └── src/
        ├── models/spacing_token.py
        ├── extractors/spacing_extractor.py
        └── aggregators/spacing_aggregator.py
```

## Token Type Specification

### Token Name
**[TOKEN_TYPE]** (e.g., typography, shadow, border, opacity, animation)

### Core Properties
[List the core properties this token type needs. Examples:]

For typography:
- font_family: str
- font_size: int (px)
- font_weight: int (100-900)
- line_height: float
- letter_spacing: float

For shadow:
- offset_x: int (px)
- offset_y: int (px)
- blur_radius: int (px)
- spread_radius: int (px)
- color: str (hex)
- opacity: float

For border:
- width: int (px)
- style: str (solid/dashed/dotted)
- color: str (hex)
- radius: int (px)

[CUSTOMIZE: Add your token's properties here]

### Computed Properties
[List derived properties to compute. Examples:]

For typography:
- font_size_rem (from px)
- readability_score
- suggested_use (heading/body/caption)

For shadow:
- elevation_level (1-5)
- css_box_shadow string
- is_soft/is_harsh

[CUSTOMIZE: Add computed properties here]

### Deduplication Strategy
[How to determine if two tokens are "the same". Examples:]

For typography:
- Same font family + size within 10% + weight within 100

For shadow:
- Euclidean distance of all numeric values within 15%

[CUSTOMIZE: Define similarity measure here]

### AI Extraction Prompt Focus
[What should Claude/OpenAI look for in images?]

For typography:
- Font families and sizes
- Heading hierarchy
- Body text styles
- Caption/label styles

For shadow:
- Drop shadows on cards/buttons
- Elevation levels
- Soft vs hard shadows
- Colored shadows

[CUSTOMIZE: Define what AI should extract]

### Export Formats
[Which export formats are needed?]

- W3C Design Tokens (required)
- CSS custom properties (required)
- [Add others: SCSS, React, Tailwind, etc.]

[CUSTOMIZE: List required formats]

## Deliverables Required

Create the following documents in `docs/planning/token-pipeline-planning/[token_type]/`:

### 1. Technical Planning Document
**File:** `[TOKEN_TYPE]_TOKEN_PIPELINE_PLANNING.md`

Following the exact structure of SPACING_TOKEN_PIPELINE_PLANNING.md:
- Architecture overview
- Pydantic model (all properties)
- SQLAlchemy model
- AI extractor implementation
- Utility functions
- Aggregator with deduplication
- Batch extractor
- API endpoints
- SSE streaming
- Export generators
- Database migration
- Testing strategy

### 2. SDLC Atomic Tasks
**File:** `[TOKEN_TYPE]_SDLC_TASKS.md`

Following SDLC_ATOMIC_TASKS.md pattern:
- All 7 SDLC phases
- Atomic tasks (2-8 hours each)
- Task IDs, dependencies, estimates
- Acceptance criteria

### 3. Implementation Roadmap
**File:** `[TOKEN_TYPE]_ROADMAP.md`

Following IMPLEMENTATION_ROADMAP.md pattern:
- Week-by-week breakdown
- Daily task allocation
- Milestones and gates

### 4. Reference Implementation Code

Create in `docs/planning/token-pipeline-planning/[token_type]/reference-implementation/`:

```
src/
├── models/[token_type]_token.py
├── extractors/
│   ├── [token_type]_extractor.py
│   ├── [token_type]_utils.py
│   └── batch_[token_type]_extractor.py
├── aggregators/[token_type]_aggregator.py
├── generators/
│   ├── [token_type]_w3c_generator.py
│   └── [token_type]_css_generator.py
└── api/[token_type]_router.py

tests/
├── conftest.py
├── unit/
│   ├── test_[token_type]_extractor.py
│   ├── test_[token_type]_utils.py
│   └── test_[token_type]_aggregator.py
└── integration/
    └── test_[token_type]_pipeline.py

config/
├── [token_type]_config.py
├── .env.[token_type].example
└── migration_[token_type]_tokens.py

scripts/
├── setup_[token_type].sh
├── run_[token_type]_tests.sh
└── seed_[token_type]_data.py
```

### 5. README
**File:** `README.md`

Index of all deliverables with quick navigation.

## Important Guidelines

1. **Follow existing patterns exactly** - Don't invent new patterns
2. **Evolve the codebase** - Build on what exists
3. **Include all SDLC phases** - Requirements through maintenance
4. **Make tasks atomic** - 2-8 hours each
5. **Add clear acceptance criteria** - Testable conditions
6. **Document integration points** - TODO comments in code
7. **Consider production readiness** - Security, caching, monitoring

## Output Format

Create all files with complete content. Don't use placeholders like "..." or "[TODO]".

For code files:
- Include complete, working implementations
- Add comprehensive docstrings
- Mark integration points with TODO comments
- Follow existing code style exactly

For documentation:
- Use markdown formatting
- Include diagrams where helpful
- Cross-reference other documents
- Be specific and actionable

## Begin

Start by reading the reference documents in the codebase to understand the patterns, then create the complete deliverable package for the [TOKEN_TYPE] token pipeline.
```

---

## Example Usage

### Creating Typography Token Pipeline

Replace the customization sections:

```markdown
### Token Name
**typography**

### Core Properties
- font_family: str
- font_size: int (px)
- font_weight: int (100-900)
- line_height: float
- letter_spacing: float (px)
- text_transform: str (none/uppercase/lowercase/capitalize)

### Computed Properties
- font_size_rem: float
- font_size_em: float
- readability_score: float (0-1)
- suggested_use: str (display/heading/body/caption/label)
- accessibility_compliant: bool

### Deduplication Strategy
Typography tokens are considered duplicates if:
- Same font family (case-insensitive)
- Font size within 2px
- Font weight within 100

### AI Extraction Prompt Focus
- Identify all text elements in the image
- Detect font families (or closest match)
- Measure font sizes in pixels
- Identify font weights
- Detect line heights and letter spacing
- Note text hierarchy (headings vs body)

### Export Formats
- W3C Design Tokens
- CSS custom properties
- SCSS variables
- Tailwind fontFamily/fontSize config
```

### Creating Shadow Token Pipeline

```markdown
### Token Name
**shadow**

### Core Properties
- offset_x: int (px)
- offset_y: int (px)
- blur_radius: int (px)
- spread_radius: int (px)
- color: str (hex with alpha)
- inset: bool

### Computed Properties
- elevation_level: int (1-5)
- css_box_shadow: str
- is_soft: bool (blur > 2x offset)
- is_colored: bool (not gray/black)
- ambient_vs_key: str (ambient/key/both)

### Deduplication Strategy
Shadow tokens are considered duplicates if:
- Euclidean distance of (offset_x, offset_y, blur, spread) < 15%
- Color Delta-E < 5

### AI Extraction Prompt Focus
- Identify shadows on UI elements (cards, buttons, modals)
- Measure shadow offsets, blur, spread
- Detect shadow colors
- Identify elevation hierarchy
- Note soft vs hard shadows

### Export Formats
- W3C Design Tokens
- CSS custom properties
- CSS box-shadow values
- Tailwind boxShadow config
```

### Creating Border Token Pipeline

```markdown
### Token Name
**border**

### Core Properties
- width: int (px)
- style: str (solid/dashed/dotted/double)
- color: str (hex)
- radius_top_left: int (px)
- radius_top_right: int (px)
- radius_bottom_right: int (px)
- radius_bottom_left: int (px)

### Computed Properties
- is_uniform_radius: bool
- radius_scale: str (none/sm/md/lg/full)
- css_border: str
- css_border_radius: str

### Deduplication Strategy
Border tokens are considered duplicates if:
- Same width
- Same style
- Color Delta-E < 5
- Radius within 2px on all corners

### AI Extraction Prompt Focus
- Identify borders on UI elements
- Measure border widths and styles
- Detect border colors
- Measure border radii
- Note patterns (rounded cards, pill buttons, etc.)

### Export Formats
- W3C Design Tokens
- CSS custom properties
- Tailwind borderWidth/borderRadius config
```

---

## Tips for Best Results

1. **Be specific about properties** - List every field the token needs
2. **Define clear deduplication** - How to know if two are "the same"
3. **Focus AI prompts** - What specifically should it look for
4. **Consider edge cases** - What happens with unusual values
5. **Think about relationships** - How does this token relate to others

---

## Advanced: Creating Artistic/Abstract Tokens

For more abstract token types like "artistic style" or "mood":

```markdown
### Token Name
**artistic_style**

### Core Properties
- style_name: str (e.g., "minimalist", "brutalist", "organic")
- visual_complexity: float (0-1)
- color_palette_type: str (monochromatic/complementary/analogous)
- shape_language: str (geometric/organic/mixed)
- texture_level: float (0-1)
- contrast_level: str (low/medium/high)

### Computed Properties
- design_era: str (modern/postmodern/contemporary)
- suggested_font_styles: list[str]
- mood_keywords: list[str]
- comparable_brands: list[str]

### Deduplication Strategy
Style tokens are considered duplicates if:
- Same style_name
- Visual complexity within 0.1
- Same shape_language

### AI Extraction Prompt Focus
- Identify overall design aesthetic
- Classify visual complexity
- Detect shape language (geometric vs organic)
- Identify texture and pattern usage
- Assess contrast and visual hierarchy
- Suggest style classification

### Export Formats
- W3C Design Tokens (with extensions)
- JSON style guide
- Markdown style description
```

---

## Maintenance

When the codebase patterns change:
1. Update the reference document paths in this prompt
2. Update the deliverable structure to match
3. Add any new required sections

---

**This prompt enables rapid creation of new token types following established patterns.**

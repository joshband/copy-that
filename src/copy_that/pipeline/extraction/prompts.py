"""Prompt templates for token extraction.

Provides specialized prompts for each token type to guide AI extraction.
"""

from copy_that.pipeline import TokenType

# System prompt for all extractions
SYSTEM_PROMPT = """You are an expert design system analyst specializing in extracting design tokens from visual designs.
Your task is to analyze the provided image and extract design tokens accurately.

Guidelines:
- Be precise and consistent in your extractions
- Use kebab-case for token names (e.g., 'primary-blue', 'space-md')
- Provide confidence scores based on clarity and certainty
- Include usage context when identifiable
- Extract all visible instances, not just unique values
- Consider the design system conventions when naming tokens"""


# Token type specific prompts
COLOR_PROMPT = """Analyze this design image and extract all color tokens.

Focus on:
1. **Brand Colors**: Primary, secondary, and accent colors used for branding
2. **UI Colors**: Colors for interactive elements (buttons, links, hover states)
3. **Semantic Colors**: Success (green), warning (yellow), error (red), info (blue)
4. **Neutral Colors**: Grays, blacks, whites for text and backgrounds
5. **Background Colors**: Page and component backgrounds

For each color:
- Provide a descriptive name following design system conventions
- Extract the exact hex value
- Include RGB values when possible
- Note the apparent usage/purpose
- Assign a confidence score (1.0 = certain, 0.5 = moderate certainty)

Use the extract_colors tool to return your findings."""


SPACING_PROMPT = """Analyze this design image and extract spacing tokens.

Focus on:
1. **Margin Values**: Outer spacing between elements
2. **Padding Values**: Inner spacing within elements
3. **Gap Values**: Spacing in flex/grid layouts
4. **Consistent Scale**: Identify the spacing scale (4px, 8px, 16px, etc.)

For each spacing value:
- Name it according to a t-shirt sizing convention (xs, sm, md, lg, xl)
- Provide the numeric value
- Specify the unit (prefer px or rem)
- Note where it's commonly used
- Assign a confidence score

Use the extract_spacing tool to return your findings."""


TYPOGRAPHY_PROMPT = """Analyze this design image and extract typography tokens.

Focus on:
1. **Headings**: H1-H6 styles
2. **Body Text**: Paragraph and content text styles
3. **UI Text**: Labels, buttons, captions
4. **Special Text**: Code, quotes, emphasis

For each typography style:
- Name it descriptively (e.g., 'heading-1', 'body-large')
- Identify the font family (or best guess)
- Extract font size with unit
- Determine font weight (100-900)
- Calculate line height
- Note letter spacing if apparent

Use the extract_typography tool to return your findings."""


SHADOW_PROMPT = """Analyze this design image and extract shadow tokens.

Focus on:
1. **Elevation Shadows**: Cards, modals, dropdowns
2. **Button Shadows**: Interactive element depth
3. **Input Shadows**: Focus states, field depth
4. **Subtle Shadows**: Borders, separators

For each shadow:
- Name it by intensity (xs, sm, md, lg, xl)
- Determine offset X and Y values
- Estimate blur radius
- Estimate spread radius
- Extract shadow color (use rgba for transparency)
- Identify shadow type (drop-shadow, box-shadow, inner)

Use the extract_shadows tool to return your findings."""


GRADIENT_PROMPT = """Analyze this design image and extract gradient tokens.

Focus on:
1. **Background Gradients**: Hero sections, feature areas
2. **Button Gradients**: CTA buttons, interactive elements
3. **Overlay Gradients**: Image overlays, text protection
4. **Accent Gradients**: Decorative elements

For each gradient:
- Give it a descriptive name
- Identify the type (linear, radial, conic)
- Determine angle for linear gradients
- Extract all color stops with positions
- Note the common usage

Use the extract_gradients tool to return your findings."""


# Prompt registry
PROMPT_REGISTRY: dict[TokenType, str] = {
    TokenType.COLOR: COLOR_PROMPT,
    TokenType.SPACING: SPACING_PROMPT,
    TokenType.TYPOGRAPHY: TYPOGRAPHY_PROMPT,
    TokenType.SHADOW: SHADOW_PROMPT,
    TokenType.GRADIENT: GRADIENT_PROMPT,
}


def get_system_prompt() -> str:
    """Get the system prompt for extraction.

    Returns:
        System prompt string
    """
    return SYSTEM_PROMPT


def get_extraction_prompt(token_type: TokenType | str) -> str:
    """Get the extraction prompt for a token type.

    Args:
        token_type: Token type to get prompt for

    Returns:
        Extraction prompt string

    Raises:
        KeyError: If token type not in registry
    """
    if isinstance(token_type, str):
        token_type = TokenType(token_type)

    if token_type not in PROMPT_REGISTRY:
        raise KeyError(f"No prompt registered for token type: {token_type}")

    return PROMPT_REGISTRY[token_type]

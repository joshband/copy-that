"""
Generator agent for multi-format token output.

Provides the GeneratorAgent class that transforms TokenResults
into various output formats using Jinja2 templates.
"""

from enum import Enum
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, TemplateError

from copy_that.pipeline.exceptions import GenerationError
from copy_that.pipeline.interfaces import BasePipelineAgent
from copy_that.pipeline.types import PipelineTask, TokenResult


class OutputFormat(str, Enum):
    """Supported output formats for token generation."""

    W3C = "w3c"
    CSS = "css"
    SCSS = "scss"
    REACT = "react"
    TAILWIND = "tailwind"


class GeneratorAgent(BasePipelineAgent):
    """
    Agent for generating token output in multiple formats.

    Transforms TokenResults into various output formats including
    W3C Design Tokens JSON, CSS Custom Properties, SCSS variables,
    React theme objects, and Tailwind configuration.

    The agent uses Jinja2 templates for flexible output generation
    and can be configured to use different formats at initialization
    or per-generation call.

    Example:
        >>> agent = GeneratorAgent(output_format=OutputFormat.CSS)
        >>> tokens = [TokenResult(...), TokenResult(...)]
        >>> output = await agent.generate(tokens)
        >>> print(output)
        :root {
          --color-primary: #FF6B35;
        }
    """

    def __init__(self, output_format: OutputFormat | str = OutputFormat.W3C) -> None:
        """
        Initialize the generator agent.

        Args:
            output_format: Output format to use (default: W3C)

        Raises:
            ValueError: If output_format string is invalid
        """
        if isinstance(output_format, str):
            try:
                output_format = OutputFormat(output_format)
            except ValueError as e:
                valid = [f.value for f in OutputFormat]
                raise ValueError(
                    f"Invalid output format: {output_format}. Valid formats: {valid}"
                ) from e

        self._output_format = output_format
        self._template_dir = Path(__file__).parent / "templates"
        self._env = Environment(
            loader=FileSystemLoader(str(self._template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Register custom filters
        self._env.filters["to_kebab"] = self._to_kebab_case
        self._env.filters["to_camel"] = self._to_camel_case
        self._env.filters["to_css_var"] = self._to_css_var
        self._env.filters["to_scss_var"] = self._to_scss_var
        self._env.filters["resolve_reference"] = self._resolve_reference
        self._env.filters["shadow_to_css"] = self._shadow_to_css

    @property
    def output_format(self) -> OutputFormat:
        """Get the current output format."""
        return self._output_format

    @output_format.setter
    def output_format(self, value: OutputFormat | str) -> None:
        """Set the output format."""
        if isinstance(value, str):
            value = OutputFormat(value)
        self._output_format = value

    @property
    def agent_type(self) -> str:
        """Return the agent type identifier."""
        return "generator"

    @property
    def stage_name(self) -> str:
        """Return the pipeline stage name."""
        return "generation"

    async def process(
        self, task: PipelineTask, *, tokens: list[TokenResult] | None = None
    ) -> list[TokenResult]:
        """
        Process a pipeline task and return token results.

        For the generator, this generates output in the configured format
        and returns the original tokens with generation metadata.

        Args:
            task: The pipeline task
            tokens: Token results to generate output from

        Returns:
            List of TokenResult objects with generation metadata

        Raises:
            GenerationError: If no tokens provided or generation fails
        """
        if tokens is None:
            raise GenerationError("No tokens provided for generation")

        if not tokens:
            return []

        # Generate output
        output = await self.generate(tokens)

        # Return tokens with generation metadata
        for token in tokens:
            if token.metadata is None:
                token.metadata = {}
            token.metadata["generated_format"] = self._output_format.value
            token.metadata["generated_output"] = output

        return tokens

    async def health_check(self) -> bool:
        """
        Check if the agent is healthy and ready.

        Verifies that templates are available for all formats.

        Returns:
            True if healthy, False otherwise
        """
        for fmt in OutputFormat:
            template_path = self._template_dir / f"{fmt.value}.j2"
            if not template_path.exists():
                return False
        return True

    async def generate(
        self,
        tokens: list[TokenResult],
        output_format: OutputFormat | None = None,
        **kwargs: Any,
    ) -> str:
        """
        Generate output from tokens in the specified format.

        Args:
            tokens: List of TokenResult objects to generate from
            output_format: Optional format override
            **kwargs: Additional template options (e.g., use_maps for SCSS)

        Returns:
            Generated output string

        Raises:
            GenerationError: If generation fails
        """
        if not tokens:
            return self._get_empty_output(output_format or self._output_format)

        fmt = output_format or self._output_format
        template_name = f"{fmt.value}.j2"

        try:
            template = self._env.get_template(template_name)
        except TemplateError as e:
            raise GenerationError(
                f"Failed to load template {template_name}",
                details={"error": str(e)},
            ) from e

        # Build token tree structure
        token_tree = self._build_token_tree(tokens)

        try:
            # Render template
            output = template.render(
                tokens=tokens,
                token_tree=token_tree,
                format=fmt.value,
                **kwargs,
            )
            return output
        except TemplateError as e:
            raise GenerationError(
                f"Template rendering failed for {fmt.value}",
                details={"error": str(e)},
            ) from e
        except (TypeError, ValueError) as e:
            raise GenerationError(
                f"Invalid token data for {fmt.value} generation",
                details={"error": str(e)},
            ) from e

    def _build_token_tree(self, tokens: list[TokenResult]) -> dict[str, Any]:
        """
        Build a nested tree structure from tokens based on their paths.

        Args:
            tokens: List of TokenResult objects

        Returns:
            Nested dictionary representing token hierarchy
        """
        tree: dict[str, Any] = {}

        for token in tokens:
            # Navigate/create path
            current = tree
            for segment in token.path:
                if segment not in current:
                    current[segment] = {}
                current = current[segment]

            # Add token at final location
            current[token.name] = token.to_w3c_dict()

        return tree

    def _get_empty_output(self, fmt: OutputFormat) -> str:
        """Get empty output for a format."""
        if fmt == OutputFormat.W3C:
            return "{}"
        elif fmt == OutputFormat.CSS:
            return ":root {\n}"
        elif fmt == OutputFormat.SCSS:
            return "// No tokens\n"
        elif fmt == OutputFormat.REACT:
            return "export const tokens = {} as const;\n"
        elif fmt == OutputFormat.TAILWIND:
            return "module.exports = {\n  theme: {\n    extend: {}\n  }\n};\n"
        return ""

    @staticmethod
    def _to_kebab_case(path: list[str] | str) -> str:
        """Convert path to kebab-case variable name."""
        if isinstance(path, list):
            return "-".join(path)
        return path.replace("_", "-").replace(".", "-")

    @staticmethod
    def _to_camel_case(s: str) -> str:
        """Convert string to camelCase."""
        parts = s.replace("-", "_").split("_")
        return parts[0] + "".join(word.capitalize() for word in parts[1:])

    @staticmethod
    def _to_css_var(path: list[str]) -> str:
        """Convert path to CSS custom property name."""
        return "--" + "-".join(path)

    @staticmethod
    def _to_scss_var(path: list[str]) -> str:
        """Convert path to SCSS variable name."""
        return "$" + "-".join(path)

    @staticmethod
    def _resolve_reference(reference: str, format_type: str = "css") -> str:
        """
        Resolve a token reference to format-specific syntax.

        Args:
            reference: Token reference like {color.primary}
            format_type: Output format type

        Returns:
            Format-specific reference
        """
        if not reference:
            return reference

        # Extract path from {path.to.token}
        path = reference.strip("{}").replace(".", "-")

        if format_type == "css":
            return f"var(--{path})"
        elif format_type == "scss":
            return f"${path}"
        else:
            return reference

    @staticmethod
    def _shadow_to_css(value: dict[str, Any]) -> str:
        """
        Convert W3C shadow value to CSS box-shadow string.

        Args:
            value: Shadow value dict with offsetX, offsetY, blur, spread, color

        Returns:
            CSS box-shadow string
        """
        if not isinstance(value, dict):
            return str(value)

        offset_x = value.get("offsetX", "0px")
        offset_y = value.get("offsetY", "0px")
        blur = value.get("blur", "0px")
        spread = value.get("spread", "0px")
        color = value.get("color", "transparent")

        return f"{offset_x} {offset_y} {blur} {spread} {color}"

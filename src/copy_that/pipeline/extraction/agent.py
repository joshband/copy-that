"""ExtractionAgent for design token extraction using Claude Tool Use.

Single configurable agent that handles all token types via tool schemas.
"""

import asyncio
import base64
import os
from typing import Any

import anthropic
import httpx

from copy_that.pipeline import (
    BasePipelineAgent,
    ExtractionError,
    PipelineTask,
    TokenResult,
    TokenType,
    W3CTokenType,
)
from copy_that.pipeline.extraction.prompts import get_extraction_prompt, get_system_prompt
from copy_that.pipeline.extraction.schemas import get_tool_schema, validate_extraction_result

# Mapping from TokenType to W3CTokenType
TOKEN_TYPE_TO_W3C: dict[TokenType, W3CTokenType] = {
    TokenType.COLOR: W3CTokenType.COLOR,
    TokenType.SPACING: W3CTokenType.DIMENSION,
    TokenType.TYPOGRAPHY: W3CTokenType.TYPOGRAPHY,
    TokenType.SHADOW: W3CTokenType.SHADOW,
    TokenType.GRADIENT: W3CTokenType.GRADIENT,
}

# Path prefix mapping for token organization
TOKEN_TYPE_PATH_PREFIX: dict[TokenType, list[str]] = {
    TokenType.COLOR: ["color"],
    TokenType.SPACING: ["spacing"],
    TokenType.TYPOGRAPHY: ["typography"],
    TokenType.SHADOW: ["shadow"],
    TokenType.GRADIENT: ["gradient"],
}


class ExtractionAgent(BasePipelineAgent):
    """Agent for extracting design tokens using Claude Tool Use.

    This agent is configurable for any token type via schemas.
    It uses Claude's Tool Use feature to extract structured token data.

    Example:
        agent = ExtractionAgent(token_type=TokenType.COLOR)
        task = PipelineTask(
            task_id="task-1",
            image_url="https://example.com/design.png",
            token_types=[TokenType.COLOR]
        )
        results = await agent.process(task)
    """

    def __init__(
        self,
        token_type: TokenType,
        api_key: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        model: str = "claude-sonnet-4-5-20250929",
    ):
        """Initialize ExtractionAgent.

        Args:
            token_type: Type of tokens to extract
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            model: Claude model to use
        """
        self._token_type = token_type
        self._api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self._timeout = timeout
        self._max_retries = max_retries
        self._model = model
        self._client: anthropic.Anthropic | None = None

        # Initialize client if API key available
        if self._api_key:
            self._client = anthropic.Anthropic(api_key=self._api_key)

    @property
    def agent_type(self) -> str:
        """Return agent type identifier."""
        return "extraction_agent"

    @property
    def stage_name(self) -> str:
        """Return pipeline stage name."""
        return "extraction"

    @property
    def token_type(self) -> TokenType:
        """Return configured token type."""
        return self._token_type

    @property
    def timeout(self) -> float:
        """Return timeout setting."""
        return self._timeout

    @property
    def max_retries(self) -> int:
        """Return max retries setting."""
        return self._max_retries

    async def health_check(self) -> bool:
        """Check if agent is healthy and ready.

        Returns:
            True if client is available, False otherwise
        """
        return self._client is not None

    async def process(self, task: PipelineTask) -> list[TokenResult]:
        """Process task and extract tokens.

        Args:
            task: Pipeline task containing image URL

        Returns:
            List of extracted TokenResult objects

        Raises:
            ExtractionError: If extraction fails
        """
        try:
            # Get image data
            image_data = await self._get_image_data(task)

            # Call Anthropic API with retry logic
            response = await self._call_with_retry(image_data)

            # Parse and validate response
            extraction_result = self._parse_response(response)

            # Convert to TokenResult objects
            results = self._convert_to_token_results(extraction_result)

            return results

        except TimeoutError:
            raise ExtractionError(
                f"Extraction timed out after {self._timeout}s",
                details={"task_id": task.task_id, "timeout": self._timeout},
            )
        except ExtractionError:
            raise
        except Exception as e:
            raise ExtractionError(
                f"Extraction failed: {str(e)}",
                details={"task_id": task.task_id, "error_type": type(e).__name__},
            )

    async def _get_image_data(self, task: PipelineTask) -> dict[str, Any]:
        """Get image data from task.

        Args:
            task: Pipeline task

        Returns:
            Image data dict with type and source
        """
        # Check for preprocessed image in context
        if task.context and "preprocessed_image" in task.context:
            preprocessed = task.context["preprocessed_image"]
            if (
                hasattr(preprocessed, "preprocessed_data")
                and preprocessed.preprocessed_data
                and "base64" in preprocessed.preprocessed_data
            ):
                return {
                    "type": "base64",
                    "media_type": f"image/{preprocessed.format}",
                    "data": preprocessed.preprocessed_data["base64"],
                }

        # Download image from URL
        async with httpx.AsyncClient() as client:
            response = await client.get(task.image_url, timeout=10.0)
            response.raise_for_status()

            # Determine media type
            content_type = response.headers.get("content-type", "image/png")
            media_type = content_type.split(";")[0].strip()

            # Encode to base64
            image_base64 = base64.b64encode(response.content).decode("utf-8")

            return {"type": "base64", "media_type": media_type, "data": image_base64}

    async def _call_with_retry(self, image_data: dict[str, Any]) -> Any:
        """Call Anthropic API with retry logic.

        Args:
            image_data: Image data for the request

        Returns:
            API response

        Raises:
            ExtractionError: If all retries fail
        """
        last_error = None

        for attempt in range(self._max_retries):
            try:
                response = await asyncio.wait_for(
                    self._call_anthropic(image_data), timeout=self._timeout
                )
                return response

            except Exception as e:
                last_error = e
                # Check if rate limited
                if hasattr(e, "status_code") and e.status_code == 429:
                    # Exponential backoff
                    wait_time = (2**attempt) * 0.5
                    await asyncio.sleep(wait_time)
                    continue
                elif isinstance(e, asyncio.TimeoutError):
                    raise
                else:
                    # Non-retryable error
                    raise

        # All retries exhausted
        raise ExtractionError(
            f"Extraction failed after {self._max_retries} attempts: {last_error}",
            details={"attempts": self._max_retries, "last_error": str(last_error)},
        )

    async def _call_anthropic(self, image_data: dict[str, Any]) -> Any:
        """Make API call to Anthropic.

        Args:
            image_data: Image data for the request

        Returns:
            API response
        """
        tool = get_tool_schema(self._token_type)
        prompt = get_extraction_prompt(self._token_type)
        system = get_system_prompt()

        # Build message with image
        message = await asyncio.to_thread(
            self._client.messages.create,
            model=self._model,
            max_tokens=4096,
            system=system,
            tools=[tool],
            tool_choice={"type": "tool", "name": tool["name"]},
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "source": image_data},
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        )

        return message

    def _parse_response(self, response: Any) -> dict[str, Any]:
        """Parse API response and extract tool result.

        Args:
            response: Anthropic API response

        Returns:
            Parsed extraction result

        Raises:
            ExtractionError: If response is invalid
        """
        # Find tool use content
        tool_use_content = None
        for content in response.content:
            if content.type == "tool_use":
                tool_use_content = content
                break

        if not tool_use_content:
            raise ExtractionError(
                "No tool use in response", details={"stop_reason": response.stop_reason}
            )

        # Validate against schema
        result = tool_use_content.input
        validate_extraction_result(self._token_type, result)

        return result

    def _convert_to_token_results(self, extraction_result: dict[str, Any]) -> list[TokenResult]:
        """Convert extraction result to TokenResult objects.

        Args:
            extraction_result: Raw extraction result from API

        Returns:
            List of TokenResult objects
        """
        results = []

        # Get items based on token type
        items = self._get_items_from_result(extraction_result)
        w3c_type = TOKEN_TYPE_TO_W3C[self._token_type]
        path_prefix = TOKEN_TYPE_PATH_PREFIX[self._token_type]

        for item in items:
            # Extract common fields
            name = item.get("name", "unknown")
            confidence = item.get("confidence", 0.5)
            usage = item.get("usage")

            # Get value and metadata based on token type
            value, metadata = self._extract_value_and_metadata(item)

            # Create TokenResult
            token_result = TokenResult(
                token_type=self._token_type,
                name=name,
                path=path_prefix.copy(),
                w3c_type=w3c_type,
                value=value,
                description=usage,
                confidence=confidence,
                metadata=metadata if metadata else None,
            )

            results.append(token_result)

        return results

    def _get_items_from_result(self, result: dict[str, Any]) -> list[dict[str, Any]]:
        """Get item list from extraction result.

        Args:
            result: Extraction result

        Returns:
            List of items
        """
        key_map = {
            TokenType.COLOR: "colors",
            TokenType.SPACING: "spacing",
            TokenType.TYPOGRAPHY: "typography",
            TokenType.SHADOW: "shadows",
            TokenType.GRADIENT: "gradients",
        }

        key = key_map[self._token_type]
        return result.get(key, [])

    def _extract_value_and_metadata(self, item: dict[str, Any]) -> tuple[Any, dict[str, Any]]:
        """Extract value and metadata from item.

        Args:
            item: Single extraction item

        Returns:
            Tuple of (value, metadata)
        """
        metadata = {}

        if self._token_type == TokenType.COLOR:
            value = item.get("hex_value", "#000000")
            if "rgb" in item:
                metadata["rgb"] = item["rgb"]
            if "hsl" in item:
                metadata["hsl"] = item["hsl"]
            if "category" in item:
                metadata["category"] = item["category"]

        elif self._token_type == TokenType.SPACING:
            num_value = item.get("value", 0)
            unit = item.get("unit", "px")
            value = f"{num_value}{unit}"
            if "scale_position" in item:
                metadata["scale_position"] = item["scale_position"]

        elif self._token_type == TokenType.TYPOGRAPHY:
            # Typography value is a composite
            value = {
                "fontFamily": item.get("font_family", "sans-serif"),
                "fontSize": self._format_dimension(item.get("font_size", {})),
                "fontWeight": item.get("font_weight", 400),
                "lineHeight": self._format_dimension(item.get("line_height", {})),
            }
            if "letter_spacing" in item:
                value["letterSpacing"] = self._format_dimension(item["letter_spacing"])

        elif self._token_type == TokenType.SHADOW:
            # Shadow value is a composite
            value = {
                "offsetX": self._format_dimension(item.get("offset_x", {})),
                "offsetY": self._format_dimension(item.get("offset_y", {})),
                "blur": self._format_dimension(item.get("blur_radius", {})),
                "spread": self._format_dimension(item.get("spread_radius", {})),
                "color": item.get("color", "rgba(0, 0, 0, 0.1)"),
            }
            if "type" in item:
                metadata["shadow_type"] = item["type"]

        elif self._token_type == TokenType.GRADIENT:
            # Gradient value is a composite
            value = {"type": item.get("type", "linear"), "stops": item.get("stops", [])}
            if "angle" in item:
                value["angle"] = item["angle"]

        else:
            value = str(item)

        return value, metadata

    def _format_dimension(self, dim: dict[str, Any]) -> str:
        """Format dimension object to string.

        Args:
            dim: Dimension dict with value and unit

        Returns:
            Formatted dimension string
        """
        if not dim:
            return "0px"

        value = dim.get("value", 0)
        unit = dim.get("unit", "px")

        if unit == "unitless":
            return str(value)

        return f"{value}{unit}"

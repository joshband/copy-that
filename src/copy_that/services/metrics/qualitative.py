"""Qualitative metrics provider - AI-powered design insights.

Provides TIER 3 metrics: design patterns, recommendations, and insights using Claude Sonnet 4.5.
Returns in 5-15 seconds with AI analysis (may return null if API unavailable).
"""

import json
import logging
import os
from typing import Any

import anthropic
from sqlalchemy.ext.asyncio import AsyncSession

from .base import MetricProvider, MetricResult, MetricTier
from .token_graph import TokenGraph

logger = logging.getLogger(__name__)


class QualitativeMetricsProvider(MetricProvider):
    """Computes qualitative metrics (TIER 3) using AI analysis.

    Metrics computed:
    - Design pattern recognition (e.g., "Material Design influenced", "Brutalist")
    - System maturity assessment (beginner/intermediate/advanced)
    - Design recommendations (improvements, best practices)
    - Consistency analysis (token usage patterns)
    - Accessibility recommendations (beyond WCAG ratios)
    - Design system health score (0-100)

    Time: 5-15 seconds (Claude API call)
    May return null: If ANTHROPIC_API_KEY not set or API fails

    Uses TokenGraph for generic token loading, supporting ANY token type.
    """

    name = "qualitative"
    tier = MetricTier.TIER_3

    def __init__(self, db: AsyncSession, api_key: str | None = None):
        """Initialize provider with database session and optional API key.

        Args:
            db: AsyncSession for database access
            api_key: Anthropic API key. If not provided, uses ANTHROPIC_API_KEY env var
        """
        self.db = db
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = "claude-sonnet-4-5-20250929"

        # Graceful degradation: provider can initialize without API key
        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY not set - qualitative metrics will return null")
            self.client = None
        else:
            self.client = anthropic.Anthropic(api_key=self.api_key)

    async def compute(self, project_id: int) -> MetricResult:
        """Compute qualitative metrics for a project using AI analysis.

        Args:
            project_id: Project to analyze

        Returns:
            MetricResult with AI insights or null data if API unavailable
        """
        # Graceful degradation: return null if no API key
        if not self.client:
            return MetricResult(
                tier=self.tier,
                provider_name=self.name,
                data=None,
                error="ANTHROPIC_API_KEY not configured",
            )

        try:
            # Load all tokens using TokenGraph
            graph = TokenGraph(project_id, self.db)
            await graph.load()

            # Get tokens by category
            colors = graph.get_tokens_by_category("color")
            spacing = graph.get_tokens_by_category("spacing")
            typography = graph.get_tokens_by_category("typography")
            shadows = graph.get_tokens_by_category("shadow")

            # Format token data for AI prompt
            token_summary = self._format_tokens_for_prompt(colors, spacing, typography, shadows)

            # Generate AI prompt
            prompt = self._create_analysis_prompt(token_summary)

            # Call Claude API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": prompt}],
                    }
                ],
            )

            # Parse AI response
            response_text = message.content[0].text
            insights = self._parse_ai_response(response_text)

            logger.info("Successfully computed qualitative metrics for project %d", project_id)
            return MetricResult(
                tier=self.tier,
                provider_name=self.name,
                data=insights,
            )

        except anthropic.APIError as e:
            logger.error("Claude API error: %s", str(e))
            return MetricResult(
                tier=self.tier,
                provider_name=self.name,
                data=None,
                error=f"Claude API error: {str(e)}",
            )
        except Exception as e:
            logger.error("Error computing qualitative metrics: %s", str(e))
            return MetricResult(
                tier=self.tier,
                provider_name=self.name,
                data=None,
                error=f"Unexpected error: {str(e)}",
            )

    def _format_tokens_for_prompt(
        self,
        colors: list[Any],
        spacing: list[Any],
        typography: list[Any],
        shadows: list[Any],
    ) -> dict[str, Any]:
        """Format token data into a summary for the AI prompt.

        Args:
            colors: Color token nodes
            spacing: Spacing token nodes
            typography: Typography token nodes
            shadows: Shadow token nodes

        Returns:
            Dictionary with token counts and sample data
        """
        return {
            "colors": {
                "count": len(colors),
                "samples": [
                    {
                        "name": token.name,
                        "value": token.value,
                        "metadata": token.metadata,
                    }
                    for token in colors[:5]  # First 5 for context
                ],
            },
            "spacing": {
                "count": len(spacing),
                "samples": [
                    {
                        "name": token.name,
                        "value": token.value,
                        "metadata": token.metadata,
                    }
                    for token in spacing[:5]
                ],
            },
            "typography": {
                "count": len(typography),
                "samples": [
                    {
                        "name": token.name,
                        "value": token.value,
                        "metadata": token.metadata,
                    }
                    for token in typography[:5]
                ],
            },
            "shadows": {
                "count": len(shadows),
                "samples": [
                    {
                        "name": token.name,
                        "value": token.value,
                        "metadata": token.metadata,
                    }
                    for token in shadows[:5]
                ],
            },
        }

    def _create_analysis_prompt(self, token_summary: dict[str, Any]) -> str:
        """Create the AI prompt for design analysis.

        Args:
            token_summary: Formatted token data

        Returns:
            Prompt string for Claude
        """
        return f"""You are a senior design systems expert analyzing a design token set.

**Token Summary:**
```json
{json.dumps(token_summary, indent=2)}
```

**Analyze this design system and provide:**

1. **Design Patterns** (1-3 patterns)
   - Identify recognizable design patterns (e.g., "Material Design", "iOS Human Interface", "Brutalist", "Minimalist")
   - Confidence level for each pattern (0-1)

2. **System Maturity** (one of: beginner/intermediate/advanced)
   - Assess overall design system sophistication
   - Consider token count, variety, naming consistency, scale systems

3. **Design Recommendations** (3-5 actionable items)
   - Specific improvements (e.g., "Add more spacing tokens for consistency")
   - Best practices to follow (e.g., "Implement 8pt grid system")
   - Avoid generic advice - be specific to THIS system

4. **Consistency Score** (0-100)
   - Rate how consistent the token naming and values are
   - Consider: naming patterns, scale ratios, color harmonies

5. **Accessibility Insights** (2-3 items)
   - Beyond WCAG ratios: color contrast patterns, text readability, spacing for touch targets
   - Specific to this design system

6. **Design System Health** (0-100 with explanation)
   - Overall score based on completeness, consistency, best practices
   - Brief explanation (1-2 sentences)

**Response Format (JSON):**
```json
{{
  "design_patterns": [
    {{"name": "Pattern Name", "confidence": 0.8, "description": "Why it matches"}}
  ],
  "system_maturity": "intermediate",
  "maturity_reasoning": "1-2 sentence explanation",
  "recommendations": [
    "Specific recommendation 1",
    "Specific recommendation 2"
  ],
  "consistency_score": 75,
  "consistency_notes": "What's consistent, what's not",
  "accessibility_insights": [
    "Insight 1",
    "Insight 2"
  ],
  "design_health_score": 78,
  "design_health_reasoning": "1-2 sentence explanation"
}}
```

Provide ONLY the JSON response, no additional text."""

    def _parse_ai_response(self, response_text: str) -> dict[str, Any]:
        """Parse Claude's response into structured insights.

        Args:
            response_text: Raw JSON response from Claude

        Returns:
            Parsed insights dictionary

        Raises:
            ValueError: If response is not valid JSON
        """
        try:
            # Extract JSON from response (Claude might wrap it in markdown)
            if "```json" in response_text:
                # Extract JSON from code block
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                json_str = response_text[start:end].strip()
            else:
                json_str = response_text.strip()

            # Parse JSON
            insights = json.loads(json_str)

            # Validate required fields
            required_fields = [
                "design_patterns",
                "system_maturity",
                "recommendations",
                "consistency_score",
                "design_health_score",
            ]
            for field in required_fields:
                if field not in insights:
                    logger.warning("Missing required field in AI response: %s", field)

            return insights

        except json.JSONDecodeError as e:
            logger.error("Failed to parse AI response as JSON: %s", str(e))
            # Return fallback structure
            return {
                "design_patterns": [],
                "system_maturity": "unknown",
                "recommendations": ["Analysis unavailable - JSON parse error"],
                "consistency_score": 0,
                "design_health_score": 0,
                "parse_error": str(e),
            }

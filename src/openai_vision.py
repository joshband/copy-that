"""
OpenAI Vision Integration for Copy That

This module provides integration with OpenAI's Vision API (GPT-4 Vision) for
advanced design analysis, component identification, and semantic understanding
of UI reference images.
"""

import os
import base64
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
import json

from openai import OpenAI
from dotenv import load_dotenv
import numpy as np
from PIL import Image

# Load environment variables
load_dotenv()


class OpenAIVisionAnalyzer:
    """
    Uses OpenAI Vision API to analyze UI designs and provide semantic insights.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenAI Vision analyzer.

        Args:
            api_key: OpenAI API key. If None, reads from OPENAI_API_KEY env variable.
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.client = OpenAI(api_key=self.api_key)
        self.model = os.getenv('OPENAI_VISION_MODEL', 'gpt-4o')
        self.max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', '4096'))
        self.temperature = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))

    def encode_image(self, image_path: Union[str, Path]) -> str:
        """
        Encode image to base64 string for API submission.

        Args:
            image_path: Path to the image file

        Returns:
            Base64 encoded image string
        """
        with open(image_path, 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def analyze_design_style(self, image_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Analyze the overall design style and aesthetic of a UI reference.

        Args:
            image_path: Path to the reference image

        Returns:
            Dictionary containing style analysis results
        """
        base64_image = self.encode_image(image_path)

        prompt = """Analyze this UI design and provide a detailed breakdown of its visual style:

1. **Design Style**: What design system or style does this follow? (Material Design, iOS, Fluent, Custom, etc.)
2. **Color Palette**: Describe the primary, secondary, and accent colors used.
3. **Typography**: Describe font weights, sizes, and hierarchy patterns.
4. **Spacing & Layout**: Describe padding, margins, and grid systems.
5. **Corner Radius**: Sharp, slightly rounded, heavily rounded, or mixed?
6. **Shadows & Depth**: Flat, subtle shadows, dramatic elevation, or neumorphic?
7. **Material Properties**: Matte, glossy, frosted glass, gradients, textures?
8. **Visual Hierarchy**: How is importance communicated? (Size, color, weight, position)
9. **Design Principles**: What principles guide this design? (Minimalism, maximalism, playful, professional)

Provide your analysis in JSON format with these keys: design_style, color_palette, typography, spacing, corners, shadows, materials, hierarchy, principles."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )

        content = response.choices[0].message.content

        # Try to parse JSON response
        try:
            # Extract JSON from markdown code blocks if present
            if '```json' in content:
                json_str = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                json_str = content.split('```')[1].split('```')[0].strip()
            else:
                json_str = content

            return json.loads(json_str)
        except json.JSONDecodeError:
            # Return raw response if JSON parsing fails
            return {"raw_analysis": content}

    def identify_components(self, image_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Identify UI components present in the reference image.

        Args:
            image_path: Path to the reference image

        Returns:
            Dictionary containing identified components and their properties
        """
        base64_image = self.encode_image(image_path)

        prompt = """Identify all UI components visible in this design. For each component, describe:

1. **Component Type**: Button, input field, card, modal, nav bar, etc.
2. **Visual State**: Default, hover, active, disabled, or focused?
3. **Variant**: Primary, secondary, tertiary, ghost, outlined, filled?
4. **Size**: Small, medium, large, or custom dimensions?
5. **Location**: Where is it positioned in the layout?
6. **Special Properties**: Icons, badges, shadows, animations, etc.

Return as JSON with structure:
{
  "components": [
    {
      "type": "button",
      "state": "default",
      "variant": "primary",
      "size": "medium",
      "location": "center",
      "properties": ["rounded corners", "drop shadow", "icon"]
    }
  ]
}"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )

        content = response.choices[0].message.content

        try:
            if '```json' in content:
                json_str = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                json_str = content.split('```')[1].split('```')[0].strip()
            else:
                json_str = content

            return json.loads(json_str)
        except json.JSONDecodeError:
            return {"raw_analysis": content}

    def extract_design_tokens(self, image_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Extract specific design tokens (colors, spacing, typography values).

        Args:
            image_path: Path to the reference image

        Returns:
            Dictionary containing extracted design tokens
        """
        base64_image = self.encode_image(image_path)

        prompt = """Extract specific design tokens from this UI. Provide exact or estimated values:

**Colors** (provide hex codes):
- Primary color
- Secondary color
- Accent colors
- Background colors
- Text colors (primary, secondary, disabled)
- Border colors
- Success/Error/Warning colors

**Spacing** (in pixels or as base unit multipliers):
- Base spacing unit (likely 4px or 8px)
- Component padding (horizontal, vertical)
- Margin between elements
- Grid gap

**Typography**:
- Font families used
- Font sizes (heading, body, caption)
- Font weights
- Line heights
- Letter spacing

**Effects**:
- Border radius values
- Shadow values (x, y, blur, spread, color, opacity)
- Opacity values for various states

Return as JSON with structure matching design token standards."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )

        content = response.choices[0].message.content

        try:
            if '```json' in content:
                json_str = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                json_str = content.split('```')[1].split('```')[0].strip()
            else:
                json_str = content

            return json.loads(json_str)
        except json.JSONDecodeError:
            return {"raw_analysis": content}

    def suggest_component_variations(
        self,
        image_path: Union[str, Path],
        component_type: str
    ) -> Dict[str, Any]:
        """
        Get AI suggestions for component variations based on the reference style.

        Args:
            image_path: Path to the reference image
            component_type: Type of component to generate variations for

        Returns:
            Dictionary containing variation suggestions
        """
        base64_image = self.encode_image(image_path)

        prompt = f"""Based on the visual style of this UI, suggest variations for a {component_type}.

Provide:
1. **Size variations**: Small, medium, large dimensions with exact pixel values
2. **Color variations**: Different color schemes that would fit this style
3. **State variations**: How hover, active, disabled, and focus states should look
4. **Style variations**: Primary, secondary, tertiary, ghost, outlined versions
5. **Special variations**: Any unique variants that would fit (with icons, loading, etc.)

For each variation, describe:
- Dimensions (width x height in px)
- Colors (specific hex codes)
- Border radius
- Shadow/elevation
- Any other distinguishing features

Return as JSON."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )

        content = response.choices[0].message.content

        try:
            if '```json' in content:
                json_str = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                json_str = content.split('```')[1].split('```')[0].strip()
            else:
                json_str = content

            return json.loads(json_str)
        except json.JSONDecodeError:
            return {"raw_analysis": content}

    def comprehensive_analysis(self, image_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Run a comprehensive analysis combining all analysis types.

        Args:
            image_path: Path to the reference image

        Returns:
            Dictionary containing all analysis results
        """
        print("Running comprehensive OpenAI Vision analysis...")

        results = {
            "style_analysis": self.analyze_design_style(image_path),
            "components": self.identify_components(image_path),
            "design_tokens": self.extract_design_tokens(image_path)
        }

        return results

    def compare_designs(
        self,
        image_path1: Union[str, Path],
        image_path2: Union[str, Path]
    ) -> Dict[str, Any]:
        """
        Compare two UI designs and identify similarities and differences.

        Args:
            image_path1: Path to first reference image
            image_path2: Path to second reference image

        Returns:
            Dictionary containing comparison results
        """
        base64_image1 = self.encode_image(image_path1)
        base64_image2 = self.encode_image(image_path2)

        prompt = """Compare these two UI designs and identify:

1. **Similarities**: What visual elements do they share?
2. **Differences**: How do they differ in style, approach, or execution?
3. **Design System Compatibility**: Could they be part of the same design system?
4. **Recommended Approach**: If creating a unified system, which elements should be adopted?

Return as JSON with keys: similarities, differences, compatibility_score (0-100), recommendations."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image1}"
                            }
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image2}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )

        content = response.choices[0].message.content

        try:
            if '```json' in content:
                json_str = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                json_str = content.split('```')[1].split('```')[0].strip()
            else:
                json_str = content

            return json.loads(json_str)
        except json.JSONDecodeError:
            return {"raw_analysis": content}


# Convenience function
def analyze_ui_with_vision(image_path: Union[str, Path], api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Quick convenience function to run comprehensive analysis.

    Args:
        image_path: Path to the reference image
        api_key: Optional OpenAI API key

    Returns:
        Comprehensive analysis results
    """
    analyzer = OpenAIVisionAnalyzer(api_key=api_key)
    return analyzer.comprehensive_analysis(image_path)

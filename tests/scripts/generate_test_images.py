#!/usr/bin/env python3
"""
Generate test images using OpenAI DALL-E for color extraction pipeline testing.

This script creates UI mockup images with specific color palettes
that can be used to validate the color extraction pipeline.

Usage:
    python tests/scripts/generate_test_images.py

Environment:
    OPENAI_API_KEY: Your OpenAI API key

Output:
    Images saved to tests/fixtures/generated_images/
"""

import asyncio
import base64
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


async def generate_test_images():
    """Generate test UI images using OpenAI DALL-E."""
    try:
        import openai
    except ImportError:
        print("OpenAI package not installed. Install with: pip install openai")
        return

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY not set. Skipping image generation.")
        print("To generate images, set: export OPENAI_API_KEY=your-key")
        return

    client = openai.OpenAI(api_key=api_key)

    # Output directory
    output_dir = Path(__file__).parent.parent / "fixtures" / "generated_images"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Test image prompts with expected color palettes
    test_prompts = [
        {
            "name": "dashboard_ui",
            "prompt": """A modern web dashboard UI design with a clean layout.
            Color palette:
            - Primary blue (#0066FF) for buttons and highlights
            - Dark gray (#333333) for text
            - Light gray (#F5F5F5) for background
            - Green (#10B981) for success states
            - Red (#EF4444) for errors
            Flat design, minimal shadows, professional look.""",
            "expected_colors": ["#0066FF", "#333333", "#F5F5F5", "#10B981", "#EF4444"],
        },
        {
            "name": "ecommerce_product",
            "prompt": """An e-commerce product page UI mockup.
            Color palette:
            - Orange (#FF6B35) for call-to-action buttons
            - Navy blue (#1E3A5F) for headers
            - White (#FFFFFF) background
            - Teal (#00A896) for accents
            - Light pink (#FFE8E8) for sale badges
            Clean, modern design with clear hierarchy.""",
            "expected_colors": ["#FF6B35", "#1E3A5F", "#FFFFFF", "#00A896", "#FFE8E8"],
        },
        {
            "name": "mobile_app_dark",
            "prompt": """A dark mode mobile app interface design.
            Color palette:
            - Dark background (#121212)
            - Purple accent (#8B5CF6)
            - White text (#FFFFFF)
            - Gray secondary (#6B7280)
            - Gradient blue (#3B82F6)
            Sleek, modern dark theme with good contrast.""",
            "expected_colors": ["#121212", "#8B5CF6", "#FFFFFF", "#6B7280", "#3B82F6"],
        },
        {
            "name": "landing_page_warm",
            "prompt": """A warm-toned marketing landing page design.
            Color palette:
            - Coral (#FF7F50) primary
            - Peach (#FFDAB9) background
            - Dark brown (#5D4037) text
            - Gold (#FFD700) highlights
            - Cream (#FFFDD0) secondary background
            Inviting, friendly design with organic shapes.""",
            "expected_colors": ["#FF7F50", "#FFDAB9", "#5D4037", "#FFD700", "#FFFDD0"],
        },
        {
            "name": "analytics_dashboard",
            "prompt": """A data analytics dashboard with charts and graphs.
            Color palette:
            - Indigo (#4F46E5) primary charts
            - Cyan (#06B6D4) secondary data
            - Gray (#9CA3AF) neutral elements
            - White (#FFFFFF) background
            - Pink (#EC4899) highlights
            - Yellow (#FBBF24) alerts
            Professional, data-focused design with multiple chart colors.""",
            "expected_colors": ["#4F46E5", "#06B6D4", "#9CA3AF", "#FFFFFF", "#EC4899", "#FBBF24"],
        },
    ]

    print(f"Generating {len(test_prompts)} test images...")

    for i, test in enumerate(test_prompts, 1):
        print(f"\n[{i}/{len(test_prompts)}] Generating: {test['name']}")

        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=test["prompt"],
                size="1024x1024",
                quality="standard",
                n=1,
                response_format="b64_json",
            )

            # Save the image
            image_data = base64.b64decode(response.data[0].b64_json)
            image_path = output_dir / f"{test['name']}.png"

            with open(image_path, "wb") as f:
                f.write(image_data)

            print(f"   Saved: {image_path}")

            # Save expected colors metadata
            meta_path = output_dir / f"{test['name']}_expected.txt"
            with open(meta_path, "w") as f:
                f.write(f"Expected colors for {test['name']}:\n")
                for color in test["expected_colors"]:
                    f.write(f"  {color}\n")

            print(f"   Expected colors: {', '.join(test['expected_colors'])}")

        except Exception as e:
            print(f"   Error generating {test['name']}: {e}")
            continue

    print("\n" + "=" * 50)
    print("Test image generation complete!")
    print(f"Images saved to: {output_dir}")
    print("\nYou can now run color extraction tests against these images.")


def create_simple_test_images():
    """Create simple solid color test images using PIL (no API needed)."""
    try:
        from PIL import Image
    except ImportError:
        print("PIL not installed. Install with: pip install Pillow")
        return

    output_dir = Path(__file__).parent.parent / "fixtures" / "simple_test_images"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Simple test patterns
    patterns = [
        {
            "name": "primary_colors",
            "colors": ["#FF0000", "#00FF00", "#0000FF"],
            "desc": "Primary RGB colors",
        },
        {
            "name": "grayscale",
            "colors": ["#000000", "#555555", "#AAAAAA", "#FFFFFF"],
            "desc": "Grayscale spectrum",
        },
        {
            "name": "warm_palette",
            "colors": ["#FF5733", "#FFC300", "#FF8D1A", "#C70039"],
            "desc": "Warm color palette",
        },
        {
            "name": "cool_palette",
            "colors": ["#3498DB", "#2ECC71", "#1ABC9C", "#9B59B6"],
            "desc": "Cool color palette",
        },
        {
            "name": "pastel",
            "colors": ["#FFB3BA", "#BAFFC9", "#BAE1FF", "#FFFFBA"],
            "desc": "Pastel colors",
        },
        {
            "name": "high_contrast",
            "colors": ["#000000", "#FFFFFF", "#FF0000", "#00FF00"],
            "desc": "High contrast for WCAG testing",
        },
        {
            "name": "similar_reds",
            "colors": ["#FF0000", "#FE0000", "#FF0101", "#FE0101"],
            "desc": "Similar reds for Delta-E deduplication testing",
        },
    ]

    print(f"Creating {len(patterns)} simple test images...")

    for pattern in patterns:
        # Create image with color stripes
        colors = pattern["colors"]
        width = 800
        height = 600
        stripe_height = height // len(colors)

        img = Image.new("RGB", (width, height))

        for i, color_hex in enumerate(colors):
            r = int(color_hex[1:3], 16)
            g = int(color_hex[3:5], 16)
            b = int(color_hex[5:7], 16)

            for y in range(i * stripe_height, (i + 1) * stripe_height):
                for x in range(width):
                    img.putpixel((x, y), (r, g, b))

        # Save image
        image_path = output_dir / f"{pattern['name']}.png"
        img.save(image_path)
        print(f"  Created: {pattern['name']}.png - {pattern['desc']}")

        # Save metadata
        meta_path = output_dir / f"{pattern['name']}_colors.txt"
        with open(meta_path, "w") as f:
            f.write(f"Colors in {pattern['name']}:\n")
            for color in colors:
                f.write(f"  {color}\n")

    print(f"\nSimple test images saved to: {output_dir}")


async def main():
    """Main entry point."""
    print("=" * 50)
    print("Color Pipeline Test Image Generator")
    print("=" * 50)

    # Always create simple test images (no API needed)
    print("\n1. Creating simple test images (no API required)...")
    create_simple_test_images()

    # Generate DALL-E images if API key is available
    print("\n2. Generating AI test images (requires OPENAI_API_KEY)...")
    await generate_test_images()


if __name__ == "__main__":
    asyncio.run(main())

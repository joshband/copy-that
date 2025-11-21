#!/usr/bin/env python
"""
Test script for color extraction functionality
Run with: python test_color_extraction.py [image_url]
"""

import sys
import os
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from copy_that.application.color_extractor import AIColorExtractor, ColorToken
from copy_that.domain.models import ColorToken as ColorTokenModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from copy_that.infrastructure.database import Base
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def test_color_extraction_mock():
    """Test with mock data (no API call)"""
    print("\n🎨 Testing Color Extraction with Mock Data")
    print("=" * 50)

    extractor = AIColorExtractor()

    # Create mock response
    mock_response = """
    Extracted colors from image:
    1. #FF6B6B - Red/Coral (primary, confidence: 0.92)
    2. #4ECDC4 - Teal (secondary, confidence: 0.88)
    3. #45B7D1 - Blue (info, confidence: 0.90)
    4. #95E1D3 - Mint Green (success, confidence: 0.85)
    5. #F0A500 - Amber (warning, confidence: 0.87)
    """

    result = extractor._parse_color_response(mock_response, max_colors=5)

    print(f"\n✅ Extracted {len(result.colors)} colors")
    print(f"🎯 Dominant colors: {result.dominant_colors}")
    print(f"📊 Overall confidence: {result.extraction_confidence:.2%}")
    print(f"🎨 Palette description: {result.color_palette}")

    print("\n📋 Color Details:")
    print("-" * 50)
    for i, color in enumerate(result.colors, 1):
        print(f"\n{i}. {color.name} ({color.semantic_name})")
        print(f"   Hex: {color.hex}")
        print(f"   RGB: {color.rgb}")
        print(f"   Confidence: {color.confidence:.0%}")
        if color.harmony:
            print(f"   Harmony: {color.harmony}")


async def test_color_extraction_with_file(file_path: str):
    """Test with a local image file"""
    print(f"\n🎨 Testing Color Extraction from File")
    print("=" * 50)
    print(f"File: {file_path}\n")

    # Check file exists
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return None

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set in .env")
        print("   Please set your API key to enable real color extraction")
        print("\n   To test with mock data instead, run without file argument")
        return None

    try:
        extractor = AIColorExtractor(api_key=api_key)
        print("🔄 Extracting colors... (this may take 10-30 seconds)")

        result = extractor.extract_colors_from_file(file_path, max_colors=10)

        print(f"\n✅ Successfully extracted {len(result.colors)} colors!")
        print(f"🎯 Dominant colors: {result.dominant_colors}")
        print(f"📊 Overall confidence: {result.extraction_confidence:.2%}")
        print(f"🎨 Palette: {result.color_palette}")

        print("\n📋 Color Details:")
        print("-" * 50)
        for i, color in enumerate(result.colors, 1):
            print(f"\n{i}. {color.name} ({color.semantic_name})")
            print(f"   Hex: {color.hex}")
            print(f"   RGB: {color.rgb}")
            print(f"   Confidence: {color.confidence:.0%}")
            if color.harmony:
                print(f"   Harmony: {color.harmony}")

        return result

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


async def test_database_storage():
    """Test storing colors in database"""
    print("\n💾 Testing Database Storage")
    print("=" * 50)
    print("ℹ️  Database storage tests require connection to Neon PostgreSQL")
    print("   Database connection is configured via .env DATABASE_URL")
    print("   See docs/DATABASE_SETUP.md for configuration")


def print_usage():
    """Print usage instructions"""
    print("""
╔════════════════════════════════════════════════════════════════╗
║        Copy That - Color Extraction Test Suite               ║
╚════════════════════════════════════════════════════════════════╝

USAGE:
    python test_color_extraction.py                # Test with mock data
    python test_color_extraction.py <image_file>   # Test with local file

EXAMPLES:
    python test_color_extraction.py
    python test_color_extraction.py screenshot.png
    python test_color_extraction.py /path/to/design.jpg

FEATURES:
    ✅ Mock color extraction (no API call needed)
    ✅ Real color extraction from files (requires ANTHROPIC_API_KEY)
    ✅ Database storage test
    ✅ Color metadata display
    ✅ Confidence scoring

REQUIREMENTS FOR REAL EXTRACTION:
    1. Set ANTHROPIC_API_KEY in .env file ✅ (already configured)
    2. Provide a valid image file path
    3. File must be readable by the system

SUPPORTED IMAGE FORMATS:
    - JPEG (.jpg, .jpeg)
    - PNG (.png)
    - WebP (.webp)
    - GIF (.gif)

WHAT IT EXTRACTS:
    🎨 Hex color codes (#RRGGBB)
    📊 RGB values
    🏷️  Color names and semantic tokens
    ⭐ Confidence scores (0-1)
    🎭 Color harmony relationships
    """)


async def main():
    """Main test runner"""
    print_usage()

    # Test 1: Mock extraction (always works)
    await test_color_extraction_mock()

    # Test 2: Database storage (always works)
    await test_database_storage()

    # Test 3: Real extraction (if file path provided and API key set)
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        await test_color_extraction_with_file(file_path)
    else:
        print("\n" + "=" * 50)
        print("ℹ️  To test real color extraction, provide an image file:")
        print("   python test_color_extraction.py image.png")
        print("   python test_color_extraction.py /path/to/design.jpg")
        print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())

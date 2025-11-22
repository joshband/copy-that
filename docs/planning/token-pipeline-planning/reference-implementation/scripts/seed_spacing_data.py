#!/usr/bin/env python3
"""
Seed Spacing Token Data for Development Testing

REFERENCE IMPLEMENTATION - This is planning/documentation code showing how the
seed data script should be structured when implemented. This script is not
meant to be run directly but serves as a complete reference for implementing
the actual seed process.

This script:
1. Creates sample spacing tokens in the database
2. Provides realistic test data for development
3. Can be run multiple times safely (idempotent)
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# When implemented, these would be actual imports:
# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
# from sqlalchemy.ext.asyncio import async_sessionmaker
# from copy_that.infrastructure.database import Base
# from copy_that.domain.models import Project, SpacingToken


# =============================================================================
# Sample Spacing Token Data
# =============================================================================

SAMPLE_SPACING_TOKENS = [
    # Extra small spacing values
    {
        "value_px": 2,
        "value_rem": 0.125,
        "value_em": 0.125,
        "scale": "3xs",
        "base_unit": 1,
        "multiplier": 2.0,
        "name": "hairline",
        "spacing_type": "padding",
        "design_intent": "minimal separation",
        "use_case": "icon padding, tight borders",
        "context": "icon container",
        "confidence": 0.82,
        "is_grid_compliant": False,
        "rhythm_consistency": "irregular",
    },
    {
        "value_px": 4,
        "value_rem": 0.25,
        "value_em": 0.25,
        "scale": "2xs",
        "base_unit": 4,
        "multiplier": 1.0,
        "name": "tight",
        "spacing_type": "padding",
        "design_intent": "compact elements",
        "use_case": "badge padding, small buttons",
        "context": "notification badge",
        "confidence": 0.88,
        "is_grid_compliant": True,
        "rhythm_consistency": "consistent",
    },
    # Small spacing values
    {
        "value_px": 8,
        "value_rem": 0.5,
        "value_em": 0.5,
        "scale": "xs",
        "base_unit": 8,
        "multiplier": 1.0,
        "name": "compact",
        "spacing_type": "padding",
        "design_intent": "efficient touch targets",
        "use_case": "button padding, form inputs",
        "context": "primary button",
        "confidence": 0.95,
        "is_grid_compliant": True,
        "rhythm_consistency": "consistent",
    },
    {
        "value_px": 12,
        "value_rem": 0.75,
        "value_em": 0.75,
        "scale": "sm",
        "base_unit": 4,
        "multiplier": 3.0,
        "name": "snug",
        "spacing_type": "gap",
        "design_intent": "related items grouping",
        "use_case": "form field gaps, list item spacing",
        "context": "form layout",
        "confidence": 0.91,
        "is_grid_compliant": True,
        "rhythm_consistency": "consistent",
    },
    # Medium spacing values
    {
        "value_px": 16,
        "value_rem": 1.0,
        "value_em": 1.0,
        "scale": "md",
        "base_unit": 8,
        "multiplier": 2.0,
        "name": "comfortable",
        "spacing_type": "padding",
        "design_intent": "standard reading comfort",
        "use_case": "card padding, section padding",
        "context": "content card",
        "confidence": 0.97,
        "is_grid_compliant": True,
        "rhythm_consistency": "consistent",
    },
    {
        "value_px": 20,
        "value_rem": 1.25,
        "value_em": 1.25,
        "scale": "md",
        "base_unit": 4,
        "multiplier": 5.0,
        "name": "default",
        "spacing_type": "margin",
        "design_intent": "standard element separation",
        "use_case": "component margins",
        "context": "card component margin",
        "confidence": 0.89,
        "is_grid_compliant": True,
        "rhythm_consistency": "consistent",
    },
    # Large spacing values
    {
        "value_px": 24,
        "value_rem": 1.5,
        "value_em": 1.5,
        "scale": "lg",
        "base_unit": 8,
        "multiplier": 3.0,
        "name": "relaxed",
        "spacing_type": "gap",
        "design_intent": "clear visual separation",
        "use_case": "grid gaps, section separation",
        "context": "product grid",
        "confidence": 0.94,
        "is_grid_compliant": True,
        "rhythm_consistency": "consistent",
    },
    {
        "value_px": 32,
        "value_rem": 2.0,
        "value_em": 2.0,
        "scale": "xl",
        "base_unit": 8,
        "multiplier": 4.0,
        "name": "spacious",
        "spacing_type": "padding",
        "design_intent": "generous whitespace",
        "use_case": "hero sections, feature blocks",
        "context": "hero section",
        "confidence": 0.93,
        "is_grid_compliant": True,
        "rhythm_consistency": "consistent",
    },
    # Extra large spacing values
    {
        "value_px": 40,
        "value_rem": 2.5,
        "value_em": 2.5,
        "scale": "xl",
        "base_unit": 8,
        "multiplier": 5.0,
        "name": "generous",
        "spacing_type": "margin",
        "design_intent": "major section separation",
        "use_case": "page section margins",
        "context": "page section",
        "confidence": 0.87,
        "is_grid_compliant": True,
        "rhythm_consistency": "consistent",
    },
    {
        "value_px": 48,
        "value_rem": 3.0,
        "value_em": 3.0,
        "scale": "2xl",
        "base_unit": 8,
        "multiplier": 6.0,
        "name": "loose",
        "spacing_type": "padding",
        "design_intent": "prominent visual breathing room",
        "use_case": "modal padding, feature sections",
        "context": "modal dialog",
        "confidence": 0.90,
        "is_grid_compliant": True,
        "rhythm_consistency": "consistent",
    },
    {
        "value_px": 64,
        "value_rem": 4.0,
        "value_em": 4.0,
        "scale": "3xl",
        "base_unit": 8,
        "multiplier": 8.0,
        "name": "extra-loose",
        "spacing_type": "margin",
        "design_intent": "maximum visual impact",
        "use_case": "page margins, major section dividers",
        "context": "landing page section",
        "confidence": 0.85,
        "is_grid_compliant": True,
        "rhythm_consistency": "consistent",
    },
    # Special use cases
    {
        "value_px": 96,
        "value_rem": 6.0,
        "value_em": 6.0,
        "scale": "4xl",
        "base_unit": 8,
        "multiplier": 12.0,
        "name": "huge",
        "spacing_type": "margin",
        "design_intent": "dramatic visual separation",
        "use_case": "hero margins, showcase sections",
        "context": "hero image container",
        "confidence": 0.78,
        "is_grid_compliant": True,
        "rhythm_consistency": "consistent",
    },
]


def generate_responsive_scales(value_px: int) -> dict:
    """Generate responsive scale values for a spacing value."""
    return {
        "mobile": int(value_px * 0.75),
        "tablet": value_px,
        "desktop": int(value_px * 1.25),
        "widescreen": int(value_px * 1.5),
    }


def generate_semantic_names(token: dict) -> dict:
    """Generate semantic names for a spacing token."""
    return {
        "simple": token["scale"],
        "descriptive": f"{token['scale']}-{token['spacing_type']}",
        "contextual": f"{token['context'].lower().replace(' ', '-')}-spacing",
        "scale_position": f"spacing-{token['value_px'] // 4}",
        "semantic": token["name"],
    }


def generate_extraction_metadata() -> dict:
    """Generate extraction metadata for a token."""
    return {
        "computation_version": "1.0",
        "algorithms_used": ["unit_conversion", "scale_detection", "grid_analysis"],
        "computation_timestamp": datetime.utcnow().isoformat(),
        "source": "seed_script",
    }


async def seed_spacing_tokens(
    session: Any,  # AsyncSession when implemented
    project_id: int,
    clear_existing: bool = False
) -> int:
    """
    Seed spacing tokens into the database.

    Args:
        session: Database session
        project_id: Project ID to associate tokens with
        clear_existing: If True, delete existing tokens first

    Returns:
        Number of tokens created
    """
    print(f"Seeding spacing tokens for project {project_id}...")

    # When implemented:
    # if clear_existing:
    #     await session.execute(
    #         delete(SpacingToken).where(SpacingToken.project_id == project_id)
    #     )
    #     await session.commit()
    #     print("Cleared existing spacing tokens")

    tokens_created = 0

    for token_data in SAMPLE_SPACING_TOKENS:
        # Add computed fields
        token_data["responsive_scales"] = generate_responsive_scales(token_data["value_px"])
        token_data["semantic_names"] = generate_semantic_names(token_data)
        token_data["extraction_metadata"] = generate_extraction_metadata()

        # When implemented:
        # token = SpacingToken(
        #     project_id=project_id,
        #     **token_data
        # )
        # session.add(token)

        tokens_created += 1
        print(f"  Created: {token_data['name']} ({token_data['value_px']}px)")

    # When implemented:
    # await session.commit()

    print(f"\nCreated {tokens_created} spacing tokens")
    return tokens_created


async def create_sample_project(session: Any) -> int:
    """
    Create a sample project for spacing tokens.

    Returns:
        Project ID
    """
    # When implemented:
    # project = Project(
    #     name="Sample Design System",
    #     description="Sample project for spacing token development",
    # )
    # session.add(project)
    # await session.commit()
    # await session.refresh(project)
    # return project.id

    print("Created sample project: Sample Design System")
    return 1


async def print_seeded_data_summary(session: Any, project_id: int):
    """Print a summary of the seeded data."""
    print("\n" + "=" * 60)
    print("SEEDED DATA SUMMARY")
    print("=" * 60)

    # When implemented:
    # from sqlalchemy import func
    # result = await session.execute(
    #     select(
    #         func.count(SpacingToken.id),
    #         func.min(SpacingToken.value_px),
    #         func.max(SpacingToken.value_px),
    #         func.avg(SpacingToken.confidence),
    #     ).where(SpacingToken.project_id == project_id)
    # )
    # count, min_px, max_px, avg_conf = result.first()

    # Mock values for reference
    count = len(SAMPLE_SPACING_TOKENS)
    min_px = min(t["value_px"] for t in SAMPLE_SPACING_TOKENS)
    max_px = max(t["value_px"] for t in SAMPLE_SPACING_TOKENS)
    avg_conf = sum(t["confidence"] for t in SAMPLE_SPACING_TOKENS) / count

    print(f"\nProject ID: {project_id}")
    print(f"Total spacing tokens: {count}")
    print(f"Value range: {min_px}px - {max_px}px")
    print(f"Average confidence: {avg_conf:.2f}")

    # Print scale distribution
    print("\nScale distribution:")
    scale_counts: dict[str, int] = {}
    for token in SAMPLE_SPACING_TOKENS:
        scale = token["scale"]
        scale_counts[scale] = scale_counts.get(scale, 0) + 1

    for scale, count in sorted(scale_counts.items()):
        print(f"  {scale}: {count}")

    # Print type distribution
    print("\nSpacing type distribution:")
    type_counts: dict[str, int] = {}
    for token in SAMPLE_SPACING_TOKENS:
        spacing_type = token["spacing_type"]
        type_counts[spacing_type] = type_counts.get(spacing_type, 0) + 1

    for spacing_type, count in sorted(type_counts.items()):
        print(f"  {spacing_type}: {count}")

    print("\n" + "=" * 60)


async def main():
    """Main entry point for the seed script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Seed spacing token data for development testing"
    )
    parser.add_argument(
        "--project-id",
        type=int,
        default=None,
        help="Project ID to seed tokens for (creates new if not specified)"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing tokens before seeding"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be created without actually creating"
    )
    parser.add_argument(
        "--database-url",
        type=str,
        default=None,
        help="Database URL (defaults to DATABASE_URL env var)"
    )

    args = parser.parse_args()

    # When implemented:
    # import os
    # database_url = args.database_url or os.environ.get("DATABASE_URL")
    # if not database_url:
    #     print("Error: DATABASE_URL not set")
    #     sys.exit(1)

    # engine = create_async_engine(database_url)
    # async_session = async_sessionmaker(engine, class_=AsyncSession)

    # async with async_session() as session:
    #     if args.project_id:
    #         project_id = args.project_id
    #     else:
    #         project_id = await create_sample_project(session)

    #     if args.dry_run:
    #         print("\nDRY RUN - No data will be created\n")
    #         print("Would create the following tokens:\n")
    #         for token in SAMPLE_SPACING_TOKENS:
    #             print(f"  - {token['name']}: {token['value_px']}px ({token['scale']})")
    #     else:
    #         await seed_spacing_tokens(session, project_id, args.clear)
    #         await print_seeded_data_summary(session, project_id)

    # For reference implementation, just print what would be done
    print("\n" + "=" * 60)
    print("REFERENCE IMPLEMENTATION - Seed Script")
    print("=" * 60)

    if args.dry_run:
        print("\nDRY RUN - Would create the following tokens:\n")
    else:
        print("\nTokens that would be created:\n")

    for token in SAMPLE_SPACING_TOKENS:
        print(f"  - {token['name']}: {token['value_px']}px ({token['scale']}, {token['spacing_type']})")

    # Print summary
    await print_seeded_data_summary(None, args.project_id or 1)

    print("\nTo run this script with actual database:")
    print("  1. Set DATABASE_URL environment variable")
    print("  2. Implement the database models")
    print("  3. Uncomment the SQLAlchemy code above")
    print("  4. Run: python seed_spacing_data.py")


if __name__ == "__main__":
    asyncio.run(main())

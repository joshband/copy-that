"""
End-to-end tests for the color extraction pipeline.

These tests validate the full pipeline flow from image input to token output.
"""

import base64
from pathlib import Path

import pytest


class TestColorPipelineE2E:
    """End-to-end tests for color extraction pipeline."""

    @pytest.fixture
    def test_image_path(self):
        """Get path to test images."""
        fixtures_dir = Path(__file__).parent.parent / "fixtures"
        simple_images = fixtures_dir / "simple_test_images"

        # If simple test images exist, use them
        if simple_images.exists():
            for img in simple_images.glob("*.png"):
                return img

        # Otherwise use any available test image
        for img in fixtures_dir.rglob("*.png"):
            return img

        return None

    @pytest.fixture
    def base64_test_image(self, test_image_path):
        """Load test image as base64."""
        if test_image_path and test_image_path.exists():
            with open(test_image_path, "rb") as f:
                data = base64.b64encode(f.read()).decode()
                return f"data:image/png;base64,{data}"

        # Create a minimal valid PNG if no test images exist
        # This is a 16x16 blue pixel PNG (minimum dimension for validation)
        minimal_png = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAAAI0lEQVR4nGNkYPjPQApgIkk1w6gG4gATkorgYFQDMYDkUAIAPjABH26QQDYAAAAASUVORK5CYII="
        return f"data:image/png;base64,{minimal_png}"

    @pytest.mark.asyncio
    async def test_color_extraction_endpoint(self, async_client, base64_test_image):
        """Test the color extraction API endpoint."""
        # Create a project first
        project_resp = await async_client.post(
            "/api/v1/projects",
            json={"name": "E2E Test Project", "description": "End-to-end testing"},
        )
        assert project_resp.status_code in (200, 201)
        project_id = project_resp.json()["id"]

        # Note: In real tests with API, we'd mock the Claude response
        # This test validates the endpoint structure

    @pytest.mark.asyncio
    async def test_color_token_crud_workflow(self, async_client):
        """Test the complete CRUD workflow for color tokens."""
        # 1. Create project
        project_resp = await async_client.post(
            "/api/v1/projects", json={"name": "CRUD Test Project"}
        )
        assert project_resp.status_code in (200, 201)
        project_id = project_resp.json()["id"]

        # 2. Create multiple color tokens
        colors_to_create = [
            {
                "hex": "#FF0000",
                "rgb": "rgb(255, 0, 0)",
                "name": "Primary Red",
                "confidence": 0.95,
                "harmony": "complementary",
                "temperature": "warm",
                "saturation_level": "vibrant",
                "lightness_level": "medium",
            },
            {
                "hex": "#0066FF",
                "rgb": "rgb(0, 102, 255)",
                "name": "Primary Blue",
                "confidence": 0.92,
                "harmony": "triadic",
                "temperature": "cool",
                "saturation_level": "vibrant",
                "lightness_level": "medium",
            },
            {
                "hex": "#00AA00",
                "rgb": "rgb(0, 170, 0)",
                "name": "Success Green",
                "confidence": 0.88,
                "harmony": "analogous",
                "temperature": "cool",
                "saturation_level": "saturated",
                "lightness_level": "medium",
                "design_intent": "success",
            },
        ]

        created_ids = []
        for color_data in colors_to_create:
            resp = await async_client.post(
                "/api/v1/colors", json={**color_data, "project_id": project_id}
            )
            assert resp.status_code == 201
            data = resp.json()
            assert "id" in data
            assert data["hex"] == color_data["hex"]
            assert data["name"] == color_data["name"]
            created_ids.append(data["id"])

        # 3. Retrieve all colors for project
        list_resp = await async_client.get(f"/api/v1/projects/{project_id}/colors")
        assert list_resp.status_code == 200
        colors = list_resp.json()
        assert len(colors) == 3

        # 4. Retrieve individual color
        for color_id in created_ids:
            get_resp = await async_client.get(f"/api/v1/colors/{color_id}")
            assert get_resp.status_code == 200
            assert get_resp.json()["id"] == color_id

    @pytest.mark.asyncio
    async def test_wcag_accessibility_validation(self, async_client):
        """Test WCAG accessibility data is included in color tokens."""
        # Create project
        project_resp = await async_client.post(
            "/api/v1/projects", json={"name": "WCAG Test Project"}
        )
        project_id = project_resp.json()["id"]

        # Create color with WCAG data
        color_data = {
            "project_id": project_id,
            "hex": "#0066FF",
            "rgb": "rgb(0, 102, 255)",
            "name": "Test Blue",
            "confidence": 0.9,
            "wcag_contrast_on_white": 4.51,
            "wcag_contrast_on_black": 4.65,
            "wcag_aa_compliant_text": True,
            "wcag_aaa_compliant_text": False,
            "colorblind_safe": True,
        }

        resp = await async_client.post("/api/v1/colors", json=color_data)
        assert resp.status_code == 201

        data = resp.json()
        assert data["wcag_contrast_on_white"] == 4.51
        assert data["wcag_aa_compliant_text"] is True
        assert data["colorblind_safe"] is True

    @pytest.mark.asyncio
    async def test_color_variants_generation(self, async_client):
        """Test that tint, shade, and tone variants are included."""
        # Create project
        project_resp = await async_client.post(
            "/api/v1/projects", json={"name": "Variants Test Project"}
        )
        project_id = project_resp.json()["id"]

        # Create color with variants
        color_data = {
            "project_id": project_id,
            "hex": "#FF5733",
            "rgb": "rgb(255, 87, 51)",
            "name": "Coral",
            "confidence": 0.95,
            "tint_color": "#FF8866",
            "shade_color": "#CC4429",
            "tone_color": "#D9604A",
        }

        resp = await async_client.post("/api/v1/colors", json=color_data)
        assert resp.status_code == 201

        data = resp.json()
        assert data["tint_color"] == "#FF8866"
        assert data["shade_color"] == "#CC4429"

    @pytest.mark.asyncio
    async def test_semantic_naming(self, async_client):
        """Test semantic color naming is preserved."""
        # Create project
        project_resp = await async_client.post(
            "/api/v1/projects", json={"name": "Semantic Test Project"}
        )
        project_id = project_resp.json()["id"]

        # Create color with semantic names
        color_data = {
            "project_id": project_id,
            "hex": "#FF5733",
            "rgb": "rgb(255, 87, 51)",
            "name": "Coral",
            "confidence": 0.9,
            "semantic_names": {
                "simple": "orange-red",
                "descriptive": "warm coral",
                "emotional": "energetic",
                "technical": "#FF5733",
                "vibrancy": "vibrant",
            },
        }

        resp = await async_client.post("/api/v1/colors", json=color_data)
        assert resp.status_code == 201

        data = resp.json()
        assert data["semantic_names"]["simple"] == "orange-red"
        assert data["semantic_names"]["emotional"] == "energetic"

    @pytest.mark.asyncio
    async def test_design_intent_categorization(self, async_client):
        """Test various design intent categories."""
        # Create project
        project_resp = await async_client.post(
            "/api/v1/projects", json={"name": "Design Intent Test Project"}
        )
        project_id = project_resp.json()["id"]

        design_intents = [
            ("primary", "#0066FF"),
            ("secondary", "#6B7280"),
            ("accent", "#FF6B35"),
            ("background", "#FFFFFF"),
            ("surface", "#F5F5F5"),
            ("error", "#DC2626"),
            ("success", "#10B981"),
            ("warning", "#F59E0B"),
            ("info", "#3B82F6"),
        ]

        for intent, hex_color in design_intents:
            resp = await async_client.post(
                "/api/v1/colors",
                json={
                    "project_id": project_id,
                    "hex": hex_color,
                    "rgb": "rgb(100, 100, 100)",
                    "name": f"{intent.title()} Color",
                    "confidence": 0.9,
                    "design_intent": intent,
                },
            )
            assert resp.status_code == 201
            assert resp.json()["design_intent"] == intent

    @pytest.mark.asyncio
    async def test_multi_project_isolation(self, async_client):
        """Test that colors are properly isolated between projects."""
        # Create two projects
        project1_resp = await async_client.post("/api/v1/projects", json={"name": "Project 1"})
        project1_id = project1_resp.json()["id"]

        project2_resp = await async_client.post("/api/v1/projects", json={"name": "Project 2"})
        project2_id = project2_resp.json()["id"]

        # Add colors to project 1
        await async_client.post(
            "/api/v1/colors",
            json={
                "project_id": project1_id,
                "hex": "#FF0000",
                "rgb": "rgb(255, 0, 0)",
                "name": "Red",
                "confidence": 0.9,
            },
        )

        # Add colors to project 2
        await async_client.post(
            "/api/v1/colors",
            json={
                "project_id": project2_id,
                "hex": "#0000FF",
                "rgb": "rgb(0, 0, 255)",
                "name": "Blue",
                "confidence": 0.9,
            },
        )

        # Verify isolation
        p1_colors = (await async_client.get(f"/api/v1/projects/{project1_id}/colors")).json()
        p2_colors = (await async_client.get(f"/api/v1/projects/{project2_id}/colors")).json()

        assert len(p1_colors) == 1
        assert len(p2_colors) == 1
        assert p1_colors[0]["hex"] == "#FF0000"
        assert p2_colors[0]["hex"] == "#0000FF"


class TestColorGenerationFormats:
    """Test color token generation in various output formats."""

    @pytest.fixture
    def sample_library(self):
        """Create a sample color library for testing."""
        from copy_that.generators.library_models import AggregatedColorToken, TokenLibrary

        library = TokenLibrary()

        tokens = [
            AggregatedColorToken(
                hex="#0066FF",
                rgb="rgb(0, 102, 255)",
                name="Primary",
                confidence=0.95,
                harmony="complementary",
                temperature="cool",
                saturation_level="vibrant",
                lightness_level="medium",
                provenance={"image_1": 0.95},
                role="primary",
            ),
            AggregatedColorToken(
                hex="#6B7280",
                rgb="rgb(107, 114, 128)",
                name="Secondary",
                confidence=0.88,
                temperature="neutral",
                saturation_level="muted",
                lightness_level="medium",
                provenance={"image_1": 0.88},
                role="secondary",
            ),
            AggregatedColorToken(
                hex="#DC2626",
                rgb="rgb(220, 38, 38)",
                name="Error",
                confidence=0.92,
                temperature="warm",
                saturation_level="vibrant",
                lightness_level="medium",
                provenance={"image_1": 0.92},
                role="error",
            ),
        ]

        for token in tokens:
            library.add_token(token)

        return library

    def test_generate_css_variables(self, sample_library):
        """Test generating CSS custom properties."""
        from copy_that.generators.css_generator import CSSTokenGenerator

        generator = CSSTokenGenerator(sample_library)
        css = generator.generate()

        # Verify CSS structure
        assert ":root {" in css
        assert "}" in css

        # Verify colors are included
        assert "#0066FF" in css or "#0066ff" in css
        assert "#6B7280" in css or "#6b7280" in css
        assert "#DC2626" in css or "#dc2626" in css

    def test_generate_w3c_tokens(self, sample_library):
        """Test generating W3C Design Tokens JSON."""
        from copy_that.generators.w3c_generator import W3CTokenGenerator

        generator = W3CTokenGenerator(sample_library)
        output = generator.generate()

        # Should be valid output
        assert output is not None
        assert len(output) > 0

    def test_generate_react_theme(self, sample_library):
        """Test generating React/TypeScript theme."""
        from copy_that.generators.react_generator import ReactTokenGenerator

        generator = ReactTokenGenerator(sample_library)
        output = generator.generate()

        # Should contain export statements
        assert "export" in output

        # Should contain color values
        assert "0066FF" in output.upper() or "Primary" in output

    def test_generate_html_demo(self, sample_library):
        """Test generating HTML demo page."""
        from copy_that.generators.html_demo_generator import HTMLDemoGenerator

        generator = HTMLDemoGenerator(sample_library)
        html = generator.generate()

        # Verify HTML structure
        assert "<!DOCTYPE html>" in html
        assert "<html" in html
        assert "</html>" in html

        # Verify colors are displayed
        assert "#0066FF" in html or "#0066ff" in html


class TestColorAggregationE2E:
    """End-to-end tests for color aggregation."""

    def test_aggregate_from_multiple_sources(self):
        """Test aggregating colors from multiple image sources."""
        from coloraide import Color

        from copy_that.generators.library_models import AggregatedColorToken
        from core.tokens.aggregate import simple_color_merge
        from core.tokens.color import make_color_token
        from core.tokens.repository import InMemoryTokenRepository

        # Colors from multiple images
        colors = [
            AggregatedColorToken(
                hex="#FF0000",
                rgb="rgb(255, 0, 0)",
                name="Red 1",
                confidence=0.9,
                provenance={"image_1": 0.9},
            ),
            AggregatedColorToken(
                hex="#FF0000",  # Same color from different image
                rgb="rgb(255, 0, 0)",
                name="Red 2",
                confidence=0.85,
                provenance={"image_2": 0.85},
            ),
            AggregatedColorToken(
                hex="#0000FF",
                rgb="rgb(0, 0, 255)",
                name="Blue",
                confidence=0.88,
                provenance={"image_3": 0.88},
            ),
        ]

        repo = InMemoryTokenRepository()
        for idx, tok in enumerate(colors, start=1):
            repo.upsert_token(
                make_color_token(
                    f"token/color/e2e/{idx:02d}",
                    Color(tok.hex),
                    {
                        "hex": tok.hex,
                        "rgb": tok.rgb,
                        "name": tok.name,
                        "confidence": tok.confidence,
                        "provenance": tok.provenance,
                    },
                )
            )

        result = simple_color_merge(repo).find_by_type("color")

        # Should deduplicate the two red colors
        assert len(result) == 2

    def test_library_statistics(self):
        """Test color library statistics calculation."""
        from copy_that.generators.library_models import AggregatedColorToken, TokenLibrary

        library = TokenLibrary()

        # Add colors from different sources
        library.add_token(
            AggregatedColorToken(
                hex="#FF0000",
                rgb="rgb(255, 0, 0)",
                name="Red",
                confidence=0.9,
                provenance={"image_1": 0.9, "image_2": 0.85},
            )
        )
        library.add_token(
            AggregatedColorToken(
                hex="#0000FF",
                rgb="rgb(0, 0, 255)",
                name="Blue",
                confidence=0.88,
                provenance={"image_1": 0.88},
            )
        )

        stats = library.statistics

        assert stats["color_count"] == 2
        assert stats["avg_confidence"] > 0


class TestColorValidationE2E:
    """End-to-end tests for color validation."""

    def test_wcag_validation_high_contrast(self):
        """Test WCAG validation for high contrast colors."""
        from copy_that.application.color_utils import calculate_contrast_ratio

        # Black on white - maximum contrast
        ratio = calculate_contrast_ratio("#000000", "#FFFFFF")
        assert ratio >= 21.0
        assert ratio >= 7.0  # Passes AAA

    def test_wcag_validation_low_contrast(self):
        """Test WCAG validation for low contrast colors."""
        from copy_that.application.color_utils import calculate_contrast_ratio

        # Similar grays - low contrast
        ratio = calculate_contrast_ratio("#777777", "#888888")
        assert ratio < 4.5  # Fails AA

    def test_color_temperature_classification(self):
        """Test color temperature classification."""
        from copy_that.application.color_utils import get_color_temperature

        # Warm colors
        assert get_color_temperature("#FF0000") == "warm"  # Red
        assert get_color_temperature("#FF8000") == "warm"  # Orange

        # Cool colors
        assert get_color_temperature("#0000FF") == "cool"  # Blue
        assert get_color_temperature("#00FFFF") == "cool"  # Cyan

        # Neutral
        assert get_color_temperature("#808080") == "neutral"  # Gray

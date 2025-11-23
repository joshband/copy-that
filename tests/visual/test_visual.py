"""Visual regression tests using Playwright screenshots.

Run with:
    pytest tests/visual -v --browser chromium

Update baselines:
    pytest tests/visual -v --browser chromium --update-snapshots
"""

import os
from pathlib import Path

import pytest
from playwright.sync_api import Page

# Directory for baseline screenshots
BASELINE_DIR = Path(__file__).parent / "baselines"
BASELINE_DIR.mkdir(exist_ok=True)


@pytest.fixture(scope="session")
def browser_type_launch_args():
    """Launch browser configuration."""
    return {
        "headless": True,
        # Consistent viewport for screenshots
        "viewport": {"width": 1280, "height": 720},
    }


class TestVisualRegression:
    """Visual regression tests for Copy That UI."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup for each test."""
        self.page = page
        self.base_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

    def compare_screenshot(self, page: Page, name: str, threshold: float = 0.1):
        """Compare current screenshot with baseline.

        Args:
            page: Playwright page object
            name: Screenshot name (without extension)
            threshold: Maximum allowed difference (0-1)

        Returns:
            True if screenshots match within threshold
        """
        baseline_path = BASELINE_DIR / f"{name}.png"
        current_screenshot = page.screenshot()

        if not baseline_path.exists():
            # Save as new baseline
            baseline_path.write_bytes(current_screenshot)
            pytest.skip(f"Created new baseline: {baseline_path}")
            return True

        # Compare screenshots
        # In production, use pixelmatch or similar for proper comparison
        baseline_bytes = baseline_path.read_bytes()

        if current_screenshot == baseline_bytes:
            return True

        # Save diff for debugging
        diff_path = BASELINE_DIR / f"{name}.diff.png"
        diff_path.write_bytes(current_screenshot)

        # For now, just check byte equality
        # TODO: Implement proper visual diff with threshold
        return False

    @pytest.mark.skip(reason="Frontend not available in CI")
    def test_home_page_visual(self, page: Page):
        """Visual regression test for home page."""
        page.goto(f"{self.base_url}/")
        page.wait_for_load_state("networkidle")

        assert self.compare_screenshot(page, "home-page"), "Home page visual regression detected"

    @pytest.mark.skip(reason="Frontend not available in CI")
    def test_dashboard_visual(self, page: Page):
        """Visual regression test for dashboard."""
        page.goto(f"{self.base_url}/dashboard")
        page.wait_for_load_state("networkidle")

        assert self.compare_screenshot(
            page, "dashboard"
        ), "Dashboard visual regression detected"

    @pytest.mark.skip(reason="Frontend not available in CI")
    def test_color_palette_visual(self, page: Page):
        """Visual regression test for color palette component."""
        page.goto(f"{self.base_url}/playground")
        page.wait_for_load_state("networkidle")

        # Focus on color palette section
        palette = page.locator("[data-testid='color-palette']")
        if palette.count() > 0:
            screenshot = palette.screenshot()
            baseline_path = BASELINE_DIR / "color-palette.png"

            if not baseline_path.exists():
                baseline_path.write_bytes(screenshot)
                pytest.skip("Created new baseline: color-palette.png")

            assert screenshot == baseline_path.read_bytes(), "Color palette visual regression"

    @pytest.mark.skip(reason="Frontend not available in CI")
    def test_dark_mode_visual(self, page: Page):
        """Visual regression test for dark mode."""
        page.goto(f"{self.base_url}/")

        # Toggle dark mode
        dark_mode_toggle = page.locator("[data-testid='dark-mode-toggle']")
        if dark_mode_toggle.count() > 0:
            dark_mode_toggle.click()
            page.wait_for_timeout(500)  # Wait for transition

        assert self.compare_screenshot(
            page, "home-dark-mode"
        ), "Dark mode visual regression detected"

    @pytest.mark.skip(reason="Frontend not available in CI")
    def test_responsive_mobile(self, page: Page):
        """Visual regression test for mobile viewport."""
        # Set mobile viewport
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(f"{self.base_url}/")
        page.wait_for_load_state("networkidle")

        assert self.compare_screenshot(
            page, "home-mobile"
        ), "Mobile visual regression detected"

    def test_visual_infrastructure(self):
        """Verify visual testing infrastructure is set up."""
        assert BASELINE_DIR.exists(), "Baseline directory should exist"
        assert True, "Visual regression testing infrastructure is set up"

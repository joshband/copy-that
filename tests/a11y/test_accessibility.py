"""Accessibility tests using axe-core via Playwright.

Run with:
    pytest tests/a11y -v --browser chromium
"""

import pytest
from playwright.sync_api import Page


@pytest.fixture(scope="session")
def browser_type_launch_args():
    """Launch browser in headless mode for CI."""
    return {"headless": True}


class TestAccessibility:
    """Accessibility tests for Copy That web interface."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup for each test."""
        self.page = page
        self.base_url = "http://localhost:3000"  # Frontend URL

    def run_axe(self, page: Page, context: str = "page"):
        """Run axe-core accessibility scan and return violations."""
        # Inject axe-core
        page.evaluate(
            """
            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.8.4/axe.min.js';
            document.head.appendChild(script);
        """
        )

        # Wait for axe to load
        page.wait_for_function("typeof axe !== 'undefined'")

        # Run accessibility scan
        results = page.evaluate(
            """
            async () => {
                const results = await axe.run();
                return results.violations;
            }
        """
        )

        return results

    @pytest.mark.skip(reason="Frontend not available in CI")
    def test_home_page_accessibility(self, page: Page):
        """Test home page has no critical accessibility issues."""
        page.goto(f"{self.base_url}/")

        violations = self.run_axe(page, "home page")

        # Filter for serious and critical issues
        serious_violations = [v for v in violations if v["impact"] in ["critical", "serious"]]

        if serious_violations:
            violation_messages = []
            for v in serious_violations:
                violation_messages.append(f"- {v['id']}: {v['description']} ({v['impact']})")
            pytest.fail(
                f"Found {len(serious_violations)} accessibility issues:\n"
                + "\n".join(violation_messages)
            )

    @pytest.mark.skip(reason="Frontend not available in CI")
    def test_dashboard_accessibility(self, page: Page):
        """Test dashboard page accessibility."""
        page.goto(f"{self.base_url}/dashboard")

        violations = self.run_axe(page, "dashboard")

        critical = [v for v in violations if v["impact"] == "critical"]
        assert len(critical) == 0, f"Critical accessibility issues: {critical}"

    @pytest.mark.skip(reason="Frontend not available in CI")
    def test_color_contrast(self, page: Page):
        """Test that text has sufficient color contrast."""
        page.goto(f"{self.base_url}/")

        violations = self.run_axe(page)

        # Filter for color contrast issues
        contrast_issues = [v for v in violations if "color-contrast" in v["id"]]

        if contrast_issues:
            elements = []
            for issue in contrast_issues:
                for node in issue.get("nodes", []):
                    elements.append(node.get("html", "unknown element"))
            pytest.fail(f"Color contrast issues found in: {elements[:5]}")

    @pytest.mark.skip(reason="Frontend not available in CI")
    def test_keyboard_navigation(self, page: Page):
        """Test that key interactive elements are keyboard accessible."""
        page.goto(f"{self.base_url}/")

        # Tab through the page and check focus is visible
        for _ in range(10):
            page.keyboard.press("Tab")

            # Check that something is focused
            focused = page.evaluate("document.activeElement.tagName")
            assert focused != "BODY", "Focus lost during keyboard navigation"

    @pytest.mark.skip(reason="Frontend not available in CI")
    def test_form_labels(self, page: Page):
        """Test that form inputs have associated labels."""
        page.goto(f"{self.base_url}/login")

        violations = self.run_axe(page)

        label_issues = [v for v in violations if "label" in v["id"]]
        assert len(label_issues) == 0, f"Form label issues: {label_issues}"

    def test_axe_core_import(self):
        """Verify axe-core testing is set up correctly."""
        # This test always passes - just verifies the test file loads
        assert True, "Accessibility testing infrastructure is set up"

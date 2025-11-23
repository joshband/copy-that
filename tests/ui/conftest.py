"""
Pytest configuration for UI tests using Playwright
"""

import pytest


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context for tests"""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
    }


def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line("markers", "ui: UI/E2E tests using Playwright")

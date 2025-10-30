"""
Basic tests for Copy That package
"""
import pytest


def test_package_import():
    """Test that the package can be imported"""
    import src
    assert src.__version__ == "0.1.0"


def test_package_author():
    """Test package author"""
    import src
    assert src.__author__ == "Copy That Team"


@pytest.mark.unit
def test_example():
    """Example unit test"""
    assert 1 + 1 == 2

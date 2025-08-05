"""
Pytest configuration file to set up proper Python path for tests.
"""
import sys
import pytest
from pathlib import Path

# Add the project root to Python path so tests can import project modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def apkg_path():
    """Fixture that provides a path to a test APKG file."""
    # Use the test output file that gets created by test_save_with_4subdecks
    return Path("test_output/4subdeck_compatibility_test.apkg")
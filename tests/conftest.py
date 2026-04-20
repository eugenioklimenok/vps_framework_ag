"""
Pytest configuration and shared fixtures for the VPS Framework test suite.
"""

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_run_command():
    """Fixture to mock utils.subprocess_wrapper.run_command.

    Use this fixture in tests to intercept system commands and return
    deterministic CommandResult objects without hitting the actual OS.
    """
    with patch("utils.subprocess_wrapper.run_command") as mock_func:
        yield mock_func

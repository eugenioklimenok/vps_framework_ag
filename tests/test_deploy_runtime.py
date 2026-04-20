"""
Tests for DEPLOY compose wrapper and smoke logic.
"""

import pytest
from unittest.mock import patch
from pathlib import Path

from models.command_result import CommandResult
from modules.deploy.runtime.compose_wrapper import (
    check_compose_availability,
    validate_compose_config,
    build_compose_stack,
    start_compose_stack,
    inspect_compose_status,
)
from modules.deploy.project.smoke import run_baseline_smoke_test


@patch("modules.deploy.runtime.compose_wrapper.run_command")
def test_check_compose_availability(mock_exec):
    mock_exec.return_value = CommandResult(
        stdout="Docker Compose version v2.20.2",
        stderr="",
        returncode=0,
        timed_out=False,
        error=""
    )
    assert check_compose_availability() is True
    
    mock_exec.return_value = CommandResult(
        stdout="",
        stderr="command not found",
        returncode=127,
        timed_out=False,
        error=""
    )
    assert check_compose_availability() is False


@patch("modules.deploy.project.smoke.inspect_compose_status")
def test_smoke_test_success(mock_inspect, tmp_path):
    # Mocking docker compose ps --format json output
    mock_inspect.return_value = CommandResult(
        stdout='{"Name":"app", "State":"running"}\n',
        stderr="",
        returncode=0,
        timed_out=False,
        error=""
    )
    
    assert run_baseline_smoke_test(tmp_path, tmp_path / ".env", "my-app") is True


@patch("modules.deploy.project.smoke.inspect_compose_status")
def test_smoke_test_failure_exited(mock_inspect, tmp_path):
    mock_inspect.return_value = CommandResult(
        stdout='{"Name":"app", "State":"exited"}\n',
        stderr="",
        returncode=0,
        timed_out=False,
        error=""
    )
    
    assert run_baseline_smoke_test(tmp_path, tmp_path / ".env", "my-app") is False


@patch("modules.deploy.project.smoke.inspect_compose_status")
def test_smoke_test_failure_bad_command(mock_inspect, tmp_path):
    mock_inspect.return_value = CommandResult(
        stdout='',
        stderr="Error",
        returncode=1,
        timed_out=False,
        error=""
    )
    
    assert run_baseline_smoke_test(tmp_path, tmp_path / ".env", "my-app") is False

"""Tests for Docker audit checks."""

from unittest.mock import patch
from models.command_result import CommandResult
from models.enums import CheckStatus, ClassificationImpact
from modules.host.audit.checks_docker import (
    run_check_docker_cli,
    run_check_docker_compose,
    run_check_docker_conflicts,
    run_check_docker_daemon,
    run_check_docker_runtime,
)


@patch("modules.host.audit.checks_docker.run_command")
def test_check_docker_cli_ok(mock_run):
    """Test docker CLI check when available."""
    mock_run.return_value = CommandResult(stdout="Docker version 24.0", stderr="", returncode=0, timed_out=False, error="")
    result = run_check_docker_cli()
    assert result.status == CheckStatus.OK
    assert result.classification_impact == ClassificationImpact.NONE


@patch("modules.host.audit.checks_docker.run_command")
def test_check_docker_cli_missing(mock_run):
    """Test docker CLI check when missing."""
    mock_run.return_value = CommandResult(stdout="", stderr="command not found", returncode=127, timed_out=False, error="")
    result = run_check_docker_cli()
    assert result.status == CheckStatus.WARN
    assert result.classification_impact == ClassificationImpact.SANEABLE


@patch("modules.host.audit.checks_docker.run_command")
def test_check_docker_daemon_active(mock_run):
    """Test docker daemon check when active."""
    mock_run.return_value = CommandResult(stdout="active\n", stderr="", returncode=0, timed_out=False, error="")
    result = run_check_docker_daemon()
    assert result.status == CheckStatus.OK
    assert result.classification_impact == ClassificationImpact.NONE


@patch("modules.host.audit.checks_docker.run_command")
def test_check_docker_daemon_inactive(mock_run):
    """Test docker daemon check when inactive."""
    mock_run.return_value = CommandResult(stdout="inactive\n", stderr="", returncode=3, timed_out=False, error="")
    result = run_check_docker_daemon()
    assert result.status == CheckStatus.WARN
    assert result.classification_impact == ClassificationImpact.SANEABLE


@patch("modules.host.audit.checks_docker.run_command")
def test_check_docker_compose_ok(mock_run):
    """Test docker compose check when available."""
    mock_run.return_value = CommandResult(stdout="Docker Compose version v2.20", stderr="", returncode=0, timed_out=False, error="")
    result = run_check_docker_compose()
    assert result.status == CheckStatus.OK
    assert result.classification_impact == ClassificationImpact.NONE


@patch("modules.host.audit.checks_docker.run_command")
def test_check_docker_compose_missing(mock_run):
    """Test docker compose check when missing."""
    mock_run.return_value = CommandResult(stdout="", stderr="docker: 'compose' is not a docker command.", returncode=1, timed_out=False, error="")
    result = run_check_docker_compose()
    assert result.status == CheckStatus.WARN
    assert result.classification_impact == ClassificationImpact.SANEABLE


@patch("modules.host.audit.checks_docker.run_command")
def test_check_docker_conflicts_none(mock_run):
    """Test docker conflict check when no conflicting packages."""
    mock_run.return_value = CommandResult(stdout="ii  vim  1.0  Vi IMproved\n", stderr="", returncode=0, timed_out=False, error="")
    result = run_check_docker_conflicts()
    assert result.status == CheckStatus.OK
    assert result.classification_impact == ClassificationImpact.NONE


@patch("modules.host.audit.checks_docker.run_command")
def test_check_docker_conflicts_found(mock_run):
    """Test docker conflict check when conflicting package exists."""
    mock_run.return_value = CommandResult(stdout="ii  docker-compose  1.29  legacy python compose\n", stderr="", returncode=0, timed_out=False, error="")
    result = run_check_docker_conflicts()
    assert result.status == CheckStatus.FAIL
    assert result.classification_impact == ClassificationImpact.BLOCKED

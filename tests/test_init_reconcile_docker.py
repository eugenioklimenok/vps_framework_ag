"""Tests for Docker reconciliation."""

from unittest.mock import patch
from models.command_result import CommandResult
from models.enums import ReconcileAction, CheckStatus, ClassificationImpact
from models.check_result import CheckResult
from modules.host.init.reconcile_docker import (
    reconcile_docker_engine,
    reconcile_docker_compose,
    enable_start_docker,
)


def _mock_result(status: CheckStatus) -> CheckResult:
    return CheckResult(
        check_id="TEST",
        title="Test",
        category="DOCKER",
        description="Test",
        evidence_command="test",
        expected_behavior="test",
        status=status,
        evidence="",
        message="",
        classification_impact=ClassificationImpact.NONE,
    )


@patch("modules.host.init.reconcile_docker.run_command")
@patch("modules.host.init.reconcile_docker.run_check_docker_cli")
def test_reconcile_docker_engine_skip(mock_cli, mock_run):
    """Test engine reconciliation skipped if already installed."""
    mock_cli.return_value = _mock_result(CheckStatus.OK)
    
    assert reconcile_docker_engine() == ReconcileAction.SKIPPED
    mock_run.assert_not_called()


@patch("modules.host.init.reconcile_docker.run_command")
@patch("modules.host.init.reconcile_docker.run_check_docker_cli")
def test_reconcile_docker_engine_install(mock_cli, mock_run):
    """Test engine reconciliation installs if not present."""
    mock_cli.return_value = _mock_result(CheckStatus.WARN)
    mock_run.return_value = CommandResult(stdout="", stderr="", returncode=0, timed_out=False, error="")
    
    assert reconcile_docker_engine() == ReconcileAction.CREATED
    assert mock_run.call_count == 2  # apt-get update, apt-get install


@patch("modules.host.init.reconcile_docker.run_command")
@patch("modules.host.init.reconcile_docker.run_check_docker_compose")
def test_reconcile_docker_compose_skip(mock_compose, mock_run):
    """Test compose reconciliation skipped if already installed."""
    mock_compose.return_value = _mock_result(CheckStatus.OK)
    
    assert reconcile_docker_compose() == ReconcileAction.SKIPPED
    mock_run.assert_not_called()


@patch("modules.host.init.reconcile_docker.run_command")
@patch("modules.host.init.reconcile_docker.run_check_docker_compose")
def test_reconcile_docker_compose_install(mock_compose, mock_run):
    """Test compose reconciliation installs if not present."""
    mock_compose.return_value = _mock_result(CheckStatus.WARN)
    mock_run.return_value = CommandResult(stdout="", stderr="", returncode=0, timed_out=False, error="")
    
    assert reconcile_docker_compose() == ReconcileAction.CREATED
    mock_run.assert_called_once()


@patch("modules.host.init.reconcile_docker.run_command")
@patch("modules.host.init.reconcile_docker.run_check_docker_daemon")
def test_enable_start_docker_skip(mock_daemon, mock_run):
    """Test daemon start skipped if already active."""
    mock_daemon.return_value = _mock_result(CheckStatus.OK)
    
    assert enable_start_docker() == ReconcileAction.SKIPPED
    mock_run.assert_not_called()


@patch("modules.host.init.reconcile_docker.run_command")
@patch("modules.host.init.reconcile_docker.run_check_docker_daemon")
def test_enable_start_docker_repair(mock_daemon, mock_run):
    """Test daemon start runs systemctl if inactive."""
    mock_daemon.return_value = _mock_result(CheckStatus.WARN)
    mock_run.return_value = CommandResult(stdout="", stderr="", returncode=0, timed_out=False, error="")
    
    assert enable_start_docker() == ReconcileAction.REPAIRED
    mock_run.assert_called_once()

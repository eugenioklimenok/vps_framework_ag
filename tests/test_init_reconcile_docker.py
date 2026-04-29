"""Tests for Docker reconciliation."""

from unittest.mock import patch, mock_open
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
@patch("builtins.open", new_callable=mock_open, read_data="ID=ubuntu\nVERSION_CODENAME=jammy")
def test_reconcile_docker_engine_install_official_repo(mock_file, mock_cli, mock_run):
    """Test engine reconciliation installs official packages and sets up repo if not present."""
    mock_cli.return_value = _mock_result(CheckStatus.WARN)
    mock_run.return_value = CommandResult(stdout="amd64\n", stderr="", returncode=0, timed_out=False, error="")
    
    assert reconcile_docker_engine() == ReconcileAction.CREATED
    
    # Verify the commands run in the correct order for the official setup
    calls = mock_run.call_args_list
    assert len(calls) == 8
    assert calls[0][0][0] == ["apt-get", "update"]
    assert calls[1][0][0] == ["apt-get", "install", "-y", "ca-certificates", "curl", "gnupg"]
    assert calls[2][0][0] == ["install", "-m", "0755", "-d", "/etc/apt/keyrings"]
    assert calls[3][0][0] == ["curl", "-fsSL", "https://download.docker.com/linux/ubuntu/gpg", "-o", "/etc/apt/keyrings/docker.asc"]
    assert calls[4][0][0] == ["chmod", "a+r", "/etc/apt/keyrings/docker.asc"]
    assert calls[5][0][0] == ["dpkg", "--print-architecture"]
    assert calls[6][0][0] == ["apt-get", "update"]
    
    expected_packages = [
        "apt-get", "install", "-y",
        "docker-ce", "docker-ce-cli", "containerd.io", 
        "docker-buildx-plugin", "docker-compose-plugin"
    ]
    assert calls[7][0][0] == expected_packages
    
    # Ensure sources.list was written
    mock_file.assert_any_call("/etc/apt/sources.list.d/docker.list", "w")


@patch("modules.host.init.reconcile_docker.run_command")
@patch("modules.host.init.reconcile_docker.run_check_docker_cli")
@patch("builtins.open", new_callable=mock_open, read_data="ID=debian\nVERSION_CODENAME=bookworm")
def test_reconcile_docker_engine_unsupported_os(mock_file, mock_cli, mock_run):
    """Test engine reconciliation fails before system mutation if OS is unsupported."""
    mock_cli.return_value = _mock_result(CheckStatus.WARN)
    
    assert reconcile_docker_engine() == ReconcileAction.FAILED
    mock_run.assert_not_called()
    assert mock_file.call_count == 1
    mock_file.assert_called_once_with("/etc/os-release", "r")


@patch("modules.host.init.reconcile_docker.run_command")
@patch("modules.host.init.reconcile_docker.run_check_docker_cli")
@patch("builtins.open", new_callable=mock_open, read_data="ID=ubuntu")
def test_reconcile_docker_engine_missing_codename(mock_file, mock_cli, mock_run):
    """Test engine reconciliation fails before system mutation if codename is missing."""
    mock_cli.return_value = _mock_result(CheckStatus.WARN)
    
    assert reconcile_docker_engine() == ReconcileAction.FAILED
    mock_run.assert_not_called()
    assert mock_file.call_count == 1
    mock_file.assert_called_once_with("/etc/os-release", "r")


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
    """Test compose reconciliation installs official plugin if not present."""
    mock_compose.return_value = _mock_result(CheckStatus.WARN)
    mock_run.return_value = CommandResult(stdout="", stderr="", returncode=0, timed_out=False, error="")
    
    assert reconcile_docker_compose() == ReconcileAction.CREATED
    mock_run.assert_called_once_with(["apt-get", "install", "-y", "docker-compose-plugin"])


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

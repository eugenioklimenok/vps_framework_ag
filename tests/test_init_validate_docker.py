"""Tests for Docker runtime validation."""

from unittest.mock import patch
from models.check_result import CheckResult
from models.enums import CheckStatus, ClassificationImpact
from models.command_result import CommandResult
from modules.host.audit.checks_docker import run_check_docker_operator_access
from modules.host.init.validate_docker import validate_docker_slice


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


@patch("modules.host.init.validate_docker.run_check_docker_compose")
@patch("modules.host.init.validate_docker.run_check_docker_runtime")
@patch("modules.host.init.validate_docker.run_check_docker_daemon")
@patch("modules.host.init.validate_docker.run_check_docker_cli")
def test_validate_docker_slice_ok(mock_cli, mock_daemon, mock_runtime, mock_compose):
    """Test validation passes when all checks are OK."""
    mock_cli.return_value = _mock_result(CheckStatus.OK)
    mock_daemon.return_value = _mock_result(CheckStatus.OK)
    mock_runtime.return_value = _mock_result(CheckStatus.OK)
    mock_compose.return_value = _mock_result(CheckStatus.OK)

    assert validate_docker_slice() is True


@patch("modules.host.init.validate_docker.run_check_docker_compose")
@patch("modules.host.init.validate_docker.run_check_docker_runtime")
@patch("modules.host.init.validate_docker.run_check_docker_daemon")
@patch("modules.host.init.validate_docker.run_check_docker_cli")
def test_validate_docker_slice_fail(mock_cli, mock_daemon, mock_runtime, mock_compose):
    """Test validation fails when any check is not OK."""
    mock_cli.return_value = _mock_result(CheckStatus.OK)
    mock_daemon.return_value = _mock_result(CheckStatus.OK)
    mock_runtime.return_value = _mock_result(CheckStatus.WARN)
    mock_compose.return_value = _mock_result(CheckStatus.OK)

    assert validate_docker_slice() is False


@patch("modules.host.init.validate_docker.run_check_docker_operator_access")
@patch("modules.host.init.validate_docker.run_check_docker_compose")
@patch("modules.host.init.validate_docker.run_check_docker_runtime")
@patch("modules.host.init.validate_docker.run_check_docker_daemon")
@patch("modules.host.init.validate_docker.run_check_docker_cli")
def test_validate_docker_slice_fails_closed_when_operator_access_fails(
    mock_cli, mock_daemon, mock_runtime, mock_compose, mock_operator_access
):
    """Operator validation is required when an operator user is provided."""
    mock_cli.return_value = _mock_result(CheckStatus.OK)
    mock_daemon.return_value = _mock_result(CheckStatus.OK)
    mock_runtime.return_value = _mock_result(CheckStatus.OK)
    mock_compose.return_value = _mock_result(CheckStatus.OK)
    mock_operator_access.return_value = _mock_result(CheckStatus.WARN)

    assert validate_docker_slice("devops") is False
    mock_operator_access.assert_called_once_with("devops")


@patch("modules.host.audit.checks_docker.run_command")
def test_run_check_docker_operator_access_uses_fresh_operator_context(mock_run):
    """Operator Docker access check validates group state and docker ps as the operator."""
    mock_run.side_effect = [
        CommandResult(stdout="uid=1001(devops) gid=1001(devops) groups=1001(devops),988(docker)\n", stderr="", returncode=0, timed_out=False, error=""),
        CommandResult(stdout="docker:x:988:devops\n", stderr="", returncode=0, timed_out=False, error=""),
        CommandResult(stdout="CONTAINER ID   IMAGE\n", stderr="", returncode=0, timed_out=False, error=""),
    ]

    result = run_check_docker_operator_access("devops")

    assert result.status == CheckStatus.OK
    assert mock_run.call_args_list[0][0][0] == ["id", "devops"]
    assert mock_run.call_args_list[1][0][0] == ["getent", "group", "docker"]
    assert mock_run.call_args_list[2][0][0] == ["runuser", "-l", "devops", "-c", "docker ps"]


@patch("modules.host.audit.checks_docker.run_command")
def test_run_check_docker_operator_access_fails_when_operator_cannot_use_docker(mock_run):
    """Permission denied from docker ps keeps the validation closed."""
    mock_run.side_effect = [
        CommandResult(stdout="uid=1001(devops) gid=1001(devops) groups=1001(devops),988(docker)\n", stderr="", returncode=0, timed_out=False, error=""),
        CommandResult(stdout="docker:x:988:devops\n", stderr="", returncode=0, timed_out=False, error=""),
        CommandResult(stdout="", stderr="permission denied while trying to connect to the Docker API\n", returncode=1, timed_out=False, error=""),
    ]

    result = run_check_docker_operator_access("devops")

    assert result.status == CheckStatus.WARN
    assert "permission denied" in result.evidence

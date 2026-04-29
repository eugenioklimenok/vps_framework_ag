"""Tests for Docker runtime validation."""

from unittest.mock import patch
from models.check_result import CheckResult
from models.enums import CheckStatus, ClassificationImpact
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

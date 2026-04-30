"""Tests for init-vps Docker operator access gating."""

from unittest.mock import patch

from models.enums import HostClassification, ReconcileAction
from models.reconcile_result import ReconcileResult
from modules.host.audit.runner import AuditReport
from modules.host.init.runner import run_init
from modules.host.init.validate import ValidationReport


def _ok_reconcile(step_id: str) -> ReconcileResult:
    return ReconcileResult(
        step_id=step_id,
        action=ReconcileAction.REUSED,
        message=f"{step_id} ok",
        evidence="test",
        success=True,
    )


@patch("modules.host.init.runner.validate_docker_slice")
@patch("modules.host.init.runner.reconcile_docker_operator_access")
@patch("modules.host.init.runner.enable_start_docker")
@patch("modules.host.init.runner.reconcile_docker_compose")
@patch("modules.host.init.runner.reconcile_docker_engine")
@patch("modules.host.init.runner.validate_init_slice")
@patch("modules.host.init.runner.reconcile_authorized_keys")
@patch("modules.host.init.runner.reconcile_ssh_directory")
@patch("modules.host.init.runner.reconcile_operator_home")
@patch("modules.host.init.runner.reconcile_operator_user")
@patch("modules.host.init.runner.run_audit")
def test_run_init_does_not_report_success_when_operator_docker_validation_fails(
    mock_audit,
    mock_user,
    mock_home,
    mock_ssh,
    mock_authorized_keys,
    mock_validate_init,
    mock_docker_engine,
    mock_docker_compose,
    mock_docker_service,
    mock_operator_access,
    mock_validate_docker,
):
    """init-vps fails closed after reconciliation if operator Docker access is not validated."""
    mock_audit.return_value = AuditReport(classification=HostClassification.SANEABLE)
    mock_user.return_value = _ok_reconcile("RECONCILE_USER")
    mock_home.return_value = _ok_reconcile("RECONCILE_HOME")
    mock_ssh.return_value = _ok_reconcile("RECONCILE_SSH_DIR")
    mock_authorized_keys.return_value = _ok_reconcile("RECONCILE_AUTHORIZED_KEYS")
    mock_validate_init.return_value = ValidationReport(results=[], all_passed=True)
    mock_docker_engine.return_value = _ok_reconcile("RECONCILE_DOCKER_ENGINE")
    mock_docker_compose.return_value = _ok_reconcile("RECONCILE_DOCKER_COMPOSE")
    mock_docker_service.return_value = _ok_reconcile("RECONCILE_DOCKER_SERVICE")
    mock_operator_access.return_value = _ok_reconcile("RECONCILE_DOCKER_OPERATOR_ACCESS")
    mock_validate_docker.return_value = False

    result = run_init("devops", "ssh-ed25519 AAAATEST")

    assert result.success is False
    assert result.aborted is True
    assert result.abort_reason == "Post-action Docker runtime validation failed."
    mock_validate_docker.assert_called_once_with("devops")

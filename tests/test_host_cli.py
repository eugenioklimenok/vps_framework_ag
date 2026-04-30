"""
Tests for HOST CLI commands output formatting.
"""

import logging
from typer.testing import CliRunner
from main import app
from unittest.mock import patch
from modules.host.init.runner import InitResult
from modules.host.audit.runner import AuditReport
from modules.host.init.validate import ValidationReport
from models.command_result import CommandResult
from models.enums import HostClassification
from models.reconcile_result import ValidationResult

runner = CliRunner()


@patch("cli.host_commands.run_init")
def test_cli_init_vps_no_raw_logs(mock_run, caplog):
    """Ensure normal successful output does not contain raw command-not-found diagnostics."""
    mock_run.return_value = InitResult(
        success=True,
        aborted=False,
        abort_reason="",
        audit_report=AuditReport(
            results=[],
            classification=HostClassification.SANEABLE,
            total=0,
            ok_count=0,
            warn_count=0,
            fail_count=0,
        ),
        reconcile_results=[],
        validation_report=ValidationReport(results=[], all_passed=True),
    )
    
    # Simulate the raw internal log being emitted as debug, which should NOT appear in CLI output
    with caplog.at_level(logging.INFO):
        # We also need to test actual subprocess wrapper behavior if possible,
        # but since we're testing the CLI, we can just invoke it.
        # To truly test that subprocess wrapper doesn't emit it at error level,
        # we can call the wrapper directly.
        from utils.subprocess_wrapper import run_command
        run_command(["nonexistent_binary_docker_test"])

        result = runner.invoke(app, ["host", "init-vps", "--operator-user", "devops", "--public-key", "dummy-key"])
        
        assert result.exit_code == 0
        assert "SUCCESS: Host baseline initialized and validated." in result.stdout
        assert "Command binary not found: docker" not in result.stdout
        assert "Command binary not found: nonexistent_binary_docker_test" not in caplog.text

def test_subprocess_wrapper_demotes_missing_binary(caplog):
    """Ensure subprocess wrapper logs missing binaries at DEBUG level, not ERROR."""
    from utils.subprocess_wrapper import run_command
    
    with caplog.at_level(logging.DEBUG):
        result = run_command(["nonexistent_binary_docker_test_xyz"])
        
    assert result.returncode == -1
    
    # Check that it IS in debug logs
    debug_logs = [r for r in caplog.records if r.levelno == logging.DEBUG]
    error_logs = [r for r in caplog.records if r.levelno >= logging.ERROR]
    
    assert any("Command binary not found: nonexistent_binary_docker_test_xyz" in r.message for r in debug_logs)
    assert not any("Command binary not found" in r.message for r in error_logs)


@patch("cli.host_commands.run_init")
def test_cli_init_vps_success_prints_docker_validation_rows(mock_run):
    """Successful init-vps output shows Docker Slice 02 validation evidence."""
    mock_run.return_value = InitResult(
        success=True,
        aborted=False,
        abort_reason="",
        audit_report=AuditReport(
            results=[],
            classification=HostClassification.SANEABLE,
            total=0,
            ok_count=0,
            warn_count=0,
            fail_count=0,
        ),
        reconcile_results=[],
        validation_report=ValidationReport(
            results=[
                ValidationResult(
                    check_id="VALIDATE_USER_EXISTS",
                    passed=True,
                    message="User 'devops' exists",
                    evidence="uid=1001(devops)",
                ),
                ValidationResult(
                    check_id="VALIDATE_DOCKER_ENGINE",
                    passed=True,
                    message="Docker Engine is installed and usable",
                    evidence="docker --version; docker info",
                ),
                ValidationResult(
                    check_id="VALIDATE_DOCKER_COMPOSE",
                    passed=True,
                    message="Docker Compose plugin is installed and usable",
                    evidence="docker compose version",
                ),
                ValidationResult(
                    check_id="VALIDATE_DOCKER_SERVICE",
                    passed=True,
                    message="Docker service is active",
                    evidence="systemctl is-active docker",
                ),
                ValidationResult(
                    check_id="VALIDATE_DOCKER_OPERATOR_ACCESS",
                    passed=True,
                    message="Operator user 'devops' can run Docker without sudo",
                    evidence="runuser -l devops -c docker ps",
                ),
            ],
            all_passed=True,
        ),
    )

    result = runner.invoke(
        app,
        ["host", "init-vps", "--operator-user", "devops", "--public-key", "dummy-key"],
    )

    assert result.exit_code == 0
    assert "[OK] VALIDATE_USER_EXISTS" in result.stdout
    assert "[OK] VALIDATE_DOCKER_ENGINE" in result.stdout
    assert "[OK] VALIDATE_DOCKER_COMPOSE" in result.stdout
    assert "[OK] VALIDATE_DOCKER_SERVICE" in result.stdout
    assert "[OK] VALIDATE_DOCKER_OPERATOR_ACCESS" in result.stdout
    assert "SUCCESS: Host baseline initialized and validated." in result.stdout


@patch("cli.host_commands.run_init")
def test_cli_init_vps_docker_validation_failure_is_visible_without_success(mock_run):
    """Docker validation failure output shows the failed row and does not print SUCCESS."""
    mock_run.return_value = InitResult(
        success=False,
        aborted=True,
        abort_reason="Post-action Docker runtime validation failed.",
        audit_report=AuditReport(
            results=[],
            classification=HostClassification.SANEABLE,
            total=0,
            ok_count=0,
            warn_count=0,
            fail_count=0,
        ),
        reconcile_results=[],
        validation_report=ValidationReport(
            results=[
                ValidationResult(
                    check_id="VALIDATE_USER_EXISTS",
                    passed=True,
                    message="User 'devops' exists",
                    evidence="uid=1001(devops)",
                ),
                ValidationResult(
                    check_id="VALIDATE_DOCKER_COMPOSE",
                    passed=False,
                    message="Docker Compose plugin is not installed and usable",
                    evidence="docker compose version failed",
                ),
            ],
            all_passed=False,
        ),
    )

    result = runner.invoke(
        app,
        ["host", "init-vps", "--operator-user", "devops", "--public-key", "dummy-key"],
    )

    assert result.exit_code == 2
    assert "[OK] VALIDATE_USER_EXISTS" in result.stdout
    assert "[X] VALIDATE_DOCKER_COMPOSE" in result.stdout
    assert "ABORTED: Post-action Docker runtime validation failed." in result.stdout
    assert "SUCCESS: Host baseline initialized and validated." not in result.stdout

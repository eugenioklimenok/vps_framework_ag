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

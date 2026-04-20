"""
Tests for OPERATE CLI.
"""

from typer.testing import CliRunner
from main import app
from unittest.mock import patch

runner = CliRunner()


@patch("cli.operate_commands.run_audit_project")
def test_cli_audit_project_success(mock_run, tmp_path):
    from models.operate_result import ProjectAuditResult
    from models.enums import AuditClassification
    
    mock_run.return_value = ProjectAuditResult(
        classification=AuditClassification.HEALTHY,
        project_slug="test-app",
        validation_passed=True,
    )
    
    target = tmp_path / "app"
    env_file = tmp_path / ".env"
    
    result = runner.invoke(app, ["operate", "audit-project", "--path", str(target), "--env-file", str(env_file)])
    
    assert result.exit_code == 0
    assert "PROJECT AUDIT REPORT" in result.stdout
    assert "HEALTHY" in result.stdout


@patch("cli.operate_commands.run_backup_project")
def test_cli_backup_project_success(mock_run, tmp_path):
    from models.operate_result import BackupResult
    from models.enums import BackupResultState
    
    mock_run.return_value = BackupResult(
        result_state=BackupResultState.CREATED,
        project_slug="test-app",
        artifact_path=tmp_path / "b.tar.gz",
        checksum_path=tmp_path / "b.tar.gz.sha256",
        artifact_validated=True,
    )
    
    target = tmp_path / "app"
    
    result = runner.invoke(app, ["operate", "backup-project", "--path", str(target)])
    
    assert result.exit_code == 0
    assert "PROJECT BACKUP REPORT" in result.stdout
    assert "CREATED" in result.stdout

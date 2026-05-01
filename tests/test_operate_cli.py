"""
Tests for OPERATE CLI.
"""

from pathlib import Path
import shutil
from typer.testing import CliRunner
from main import app
import uuid
from unittest.mock import patch

import pytest

runner = CliRunner()


@pytest.fixture
def local_tmp_path() -> Path:
    root = Path(".test-work-operate") / f"cli-{uuid.uuid4().hex}"
    root.mkdir(parents=True)
    try:
        yield root.resolve()
    finally:
        shutil.rmtree(root, ignore_errors=True)


@patch("cli.operate_commands.run_audit_project")
def test_cli_audit_project_success(mock_run, local_tmp_path):
    from models.operate_result import ProjectAuditResult
    from models.enums import AuditClassification
    
    mock_run.return_value = ProjectAuditResult(
        classification=AuditClassification.HEALTHY,
        project_slug="test-app",
        validation_passed=True,
    )
    
    target = local_tmp_path / "app"
    env_file = local_tmp_path / ".env"
    
    result = runner.invoke(app, ["operate", "audit-project", "--path", str(target), "--env-file", str(env_file)])
    
    assert result.exit_code == 0
    assert "PROJECT AUDIT REPORT" in result.stdout
    assert "HEALTHY" in result.stdout


@patch("cli.operate_commands.run_backup_project")
def test_cli_backup_project_success(mock_run, local_tmp_path):
    from models.operate_result import BackupResult
    from models.enums import BackupResultState
    
    mock_run.return_value = BackupResult(
        result_state=BackupResultState.CREATED,
        project_slug="test-app",
        artifact_path=local_tmp_path / "b.tar.gz",
        checksum_path=local_tmp_path / "b.tar.gz.sha256",
        artifact_validated=True,
    )
    
    target = local_tmp_path / "app"
    output_dir = local_tmp_path / "backups"
    
    result = runner.invoke(
        app,
        ["operate", "backup-project", "--path", str(target), "--output-dir", str(output_dir)],
    )
    
    assert result.exit_code == 0
    assert "PROJECT BACKUP REPORT" in result.stdout
    assert "CREATED" in result.stdout


def test_cli_backup_project_blocks_missing_path(local_tmp_path):
    result = runner.invoke(
        app,
        ["operate", "backup-project", "--output-dir", str(local_tmp_path / "backups")],
    )

    assert result.exit_code != 0
    assert "Missing option" in result.stdout or "Missing option" in result.stderr


def test_cli_backup_project_blocks_missing_output_dir(local_tmp_path):
    target = local_tmp_path / "app"

    result = runner.invoke(app, ["operate", "backup-project", "--path", str(target)])

    assert result.exit_code != 0
    assert "Missing option" in result.stdout or "Missing option" in result.stderr

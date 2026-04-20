"""
Tests for OPERATE backup engine.
"""

from pathlib import Path
import tarfile

from models.enums import BackupResultState
from modules.operate.backup.runner import run_backup_project


def test_run_backup_success(tmp_path: Path):
    target = tmp_path / "app"
    target.mkdir()
    (target / "project.yaml").write_text("project_slug: test-app\n")
    (target / "source.txt").write_text("hello")
    
    # We should exclude .env by default
    (target / ".env").write_text("SECRET=1")
    
    result = run_backup_project(str(target), include_env=False)
    
    assert result.result_state == BackupResultState.CREATED
    assert result.project_slug == "test-app"
    assert result.artifact_path.exists()
    assert result.checksum_path.exists()
    assert result.artifact_validated is True
    
    # Verify the tar contents
    with tarfile.open(result.artifact_path, "r:gz") as tar:
        names = tar.getnames()
        assert "./project.yaml" in names
        assert "./source.txt" in names
        assert "./.env" not in names


def test_run_backup_blocked_invalid_project(tmp_path: Path):
    target = tmp_path / "app"
    target.mkdir()
    
    result = run_backup_project(str(target))
    
    assert result.result_state == BackupResultState.BLOCKED
    assert "Missing authoritative project.yaml" in result.blocked_reason

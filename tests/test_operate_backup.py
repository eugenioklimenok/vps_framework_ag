"""
Tests for OPERATE backup engine.
"""

from pathlib import Path
import os
import shutil
import tarfile
import uuid

import pytest

from models.enums import BackupResultState
from modules.operate.backup.runner import run_backup_project


@pytest.fixture
def local_tmp_path() -> Path:
    root = Path(".test-work-operate") / f"backup-{uuid.uuid4().hex}"
    root.mkdir(parents=True)
    try:
        yield root.resolve()
    finally:
        shutil.rmtree(root, ignore_errors=True)


def make_project(root: Path) -> Path:
    target = root / "app"
    target.mkdir()
    (target / "project.yaml").write_text("project_slug: test-app\n")
    (target / "source.txt").write_text("hello")
    (target / ".env").write_text("SECRET=1")
    return target


def test_run_backup_success_existing_writable_output_dir(local_tmp_path: Path):
    target = make_project(local_tmp_path)
    output_dir = local_tmp_path / "backups"
    output_dir.mkdir()

    result = run_backup_project(str(target), output_dir=str(output_dir), include_env=False)

    assert result.result_state == BackupResultState.CREATED
    assert result.project_slug == "test-app"
    assert result.artifact_path.exists()
    assert result.artifact_path.parent == output_dir.resolve()
    assert result.checksum_path.exists()
    assert result.artifact_validated is True

    with tarfile.open(result.artifact_path, "r:gz") as tar:
        names = tar.getnames()
        assert "./project.yaml" in names
        assert "./source.txt" in names
        assert "./.env" not in names


def test_run_backup_creates_safe_missing_output_dir_and_revalidates(local_tmp_path: Path):
    target = make_project(local_tmp_path)
    output_dir = local_tmp_path / "created-backups"

    result = run_backup_project(str(target), output_dir=str(output_dir))

    assert result.result_state == BackupResultState.CREATED
    assert output_dir.is_dir()
    assert result.artifact_path.parent == output_dir.resolve()


def test_run_backup_blocked_missing_project_yaml(local_tmp_path: Path):
    target = local_tmp_path / "app"
    target.mkdir()

    result = run_backup_project(str(target), output_dir=str(local_tmp_path / "backups"))

    assert result.result_state == BackupResultState.BLOCKED
    assert "Missing authoritative project.yaml" in result.blocked_reason


def test_run_backup_blocks_output_dir_equal_to_project_root(local_tmp_path: Path):
    target = make_project(local_tmp_path)

    result = run_backup_project(str(target), output_dir=str(target))

    assert result.result_state == BackupResultState.BLOCKED
    assert "inside project root" in result.blocked_reason


def test_run_backup_blocks_output_dir_inside_project_root(local_tmp_path: Path):
    target = make_project(local_tmp_path)

    result = run_backup_project(str(target), output_dir=str(target / "backups"))

    assert result.result_state == BackupResultState.BLOCKED
    assert "inside project root" in result.blocked_reason


def test_run_backup_blocks_symlinked_output_dir_resolving_inside_project_root(local_tmp_path: Path):
    target = make_project(local_tmp_path)
    inside_output = target / "actual-backups"
    inside_output.mkdir()
    outside_link = local_tmp_path / "outside-link"
    try:
        os.symlink(inside_output, outside_link, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("Directory symlinks are unavailable in this environment")

    result = run_backup_project(str(target), output_dir=str(outside_link))

    assert result.result_state == BackupResultState.BLOCKED
    assert "inside project root" in result.blocked_reason


def test_run_backup_blocks_output_path_existing_as_file(local_tmp_path: Path):
    target = make_project(local_tmp_path)
    output_path = local_tmp_path / "backup-file"
    output_path.write_text("not a directory")

    result = run_backup_project(str(target), output_dir=str(output_path))

    assert result.result_state == BackupResultState.BLOCKED
    assert "not a directory" in result.blocked_reason


def test_run_backup_validates_artifact_before_created(local_tmp_path: Path, monkeypatch):
    target = make_project(local_tmp_path)
    output_dir = local_tmp_path / "backups"

    def fake_create(plan):
        return True, plan.artifact_path, plan.checksum_path, ""

    monkeypatch.setattr("modules.operate.backup.runner.create_backup_archive", fake_create)

    result = run_backup_project(str(target), output_dir=str(output_dir))

    assert result.result_state == BackupResultState.FAILED
    assert result.artifact_validated is False
    assert "does not exist" in result.blocked_reason


def test_run_backup_rejects_empty_artifact(local_tmp_path: Path, monkeypatch):
    target = make_project(local_tmp_path)
    output_dir = local_tmp_path / "backups"

    def fake_create(plan):
        plan.output_dir.mkdir(parents=True, exist_ok=True)
        plan.artifact_path.write_bytes(b"")
        plan.checksum_path.write_text("fake")
        return True, plan.artifact_path, plan.checksum_path, ""

    monkeypatch.setattr("modules.operate.backup.runner.create_backup_archive", fake_create)

    result = run_backup_project(str(target), output_dir=str(output_dir))

    assert result.result_state == BackupResultState.FAILED
    assert "empty" in result.blocked_reason


def test_run_backup_rejects_unreadable_archive(local_tmp_path: Path, monkeypatch):
    target = make_project(local_tmp_path)
    output_dir = local_tmp_path / "backups"

    def fake_create(plan):
        plan.output_dir.mkdir(parents=True, exist_ok=True)
        plan.artifact_path.write_text("not an archive")
        plan.checksum_path.write_text("fake")
        return True, plan.artifact_path, plan.checksum_path, ""

    monkeypatch.setattr("modules.operate.backup.runner.create_backup_archive", fake_create)

    result = run_backup_project(str(target), output_dir=str(output_dir))

    assert result.result_state == BackupResultState.FAILED
    assert "readable" in result.blocked_reason


def test_run_backup_archive_contains_expected_planned_content(local_tmp_path: Path):
    target = make_project(local_tmp_path)
    output_dir = local_tmp_path / "backups"

    result = run_backup_project(str(target), output_dir=str(output_dir))

    assert result.result_state == BackupResultState.CREATED
    with tarfile.open(result.artifact_path, "r:gz") as tar:
        names = set(tar.getnames())
    assert "./project.yaml" in names
    assert "./source.txt" in names


def test_run_backup_archive_excludes_output_dir_and_generated_files(local_tmp_path: Path):
    target = make_project(local_tmp_path)
    output_dir = local_tmp_path / "backups"

    result = run_backup_project(str(target), output_dir=str(output_dir))

    assert result.result_state == BackupResultState.CREATED
    with tarfile.open(result.artifact_path, "r:gz") as tar:
        names = set(tar.getnames())

    assert not any(str(output_dir.name) in name for name in names)
    assert result.artifact_path.name not in names
    assert result.checksum_path.name not in names


def test_run_backup_does_not_mutate_source_project_files(local_tmp_path: Path):
    target = make_project(local_tmp_path)
    before = {
        path.relative_to(target): path.read_bytes()
        for path in target.rglob("*")
        if path.is_file()
    }

    result = run_backup_project(str(target), output_dir=str(local_tmp_path / "backups"))

    after = {
        path.relative_to(target): path.read_bytes()
        for path in target.rglob("*")
        if path.is_file()
    }
    assert result.result_state == BackupResultState.CREATED
    assert after == before

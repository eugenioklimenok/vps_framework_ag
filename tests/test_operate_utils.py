"""
Tests for OPERATE shared utilities.
"""

from pathlib import Path

from modules.operate.utils import validate_project_identity, extract_project_slug


def test_extract_project_slug_success(tmp_path: Path):
    yaml_file = tmp_path / "project.yaml"
    yaml_file.write_text("project_slug: valid-slug\n")
    assert extract_project_slug(yaml_file) == "valid-slug"


def test_extract_project_slug_missing(tmp_path: Path):
    assert extract_project_slug(tmp_path / "missing.yaml") is None


def test_validate_project_identity_success(tmp_path: Path):
    target = tmp_path / "app"
    target.mkdir()
    (target / "project.yaml").write_text("project_slug: test-app\n")
    
    is_valid, slug, reason = validate_project_identity(target)
    assert is_valid is True
    assert slug == "test-app"
    assert reason == ""


def test_validate_project_identity_blocked(tmp_path: Path):
    target = tmp_path / "app"
    target.mkdir()
    
    is_valid, slug, reason = validate_project_identity(target)
    assert is_valid is False
    assert slug == ""
    assert "Missing authoritative project.yaml" in reason

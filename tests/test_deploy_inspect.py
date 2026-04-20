"""
Tests for DEPLOY project inspection.
"""

from pathlib import Path

from models.enums import DeploymentClassification
from modules.deploy.project.inspect_project import inspect_project_for_deployment


def test_inspect_missing_project(tmp_path: Path):
    target = tmp_path / "missing"
    classification, slug, msg = inspect_project_for_deployment(target)
    assert classification == DeploymentClassification.BLOCKED
    assert "not exist" in msg


def test_inspect_missing_yaml(tmp_path: Path):
    target = tmp_path / "app"
    target.mkdir()
    (target / "compose.yaml").write_text("...")
    
    classification, slug, msg = inspect_project_for_deployment(target)
    assert classification == DeploymentClassification.BLOCKED
    assert "Missing authoritative project.yaml" in msg


def test_inspect_missing_compose(tmp_path: Path):
    target = tmp_path / "app"
    target.mkdir()
    (target / "project.yaml").write_text("project_slug: my-app")
    
    classification, slug, msg = inspect_project_for_deployment(target)
    assert classification == DeploymentClassification.BLOCKED
    assert "Missing baseline compose.yaml" in msg


def test_inspect_valid_project(tmp_path: Path):
    target = tmp_path / "app"
    target.mkdir()
    (target / "project.yaml").write_text("project_slug: valid-app\n")
    (target / "compose.yaml").write_text("services:")
    
    classification, slug, msg = inspect_project_for_deployment(target)
    assert classification == DeploymentClassification.READY
    assert slug == "valid-app"
    assert msg == ""

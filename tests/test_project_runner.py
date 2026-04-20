"""
Tests for PROJECT runner and orchestrator.
"""

import pytest
from pathlib import Path
from models.enums import TargetClassification, ScaffoldAction
from modules.project.runner import run_new_project


def test_run_new_project_invalid_slug(tmp_path: Path):
    result = run_new_project("Invalid Slug!", str(tmp_path))
    assert result.classification == TargetClassification.BLOCKED
    assert ScaffoldAction.BLOCK in result.actions_taken
    assert "Invalid slug" in result.blocked_reason


def test_run_new_project_clean_target(tmp_path: Path):
    target = tmp_path / "my-project"
    result = run_new_project("my-project", str(target))
    
    assert result.classification == TargetClassification.CLEAN
    assert ScaffoldAction.CREATE in result.actions_taken
    assert result.validation_passed is True
    
    # Check that required files and dirs are created
    assert (target / "project.yaml").exists()
    assert (target / "compose.yaml").exists()
    assert (target / "app").is_dir()
    assert (target / "tests").is_dir()


def test_run_new_project_compatible_target(tmp_path: Path):
    # Pre-create a compatible state
    target = tmp_path / "my-project"
    target.mkdir()
    (target / "project.yaml").write_text("project_slug: my-project")
    (target / "compose.yaml").write_text("services:")
    
    result = run_new_project("my-project", str(target))
    
    assert result.classification == TargetClassification.COMPATIBLE
    assert ScaffoldAction.REUSE in result.actions_taken
    assert result.validation_passed is True
    assert target in result.reused_paths
    assert (target / "project.yaml") in result.reused_paths


def test_run_new_project_blocked_target(tmp_path: Path):
    # Create an incompatible state
    target = tmp_path / "my-project"
    target.mkdir()
    (target / "random.txt").write_text("data")
    
    result = run_new_project("my-project", str(target))
    
    assert result.classification == TargetClassification.BLOCKED
    assert ScaffoldAction.BLOCK in result.actions_taken

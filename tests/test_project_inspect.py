"""
Tests for PROJECT target inspection logic.
"""

import pytest
from pathlib import Path
from models.enums import TargetClassification
from modules.project.inspect_target import classify_target


def test_classify_clean_not_exists(tmp_path: Path):
    target = tmp_path / "new_dir"
    assert classify_target(target) == TargetClassification.CLEAN


def test_classify_clean_empty_dir(tmp_path: Path):
    assert classify_target(tmp_path) == TargetClassification.CLEAN


def test_classify_blocked_not_a_dir(tmp_path: Path):
    target = tmp_path / "file.txt"
    target.write_text("hello")
    assert classify_target(target) == TargetClassification.BLOCKED


def test_classify_saneable_allowed_files(tmp_path: Path):
    (tmp_path / ".git").mkdir()
    (tmp_path / "README.md").write_text("test")
    assert classify_target(tmp_path) == TargetClassification.SANEABLE


def test_classify_blocked_unallowed_files(tmp_path: Path):
    (tmp_path / "random_file.txt").write_text("test")
    assert classify_target(tmp_path) == TargetClassification.BLOCKED


def test_classify_compatible_framework_project(tmp_path: Path):
    (tmp_path / "project.yaml").write_text("test")
    (tmp_path / "compose.yaml").write_text("test")
    assert classify_target(tmp_path) == TargetClassification.COMPATIBLE


def test_classify_blocked_partial_framework(tmp_path: Path):
    (tmp_path / "project.yaml").write_text("test")
    # missing compose.yaml
    assert classify_target(tmp_path) == TargetClassification.BLOCKED

"""
Tests for PROJECT CLI commands.
"""

from typer.testing import CliRunner
from main import app
import pytest

runner = CliRunner()


def test_cli_new_project_success(tmp_path):
    target = tmp_path / "test-proj"
    result = runner.invoke(app, ["project", "new-project", "--name", "test-proj", "--path", str(target)])
    
    assert result.exit_code == 0
    assert "PROJECT SCAFFOLD REPORT" in result.stdout
    assert "test-proj" in result.stdout
    assert "CLEAN" in result.stdout
    assert "PASS" in result.stdout
    
    # Verify it actually created it
    assert target.exists()


def test_cli_new_project_invalid_slug(tmp_path):
    target = tmp_path / "test-proj"
    result = runner.invoke(app, ["project", "new-project", "--name", "Invalid Slug", "--path", str(target)])
    
    # Expect failure code
    assert result.exit_code == 2
    assert "BLOCKED" in result.stdout


def test_cli_new_project_blocked_target(tmp_path):
    target = tmp_path / "test-proj"
    target.mkdir()
    (target / "random.txt").write_text("hi")
    
    result = runner.invoke(app, ["project", "new-project", "--name", "test-proj", "--path", str(target)])
    
    assert result.exit_code == 2
    assert "BLOCKED" in result.stdout

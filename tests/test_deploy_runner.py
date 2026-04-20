"""
Tests for DEPLOY runner orchestration.
"""

from pathlib import Path
from unittest.mock import patch

from models.enums import DeploymentClassification, DeployAction
from modules.deploy.project.runner import run_deploy_project


@patch("modules.deploy.project.runner.compose_wrapper")
@patch("modules.deploy.project.runner.run_baseline_smoke_test")
def test_run_deploy_missing_env(mock_smoke, mock_compose, tmp_path):
    result = run_deploy_project(str(tmp_path), str(tmp_path / "missing.env"))
    assert result.classification == DeploymentClassification.BLOCKED
    assert DeployAction.BLOCK in result.actions_taken
    assert "missing or invalid" in result.blocked_reason


@patch("modules.deploy.project.runner.compose_wrapper")
@patch("modules.deploy.project.runner.run_baseline_smoke_test")
def test_run_deploy_success(mock_smoke, mock_compose, tmp_path):
    # Setup valid project
    target = tmp_path / "app"
    target.mkdir()
    (target / "project.yaml").write_text("project_slug: valid-app\n")
    (target / "compose.yaml").write_text("services:")
    
    env_file = tmp_path / ".env"
    env_file.write_text("ENV=1")
    
    # Mock compose success
    mock_compose.check_compose_availability.return_value = True
    
    class MockResult:
        returncode = 0
        stdout = ""
        stderr = ""
        
    mock_compose.validate_compose_config.return_value = MockResult()
    mock_compose.build_compose_stack.return_value = MockResult()
    mock_compose.start_compose_stack.return_value = MockResult()
    # Mock ps returning empty string (so it stays READY, not REDEPLOYABLE)
    class EmptyResult:
        returncode = 0
        stdout = ""
    mock_compose.inspect_compose_status.return_value = EmptyResult()
    
    mock_smoke.return_value = True
    
    result = run_deploy_project(str(target), str(env_file))
    
    assert result.classification == DeploymentClassification.READY
    assert result.project_slug == "valid-app"
    assert result.config_validated is True
    assert result.build_succeeded is True
    assert result.startup_succeeded is True
    assert result.smoke_passed is True
    assert result.validation_passed is True
    assert result.blocked_reason == ""
    
    assert DeployAction.VALIDATE in result.actions_taken
    assert DeployAction.BUILD in result.actions_taken
    assert DeployAction.START in result.actions_taken
    assert DeployAction.SMOKE in result.actions_taken

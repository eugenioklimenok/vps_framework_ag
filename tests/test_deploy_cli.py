"""
Tests for DEPLOY CLI.
"""

from typer.testing import CliRunner
from main import app
from unittest.mock import patch

runner = CliRunner()


@patch("cli.deploy_commands.run_deploy_project")
def test_cli_deploy_project_success(mock_run, tmp_path):
    from models.deploy_result import DeployResult
    from models.enums import DeploymentClassification
    
    mock_run.return_value = DeployResult(
        classification=DeploymentClassification.READY,
        project_slug="test-app",
        config_validated=True,
        build_succeeded=True,
        startup_succeeded=True,
        smoke_passed=True,
        validation_passed=True,
    )
    
    target = tmp_path / "app"
    env_file = tmp_path / ".env"
    
    result = runner.invoke(app, ["deploy", "deploy-project", "--path", str(target), "--env-file", str(env_file)])
    
    assert result.exit_code == 0
    assert "PROJECT DEPLOY REPORT" in result.stdout
    assert "test-app" in result.stdout
    assert "READY" in result.stdout


@patch("cli.deploy_commands.run_deploy_project")
def test_cli_deploy_project_blocked(mock_run, tmp_path):
    from models.deploy_result import DeployResult
    from models.enums import DeploymentClassification
    
    mock_run.return_value = DeployResult(
        classification=DeploymentClassification.BLOCKED,
        blocked_reason="Missing compose.yaml"
    )
    
    target = tmp_path / "app"
    env_file = tmp_path / ".env"
    
    result = runner.invoke(app, ["deploy", "deploy-project", "--path", str(target), "--env-file", str(env_file)])
    
    assert result.exit_code == 2
    assert "BLOCKED" in result.stdout
    assert "Missing compose.yaml" in result.stdout

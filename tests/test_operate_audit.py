"""
Tests for OPERATE audit engine.
"""

from pathlib import Path
from unittest.mock import patch

from models.enums import AuditClassification, CheckStatus, ClassificationImpact
from modules.operate.audit.runner import run_audit_project


@patch("modules.operate.audit.runner.check_endpoint_url")
@patch("modules.operate.audit.runner.check_runtime_status")
def test_run_audit_success(mock_runtime, mock_endpoint, tmp_path):
    from models.check_result import CheckResult
    
    target = tmp_path / "app"
    target.mkdir()
    (target / "project.yaml").write_text("project_slug: test-app\n")
    
    env_file = tmp_path / ".env"
    env_file.write_text("ENV=1")
    
    mock_runtime.return_value = CheckResult(
        check_id="OP_CHK_RUNTIME_01",
        title="Test",
        category="RUNTIME",
        description="Test",
        evidence_command="cmd",
        expected_behavior="pass",
        status=CheckStatus.OK,
        evidence="",
        message="All running",
        classification_impact=ClassificationImpact.NONE,
    )
    
    result = run_audit_project(str(target), str(env_file))
    
    assert result.classification == AuditClassification.HEALTHY
    assert result.project_slug == "test-app"
    assert len(result.checks) == 1
    assert result.checks[0].status == CheckStatus.OK


@patch("modules.operate.audit.runner.check_runtime_status")
def test_run_audit_degraded(mock_runtime, tmp_path):
    from models.check_result import CheckResult
    
    target = tmp_path / "app"
    target.mkdir()
    (target / "project.yaml").write_text("project_slug: test-app\n")
    env_file = tmp_path / ".env"
    env_file.write_text("ENV=1")
    
    mock_runtime.return_value = CheckResult(
        check_id="OP_CHK_RUNTIME_01",
        title="Test",
        category="RUNTIME",
        description="Test",
        evidence_command="cmd",
        expected_behavior="pass",
        status=CheckStatus.WARN,
        evidence="",
        message="Some down",
        classification_impact=ClassificationImpact.SANEABLE,
    )
    
    result = run_audit_project(str(target), str(env_file))
    
    assert result.classification == AuditClassification.DEGRADED
    assert "Some down" in result.degraded_findings


@patch("modules.operate.audit.runner.check_runtime_status")
def test_run_audit_blocked(mock_runtime, tmp_path):
    from models.check_result import CheckResult
    
    target = tmp_path / "app"
    target.mkdir()
    (target / "project.yaml").write_text("project_slug: test-app\n")
    env_file = tmp_path / ".env"
    env_file.write_text("ENV=1")
    
    mock_runtime.return_value = CheckResult(
        check_id="OP_CHK_RUNTIME_01",
        title="Test",
        category="RUNTIME",
        description="Test",
        evidence_command="cmd",
        expected_behavior="pass",
        status=CheckStatus.FAIL,
        evidence="",
        message="All down",
        classification_impact=ClassificationImpact.BLOCKED,
    )
    
    result = run_audit_project(str(target), str(env_file))
    
    assert result.classification == AuditClassification.BLOCKED
    assert "Runtime failure: All down" in result.blocked_reason

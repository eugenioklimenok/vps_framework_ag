"""
Runner for the OPERATE audit module.
"""

from pathlib import Path
from typing import Optional

from models.enums import AuditClassification, CheckStatus
from models.operate_result import ProjectAuditResult
from modules.operate.audit.checks import check_endpoint_url, check_runtime_status
from modules.operate.utils import validate_project_identity


def run_audit_project(path: str, env_file_path: str, endpoint_url: Optional[str] = None) -> ProjectAuditResult:
    """
    Orchestrates the project audit.
    """
    target_path = Path(path).resolve()
    env_file = Path(env_file_path).resolve()
    
    # Validate identity
    is_valid, slug, reason = validate_project_identity(target_path)
    if not is_valid:
        return ProjectAuditResult(
            classification=AuditClassification.BLOCKED,
            blocked_reason=reason
        )
        
    if not env_file.exists() or not env_file.is_file():
         return ProjectAuditResult(
            classification=AuditClassification.BLOCKED,
            project_slug=slug,
            blocked_reason=f"Environment file not found: {env_file}"
        )

    checks = []
    degraded_findings = []
    
    # 1. Runtime status check
    runtime_result = check_runtime_status(target_path, env_file, slug)
    checks.append(runtime_result)
    
    if runtime_result.status == CheckStatus.FAIL:
         return ProjectAuditResult(
            classification=AuditClassification.BLOCKED,
            project_slug=slug,
            checks=checks,
            blocked_reason=f"Runtime failure: {runtime_result.message}"
        )
    elif runtime_result.status == CheckStatus.WARN:
        degraded_findings.append(runtime_result.message)
        
    # 2. Optional endpoint check
    if endpoint_url:
        endpoint_result = check_endpoint_url(endpoint_url)
        checks.append(endpoint_result)
        
        if endpoint_result.status == CheckStatus.FAIL:
             return ProjectAuditResult(
                classification=AuditClassification.BLOCKED,
                project_slug=slug,
                checks=checks,
                blocked_reason=f"Endpoint failure: {endpoint_result.message}"
            )
        elif endpoint_result.status == CheckStatus.WARN:
             degraded_findings.append(endpoint_result.message)
             
    # Classification logic
    if degraded_findings:
        classification = AuditClassification.DEGRADED
    else:
        classification = AuditClassification.HEALTHY
        
    return ProjectAuditResult(
        classification=classification,
        project_slug=slug,
        checks=checks,
        degraded_findings=degraded_findings,
        validation_passed=True
    )

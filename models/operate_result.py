"""
Operate execution result models.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from models.check_result import CheckResult
from models.enums import AuditClassification, BackupResultState


@dataclass(frozen=True)
class ProjectAuditResult:
    """Result of an audit-project execution.
    
    Attributes:
        classification:   Final audit classification (HEALTHY, DEGRADED, BLOCKED).
        project_slug:     The resolved project identity.
        checks:           Ordered list of executed checks.
        degraded_findings: List of failed non-blocking checks.
        validation_passed: True if the audit completed successfully and rules were met.
        blocked_reason:   Reason for aborting, if applicable.
    """

    classification: AuditClassification
    project_slug: str = ""
    checks: list[CheckResult] = field(default_factory=list)
    degraded_findings: list[str] = field(default_factory=list)
    validation_passed: bool = False
    blocked_reason: str = ""


@dataclass(frozen=True)
class BackupResult:
    """Result of a backup-project execution.
    
    Attributes:
        result_state:     Final result state (CREATED, BLOCKED, FAILED).
        project_slug:     The resolved project identity.
        artifact_path:    Path to the created backup archive.
        checksum_path:    Path to the created checksum file (if any).
        artifact_validated: True if post-creation validation passed.
        blocked_reason:   Reason for aborting or failing, if applicable.
    """

    result_state: BackupResultState
    project_slug: str = ""
    artifact_path: Optional[Path] = None
    checksum_path: Optional[Path] = None
    artifact_validated: bool = False
    blocked_reason: str = ""
    plan: Optional[Any] = None

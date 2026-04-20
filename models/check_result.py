"""
CheckResult — Structured result object for individual audit checks.

Each audit check MUST return a CheckResult containing all fields required
by the AUDIT_VPS_SPEC.md §5.4 and §6.

This dataclass is the single source of truth for audit check outcomes.
It supports both human-readable output and future structured export (JSON).
"""

from dataclasses import dataclass

from models.enums import CheckStatus, ClassificationImpact


@dataclass(frozen=True)
class CheckResult:
    """Immutable result of a single audit check.

    Attributes:
        check_id:              Unique identifier (e.g., "CHECK_OS_01").
        title:                 Human-readable check name.
        category:              Check group (OS, USER, SSH, FILESYSTEM, SYSTEM).
        description:           What this check evaluates.
        evidence_command:       The system command used to collect evidence.
        expected_behavior:     What constitutes a passing result.
        status:                Result status (OK, WARN, FAIL).
        evidence:              Raw evidence collected from the system.
        message:               Human-readable result explanation.
        classification_impact: How this result affects host classification.
    """

    check_id: str
    title: str
    category: str
    description: str
    evidence_command: str
    expected_behavior: str
    status: CheckStatus
    evidence: str
    message: str
    classification_impact: ClassificationImpact

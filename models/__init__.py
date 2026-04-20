"""
Models package — Shared data models, enums, and typed result objects.

Public API:
    Enums:
        - CheckStatus: OK, WARN, FAIL
        - HostClassification: CLEAN, COMPATIBLE, SANEABLE, BLOCKED
        - ClassificationImpact: NONE, SANEABLE, BLOCKED
        - ReconcileAction: CREATED, REUSED, REPAIRED, SKIPPED, FAILED, BLOCKED

    Dataclasses:
        - CheckResult: Individual audit check outcome
        - CommandResult: Subprocess execution outcome
        - ReconcileResult: Reconciliation step outcome
        - ValidationResult: Post-action validation outcome
"""

from models.check_result import CheckResult
from models.command_result import CommandResult
from models.enums import (
    CheckStatus,
    ClassificationImpact,
    HostClassification,
    ReconcileAction,
)
from models.reconcile_result import ReconcileResult, ValidationResult

__all__ = [
    "CheckResult",
    "CheckStatus",
    "ClassificationImpact",
    "CommandResult",
    "HostClassification",
    "ReconcileAction",
    "ReconcileResult",
    "ValidationResult",
]

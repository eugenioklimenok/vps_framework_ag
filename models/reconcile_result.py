"""
ReconcileResult — Structured result for reconciliation and validation steps.

Used by init-vps to report the outcome of each reconciliation step.
Governed by: HOST_BASELINE_TDD.md §11.

Each reconciliation step MUST produce an explicit result containing:
    - action taken
    - state reused
    - ambiguity detected
    - validation passed or failed
    - fatal safety stop required
"""

from dataclasses import dataclass

from models.enums import ReconcileAction


@dataclass(frozen=True)
class ReconcileResult:
    """Immutable result of a single reconciliation step.

    Attributes:
        step_id:   Identifier for the reconciliation step (e.g., "RECONCILE_USER").
        action:    The action that was taken (CREATED, REUSED, REPAIRED, etc.).
        message:   Human-readable explanation of the outcome.
        evidence:  Raw evidence or detail about what was found/done.
        success:   Whether the step completed successfully.
    """

    step_id: str
    action: ReconcileAction
    message: str
    evidence: str
    success: bool


@dataclass(frozen=True)
class ValidationResult:
    """Immutable result of a single post-action validation check.

    Attributes:
        check_id:  Identifier for the validation check (e.g., "VALIDATE_USER_EXISTS").
        passed:    Whether the validation passed.
        message:   Human-readable explanation.
        evidence:  Raw evidence collected during validation.
    """

    check_id: str
    passed: bool
    message: str
    evidence: str

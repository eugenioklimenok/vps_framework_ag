"""
User Reconciliation — Create or reuse the operator user safely.

Governed by: HOST_BASELINE_CONTRACT.md §10, HOST_BASELINE_FDD.md §9,
             HOST_BASELINE_TDD.md §9.

Responsibilities:
    - Check if operator user exists
    - If exists and compatible → reuse
    - If missing → create safely
    - If ambiguous → abort (BLOCKED)
"""

import logging

from config.host_config import DEFAULT_OPERATOR_SHELL, get_expected_operator_home
from models.enums import ReconcileAction
from models.reconcile_result import ReconcileResult
from utils.subprocess_wrapper import run_command

logger = logging.getLogger(__name__)


def _user_exists(operator_user: str) -> bool | None:
    """Check if user exists. Returns True/False/None (ambiguous)."""
    result = run_command(["id", operator_user])
    if result.error:
        return None
    return result.returncode == 0


def _get_user_home(operator_user: str) -> str | None:
    """Get current home directory from passwd. Returns path or None."""
    result = run_command(["getent", "passwd", operator_user])
    if result.error or result.returncode != 0:
        return None
    parts = result.stdout_stripped.split(":")
    return parts[5] if len(parts) >= 6 else None


def _create_user(operator_user: str) -> ReconcileResult:
    """Create operator user with useradd -m -d <home> -s <shell>."""
    expected_home = get_expected_operator_home(operator_user)
    result = run_command([
        "useradd", "-m", "-d", expected_home, "-s", DEFAULT_OPERATOR_SHELL, operator_user,
    ])

    if result.error:
        return ReconcileResult(
            step_id="RECONCILE_USER_CREATE", action=ReconcileAction.FAILED,
            message=f"Failed to create user '{operator_user}': {result.error}",
            evidence=result.error, success=False,
        )
    if result.returncode != 0:
        detail = result.stderr_stripped or result.stdout_stripped
        return ReconcileResult(
            step_id="RECONCILE_USER_CREATE", action=ReconcileAction.FAILED,
            message=f"useradd failed for '{operator_user}': {detail}",
            evidence=detail, success=False,
        )
    return ReconcileResult(
        step_id="RECONCILE_USER_CREATE", action=ReconcileAction.CREATED,
        message=f"Operator user '{operator_user}' created with home '{expected_home}'",
        evidence=f"useradd -m -d {expected_home} -s {DEFAULT_OPERATOR_SHELL} {operator_user}",
        success=True,
    )


def reconcile_operator_user(operator_user: str) -> ReconcileResult:
    """Reconcile operator user: create if missing, reuse if compatible, abort if ambiguous.

    Args:
        operator_user: The operator username to reconcile.

    Returns:
        ReconcileResult indicating what action was taken.
    """
    logger.info("Reconciling operator user: %s", operator_user)
    exists = _user_exists(operator_user)

    if exists is None:
        return ReconcileResult(
            step_id="RECONCILE_USER", action=ReconcileAction.BLOCKED,
            message=f"Cannot determine if user '{operator_user}' exists. Aborting.",
            evidence="id command failed or ambiguous", success=False,
        )

    if not exists:
        logger.info("User '%s' does not exist. Creating...", operator_user)
        return _create_user(operator_user)

    # User exists — validate home mapping
    logger.info("User '%s' exists. Checking compatibility...", operator_user)
    actual_home = _get_user_home(operator_user)
    expected_home = get_expected_operator_home(operator_user)

    if actual_home is None:
        return ReconcileResult(
            step_id="RECONCILE_USER", action=ReconcileAction.BLOCKED,
            message=f"User '{operator_user}' exists but cannot read passwd. Aborting.",
            evidence="getent passwd failed", success=False,
        )

    if actual_home == expected_home:
        return ReconcileResult(
            step_id="RECONCILE_USER", action=ReconcileAction.REUSED,
            message=f"Operator user '{operator_user}' exists with expected home '{expected_home}'",
            evidence=f"home={actual_home}", success=True,
        )

    # Any home mismatch is ambiguous — abort per contract
    return ReconcileResult(
        step_id="RECONCILE_USER", action=ReconcileAction.BLOCKED,
        message=(
            f"User '{operator_user}' has mismatched home: actual='{actual_home}', "
            f"expected='{expected_home}'. Manual intervention required."
        ),
        evidence=f"actual_home={actual_home}, expected_home={expected_home}", success=False,
    )

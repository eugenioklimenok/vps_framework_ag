"""
Init Runner — Orchestrates gate → reconcile → validate flow for init-vps.

Governed by: HOST_BASELINE_TDD.md §8.2, HOST_BASELINE_CONTRACT.md §10.

Flow:
    1. Validate explicit inputs
    2. Execute audit gate (classification)
    3. If BLOCKED → abort with exit code 2
    4. Reconcile operator user
    5. Reconcile filesystem (home, .ssh, authorized_keys)
    6. Run post-action validation
    7. Return deterministic result
"""

import logging
from dataclasses import dataclass, field

from models.enums import HostClassification, ReconcileAction
from models.reconcile_result import ReconcileResult
from modules.host.audit.runner import AuditReport, run_audit
from modules.host.init.reconcile_filesystem import (
    reconcile_authorized_keys,
    reconcile_operator_home,
    reconcile_ssh_directory,
)
from modules.host.init.reconcile_user import reconcile_operator_user
from modules.host.init.reconcile_docker import (
    reconcile_docker_engine,
    reconcile_docker_compose,
    enable_start_docker,
    reconcile_docker_operator_access,
)
from modules.host.init.validate_docker import validate_docker_slice
from modules.host.init.validate import ValidationReport, validate_init_slice

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class InitResult:
    """Structured result of the init-vps command.

    Attributes:
        success:              Whether the entire init flow succeeded.
        audit_report:         The audit gate report (if audit was run).
        reconcile_results:    List of reconciliation step results.
        validation_report:    Post-action validation report (if reached).
        aborted:              Whether the flow was aborted before completion.
        abort_reason:         Reason for abort if applicable.
    """

    success: bool = False
    audit_report: AuditReport | None = None
    reconcile_results: list[ReconcileResult] = field(default_factory=list)
    validation_report: ValidationReport | None = None
    aborted: bool = False
    abort_reason: str = ""


def _load_public_key(public_key_input: str) -> str | None:
    """Load the public key from a file path or return it as a string.

    If the input looks like a file path (starts with / or contains .pub),
    attempt to read it. Otherwise, treat it as the key string itself.

    Args:
        public_key_input: File path or raw public key string.

    Returns:
        The public key string, or None if loading failed.
    """
    # Heuristic: if it starts with ssh- it's likely an inline key
    if public_key_input.strip().startswith("ssh-"):
        return public_key_input.strip()

    # Try to read as file path
    from utils.subprocess_wrapper import run_command
    result = run_command(["cat", public_key_input])
    if result.error or result.returncode != 0:
        logger.error("Failed to read public key file '%s': %s",
                      public_key_input, result.error or result.stderr_stripped)
        return None

    key = result.stdout_stripped
    if not key:
        logger.error("Public key file '%s' is empty", public_key_input)
        return None

    return key


def run_init(operator_user: str, public_key_input: str) -> InitResult:
    """Execute the init-vps reconciliation pipeline.

    Args:
        operator_user: The operator user identity.
        public_key_input: Public key file path or inline key string.

    Returns:
        InitResult with full pipeline outcome.
    """
    logger.info("Starting init-vps for operator user: %s", operator_user)

    # === Step 1: Validate inputs ===
    if not operator_user or not operator_user.strip():
        return InitResult(
            aborted=True, abort_reason="Operator user identity is empty.",
        )

    public_key = _load_public_key(public_key_input)
    if not public_key:
        return InitResult(
            aborted=True,
            abort_reason=f"Cannot load public key from: {public_key_input}",
        )

    # === Step 2: Audit gate ===
    logger.info("Running audit gate...")
    audit_report = run_audit(operator_user)

    # === Step 3: Classification gate ===
    if audit_report.classification == HostClassification.BLOCKED:
        logger.warning("Host is BLOCKED. Aborting init-vps.")
        return InitResult(
            audit_report=audit_report, aborted=True,
            abort_reason=(
                f"Host classification is BLOCKED. "
                f"({audit_report.fail_count} failures detected). "
                f"Manual intervention required before init-vps can proceed."
            ),
        )

    logger.info("Audit gate passed: %s", audit_report.classification.value)

    # === Step 4: Reconcile operator user ===
    reconcile_results: list[ReconcileResult] = []

    user_result = reconcile_operator_user(operator_user)
    reconcile_results.append(user_result)

    if not user_result.success:
        return InitResult(
            audit_report=audit_report, reconcile_results=reconcile_results,
            aborted=True,
            abort_reason=f"User reconciliation failed: {user_result.message}",
        )

    # === Step 5: Reconcile filesystem ===
    home_result = reconcile_operator_home(operator_user)
    reconcile_results.append(home_result)
    if not home_result.success:
        return InitResult(
            audit_report=audit_report, reconcile_results=reconcile_results,
            aborted=True,
            abort_reason=f"Home reconciliation failed: {home_result.message}",
        )

    ssh_result = reconcile_ssh_directory(operator_user)
    reconcile_results.append(ssh_result)
    if not ssh_result.success:
        return InitResult(
            audit_report=audit_report, reconcile_results=reconcile_results,
            aborted=True,
            abort_reason=f"SSH directory reconciliation failed: {ssh_result.message}",
        )

    ak_result = reconcile_authorized_keys(operator_user, public_key)
    reconcile_results.append(ak_result)
    if not ak_result.success:
        return InitResult(
            audit_report=audit_report, reconcile_results=reconcile_results,
            aborted=True,
            abort_reason=f"authorized_keys reconciliation failed: {ak_result.message}",
        )

    # === Step 6: Post-action validation ===
    logger.info("Running post-action validation...")
    validation_report = validate_init_slice(operator_user, public_key)

    if not validation_report.all_passed:
        failed = [r for r in validation_report.results if not r.passed]
        reasons = "; ".join(r.message for r in failed)
        return InitResult(
            audit_report=audit_report, reconcile_results=reconcile_results,
            validation_report=validation_report,
            abort_reason=f"Post-action validation failed: {reasons}",
        )

    # === Step 7: Reconcile Docker / Compose Runtime (Slice 02) ===
    logger.info("Reconciling Docker / Compose Runtime (Slice 02)...")
    
    docker_engine_res = reconcile_docker_engine()
    reconcile_results.append(docker_engine_res)
    if not docker_engine_res.success:
        return InitResult(
            audit_report=audit_report, reconcile_results=reconcile_results,
            validation_report=validation_report,
            aborted=True,
            abort_reason=docker_engine_res.message,
        )

    docker_compose_res = reconcile_docker_compose()
    reconcile_results.append(docker_compose_res)
    if not docker_compose_res.success:
        return InitResult(
            audit_report=audit_report, reconcile_results=reconcile_results,
            validation_report=validation_report,
            aborted=True,
            abort_reason=docker_compose_res.message,
        )

    docker_service_res = enable_start_docker()
    reconcile_results.append(docker_service_res)
    if not docker_service_res.success:
        return InitResult(
            audit_report=audit_report, reconcile_results=reconcile_results,
            validation_report=validation_report,
            aborted=True,
            abort_reason=docker_service_res.message,
        )

    operator_docker_res = reconcile_docker_operator_access(operator_user)
    reconcile_results.append(operator_docker_res)
    if not operator_docker_res.success:
        return InitResult(
            audit_report=audit_report, reconcile_results=reconcile_results,
            validation_report=validation_report,
            aborted=True,
            abort_reason=operator_docker_res.message,
        )

    # === Step 8: Validate Docker Slice 02 ===
    if not validate_docker_slice(operator_user):
        return InitResult(
            audit_report=audit_report, reconcile_results=reconcile_results,
            validation_report=validation_report,
            abort_reason="Post-action Docker runtime validation failed.",
        )

    # === Step 9: Success ===
    logger.info("init-vps completed successfully.")
    return InitResult(
        success=True, audit_report=audit_report,
        reconcile_results=reconcile_results,
        validation_report=validation_report,
    )

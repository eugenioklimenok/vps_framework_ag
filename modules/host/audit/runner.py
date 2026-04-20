"""
Audit Runner — Orchestrates all audit checks and produces the audit report.

Governed by: AUDIT_VPS_SPEC.md §10, §16 and HOST_BASELINE_TDD.md §8.1.

Flow:
    1. Execute all configured checks in documented order
    2. Aggregate results
    3. Reduce classification
    4. Return structured AuditReport

Implementation order (per AUDIT_VPS_SPEC §16):
    1. OS checks
    2. User checks
    3. SSH checks
    4. Filesystem checks
    5. System safety checks
"""

import logging
from dataclasses import dataclass, field

from models.check_result import CheckResult
from models.enums import CheckStatus, HostClassification
from modules.host.audit.checks_fs import (
    run_check_operator_home_state,
    run_check_operator_ssh_paths,
)
from modules.host.audit.checks_os import (
    run_check_os_architecture,
    run_check_os_supported,
)
from modules.host.audit.checks_ssh import (
    run_check_ssh_effective_config,
    run_check_ssh_syntax,
)
from modules.host.audit.checks_system import run_check_root_free_space
from modules.host.audit.checks_user import (
    run_check_user_exists,
    run_check_user_home_mapping,
)
from modules.host.audit.classifier import reduce_classification

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AuditReport:
    """Structured audit report containing all check results and final classification.

    Attributes:
        results:        Ordered list of all check results.
        classification: Final host classification derived from results.
        total:          Total number of checks executed.
        ok_count:       Number of checks with OK status.
        warn_count:     Number of checks with WARN status.
        fail_count:     Number of checks with FAIL status.
    """

    results: list[CheckResult] = field(default_factory=list)
    classification: HostClassification = HostClassification.BLOCKED
    total: int = 0
    ok_count: int = 0
    warn_count: int = 0
    fail_count: int = 0


def run_audit(operator_user: str) -> AuditReport:
    """Execute the full audit pipeline and return a structured report.

    Runs all 9 checks in documented order, aggregates results, and
    derives the final host classification.

    Args:
        operator_user: The operator user identity to evaluate.

    Returns:
        AuditReport with all results, classification, and summary counters.
    """
    logger.info("Starting HOST audit for operator user: %s", operator_user)

    results: list[CheckResult] = []

    # === OS Checks (§8.1) ===
    logger.debug("Running OS checks...")
    results.append(run_check_os_supported())
    results.append(run_check_os_architecture())

    # === USER Checks (§8.2) ===
    logger.debug("Running USER checks...")
    results.append(run_check_user_exists(operator_user))
    results.append(run_check_user_home_mapping(operator_user))

    # === SSH Checks (§8.3) ===
    logger.debug("Running SSH checks...")
    results.append(run_check_ssh_syntax())
    results.append(run_check_ssh_effective_config())

    # === FILESYSTEM Checks (§8.4) ===
    logger.debug("Running FILESYSTEM checks...")
    results.append(run_check_operator_home_state(operator_user))
    results.append(run_check_operator_ssh_paths(operator_user))

    # === SYSTEM SAFETY Checks (§8.5) ===
    logger.debug("Running SYSTEM checks...")
    results.append(run_check_root_free_space())

    # === Classification Reduction ===
    classification = reduce_classification(results)
    logger.info("Audit complete. Classification: %s", classification.value)

    # === Summary Counters ===
    ok_count = sum(1 for r in results if r.status == CheckStatus.OK)
    warn_count = sum(1 for r in results if r.status == CheckStatus.WARN)
    fail_count = sum(1 for r in results if r.status == CheckStatus.FAIL)

    return AuditReport(
        results=results,
        classification=classification,
        total=len(results),
        ok_count=ok_count,
        warn_count=warn_count,
        fail_count=fail_count,
    )

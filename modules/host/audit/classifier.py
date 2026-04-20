"""
Classification Reducer — Derives final host classification from audit check results.

Governed by: AUDIT_VPS_SPEC.md §7.

Classification Priority:
    BLOCKED > SANEABLE > COMPATIBLE > CLEAN

Rules:
    - BLOCKED: any check with ClassificationImpact.BLOCKED
    - SANEABLE: any check with ClassificationImpact.SANEABLE (and none BLOCKED)
    - COMPATIBLE: at least one WARN with no classification impact pushing higher
    - CLEAN: all checks OK with no impacts
"""

import logging

from models.check_result import CheckResult
from models.enums import CheckStatus, ClassificationImpact, HostClassification

logger = logging.getLogger(__name__)


def reduce_classification(results: list[CheckResult]) -> HostClassification:
    """Derive the final host classification from a list of audit check results.

    The classification is determined by scanning all results for their
    classification_impact values and applying the priority rule:
        BLOCKED > SANEABLE > COMPATIBLE > CLEAN

    Args:
        results: List of CheckResult objects from all audit checks.

    Returns:
        The final HostClassification for the host.
    """
    if not results:
        logger.warning("No check results provided — defaulting to BLOCKED")
        return HostClassification.BLOCKED

    has_blocked = False
    has_saneable = False
    has_warn = False

    for result in results:
        if result.classification_impact == ClassificationImpact.BLOCKED:
            has_blocked = True
        elif result.classification_impact == ClassificationImpact.SANEABLE:
            has_saneable = True

        if result.status == CheckStatus.WARN:
            has_warn = True

    # Apply priority: BLOCKED > SANEABLE > COMPATIBLE > CLEAN
    if has_blocked:
        return HostClassification.BLOCKED

    if has_saneable:
        return HostClassification.SANEABLE

    if has_warn:
        # Warnings with no SANEABLE/BLOCKED impact indicate compatible state
        # (e.g., SSH pre-hardening deviations that are acceptable)
        return HostClassification.COMPATIBLE

    return HostClassification.CLEAN

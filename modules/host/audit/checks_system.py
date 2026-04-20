"""
SYSTEM SAFETY Checks — CHECK_SYS_01.

Verifies essential system safety signals for safe baseline operations.
Governed by: AUDIT_VPS_SPEC.md §8.5.

CHECK_SYS_01 — Root Filesystem Free Space
    Evidence: df -Pk /
    OK: sufficient free space above LOW threshold
    WARN: low but usable space (between MIN and LOW) → SANEABLE
    FAIL: critically low space below MIN threshold → BLOCKED

Threshold Rule (§8.5):
    Threshold values must be documented in config and must not be hidden heuristics.
"""

import logging

from config.host_config import LOW_FREE_SPACE_MB, MIN_FREE_SPACE_MB
from models.check_result import CheckResult
from models.enums import CheckStatus, ClassificationImpact
from utils.subprocess_wrapper import run_command

logger = logging.getLogger(__name__)


def _parse_df_available_kb(output: str) -> int | None:
    """Parse available space in KB from df -Pk output.

    Expected format (POSIX):
        Filesystem     1024-blocks      Used Available Capacity Mounted on
        /dev/sda1        51474044   5234512  43603344      11% /

    The 'Available' column is the 4th field (index 3) of the second line.

    Args:
        output: Raw output from df -Pk /.

    Returns:
        Available space in KB, or None if parsing fails.
    """
    lines = output.strip().splitlines()
    if len(lines) < 2:
        return None

    # Take the data line (second line), split into fields
    fields = lines[1].split()
    if len(fields) < 4:
        return None

    try:
        return int(fields[3])
    except ValueError:
        return None


def run_check_root_free_space() -> CheckResult:
    """CHECK_SYS_01 — Verify adequate free space on root filesystem.

    Evidence command: df -Pk /
    Uses documented thresholds from config:
        - MIN_FREE_SPACE_MB: below this → BLOCKED
        - LOW_FREE_SPACE_MB: below this → WARN (SANEABLE)

    Returns:
        CheckResult with OK, WARN, or FAIL depending on available space.
    """
    cmd_result = run_command(["df", "-Pk", "/"])

    # Handle execution failure
    if cmd_result.error:
        return CheckResult(
            check_id="CHECK_SYS_01",
            title="Root Filesystem Free Space",
            category="SYSTEM",
            description="Verify adequate free space for safe baseline operations.",
            evidence_command="df -Pk /",
            expected_behavior=f"At least {MIN_FREE_SPACE_MB}MB free on root filesystem",
            status=CheckStatus.FAIL,
            evidence=cmd_result.error,
            message=f"Cannot determine root filesystem free space: {cmd_result.error}",
            classification_impact=ClassificationImpact.BLOCKED,
        )

    # Handle non-zero exit code
    if cmd_result.returncode != 0:
        return CheckResult(
            check_id="CHECK_SYS_01",
            title="Root Filesystem Free Space",
            category="SYSTEM",
            description="Verify adequate free space for safe baseline operations.",
            evidence_command="df -Pk /",
            expected_behavior=f"At least {MIN_FREE_SPACE_MB}MB free on root filesystem",
            status=CheckStatus.FAIL,
            evidence=cmd_result.stderr_stripped or cmd_result.stdout_stripped,
            message="Failed to check root filesystem free space",
            classification_impact=ClassificationImpact.BLOCKED,
        )

    # Parse available space
    available_kb = _parse_df_available_kb(cmd_result.stdout)

    if available_kb is None:
        return CheckResult(
            check_id="CHECK_SYS_01",
            title="Root Filesystem Free Space",
            category="SYSTEM",
            description="Verify adequate free space for safe baseline operations.",
            evidence_command="df -Pk /",
            expected_behavior=f"At least {MIN_FREE_SPACE_MB}MB free on root filesystem",
            status=CheckStatus.FAIL,
            evidence=cmd_result.stdout_stripped,
            message="Cannot parse df output to determine available space",
            classification_impact=ClassificationImpact.BLOCKED,
        )

    available_mb = available_kb // 1024
    evidence_str = f"available={available_mb}MB ({available_kb}KB)"

    # Critically low — BLOCKED
    if available_mb < MIN_FREE_SPACE_MB:
        return CheckResult(
            check_id="CHECK_SYS_01",
            title="Root Filesystem Free Space",
            category="SYSTEM",
            description="Verify adequate free space for safe baseline operations.",
            evidence_command="df -Pk /",
            expected_behavior=f"At least {MIN_FREE_SPACE_MB}MB free",
            status=CheckStatus.FAIL,
            evidence=evidence_str,
            message=(
                f"Critically low disk space: {available_mb}MB available "
                f"(minimum required: {MIN_FREE_SPACE_MB}MB)"
            ),
            classification_impact=ClassificationImpact.BLOCKED,
        )

    # Low but usable — WARN
    if available_mb < LOW_FREE_SPACE_MB:
        return CheckResult(
            check_id="CHECK_SYS_01",
            title="Root Filesystem Free Space",
            category="SYSTEM",
            description="Verify adequate free space for safe baseline operations.",
            evidence_command="df -Pk /",
            expected_behavior=f"At least {LOW_FREE_SPACE_MB}MB free (recommended)",
            status=CheckStatus.WARN,
            evidence=evidence_str,
            message=(
                f"Low disk space: {available_mb}MB available "
                f"(recommended: {LOW_FREE_SPACE_MB}MB)"
            ),
            classification_impact=ClassificationImpact.SANEABLE,
        )

    # Sufficient space — OK
    return CheckResult(
        check_id="CHECK_SYS_01",
        title="Root Filesystem Free Space",
        category="SYSTEM",
        description="Verify adequate free space for safe baseline operations.",
        evidence_command="df -Pk /",
        expected_behavior=f"At least {LOW_FREE_SPACE_MB}MB free",
        status=CheckStatus.OK,
        evidence=evidence_str,
        message=f"Sufficient disk space: {available_mb}MB available",
        classification_impact=ClassificationImpact.NONE,
    )

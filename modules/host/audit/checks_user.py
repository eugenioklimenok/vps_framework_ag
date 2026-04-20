"""
USER Checks — CHECK_USER_01 and CHECK_USER_02.

Verifies operator user existence and home directory mapping.
Governed by: AUDIT_VPS_SPEC.md §8.2.

CHECK_USER_01 — Operator User Exists
    Evidence: id <operator_user>
    OK: user exists
    WARN: user does not exist → SANEABLE

CHECK_USER_02 — Operator User Home Mapping
    Evidence: getent passwd <operator_user>
    OK: user exists with valid home path mapping
    WARN: user missing or home path differs but safely normalizable → SANEABLE
    FAIL: malformed passwd data or unsafe conflicting home state → BLOCKED
"""

import logging

from config.host_config import get_expected_operator_home
from models.check_result import CheckResult
from models.enums import CheckStatus, ClassificationImpact
from utils.subprocess_wrapper import run_command

logger = logging.getLogger(__name__)


def run_check_user_exists(operator_user: str) -> CheckResult:
    """CHECK_USER_01 — Verify whether the operator user exists.

    Evidence command: id <operator_user>

    Args:
        operator_user: The operator username to check.

    Returns:
        CheckResult with OK if user exists, WARN if missing (SANEABLE).
    """
    cmd_result = run_command(["id", operator_user])

    # Handle execution failure (binary not found, etc.)
    if cmd_result.error:
        return CheckResult(
            check_id="CHECK_USER_01",
            title="Operator User Exists",
            category="USER",
            description="Verify whether the operator user exists.",
            evidence_command=f"id {operator_user}",
            expected_behavior="User exists in the system",
            status=CheckStatus.WARN,
            evidence=cmd_result.error,
            message=f"Cannot verify operator user '{operator_user}': {cmd_result.error}",
            classification_impact=ClassificationImpact.SANEABLE,
        )

    # Non-zero exit code means user does not exist
    if cmd_result.returncode != 0:
        return CheckResult(
            check_id="CHECK_USER_01",
            title="Operator User Exists",
            category="USER",
            description="Verify whether the operator user exists.",
            evidence_command=f"id {operator_user}",
            expected_behavior="User exists in the system",
            status=CheckStatus.WARN,
            evidence=cmd_result.stderr_stripped or "user not found",
            message=f"Operator user '{operator_user}' does not exist",
            classification_impact=ClassificationImpact.SANEABLE,
        )

    # User exists
    return CheckResult(
        check_id="CHECK_USER_01",
        title="Operator User Exists",
        category="USER",
        description="Verify whether the operator user exists.",
        evidence_command=f"id {operator_user}",
        expected_behavior="User exists in the system",
        status=CheckStatus.OK,
        evidence=cmd_result.stdout_stripped,
        message=f"Operator user '{operator_user}' exists",
        classification_impact=ClassificationImpact.NONE,
    )


def _parse_passwd_entry(line: str) -> dict[str, str] | None:
    """Parse a single getent passwd line into structured fields.

    Expected format: username:x:uid:gid:gecos:home:shell

    Args:
        line: A single line from getent passwd output.

    Returns:
        Dictionary with keys (username, uid, gid, home, shell) or None if malformed.
    """
    parts = line.strip().split(":")
    if len(parts) < 7:
        return None
    return {
        "username": parts[0],
        "uid": parts[2],
        "gid": parts[3],
        "home": parts[5],
        "shell": parts[6],
    }


def run_check_user_home_mapping(operator_user: str) -> CheckResult:
    """CHECK_USER_02 — Verify the current passwd mapping for the operator user.

    Evidence command: getent passwd <operator_user>
    Expected parsing: username, home directory, shell

    Args:
        operator_user: The operator username to check.

    Returns:
        CheckResult with OK if valid home mapping, WARN if fixable, FAIL if ambiguous.
    """
    cmd_result = run_command(["getent", "passwd", operator_user])
    expected_home = get_expected_operator_home(operator_user)

    # Handle execution failure
    if cmd_result.error:
        return CheckResult(
            check_id="CHECK_USER_02",
            title="Operator User Home Mapping",
            category="USER",
            description="Verify the current passwd mapping for the operator user.",
            evidence_command=f"getent passwd {operator_user}",
            expected_behavior=f"User exists with home path {expected_home}",
            status=CheckStatus.WARN,
            evidence=cmd_result.error,
            message=f"Cannot verify passwd mapping for '{operator_user}': {cmd_result.error}",
            classification_impact=ClassificationImpact.SANEABLE,
        )

    # User not found in passwd (returncode 2 typically means not found)
    if cmd_result.returncode != 0:
        return CheckResult(
            check_id="CHECK_USER_02",
            title="Operator User Home Mapping",
            category="USER",
            description="Verify the current passwd mapping for the operator user.",
            evidence_command=f"getent passwd {operator_user}",
            expected_behavior=f"User exists with home path {expected_home}",
            status=CheckStatus.WARN,
            evidence=cmd_result.stderr_stripped or "user not found in passwd",
            message=f"Operator user '{operator_user}' not found in passwd database",
            classification_impact=ClassificationImpact.SANEABLE,
        )

    # Parse the passwd entry
    passwd_data = _parse_passwd_entry(cmd_result.stdout_stripped)

    if passwd_data is None:
        return CheckResult(
            check_id="CHECK_USER_02",
            title="Operator User Home Mapping",
            category="USER",
            description="Verify the current passwd mapping for the operator user.",
            evidence_command=f"getent passwd {operator_user}",
            expected_behavior=f"User exists with home path {expected_home}",
            status=CheckStatus.FAIL,
            evidence=cmd_result.stdout_stripped,
            message=f"Malformed passwd data for '{operator_user}'",
            classification_impact=ClassificationImpact.BLOCKED,
        )

    actual_home = passwd_data["home"]
    evidence_str = (
        f"username={passwd_data['username']}, "
        f"home={actual_home}, "
        f"shell={passwd_data['shell']}"
    )

    # Home matches expected path
    if actual_home == expected_home:
        return CheckResult(
            check_id="CHECK_USER_02",
            title="Operator User Home Mapping",
            category="USER",
            description="Verify the current passwd mapping for the operator user.",
            evidence_command=f"getent passwd {operator_user}",
            expected_behavior=f"User exists with home path {expected_home}",
            status=CheckStatus.OK,
            evidence=evidence_str,
            message=f"Operator user '{operator_user}' has expected home path: {actual_home}",
            classification_impact=ClassificationImpact.NONE,
        )

    # Home differs — check if it's in a safe normalizable location (/home/*)
    if actual_home.startswith("/home/"):
        return CheckResult(
            check_id="CHECK_USER_02",
            title="Operator User Home Mapping",
            category="USER",
            description="Verify the current passwd mapping for the operator user.",
            evidence_command=f"getent passwd {operator_user}",
            expected_behavior=f"User exists with home path {expected_home}",
            status=CheckStatus.WARN,
            evidence=evidence_str,
            message=(
                f"Operator user '{operator_user}' home path differs: "
                f"actual={actual_home}, expected={expected_home}. "
                f"Appears safe to normalize."
            ),
            classification_impact=ClassificationImpact.SANEABLE,
        )

    # Home is in an unsafe or conflicting location (e.g., /root, /var, etc.)
    return CheckResult(
        check_id="CHECK_USER_02",
        title="Operator User Home Mapping",
        category="USER",
        description="Verify the current passwd mapping for the operator user.",
        evidence_command=f"getent passwd {operator_user}",
        expected_behavior=f"User exists with home path {expected_home}",
        status=CheckStatus.FAIL,
        evidence=evidence_str,
        message=(
            f"Operator user '{operator_user}' maps to unsafe home path: {actual_home}. "
            f"Expected: {expected_home}. Manual intervention required."
        ),
        classification_impact=ClassificationImpact.BLOCKED,
    )

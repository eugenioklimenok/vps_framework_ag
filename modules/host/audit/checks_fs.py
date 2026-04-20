"""
FILESYSTEM Checks — CHECK_FS_01 and CHECK_FS_02.

Verifies operator home path state and SSH access paths.
Governed by: AUDIT_VPS_SPEC.md §8.4.

CHECK_FS_01 — Operator Home Path State
    Evidence: stat -c "%F %U %G %a %n" <expected_operator_home>
    OK: path exists as directory with compatible ownership, or path absent (safely creatable)
    WARN: path exists but requires safe ownership/permission normalization → SANEABLE
    FAIL: path is conflicting, not a directory, or unsafe → BLOCKED

CHECK_FS_02 — Operator SSH Access Paths
    Evidence: stat on .ssh and authorized_keys
    OK: both exist in compatible form
    WARN: one or more missing or need normalization → SANEABLE
    FAIL: conflicting or wrong type → BLOCKED
"""

import logging

from config.host_config import (
    EXPECTED_AUTHORIZED_KEYS_PERMISSION,
    EXPECTED_HOME_PERMISSION,
    EXPECTED_SSH_DIR_PERMISSION,
    get_expected_operator_home,
)
from models.check_result import CheckResult
from models.enums import CheckStatus, ClassificationImpact
from utils.subprocess_wrapper import run_command

logger = logging.getLogger(__name__)


def _parse_stat_output(output: str) -> dict[str, str] | None:
    """Parse output from stat -c '%F %U %G %a %n'.

    Expected format: "directory root root 755 /home/deploy"
    The file type may be multi-word (e.g., "regular file", "regular empty file").

    Args:
        output: Stripped stdout from stat command.

    Returns:
        Dictionary with keys (file_type, owner, group, permission, path) or None if malformed.
    """
    parts = output.strip().split()
    if len(parts) < 5:
        return None

    # The path is always the last element, permission is second-to-last,
    # group is third-to-last, owner is fourth-to-last.
    # Everything before owner is the file type (may be multi-word).
    path = parts[-1]
    permission = parts[-2]
    group = parts[-3]
    owner = parts[-4]
    file_type = " ".join(parts[:-4])

    return {
        "file_type": file_type,
        "owner": owner,
        "group": group,
        "permission": permission,
        "path": path,
    }


def run_check_operator_home_state(operator_user: str) -> CheckResult:
    """CHECK_FS_01 — Verify the state of the operator home path.

    Evidence command: stat -c "%F %U %G %a %n" <expected_operator_home>

    OK: path exists as directory with compatible ownership, or path absent (safely creatable).
    WARN: path exists but requires safe normalization.
    FAIL: path exists in conflicting or ambiguous form.

    Args:
        operator_user: The operator username.

    Returns:
        CheckResult with OK, WARN, or FAIL.
    """
    expected_home = get_expected_operator_home(operator_user)
    evidence_cmd = f'stat -c "%F %U %G %a %n" {expected_home}'
    cmd_result = run_command(["stat", "-c", "%F %U %G %a %n", expected_home])

    # Path does not exist — this is OK (safely creatable by init-vps)
    if cmd_result.returncode != 0 and not cmd_result.error:
        return CheckResult(
            check_id="CHECK_FS_01",
            title="Operator Home Path State",
            category="FILESYSTEM",
            description="Verify the state of the operator home path.",
            evidence_command=evidence_cmd,
            expected_behavior=f"Directory at {expected_home} or absent (safely creatable)",
            status=CheckStatus.OK,
            evidence=f"Path does not exist: {expected_home}",
            message=f"Operator home '{expected_home}' does not exist yet (safely creatable)",
            classification_impact=ClassificationImpact.NONE,
        )

    # Handle execution failure (stat binary not found, etc.)
    if cmd_result.error:
        return CheckResult(
            check_id="CHECK_FS_01",
            title="Operator Home Path State",
            category="FILESYSTEM",
            description="Verify the state of the operator home path.",
            evidence_command=evidence_cmd,
            expected_behavior=f"Directory at {expected_home} or absent (safely creatable)",
            status=CheckStatus.WARN,
            evidence=cmd_result.error,
            message=f"Cannot verify home path state: {cmd_result.error}",
            classification_impact=ClassificationImpact.SANEABLE,
        )

    # Parse stat output
    stat_data = _parse_stat_output(cmd_result.stdout_stripped)

    if stat_data is None:
        return CheckResult(
            check_id="CHECK_FS_01",
            title="Operator Home Path State",
            category="FILESYSTEM",
            description="Verify the state of the operator home path.",
            evidence_command=evidence_cmd,
            expected_behavior=f"Directory at {expected_home} or absent (safely creatable)",
            status=CheckStatus.FAIL,
            evidence=cmd_result.stdout_stripped,
            message=f"Cannot parse stat output for '{expected_home}'",
            classification_impact=ClassificationImpact.BLOCKED,
        )

    evidence_str = (
        f"type={stat_data['file_type']}, owner={stat_data['owner']}, "
        f"group={stat_data['group']}, permission={stat_data['permission']}, "
        f"path={stat_data['path']}"
    )

    # Must be a directory
    if "directory" not in stat_data["file_type"].lower():
        return CheckResult(
            check_id="CHECK_FS_01",
            title="Operator Home Path State",
            category="FILESYSTEM",
            description="Verify the state of the operator home path.",
            evidence_command=evidence_cmd,
            expected_behavior=f"Directory at {expected_home}",
            status=CheckStatus.FAIL,
            evidence=evidence_str,
            message=(
                f"Path '{expected_home}' exists but is not a directory: "
                f"{stat_data['file_type']}"
            ),
            classification_impact=ClassificationImpact.BLOCKED,
        )

    # Directory exists with correct owner
    if stat_data["owner"] == operator_user:
        if stat_data["permission"] == EXPECTED_HOME_PERMISSION:
            return CheckResult(
                check_id="CHECK_FS_01",
                title="Operator Home Path State",
                category="FILESYSTEM",
                description="Verify the state of the operator home path.",
                evidence_command=evidence_cmd,
                expected_behavior=f"Directory at {expected_home} owned by {operator_user}",
                status=CheckStatus.OK,
                evidence=evidence_str,
                message=f"Operator home '{expected_home}' exists with correct ownership and permissions",
                classification_impact=ClassificationImpact.NONE,
            )
        else:
            # Correct owner but wrong permissions — safely fixable
            return CheckResult(
                check_id="CHECK_FS_01",
                title="Operator Home Path State",
                category="FILESYSTEM",
                description="Verify the state of the operator home path.",
                evidence_command=evidence_cmd,
                expected_behavior=(
                    f"Directory at {expected_home} with permission {EXPECTED_HOME_PERMISSION}"
                ),
                status=CheckStatus.WARN,
                evidence=evidence_str,
                message=(
                    f"Operator home '{expected_home}' has wrong permissions: "
                    f"{stat_data['permission']} (expected {EXPECTED_HOME_PERMISSION})"
                ),
                classification_impact=ClassificationImpact.SANEABLE,
            )

    # Directory exists with different owner — check if root (potentially safe to chown)
    if stat_data["owner"] == "root":
        return CheckResult(
            check_id="CHECK_FS_01",
            title="Operator Home Path State",
            category="FILESYSTEM",
            description="Verify the state of the operator home path.",
            evidence_command=evidence_cmd,
            expected_behavior=f"Directory at {expected_home} owned by {operator_user}",
            status=CheckStatus.WARN,
            evidence=evidence_str,
            message=(
                f"Operator home '{expected_home}' owned by root "
                f"(expected {operator_user}). Safe to normalize."
            ),
            classification_impact=ClassificationImpact.SANEABLE,
        )

    # Different non-root owner — ambiguous and unsafe
    return CheckResult(
        check_id="CHECK_FS_01",
        title="Operator Home Path State",
        category="FILESYSTEM",
        description="Verify the state of the operator home path.",
        evidence_command=evidence_cmd,
        expected_behavior=f"Directory at {expected_home} owned by {operator_user}",
        status=CheckStatus.FAIL,
        evidence=evidence_str,
        message=(
            f"Operator home '{expected_home}' is owned by '{stat_data['owner']}' "
            f"(expected '{operator_user}'). Ownership conflict — manual intervention required."
        ),
        classification_impact=ClassificationImpact.BLOCKED,
    )


def _check_single_ssh_path(
    path: str,
    operator_user: str,
    expected_type: str,
    expected_permission: str,
    label: str,
) -> tuple[CheckStatus, ClassificationImpact, str, str]:
    """Check a single SSH-related filesystem path.

    Args:
        path: Full path to check.
        operator_user: Expected owner.
        expected_type: Expected file type ("directory" or "regular").
        expected_permission: Expected permission mode.
        label: Human-readable label for messages.

    Returns:
        Tuple of (status, impact, evidence, message).
    """
    cmd_result = run_command(["stat", "-c", "%F %U %G %a %n", path])

    # Path does not exist — safely creatable
    if cmd_result.returncode != 0 and not cmd_result.error:
        return (
            CheckStatus.WARN,
            ClassificationImpact.SANEABLE,
            f"Path does not exist: {path}",
            f"{label} does not exist at '{path}' (safely creatable)",
        )

    # Execution error
    if cmd_result.error:
        return (
            CheckStatus.WARN,
            ClassificationImpact.SANEABLE,
            cmd_result.error,
            f"Cannot verify {label}: {cmd_result.error}",
        )

    stat_data = _parse_stat_output(cmd_result.stdout_stripped)
    if stat_data is None:
        return (
            CheckStatus.FAIL,
            ClassificationImpact.BLOCKED,
            cmd_result.stdout_stripped,
            f"Cannot parse stat output for {label}",
        )

    evidence_str = (
        f"type={stat_data['file_type']}, owner={stat_data['owner']}, "
        f"permission={stat_data['permission']}"
    )

    # Verify file type
    if expected_type not in stat_data["file_type"].lower():
        return (
            CheckStatus.FAIL,
            ClassificationImpact.BLOCKED,
            evidence_str,
            f"{label} at '{path}' is not a {expected_type}: {stat_data['file_type']}",
        )

    # Check ownership and permissions
    issues: list[str] = []
    if stat_data["owner"] != operator_user:
        issues.append(f"owner={stat_data['owner']} (expected {operator_user})")
    if stat_data["permission"] != expected_permission:
        issues.append(f"permission={stat_data['permission']} (expected {expected_permission})")

    if not issues:
        return (
            CheckStatus.OK,
            ClassificationImpact.NONE,
            evidence_str,
            f"{label} exists with correct ownership and permissions",
        )

    # Issues found — determine if safely fixable
    if stat_data["owner"] in (operator_user, "root"):
        return (
            CheckStatus.WARN,
            ClassificationImpact.SANEABLE,
            evidence_str,
            f"{label} requires normalization: {'; '.join(issues)}",
        )

    return (
        CheckStatus.FAIL,
        ClassificationImpact.BLOCKED,
        evidence_str,
        f"{label} has conflicting state: {'; '.join(issues)}",
    )


def run_check_operator_ssh_paths(operator_user: str) -> CheckResult:
    """CHECK_FS_02 — Verify the state of .ssh and authorized_keys.

    Evidence commands:
        stat -c "%F %U %G %a %n" <home>/.ssh
        stat -c "%F %U %G %a %n" <home>/.ssh/authorized_keys

    OK: both exist in compatible form with safe ownership and permissions.
    WARN: one or more missing or require normalization → SANEABLE.
    FAIL: conflicting or ambiguous form → BLOCKED.

    Args:
        operator_user: The operator username.

    Returns:
        CheckResult with the worst status found across both paths.
    """
    expected_home = get_expected_operator_home(operator_user)
    ssh_dir = f"{expected_home}/.ssh"
    auth_keys = f"{expected_home}/.ssh/authorized_keys"

    evidence_cmd = (
        f'stat -c "%F %U %G %a %n" {ssh_dir}; '
        f'stat -c "%F %U %G %a %n" {auth_keys}'
    )

    # Check .ssh directory
    ssh_status, ssh_impact, ssh_evidence, ssh_message = _check_single_ssh_path(
        path=ssh_dir,
        operator_user=operator_user,
        expected_type="directory",
        expected_permission=EXPECTED_SSH_DIR_PERMISSION,
        label=".ssh directory",
    )

    # Check authorized_keys file
    ak_status, ak_impact, ak_evidence, ak_message = _check_single_ssh_path(
        path=auth_keys,
        operator_user=operator_user,
        expected_type="regular",
        expected_permission=EXPECTED_AUTHORIZED_KEYS_PERMISSION,
        label="authorized_keys",
    )

    # Combine evidence
    combined_evidence = f".ssh: [{ssh_evidence}] | authorized_keys: [{ak_evidence}]"
    combined_message = f"{ssh_message}; {ak_message}"

    # Determine worst status (FAIL > WARN > OK)
    status_priority = {CheckStatus.OK: 0, CheckStatus.WARN: 1, CheckStatus.FAIL: 2}
    worst_status = ssh_status if status_priority[ssh_status] >= status_priority[ak_status] else ak_status

    # Determine worst impact (BLOCKED > SANEABLE > NONE)
    impact_priority = {
        ClassificationImpact.NONE: 0,
        ClassificationImpact.SANEABLE: 1,
        ClassificationImpact.BLOCKED: 2,
    }
    worst_impact = ssh_impact if impact_priority[ssh_impact] >= impact_priority[ak_impact] else ak_impact

    return CheckResult(
        check_id="CHECK_FS_02",
        title="Operator SSH Access Paths",
        category="FILESYSTEM",
        description="Verify the state of .ssh and authorized_keys for safe reconciliation.",
        evidence_command=evidence_cmd,
        expected_behavior=(
            f".ssh directory ({EXPECTED_SSH_DIR_PERMISSION}) and "
            f"authorized_keys ({EXPECTED_AUTHORIZED_KEYS_PERMISSION}) "
            f"owned by {operator_user}"
        ),
        status=worst_status,
        evidence=combined_evidence,
        message=combined_message,
        classification_impact=worst_impact,
    )

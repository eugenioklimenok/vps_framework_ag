"""
Post-Action Validation — Verify all in-scope outcomes after reconciliation.

Governed by: HOST_BASELINE_CONTRACT.md §11, HOST_BASELINE_FDD.md §11.

Required validation for current init-vps slice:
    - Operator user exists
    - Expected operator home exists
    - .ssh exists with correct permissions (700) and ownership
    - authorized_keys exists with correct permissions (600) and ownership
    - Target public key is present in authorized_keys

Rule: If any required validation fails, the operation is FAILED.
"""

import logging
from dataclasses import dataclass, field

from config.host_config import (
    EXPECTED_AUTHORIZED_KEYS_PERMISSION,
    EXPECTED_SSH_DIR_PERMISSION,
    get_expected_operator_home,
)
from models.reconcile_result import ValidationResult
from utils.subprocess_wrapper import run_command

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ValidationReport:
    """Aggregated validation results for the init-vps slice.

    Attributes:
        results: List of individual validation check results.
        all_passed: Whether all validations passed.
    """

    results: list[ValidationResult] = field(default_factory=list)
    all_passed: bool = False


def _validate_user_exists(operator_user: str) -> ValidationResult:
    """Validate that the operator user exists."""
    result = run_command(["id", operator_user])
    passed = result.returncode == 0 and not result.error
    return ValidationResult(
        check_id="VALIDATE_USER_EXISTS", passed=passed,
        message=f"User '{operator_user}' {'exists' if passed else 'does NOT exist'}",
        evidence=result.stdout_stripped if passed else (result.error or result.stderr_stripped),
    )


def _validate_path_state(
    path: str, expected_type: str, expected_owner: str,
    expected_perm: str, check_id: str, label: str,
) -> ValidationResult:
    """Validate a path exists with correct type, ownership, and permissions."""
    result = run_command(["stat", "-c", "%F %U %a", path])
    if result.error or result.returncode != 0:
        return ValidationResult(
            check_id=check_id, passed=False,
            message=f"{label} at '{path}' does not exist or cannot be checked",
            evidence=result.error or result.stderr_stripped,
        )

    parts = result.stdout_stripped.rsplit(None, 2)
    if len(parts) < 3:
        return ValidationResult(
            check_id=check_id, passed=False,
            message=f"Cannot parse stat output for '{path}'",
            evidence=result.stdout_stripped,
        )

    # Parts: [file_type_words..., owner, permission]
    # Permission is last, owner is second-to-last, rest is file type
    all_parts = result.stdout_stripped.split()
    permission = all_parts[-1]
    owner = all_parts[-2]
    file_type = " ".join(all_parts[:-2]).lower()

    issues: list[str] = []
    if expected_type not in file_type:
        issues.append(f"type={file_type} (expected {expected_type})")
    if owner != expected_owner:
        issues.append(f"owner={owner} (expected {expected_owner})")
    if permission != expected_perm:
        issues.append(f"permission={permission} (expected {expected_perm})")

    if issues:
        return ValidationResult(
            check_id=check_id, passed=False,
            message=f"{label} validation failed: {'; '.join(issues)}",
            evidence=f"type={file_type}, owner={owner}, perm={permission}",
        )

    return ValidationResult(
        check_id=check_id, passed=True,
        message=f"{label} validated: correct type, ownership, and permissions",
        evidence=f"type={file_type}, owner={owner}, perm={permission}",
    )


def _validate_key_present(ak_path: str, public_key: str) -> ValidationResult:
    """Validate target public key is present in authorized_keys."""
    result = run_command(["cat", ak_path])
    if result.error or result.returncode != 0:
        return ValidationResult(
            check_id="VALIDATE_KEY_PRESENT", passed=False,
            message=f"Cannot read '{ak_path}' to verify key presence",
            evidence=result.error or result.stderr_stripped,
        )

    key_line = public_key.strip()
    existing = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    present = key_line in existing

    return ValidationResult(
        check_id="VALIDATE_KEY_PRESENT", passed=present,
        message=f"Target key {'is present' if present else 'NOT found'} in authorized_keys",
        evidence=f"key_count={len(existing)}, target_found={present}",
    )


def validate_init_slice(
    operator_user: str, public_key: str,
) -> ValidationReport:
    """Run all post-action validations for the current init-vps slice.

    Args:
        operator_user: The operator username.
        public_key: The public key string that should be present.

    Returns:
        ValidationReport with all results and overall pass/fail.
    """
    expected_home = get_expected_operator_home(operator_user)
    ssh_dir = f"{expected_home}/.ssh"
    ak_path = f"{expected_home}/.ssh/authorized_keys"

    logger.info("Running post-action validation for user: %s", operator_user)

    results: list[ValidationResult] = []

    # 1. User exists
    results.append(_validate_user_exists(operator_user))

    # 2. Home exists with correct ownership
    results.append(_validate_path_state(
        expected_home, "directory", operator_user, "755",
        "VALIDATE_HOME", "Operator home",
    ))

    # 3. .ssh exists with 700 and correct ownership
    results.append(_validate_path_state(
        ssh_dir, "directory", operator_user, EXPECTED_SSH_DIR_PERMISSION,
        "VALIDATE_SSH_DIR", ".ssh directory",
    ))

    # 4. authorized_keys exists with 600 and correct ownership
    results.append(_validate_path_state(
        ak_path, "regular", operator_user, EXPECTED_AUTHORIZED_KEYS_PERMISSION,
        "VALIDATE_AUTH_KEYS", "authorized_keys",
    ))

    # 5. Target key present
    results.append(_validate_key_present(ak_path, public_key))

    all_passed = all(r.passed for r in results)
    logger.info("Validation complete: all_passed=%s", all_passed)

    return ValidationReport(results=results, all_passed=all_passed)

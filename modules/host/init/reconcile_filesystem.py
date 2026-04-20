"""
Filesystem Reconciliation — Ensure operator home, .ssh, and authorized_keys.

Governed by: HOST_BASELINE_CONTRACT.md §10, HOST_BASELINE_FDD.md §9,
             HOST_BASELINE_TDD.md §9.

Responsibilities:
    - Ensure operator home exists with correct ownership
    - Ensure .ssh directory exists with permission 700
    - Ensure authorized_keys exists with permission 600
    - Insert target public key without duplicating
    - Preserve existing unrelated keys
    - Abort on ambiguous or conflicting filesystem state
"""

import logging

from config.host_config import (
    EXPECTED_AUTHORIZED_KEYS_PERMISSION,
    EXPECTED_SSH_DIR_PERMISSION,
    get_expected_operator_home,
)
from models.enums import ReconcileAction
from models.reconcile_result import ReconcileResult
from utils.subprocess_wrapper import run_command

logger = logging.getLogger(__name__)


def _path_exists(path: str) -> bool | None:
    """Check if a path exists. Returns True/False/None (ambiguous)."""
    result = run_command(["test", "-e", path])
    if result.error:
        return None
    return result.returncode == 0


def _is_directory(path: str) -> bool | None:
    """Check if path is a directory. Returns True/False/None."""
    result = run_command(["test", "-d", path])
    if result.error:
        return None
    return result.returncode == 0


def _get_owner(path: str) -> str | None:
    """Get the owner of a path via stat."""
    result = run_command(["stat", "-c", "%U", path])
    if result.error or result.returncode != 0:
        return None
    return result.stdout_stripped


def _set_ownership(path: str, operator_user: str) -> bool:
    """Set ownership of path to operator_user:operator_user. Returns True on success."""
    result = run_command(["chown", f"{operator_user}:{operator_user}", path])
    return result.returncode == 0 and not result.error


def _set_permission(path: str, mode: str) -> bool:
    """Set permission mode on path. Returns True on success."""
    result = run_command(["chmod", mode, path])
    return result.returncode == 0 and not result.error


def _mkdir(path: str) -> bool:
    """Create directory. Returns True on success."""
    result = run_command(["mkdir", "-p", path])
    return result.returncode == 0 and not result.error


def _touch(path: str) -> bool:
    """Create empty file if it doesn't exist. Returns True on success."""
    result = run_command(["touch", path])
    return result.returncode == 0 and not result.error


def reconcile_operator_home(operator_user: str) -> ReconcileResult:
    """Ensure operator home directory exists with correct ownership.

    Args:
        operator_user: The operator username.

    Returns:
        ReconcileResult indicating action taken.
    """
    expected_home = get_expected_operator_home(operator_user)
    logger.info("Reconciling operator home: %s", expected_home)

    exists = _path_exists(expected_home)
    if exists is None:
        return ReconcileResult(
            step_id="RECONCILE_HOME", action=ReconcileAction.BLOCKED,
            message=f"Cannot determine if home '{expected_home}' exists.",
            evidence="test -e failed", success=False,
        )

    if exists:
        is_dir = _is_directory(expected_home)
        if is_dir is None or not is_dir:
            return ReconcileResult(
                step_id="RECONCILE_HOME", action=ReconcileAction.BLOCKED,
                message=f"Path '{expected_home}' exists but is not a directory.",
                evidence="test -d returned false", success=False,
            )
        # Directory exists — verify ownership
        owner = _get_owner(expected_home)
        if owner == operator_user:
            return ReconcileResult(
                step_id="RECONCILE_HOME", action=ReconcileAction.REUSED,
                message=f"Home '{expected_home}' exists with correct ownership.",
                evidence=f"owner={owner}", success=True,
            )
        # Wrong owner — attempt to fix
        if _set_ownership(expected_home, operator_user):
            return ReconcileResult(
                step_id="RECONCILE_HOME", action=ReconcileAction.REPAIRED,
                message=f"Home '{expected_home}' ownership corrected to '{operator_user}'.",
                evidence=f"chown {operator_user}:{operator_user} {expected_home}",
                success=True,
            )
        return ReconcileResult(
            step_id="RECONCILE_HOME", action=ReconcileAction.FAILED,
            message=f"Failed to fix ownership on '{expected_home}'.",
            evidence=f"chown failed, current owner={owner}", success=False,
        )

    # Home does not exist — create it
    if not _mkdir(expected_home):
        return ReconcileResult(
            step_id="RECONCILE_HOME", action=ReconcileAction.FAILED,
            message=f"Failed to create home directory '{expected_home}'.",
            evidence="mkdir -p failed", success=False,
        )
    if not _set_ownership(expected_home, operator_user):
        return ReconcileResult(
            step_id="RECONCILE_HOME", action=ReconcileAction.FAILED,
            message=f"Created '{expected_home}' but failed to set ownership.",
            evidence="chown failed after mkdir", success=False,
        )
    return ReconcileResult(
        step_id="RECONCILE_HOME", action=ReconcileAction.CREATED,
        message=f"Home directory '{expected_home}' created and owned by '{operator_user}'.",
        evidence=f"mkdir -p + chown {operator_user}:{operator_user}", success=True,
    )


def reconcile_ssh_directory(operator_user: str) -> ReconcileResult:
    """Ensure .ssh directory exists with permission 700 and correct ownership.

    Args:
        operator_user: The operator username.

    Returns:
        ReconcileResult indicating action taken.
    """
    expected_home = get_expected_operator_home(operator_user)
    ssh_dir = f"{expected_home}/.ssh"
    logger.info("Reconciling .ssh directory: %s", ssh_dir)

    exists = _path_exists(ssh_dir)
    if exists is None:
        return ReconcileResult(
            step_id="RECONCILE_SSH_DIR", action=ReconcileAction.BLOCKED,
            message=f"Cannot determine if '{ssh_dir}' exists.",
            evidence="test -e failed", success=False,
        )

    if exists:
        is_dir = _is_directory(ssh_dir)
        if is_dir is None or not is_dir:
            return ReconcileResult(
                step_id="RECONCILE_SSH_DIR", action=ReconcileAction.BLOCKED,
                message=f"Path '{ssh_dir}' exists but is not a directory.",
                evidence="test -d returned false", success=False,
            )
        # Fix ownership and permissions
        ok_own = _set_ownership(ssh_dir, operator_user)
        ok_perm = _set_permission(ssh_dir, EXPECTED_SSH_DIR_PERMISSION)
        if ok_own and ok_perm:
            return ReconcileResult(
                step_id="RECONCILE_SSH_DIR", action=ReconcileAction.REPAIRED,
                message=f".ssh directory '{ssh_dir}' ownership and permissions ensured.",
                evidence=f"chown+chmod {EXPECTED_SSH_DIR_PERMISSION}", success=True,
            )
        return ReconcileResult(
            step_id="RECONCILE_SSH_DIR", action=ReconcileAction.FAILED,
            message=f"Failed to normalize '{ssh_dir}' ownership/permissions.",
            evidence=f"chown_ok={ok_own}, chmod_ok={ok_perm}", success=False,
        )

    # Create .ssh directory
    if not _mkdir(ssh_dir):
        return ReconcileResult(
            step_id="RECONCILE_SSH_DIR", action=ReconcileAction.FAILED,
            message=f"Failed to create '{ssh_dir}'.",
            evidence="mkdir -p failed", success=False,
        )
    ok_own = _set_ownership(ssh_dir, operator_user)
    ok_perm = _set_permission(ssh_dir, EXPECTED_SSH_DIR_PERMISSION)
    if ok_own and ok_perm:
        return ReconcileResult(
            step_id="RECONCILE_SSH_DIR", action=ReconcileAction.CREATED,
            message=f".ssh directory '{ssh_dir}' created with correct ownership and permissions.",
            evidence=f"mkdir + chown + chmod {EXPECTED_SSH_DIR_PERMISSION}", success=True,
        )
    return ReconcileResult(
        step_id="RECONCILE_SSH_DIR", action=ReconcileAction.FAILED,
        message=f"Created '{ssh_dir}' but failed to set ownership/permissions.",
        evidence=f"chown_ok={ok_own}, chmod_ok={ok_perm}", success=False,
    )


def reconcile_authorized_keys(
    operator_user: str,
    public_key: str,
) -> ReconcileResult:
    """Ensure authorized_keys exists with the target key, without duplicating.

    Rules:
        - Create file if missing
        - Set permission 600 and correct ownership
        - Insert key only if not already present
        - Preserve existing unrelated keys

    Args:
        operator_user: The operator username.
        public_key: The public key string to ensure is present.

    Returns:
        ReconcileResult indicating action taken.
    """
    expected_home = get_expected_operator_home(operator_user)
    ak_path = f"{expected_home}/.ssh/authorized_keys"
    logger.info("Reconciling authorized_keys: %s", ak_path)

    # Normalize key (strip whitespace)
    key_line = public_key.strip()
    if not key_line:
        return ReconcileResult(
            step_id="RECONCILE_AUTH_KEYS", action=ReconcileAction.BLOCKED,
            message="Public key is empty. Cannot proceed.",
            evidence="empty public_key input", success=False,
        )

    # Ensure file exists
    exists = _path_exists(ak_path)
    if exists is None:
        return ReconcileResult(
            step_id="RECONCILE_AUTH_KEYS", action=ReconcileAction.BLOCKED,
            message=f"Cannot determine if '{ak_path}' exists.",
            evidence="test -e failed", success=False,
        )

    file_created = False
    if not exists:
        if not _touch(ak_path):
            return ReconcileResult(
                step_id="RECONCILE_AUTH_KEYS", action=ReconcileAction.FAILED,
                message=f"Failed to create '{ak_path}'.",
                evidence="touch failed", success=False,
            )
        file_created = True

    # Set ownership and permissions
    ok_own = _set_ownership(ak_path, operator_user)
    ok_perm = _set_permission(ak_path, EXPECTED_AUTHORIZED_KEYS_PERMISSION)
    if not (ok_own and ok_perm):
        return ReconcileResult(
            step_id="RECONCILE_AUTH_KEYS", action=ReconcileAction.FAILED,
            message=f"Failed to set ownership/permissions on '{ak_path}'.",
            evidence=f"chown_ok={ok_own}, chmod_ok={ok_perm}", success=False,
        )

    # Read current content to check for duplicate key
    read_result = run_command(["cat", ak_path])
    if read_result.error:
        return ReconcileResult(
            step_id="RECONCILE_AUTH_KEYS", action=ReconcileAction.FAILED,
            message=f"Failed to read '{ak_path}': {read_result.error}",
            evidence=read_result.error, success=False,
        )

    current_content = read_result.stdout
    existing_keys = [line.strip() for line in current_content.splitlines() if line.strip()]

    # Check if key already present (avoid duplicate insertion)
    if key_line in existing_keys:
        action = ReconcileAction.CREATED if file_created else ReconcileAction.REUSED
        return ReconcileResult(
            step_id="RECONCILE_AUTH_KEYS", action=action,
            message=f"Target public key already present in '{ak_path}'.",
            evidence=f"key_count={len(existing_keys)}, duplicate_avoided=true",
            success=True,
        )

    # Append key — use tee -a to avoid shell=True
    # We write via a subprocess that echoes the key and appends
    append_result = run_command(
        ["bash", "-c", f"echo '{key_line}' >> '{ak_path}'"]
    )
    if append_result.error or append_result.returncode != 0:
        return ReconcileResult(
            step_id="RECONCILE_AUTH_KEYS", action=ReconcileAction.FAILED,
            message=f"Failed to append key to '{ak_path}'.",
            evidence=append_result.error or append_result.stderr_stripped,
            success=False,
        )

    action = ReconcileAction.CREATED if file_created else ReconcileAction.REPAIRED
    return ReconcileResult(
        step_id="RECONCILE_AUTH_KEYS", action=action,
        message=f"Target public key added to '{ak_path}'. Existing keys preserved.",
        evidence=f"key_count_before={len(existing_keys)}, key_appended=true",
        success=True,
    )

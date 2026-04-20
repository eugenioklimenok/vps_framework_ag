"""
SSH Checks — CHECK_SSH_01 and CHECK_SSH_02.

Verifies SSH daemon availability, syntax validity, and effective runtime configuration.
Governed by: AUDIT_VPS_SPEC.md §8.3.

CHECK_SSH_01 — sshd Binary and Syntax Validity
    Evidence: sshd -t
    OK: exit code success, no syntax errors
    FAIL: binary missing, syntax invalid → BLOCKED

CHECK_SSH_02 — Effective SSH Runtime Configuration
    Evidence: sshd -T
    OK: pubkeyauthentication yes
    WARN: password auth enabled, root login not hardened (non-blocking)
    FAIL: pubkeyauthentication no, effective config undetermined → BLOCKED

Interpretation Rule (§8.3):
    Because SSH hardening is deferred from the current init-vps slice:
    - password authentication enabled is NOT blocking
    - lack of trusted key-auth capability IS blocking
"""

import logging

from config.host_config import REQUIRED_PUBKEY_AUTH, SSH_CONFIG_KEYS
from models.check_result import CheckResult
from models.enums import CheckStatus, ClassificationImpact
from utils.subprocess_wrapper import run_command

logger = logging.getLogger(__name__)


def run_check_ssh_syntax() -> CheckResult:
    """CHECK_SSH_01 — Verify SSH daemon availability and valid syntax.

    Evidence command: sshd -t
    OK if exit code is 0 (no syntax errors).
    FAIL if binary missing, syntax invalid, or execution error.

    Returns:
        CheckResult with OK or FAIL (BLOCKED).
    """
    cmd_result = run_command(["sshd", "-t"])

    # Handle execution failure (binary not found)
    if cmd_result.error:
        return CheckResult(
            check_id="CHECK_SSH_01",
            title="sshd Binary and Syntax Validity",
            category="SSH",
            description="Verify SSH daemon availability and valid syntax.",
            evidence_command="sshd -t",
            expected_behavior="Exit code 0, no syntax errors",
            status=CheckStatus.FAIL,
            evidence=cmd_result.error,
            message=f"SSH daemon not available: {cmd_result.error}",
            classification_impact=ClassificationImpact.BLOCKED,
        )

    # Non-zero exit code means syntax error or other failure
    if cmd_result.returncode != 0:
        error_detail = cmd_result.stderr_stripped or cmd_result.stdout_stripped
        return CheckResult(
            check_id="CHECK_SSH_01",
            title="sshd Binary and Syntax Validity",
            category="SSH",
            description="Verify SSH daemon availability and valid syntax.",
            evidence_command="sshd -t",
            expected_behavior="Exit code 0, no syntax errors",
            status=CheckStatus.FAIL,
            evidence=error_detail,
            message=f"SSH daemon configuration has syntax errors: {error_detail}",
            classification_impact=ClassificationImpact.BLOCKED,
        )

    # sshd -t succeeded — syntax is valid
    return CheckResult(
        check_id="CHECK_SSH_01",
        title="sshd Binary and Syntax Validity",
        category="SSH",
        description="Verify SSH daemon availability and valid syntax.",
        evidence_command="sshd -t",
        expected_behavior="Exit code 0, no syntax errors",
        status=CheckStatus.OK,
        evidence="sshd -t returned exit code 0",
        message="SSH daemon configuration syntax is valid",
        classification_impact=ClassificationImpact.NONE,
    )


def _parse_sshd_config(content: str) -> dict[str, str]:
    """Parse effective SSH config output (sshd -T) into key-value pairs.

    sshd -T outputs lines like:
        pubkeyauthentication yes
        passwordauthentication yes
        permitrootlogin prohibit-password

    Args:
        content: Raw output from sshd -T.

    Returns:
        Dictionary of lowercase key → value pairs for the keys we care about.
    """
    result: dict[str, str] = {}
    for line in content.splitlines():
        line = line.strip().lower()
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) == 2 and parts[0] in SSH_CONFIG_KEYS:
            result[parts[0]] = parts[1]
    return result


def run_check_ssh_effective_config() -> CheckResult:
    """CHECK_SSH_02 — Inspect effective SSH runtime configuration.

    Evidence command: sshd -T
    Expected parsing: pubkeyauthentication, passwordauthentication,
                      permitrootlogin, kbdinteractiveauthentication

    OK: pubkeyauthentication yes
    WARN: password auth enabled, root login not hardened (non-blocking before harden-vps)
    FAIL: pubkeyauthentication no or config cannot be determined → BLOCKED

    Returns:
        CheckResult with OK, WARN, or FAIL depending on effective config.
    """
    cmd_result = run_command(["sshd", "-T"])

    # Handle execution failure
    if cmd_result.error:
        return CheckResult(
            check_id="CHECK_SSH_02",
            title="Effective SSH Runtime Configuration",
            category="SSH",
            description="Inspect effective SSH configuration for key-auth capability.",
            evidence_command="sshd -T",
            expected_behavior=f"pubkeyauthentication {REQUIRED_PUBKEY_AUTH}",
            status=CheckStatus.FAIL,
            evidence=cmd_result.error,
            message=f"Cannot determine effective SSH configuration: {cmd_result.error}",
            classification_impact=ClassificationImpact.BLOCKED,
        )

    # Non-zero exit code
    if cmd_result.returncode != 0:
        error_detail = cmd_result.stderr_stripped or cmd_result.stdout_stripped
        return CheckResult(
            check_id="CHECK_SSH_02",
            title="Effective SSH Runtime Configuration",
            category="SSH",
            description="Inspect effective SSH configuration for key-auth capability.",
            evidence_command="sshd -T",
            expected_behavior=f"pubkeyauthentication {REQUIRED_PUBKEY_AUTH}",
            status=CheckStatus.FAIL,
            evidence=error_detail,
            message=f"Cannot determine effective SSH configuration: {error_detail}",
            classification_impact=ClassificationImpact.BLOCKED,
        )

    # Parse the effective config
    ssh_config = _parse_sshd_config(cmd_result.stdout)

    # Build evidence string from parsed values
    evidence_parts = [f"{k}={ssh_config.get(k, 'unknown')}" for k in SSH_CONFIG_KEYS]
    evidence_str = ", ".join(evidence_parts)

    # Critical check: pubkeyauthentication must be enabled
    pubkey_auth = ssh_config.get("pubkeyauthentication", "unknown")
    if pubkey_auth != REQUIRED_PUBKEY_AUTH:
        return CheckResult(
            check_id="CHECK_SSH_02",
            title="Effective SSH Runtime Configuration",
            category="SSH",
            description="Inspect effective SSH configuration for key-auth capability.",
            evidence_command="sshd -T",
            expected_behavior=f"pubkeyauthentication {REQUIRED_PUBKEY_AUTH}",
            status=CheckStatus.FAIL,
            evidence=evidence_str,
            message=(
                f"Public key authentication is not enabled: "
                f"pubkeyauthentication={pubkey_auth}"
            ),
            classification_impact=ClassificationImpact.BLOCKED,
        )

    # Non-blocking warnings: password auth or root login not yet hardened
    # These are acceptable before harden-vps (per AUDIT_VPS_SPEC §8.3 interpretation rule)
    warnings: list[str] = []
    password_auth = ssh_config.get("passwordauthentication", "unknown")
    if password_auth == "yes":
        warnings.append("password authentication is enabled")

    permit_root = ssh_config.get("permitrootlogin", "unknown")
    if permit_root not in ("no", "prohibit-password"):
        warnings.append(f"root login policy is not yet hardened (permitrootlogin={permit_root})")

    kbd_auth = ssh_config.get("kbdinteractiveauthentication", "unknown")
    if kbd_auth == "yes":
        warnings.append("keyboard-interactive authentication is enabled")

    if warnings:
        return CheckResult(
            check_id="CHECK_SSH_02",
            title="Effective SSH Runtime Configuration",
            category="SSH",
            description="Inspect effective SSH configuration for key-auth capability.",
            evidence_command="sshd -T",
            expected_behavior=f"pubkeyauthentication {REQUIRED_PUBKEY_AUTH}",
            status=CheckStatus.WARN,
            evidence=evidence_str,
            message=(
                f"SSH key-auth is enabled but pre-hardening deviations detected: "
                f"{'; '.join(warnings)}"
            ),
            classification_impact=ClassificationImpact.NONE,
        )

    # Everything looks good
    return CheckResult(
        check_id="CHECK_SSH_02",
        title="Effective SSH Runtime Configuration",
        category="SSH",
        description="Inspect effective SSH configuration for key-auth capability.",
        evidence_command="sshd -T",
        expected_behavior=f"pubkeyauthentication {REQUIRED_PUBKEY_AUTH}",
        status=CheckStatus.OK,
        evidence=evidence_str,
        message="SSH effective configuration is fully aligned",
        classification_impact=ClassificationImpact.NONE,
    )

"""
OS Checks — CHECK_OS_01 and CHECK_OS_02.

Verifies operating system support and CPU architecture.
Governed by: AUDIT_VPS_SPEC.md §8.1.

CHECK_OS_01 — Supported Operating System
    Evidence: cat /etc/os-release
    OK: ID=ubuntu, VERSION_ID in supported list
    FAIL: file missing, non-Ubuntu, unsupported version → BLOCKED

CHECK_OS_02 — CPU Architecture
    Evidence: uname -m
    OK: x86_64 or aarch64
    FAIL: any other value → BLOCKED
"""

import logging

from config.host_config import (
    SUPPORTED_ARCHITECTURES,
    SUPPORTED_OS_IDS,
    SUPPORTED_UBUNTU_VERSIONS,
)
from models.check_result import CheckResult
from models.enums import CheckStatus, ClassificationImpact
from utils.subprocess_wrapper import run_command

logger = logging.getLogger(__name__)


def _parse_os_release(content: str) -> dict[str, str]:
    """Parse /etc/os-release content into a key-value dictionary.

    Handles quoted and unquoted values. Lines without '=' are skipped.

    Args:
        content: Raw content of /etc/os-release.

    Returns:
        Dictionary of key-value pairs (e.g., {"ID": "ubuntu", "VERSION_ID": "24.04"}).
    """
    result: dict[str, str] = {}
    for line in content.splitlines():
        line = line.strip()
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        # Remove surrounding quotes if present
        value = value.strip().strip('"').strip("'")
        result[key.strip()] = value
    return result


def run_check_os_supported() -> CheckResult:
    """CHECK_OS_01 — Verify that the host runs a supported Ubuntu release.

    Evidence command: cat /etc/os-release
    Expected parsing: ID, VERSION_ID, PRETTY_NAME

    Returns:
        CheckResult with OK if Ubuntu and supported version, FAIL otherwise.
    """
    cmd_result = run_command(["cat", "/etc/os-release"])

    # Handle execution failure
    if cmd_result.error:
        return CheckResult(
            check_id="CHECK_OS_01",
            title="Supported Operating System",
            category="OS",
            description="Verify that the host runs a supported Ubuntu release.",
            evidence_command="cat /etc/os-release",
            expected_behavior="ID=ubuntu, VERSION_ID in supported list",
            status=CheckStatus.FAIL,
            evidence=cmd_result.error,
            message=f"Failed to read /etc/os-release: {cmd_result.error}",
            classification_impact=ClassificationImpact.BLOCKED,
        )

    # Handle non-zero exit code (file missing or read error)
    if cmd_result.returncode != 0:
        return CheckResult(
            check_id="CHECK_OS_01",
            title="Supported Operating System",
            category="OS",
            description="Verify that the host runs a supported Ubuntu release.",
            evidence_command="cat /etc/os-release",
            expected_behavior="ID=ubuntu, VERSION_ID in supported list",
            status=CheckStatus.FAIL,
            evidence=cmd_result.stderr_stripped or cmd_result.stdout_stripped,
            message="/etc/os-release not found or not readable",
            classification_impact=ClassificationImpact.BLOCKED,
        )

    # Parse the file content
    os_data = _parse_os_release(cmd_result.stdout)
    os_id = os_data.get("ID", "").lower()
    version_id = os_data.get("VERSION_ID", "")
    pretty_name = os_data.get("PRETTY_NAME", "unknown")

    evidence_str = f"ID={os_id}, VERSION_ID={version_id}, PRETTY_NAME={pretty_name}"

    # Validate OS ID
    if os_id not in SUPPORTED_OS_IDS:
        return CheckResult(
            check_id="CHECK_OS_01",
            title="Supported Operating System",
            category="OS",
            description="Verify that the host runs a supported Ubuntu release.",
            evidence_command="cat /etc/os-release",
            expected_behavior=f"ID in {SUPPORTED_OS_IDS}",
            status=CheckStatus.FAIL,
            evidence=evidence_str,
            message=f"Unsupported operating system: {os_id} ({pretty_name})",
            classification_impact=ClassificationImpact.BLOCKED,
        )

    # Validate version
    if version_id not in SUPPORTED_UBUNTU_VERSIONS:
        return CheckResult(
            check_id="CHECK_OS_01",
            title="Supported Operating System",
            category="OS",
            description="Verify that the host runs a supported Ubuntu release.",
            evidence_command="cat /etc/os-release",
            expected_behavior=f"VERSION_ID in {SUPPORTED_UBUNTU_VERSIONS}",
            status=CheckStatus.FAIL,
            evidence=evidence_str,
            message=f"Unsupported Ubuntu version: {version_id} ({pretty_name})",
            classification_impact=ClassificationImpact.BLOCKED,
        )

    # All checks passed
    return CheckResult(
        check_id="CHECK_OS_01",
        title="Supported Operating System",
        category="OS",
        description="Verify that the host runs a supported Ubuntu release.",
        evidence_command="cat /etc/os-release",
        expected_behavior=f"ID in {SUPPORTED_OS_IDS}, VERSION_ID in {SUPPORTED_UBUNTU_VERSIONS}",
        status=CheckStatus.OK,
        evidence=evidence_str,
        message=f"Supported operating system detected: {pretty_name}",
        classification_impact=ClassificationImpact.NONE,
    )


def run_check_os_architecture() -> CheckResult:
    """CHECK_OS_02 — Verify supported CPU architecture.

    Evidence command: uname -m
    OK: x86_64 or aarch64
    FAIL: any other value → BLOCKED

    Returns:
        CheckResult with OK if supported architecture, FAIL otherwise.
    """
    cmd_result = run_command(["uname", "-m"])

    # Handle execution failure
    if cmd_result.error:
        return CheckResult(
            check_id="CHECK_OS_02",
            title="CPU Architecture",
            category="OS",
            description="Verify supported CPU architecture.",
            evidence_command="uname -m",
            expected_behavior=f"Architecture in {SUPPORTED_ARCHITECTURES}",
            status=CheckStatus.FAIL,
            evidence=cmd_result.error,
            message=f"Failed to determine CPU architecture: {cmd_result.error}",
            classification_impact=ClassificationImpact.BLOCKED,
        )

    architecture = cmd_result.stdout_stripped

    # Validate architecture
    if architecture not in SUPPORTED_ARCHITECTURES:
        return CheckResult(
            check_id="CHECK_OS_02",
            title="CPU Architecture",
            category="OS",
            description="Verify supported CPU architecture.",
            evidence_command="uname -m",
            expected_behavior=f"Architecture in {SUPPORTED_ARCHITECTURES}",
            status=CheckStatus.FAIL,
            evidence=architecture,
            message=f"Unsupported CPU architecture: {architecture}",
            classification_impact=ClassificationImpact.BLOCKED,
        )

    return CheckResult(
        check_id="CHECK_OS_02",
        title="CPU Architecture",
        category="OS",
        description="Verify supported CPU architecture.",
        evidence_command="uname -m",
        expected_behavior=f"Architecture in {SUPPORTED_ARCHITECTURES}",
        status=CheckStatus.OK,
        evidence=architecture,
        message=f"Supported CPU architecture: {architecture}",
        classification_impact=ClassificationImpact.NONE,
    )

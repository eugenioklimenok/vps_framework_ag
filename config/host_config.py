"""
HOST Configuration — Explicit policy values and thresholds for the HOST module.

All configurable values used by HOST audit, init, and harden are declared here.
This avoids hidden defaults, hardcoded heuristics, and scattered magic numbers.

Governed by: AUDIT_VPS_SPEC.md §8, HOST_BASELINE_CONTRACT.md §6,
             PYTHON_IMPLEMENTATION_BASELINE.md §7.

Rules:
    - No hidden defaults that alter behavior invisibly
    - All thresholds must be documented
    - No hardcoded operator identity or environment assumptions
"""

# =============================================================================
# OS Support Policy
# =============================================================================

# Supported operating system identifiers (from /etc/os-release ID field)
SUPPORTED_OS_IDS: list[str] = ["ubuntu"]

# Supported Ubuntu version identifiers (from /etc/os-release VERSION_ID field)
SUPPORTED_UBUNTU_VERSIONS: list[str] = ["22.04", "24.04"]

# Supported CPU architectures (from uname -m)
SUPPORTED_ARCHITECTURES: list[str] = ["x86_64", "aarch64"]


# =============================================================================
# Filesystem Permissions Policy
# =============================================================================

# Expected permission mode for operator home directory
EXPECTED_HOME_PERMISSION: str = "755"

# Expected permission mode for operator .ssh directory
EXPECTED_SSH_DIR_PERMISSION: str = "700"

# Expected permission mode for operator authorized_keys file
EXPECTED_AUTHORIZED_KEYS_PERMISSION: str = "600"


# =============================================================================
# Disk Space Thresholds
# =============================================================================

# Minimum free space on root filesystem (in MB) below which reconciliation is BLOCKED
MIN_FREE_SPACE_MB: int = 500

# Free space threshold (in MB) below which a WARNING is raised
LOW_FREE_SPACE_MB: int = 1000


# =============================================================================
# SSH Policy Constants
# =============================================================================

# SSH configuration keys to inspect from effective config (sshd -T)
SSH_CONFIG_KEYS: list[str] = [
    "pubkeyauthentication",
    "passwordauthentication",
    "permitrootlogin",
    "kbdinteractiveauthentication",
]

# Required SSH value: public key authentication must be enabled
REQUIRED_PUBKEY_AUTH: str = "yes"


# =============================================================================
# Operator Home Path Policy
# =============================================================================

def get_expected_operator_home(operator_user: str) -> str:
    """Return the expected home directory path for the operator user.

    Args:
        operator_user: The operator username.

    Returns:
        The expected home path (e.g., "/home/deploy").
    """
    return f"/home/{operator_user}"


# =============================================================================
# Default Shell Policy
# =============================================================================

# Default shell assigned to newly created operator users
DEFAULT_OPERATOR_SHELL: str = "/bin/bash"

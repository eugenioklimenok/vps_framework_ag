"""
Tests for the HOST configuration module.
Governed by: HOST_BASELINE_CONTRACT.md §6 and PYTHON_IMPLEMENTATION_BASELINE.md §7.
"""

from config.host_config import (
    DEFAULT_OPERATOR_SHELL,
    EXPECTED_AUTHORIZED_KEYS_PERMISSION,
    EXPECTED_HOME_PERMISSION,
    EXPECTED_SSH_DIR_PERMISSION,
    LOW_FREE_SPACE_MB,
    MIN_FREE_SPACE_MB,
    REQUIRED_PUBKEY_AUTH,
    SSH_CONFIG_KEYS,
    SUPPORTED_ARCHITECTURES,
    SUPPORTED_OS_IDS,
    SUPPORTED_UBUNTU_VERSIONS,
    get_expected_operator_home,
)


def test_supported_os_policy():
    """Verify supported OS configurations."""
    assert "ubuntu" in SUPPORTED_OS_IDS
    assert "24.04" in SUPPORTED_UBUNTU_VERSIONS
    assert "22.04" in SUPPORTED_UBUNTU_VERSIONS
    assert "x86_64" in SUPPORTED_ARCHITECTURES
    assert "aarch64" in SUPPORTED_ARCHITECTURES


def test_filesystem_permissions_policy():
    """Verify expected filesystem permissions."""
    assert EXPECTED_HOME_PERMISSION == "755"
    assert EXPECTED_SSH_DIR_PERMISSION == "700"
    assert EXPECTED_AUTHORIZED_KEYS_PERMISSION == "600"


def test_disk_space_policy():
    """Verify disk space thresholds."""
    assert MIN_FREE_SPACE_MB == 500
    assert LOW_FREE_SPACE_MB == 1000
    assert MIN_FREE_SPACE_MB < LOW_FREE_SPACE_MB


def test_ssh_policy():
    """Verify SSH configuration policy."""
    assert "pubkeyauthentication" in SSH_CONFIG_KEYS
    assert REQUIRED_PUBKEY_AUTH == "yes"


def test_operator_home_generation():
    """Verify dynamic generation of operator home path."""
    assert get_expected_operator_home("deploy") == "/home/deploy"
    assert get_expected_operator_home("admin") == "/home/admin"


def test_default_shell():
    """Verify default shell for new users."""
    assert DEFAULT_OPERATOR_SHELL == "/bin/bash"

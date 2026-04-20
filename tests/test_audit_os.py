"""
Tests for the OS audit checks using mocked subprocess execution.
"""

from unittest.mock import patch

from models.command_result import CommandResult
from models.enums import CheckStatus, ClassificationImpact
from modules.host.audit.checks_os import run_check_os_architecture, run_check_os_supported


@patch("modules.host.audit.checks_os.run_command")
def test_check_os_supported_ubuntu_2404(mock_run_command):
    """Test CHECK_OS_01 with a valid Ubuntu 24.04 response."""
    # Mock cat /etc/os-release success
    mock_run_command.return_value = CommandResult(
        stdout='ID=ubuntu\nVERSION_ID="24.04"\nPRETTY_NAME="Ubuntu 24.04.1 LTS"\n',
        stderr="", returncode=0, timed_out=False, error="",
    )

    result = run_check_os_supported()
    
    # Assert call
    mock_run_command.assert_called_once_with(["cat", "/etc/os-release"])
    
    # Assert result
    assert result.status == CheckStatus.OK
    assert result.classification_impact == ClassificationImpact.NONE
    assert "Ubuntu 24.04.1 LTS" in result.message


@patch("modules.host.audit.checks_os.run_command")
def test_check_os_supported_unsupported_os(mock_run_command):
    """Test CHECK_OS_01 with an unsupported OS (Debian)."""
    mock_run_command.return_value = CommandResult(
        stdout='ID=debian\nVERSION_ID="12"\nPRETTY_NAME="Debian 12"\n',
        stderr="", returncode=0, timed_out=False, error="",
    )

    result = run_check_os_supported()
    
    assert result.status == CheckStatus.FAIL
    assert result.classification_impact == ClassificationImpact.BLOCKED
    assert "Unsupported operating system" in result.message


@patch("modules.host.audit.checks_os.run_command")
def test_check_os_supported_missing_file(mock_run_command):
    """Test CHECK_OS_01 when /etc/os-release is missing."""
    mock_run_command.return_value = CommandResult(
        stdout="", stderr="cat: /etc/os-release: No such file or directory", 
        returncode=1, timed_out=False, error="",
    )

    result = run_check_os_supported()
    
    assert result.status == CheckStatus.FAIL
    assert result.classification_impact == ClassificationImpact.BLOCKED
    assert "not found or not readable" in result.message


@patch("modules.host.audit.checks_os.run_command")
def test_check_os_architecture_supported(mock_run_command):
    """Test CHECK_OS_02 with x86_64 architecture."""
    mock_run_command.return_value = CommandResult(
        stdout="x86_64\n", stderr="", returncode=0, timed_out=False, error="",
    )

    result = run_check_os_architecture()
    
    mock_run_command.assert_called_once_with(["uname", "-m"])
    assert result.status == CheckStatus.OK
    assert result.classification_impact == ClassificationImpact.NONE


@patch("modules.host.audit.checks_os.run_command")
def test_check_os_architecture_unsupported(mock_run_command):
    """Test CHECK_OS_02 with an unsupported architecture (i686)."""
    mock_run_command.return_value = CommandResult(
        stdout="i686\n", stderr="", returncode=0, timed_out=False, error="",
    )

    result = run_check_os_architecture()
    
    assert result.status == CheckStatus.FAIL
    assert result.classification_impact == ClassificationImpact.BLOCKED

"""
Subprocess Wrapper — Centralized system command execution.

All system interaction MUST go through this module.
Governed by: AUDIT_VPS_SPEC.md §11 and PYTHON_IMPLEMENTATION_BASELINE.md §5.

Responsibilities:
    - Receive command as explicit argument list
    - Execute via subprocess.run()
    - Capture stdout, stderr, and return code
    - Handle timeout
    - Handle execution errors (binary not found, permission denied, etc.)
    - Return structured CommandResult
    - Centralize all system interaction for clean mocking in tests

Rules:
    - No shell=True unless strictly justified
    - No silent failures
    - No direct console output from this layer
"""

import logging
import subprocess

from models.command_result import CommandResult

logger = logging.getLogger(__name__)

# Default timeout in seconds for subprocess execution
DEFAULT_TIMEOUT_SECONDS = 30


def run_command(
    cmd: list[str],
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> CommandResult:
    """Execute a system command and return a structured result.

    Args:
        cmd:     Command as explicit argument list (e.g., ["uname", "-m"]).
        timeout: Maximum execution time in seconds before the command is killed.

    Returns:
        CommandResult with stdout, stderr, returncode, timeout flag, and error message.

    This function NEVER raises exceptions. All error conditions are captured
    in the returned CommandResult for deterministic handling by callers.
    """
    cmd_str = " ".join(cmd)
    logger.debug("Executing command: %s (timeout=%ds)", cmd_str, timeout)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
        )

        logger.debug(
            "Command completed: returncode=%d, stdout_len=%d, stderr_len=%d",
            result.returncode,
            len(result.stdout),
            len(result.stderr),
        )

        return CommandResult(
            stdout=result.stdout,
            stderr=result.stderr,
            returncode=result.returncode,
            timed_out=False,
            error="",
        )

    except subprocess.TimeoutExpired:
        logger.warning("Command timed out after %ds: %s", timeout, cmd_str)
        return CommandResult(
            stdout="",
            stderr="",
            returncode=-1,
            timed_out=True,
            error=f"Command timed out after {timeout}s: {cmd_str}",
        )

    except FileNotFoundError:
        logger.error("Command binary not found: %s", cmd[0] if cmd else "<empty>")
        return CommandResult(
            stdout="",
            stderr="",
            returncode=-1,
            timed_out=False,
            error=f"Command binary not found: {cmd[0] if cmd else '<empty>'}",
        )

    except PermissionError:
        logger.error("Permission denied executing: %s", cmd_str)
        return CommandResult(
            stdout="",
            stderr="",
            returncode=-1,
            timed_out=False,
            error=f"Permission denied executing: {cmd_str}",
        )

    except OSError as e:
        logger.error("OS error executing command '%s': %s", cmd_str, e)
        return CommandResult(
            stdout="",
            stderr="",
            returncode=-1,
            timed_out=False,
            error=f"OS error executing command '{cmd_str}': {e}",
        )

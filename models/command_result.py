"""
CommandResult — Structured result object for subprocess execution.

Wraps the outcome of every system command executed through the subprocess wrapper.
Governed by: AUDIT_VPS_SPEC.md §11 and PYTHON_IMPLEMENTATION_BASELINE.md §5.

This ensures:
    - stdout, stderr, and return code are always captured
    - timeout conditions are explicit
    - execution errors are surfaced, not hidden
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CommandResult:
    """Immutable result of a subprocess execution.

    Attributes:
        stdout:     Standard output captured from the command.
        stderr:     Standard error captured from the command.
        returncode: Exit code of the process (-1 if execution failed).
        timed_out:  Whether the command was terminated due to timeout.
        error:      Error message if execution itself failed (e.g., binary not found).
                    Empty string if execution succeeded (regardless of exit code).
    """

    stdout: str
    stderr: str
    returncode: int
    timed_out: bool
    error: str

    @property
    def success(self) -> bool:
        """Whether the command completed with exit code 0 and no execution error."""
        return self.returncode == 0 and not self.timed_out and not self.error

    @property
    def stdout_stripped(self) -> str:
        """Stdout with leading/trailing whitespace removed for parsing."""
        return self.stdout.strip()

    @property
    def stderr_stripped(self) -> str:
        """Stderr with leading/trailing whitespace removed for parsing."""
        return self.stderr.strip()

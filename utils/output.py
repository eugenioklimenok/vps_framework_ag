"""
Output Formatting — Human-readable output rendering for audit results.

Governed by: AUDIT_VPS_SPEC.md §12.

Requirements:
    - Grouped by category (OS, USER, SSH, FILESYSTEM, SYSTEM)
    - Each line: status, check_id, short message
    - Final classification clearly displayed
    - Summary counters (total, ok, warn, fail)

This module renders structured data into formatted console output.
It MUST NOT contain business logic.
"""

from models.check_result import CheckResult
from models.enums import CheckStatus, HostClassification


# Status display symbols
_STATUS_SYMBOLS: dict[CheckStatus, str] = {
    CheckStatus.OK: "[OK]",
    CheckStatus.WARN: "[!]",
    CheckStatus.FAIL: "[X]",
}

# Classification display colors (ANSI escape codes)
_CLASSIFICATION_STYLES: dict[HostClassification, str] = {
    HostClassification.CLEAN: "\033[92m",       # bright green
    HostClassification.COMPATIBLE: "\033[96m",   # bright cyan
    HostClassification.SANEABLE: "\033[93m",     # bright yellow
    HostClassification.BLOCKED: "\033[91m",      # bright red
}

_STATUS_STYLES: dict[CheckStatus, str] = {
    CheckStatus.OK: "\033[92m",     # bright green
    CheckStatus.WARN: "\033[93m",   # bright yellow
    CheckStatus.FAIL: "\033[91m",   # bright red
}

_RESET = "\033[0m"
_BOLD = "\033[1m"
_DIM = "\033[2m"


def format_check_line(result: CheckResult) -> str:
    """Format a single check result as a human-readable line.

    Format: [STATUS_SYMBOL] CHECK_ID — message

    Args:
        result: A CheckResult to format.

    Returns:
        Formatted string for console output.
    """
    symbol = _STATUS_SYMBOLS.get(result.status, "?")
    style = _STATUS_STYLES.get(result.status, "")
    return f"  {style}{symbol}{_RESET} {result.check_id} — {result.message}"


def format_audit_report(
    results: list[CheckResult],
    classification: HostClassification,
    total: int,
    ok_count: int,
    warn_count: int,
    fail_count: int,
) -> str:
    """Format a complete audit report as human-readable grouped output.

    Groups checks by category, displays each result, and shows
    the final classification with summary counters.

    Args:
        results: Ordered list of CheckResult objects.
        classification: Final host classification.
        total: Total checks executed.
        ok_count: Number of OK results.
        warn_count: Number of WARN results.
        fail_count: Number of FAIL results.

    Returns:
        Multi-line formatted string for console output.
    """
    lines: list[str] = []

    # Header
    lines.append("")
    lines.append(f"{_BOLD}==================================================={_RESET}")
    lines.append(f"{_BOLD}  VPS HOST AUDIT REPORT{_RESET}")
    lines.append(f"{_BOLD}==================================================={_RESET}")

    # Group results by category (preserving order)
    categories: dict[str, list[CheckResult]] = {}
    for result in results:
        if result.category not in categories:
            categories[result.category] = []
        categories[result.category].append(result)

    # Render each category
    for category, checks in categories.items():
        lines.append("")
        lines.append(f"{_BOLD}  [{category}]{_RESET}")
        lines.append(f"  {'-' * 47}")
        for check in checks:
            lines.append(format_check_line(check))

    # Classification
    cls_style = _CLASSIFICATION_STYLES.get(classification, "")
    lines.append("")
    lines.append(f"{_BOLD}==================================================={_RESET}")
    lines.append(f"  {_BOLD}CLASSIFICATION:{_RESET} {cls_style}{_BOLD}{classification.value}{_RESET}")
    lines.append(
        f"  {_DIM}Total: {total} | "
        f"{_STATUS_STYLES[CheckStatus.OK]}OK: {ok_count}{_RESET}{_DIM} | "
        f"{_STATUS_STYLES[CheckStatus.WARN]}WARN: {warn_count}{_RESET}{_DIM} | "
        f"{_STATUS_STYLES[CheckStatus.FAIL]}FAIL: {fail_count}{_RESET}"
    )
    lines.append(f"{_BOLD}==================================================={_RESET}")
    lines.append("")

    return "\n".join(lines)

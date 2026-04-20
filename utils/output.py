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
from models.deploy_result import DeployResult
from models.enums import AuditClassification, BackupResultState, CheckStatus, DeploymentClassification, HostClassification, TargetClassification
from models.project_result import ScaffoldResult


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

_TARGET_CLASSIFICATION_STYLES: dict[TargetClassification, str] = {
    TargetClassification.CLEAN: "\033[92m",       # bright green
    TargetClassification.COMPATIBLE: "\033[96m",   # bright cyan
    TargetClassification.SANEABLE: "\033[93m",     # bright yellow
    TargetClassification.BLOCKED: "\033[91m",      # bright red
}

_DEPLOYMENT_CLASSIFICATION_STYLES: dict[DeploymentClassification, str] = {
    DeploymentClassification.READY: "\033[92m",         # bright green
    DeploymentClassification.REDEPLOYABLE: "\033[96m",  # bright cyan
    DeploymentClassification.BLOCKED: "\033[91m",       # bright red
}

_AUDIT_CLASSIFICATION_STYLES: dict[AuditClassification, str] = {
    AuditClassification.HEALTHY: "\033[92m",    # bright green
    AuditClassification.DEGRADED: "\033[93m",   # bright yellow
    AuditClassification.BLOCKED: "\033[91m",    # bright red
}

_BACKUP_STATE_STYLES: dict[BackupResultState, str] = {
    BackupResultState.CREATED: "\033[92m",  # bright green
    BackupResultState.BLOCKED: "\033[91m",  # bright red
    BackupResultState.FAILED: "\033[91m",   # bright red
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


def format_scaffold_report(result: ScaffoldResult, slug: str, target_path: str) -> str:
    """Format a complete scaffold report as human-readable output.

    Args:
        result: The ScaffoldResult from the operation.
        slug: The project slug.
        target_path: The project target path.

    Returns:
        Formatted string for console output.
    """
    lines: list[str] = []

    lines.append("")
    lines.append(f"{_BOLD}==================================================={_RESET}")
    lines.append(f"{_BOLD}  PROJECT SCAFFOLD REPORT{_RESET}")
    lines.append(f"{_BOLD}==================================================={_RESET}")
    lines.append(f"  {_DIM}Project Slug:{_RESET} {slug}")
    lines.append(f"  {_DIM}Target Path:{_RESET}  {target_path}")
    
    cls_style = _TARGET_CLASSIFICATION_STYLES.get(result.classification, "")
    lines.append(f"  {_DIM}Target Class:{_RESET} {cls_style}{_BOLD}{result.classification.value}{_RESET}")
    
    lines.append("")

    if result.classification == TargetClassification.BLOCKED:
        lines.append(f"  {_STATUS_STYLES[CheckStatus.FAIL]}[BLOCKED]{_RESET} {result.blocked_reason}")
    else:
        # Actions taken
        lines.append(f"{_BOLD}  [Actions Taken]{_RESET}")
        lines.append(f"  {'-' * 47}")
        for action in result.actions_taken:
            lines.append(f"  - {action.value}")
        
        # Created/Reused items
        lines.append("")
        lines.append(f"{_BOLD}  [Artifacts]{_RESET}")
        lines.append(f"  {'-' * 47}")
        lines.append(f"  Created: {len(result.created_paths)}")
        lines.append(f"  Reused:  {len(result.reused_paths)}")

        # Validation
        lines.append("")
        val_status = "PASS" if result.validation_passed else "FAIL"
        val_color = _STATUS_STYLES[CheckStatus.OK] if result.validation_passed else _STATUS_STYLES[CheckStatus.FAIL]
        lines.append(f"  {_BOLD}Validation:{_RESET} {val_color}{val_status}{_RESET}")

    lines.append(f"{_BOLD}==================================================={_RESET}")
    lines.append("")

    return "\n".join(lines)


def format_deploy_report(result: DeployResult, target_path: str, env_file: str) -> str:
    """Format a complete deploy report as human-readable output.

    Args:
        result: The DeployResult from the operation.
        target_path: The project target path.
        env_file: The path to the environment file.

    Returns:
        Formatted string for console output.
    """
    lines: list[str] = []

    lines.append("")
    lines.append(f"{_BOLD}==================================================={_RESET}")
    lines.append(f"{_BOLD}  PROJECT DEPLOY REPORT{_RESET}")
    lines.append(f"{_BOLD}==================================================={_RESET}")
    lines.append(f"  {_DIM}Project Slug:{_RESET} {result.project_slug or 'UNKNOWN'}")
    lines.append(f"  {_DIM}Target Path:{_RESET}  {target_path}")
    lines.append(f"  {_DIM}Env File:{_RESET}     {env_file}")
    
    cls_style = _DEPLOYMENT_CLASSIFICATION_STYLES.get(result.classification, "")
    lines.append(f"  {_DIM}Deploy Class:{_RESET} {cls_style}{_BOLD}{result.classification.value}{_RESET}")
    
    lines.append("")

    if result.classification == DeploymentClassification.BLOCKED:
        lines.append(f"  {_STATUS_STYLES[CheckStatus.FAIL]}[BLOCKED]{_RESET} {result.blocked_reason}")
    else:
        # Actions taken
        lines.append(f"{_BOLD}  [Execution Phases]{_RESET}")
        lines.append(f"  {'-' * 47}")
        
        cfg_status = "PASS" if result.config_validated else "FAIL"
        cfg_color = _STATUS_STYLES[CheckStatus.OK] if result.config_validated else _STATUS_STYLES[CheckStatus.FAIL]
        lines.append(f"  {_DIM}Config Validation:{_RESET} {cfg_color}{cfg_status}{_RESET}")
        
        if result.config_validated:
            bld_status = "PASS" if result.build_succeeded else "FAIL"
            bld_color = _STATUS_STYLES[CheckStatus.OK] if result.build_succeeded else _STATUS_STYLES[CheckStatus.FAIL]
            lines.append(f"  {_DIM}Stack Build:{_RESET}       {bld_color}{bld_status}{_RESET}")
            
        if result.build_succeeded:
            up_status = "PASS" if result.startup_succeeded else "FAIL"
            up_color = _STATUS_STYLES[CheckStatus.OK] if result.startup_succeeded else _STATUS_STYLES[CheckStatus.FAIL]
            lines.append(f"  {_DIM}Stack Startup:{_RESET}     {up_color}{up_status}{_RESET}")
            
        if result.startup_succeeded:
            smk_status = "PASS" if result.smoke_passed else "FAIL"
            smk_color = _STATUS_STYLES[CheckStatus.OK] if result.smoke_passed else _STATUS_STYLES[CheckStatus.FAIL]
            lines.append(f"  {_DIM}Smoke Tests:{_RESET}       {smk_color}{smk_status}{_RESET}")

        # Validation
        lines.append("")
        val_status = "PASS" if result.validation_passed else "FAIL"
        val_color = _STATUS_STYLES[CheckStatus.OK] if result.validation_passed else _STATUS_STYLES[CheckStatus.FAIL]
        lines.append(f"  {_BOLD}Validation:{_RESET} {val_color}{val_status}{_RESET}")
        
        if not result.validation_passed and result.blocked_reason:
            lines.append(f"  {_STATUS_STYLES[CheckStatus.FAIL]}Error:{_RESET} {result.blocked_reason}")

    lines.append(f"{_BOLD}==================================================={_RESET}")
    lines.append("")

    return "\n".join(lines)


def format_audit_project_report(result: "models.operate_result.ProjectAuditResult", target_path: str) -> str:
    """Format a complete project audit report as human-readable output."""
    lines: list[str] = []

    lines.append("")
    lines.append(f"{_BOLD}==================================================={_RESET}")
    lines.append(f"{_BOLD}  PROJECT AUDIT REPORT{_RESET}")
    lines.append(f"{_BOLD}==================================================={_RESET}")
    lines.append(f"  {_DIM}Project Slug:{_RESET} {result.project_slug or 'UNKNOWN'}")
    lines.append(f"  {_DIM}Target Path:{_RESET}  {target_path}")
    
    cls_style = _AUDIT_CLASSIFICATION_STYLES.get(result.classification, "")
    lines.append(f"  {_DIM}Audit Class:{_RESET}  {cls_style}{_BOLD}{result.classification.value}{_RESET}")
    
    lines.append("")

    if result.classification == AuditClassification.BLOCKED:
        lines.append(f"  {_STATUS_STYLES[CheckStatus.FAIL]}[BLOCKED]{_RESET} {result.blocked_reason}")
    
    if result.checks:
        lines.append(f"{_BOLD}  [Audit Checks]{_RESET}")
        lines.append(f"  {'-' * 47}")
        for check in result.checks:
            lines.append(format_check_line(check))

    lines.append(f"{_BOLD}==================================================={_RESET}")
    lines.append("")

    return "\n".join(lines)


def format_backup_report(result: "models.operate_result.BackupResult", target_path: str) -> str:
    """Format a backup report as human-readable output."""
    lines: list[str] = []

    lines.append("")
    lines.append(f"{_BOLD}==================================================={_RESET}")
    lines.append(f"{_BOLD}  PROJECT BACKUP REPORT{_RESET}")
    lines.append(f"{_BOLD}==================================================={_RESET}")
    lines.append(f"  {_DIM}Project Slug:{_RESET} {result.project_slug or 'UNKNOWN'}")
    lines.append(f"  {_DIM}Target Path:{_RESET}  {target_path}")
    
    cls_style = _BACKUP_STATE_STYLES.get(result.result_state, "")
    lines.append(f"  {_DIM}Result State:{_RESET} {cls_style}{_BOLD}{result.result_state.value}{_RESET}")
    
    lines.append("")

    if result.result_state in (BackupResultState.BLOCKED, BackupResultState.FAILED):
        lines.append(f"  {_STATUS_STYLES[CheckStatus.FAIL]}[ERROR]{_RESET} {result.blocked_reason}")
    else:
        lines.append(f"{_BOLD}  [Artifacts]{_RESET}")
        lines.append(f"  {'-' * 47}")
        lines.append(f"  Archive:  {result.artifact_path}")
        lines.append(f"  Checksum: {result.checksum_path}")
        
        # Validation
        lines.append("")
        val_status = "PASS" if result.artifact_validated else "FAIL"
        val_color = _STATUS_STYLES[CheckStatus.OK] if result.artifact_validated else _STATUS_STYLES[CheckStatus.FAIL]
        lines.append(f"  {_BOLD}Validation:{_RESET} {val_color}{val_status}{_RESET}")

    lines.append(f"{_BOLD}==================================================={_RESET}")
    lines.append("")

    return "\n".join(lines)

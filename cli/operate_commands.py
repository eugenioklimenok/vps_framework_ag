"""
Operate CLI commands for the VPS framework.
"""

import typer
from typing import Optional

from models.enums import AuditClassification, BackupResultState
from modules.operate.audit.runner import run_audit_project
from modules.operate.backup.runner import run_backup_project
from utils.output import format_audit_project_report, format_backup_report

app = typer.Typer(
    help="OPERATE domain: Maintain, audit, and backup projects.",
    no_args_is_help=True,
)


@app.command("audit-project")
def audit_project(
    path: str = typer.Option(
        ...,
        "--path",
        help="Target directory path of the project scaffold.",
    ),
    env_file: str = typer.Option(
        ...,
        "--env-file",
        help="Explicit path to the environment file to use for audit.",
    ),
    endpoint_url: Optional[str] = typer.Option(
        None,
        "--endpoint-url",
        help="Optional HTTP endpoint to validate health.",
    ),
):
    """
    Run diagnostic checks on a running project stack.
    """
    result = run_audit_project(path=path, env_file_path=env_file, endpoint_url=endpoint_url)

    # Print the report
    report = format_audit_project_report(result, path)
    typer.echo(report)

    if result.classification == AuditClassification.BLOCKED:
        raise typer.Exit(code=2)
    elif result.classification == AuditClassification.DEGRADED:
        raise typer.Exit(code=1)
    
    # Success (HEALTHY)
    raise typer.Exit(code=0)


@app.command("backup-project")
def backup_project(
    path: str = typer.Option(
        ...,
        "--path",
        help="Target directory path of the project scaffold.",
    ),
    output_dir: str = typer.Option(
        ...,
        "--output-dir",
        help="Explicit directory where backup artifacts will be created.",
    ),
    include_env: bool = typer.Option(
        False,
        "--include-env",
        help="If set, includes the .env file in the backup (insecure).",
    ),
):
    """
    Create a deterministic backup artifact of the project.
    """
    result = run_backup_project(path=path, output_dir=output_dir, include_env=include_env)

    # Print the report
    report = format_backup_report(result, path)
    typer.echo(report)

    if result.result_state in (BackupResultState.BLOCKED, BackupResultState.FAILED):
        raise typer.Exit(code=2)
    
    # Success
    raise typer.Exit(code=0)

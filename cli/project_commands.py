"""
Project CLI commands for the VPS framework.
"""

import typer

from models.enums import TargetClassification
from modules.project.runner import run_new_project
from utils.output import format_scaffold_report

app = typer.Typer(
    help="PROJECT domain: Generate and manage project scaffolds.",
    no_args_is_help=True,
)


@app.command("new-project")
def new_project(
    name: str = typer.Option(
        ...,
        "--name",
        help="Project slug (lowercase, alphanumeric, hyphens only).",
    ),
    path: str = typer.Option(
        ...,
        "--path",
        help="Target directory path for the project scaffold.",
    ),
):
    """
    Generate a new deterministic project scaffold.

    Validates inputs, inspects the target directory, classifies it,
    and safely creates the project baseline without destroying existing data.
    """
    result = run_new_project(slug=name, path=path)

    # Print the report
    report = format_scaffold_report(result, name, path)
    typer.echo(report)

    # Determine exit code based on the strict CLI contract
    if result.classification == TargetClassification.BLOCKED or not result.validation_passed:
        raise typer.Exit(code=2)
    
    # Success
    raise typer.Exit(code=0)

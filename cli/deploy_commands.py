"""
Deploy CLI commands for the VPS framework.
"""

import typer

from models.enums import DeploymentClassification
from modules.deploy.project.runner import run_deploy_project
from utils.output import format_deploy_report

app = typer.Typer(
    help="DEPLOY domain: Turn project scaffolds into running stacks.",
    no_args_is_help=True,
)


@app.command("deploy-project")
def deploy_project(
    path: str = typer.Option(
        ...,
        "--path",
        help="Target directory path of the project scaffold.",
    ),
    env_file: str = typer.Option(
        ...,
        "--env-file",
        help="Explicit path to the environment file to use for deployment.",
    ),
):
    """
    Deploy or re-deploy a project stack.

    Validates the scaffold, runtime prerequisites, deploy configuration,
    executes build and startup, and runs smoke tests.
    """
    result = run_deploy_project(path=path, env_file_path=env_file)

    # Print the report
    report = format_deploy_report(result, path, env_file)
    typer.echo(report)

    # Determine exit code based on the strict CLI contract
    if result.classification == DeploymentClassification.BLOCKED or not result.validation_passed:
        raise typer.Exit(code=2)
    
    # Success
    raise typer.Exit(code=0)

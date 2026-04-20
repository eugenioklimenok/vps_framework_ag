"""
VPS Framework — CLI Root

This is the main entry point for the VPS framework CLI.
All domain commands are registered here through Typer subcommand groups.

Usage:
    python main.py --help
    python main.py host --help
"""

import typer

from cli.deploy_commands import app as deploy_app
from cli.host_commands import host_app
from cli.operate_commands import app as operate_app
from cli.project_commands import app as project_app

app = typer.Typer(
    name="vps",
    help="VPS Framework — Modular CLI for VPS preparation, validation and management.",
    no_args_is_help=True,
)

# Register HOST module commands
app.add_typer(host_app, name="host", help="HOST module — Audit, initialize, and harden the VPS.")

# Register PROJECT module commands
app.add_typer(project_app, name="project", help="PROJECT module — Generate and manage project scaffolds.")

# Register DEPLOY module commands
app.add_typer(deploy_app, name="deploy", help="DEPLOY module — Turn project scaffolds into running stacks.")

# Register OPERATE module commands
app.add_typer(operate_app, name="operate", help="OPERATE module — Maintain, audit, and backup projects.")


if __name__ == "__main__":
    app()

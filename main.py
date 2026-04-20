"""
VPS Framework — CLI Root

This is the main entry point for the VPS framework CLI.
All domain commands are registered here through Typer subcommand groups.

Usage:
    python main.py --help
    python main.py host --help
"""

import typer

from cli.host_commands import host_app

app = typer.Typer(
    name="vps",
    help="VPS Framework — Modular CLI for VPS preparation, validation and management.",
    no_args_is_help=True,
)

# Register HOST module commands
app.add_typer(host_app, name="host", help="HOST module — Audit, initialize, and harden the VPS.")


if __name__ == "__main__":
    app()

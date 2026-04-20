"""
HOST CLI Commands — Typer entrypoints for the HOST module.

Exposes:
    - audit-vps: Read-only host diagnostic
    - init-vps: Controlled host reconciliation
    - harden-vps: Post-initialization security hardening

Each command delegates to its respective runner.
CLI code is a thin entry layer — it MUST NOT absorb business logic.
"""

import typer

host_app = typer.Typer(
    name="host",
    help="HOST module commands: audit, initialize, and harden the VPS baseline.",
    no_args_is_help=True,
)


@host_app.command("audit-vps", help="Read-only diagnostic audit of the host VPS.")
def audit_vps(
    operator_user: str = typer.Option(
        ...,
        "--operator-user",
        "-u",
        help="Operator user identity to evaluate.",
    ),
) -> None:
    """Run a read-only audit of the host and classify its state."""
    # TODO: Phase 5 — delegate to audit runner
    typer.echo("[audit-vps] Not yet implemented. Pending Phase 5.")
    raise typer.Exit(code=3)


@host_app.command("init-vps", help="Controlled reconciliation of the host baseline.")
def init_vps(
    operator_user: str = typer.Option(
        ...,
        "--operator-user",
        "-u",
        help="Operator user identity to reconcile.",
    ),
    public_key: str = typer.Option(
        ...,
        "--public-key",
        "-k",
        help="Path to the public key file or the public key string.",
    ),
) -> None:
    """Initialize or normalize the host baseline through controlled reconciliation."""
    # TODO: Phase 6 — delegate to init runner
    typer.echo("[init-vps] Not yet implemented. Pending Phase 6.")
    raise typer.Exit(code=3)


@host_app.command("harden-vps", help="Post-initialization security hardening.")
def harden_vps() -> None:
    """Apply post-initialization security hardening to the host."""
    # Intentionally deferred — not part of the current implementation slice
    typer.echo("[harden-vps] Not yet implemented. Deferred to a future slice.")
    raise typer.Exit(code=3)

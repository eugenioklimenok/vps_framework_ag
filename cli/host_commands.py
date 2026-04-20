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

from models.enums import CheckStatus, HostClassification, ReconcileAction
from modules.host.audit.runner import run_audit
from modules.host.init.runner import run_init
from utils.output import format_audit_report

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
    try:
        report = run_audit(operator_user)
    except Exception as e:
        typer.secho(f"\n[FATAL] Audit execution failed: {e}", fg=typer.colors.RED, bold=True)
        raise typer.Exit(code=3)

    output = format_audit_report(
        results=report.results,
        classification=report.classification,
        total=report.total,
        ok_count=report.ok_count,
        warn_count=report.warn_count,
        fail_count=report.fail_count,
    )
    typer.echo(output)

    # Deterministic exit codes (AUDIT_VPS_SPEC.md §13)
    if report.classification == HostClassification.BLOCKED:
        raise typer.Exit(code=2)
    if report.warn_count > 0:
        raise typer.Exit(code=1)
    
    raise typer.Exit(code=0)


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
    typer.secho(f"\n[INIT-VPS] Starting controlled reconciliation for '{operator_user}'", bold=True)
    
    try:
        result = run_init(operator_user, public_key)
    except Exception as e:
        typer.secho(f"\n[FATAL] Init execution failed: {e}", fg=typer.colors.RED, bold=True)
        raise typer.Exit(code=3)

    if result.audit_report:
        typer.echo("\n--- Audit Gate ---")
        typer.echo(f"Classification: {result.audit_report.classification.value}")
    
    if result.reconcile_results:
        typer.echo("\n--- Reconciliation Steps ---")
        for rr in result.reconcile_results:
            color = typer.colors.GREEN if rr.success else typer.colors.RED
            typer.secho(f"[{rr.action.value}] {rr.step_id} — {rr.message}", fg=color)

    if result.validation_report:
        typer.echo("\n--- Post-Action Validation ---")
        for vr in result.validation_report.results:
            color = typer.colors.GREEN if vr.passed else typer.colors.RED
            symbol = "[OK]" if vr.passed else "[X]"
            typer.secho(f"{symbol} {vr.check_id} — {vr.message}", fg=color)

    typer.echo("\n" + "=" * 50)
    
    if result.aborted:
        typer.secho(f"ABORTED: {result.abort_reason}", fg=typer.colors.RED, bold=True)
        raise typer.Exit(code=2)
        
    if not result.success:
        typer.secho("FAILED: Post-action validation did not pass.", fg=typer.colors.RED, bold=True)
        raise typer.Exit(code=2)

    typer.secho("SUCCESS: Host baseline initialized and validated.", fg=typer.colors.GREEN, bold=True)
    raise typer.Exit(code=0)


@host_app.command("harden-vps", help="Post-initialization security hardening.")
def harden_vps() -> None:
    """Apply post-initialization security hardening to the host."""
    # Intentionally deferred — not part of the current implementation slice
    typer.echo("[harden-vps] Not yet implemented. Deferred to a future slice.")
    raise typer.Exit(code=3)

"""
Docker Validation — Verifies the Docker runtime state after reconciliation.

Governed by: HOST_SLICE_02_DOCKER_COMPOSE_ADDENDUM.md §15.
"""

import logging

from models.check_result import CheckResult
from models.enums import CheckStatus
from models.reconcile_result import ValidationResult
from modules.host.audit.checks_docker import (
    run_check_docker_cli,
    run_check_docker_compose,
    run_check_docker_daemon,
    run_check_docker_runtime,
    run_check_docker_operator_access,
)
from modules.host.init.validate import ValidationReport

logger = logging.getLogger(__name__)


def _docker_validation_result(
    check_id: str,
    passed: bool,
    ok_message: str,
    failed_message: str,
    evidence: str,
) -> ValidationResult:
    """Build a Docker validation row for init-vps reporting."""
    return ValidationResult(
        check_id=check_id,
        passed=passed,
        message=ok_message if passed else failed_message,
        evidence=evidence,
    )


def _check_evidence(*checks: CheckResult) -> str:
    """Join the source audit-check evidence used by one validation row."""
    return "; ".join(
        f"{check.check_id}={check.status.value}: {check.evidence}"
        for check in checks
    )


def validate_docker_slice_report(operator_user: str | None = None) -> ValidationReport:
    """Validate Docker runtime readiness and return visible validation rows.

    Args:
        operator_user: The operator user to validate Docker access for. If None, skip operator access check.

    Returns:
        ValidationReport with one row per Slice 02 validation responsibility.
    """
    logger.info("Validating Docker runtime baseline...")

    results: list[ValidationResult] = []

    cli_check = run_check_docker_cli()
    runtime_check = run_check_docker_runtime()
    engine_passed = (
        cli_check.status == CheckStatus.OK
        and runtime_check.status == CheckStatus.OK
    )
    if not engine_passed:
        logger.error("Validation failed: Docker Engine is not installed and usable.")
    results.append(_docker_validation_result(
        "VALIDATE_DOCKER_ENGINE",
        engine_passed,
        "Docker Engine is installed and usable",
        "Docker Engine is not installed and usable",
        _check_evidence(cli_check, runtime_check),
    ))

    compose_check = run_check_docker_compose()
    compose_passed = compose_check.status == CheckStatus.OK
    if not compose_passed:
        logger.error("Validation failed: Docker Compose plugin is not available.")
    results.append(_docker_validation_result(
        "VALIDATE_DOCKER_COMPOSE",
        compose_passed,
        "Docker Compose plugin is installed and usable",
        "Docker Compose plugin is not installed and usable",
        _check_evidence(compose_check),
    ))

    service_check = run_check_docker_daemon()
    service_passed = service_check.status == CheckStatus.OK
    if not service_passed:
        logger.error("Validation failed: Docker service is not active.")
    results.append(_docker_validation_result(
        "VALIDATE_DOCKER_SERVICE",
        service_passed,
        "Docker service is active",
        "Docker service is not active",
        _check_evidence(service_check),
    ))

    if operator_user:
        operator_check = run_check_docker_operator_access(operator_user)
        operator_passed = operator_check.status == CheckStatus.OK
        if not operator_passed:
            logger.error(
                "Validation failed: Operator user %s cannot access Docker.",
                operator_user,
            )
        results.append(_docker_validation_result(
            "VALIDATE_DOCKER_OPERATOR_ACCESS",
            operator_passed,
            f"Operator user '{operator_user}' can run Docker without sudo",
            f"Operator user '{operator_user}' cannot run Docker without sudo",
            _check_evidence(operator_check),
        ))

    all_passed = all(result.passed for result in results)
    if all_passed:
        logger.info("Docker runtime baseline validated successfully.")

    return ValidationReport(results=results, all_passed=all_passed)


def validate_docker_slice(operator_user: str | None = None) -> bool:
    """Validate Docker runtime readiness.

    Args:
        operator_user: The operator user to validate Docker access for. If None, skip operator access check.

    Returns:
        True if all required Docker runtime conditions are met.
        False if validation fails.
    """
    return validate_docker_slice_report(operator_user).all_passed

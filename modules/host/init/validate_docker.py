"""
Docker Validation — Verifies the Docker runtime state after reconciliation.

Governed by: HOST_SLICE_02_DOCKER_COMPOSE_ADDENDUM.md §15.
"""

import logging

from modules.host.audit.checks_docker import (
    run_check_docker_cli,
    run_check_docker_compose,
    run_check_docker_daemon,
    run_check_docker_runtime,
    run_check_docker_operator_access,
)

logger = logging.getLogger(__name__)


def validate_docker_slice(operator_user: str | None = None) -> bool:
    """Validate Docker runtime readiness.

    Args:
        operator_user: The operator user to validate Docker access for. If None, skip operator access check.

    Returns:
        True if all required Docker runtime conditions are met.
        False if validation fails.
    """
    logger.info("Validating Docker runtime baseline...")

    if run_check_docker_cli().status != "OK":
        logger.error("Validation failed: Docker CLI is not available.")
        return False

    if run_check_docker_daemon().status != "OK":
        logger.error("Validation failed: Docker daemon is not active.")
        return False

    if run_check_docker_runtime().status != "OK":
        logger.error("Validation failed: Docker runtime is not responding to commands.")
        return False

    if run_check_docker_compose().status != "OK":
        logger.error("Validation failed: Docker Compose plugin is not available.")
        return False

    if operator_user:
        if run_check_docker_operator_access(operator_user).status != "OK":
            logger.error(f"Validation failed: Operator user {operator_user} cannot access Docker.")
            return False

    logger.info("Docker runtime baseline validated successfully.")
    return True

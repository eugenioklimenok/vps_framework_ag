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
)

logger = logging.getLogger(__name__)


def validate_docker_slice() -> bool:
    """Validate Docker runtime readiness.

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

    logger.info("Docker runtime baseline validated successfully.")
    return True

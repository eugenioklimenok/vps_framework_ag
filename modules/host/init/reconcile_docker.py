"""
Docker Reconciler — Installs and configures Docker runtime and Compose plugin.

Governed by: HOST_SLICE_02_DOCKER_COMPOSE_ADDENDUM.md §14.
"""

import logging

from models.enums import ReconcileAction
from modules.host.audit.checks_docker import (
    run_check_docker_cli,
    run_check_docker_compose,
    run_check_docker_daemon,
)
from utils.subprocess_wrapper import run_command

logger = logging.getLogger(__name__)


def reconcile_docker_engine() -> ReconcileAction:
    """Ensure Docker Engine is installed."""
    if run_check_docker_cli().status == "OK":
        return ReconcileAction.SKIPPED

    logger.info("Docker CLI not found. Installing Docker Engine...")

    res_update = run_command(["apt-get", "update"])
    if res_update.returncode != 0:
        logger.error("Failed to run apt-get update: %s", res_update.stderr)
        return ReconcileAction.FAILED

    res_install = run_command(["apt-get", "install", "-y", "docker.io"])
    if res_install.returncode != 0:
        logger.error("Failed to install docker.io: %s", res_install.stderr)
        return ReconcileAction.FAILED

    return ReconcileAction.CREATED


def reconcile_docker_compose() -> ReconcileAction:
    """Ensure Docker Compose plugin is installed."""
    if run_check_docker_compose().status == "OK":
        return ReconcileAction.SKIPPED

    logger.info("Docker Compose plugin not found. Installing docker-compose-v2...")

    res_install = run_command(["apt-get", "install", "-y", "docker-compose-v2"])
    if res_install.returncode != 0:
        logger.error("Failed to install docker-compose-v2: %s", res_install.stderr)
        return ReconcileAction.FAILED

    return ReconcileAction.CREATED


def enable_start_docker() -> ReconcileAction:
    """Ensure Docker service is enabled and started."""
    daemon_check = run_check_docker_daemon()
    if daemon_check.status == "OK":
        return ReconcileAction.SKIPPED

    logger.info("Docker daemon not active. Enabling and starting docker service...")

    res_enable = run_command(["systemctl", "enable", "--now", "docker"])
    if res_enable.returncode != 0:
        logger.error("Failed to enable docker service: %s", res_enable.stderr)
        return ReconcileAction.FAILED

    return ReconcileAction.REPAIRED

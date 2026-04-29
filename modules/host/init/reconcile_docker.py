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
from modules.host.audit.checks_os import _parse_os_release
from utils.subprocess_wrapper import run_command

logger = logging.getLogger(__name__)


def _setup_docker_official_repo() -> bool:
    """Safely configure the official Docker APT repository."""
    logger.info("Setting up official Docker repository...")
    
    # 1. Determine OS and codename BEFORE modifying the system
    try:
        with open("/etc/os-release", "r") as f:
            os_data = _parse_os_release(f.read())
            
            os_id = os_data.get("ID", "").lower()
            if os_id != "ubuntu":
                logger.error("Unsupported OS for Docker official repo: %s", os_id)
                return False
                
            codename = os_data.get("VERSION_CODENAME")
            # Fallback if UBUNTU_CODENAME is used instead of VERSION_CODENAME
            if not codename:
                codename = os_data.get("UBUNTU_CODENAME")
                
            if not codename:
                logger.error("VERSION_CODENAME/UBUNTU_CODENAME not found in /etc/os-release")
                return False
    except OSError as e:
        logger.error("Failed to read /etc/os-release: %s", e)
        return False

    # 2. Install prerequisites
    cmds = [
        ["apt-get", "update"],
        ["apt-get", "install", "-y", "ca-certificates", "curl", "gnupg"],
        ["install", "-m", "0755", "-d", "/etc/apt/keyrings"],
        ["curl", "-fsSL", "https://download.docker.com/linux/ubuntu/gpg", "-o", "/etc/apt/keyrings/docker.asc"],
        ["chmod", "a+r", "/etc/apt/keyrings/docker.asc"]
    ]
    
    for cmd in cmds:
        res = run_command(cmd)
        if res.returncode != 0:
            logger.error("Failed prerequisite command: %s (stderr: %s)", " ".join(cmd), res.stderr)
            return False
            
    # 3. Determine architecture
    arch_res = run_command(["dpkg", "--print-architecture"])
    if arch_res.returncode != 0:
        logger.error("Failed to determine dpkg architecture.")
        return False
    arch = arch_res.stdout.strip()
    
    # 4. Write repository source file
    source_entry = f"deb [arch={arch} signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu {codename} stable\n"
    
    try:
        with open("/etc/apt/sources.list.d/docker.list", "w") as f:
            f.write(source_entry)
    except OSError as e:
        logger.error("Failed to write docker sources.list: %s", e)
        return False
        
    res_update = run_command(["apt-get", "update"])
    if res_update.returncode != 0:
        logger.error("Failed apt-get update after adding docker repo: %s", res_update.stderr)
        return False
        
    return True


def reconcile_docker_engine() -> ReconcileAction:
    """Ensure Docker Engine is installed."""
    if run_check_docker_cli().status == "OK":
        return ReconcileAction.SKIPPED

    logger.info("Docker CLI not found. Installing official Docker Engine...")

    if not _setup_docker_official_repo():
        return ReconcileAction.FAILED

    packages = [
        "docker-ce",
        "docker-ce-cli",
        "containerd.io",
        "docker-buildx-plugin",
        "docker-compose-plugin"
    ]
    
    res_install = run_command(["apt-get", "install", "-y"] + packages)
    if res_install.returncode != 0:
        logger.error("Failed to install official Docker packages: %s", res_install.stderr)
        return ReconcileAction.FAILED

    return ReconcileAction.CREATED


def reconcile_docker_compose() -> ReconcileAction:
    """Ensure Docker Compose plugin is installed."""
    if run_check_docker_compose().status == "OK":
        return ReconcileAction.SKIPPED

    logger.info("Docker Compose plugin not found. Installing docker-compose-plugin...")

    res_install = run_command(["apt-get", "install", "-y", "docker-compose-plugin"])
    if res_install.returncode != 0:
        logger.error("Failed to install docker-compose-plugin: %s", res_install.stderr)
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

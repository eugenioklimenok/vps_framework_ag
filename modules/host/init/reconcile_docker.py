"""
Docker Reconciler — Installs and configures Docker runtime and Compose plugin.

Governed by: HOST_SLICE_02_DOCKER_COMPOSE_ADDENDUM.md §14.
"""

import logging

from models.enums import ReconcileAction
from models.reconcile_result import ReconcileResult
from modules.host.audit.checks_docker import (
    run_check_docker_cli,
    run_check_docker_compose,
    run_check_docker_daemon,
)
from modules.host.audit.checks_os import _parse_os_release
from utils.subprocess_wrapper import run_command
from modules.host.init.validate_docker import validate_docker_slice

logger = logging.getLogger(__name__)


def _setup_docker_official_repo() -> tuple[bool, str]:
    """Safely configure the official Docker APT repository.
    Returns (success, error_message).
    """
    logger.debug("Setting up official Docker repository...")
    
    try:
        with open("/etc/os-release", "r") as f:
            os_data = _parse_os_release(f.read())
            
            os_id = os_data.get("ID", "").lower()
            if os_id != "ubuntu":
                return False, f"Unsupported OS for Docker official repo: {os_id}"
                
            codename = os_data.get("VERSION_CODENAME")
            if not codename:
                codename = os_data.get("UBUNTU_CODENAME")
                
            if not codename:
                return False, "VERSION_CODENAME/UBUNTU_CODENAME not found in /etc/os-release"
    except OSError as e:
        return False, f"Failed to read /etc/os-release: {e}"

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
            return False, f"Failed prerequisite command: {' '.join(cmd)}"
            
    arch_res = run_command(["dpkg", "--print-architecture"])
    if arch_res.returncode != 0:
        return False, "Failed to determine dpkg architecture."
    
    arch = arch_res.stdout.strip()
    source_entry = f"deb [arch={arch} signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu {codename} stable\n"
    
    try:
        with open("/etc/apt/sources.list.d/docker.list", "w") as f:
            f.write(source_entry)
    except OSError as e:
        return False, f"Failed to write docker sources.list: {e}"
        
    res_update = run_command(["apt-get", "update"])
    if res_update.returncode != 0:
        return False, "Failed apt-get update after adding docker repo."
        
    return True, ""


def reconcile_docker_engine() -> ReconcileResult:
    """Ensure Docker Engine is installed."""
    if run_check_docker_cli().status == "OK":
        return ReconcileResult(
            step_id="RECONCILE_DOCKER_ENGINE",
            action=ReconcileAction.SKIPPED,
            message="Docker Engine is installed and validated",
            evidence="Docker CLI found",
            success=True,
        )

    logger.debug("Docker CLI not found. Installing official Docker Engine...")

    repo_ok, repo_err = _setup_docker_official_repo()
    if not repo_ok:
        msg = (
            "Docker Engine reconciliation failed at repository setup.\n"
            "Failure type: command failure\n"
            f"Reason: {repo_err}\n"
            "Diagnostic command:\n"
            "  sudo apt-get update"
        )
        return ReconcileResult(
            step_id="RECONCILE_DOCKER_ENGINE", action=ReconcileAction.FAILED,
            message=msg, evidence="repository setup failed", success=False
        )

    packages = [
        "docker-ce",
        "docker-ce-cli",
        "containerd.io",
        "docker-buildx-plugin",
        "docker-compose-plugin"
    ]
    
    cmd = ["apt-get", "install", "-y"] + packages
    res_install = run_command(cmd, timeout=300)
    
    if res_install.returncode != 0:
        if res_install.timed_out:
            logger.debug("Docker apt install timed out. Running post-timeout validation recovery...")
            if validate_docker_slice():
                return ReconcileResult(
                    step_id="RECONCILE_DOCKER_ENGINE", action=ReconcileAction.CREATED,
                    message="Docker Engine is installed and validated (recovered after timeout)",
                    evidence="validate_docker_slice passed after timeout", success=True
                )
            
            msg = (
                "Docker Engine reconciliation failed.\n"
                "Failure type: timeout and validation failure\n"
                f"Command attempted: {' '.join(cmd)}\n"
                "Next diagnostic commands:\n"
                f"  sudo {' '.join(cmd)}\n"
                "  docker --version\n"
                "  docker info\n"
                "  docker compose version\n"
                "  systemctl is-active docker"
            )
            return ReconcileResult(
                step_id="RECONCILE_DOCKER_ENGINE", action=ReconcileAction.FAILED,
                message=msg, evidence="timeout and validation failed", success=False
            )
            
        msg = (
            "Docker Engine reconciliation failed.\n"
            "Failure type: command failure\n"
            f"Command attempted: {' '.join(cmd)}\n"
            "Next diagnostic commands:\n"
            f"  sudo {' '.join(cmd)}\n"
            "  docker --version"
        )
        return ReconcileResult(
            step_id="RECONCILE_DOCKER_ENGINE", action=ReconcileAction.FAILED,
            message=msg, evidence="apt-get install failed", success=False
        )

    return ReconcileResult(
        step_id="RECONCILE_DOCKER_ENGINE", action=ReconcileAction.CREATED,
        message="Docker Engine is installed and validated",
        evidence="apt-get install succeeded", success=True
    )


def reconcile_docker_compose() -> ReconcileResult:
    """Ensure Docker Compose plugin is installed."""
    if run_check_docker_compose().status == "OK":
        return ReconcileResult(
            step_id="RECONCILE_DOCKER_COMPOSE", action=ReconcileAction.SKIPPED,
            message="Docker Compose plugin is installed and validated",
            evidence="Compose CLI found", success=True
        )

    logger.debug("Docker Compose plugin not found. Installing docker-compose-plugin...")

    cmd = ["apt-get", "install", "-y", "docker-compose-plugin"]
    res_install = run_command(cmd, timeout=300)
    
    if res_install.returncode != 0:
        if res_install.timed_out:
            msg = (
                "Docker Compose plugin reconciliation failed.\n"
                "Failure type: timeout\n"
                f"Command attempted: {' '.join(cmd)}\n"
                "Next diagnostic commands:\n"
                f"  sudo {' '.join(cmd)}\n"
                "  docker compose version"
            )
            return ReconcileResult(
                step_id="RECONCILE_DOCKER_COMPOSE", action=ReconcileAction.FAILED,
                message=msg, evidence="timeout", success=False
            )
            
        msg = (
            "Docker Compose plugin reconciliation failed.\n"
            "Failure type: command failure\n"
            f"Command attempted: {' '.join(cmd)}\n"
            "Next diagnostic commands:\n"
            f"  sudo {' '.join(cmd)}\n"
            "  docker compose version"
        )
        return ReconcileResult(
            step_id="RECONCILE_DOCKER_COMPOSE", action=ReconcileAction.FAILED,
            message=msg, evidence="apt-get install failed", success=False
        )

    return ReconcileResult(
        step_id="RECONCILE_DOCKER_COMPOSE", action=ReconcileAction.CREATED,
        message="Docker Compose plugin is installed and validated",
        evidence="apt-get install succeeded", success=True
    )


def enable_start_docker() -> ReconcileResult:
    """Ensure Docker service is enabled and started."""
    if run_check_docker_daemon().status == "OK":
        return ReconcileResult(
            step_id="RECONCILE_DOCKER_SERVICE", action=ReconcileAction.SKIPPED,
            message="Docker service is active", evidence="Daemon is active", success=True
        )

    logger.debug("Docker daemon not active. Enabling and starting docker service...")

    cmd = ["systemctl", "enable", "--now", "docker"]
    res_enable = run_command(cmd, timeout=60)
    
    if res_enable.returncode != 0:
        msg = (
            "Docker service enablement failed.\n"
            "Failure type: command failure\n"
            f"Command attempted: {' '.join(cmd)}\n"
            "Next diagnostic commands:\n"
            f"  sudo {' '.join(cmd)}\n"
            "  systemctl status docker"
        )
        return ReconcileResult(
            step_id="RECONCILE_DOCKER_SERVICE", action=ReconcileAction.FAILED,
            message=msg, evidence="systemctl failed", success=False
        )

    return ReconcileResult(
        step_id="RECONCILE_DOCKER_SERVICE", action=ReconcileAction.REPAIRED,
        message="Docker service is active",
        evidence="systemctl succeeded", success=True
    )


def reconcile_docker_operator_access(operator_user: str) -> ReconcileResult:
    """Ensure the operator user is in the docker group."""
    from utils.subprocess_wrapper import run_command
    
    # Check if docker group exists
    res_group = run_command(["getent", "group", "docker"])
    if res_group.returncode != 0:
        return ReconcileResult(
            step_id="RECONCILE_DOCKER_OPERATOR_ACCESS", action=ReconcileAction.FAILED,
            message="Docker group does not exist.", evidence="getent group docker failed", success=False
        )

    # Check if user is in docker group
    res_id = run_command(["id", "-nG", operator_user])
    if res_id.returncode != 0:
        return ReconcileResult(
            step_id="RECONCILE_DOCKER_OPERATOR_ACCESS", action=ReconcileAction.FAILED,
            message=f"Failed to get groups for user {operator_user}.", evidence="id -nG failed", success=False
        )

    groups = res_id.stdout.split()
    if "docker" in groups:
        return ReconcileResult(
            step_id="RECONCILE_DOCKER_OPERATOR_ACCESS", action=ReconcileAction.SKIPPED,
            message=f"Operator user '{operator_user}' already has docker group access",
            evidence="user already in docker group", success=True
        )

    logger.debug(f"Adding user {operator_user} to docker group...")
    res_usermod = run_command(["usermod", "-aG", "docker", operator_user])
    
    if res_usermod.returncode != 0:
        return ReconcileResult(
            step_id="RECONCILE_DOCKER_OPERATOR_ACCESS", action=ReconcileAction.FAILED,
            message=f"Failed to add {operator_user} to docker group.", evidence="usermod failed", success=False
        )

    return ReconcileResult(
        step_id="RECONCILE_DOCKER_OPERATOR_ACCESS", action=ReconcileAction.REPAIRED,
        message=f"Operator user '{operator_user}' added to docker group",
        evidence="usermod succeeded", success=True
    )


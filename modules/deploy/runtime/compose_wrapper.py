"""
Deployment runtime wrapper.
Provides Python interfaces to `docker compose` using the safe subprocess wrapper.
Governed by: DEPLOY_BASELINE_TDD.md §9
"""

from pathlib import Path

from models.command_result import CommandResult
from utils.subprocess_wrapper import run_command


def check_compose_availability() -> bool:
    """
    Checks if `docker compose` is available and runnable.
    """
    result = run_command(["docker", "compose", "version"], timeout=5)
    return result.returncode == 0


def validate_compose_config(project_path: Path, env_file: Path, project_name: str) -> CommandResult:
    """
    Runs `docker compose config` to validate configuration before mutation.
    """
    cmd = [
        "docker",
        "compose",
        "--project-directory", str(project_path),
        "--file", str(project_path / "compose.yaml"),
        "--env-file", str(env_file),
        "--project-name", project_name,
        "config",
        "--quiet",
    ]
    return run_command(cmd, timeout=10)


def build_compose_stack(project_path: Path, env_file: Path, project_name: str) -> CommandResult:
    """
    Builds the docker compose stack.
    """
    cmd = [
        "docker",
        "compose",
        "--project-directory", str(project_path),
        "--file", str(project_path / "compose.yaml"),
        "--env-file", str(env_file),
        "--project-name", project_name,
        "build",
    ]
    return run_command(cmd, timeout=300)  # 5 minute timeout for builds


def start_compose_stack(project_path: Path, env_file: Path, project_name: str) -> CommandResult:
    """
    Starts the docker compose stack in detached mode.
    """
    cmd = [
        "docker",
        "compose",
        "--project-directory", str(project_path),
        "--file", str(project_path / "compose.yaml"),
        "--env-file", str(env_file),
        "--project-name", project_name,
        "up",
        "-d",
    ]
    return run_command(cmd, timeout=60)


def inspect_compose_status(project_path: Path, env_file: Path, project_name: str) -> CommandResult:
    """
    Retrieves the status of the docker compose stack.
    Uses `ps --format json` to allow structured checking.
    """
    cmd = [
        "docker",
        "compose",
        "--project-directory", str(project_path),
        "--file", str(project_path / "compose.yaml"),
        "--env-file", str(env_file),
        "--project-name", project_name,
        "ps",
        "--format", "json",
    ]
    return run_command(cmd, timeout=10)

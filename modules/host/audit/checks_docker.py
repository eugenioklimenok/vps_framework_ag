"""
Docker Audit Checks.

Governed by: HOST_SLICE_02_DOCKER_COMPOSE_ADDENDUM.md §12.
"""

from models.check_result import CheckResult
from models.enums import CheckStatus, ClassificationImpact
from utils.subprocess_wrapper import run_command


def _parse_group_members(group_entry: str) -> set[str]:
    """Parse members from a getent group entry."""
    parts = group_entry.strip().split(":")
    if len(parts) < 4 or not parts[3].strip():
        return set()
    return {member.strip() for member in parts[3].split(",") if member.strip()}


def run_check_docker_cli() -> CheckResult:
    """CHECK_DOCKER_01: Docker CLI availability."""
    cmd = ["docker", "--version"]
    result = run_command(cmd)

    if result.returncode == 0:
        return CheckResult(
            check_id="CHECK_DOCKER_01",
            title="Docker CLI Availability",
            category="DOCKER",
            description="Verifies if the Docker CLI is installed and usable.",
            evidence_command=" ".join(cmd),
            expected_behavior="Docker CLI responds with version information.",
            status=CheckStatus.OK,
            evidence=result.stdout.strip()[:100],
            message="Docker CLI is available.",
            classification_impact=ClassificationImpact.NONE,
        )

    return CheckResult(
        check_id="CHECK_DOCKER_01",
        title="Docker CLI Availability",
        category="DOCKER",
        description="Verifies if the Docker CLI is installed and usable.",
        evidence_command=" ".join(cmd),
        expected_behavior="Docker CLI responds with version information.",
        status=CheckStatus.WARN,
        evidence=result.error or result.stderr.strip() or "Command failed.",
        message="Docker CLI is not available. Installation required.",
        classification_impact=ClassificationImpact.SANEABLE,
    )


def run_check_docker_daemon() -> CheckResult:
    """CHECK_DOCKER_02: Docker daemon/service state."""
    cmd = ["systemctl", "is-active", "docker"]
    result = run_command(cmd)

    evidence = result.stdout.strip() or result.stderr.strip() or result.error or "Unknown"

    if result.returncode == 0 and result.stdout.strip() == "active":
        return CheckResult(
            check_id="CHECK_DOCKER_02",
            title="Docker Daemon State",
            category="DOCKER",
            description="Verifies if the Docker service is active.",
            evidence_command=" ".join(cmd),
            expected_behavior="Docker service is active.",
            status=CheckStatus.OK,
            evidence=evidence,
            message="Docker daemon is active.",
            classification_impact=ClassificationImpact.NONE,
        )

    return CheckResult(
        check_id="CHECK_DOCKER_02",
        title="Docker Daemon State",
        category="DOCKER",
        description="Verifies if the Docker service is active.",
        evidence_command=" ".join(cmd),
        expected_behavior="Docker service is active.",
        status=CheckStatus.WARN,
        evidence=evidence,
        message="Docker daemon is not active or not installed.",
        classification_impact=ClassificationImpact.SANEABLE,
    )


def run_check_docker_runtime() -> CheckResult:
    """CHECK_DOCKER_03: Docker runtime usability."""
    cmd = ["docker", "info"]
    result = run_command(cmd)

    if result.returncode == 0:
        return CheckResult(
            check_id="CHECK_DOCKER_03",
            title="Docker Runtime Usability",
            category="DOCKER",
            description="Verifies if the Docker runtime can be communicated with.",
            evidence_command=" ".join(cmd),
            expected_behavior="docker info returns successfully.",
            status=CheckStatus.OK,
            evidence="Docker info successful",
            message="Docker runtime is responding.",
            classification_impact=ClassificationImpact.NONE,
        )

    return CheckResult(
        check_id="CHECK_DOCKER_03",
        title="Docker Runtime Usability",
        category="DOCKER",
        description="Verifies if the Docker runtime can be communicated with.",
        evidence_command=" ".join(cmd),
        expected_behavior="docker info returns successfully.",
        status=CheckStatus.WARN,
        evidence=result.error or result.stderr.strip() or "Command failed.",
        message="Docker runtime is not responding or not installed.",
        classification_impact=ClassificationImpact.SANEABLE,
    )


def run_check_docker_compose() -> CheckResult:
    """CHECK_DOCKER_04: Docker Compose availability."""
    cmd = ["docker", "compose", "version"]
    result = run_command(cmd)

    if result.returncode == 0:
        return CheckResult(
            check_id="CHECK_DOCKER_04",
            title="Docker Compose Availability",
            category="DOCKER",
            description="Verifies if Docker Compose plugin is available.",
            evidence_command=" ".join(cmd),
            expected_behavior="docker compose version returns successfully.",
            status=CheckStatus.OK,
            evidence=result.stdout.strip()[:100],
            message="Docker Compose plugin is available.",
            classification_impact=ClassificationImpact.NONE,
        )

    return CheckResult(
        check_id="CHECK_DOCKER_04",
        title="Docker Compose Availability",
        category="DOCKER",
        description="Verifies if Docker Compose plugin is available.",
        evidence_command=" ".join(cmd),
        expected_behavior="docker compose version returns successfully.",
        status=CheckStatus.WARN,
        evidence=result.error or result.stderr.strip() or "Command failed.",
        message="Docker Compose plugin is not available. Installation required.",
        classification_impact=ClassificationImpact.SANEABLE,
    )


def run_check_docker_conflicts() -> CheckResult:
    """CHECK_DOCKER_05: Conflicting Docker packages."""
    cmd = ["dpkg", "-l"]
    result = run_command(cmd)

    conflicting_packages = [
        "docker.io",
        "docker-doc",
        "docker-compose",
        "docker-compose-v2",
        "podman-docker"
    ]
    found_conflicts = []

    if result.returncode == 0:
        lines = result.stdout.splitlines()
        for line in lines:
            if line.startswith("ii ") or line.startswith("hi "):
                parts = line.split()
                if len(parts) > 1:
                    pkg = parts[1].split(":")[0]  # remove arch if present
                    if pkg in conflicting_packages:
                        found_conflicts.append(pkg)

    if not found_conflicts:
        return CheckResult(
            check_id="CHECK_DOCKER_05",
            title="Docker Conflict Check",
            category="DOCKER",
            description="Verifies there are no conflicting legacy Docker packages installed.",
            evidence_command="dpkg -l | grep ...",
            expected_behavior="No conflicting packages found.",
            status=CheckStatus.OK,
            evidence="No conflicts detected.",
            message="No legacy or conflicting Docker packages found.",
            classification_impact=ClassificationImpact.NONE,
        )

    return CheckResult(
        check_id="CHECK_DOCKER_05",
        title="Docker Conflict Check",
        category="DOCKER",
        description="Verifies there are no conflicting legacy Docker packages installed.",
        evidence_command="dpkg -l | grep ...",
        expected_behavior="No conflicting packages found.",
        status=CheckStatus.FAIL,
        evidence=f"Conflicts: {', '.join(found_conflicts)}",
        message="Found conflicting legacy Docker packages.",
        classification_impact=ClassificationImpact.BLOCKED,
    )


def run_check_docker_operator_access(operator_user: str) -> CheckResult:
    """CHECK_DOCKER_06: Docker operator access."""
    id_cmd = ["id", operator_user]
    id_result = run_command(id_cmd)
    if id_result.returncode != 0:
        return CheckResult(
            check_id="CHECK_DOCKER_06",
            title="Docker Operator Access",
            category="DOCKER",
            description="Verifies if the operator user can interact with the Docker daemon.",
            evidence_command=" ".join(id_cmd),
            expected_behavior="operator user exists before Docker access validation.",
            status=CheckStatus.WARN,
            evidence=id_result.error or id_result.stderr.strip() or "Command failed.",
            message="Operator user does not exist or cannot be inspected.",
            classification_impact=ClassificationImpact.SANEABLE,
        )

    group_cmd = ["getent", "group", "docker"]
    group_result = run_command(group_cmd)
    if group_result.returncode != 0:
        return CheckResult(
            check_id="CHECK_DOCKER_06",
            title="Docker Operator Access",
            category="DOCKER",
            description="Verifies if the operator user can interact with the Docker daemon.",
            evidence_command=" ".join(group_cmd),
            expected_behavior="docker group exists and includes the operator user.",
            status=CheckStatus.WARN,
            evidence=group_result.error or group_result.stderr.strip() or "Command failed.",
            message="Docker group does not exist or cannot be inspected.",
            classification_impact=ClassificationImpact.SANEABLE,
        )

    if operator_user not in _parse_group_members(group_result.stdout):
        return CheckResult(
            check_id="CHECK_DOCKER_06",
            title="Docker Operator Access",
            category="DOCKER",
            description="Verifies if the operator user can interact with the Docker daemon.",
            evidence_command=" ".join(group_cmd),
            expected_behavior="docker group exists and includes the operator user.",
            status=CheckStatus.WARN,
            evidence=group_result.stdout.strip() or "docker group has no listed members.",
            message="Operator user is not listed as a docker group member.",
            classification_impact=ClassificationImpact.SANEABLE,
        )

    cmd = ["runuser", "-l", operator_user, "-c", "docker ps"]
    result = run_command(cmd)

    if result.returncode == 0:
        return CheckResult(
            check_id="CHECK_DOCKER_06",
            title="Docker Operator Access",
            category="DOCKER",
            description="Verifies if the operator user can interact with the Docker daemon.",
            evidence_command=" ".join(cmd),
            expected_behavior="runuser with docker ps returns successfully.",
            status=CheckStatus.OK,
            evidence="Docker ps successful",
            message="Operator user has Docker access.",
            classification_impact=ClassificationImpact.NONE,
        )

    return CheckResult(
        check_id="CHECK_DOCKER_06",
        title="Docker Operator Access",
        category="DOCKER",
        description="Verifies if the operator user can interact with the Docker daemon.",
        evidence_command=" ".join(cmd),
        expected_behavior="runuser with docker ps returns successfully.",
        status=CheckStatus.WARN,
        evidence=result.error or result.stderr.strip() or "Command failed.",
        message="Operator user cannot interact with the Docker daemon.",
        classification_impact=ClassificationImpact.SANEABLE,
    )

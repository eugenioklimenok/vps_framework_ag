"""
Runtime checks for the OPERATE module.
Governed by: OPERATE_BASELINE_TDD.md
"""

from pathlib import Path

from models.check_result import CheckResult
from models.enums import CheckStatus, ClassificationImpact
from modules.deploy.runtime.compose_wrapper import inspect_compose_status


def check_runtime_status(project_path: Path, env_file: Path, project_slug: str) -> CheckResult:
    """
    Checks if the project services are running.
    """
    import json
    
    result = inspect_compose_status(project_path, env_file, project_slug)
    
    if result.returncode != 0:
        return CheckResult(
            check_id="OP_CHK_RUNTIME_01",
            title="Docker Compose Status",
            category="RUNTIME",
            description="Check if services are running.",
            evidence_command="docker compose ps",
            expected_behavior="All services running.",
            status=CheckStatus.FAIL,
            evidence=result.stderr.strip(),
            message="Failed to query Docker Compose status.",
            classification_impact=ClassificationImpact.BLOCKED,
        )
        
    try:
        lines = result.stdout.strip().splitlines()
        if not lines:
            return CheckResult(
                check_id="OP_CHK_RUNTIME_01",
                title="Docker Compose Status",
                category="RUNTIME",
                description="Check if services are running.",
                evidence_command="docker compose ps",
                expected_behavior="All services running.",
                status=CheckStatus.WARN,
                evidence="Empty state",
                message="No services are currently running.",
                classification_impact=ClassificationImpact.SANEABLE,
            )
            
        services_running = 0
        services_exited = 0
        total_services = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            data = json.loads(line)
            
            if isinstance(data, list):
                for svc in data:
                    total_services += 1
                    state = svc.get("State", "").lower()
                    if state == "running":
                        services_running += 1
                    else:
                        services_exited += 1
            else:
                total_services += 1
                state = data.get("State", "").lower()
                if state == "running":
                    services_running += 1
                else:
                    services_exited += 1

        if services_running == 0:
             return CheckResult(
                check_id="OP_CHK_RUNTIME_01",
                title="Docker Compose Status",
                category="RUNTIME",
                description="Check if services are running.",
                evidence_command="docker compose ps",
                expected_behavior="All services running.",
                status=CheckStatus.FAIL,
                evidence=f"Total: {total_services}",
                message="All services are down.",
                classification_impact=ClassificationImpact.BLOCKED,
            )
            
        if services_exited > 0:
            return CheckResult(
                check_id="OP_CHK_RUNTIME_01",
                title="Docker Compose Status",
                category="RUNTIME",
                description="Check if services are running.",
                evidence_command="docker compose ps",
                expected_behavior="All services running.",
                status=CheckStatus.WARN,
                evidence=f"Running: {services_running}, Down: {services_exited}",
                message="Some services are not running.",
                classification_impact=ClassificationImpact.SANEABLE,
            )
            
        return CheckResult(
            check_id="OP_CHK_RUNTIME_01",
            title="Docker Compose Status",
            category="RUNTIME",
            description="Check if services are running.",
            evidence_command="docker compose ps",
            expected_behavior="All services running.",
            status=CheckStatus.OK,
            evidence=f"Running: {services_running}",
            message="All services are running.",
            classification_impact=ClassificationImpact.NONE,
        )
        
    except json.JSONDecodeError:
        return CheckResult(
            check_id="OP_CHK_RUNTIME_01",
            title="Docker Compose Status",
            category="RUNTIME",
            description="Check if services are running.",
            evidence_command="docker compose ps",
            expected_behavior="All services running.",
            status=CheckStatus.FAIL,
            evidence="Invalid JSON",
            message="Could not parse Docker Compose status output.",
            classification_impact=ClassificationImpact.BLOCKED,
        )


def check_endpoint_url(url: str) -> CheckResult:
    """
    Validates if an HTTP endpoint returns a 200 OK.
    """
    import urllib.request
    from urllib.error import URLError, HTTPError
    
    try:
        # A simple lightweight ping
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as response:
            status = response.status
            if status >= 200 and status < 400:
                return CheckResult(
                    check_id="OP_CHK_ENDPOINT_01",
                    title="Endpoint Reachability",
                    category="ENDPOINT",
                    description="Check HTTP endpoint.",
                    evidence_command=f"GET {url}",
                    expected_behavior="HTTP 200 OK",
                    status=CheckStatus.OK,
                    evidence=f"HTTP {status}",
                    message=f"Endpoint is reachable (HTTP {status}).",
                    classification_impact=ClassificationImpact.NONE,
                )
            else:
                return CheckResult(
                    check_id="OP_CHK_ENDPOINT_01",
                    title="Endpoint Reachability",
                    category="ENDPOINT",
                    description="Check HTTP endpoint.",
                    evidence_command=f"GET {url}",
                    expected_behavior="HTTP 200 OK",
                    status=CheckStatus.WARN,
                    evidence=f"HTTP {status}",
                    message=f"Endpoint returned non-200 status (HTTP {status}).",
                    classification_impact=ClassificationImpact.SANEABLE,
                )
    except HTTPError as e:
         return CheckResult(
            check_id="OP_CHK_ENDPOINT_01",
            title="Endpoint Reachability",
            category="ENDPOINT",
            description="Check HTTP endpoint.",
            evidence_command=f"GET {url}",
            expected_behavior="HTTP 200 OK",
            status=CheckStatus.WARN,
            evidence=str(e.code),
            message=f"Endpoint returned HTTP Error ({e.code}).",
            classification_impact=ClassificationImpact.SANEABLE,
        )
    except URLError as e:
        return CheckResult(
            check_id="OP_CHK_ENDPOINT_01",
            title="Endpoint Reachability",
            category="ENDPOINT",
            description="Check HTTP endpoint.",
            evidence_command=f"GET {url}",
            expected_behavior="HTTP 200 OK",
            status=CheckStatus.WARN,
            evidence=str(e.reason),
            message=f"Endpoint unreachable: {e.reason}",
            classification_impact=ClassificationImpact.SANEABLE,
        )
    except Exception as e:
         return CheckResult(
            check_id="OP_CHK_ENDPOINT_01",
            title="Endpoint Reachability",
            category="ENDPOINT",
            description="Check HTTP endpoint.",
            evidence_command=f"GET {url}",
            expected_behavior="HTTP 200 OK",
            status=CheckStatus.FAIL,
            evidence=str(e),
            message=f"Endpoint check failed: {e}",
            classification_impact=ClassificationImpact.BLOCKED,
        )

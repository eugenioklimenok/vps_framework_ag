"""
Smoke testing and runtime validation logic for DEPLOY module.
Governed by: DEPLOY_BASELINE_TDD.md §9 and DEPLOY_PROJECT_SPEC.md §11
"""

import json
from pathlib import Path

from models.command_result import CommandResult
from modules.deploy.runtime.compose_wrapper import inspect_compose_status


def run_baseline_smoke_test(project_path: Path, env_file: Path, project_name: str) -> bool:
    """
    Executes the baseline smoke test.
    For the current baseline, this checks if the compose stack is reporting
    its services as running (or another acceptable state).
    
    Returns:
        True if smoke test passed, False otherwise.
    """
    result = inspect_compose_status(project_path, env_file, project_name)
    if result.returncode != 0:
        return False
        
    try:
        # Expected docker compose ps --format json output is either
        # a single JSON object (if one service) or a JSON array,
        # or multiple JSON objects separated by newlines depending on docker version.
        
        # We naively parse by splitting on newlines to handle JSON lines format
        lines = result.stdout.strip().splitlines()
        if not lines:
            # If nothing is running, smoke fails
            return False
            
        services_running = 0
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Simple check, we just want to ensure it's parseable and state is 'running'
            # Some versions return list, some return dict per line
            data = json.loads(line)
            
            if isinstance(data, list):
                for svc in data:
                    state = svc.get("State", "").lower()
                    if state == "running":
                        services_running += 1
            else:
                state = data.get("State", "").lower()
                if state == "running":
                    services_running += 1

        # We consider the smoke passed if at least one service is running
        # (For the baseline alpine stack, the app service should be running)
        return services_running > 0
        
    except json.JSONDecodeError:
        # If we can't parse the output, we fail safe
        return False


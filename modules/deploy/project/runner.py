"""
Orchestrator runner for the DEPLOY module.
Governed by: DEPLOY_BASELINE_TDD.md §9 and DEPLOY_PROJECT_SPEC.md §9
"""

from pathlib import Path

from models.deploy_result import DeployResult
from models.enums import DeployAction, DeploymentClassification
from modules.deploy.project.inspect_project import inspect_project_for_deployment
from modules.deploy.project.smoke import run_baseline_smoke_test
from modules.deploy.runtime import compose_wrapper


def run_deploy_project(path: str, env_file_path: str) -> DeployResult:
    """
    Main orchestration function for deploy-project.
    
    Phases:
    1. Input Validation
    2. Project Inspection
    3. Classification
    4. Runtime Prerequisite Validation
    5. Configuration Validation
    6. Build
    7. Startup
    8. Smoke Testing
    9. Post-Deploy Validation
    """
    target_path = Path(path).resolve()
    env_file = Path(env_file_path).resolve()
    
    actions_taken = []
    
    # Phase 1: Input Validation
    if not env_file.exists() or not env_file.is_file():
        return DeployResult(
            classification=DeploymentClassification.BLOCKED,
            actions_taken=[DeployAction.BLOCK],
            blocked_reason=f"Explicit env file '{env_file_path}' is missing or invalid.",
        )

    # Phase 2 & 3: Inspection and Classification
    classification, slug, error_msg = inspect_project_for_deployment(target_path)
    if classification == DeploymentClassification.BLOCKED:
        return DeployResult(
            classification=classification,
            actions_taken=[DeployAction.BLOCK],
            blocked_reason=error_msg,
        )

    # Phase 4: Runtime Prerequisite Validation
    if not compose_wrapper.check_compose_availability():
        return DeployResult(
            classification=DeploymentClassification.BLOCKED,
            actions_taken=[DeployAction.BLOCK],
            project_slug=slug,
            blocked_reason="Deployment runtime (docker compose) is missing or unusable.",
        )

    # Phase 5: Configuration Validation
    actions_taken.append(DeployAction.VALIDATE)
    config_result = compose_wrapper.validate_compose_config(target_path, env_file, slug)
    if config_result.returncode != 0:
        return DeployResult(
            classification=DeploymentClassification.BLOCKED,
            actions_taken=actions_taken + [DeployAction.BLOCK],
            project_slug=slug,
            config_validated=False,
            blocked_reason=f"Configuration validation failed: {config_result.stderr.strip()}",
        )
    
    # Check if REDEPLOYABLE (are services already running?)
    status_result = compose_wrapper.inspect_compose_status(target_path, env_file, slug)
    if status_result.returncode == 0 and status_result.stdout.strip():
        classification = DeploymentClassification.REDEPLOYABLE

    # Phase 6: Build
    actions_taken.append(DeployAction.BUILD)
    build_result = compose_wrapper.build_compose_stack(target_path, env_file, slug)
    if build_result.returncode != 0:
        return DeployResult(
            classification=classification,
            actions_taken=actions_taken,
            project_slug=slug,
            config_validated=True,
            build_succeeded=False,
            blocked_reason=f"Build failed: {build_result.stderr.strip()}",
        )

    # Phase 7: Startup
    actions_taken.append(DeployAction.START)
    start_result = compose_wrapper.start_compose_stack(target_path, env_file, slug)
    if start_result.returncode != 0:
        return DeployResult(
            classification=classification,
            actions_taken=actions_taken,
            project_slug=slug,
            config_validated=True,
            build_succeeded=True,
            startup_succeeded=False,
            blocked_reason=f"Startup failed: {start_result.stderr.strip()}",
        )

    # Phase 8: Smoke Testing
    actions_taken.append(DeployAction.SMOKE)
    smoke_passed = run_baseline_smoke_test(target_path, env_file, slug)
    
    # Phase 9: Post-Deploy Validation
    # In the current baseline, validation is essentially smoke testing passing
    validation_passed = smoke_passed
    
    blocked_reason = ""
    if not validation_passed:
        actions_taken.append(DeployAction.BLOCK)
        blocked_reason = "Smoke tests or runtime state validation failed."

    return DeployResult(
        classification=classification,
        actions_taken=actions_taken,
        project_slug=slug,
        config_validated=True,
        build_succeeded=True,
        startup_succeeded=True,
        smoke_passed=smoke_passed,
        validation_passed=validation_passed,
        blocked_reason=blocked_reason,
    )

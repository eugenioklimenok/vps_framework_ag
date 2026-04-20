"""
Orchestrator runner for the PROJECT module.
"""

from pathlib import Path
from typing import Optional

from models.enums import ScaffoldAction, TargetClassification
from models.project_result import ScaffoldResult
from modules.project.inspect_target import classify_target
from modules.project.plan import validate_slug
from modules.project.render import materialize_scaffold


def validate_project_post_creation(target_path: Path) -> bool:
    """
    Validates that the project was successfully scaffolded.
    """
    from config.project_config import REQUIRED_PROJECT_DIRS, REQUIRED_PROJECT_FILES

    for d in REQUIRED_PROJECT_DIRS:
        if not (target_path / d).is_dir():
            return False

    for f in REQUIRED_PROJECT_FILES:
        if not (target_path / f).is_file():
            return False

    return True


def run_new_project(slug: str, path: str) -> ScaffoldResult:
    """
    Main orchestration function for new-project.
    
    Phases:
    1. Input Validation
    2. Inspection & Classification
    3. Materialization
    4. Post-action validation
    """
    target_path = Path(path).resolve()

    # Phase 1: Input Validation
    if not validate_slug(slug):
        return ScaffoldResult(
            classification=TargetClassification.BLOCKED,
            actions_taken=[ScaffoldAction.BLOCK],
            blocked_reason=f"Invalid slug '{slug}'. Must be lowercase alphanumeric with hyphens.",
        )

    # Phase 2: Inspection & Classification
    classification = classify_target(target_path)

    if classification == TargetClassification.BLOCKED:
        return ScaffoldResult(
            classification=classification,
            actions_taken=[ScaffoldAction.BLOCK],
            blocked_reason=f"Target path '{target_path}' contains conflicting or ambiguous files.",
        )

    # Phase 3: Materialization
    result = materialize_scaffold(target_path, slug, classification)

    if ScaffoldAction.BLOCK in result.actions_taken:
        return result

    # Phase 4: Post-action validation
    is_valid = validate_project_post_creation(target_path)
    
    # We reconstruct the dataclass to update the validation flag
    final_result = ScaffoldResult(
        classification=result.classification,
        actions_taken=result.actions_taken,
        created_paths=result.created_paths,
        reused_paths=result.reused_paths,
        blocked_reason=result.blocked_reason if not is_valid else "",
        validation_passed=is_valid,
    )
    
    if not is_valid:
        # If validation fails, we treat it as a failure
        return ScaffoldResult(
            classification=final_result.classification,
            actions_taken=final_result.actions_taken,
            created_paths=final_result.created_paths,
            reused_paths=final_result.reused_paths,
            blocked_reason="Post-creation validation failed: missing required files or directories.",
            validation_passed=False,
        )

    return final_result
